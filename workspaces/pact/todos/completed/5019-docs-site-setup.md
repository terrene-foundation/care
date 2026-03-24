# 5019: Set up documentation site

**Milestone**: M17 — Documentation Site
**Priority**: High
**Effort**: Medium

## What

Set up MkDocs (or Sphinx with MyST-Parser) to build a documentation site from the existing `docs/` markdown files. Configure navigation, theme, and search. The existing docs include architecture.md, getting-started.md, api.md, cookbook.md, operator-guide.md, environment-config.md.

## Where

- `mkdocs.yml` (or `docs/conf.py` for Sphinx) — documentation configuration
- `docs/` — existing markdown files become the content source

## Evidence

- `mkdocs build` (or `make html`) produces a complete docs site
- Navigation covers all existing documentation sections
- Build produces no warnings

## Dependencies

- None (can start independently)
