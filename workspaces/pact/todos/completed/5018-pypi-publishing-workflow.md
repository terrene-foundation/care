# 5018: Add PyPI publishing workflow

**Milestone**: M16 — Package Publishing
**Priority**: High
**Effort**: Medium

## What

Create GitHub Actions workflow triggered on release tags that builds sdist+wheel and publishes to PyPI. Use TestPyPI for initial validation. Include version bump synchronization between `pyproject.toml` and `__version__`.

## Where

- `.github/workflows/publish.yml` — new workflow for PyPI publishing
- `src/pact/__init__.py` — ensure `__version__` matches pyproject.toml

## Evidence

- Release tag triggers publish workflow
- Package published to TestPyPI successfully
- `pip install pact` from TestPyPI works
- Version numbers consistent across pyproject.toml and **init**.py

## Dependencies

- 5017 (package must build cleanly first)
