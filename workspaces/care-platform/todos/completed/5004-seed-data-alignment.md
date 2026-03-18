# 5004: Align seed data with DM team config

**Milestone**: M12 — API Data Wiring Fixes
**Priority**: Medium
**Effort**: Medium

## What

Ensure `seed_demo.py` agent IDs, team IDs, and envelope IDs align with the canonical DM team config in `src/care_platform/verticals/dm_team.py`. Currently seed data may use IDs that don't match the DM team definition.

## Where

- `scripts/seed_demo.py` — align IDs with `dm_team.py`
- `src/care_platform/verticals/dm_team.py` — reference for canonical IDs

## Evidence

- Seed agent IDs match DM team config exactly
- Dashboard shows consistent agent names across all pages
- `validate_dm_team()` passes on seeded data

## Dependencies

- 5001, 5002, 5003 (wiring must be in place)
