# 5035: Validation error severity levels

**Milestone**: M19 — Org Validation Hardening
**Priority**: Medium
**Effort**: Small

## What

Add severity levels (ERROR vs WARNING) to validation results. Structural errors (dangling references, duplicate IDs) are ERRORs that block building. Coverage gaps (unmatched capabilities, wide windows) are WARNINGs that allow building with notification.

## Where

- `src/pact/org/builder.py` — refactor `validate_org()` return type
- `src/pact/cli/__init__.py` — display warnings vs errors differently

## Evidence

- `validate_org()` returns `(bool, list[ValidationResult])` with severity per result
- `build()` blocks on ERRORs, allows WARNINGs with log output
- CLI shows warnings in yellow, errors in red

## Dependencies

- 5029-5034 (all validation rules must exist to classify them)
