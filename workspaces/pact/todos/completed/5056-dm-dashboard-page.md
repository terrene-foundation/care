# 5056: DM Team dashboard page

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: Medium
**Effort**: Medium

## What

Frontend page showing the 5 DM agents, their current postures, pending tasks, recent actions, and team health. Includes links to individual agent detail pages and the ShadowEnforcer dashboard.

## Where

- `apps/web/app/dm/page.tsx` — new DM team page
- `apps/web/components/dm/` — DM-specific components

## Evidence

- Page shows all 5 DM agents with current posture badges
- Pending task count per agent
- Recent actions list with verification gradient levels
- Team-level metrics (total actions, approval rate, cost)

## Dependencies

- 5052 (DM API endpoints)
