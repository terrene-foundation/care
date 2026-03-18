# 5053: ShadowEnforcer simulation runner

**Milestone**: M24 — ShadowEnforcer Calibration
**Priority**: High
**Effort**: Medium

## What

Create a script/tool that feeds historical or synthetic DM actions through the ShadowEnforcer to generate baseline metrics before live execution. This calibrates thresholds and establishes what "normal" looks like for each agent.

## Where

- `scripts/shadow_calibrate.py` — calibration runner script
- `src/care_platform/trust/shadow_enforcer.py` — ensure evaluate() works with synthetic actions

## Evidence

- Script runs 100+ synthetic actions per agent through ShadowEnforcer
- Produces baseline metrics report per agent
- Pass rate, flag rate, and dimension breakdown are reasonable (not all-pass or all-fail)

## Dependencies

- 5049 (DMTeamRunner provides the action context)
