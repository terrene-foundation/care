# 5006: Add ShadowEnforcer report API endpoint

**Milestone**: M13 — ShadowEnforcer Backend
**Priority**: High
**Effort**: Medium

## What

Add `GET /api/v1/shadow/{agent_id}/report` endpoint that returns `ShadowReport` from `ShadowEnforcer.generate_report()`. Includes upgrade eligibility, dimension breakdown, and pass rate data.

## Where

- `src/pact/api/endpoints.py` — add `shadow_report()` method to PlatformAPI
- `src/pact/api/server.py` — register the endpoint route

## Evidence

- `GET /api/v1/shadow/dm-content-creator/report` returns valid ShadowReport JSON
- Report includes upgrade eligibility determination
- Unit test for the endpoint

## Dependencies

- 5005 (metrics endpoint first, report builds on it)
