# 5054: ShadowEnforcer live mode integration

**Milestone**: M24 — ShadowEnforcer Calibration
**Priority**: Medium
**Effort**: Small

## What

Wire `ShadowEnforcerLive` into `KaizenBridge.execute_task()` so every live execution records agreement/divergence between the real enforcer and the shadow enforcer. This enables continuous calibration.

## Where

- `src/care_platform/execution/kaizen_bridge.py` — add shadow live evaluation hook
- `src/care_platform/trust/shadow_enforcer_live.py` — verify integration points

## Evidence

- Every task execution through KaizenBridge creates a shadow evaluation
- Agreement/divergence recorded in shadow metrics
- No performance degradation from shadow evaluation (async or batched)

## Dependencies

- 5049 (DMTeamRunner), 5053 (calibration baseline established)
