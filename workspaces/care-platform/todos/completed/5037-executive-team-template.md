# 5037: Executive/leadership team template

**Milestone**: M20 — Template Library Expansion
**Priority**: Medium
**Effort**: Medium

## What

Add executive team template: Chief of Staff + strategy analyst + reporting agent. Broader read access, stricter write access, higher action limits. Suitable for organizational leadership functions.

## Where

- `src/care_platform/templates/registry.py` — add executive template
- `tests/unit/templates/test_registry.py` — add tests

## Evidence

- Template passes full validation suite
- Constraint envelopes reflect leadership pattern (wide read, narrow write)
- Template usable via `care-platform org create --template executive`

## Dependencies

- 5036 (template pattern established)
