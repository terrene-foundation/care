# TODO-3005: Default envelopes by trust posture

Status: pending
Priority: medium
Dependencies: [3002]
Milestone: M3

## What

Implement `default_envelope_for_posture()` per PACT-REQ-014. When an agent has no explicit RoleEnvelope in the registry, the system must not fail open. Instead, it uses a conservative default envelope derived from the agent's current trust posture. Each posture level has a set of safe defaults that allow meaningful operation while maintaining governance integrity.

Default envelopes per thesis Section 5.5:

**PSEUDO_AGENT** — observe only, no side effects:

- Financial: `None` (no spending capability)
- Operational: `allowed_actions=["read", "list", "observe"]`, `blocked_actions=["write", "delete", "execute", "send", "approve"]`, `max_actions_per_day=50`
- Temporal: active hours `09:00-17:00` UTC, no blackouts
- Data Access: `read_paths=[]` (empty means nothing accessible — must have explicit grants), `write_paths=[]`, `blocked_data_types=["pii", "financial_records", "credentials"]`
- Communication: `internal_only=True`, `external_requires_approval=True`
- Clearance: `PUBLIC`

**SUPERVISED** — agent acts, human reviews:

- Financial: `max_spend_usd=10.0`, `requires_approval_above_usd=1.0`
- Operational: `allowed_actions=[]` (all not blocked), `blocked_actions=["delete", "approve", "admin"]`, `max_actions_per_day=200`
- Temporal: active hours `09:00-18:00` UTC
- Data Access: `read_paths=["workspace/*"]`, `write_paths=["workspace/drafts/*"]`, `blocked_data_types=["credentials"]`
- Communication: `internal_only=True`, `external_requires_approval=True`
- Clearance: `RESTRICTED`

**SHARED_PLANNING** — collaborative autonomy:

- Financial: `max_spend_usd=100.0`, `requires_approval_above_usd=25.0`
- Operational: `blocked_actions=["admin"]`, `max_actions_per_day=500`
- Temporal: active hours `08:00-20:00` UTC
- Data Access: `read_paths=["workspace/*", "shared/*"]`, `write_paths=["workspace/*"]`, `blocked_data_types=["credentials"]`
- Communication: `internal_only=True`, `external_requires_approval=True`
- Clearance: `CONFIDENTIAL`

**CONTINUOUS_INSIGHT** — monitored autonomy:

- Financial: `max_spend_usd=500.0`, `requires_approval_above_usd=100.0`
- Operational: `blocked_actions=["admin"]`, `max_actions_per_day=2000`
- Temporal: no active hour restriction
- Data Access: `read_paths=["*"]`, `write_paths=["workspace/*", "outputs/*"]`, `blocked_data_types=["credentials"]`
- Communication: `internal_only=False`, `external_requires_approval=True`
- Clearance: `CONFIDENTIAL`

**DELEGATED** — full role capability within envelope:

- Financial: `max_spend_usd=5000.0` (ceiling — actual envelope should narrow this)
- Operational: no restrictions beyond role-specific blocks, `max_actions_per_day=10000`
- Temporal: no restriction
- Data Access: `read_paths=["*"]`, `write_paths=["*"]`
- Communication: `internal_only=False`, `external_requires_approval=False`
- Clearance: `CONFIDENTIAL` (SECRET+ always requires explicit RoleEnvelope — no default)

These are the **fallback** defaults. When a supervisor creates an explicit RoleEnvelope, the explicit envelope governs and these defaults are irrelevant. The defaults exist to prevent fail-open behavior in the absence of explicit governance.

## Where

- `src/pact/governance/envelopes.py` — `default_envelope_for_posture()`, `DEFAULT_ENVELOPES: dict[TrustPostureLevel, ConstraintEnvelopeConfig]`
- `tests/unit/governance/test_default_envelopes.py`

## Evidence

- Each posture level produces a `ConstraintEnvelope` with the correct defaults.
- `default_envelope_for_posture(TrustPostureLevel.PSEUDO_AGENT)` returns an envelope with `financial=None`.
- `default_envelope_for_posture(TrustPostureLevel.PSEUDO_AGENT)` envelope blocks write actions.
- Progression is monotonically wider: `delegated_default.is_tighter_than(pseudo_default)` is False (DELEGATED is wider than PSEUDO_AGENT — they move in opposite directions).
- `DELEGATED` default has `max_spend_usd=5000`, `PSEUDO_AGENT` has `financial=None`.
- `DELEGATED` default does NOT grant SECRET or TOP_SECRET clearance (explicit RoleEnvelope required for those).

## Details

```python
from pact.trust.constraint.envelope import ConstraintEnvelope
from pact.build.config.schema import (
    ConstraintEnvelopeConfig, FinancialConstraintConfig,
    OperationalConstraintConfig, TemporalConstraintConfig,
    DataAccessConstraintConfig, CommunicationConstraintConfig,
    ConfidentialityLevel, TrustPostureLevel,
)

def default_envelope_for_posture(
    role_address: str,
    posture: TrustPostureLevel,
) -> ConstraintEnvelope:
    """Return the conservative default envelope for an agent at the given posture.

    This is used by compute_effective_envelope() when no explicit RoleEnvelope
    exists in the registry. It is fail-closed: PSEUDO_AGENT cannot write or spend.

    Args:
        role_address: Used to generate a unique envelope ID.
        posture: The agent's current trust posture.
    """
    config = _DEFAULT_CONFIGS[posture]
    # Create with role-specific ID to avoid ID collisions in audit records
    personalized = config.model_copy(update={"id": f"default:{posture.value}:{role_address}"})
    return ConstraintEnvelope(config=personalized)

# Pre-built default configs (immutable)
_DEFAULT_CONFIGS: dict[TrustPostureLevel, ConstraintEnvelopeConfig] = {
    TrustPostureLevel.PSEUDO_AGENT: ConstraintEnvelopeConfig(
        id="default:pseudo_agent",
        description="Conservative default for PSEUDO_AGENT posture",
        confidentiality_clearance=ConfidentialityLevel.PUBLIC,
        financial=None,
        operational=OperationalConstraintConfig(
            allowed_actions=["read", "list", "observe"],
            blocked_actions=["write", "delete", "execute", "send", "approve"],
            max_actions_per_day=50,
        ),
        ...
    ),
    # SUPERVISED, SHARED_PLANNING, CONTINUOUS_INSIGHT, DELEGATED configs
}
```
