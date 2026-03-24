# TODO-6001: Exhaustive Access Enforcement Test Matrix

Status: pending
Priority: high
Dependencies: [2006]
Milestone: M6

## What

Create a comprehensive test matrix for the 5-step Access Enforcement Algorithm. The matrix covers every combination of the six independent variables, generating 100+ test cases that prove the algorithm is correct across its full input space. The goal is to prove two properties simultaneously: (1) no false positives — nothing is allowed that should be denied, and (2) no false negatives — nothing is denied that should be allowed.

The six independent variables:

| Variable                    | Values                                                                             |
| --------------------------- | ---------------------------------------------------------------------------------- |
| Organizational relationship | same-unit, parent-child, cross-unit sibling, cross-org                             |
| KSP presence                | no KSP, KSP present (matching), KSP present (not matching)                         |
| Bridge presence             | no bridge, active bridge (in scope), active bridge (out of scope), revoked bridge  |
| Clearance level             | PUBLIC, RESTRICTED, CONFIDENTIAL, SECRET, TOP_SECRET (each vs item classification) |
| Trust posture               | PSEUDO_AGENT, SUPERVISED, SHARED_PLANNING, CONTINUOUS_INSIGHT, DELEGATED           |
| Compartments                | required + present, required + absent, not required                                |

Not all combinations are independent (some are physically impossible, e.g., cross-unit without KSP + allowed is impossible). The test matrix must enumerate the valid combinations and verify the correct outcome for each.

## Where

- `tests/unit/governance/test_access_matrix.py`

## Evidence

- At least 100 test cases in the matrix
- Zero false positives: every case where the expected outcome is `DENIED` actually returns `DENIED`
- Zero false negatives: every case where the expected outcome is `ALLOWED` actually returns `ALLOWED`
- Matrix is parameterized using `@pytest.mark.parametrize` (not 100+ individual test functions)
- Coverage report shows `pact.governance.access` at 100% branch coverage
- `pytest tests/unit/governance/test_access_matrix.py -v` passes

## Details

### Matrix structure

Use `pytest.mark.parametrize` with a list of named tuples or dicts. Each entry specifies:

```python
import pytest
from dataclasses import dataclass
from typing import NamedTuple

class MatrixCase(NamedTuple):
    case_id: str                        # Human-readable identifier
    org_relationship: str               # "same_unit", "parent_child", "cross_unit", "cross_org"
    ksp_config: str                     # "none", "matching", "not_matching"
    bridge_config: str                  # "none", "active_in_scope", "active_out_of_scope", "revoked"
    requester_clearance: str            # ConfidentialityLevel name
    item_classification: str            # ConfidentialityLevel name
    posture: str                        # TrustPostureLevel name
    compartments_required: list[str]    # e.g., ["human-subjects"]
    requester_compartments: list[str]   # what the requester has
    expected: str                       # "ALLOWED" or "DENIED"
    denied_at_step: int | None          # Which step should produce denial (None if ALLOWED)
```

### Key invariants to test

**Invariant 1: Default-deny**
Every combination where there is no permitting KSP or bridge must produce `DENIED`. Test at least 20 default-deny cases.

**Invariant 2: Clearance must meet item level**
Even with a permitting KSP, if the requester's clearance (after posture-capping) is below the item's classification, access is `DENIED`. Test all 25 combinations of (5 clearance levels) × (5 item classifications).

**Invariant 3: Compartment independence**
For SECRET+ items with required compartments: clearance level alone is insufficient. The requester must have the required compartment. Test all 4 compartment combinations: (required+present, required+absent, not-required+present, not-required+absent).

**Invariant 4: Posture-capping**
For each clearance level, test that the POSTURE_CEILING is enforced. An agent at DELEGATED with CONFIDENTIAL clearance has effective clearance of RESTRICTED. Test all 25 combinations.

**Invariant 5: Revoked bridge is no bridge**
A revoked bridge must not mediate access. Test: bridge exists but status=revoked → same result as no bridge.

**Invariant 6: Bridge scope enforcement**
Access mediated by a Scoped bridge must be restricted to the bridge's item prefix. Test: valid bridge, item outside scope → `DENIED`.

**Invariant 7: T-inherits-D**
A Team role can never have a permissive access path that the parent Department does not have. Test: cross-unit access for a Team role when the parent Department would be denied → still `DENIED`.

### Parameterized test structure

```python
@pytest.mark.parametrize("case", ACCESS_MATRIX_CASES, ids=[c.case_id for c in ACCESS_MATRIX_CASES])
def test_access_matrix(case: MatrixCase, access_matrix_fixtures):
    """Run one case from the access enforcement matrix.

    access_matrix_fixtures provides a factory function that builds the
    appropriate stores configuration for the given case parameters.
    """
    stores = access_matrix_fixtures.build(case)
    result = can_access(
        requester_address=stores.requester_address,
        knowledge_item=stores.knowledge_item,
        compiled_org=stores.compiled_org,
        clearance_store=stores.clearance_store,
        policy_store=stores.policy_store,
        posture=case.posture,
    )
    assert result.decision == case.expected, (
        f"Case {case.case_id}: expected {case.expected}, got {result.decision}. "
        f"Denial reason: {result.reason}"
    )
    if case.expected == "DENIED" and case.denied_at_step is not None:
        assert result.step_failed == case.denied_at_step, (
            f"Case {case.case_id}: expected denial at step {case.denied_at_step}, "
            f"got step {result.step_failed}"
        )
```

### Cases that must be explicitly present

The following 12 "golden" cases must appear by name in the matrix:

1. `"same_unit_public_item_allowed"` — same unit, no KSP needed, PUBLIC item, any posture → ALLOWED
2. `"cross_unit_no_ksp_denied"` — cross unit, no KSP, CONFIDENTIAL item → DENIED at step 1
3. `"ksp_matching_clearance_sufficient_allowed"` — KSP matches, clearance sufficient → ALLOWED
4. `"ksp_matching_clearance_insufficient_denied"` — KSP matches but requester clearance below item → DENIED at step 3
5. `"bridge_active_in_scope_allowed"` — active bridge, item in scope → ALLOWED
6. `"bridge_revoked_denied"` — bridge exists but revoked, no KSP → DENIED at step 1
7. `"bridge_active_out_of_scope_denied"` — active bridge, item outside scope → DENIED
8. `"compartment_required_present_allowed"` — SECRET item, requester has compartment → ALLOWED (if other conditions met)
9. `"compartment_required_absent_denied"` — SECRET item, requester lacks compartment → DENIED at step 4
10. `"posture_capped_clearance_denied"` — DELEGATED posture caps CONFIDENTIAL→RESTRICTED, item is CONFIDENTIAL → DENIED at step 3
11. `"top_secret_blocked_all_postures"` — TOP_SECRET item, any non-SUPERVISED posture → DENIED
12. `"flagship_cs_agent_student_records"` — Engineering agent, Student Affairs disciplinary record → DENIED (university flagship)
