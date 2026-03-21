# 5008: Add ShadowEnforcer seed data

**Milestone**: M13 — ShadowEnforcer Backend
**Priority**: Medium
**Effort**: Medium

## What

Extend `seed_demo.py` to create a `ShadowEnforcer`, run simulated actions through it for each seeded DM agent, producing realistic shadow metrics and reports. This gives the dashboard real data to display.

## Where

- `scripts/seed_demo.py` — add shadow enforcer seeding section
- `src/pact/trust/shadow_enforcer.py` — verify `evaluate()` works with synthetic actions

## Evidence

- Shadow endpoints return data for all seeded agents
- Metrics show realistic pass/fail/flag distributions
- ShadowEnforcer dashboard page populates with real agent data

## Dependencies

- 5004 (aligned seed data), 5007 (shadow wired to API)
