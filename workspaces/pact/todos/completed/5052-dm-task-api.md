# 5052: DM task submission and status API endpoints

**Milestone**: M23 — DM Team Execution Wiring
**Priority**: High
**Effort**: Medium

## What

Add DM-specific API endpoints:

- `POST /api/v1/dm/tasks` — submit a task description, auto-route to appropriate DM agent, return task ID
- `GET /api/v1/dm/tasks/{task_id}` — return task result, lifecycle state, audit trail
- `GET /api/v1/dm/status` — return all 5 agents' postures, pending approvals, recent actions

## Where

- `src/pact/api/endpoints.py` — add DM endpoint methods
- `src/pact/api/server.py` — register DM routes
- `tests/unit/api/test_dm_endpoints.py` — endpoint tests

## Evidence

- POST returns task_id and routed agent
- GET task returns lifecycle state (pending → executing → complete/held)
- GET status shows all 5 agents with current posture and action counts

## Dependencies

- 5049 (DMTeamRunner), 5051 (routing)
