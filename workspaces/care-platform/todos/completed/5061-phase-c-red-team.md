# 5061: Phase C red team validation

**Milestone**: M25 — DM Dashboard and E2E
**Priority**: High
**Effort**: Medium

## What

Red team the completed Phase C (DM Team Vertical). Focus areas:

- Can DM agents be tricked into producing harmful content via prompt injection?
- Does the verification gradient correctly classify all DM action types?
- Is the approval queue responsive under realistic DM workload?
- Does cascade revocation work when a DM agent is compromised?
- Are DM agent outputs properly sanitized before storage/display?
- LLM cost controls — can an agent run away with spending?

## Where

- `workspaces/care-platform/04-validate/` — red team report

## Evidence

- Red team report with 0 CRITICAL findings
- Prompt injection attempts caught by constraint envelope
- Cost runaway scenario mitigated by budget controls
- All findings documented with mitigation plan

## Dependencies

- 5049-5060 (all Phase C tasks)
