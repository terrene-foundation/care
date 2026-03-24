# 5014: Add Docker build test to CI

**Milestone**: M15 — CI/CD Pipeline
**Priority**: Medium
**Effort**: Small

## What

Add a CI job that builds the Dockerfile and runs `docker compose up --wait` with a health check. Verifies the Docker infrastructure works on every push.

## Where

- `.github/workflows/ci.yml` — add `docker-build` job
- `docker-compose.yml` — verify health checks are correct

## Evidence

- CI includes a Docker build job
- `docker compose up --wait` succeeds with health checks passing
- `/health` endpoint returns 200

## Dependencies

- 5012 (CI paths fixed)
