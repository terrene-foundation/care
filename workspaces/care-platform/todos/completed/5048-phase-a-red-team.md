# 5048: Phase A + B red team validation

**Milestone**: M22 — Integration and Dog-fooding
**Priority**: High
**Effort**: Medium

## What

Red team the completed Phase A (Polish & Deploy) and Phase B (Org Builder) work. Verify:

- All mock data removed from frontend
- All API endpoints return real data
- CI pipeline passes with correct paths
- Docker Compose runs end-to-end
- Org builder validation catches all known invalid configurations
- Documentation site is accessible and accurate
- No security regressions from new endpoints

## Where

- `workspaces/care-platform/04-validate/` — red team report

## Evidence

- Red team report with 0 CRITICAL/HIGH findings
- All MEDIUM findings documented with mitigation plan
- Test suite passes (3,070+ tests)

## Dependencies

- 5001-5047 (all Phase A + B tasks complete)
