# 5032: Verification gradient coverage validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: Medium
**Effort**: Small

## What

Validate that all agent capabilities have at least one matching verification gradient rule (pattern match). Warn (not error) on unmatched capabilities — ensures the verification gradient doesn't have blind spots.

## Where

- `src/care_platform/org/builder.py` — add gradient coverage check
- `tests/unit/org/test_builder.py` — add tests

## Evidence

- Validation warns when an agent capability has no matching gradient rule
- Uses WARNING severity (not ERROR) per the validation severity system
- DM team config has full coverage

## Dependencies

- 5029, 5030 (part of validation sequence)
