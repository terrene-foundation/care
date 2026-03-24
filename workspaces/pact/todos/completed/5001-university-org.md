# TODO-5001: University Example Vertical — D/T/R Structure

Status: pending
Priority: high
Dependencies: [1003]
Milestone: M5

## What

Create the university example vertical as the canonical demonstration of PACT's D/T/R grammar. The university is chosen because it has natural information barriers (faculty records vs. student disciplinary records), clearance independence from authority (a junior IRB researcher has higher clearance than a Dean for human-subjects data), and cross-functional bridges (Provost–VP Admin budget coordination, Engineering–Medicine joint research).

The org must be at least 4 levels deep and have at least 15 nodes in the compiled tree. Every D (Department) and T (Team) must be immediately followed by exactly one R (Role) — the D/T/R grammar core invariant. The `compile_org()` function from TODO-1003 must succeed without errors.

### D/T/R structure specification

Top level (L1):

- D: Office of the Provost
  - R: Provost

Departments under Provost (L2 Departments):

- D: Academic Affairs
  - R: Vice Provost for Academic Affairs
  - T: Curriculum Committee
    - R: Committee Chair
  - T: Faculty Senate Liaison
    - R: Senate Liaison Officer
- D: Engineering
  - R: Dean of Engineering
  - T: Research Office (Engineering)
    - R: Associate Dean for Research
  - T: Graduate Programs
    - R: Director of Graduate Studies
- D: Medicine
  - R: Dean of Medicine
  - T: IRB Office
    - R: IRB Director
  - T: Clinical Research
    - R: Director of Clinical Research
- D: Administration
  - R: VP Administration
  - T: Finance
    - R: Controller
  - T: Human Resources
    - R: HR Director
- D: Student Affairs
  - R: Dean of Students
  - T: Conduct Office
    - R: Student Conduct Coordinator
  - T: Registrar
    - R: Registrar

This gives: 1 (Provost D) + 5 departments × ~3 nodes each = ~16+ nodes. Satisfies the 15-node minimum.

## Where

- `src/pact/examples/university/__init__.py` — package marker with `__all__`
- `src/pact/examples/university/org.py` — `build_university_org()` function that returns a compiled org

## Evidence

- `from pact.examples.university.org import build_university_org` succeeds
- `compile_org(build_university_org())` returns a `CompiledOrg` without error
- Compiled org has at least 15 nodes
- Every D/T node has exactly one immediately-following R sibling (grammar invariant)
- Positional addresses are computed correctly (e.g., Provost = `D1-R1`, Dean of Engineering = `D1-R1-D3-R1`, IRB Director = `D1-R1-D4-R1-T1-R1`)
- `pytest tests/unit/governance/test_university_org.py` passes

## Details

### build_university_org function

```python
# src/pact/examples/university/org.py
# Copyright 2026 Terrene Foundation
# SPDX-License-Identifier: Apache-2.0
"""University example vertical — D/T/R structure.

Demonstrates PACT D/T/R grammar with a 4-level university organization.
Used in integration tests, documentation, and as a reference for how to
define a PACT organization using the framework-agnostic OrgDefinition API.
"""

from __future__ import annotations

from pact.governance.org import OrgDefinition, DepartmentConfig, TeamConfig, RoleDefinition

def build_university_org() -> OrgDefinition:
    """Return an OrgDefinition for a representative university.

    Structure (4 levels deep):
        Office of the Provost (D)
          Provost (R)
          Academic Affairs (D)
            VP for Academic Affairs (R)
            Curriculum Committee (T)
              Committee Chair (R)
            Faculty Senate Liaison (T)
              Senate Liaison Officer (R)
          Engineering (D)
            Dean of Engineering (R)
            Research Office (T)
              Associate Dean for Research (R)
            Graduate Programs (T)
              Director of Graduate Studies (R)
          Medicine (D)
            Dean of Medicine (R)
            IRB Office (T)
              IRB Director (R)
            Clinical Research (T)
              Director of Clinical Research (R)
          Administration (D)
            VP Administration (R)
            Finance (T)
              Controller (R)
            Human Resources (T)
              HR Director (R)
          Student Affairs (D)
            Dean of Students (R)
            Conduct Office (T)
              Student Conduct Coordinator (R)
            Registrar (T)
              Registrar (R)
    """
    ...
```

### Address assignments (expected)

After `compile_org()`, the following addresses should be assigned. These are deterministic based on the order of definition:

| Role                          | Expected Address    |
| ----------------------------- | ------------------- |
| Provost                       | `D1-R1`             |
| VP Academic Affairs           | `D1-R1-D1-R1`       |
| Committee Chair               | `D1-R1-D1-R1-T1-R1` |
| Senate Liaison Officer        | `D1-R1-D1-R1-T2-R1` |
| Dean of Engineering           | `D1-R1-D2-R1`       |
| Associate Dean for Research   | `D1-R1-D2-R1-T1-R1` |
| Director of Graduate Studies  | `D1-R1-D2-R1-T2-R1` |
| Dean of Medicine              | `D1-R1-D3-R1`       |
| IRB Director                  | `D1-R1-D3-R1-T1-R1` |
| Director of Clinical Research | `D1-R1-D3-R1-T2-R1` |
| VP Administration             | `D1-R1-D4-R1`       |
| Controller                    | `D1-R1-D4-R1-T1-R1` |
| HR Director                   | `D1-R1-D4-R1-T2-R1` |
| Dean of Students              | `D1-R1-D5-R1`       |
| Student Conduct Coordinator   | `D1-R1-D5-R1-T1-R1` |
| Registrar                     | `D1-R1-D5-R1-T2-R1` |

### Package init

```python
# src/pact/examples/university/__init__.py
"""University example vertical for PACT framework demonstrations."""

from pact.examples.university.org import build_university_org

__all__ = ["build_university_org"]
```

### What to import

`build_university_org()` only uses `pact.governance` types — no imports from `pact.trust` or `pact.build`. The university example is a pure governance-layer demonstration.

The result of `build_university_org()` is passed to `compile_org()` to produce a `CompiledOrg`. The `CompiledOrg` is what subsequent university todos (5002, 5003) use to configure clearances and barriers.

### Boundary check

After this todo, running the boundary check command must still return clean:

```bash
grep -rn 'DmTeam\|dm_team\|DigitalMedia\|digital_media\|FoundationOrg\|foundation_org' \
  src/pact/build/ src/pact/trust/ src/pact/use/
```

The university org code lives in `src/pact/examples/university/` and is not subject to the framework boundary rule. The `src/pact/build/`, `src/pact/trust/`, and `src/pact/use/` directories must remain domain-vocabulary-free.
