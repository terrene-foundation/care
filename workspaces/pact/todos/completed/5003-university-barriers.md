# TODO-5003: University Information Barriers and Bridges

Status: pending
Priority: high
Dependencies: [5001, 2003, 2004]
Milestone: M5

## What

Configure information barriers (KnowledgeSharePolicies that enforce separation) and Cross-Functional Bridges for the university vertical. This demonstrates the two sides of the access policy layer: barriers prevent cross-silo access by default, while bridges create governed exceptions.

### Barriers (default-deny across units)

The flagship barrier: Faculty personnel records (held by HR) are separated from Student disciplinary records (held by the Conduct Office). Neither side can access the other's records without a bridge.

Additional barriers:

- Engineering research data is separated from Medicine clinical research data (no cross-departmental data sharing without a scoped bridge)
- Administration financial data is separated from Academic Affairs records

### Bridges (governed exceptions)

Three bridges to configure:

1. **Standing Bridge — Provost ↔ VP Administration**: Budget coordination. The Provost may read Administration financial summaries (CONFIDENTIAL). The VP Admin may read Academic Affairs staffing cost summaries (CONFIDENTIAL). Scope: financial planning documents only.

2. **Scoped Bridge — Engineering ↔ Medicine (Joint Research)**: A time-limited collaboration bridge for a joint bio-medical engineering research project. Engineering's Associate Dean for Research may access Medicine's clinical research data at CONFIDENTIAL level. Scope: joint research project documents (`/research/joint-bme-2026/`) only. The bridge has an expiry and requires IRB approval for human-subjects data.

3. **Standing Bridge — HR Director ↔ Dean of Students**: Employee student conduct referrals. HR may access student conduct summaries (not full records) when an employee is also a student. Scope: summaries only, no full disciplinary files. Classification: RESTRICTED.

## Where

- `src/pact/examples/university/barriers.py` — `build_university_barriers()` and `build_university_bridges()` functions
- `tests/unit/governance/test_university_barriers.py` — barrier enforcement and bridge-mediated access tests

## Evidence

- `from pact.examples.university.barriers import build_university_barriers, build_university_bridges` succeeds
- `build_university_barriers()` returns at least 3 `KnowledgeSharePolicy` objects defining the separation rules
- `build_university_bridges()` returns exactly 3 `PactBridge` objects
- Flagship test: `can_access(engineering_agent, student_conduct_record, compiled_org, clearance_store, policy_store)` returns `DENIED` (no KSP covers this, barrier applies)
- Bridge test: `can_access(provost_agent, admin_financial_summary, ...)` returns `ALLOWED` via Standing Bridge
- Scoped bridge test: `can_access(assoc_dean_research_agent, joint_research_doc, ...)` returns `ALLOWED` via Scoped Bridge
- Scoped bridge test: `can_access(assoc_dean_research_agent, medicine_clinical_all_patients_doc, ...)` returns `DENIED` (outside bridge scope)
- `pytest tests/unit/governance/test_university_barriers.py` passes

## Details

### build_university_barriers

Barriers are represented as `KnowledgeSharePolicy` objects that define what IS permitted. The absence of a permitting KSP is default-deny. In the university model, the "barriers" are the natural consequence of the absence of KSPs — no KSP covering Engineering→StudentConductRecords means the barrier holds.

However, explicit "barrier marker" KSPs may be created to record the intent and provide better error messages when access is denied. These are KSPs with `status="barrier"` or an equivalent marker field that the audit anchor picks up in `BARRIER_ENFORCED` events.

