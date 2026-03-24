# 5005: Add ShadowEnforcer metrics API endpoint

**Milestone**: M13 — ShadowEnforcer Backend
**Priority**: High
**Effort**: Medium

## What

Add `GET /api/v1/shadow/{agent_id}/metrics` endpoint that returns `ShadowMetrics` from `ShadowEnforcer.get_metrics()`. The backend `ShadowEnforcer` class already produces this data structure — just needs HTTP exposure.

## Where

- `src/pact/api/endpoints.py` — add `shadow_metrics()` method to PlatformAPI
- `src/pact/api/server.py` — register the endpoint route

## Evidence

- `GET /api/v1/shadow/dm-content-creator/metrics` returns valid ShadowMetrics JSON
- Response matches the ShadowMetrics Pydantic model schema
- Unit test for the endpoint

## Dependencies

- 5004 (seed data alignment — need real agent IDs)
