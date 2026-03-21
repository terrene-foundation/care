# TODO-3002: RoleEnvelope (standing)

Status: pending
Priority: high
Dependencies: [3001, 1003]
Milestone: M3

## What

Implement `RoleEnvelope` per PACT-REQ-009. A RoleEnvelope is the standing constraint boundary assigned to a specific role by its immediate supervisor. It defines the maximum operating space for that role regardless of what task the agent is performing. It is persistent — it does not expire unless explicitly revoked.

Key properties per thesis Section 5.2:

- `role_address`: D/T/R positional address of the role this envelope governs.
- `supervisor_address`: address of the role that defined and signed off on this envelope (the immediate supervisor in the D/T/R hierarchy).
- `envelope`: the `ConstraintEnvelope` defining the actual constraints.
- `version`: integer, starts at 1, increments on each modification. Versioned to allow audit of "envelope at the time of this action".
- `approved_at`: datetime when the supervisor approved this envelope.
- `superseded_by`: ID of the new envelope version when this one is replaced (for audit trail).

Monotonic tightening validation:

When a new `RoleEnvelope` is created, it must be validated against the supervisor's effective envelope. If the role_address is `D1-R1-T1-R1`, the supervisor envelope is the effective envelope for `D1-R1-T1-R1`'s supervisor role. The new RoleEnvelope must satisfy `new_envelope.is_tighter_than(supervisor_effective_envelope)`.

If the supervisor does not yet have a RoleEnvelope (because they are the root of the hierarchy), the new envelope has no tightening constraint — any envelope is valid.

The `validate_tightening()` method raises `EnvelopeTighteningError` with the dimension name when the proposed envelope is wider than the supervisor's envelope on any dimension. This gives a precise error: "proposed envelope is wider than supervisor on dimension: financial (max_spend_usd: 1000 > 500)".

```python
@dataclass
class RoleEnvelope:
    role_address: str
    supervisor_address: str
    envelope: ConstraintEnvelope
    approved_at: datetime
    version: int = 1
    superseded_by: str | None = None   # envelope ID of replacement

    def validate_tightening(self, supervisor_effective: ConstraintEnvelope | None) -> None:
        """Raises EnvelopeTighteningError if this envelope widens any dimension of supervisor's."""
        if supervisor_effective is None:
            return  # Root of hierarchy — no constraint to validate against
        if not self.envelope.is_tighter_than(supervisor_effective):
            raise EnvelopeTighteningError(
                f"RoleEnvelope for {self.role_address!r} is wider than "
                f"supervisor {self.supervisor_address!r} on at least one dimension"
            )
```

Note: `validate_tightening()` uses `is_tighter_than()` from the existing `ConstraintEnvelope` in `src/pact/trust/constraint/envelope.py`. This is not a new method — it calls the existing one.

`RoleEnvelopeRegistry`: a simple dict-like container `{role_address: list[RoleEnvelope]}` that keeps the version history and provides `get_active(role_address) -> RoleEnvelope | None` (the latest non-superseded version).

## Where

- `src/pact/governance/envelopes.py` — `RoleEnvelope`, `RoleEnvelopeRegistry`
- `tests/unit/governance/test_role_envelope.py`

## Evidence

- `RoleEnvelope` creation with valid supervisor envelope constructs successfully.
- `RoleEnvelope` with `max_spend_usd=1000` when supervisor has `max_spend_usd=500` raises `EnvelopeTighteningError` with message identifying the financial dimension.
- `validate_tightening(supervisor_effective=None)` passes (root node).
- Version increments: creating a second RoleEnvelope for the same role (replacing the first) increments version to 2.
- `RoleEnvelopeRegistry.get_active(address)` returns the latest version.
- `RoleEnvelopeRegistry.get_active(address)` returns None for unregistered addresses.

## Details

Error class: `EnvelopeTighteningError(PactGovernanceError)` with fields `role_address`, `supervisor_address`, and `dimension` (the first dimension found to be wider, for debugging).

The `envelopes.py` module will grow across TODOs 3001-3006. Structure it with:

- Module-level functions: `intersect_envelopes()` (TODO-3001), `compute_effective_envelope()` (TODO-3004), `default_envelope_for_posture()` (TODO-3005)
- Dataclasses: `RoleEnvelope`, `TaskEnvelope`
- Registry classes: `RoleEnvelopeRegistry`
- Private helpers: `_intersect_*`, `_intersect_time_windows()`, etc.
