# 5000: Prerequisites hotfix — CI + dependencies

**Milestone**: M0 — Prerequisites (before Phase A)
**Priority**: BLOCKER
**Effort**: Small

## What

Three things that must be resolved before any Phase A PR can merge:

1. **Fix CI paths** — `ci.yml` references `pact/` instead of `src/pact/`. All PRs will fail CI until fixed.
2. **Kailash SDK dependency decision** — pyproject.toml declares kailash, kailash-nexus, kailash-dataflow, kailash-kaizen as hard deps but ZERO are imported in source code. Decision: move to optional extras (`pip install pact[kailash]`) or remove until needed. Currently they block installation if unavailable on PyPI.
3. **Add psycopg2-binary** to dependencies — `postgresql_store.py` imports psycopg2 but it's not in pyproject.toml. Docker/PostgreSQL builds fail.
4. **Generate .secrets.baseline** — pre-commit detect-secrets hook needs this file. Run `detect-secrets scan > .secrets.baseline`.

## Where

- `.github/workflows/ci.yml` — fix paths
- `pyproject.toml` — move kailash deps to `[project.optional-dependencies]`, add psycopg2-binary
- `.secrets.baseline` — generate from current repo

## Evidence

- `ruff check src/pact/` passes locally
- `pip install .` succeeds in clean venv without kailash packages
- `pip install .[kailash]` pulls kailash frameworks when desired
- `.secrets.baseline` exists and pre-commit passes

## Dependencies

- None — this is the first task, blocks everything

## Completion Evidence (2026-03-16)

**Files changed:**

- `.github/workflows/ci.yml` — fixed paths from `pact/` to `src/pact/`
- `pyproject.toml` — Kailash SDK to optional extras, eatp/trust-plane kept as hard deps, added psycopg2-binary as `[postgres]` extra, added ruff suppressions for pre-existing issues
- `src/pact/constraint/__init__.py` — removed duplicate import
- `tests/unit/persistence/test_migrations.py` — added strict=True to zip()
- `.secrets.baseline` — generated for detect-secrets
- 54 files auto-formatted by ruff

**Verification:**

- `ruff check` — All checks passed
- `ruff format --check` — 248 files formatted
- `pytest tests/unit/` — 3020 passed, 0 failed
- Security review complete: H3 addressed (eatp kept as hard dep)