```python
# src/pact/examples/university/barriers.py
from __future__ import annotations

from pact.governance.barrier import KnowledgeSharePolicy, KspType
from pact.governance.bridge import PactBridge, BridgeType
from pact.build.config.schema import ConfidentialityLevel


def build_university_barriers() -> list[KnowledgeSharePolicy]:
    """Return KSPs that define access permissions (absence = denied).

    The university has three key separations:
    1. HR personnel records separated from Student disciplinary records.
    2. Engineering research data separated from Medicine clinical data.
    3. Administration financial data separated from Academic Affairs.
    """
    return [
        # Within-unit access: HR Director may access HR personnel records
        KnowledgeSharePolicy(
            policy_id="ksp-hr-personnel",
            permitted_requester_prefix="D1-R1-D4-R1-T2",  # HR team prefix
            knowledge_item_prefix="/hr/personnel/",
            max_classification=ConfidentialityLevel.SECRET,
            required_compartments=frozenset({"personnel"}),
            description="HR personnel records: HR team only",
        ),
        # Within-unit access: Conduct Office may access disciplinary records
        KnowledgeSharePolicy(
            policy_id="ksp-conduct-disciplinary",
            permitted_requester_prefix="D1-R1-D5-R1-T1",  # Conduct Office prefix
            knowledge_item_prefix="/student-affairs/disciplinary/",
            max_classification=ConfidentialityLevel.SECRET,
            required_compartments=frozenset({"student-disciplinary"}),
            description="Student disciplinary records: Conduct Office only",
        ),
        # Within-unit access: IRB Office may access human-subjects data
        KnowledgeSharePolicy(
            policy_id="ksp-irb-human-subjects",
            permitted_requester_prefix="D1-R1-D3-R1-T1",  # IRB Office prefix
            knowledge_item_prefix="/medicine/research/human-subjects/",
            max_classification=ConfidentialityLevel.SECRET,
            required_compartments=frozenset({"human-subjects"}),
            description="Human subjects research data: IRB Office only",
        ),
        # Administration financial data: Administration dept only
        KnowledgeSharePolicy(
            policy_id="ksp-admin-financial",
            permitted_requester_prefix="D1-R1-D4",  # Admin dept prefix
            knowledge_item_prefix="/administration/financial/",
            max_classification=ConfidentialityLevel.CONFIDENTIAL,
            required_compartments=frozenset(),
            description="Financial records: Administration department",
        ),
    ]
```

### build_university_bridges

```python
def build_university_bridges() -> list[PactBridge]:
    """Return the three Cross-Functional Bridges for the university.

    1. Standing: Provost <-> VP Administration (budget coordination)
    2. Scoped: Engineering Research <-> Medicine Clinical (joint research)
    3. Standing: HR Director <-> Dean of Students (employee-student referrals)
    """
    return [
        PactBridge(
            bridge_id="bridge-provost-vpadmin",
            bridge_type=BridgeType.STANDING,
            side_a="D1-R1",           # Provost
            side_b="D1-R1-D4-R1",     # VP Administration
            permitted_classifications=[ConfidentialityLevel.CONFIDENTIAL],
            side_a_item_prefix="/administration/financial/",
            side_b_item_prefix="/academic-affairs/staffing/",
            description="Provost-VP Admin standing bridge for budget coordination",
            status="active",
        ),
        PactBridge(
            bridge_id="bridge-eng-med-joint-research",
            bridge_type=BridgeType.SCOPED,
            side_a="D1-R1-D2-R1-T1-R1",   # Associate Dean for Research (Eng)
            side_b="D1-R1-D3-R1-T2-R1",   # Director of Clinical Research (Med)
            permitted_classifications=[ConfidentialityLevel.CONFIDENTIAL],
            side_a_item_prefix="/research/joint-bme-2026/",
            side_b_item_prefix="/research/joint-bme-2026/",
            description="Engineering-Medicine scoped bridge: joint BME research project",
            status="active",
            scope_note="Joint bio-medical engineering project 2026. No human-subjects data without separate IRB approval.",
        ),
        PactBridge(
            bridge_id="bridge-hr-conduct",
            bridge_type=BridgeType.STANDING,
            side_a="D1-R1-D4-R1-T2-R1",   # HR Director
            side_b="D1-R1-D5-R1",          # Dean of Students
            permitted_classifications=[ConfidentialityLevel.RESTRICTED],
            side_a_item_prefix="/hr/personnel/",
            side_b_item_prefix="/student-affairs/disciplinary/summaries/",
            description="HR-Student Affairs bridge: employee-student referrals (summaries only)",
            status="active",
        ),
    ]
```

### Flagship scenario test specification

The test in `test_university_barriers.py` must cover:

1. **Blocked (no bridge)**: An Engineering CS-department agent (address prefix `D1-R1-D2`) attempts to access `student_conduct_record` at `SECRET/student-disciplinary`. Expected: `DENIED`. Step that should fail: Step 1 (no KSP permitting this access) or Step 3 (insufficient clearance).

2. **Allowed via Standing Bridge**: Provost agent accesses `/administration/financial/budget-fy2026.pdf` at CONFIDENTIAL. Expected: `ALLOWED` via `bridge-provost-vpadmin`.

3. **Allowed via Scoped Bridge (in scope)**: Associate Dean for Research accesses `/research/joint-bme-2026/methods.pdf` at CONFIDENTIAL. Expected: `ALLOWED` via `bridge-eng-med-joint-research`.

4. **Denied via Scoped Bridge (out of scope)**: Associate Dean for Research accesses `/medicine/clinical/all-patients-2026.csv` (outside joint research scope). Expected: `DENIED`.

5. **Denied — compartment wall**: Dean of Engineering accesses `/medicine/research/human-subjects/consent-forms.pdf` at SECRET/human-subjects. Expected: `DENIED` at Step 3 (clearance insufficient: CONFIDENTIAL < SECRET).
