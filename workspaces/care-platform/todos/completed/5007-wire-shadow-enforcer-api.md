# 5007: Wire ShadowEnforcer into PlatformAPI constructor

**Milestone**: M13 — ShadowEnforcer Backend
**Priority**: High
**Effort**: Medium

## What

Add optional `ShadowEnforcer` parameter to `PlatformAPI.__init__()`. Wire it from the seeded server. The ShadowEnforcer class already exists with full metrics/report capabilities — just needs to be available to the API layer.

## Where

- `src/care_platform/api/endpoints.py` — add `shadow_enforcer` parameter to PlatformAPI
- `scripts/run_seeded_server.py` — create and pass ShadowEnforcer instance

## Evidence

- PlatformAPI accepts and stores a ShadowEnforcer instance
- Shadow endpoints use the real ShadowEnforcer (not mock)
- Existing tests still pass

## Dependencies

- 5005, 5006 (endpoints must exist to wire to)
