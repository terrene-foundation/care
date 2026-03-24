# TODO-0003: Governance Package Scaffold

Status: pending
Priority: critical
Dependencies: []
Milestone: M0

## What

Create the `src/pact/governance/` package and its six empty module files. Create the
`tests/unit/governance/` test directory with a `conftest.py`. Nothing in these files
is implemented yet — this task establishes the package structure that all M1 tasks
depend on.

The governance package is the new home for all PACT-specific domain logic: positional
addressing, org compilation, knowledge clearance, access enforcement, operating
envelopes, and the governance store. It is entirely separate from `src/pact/build/`
(org loading and YAML config), `src/pact/trust/` (EATP cryptographic trust), and
`src/pact/use/` (runtime execution).

## Where

New files to create:

`src/pact/governance/__init__.py`

- Copyright header
- Module docstring: "PACT governance — D/T/R addressing, org compilation, knowledge
  clearance, access enforcement, and operating envelope management."
- Export list: empty for now (`__all__: list[str] = []`)

`src/pact/governance/addressing.py`

- Copyright header
- Docstring: "Positional addressing — D/T/R grammar and Address value type."
- `__all__: list[str] = []`
- No implementation yet

`src/pact/governance/compilation.py`

- Copyright header
- Docstring: "Org compilation — parse OrgDefinition into addressed CompiledOrg."
- `__all__: list[str] = []`
- No implementation yet

`src/pact/governance/clearance.py`

- Copyright header
- Docstring: "Knowledge clearance — RoleClearance, compartments, and barrier crossing."
- `__all__: list[str] = []`
- No implementation yet

`src/pact/governance/access.py`

- Copyright header
- Docstring: "Access enforcement — 5-step access enforcement algorithm."
- `__all__: list[str] = []`
- No implementation yet

`src/pact/governance/envelopes.py`

- Copyright header
- Docstring: "Operating envelopes — RoleEnvelope, TaskEnvelope, effective envelope."
- `__all__: list[str] = []`
- No implementation yet

`src/pact/governance/store.py`

- Copyright header
- Docstring: "Governance store protocols — persistence interfaces for governance state."
- `__all__: list[str] = []`
- No implementation yet

`tests/unit/governance/__init__.py`

- Empty (pytest discovery marker)

`tests/unit/governance/conftest.py`

- Copyright header
- Docstring: "Shared fixtures for governance unit tests."
- No fixtures yet — placeholder only

## Evidence

- `python -c "from pact.governance import addressing"` exits 0 with no error
- `python -c "from pact.governance import compilation"` exits 0
- `python -c "from pact.governance import clearance"` exits 0
- `python -c "from pact.governance import access"` exits 0
- `python -c "from pact.governance import envelopes"` exits 0
- `python -c "from pact.governance import store"` exits 0
- `pytest tests/unit/governance/ --collect-only` reports "no tests ran" (not an error —
  the package is discovered, but no test functions exist yet)
- All 6 module files exist at `src/pact/governance/*.py`
- `tests/unit/governance/conftest.py` exists

## Details

### File header template

Every file must start with:

```python
# Copyright 2026 Terrene Foundation
# SPDX-License-Identifier: Apache-2.0
```

### Why separate from build/

`src/pact/build/` handles loading and validating YAML config files. It produces
`OrgDefinition` objects from configuration. The governance package takes those
`OrgDefinition` objects and performs domain operations on them — assigning addresses,
enforcing grammar, computing envelopes, evaluating access. The split keeps IO/config
concerns separate from pure domain logic.

### Why not extend existing modules

The existing modules (`pact.build.config.schema`, `pact.build.org.builder`) are
already stable, tested, and depended upon by hundreds of test cases. Adding the
governance domain to them would entangle two concerns and risk breaking the existing
test suite. A new package with zero dependencies on the existing modules (except
importing `OrgDefinition` as a parameter type) avoids this risk.

### Import direction

The governance package MAY import types from `pact.build.config.schema`
(e.g., `OrgDefinition`, `AgentConfig`, `ConstraintEnvelopeConfig`) as input parameter
types. It must NOT import from `pact.trust` or `pact.use`. Those packages may later
import from `pact.governance`, but not the reverse — governance is a pure domain layer
with no execution or cryptographic dependencies.
