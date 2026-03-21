# 5047: Organization builder dashboard page

**Milestone**: M22 — Integration and Dog-fooding
**Priority**: Medium
**Effort**: Large

## What

Frontend page showing org structure: teams as cards, agents within teams, constraint envelopes as expandable details, workspaces as linked nodes. Visual hierarchy that makes the org definition legible. Read-only initially — editing comes later.

## Where

- `apps/web/app/org/page.tsx` — new org builder page
- `apps/web/components/org/` — org-specific components (TeamCard, AgentList, EnvelopeDetail)
- `src/pact/api/endpoints.py` — add `GET /api/v1/org` endpoint

## Evidence

- Page shows all teams, agents, envelopes in a readable hierarchy
- Constraint envelopes show all 5 dimensions
- Agent cards show posture, capabilities, and team membership
- Responsive layout works on desktop and tablet

## Dependencies

- 5044 (org deploy — need org data in the system), 5004 (seed data aligned)
