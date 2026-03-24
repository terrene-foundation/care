# 5030: Generic monotonic constraint tightening validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: High
**Effort**: Medium

## What

Add generic validation to `validate_org()` that enforces sub-agent envelopes are tighter than team lead across all 5 CARE dimensions (financial, operational, temporal, data_access, communication). Currently `dm_team.py` does this manually — make it generic for any org definition.

## Where

- `src/pact/org/builder.py` — add tightening validation to `validate_org()`
- `src/pact/constraint/` — reuse existing `is_tighter_than()` logic
- `tests/unit/org/test_builder.py` — add tests

## Evidence

- `validate_org()` catches sub-agent envelopes wider than team lead
- All 5 dimensions validated independently
- DM team config passes this generic validation (proving parity with manual check)

## Dependencies

- 5029 (capability validation first)
