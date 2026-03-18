# 5049: DMTeamRunner orchestrator class

**Milestone**: M23 — DM Team Execution Wiring
**Priority**: Critical
**Effort**: Large

## What

Create a `DMTeamRunner` that wires DM team agents, envelopes, verification gradient, LLM backends, approval queue, and trust store into a KaizenBridge. Configured from `get_dm_team_config()`. This is the piece that connects the existing governance layer to actual agent execution.

Start with dry-run mode (structured output without real LLM calls) to prove governance works before incurring LLM costs.

## Where

- `src/care_platform/verticals/dm_runner.py` — new DMTeamRunner class
- `src/care_platform/execution/kaizen_bridge.py` — extend for DM-specific wiring
- `tests/unit/verticals/test_dm_runner.py` — tests with StubBackend

## Evidence

- DMTeamRunner initializes all 5 agents with correct envelopes
- Task submission flows through verification gradient
- HELD actions go to approval queue
- Audit trail created for every action
- Dry-run mode produces structured outputs without LLM calls

## Dependencies

- Phase A + B complete (platform deployed, org builder working)
