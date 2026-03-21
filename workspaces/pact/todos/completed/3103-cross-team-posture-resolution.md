# Todo 3103: Cross-Team Posture Resolution

**Milestone**: M31 — Bridge Trust Foundation
**Priority**: High
**Effort**: Small
**Source**: Phase 4 plan
**Dependencies**: None

## What

Implement two functions in a new `src/pact/trust/bridge_posture.py` module that resolve trust posture and verification level when an agent from one team acts through a bridge into another team's workspace.

### Function 1: `effective_posture`

```python
def effective_posture(
    posture_a: TrustPostureLevel,
    posture_b: TrustPostureLevel,
) -> TrustPostureLevel:
```

Returns the more restrictive (minimum) of the two postures. Uses the existing `POSTURE_ORDER` mapping from `src/pact/trust/posture.py` for numeric comparison. The posture with the lower `POSTURE_ORDER` value is returned.

Example: `effective_posture(SUPERVISED, CONTINUOUS_INSIGHT)` returns `SUPERVISED`.

### Function 2: `bridge_verification_level`

```python
def bridge_verification_level(
    effective_posture: TrustPostureLevel,
    base_level: VerificationLevel,
) -> VerificationLevel:
```

Applies the effective posture to determine the verification gradient level for a cross-bridge action. The logic escalates verification when the effective posture is more restrictive:

- `PSEUDO_AGENT` effective posture: all actions are BLOCKED
- `SUPERVISED` effective posture: escalate base_level by two steps (e.g., AUTO_APPROVED becomes HELD, FLAGGED becomes HELD, HELD stays HELD)
- `SHARED_PLANNING` effective posture: escalate base_level by one step (AUTO_APPROVED becomes FLAGGED, FLAGGED becomes HELD, HELD stays HELD)
- `CONTINUOUS_INSIGHT` effective posture: no escalation (base_level returned as-is)
- `DELEGATED` effective posture: no escalation (base_level returned as-is)

Uses the `VerificationLevel` enum from `pact/config/schema.py`. The `VerificationLevel` ordering is: `AUTO_APPROVED < FLAGGED < HELD < BLOCKED`.

Import `POSTURE_ORDER` from `pact.trust.posture` and `VerificationLevel` from `pact.config.schema`.

## Where

- `src/pact/trust/bridge_posture.py` (new file)

## Evidence

- [ ] `src/pact/trust/bridge_posture.py` exists with both functions
- [ ] `effective_posture()` returns the minimum posture for all 25 combinations of 5x5 posture levels
- [ ] `effective_posture()` is symmetric: `f(a, b) == f(b, a)` for all inputs
- [ ] `effective_posture()` is idempotent: `f(a, a) == a` for all inputs
- [ ] `bridge_verification_level()` escalates correctly for SUPERVISED (2 steps up)
- [ ] `bridge_verification_level()` escalates correctly for SHARED_PLANNING (1 step up)
- [ ] `bridge_verification_level()` returns BLOCKED for PSEUDO_AGENT effective posture
- [ ] `bridge_verification_level()` returns base_level unchanged for CONTINUOUS_INSIGHT and DELEGATED
- [ ] Escalation never exceeds BLOCKED (capped at maximum)
- [ ] All unit tests pass
