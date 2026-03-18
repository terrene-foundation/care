# 5058: DM-specific seed data

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: Medium
**Effort**: Small

## What

Update `seed_demo.py` to include DM team agents provisioned from the canonical `dm_team.py` config. Include sample completed tasks, pending tasks, and held actions to make the DM dashboard page populated from first run.

## Where

- `scripts/seed_demo.py` — add DM team seed section using `get_dm_team_config()`

## Evidence

- DM dashboard page shows populated data on fresh seed
- Agent IDs match `dm_team.py` exactly
- Mix of completed, pending, and held tasks visible

## Dependencies

- 5004 (seed alignment), 5049 (DMTeamRunner)
