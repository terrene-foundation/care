# 5036: Engineering team template

**Milestone**: M20 — Template Library Expansion
**Priority**: Medium
**Effort**: Medium

## What

Add engineering/development team template to TemplateRegistry: team lead + code reviewer + testing agent + deployment agent. Envelopes: code read/write, CI trigger access, no production deploy without approval.

## Where

- `src/pact/templates/registry.py` — add engineering template
- `tests/unit/templates/test_registry.py` — add tests

## Evidence

- `TemplateRegistry` includes "engineering" template
- Template passes `validate_org()` with all validation rules
- Monotonic tightening verified across team

## Dependencies

- 5029-5035 (validation must be complete to validate new templates)
