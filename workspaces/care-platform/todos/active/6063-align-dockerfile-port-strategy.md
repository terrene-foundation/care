# Task 6063: Align Dockerfile Port Strategy

**Milestone**: M43
**Priority**: Medium
**Effort**: Small
**Status**: Active

## Description

There is a mismatch between the port the production Dockerfile exposes (8080, required by Cloud Run) and the port used in Docker Compose for local development (8000). This creates confusion for contributors and deployment engineers. The resolution is not to change either port, but to document the strategy clearly and ensure the configuration is explicit.

Cloud Run: must listen on 8080 (or use the PORT env var)
Docker Compose: conventionally uses 8000 for local dev

The correct approach: the application reads `PORT` from the environment (defaulting to 8000 for local), and both Dockerfile and docker-compose.yml are explicit about what they set.

## Acceptance Criteria

- [ ] Application reads port from `PORT` environment variable with default 8000
- [ ] Root `Dockerfile` sets `ENV PORT=8080` (for Cloud Run compatibility)
- [ ] `docker-compose.yml` sets `PORT=8000` in the backend service environment (or omits it to use the default)
- [ ] `docker-compose.yml` maps host port 8000 to container port `${PORT:-8000}` correctly
- [ ] `deploy/deployment-config.md` (or equivalent) documents the port strategy: "Cloud Run requires 8080 — set via ENV PORT in Dockerfile. Local dev uses 8000 via docker-compose.yml override."
- [ ] Existing local dev workflow (`docker compose up`) still works after the change

## Dependencies

- Task 6001 (Dockerfile already being touched for CARE_DEV_MODE removal)
