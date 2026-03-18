# Task 6064: Document PyPI Trusted Publisher Setup Steps

**Milestone**: M43
**Priority**: Medium
**Effort**: Small
**Status**: Active

## Description

Publishing to PyPI requires setting up a Trusted Publisher on PyPI (OIDC-based publishing from GitHub Actions, no API keys needed). The setup requires manual steps on the PyPI website that cannot be automated. This task documents those steps clearly so any Foundation member can complete the setup.

The documentation should also cover: TestPyPI setup for dry-run publishing, the GitHub Actions workflow for publishing on tag push, and how to verify a successful publish.

## Acceptance Criteria

- [ ] `docs/publishing.md` (or equivalent) created covering:
  - How to create a PyPI account and register the `care-platform` project (first publish)
  - How to add a Trusted Publisher on PyPI (project → Manage → Publishing → GitHub Actions publisher)
  - Required fields: GitHub org (`terrene-foundation`), repository (`care`), workflow filename, environment name
  - How to add the same on TestPyPI for staging
  - The GitHub Actions publish workflow (`.github/workflows/publish.yml`) — what it does on tag push
  - How to verify the publish succeeded: `pip install care-platform==X.Y.Z` from PyPI
- [ ] `.github/workflows/publish.yml` created (or documented as a template) with the PyPI trusted publisher action
- [ ] No API keys, no PYPI_TOKEN — uses trusted publisher (OIDC) only
- [ ] The workflow is gated on tag push matching `v*.*.*`

## Dependencies

- Task 6002 (pyproject.toml must be correct before any publish attempt)
- Task 6004 (CHANGELOG.md should exist for any release)
