# 5027: Expand health check endpoint

**Milestone**: M18 — Production Hardening
**Priority**: Medium
**Effort**: Small

## What

Expand `/health` endpoint to report component health: database connection status, trust store availability, LLM backend reachability, approval queue status. Return structured JSON with component-level health.

## Where

- `src/pact/api/server.py` — enhance `/health` endpoint
- `src/pact/persistence/health.py` — add component health checks

## Evidence

- `/health` returns `{"status": "healthy", "components": {...}}` with per-component status
- Unhealthy components reported with reason
- Docker Compose health check still works

## Dependencies

- None (independent)
