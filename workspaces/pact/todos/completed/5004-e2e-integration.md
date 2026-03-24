# TODO-5004: End-to-End Integration Test Suite

Status: pending
Priority: high
Dependencies: [1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 3001, 3002, 3003, 3004, 3005, 3006, 4001, 4002, 4003, 4004, 5001, 5002, 5003]
Milestone: M5

## What

End-to-end integration test suite that runs the full PACT governance lifecycle using the university example vertical. This test proves that all PACT concepts work together correctly, not just in isolation. It is the integration-level analogue of the unit tests in each milestone.

The suite covers 10+ scenarios that together demonstrate every normative PACT requirement:

1. Same-unit access (allowed by default)
2. Cross-unit blocked (default-deny without KSP)
3. Bridge-mediated access (allowed via Standing Bridge)
4. Clearance-independent access (clearance blocks even within-unit)
5. Compartment enforcement (compartment required for SECRET+ items)
6. Posture-capping (effective clearance reduced at high autonomy)
7. T-inherits-D (Team envelope is intersection with Department envelope)
8. Effective envelope computation (role ∩ task = effective)
9. Degenerate envelope detection (pass-through envelope flagged)
10. Audit trail completeness (every decision produces an audit anchor)
11. Address containment (get_nodes_by_prefix returns correct subtree)
12. Vacancy handling (vacant role has reduced envelope)

The suite uses the in-memory store implementations (no SQLite needed for integration tests). Real `compile_org()`, real `can_access()`, real `compute_effective_envelope()`.

## Where

- `tests/integration/governance/test_pact_e2e.py`

## Evidence

- All 10+ scenarios pass
- Each scenario uses real PACT types (no mocks of governance functions)
- Audit anchors verified: after each decision, the audit store contains the correct anchor type
- `pytest tests/integration/governance/test_pact_e2e.py -v` shows all tests passing
- No existing tests broken (existing test suite still passes)

## Details

### Test file structure

```python
# tests/integration/governance/test_pact_e2e.py
# Copyright 2026 Terrene Foundation
# SPDX-License-Identifier: Apache-2.0
"""End-to-end integration tests for the PACT governance framework.

Uses the university example vertical to demonstrate all PACT normative
requirements working together: D/T/R grammar, positional addressing,
knowledge clearance, information barriers, bridges, constraint envelopes,
and EATP audit anchors.
"""

import pytest
from pact.examples.university.org import build_university_org
from pact.examples.university.clearance import build_university_clearances
from pact.examples.university.barriers import build_university_barriers, build_university_bridges
from pact.governance.org import compile_org
from pact.governance.access import can_access, AccessDecision
from pact.governance.envelope import compute_effective_envelope
from pact.governance.store import (
    InMemoryOrgStore, InMemoryEnvelopeStore,
    InMemoryClearanceStore, InMemoryAccessPolicyStore,
)


@pytest.fixture(scope="module")
def university_setup():
    """Full university PACT setup: compiled org + all stores populated."""
    # Compile org
    org_def = build_university_org()
    compiled = compile_org(org_def)

    # Populate stores
    org_store = InMemoryOrgStore()
    org_store.store_org("university-2026", compiled.to_dict())

    clearance_store = InMemoryClearanceStore()
    for clearance in build_university_clearances():
        clearance_store.store_clearance(clearance.role_address, clearance.to_dict())

    policy_store = InMemoryAccessPolicyStore()
    for ksp in build_university_barriers():
        policy_store.store_ksp(ksp.policy_id, ksp.to_dict())
    for bridge in build_university_bridges():
        policy_store.store_bridge(bridge.bridge_id, bridge.to_dict())

    return {
        "org_id": "university-2026",
        "compiled": compiled,
        "org_store": org_store,
        "clearance_store": clearance_store,
        "policy_store": policy_store,
    }
```

### Scenario specifications

**Scenario 1: Same-unit access (allowed)**

- Agent: IRB Director (`D1-R1-D3-R1-T1-R1`)
- Item: `/medicine/research/human-subjects/consent-forms.pdf` (SECRET/human-subjects)
- Expected: `ALLOWED`
- Reason: IRB Director has SECRET clearance with `human-subjects` compartment; KSP `ksp-irb-human-subjects` permits this access

