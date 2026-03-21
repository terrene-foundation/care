# M13-T01: Move pact/ to src/pact/

**Status**: ACTIVE
**Priority**: Critical
**Milestone**: M13 — Project Restructure
**Dependencies**: None (first task)
**Effort**: Small (high blast radius)

## What

Move the entire `pact/` directory to `src/pact/`. This is the Python `src/` layout best practice — prevents accidental imports from the working directory.

## Where

- `src/pact/` (new location for all 60 Python modules)
- Remove stale `pact.egg-info/`

## Evidence

- `ls src/pact/__init__.py` succeeds
- `ls pact/` fails (old location gone)
- `python -c "import pact"` works after `pip install -e .`

## Risk

HIGH blast radius — 136 internal cross-module imports, 369 test import references, eager loading in `__init__.py`. Must be atomic.
