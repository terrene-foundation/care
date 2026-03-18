# 5034: Foundation-level multi-team validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: High
**Effort**: Medium

## What

Create comprehensive multi-team validation: no overlapping agent IDs across teams, no contradictory envelope rules, bridge endpoints reference valid teams, workspace paths don't conflict. This validates the entire organization as a coherent unit.

## Where

- `src/care_platform/org/builder.py` — add `validate_multi_team()` method
- `tests/unit/org/test_builder.py` — add multi-team tests

## Evidence

- Catches duplicate agent IDs across different teams
- Catches bridge references to non-existent teams
- Catches workspace path conflicts
- Foundation template passes multi-team validation

## Dependencies

- 5029-5033 (per-team validation must work first)
