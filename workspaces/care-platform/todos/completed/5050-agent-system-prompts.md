# 5050: Agent-specific system prompts

**Milestone**: M23 — DM Team Execution Wiring
**Priority**: High
**Effort**: Medium

## What

Create role-specific system prompts for each of the 5 DM agents. Currently KaizenBridge uses a generic system prompt. Each agent needs a tailored prompt reflecting its role, capabilities, constraints, and output format expectations.

## Where

- `src/care_platform/verticals/dm_prompts.py` — system prompts for each DM agent
- `src/care_platform/execution/kaizen_bridge.py` — use agent-specific prompts

## Evidence

- Each DM agent has a unique system prompt
- Prompts reference the agent's capabilities and constraints
- Prompts specify expected output format
- StubBackend tests verify prompts are passed correctly

## Dependencies

- 5049 (DMTeamRunner must exist)
