# 5012: Fix CI pipeline lint/type check paths

**Milestone**: M15 — CI/CD Pipeline
**Priority**: Critical
**Effort**: Small

## What

Fix `.github/workflows/ci.yml` lines 33-34, 39 where lint (ruff) and type checking (mypy) reference `pact/` instead of `src/pact/`. This means CI may be silently passing without actually checking the source code.

## Where

- `.github/workflows/ci.yml` — fix paths from `pact/` to `src/pact/`

## Evidence

- `ruff check src/pact/ tests/` runs on correct directory
- `mypy src/pact/` runs on correct directory
- CI pipeline passes with correct paths (verify locally before pushing)

## Dependencies

- None (highest priority, first fix)
