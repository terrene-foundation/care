# 5012: Fix CI pipeline lint/type check paths

**Milestone**: M15 — CI/CD Pipeline
**Priority**: Critical
**Effort**: Small

## What

Fix `.github/workflows/ci.yml` lines 33-34, 39 where lint (ruff) and type checking (mypy) reference `care_platform/` instead of `src/care_platform/`. This means CI may be silently passing without actually checking the source code.

## Where

- `.github/workflows/ci.yml` — fix paths from `care_platform/` to `src/care_platform/`

## Evidence

- `ruff check src/care_platform/ tests/` runs on correct directory
- `mypy src/care_platform/` runs on correct directory
- CI pipeline passes with correct paths (verify locally before pushing)

## Dependencies

- None (highest priority, first fix)
