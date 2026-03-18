# 5055: Posture upgrade recommendation endpoint

**Milestone**: M24 — ShadowEnforcer Calibration
**Priority**: Medium
**Effort**: Small

## What

Add `GET /api/v1/shadow/{agent_id}/upgrade-recommendation` endpoint that returns the ShadowReport with upgrade eligibility determination. The frontend posture upgrade wizard can then use real evidence data.

## Where

- `src/care_platform/api/endpoints.py` — add upgrade recommendation endpoint
- `src/care_platform/api/server.py` — register route
- `apps/web/components/agents/PostureUpgradeWizard.tsx` — wire to real API (has TODOs)

## Evidence

- Endpoint returns upgrade eligibility with evidence data
- Posture upgrade wizard shows real shadow data instead of placeholders
- Upgrade recommendation includes all dimension scores

## Dependencies

- 5053 (calibration data must exist for meaningful recommendations)
