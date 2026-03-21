# 5011: Replace Math.random() dashboard trends with real data

**Milestone**: M14 — Frontend Fixes
**Priority**: Medium
**Effort**: Medium

## What

The dashboard overview page generates fake 7-day trends using `Math.random()` (line ~459 of `apps/web/app/page.tsx`). Replace with either: (a) a time-series API endpoint that computes real trends from audit/action data, or (b) remove the trend display until real data is available. Option (a) preferred.

## Where

- `apps/web/app/page.tsx` — replace synthetic trend generation
- `src/pact/api/endpoints.py` — add `GET /api/v1/dashboard/trends` endpoint (if option a)
- `scripts/seed_demo.py` — seed time-series data with realistic timestamps

## Evidence

- Dashboard trends show consistent data across page refreshes
- No `Math.random()` calls in production dashboard code
- Trend data sourced from real audit records

## Dependencies

- 5001, 5002, 5003 (data wiring must be complete for real stats)
