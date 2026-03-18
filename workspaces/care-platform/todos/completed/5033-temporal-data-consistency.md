# 5033: Temporal and data path consistency validation

**Milestone**: M19 — Org Validation Hardening
**Priority**: Medium
**Effort**: Small

## What

Validate that sub-agent temporal windows fall within lead's window, and sub-agent read/write data access paths are subsets of lead's paths. Ensures constraint containment is correct across time and data dimensions.

## Where

- `src/care_platform/org/builder.py` — add to `validate_org()`
- `tests/unit/org/test_builder.py` — add tests (edge cases: overnight windows, path wildcards)

## Evidence

- Validation catches sub-agent with wider time window than lead
- Validation catches sub-agent accessing data paths outside lead's scope
- Edge cases handled (midnight-crossing windows, path glob patterns)

## Dependencies

- 5030 (monotonic tightening — this is a specialization)