**Scenario 2: Cross-unit blocked (no bridge, no KSP)**

- Agent: Dean of Engineering (`D1-R1-D2-R1`)
- Item: `/student-affairs/disciplinary/case-2026-042.pdf` (SECRET/student-disciplinary)
- Expected: `DENIED`
- Reason: No KSP covers Engineering access to Student Affairs disciplinary records; also Dean of Engineering lacks SECRET/student-disciplinary clearance

**Scenario 3: Bridge-mediated access (Standing Bridge)**

- Agent: Provost (`D1-R1`)
- Item: `/administration/financial/budget-fy2026.pdf` (CONFIDENTIAL)
- Expected: `ALLOWED` via `bridge-provost-vpadmin`
- Reason: Standing bridge permits Provost to access Administration financial summaries at CONFIDENTIAL

**Scenario 4: Clearance-independent access denial**

- Agent: Dean of Engineering (`D1-R1-D2-R1`, CONFIDENTIAL clearance)
- Item: `/medicine/research/human-subjects/protocol-nih-2026.pdf` (SECRET/human-subjects)
- Expected: `DENIED`
- Reason: CONFIDENTIAL clearance insufficient for SECRET item; authority (Dean) does not override clearance

**Scenario 5: Compartment enforcement**

- Agent: Director of Clinical Research (`D1-R1-D3-R1-T2-R1`, SECRET/{human-subjects, clinical-trials})
- Item: `/hr/personnel/academic-staff-salaries.xlsx` (SECRET/personnel)
- Expected: `DENIED`
- Reason: No `personnel` compartment in Clinical Research director's clearance; no KSP permits this cross-unit access

**Scenario 6: Posture-capping reduces effective clearance**

- Agent: IRB Director at DELEGATED posture (effective clearance should be RESTRICTED, not SECRET)
- Item: `/medicine/research/human-subjects/consent-forms.pdf` (SECRET/human-subjects)
- Expected: `DENIED`
- Reason: Effective clearance at DELEGATED posture = RESTRICTED (capped below SECRET)
- Assertion: `effective_clearance(irb_clearance, DELEGATED) == RESTRICTED`

**Scenario 7: T-inherits-D envelope (Team cannot exceed Department)**

- Agent: IRB Director (in IRB Office Team under Medicine Department)
- The IRB Office team envelope must be a subset of Medicine Department envelope
- Assertion: `compute_effective_envelope(irb_role_env, medicine_dept_env)` equals Medicine envelope (intersection, since IRB is within Medicine)

**Scenario 8: Effective envelope computation**

- Agent: IRB Director with a task envelope (specific task with tighter constraints)
- Assertion: `compute_effective_envelope(role_env, task_env)` equals the tighter intersection

**Scenario 9: Scoped bridge scope enforcement**

- Agent: Associate Dean for Research (`D1-R1-D2-R1-T1-R1`)
- In-scope item: `/research/joint-bme-2026/results-q1.pdf` → `ALLOWED`
- Out-of-scope item: `/medicine/clinical/all-patients.csv` → `DENIED`

**Scenario 10: Audit trail completeness**

- After running Scenario 2 (denied access), assert that an `AuditAnchor` with action `barrier_enforced` exists in the audit log
- The anchor must have `details["requesting_role"]`, `details["target_item"]`, `details["step_failed"]`, `details["reason"]`

**Scenario 11: Address containment query**

- `org_store.get_nodes_by_prefix("university-2026", "D1-R1-D3")` returns all Medicine department nodes (IRB Office, Clinical Research, Dean of Medicine, their roles)
- Expected: 5 nodes (Dean of Medicine + IRB T + IRB R + Clinical T + Clinical R)

**Scenario 12: Vacancy handling**

- Create a vacancy at Senate Liaison Officer role
- Assertion: the vacant role's effective envelope is the restricted vacancy envelope (not the full role envelope)

### pytest fixtures

The `university_setup` fixture uses `scope="module"` to avoid rebuilding the entire org for each test case. Individual test functions receive it as a parameter and access data through the returned dict.

Each scenario is a separate test function named `test_scenario_<N>_<description>`. No test depends on the side effects of another test (stores are read-only after setup, except for Scenario 12 which creates its own isolated store).
