# 5013: Add integration test job to CI

**Milestone**: M15 — CI/CD Pipeline
**Priority**: High
**Effort**: Medium

## What

Add a CI job that runs integration tests (`pytest tests/integration/`) with seed data. Currently CI only runs unit tests. Integration tests verify the API layer, seed data, and component wiring work together.

## Where

- `.github/workflows/ci.yml` — add `integration-test` job
- `tests/integration/` — ensure integration tests exist and are discoverable

## Evidence

- CI has a separate `integration-test` job
- Integration tests run against seeded data
- Job passes in CI

## Dependencies

- 5012 (CI paths must be correct first)
