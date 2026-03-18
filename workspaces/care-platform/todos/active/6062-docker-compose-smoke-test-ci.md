# Task 6062: Add Docker Compose Smoke Test to CI

**Milestone**: M43
**Priority**: Medium
**Effort**: Medium
**Status**: Active

## Description

Add a CI job that spins up the full Docker Compose stack (backend + frontend + database) and runs a basic smoke test to verify the stack starts and responds to health checks. This catches Docker-level integration failures (wrong env vars, port conflicts, missing dependencies) that unit tests cannot catch.

Smoke test steps:

1. `docker compose up -d` — start all services
2. Wait for health check endpoints to respond (with timeout)
3. `curl /health` on the backend returns 200
4. `curl /` on the frontend returns 200 (or 304)
5. `docker compose down` — clean up

## Acceptance Criteria

- [ ] New CI job `docker-smoke-test` in `.github/workflows/ci.yml`
- [ ] Job runs on: `push` to main, `pull_request` to main
- [ ] Job uses `docker compose` (not `docker-compose` v1)
- [ ] Health check polling with timeout (max 60 seconds, poll every 5 seconds)
- [ ] Job fails if backend health check does not respond within timeout
- [ ] Job cleans up containers even on failure (using `docker compose down` in a `always` step)
- [ ] Docker layer caching used to speed up builds (actions/cache with Docker BuildKit)
- [ ] No secrets or API keys hardcoded in CI — uses test environment variables only

## Dependencies

- Task 6001 (CARE_DEV_MODE removed from Dockerfile — image must be correct before smoke testing it)
- Task 6063 (port strategy documented/aligned before smoke test is configured)
