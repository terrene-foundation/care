# 5002: Wire envelope_registry into PlatformAPI

**Milestone**: M12 — API Data Wiring Fixes
**Priority**: Critical
**Effort**: Small

## What

Pass `envelope_registry` from `seed_demo.py` output to `PlatformAPI` in `run_seeded_server.py`. Enables the `GET /api/v1/envelopes/{envelope_id}` endpoint to return real constraint envelope data.

## Where

- `scripts/run_seeded_server.py` — pass `components["envelope_registry"]` to PlatformAPI
- `src/care_platform/api/endpoints.py` — verify envelope endpoints use the registry

## Evidence

- `GET /api/v1/envelopes` returns populated envelope data
- Dashboard envelope pages show real constraint dimensions
- Existing tests still pass

## Dependencies

- None (can parallel with 5001)
