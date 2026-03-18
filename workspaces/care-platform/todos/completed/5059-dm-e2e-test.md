# 5059: End-to-end DM execution test

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: High
**Effort**: Medium

## What

Integration test that exercises the full DM pipeline: submit task → route to agent → verify through gradient → execute via StubBackend → check audit trail → verify approval queue (for HELD actions). Proves governance works end-to-end without real LLM costs.

## Where

- `tests/integration/test_dm_e2e.py` — new integration test

## Evidence

- Test submits a "draft post" task → routes to content creator → AUTO_APPROVED → executes → audit created
- Test submits a "publish post" task → routes to content creator → HELD → approval queue → audit created
- Test submits a "delete all posts" task → BLOCKED → rejected → audit created
- All 3 verification gradient levels exercised

## Dependencies

- 5049-5052 (full DM execution pipeline)
