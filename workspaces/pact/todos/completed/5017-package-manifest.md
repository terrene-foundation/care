# 5017: Create MANIFEST.in and validate package build

**Milestone**: M16 — Package Publishing
**Priority**: High
**Effort**: Small

## What

Create `MANIFEST.in` to include LICENSE, README.md, py.typed, and exclude tests/docs. Add a CI step that runs `python -m build` + `twine check dist/*` to catch packaging issues early.

## Where

- `MANIFEST.in` — new file at repo root
- `.github/workflows/ci.yml` — add package build validation step

## Evidence

- `python -m build` produces valid sdist and wheel
- `twine check dist/*` passes with no warnings
- Package includes all necessary files, excludes tests

## Dependencies

- 5012 (CI paths fixed)
