# 5001: Wire verification_stats into PlatformAPI

**Milestone**: M12 — API Data Wiring Fixes
**Priority**: Critical
**Effort**: Small

## What

Fix `scripts/run_seeded_server.py` to pass `verification_stats` from `seed_demo.py` output to the `PlatformAPI` constructor. Currently passes `verification_stats={}` (empty dict), causing the dashboard verification page to show an error banner.

## Where

- `scripts/run_seeded_server.py` — pass `components["verification_stats"]` to PlatformAPI
- `src/pact/api/server.py` — verify the `_build_platform_api()` function accepts and forwards the data

## Evidence

- `GET /api/v1/verification/stats` returns real counts (not empty or error)
- Dashboard verification page shows populated stats
- Existing tests still pass

## Dependencies

- None (first task)
