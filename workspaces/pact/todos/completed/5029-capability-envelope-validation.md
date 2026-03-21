# 5029: Capability-envelope alignment validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: High
**Effort**: Medium

## What

Add validation to `OrgDefinition.validate_org()` that verifies each agent's capabilities are a subset of its constraint envelope's `allowed_actions`. Currently only checks that the envelope ID reference exists, not that the content is aligned.

## Where

- `src/pact/org/builder.py` — extend `validate_org()`
- `tests/unit/org/test_builder.py` — add validation tests

## Evidence

- `validate_org()` catches agents with capabilities not covered by their envelope
- Test: agent with "publish" capability but envelope blocks "publish" → validation error
- Existing tests still pass

## Dependencies

- None (Phase B can start after Phase A)
