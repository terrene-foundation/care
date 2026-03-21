# TODO-5002: University Clearance Configuration

Status: pending
Priority: high
Dependencies: [5001, 2001]
Milestone: M5

## What

Configure knowledge clearances for the university vertical. The flagship demonstration is clearance independence from authority: the IRB Director (a specialist role several levels below the Dean of Engineering) holds SECRET clearance for the `human-subjects` compartment, while the Dean of Engineering holds only CONFIDENTIAL with no compartments. Authority (position in the hierarchy) does not determine clearance — specialist certification does.

This configuration serves two purposes:

1. It demonstrates the core PACT thesis claim: clearance is orthogonal to authority.
2. It provides the clearance data that the information barrier test (TODO-5003) and the access enforcement tests (TODO-5004) depend on.

### Clearance assignments

| Role                          | Address             | Level        | Compartments                      | Vetting Status |
| ----------------------------- | ------------------- | ------------ | --------------------------------- | -------------- |
| Provost                       | `D1-R1`             | CONFIDENTIAL | —                                 | ACTIVE         |
| VP Academic Affairs           | `D1-R1-D1-R1`       | RESTRICTED   | —                                 | ACTIVE         |
| Committee Chair               | `D1-R1-D1-R1-T1-R1` | RESTRICTED   | —                                 | ACTIVE         |
| Senate Liaison Officer        | `D1-R1-D1-R1-T2-R1` | PUBLIC       | —                                 | ACTIVE         |
| Dean of Engineering           | `D1-R1-D2-R1`       | CONFIDENTIAL | —                                 | ACTIVE         |
| Associate Dean for Research   | `D1-R1-D2-R1-T1-R1` | CONFIDENTIAL | —                                 | ACTIVE         |
| Director of Graduate Studies  | `D1-R1-D2-R1-T2-R1` | RESTRICTED   | —                                 | ACTIVE         |
| Dean of Medicine              | `D1-R1-D3-R1`       | CONFIDENTIAL | —                                 | ACTIVE         |
| IRB Director                  | `D1-R1-D3-R1-T1-R1` | SECRET       | {human-subjects}                  | ACTIVE         |
| Director of Clinical Research | `D1-R1-D3-R1-T2-R1` | SECRET       | {human-subjects, clinical-trials} | ACTIVE         |
| VP Administration             | `D1-R1-D4-R1`       | CONFIDENTIAL | —                                 | ACTIVE         |
| Controller                    | `D1-R1-D4-R1-T1-R1` | CONFIDENTIAL | —                                 | ACTIVE         |
| HR Director                   | `D1-R1-D4-R1-T2-R1` | SECRET       | {personnel}                       | ACTIVE         |
| Dean of Students              | `D1-R1-D5-R1`       | CONFIDENTIAL | —                                 | ACTIVE         |
| Student Conduct Coordinator   | `D1-R1-D5-R1-T1-R1` | SECRET       | {student-disciplinary}            | ACTIVE         |
| Registrar                     | `D1-R1-D5-R1-T2-R1` | RESTRICTED   | —                                 | ACTIVE         |

### Posture-capping demonstration

The IRB Director holds SECRET clearance. Per the POSTURE_CEILING mapping (thesis Section 6.2), an agent with SECRET clearance may not operate at CONTINUOUS_INSIGHT or higher posture — the maximum posture is SUPERVISED. An IRB agent running at DELEGATED posture would have its effective clearance capped to RESTRICTED (below SECRET's ceiling of SUPERVISED).

The test for this must show that `effective_clearance(irb_clearance, TrustPostureLevel.DELEGATED)` returns `RESTRICTED`, not `SECRET`.

## Where

- `src/pact/examples/university/clearance.py` — `build_university_clearances()` function returning a list of `RoleClearance` objects
- `tests/unit/governance/test_university_clearance.py` — clearance assignment tests and posture-capping tests

## Evidence

- `from pact.examples.university.clearance import build_university_clearances` succeeds
- `build_university_clearances()` returns 16 `RoleClearance` objects (one per role)
- IRB Director clearance: `level == SECRET`, `"human-subjects" in compartments`
- Dean of Engineering clearance: `level == CONFIDENTIAL`, `compartments == frozenset()`
- Posture-capping test: `effective_clearance(irb_clearance, TrustPostureLevel.DELEGATED)` returns `RESTRICTED`
- Posture-capping test: `effective_clearance(irb_clearance, TrustPostureLevel.SUPERVISED)` returns `SECRET` (posture compatible with ceiling)
- Compartment test: IRB Director `has_compartment("human-subjects")` is True; Dean of Engineering `has_compartment("human-subjects")` is False
- `pytest tests/unit/governance/test_university_clearance.py` passes

## Details

### build_university_clearances function

```python
# src/pact/examples/university/clearance.py
from __future__ import annotations

from pact.governance.clearance import RoleClearance, VettingStatus
from pact.build.config.schema import ConfidentialityLevel


def build_university_clearances() -> list[RoleClearance]:
    """Return RoleClearance assignments for all university roles.

    Key demonstration: IRB Director (specialist) holds SECRET/human-subjects
    clearance while Dean of Engineering (authority figure) holds only
    CONFIDENTIAL (no compartments). Clearance is orthogonal to authority.
    """
    return [
        RoleClearance(
            role_address="D1-R1",
            level=ConfidentialityLevel.CONFIDENTIAL,
            compartments=frozenset(),
            vetting_status=VettingStatus.ACTIVE,
        ),
        # ... all 16 roles
        RoleClearance(
            role_address="D1-R1-D3-R1-T1-R1",  # IRB Director
            level=ConfidentialityLevel.SECRET,
            compartments=frozenset({"human-subjects"}),
            vetting_status=VettingStatus.ACTIVE,
        ),
        RoleClearance(
            role_address="D1-R1-D2-R1",  # Dean of Engineering
            level=ConfidentialityLevel.CONFIDENTIAL,
            compartments=frozenset(),
            vetting_status=VettingStatus.ACTIVE,
        ),
        # ... remaining roles per table above
    ]
```

### Posture-capping narrative (for documentation use)

The university vertical illustrates why clearance independence from authority matters:

- An IRB researcher conducting a large longitudinal human-subjects study needs SECRET/human-subjects clearance to access participant data, consent forms, and adverse event reports.
- The Dean of Engineering oversees the CS and ECE departments — a senior authority role — but has no legitimate need to access human-subjects research data. Their CONFIDENTIAL clearance reflects their actual knowledge access needs.
- If a CS department agent operating at CONTINUOUS_INSIGHT posture attempted to access human-subjects data, the Access Enforcement Algorithm would deny it at two independent steps: (1) insufficient clearance (CONFIDENTIAL < SECRET), and (2) missing compartment (`human-subjects` not in their compartment set).

This independence is not about distrust of the Dean — it is about structuring the organization so that authority does not automatically confer access to sensitive research participant data.
