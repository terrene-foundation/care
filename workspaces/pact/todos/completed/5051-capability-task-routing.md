# 5051: Capability-based task routing

**Milestone**: M23 — DM Team Execution Wiring
**Priority**: High
**Effort**: Medium

## What

Extend the execution runtime to select DM agents by matching task keywords/intents to agent capabilities. "Draft a LinkedIn post" routes to Content Creator. "Analyze engagement metrics" routes to Analytics. Falls back to Team Lead for ambiguous tasks.

## Where

- `src/pact/execution/runtime.py` — add capability-based agent selection
- `src/pact/verticals/dm_runner.py` — configure routing rules
- `tests/unit/execution/test_routing.py` — routing tests

## Evidence

- "Draft a post about AI governance" → routes to dm-content-creator
- "What was our engagement last week?" → routes to dm-analytics
- "Ambiguous task" → routes to dm-team-lead
- Routing decision recorded in audit trail

## Dependencies

- 5049 (DMTeamRunner), 5050 (system prompts)
