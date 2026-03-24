# 5031: Team lead capability superset validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: Medium
**Effort**: Small

## What

Validate that team leads hold all capabilities that any sub-agent in the team holds. If a sub-agent can "draft_post", the team lead must also have "draft_post" in their capabilities. This ensures the delegation chain makes semantic sense.

## Where

- `src/pact/org/builder.py` — add to `validate_org()`
- `tests/unit/org/test_builder.py` — add tests

## Evidence

- Validation catches team lead missing a sub-agent's capability
- DM team config passes (lead already has superset)

## Dependencies

- 5029, 5030 (part of validation hardening sequence)
