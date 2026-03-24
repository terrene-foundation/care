# 5015: Add security scanning to CI

**Milestone**: M15 — CI/CD Pipeline
**Priority**: Medium
**Effort**: Small

## What

Add `pip-audit` or `safety` dependency vulnerability scanning to CI. Optionally add CodeQL analysis for Python static analysis.

## Where

- `.github/workflows/ci.yml` — add security scanning step
- `pyproject.toml` — add `pip-audit` to dev dependencies if needed

## Evidence

- CI runs dependency vulnerability scanning
- No critical vulnerabilities in current dependencies
- Results visible in CI output

## Dependencies

- 5012 (CI paths fixed)
