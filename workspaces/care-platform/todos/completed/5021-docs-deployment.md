# 5021: Deploy docs to GitHub Pages

**Milestone**: M17 — Documentation Site
**Priority**: Medium
**Effort**: Small

## What

Add GitHub Actions workflow to build and deploy documentation to GitHub Pages on push to main. Configure custom domain if available (e.g., `docs.terrene.dev/care`).

## Where

- `.github/workflows/docs.yml` — new workflow for docs deployment
- `mkdocs.yml` — add site_url and custom domain config

## Evidence

- Docs deploy automatically on push to main
- Site accessible at GitHub Pages URL
- Navigation and search work correctly

## Dependencies

- 5019 (docs site must build first)
