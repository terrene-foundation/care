# 5026: Add container registry publishing

**Milestone**: M18 — Production Hardening
**Priority**: Medium
**Effort**: Small

## What

Add GitHub Actions step to build and push Docker images to GitHub Container Registry (ghcr.io) on release tags. Tag images with version and latest.

## Where

- `.github/workflows/publish.yml` — add Docker push step (alongside PyPI publish)

## Evidence

- Release tag triggers Docker image build and push
- Image available at `ghcr.io/terrene-foundation/care-platform:latest`
- Image runs correctly with `docker pull` + `docker run`

## Dependencies

- 5014 (Docker build must work in CI), 5018 (publish workflow exists)
