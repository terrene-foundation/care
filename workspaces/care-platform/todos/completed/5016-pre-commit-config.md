# 5016: Add pre-commit configuration

**Milestone**: M15 — CI/CD Pipeline
**Priority**: Medium
**Effort**: Small

## What

Create `.pre-commit-config.yaml` with ruff (linting), mypy (type checking), and detect-secrets (credential scanning). These tools are already in dev dependencies.

## Where

- `.pre-commit-config.yaml` — new file at repo root

## Evidence

- `pre-commit run --all-files` passes
- Ruff, mypy, and detect-secrets all run as hooks
- Configuration matches CI pipeline checks

## Dependencies

- 5012 (CI paths fixed — pre-commit should match CI)
