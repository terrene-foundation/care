# 5009: Replace ShadowEnforcer mock data with real API calls

**Milestone**: M14 — Frontend Fixes
**Priority**: High
**Effort**: Medium

## What

Replace the hardcoded `mock-data.ts` imports in the ShadowEnforcer dashboard page with `useApi()` calls to the new shadow endpoints. The mock data uses fake agent IDs (`agent-ops-lead`, `agent-finance-analyst`) that don't match the platform's actual agents.

## Where

- `apps/web/app/shadow/page.tsx` — replace `getMockShadowData()` with API calls
- `apps/web/app/shadow/elements/mock-data.ts` — delete after migration
- `apps/web/app/shadow/elements/*.tsx` — update components to accept API data

## Evidence

- ShadowEnforcer page loads data from `/api/v1/shadow/{agent_id}/metrics`
- Agent selector shows real seeded agents (DM team members)
- No references to `mock-data.ts` remain
- Page renders correctly with real data

## Dependencies

- 5005, 5006, 5007, 5008 (shadow backend must be complete)
