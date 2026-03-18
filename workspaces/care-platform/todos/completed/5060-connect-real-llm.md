# 5060: Connect real LLM backends for DM agents

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: Medium
**Effort**: Medium

## What

After dry-run validation succeeds, connect the Content Creator agent (first agent) to a real LLM backend (Anthropic or OpenAI). Start with one agent to validate cost and quality before scaling to all 5. Configure cost budgets per agent.

## Where

- `src/care_platform/verticals/dm_runner.py` — switch from StubBackend to real backend for content creator
- `src/care_platform/execution/backends/` — verify Anthropic/OpenAI backends work with DM prompts
- `.env` — add LLM API keys

## Evidence

- Content creator produces real content from LLM
- Cost tracked per action in CostTracker
- Budget limits enforced (action rejected if budget exceeded)
- One agent's real output displayed in dashboard

## Dependencies

- 5059 (dry-run E2E passes first), 5050 (system prompts)
