# 5003: Wire posture_store into PlatformAPI

**Milestone**: M12 — API Data Wiring Fixes
**Priority**: High
**Effort**: Small

## What

Pass `posture_store` from `seed_demo.py` output to `PlatformAPI`. Currently posture history data is seeded but discarded at server startup.

## Where

- `scripts/run_seeded_server.py` — pass `components["posture_store"]` to PlatformAPI
- `src/care_platform/api/endpoints.py` — verify posture history endpoints use the store

## Evidence

- Agent detail pages show posture history with real data
- Posture upgrade wizard has real evidence data
- Existing tests still pass

## Dependencies

- None (can parallel with 5001, 5002)
