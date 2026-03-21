# TODO-3001: Envelope intersection per-dimension

Status: pending
Priority: critical
Dependencies: []
Milestone: M3

## What

Implement `ConstraintEnvelope.intersect(other)` per thesis Section 5.3. The intersection of two envelopes is the most restrictive combination of their constraints across all five dimensions. This is the mathematical foundation of monotonic tightening: when an agent operates across a boundary (via bridge or delegation), the effective constraints are the intersection of all applicable envelopes.

Intersection rules per thesis Section 5.3 table:

**Financial dimension:**

- `max_spend_usd`: `min(a, b)`
- `api_cost_budget_usd`: `min(a, b)` (None means unlimited; `min(x, None) = x`)
- `requires_approval_above_usd`: `min(a, b)` (None means no approval threshold; min is more restrictive)
- `reasoning_required`: `a OR b` (either requiring reasoning means intersection requires it)
- If either envelope has `financial=None`, intersection has `financial=None` (no spend capability)

**Operational dimension:**

- `allowed_actions`: set intersection. If either is empty (means "all allowed"), use the other's set. If both are non-empty, intersect. If both empty, result is empty (all allowed).
- `blocked_actions`: set union (deny-overrides — if either blocks it, intersection blocks it).
- `max_actions_per_day`: `min(a, b)` treating None as unlimited (so min(100, None) = 100).
- `reasoning_required`: `a OR b`

**Temporal dimension:**

- `active_hours_start`/`active_hours_end`: compute overlap of the two windows. If windows don't overlap, result is empty (no active hours — the intersection has zero operating time, which is degenerate). Use `_intersect_time_windows()` helper.
- `blackout_periods`: set union (if either has a blackout, intersection has it).
- `timezone`: if both specify timezone, they must agree or intersection fails. If one is None/UTC, use the other.
- `reasoning_required`: `a OR b`

**Data Access dimension:**

- `read_paths`: set intersection using prefix semantics (only paths covered by both). Use `_intersect_paths()`.
- `write_paths`: set intersection using prefix semantics.
- `blocked_data_types`: set union (deny-overrides).
- `confidentiality_clearance`: `min(a.clearance, b.clearance)` (more restrictive of the two).
- `reasoning_required`: `a OR b`

**Communication dimension:**

- `internal_only`: `a OR b` (if either requires internal-only, intersection does).
- `external_requires_approval`: `a OR b`
- `allowed_channels`: set intersection (only channels both permit).
- `reasoning_required`: `a OR b`

**Identity for None dimensions:**

- An absent/None optional field is treated as "maximally permissive" for that field.
- `min(x, None) = x`, `union(x, {}) = x`, `intersection(x, all) = x`

**Key mathematical property:**
`intersect(A, B).is_tighter_than(A)` must return True, and `intersect(A, B).is_tighter_than(B)` must return True. The intersection is always at least as tight as either input — this is the key invariant. Tests must verify this property.

The result of `intersect()` is a new `ConstraintEnvelope` with a generated ID (`f"{a.id}+{b.id}"`), version=1, and `parent_envelope_id=None` (it is a derived envelope, not a direct child of either).

## Where

- `src/pact/governance/envelopes.py` — `intersect_envelopes(a, b)` module-level function (do not extend `ConstraintEnvelope` itself since it is Pydantic frozen; create a standalone function)
- `tests/unit/governance/test_intersection.py`

## Evidence

- Financial: `intersect(max_spend=100, max_spend=50)` → result has `max_spend=50`.
- Financial: `intersect(financial=None, financial=FinancialConfig(...))` → result has `financial=None`.
- Operational: `intersect(allowed={"read","write"}, allowed={"read","delete"})` → result has `allowed={"read"}`.
- Operational: `intersect(blocked={"exec"}, blocked={"drop"})` → result has `blocked={"exec","drop"}` (deny-overrides).
- Temporal: non-overlapping time windows (`09:00-12:00` intersect `14:00-17:00`) → result has no active hours (degenerate — triggers warning from TODO-3006).
- Temporal: overlapping windows (`09:00-17:00` intersect `12:00-20:00`) → result has `12:00-17:00`.
- Data Access: `read_paths=["a/*"]` intersect `read_paths=["a/b/*"]` → result has `read_paths=["a/b/*"]` (more specific wins in intersection).
- Communication: `internal_only=False` intersect `internal_only=True` → result has `internal_only=True`.
- Property test: for 10 randomly constructed envelope pairs, `result.is_tighter_than(a)` and `result.is_tighter_than(b)` both hold.

## Details

```python
from __future__ import annotations
from pact.trust.constraint.envelope import ConstraintEnvelope
from pact.build.config.schema import (
    ConstraintEnvelopeConfig, FinancialConstraintConfig,
    OperationalConstraintConfig, TemporalConstraintConfig,
    DataAccessConstraintConfig, CommunicationConstraintConfig,
    ConfidentialityLevel, CONFIDENTIALITY_ORDER,
)


def intersect_envelopes(a: ConstraintEnvelope, b: ConstraintEnvelope) -> ConstraintEnvelope:
    """Compute the intersection of two constraint envelopes.

    The intersection is the most restrictive combination of their constraints.
    The resulting envelope is always at least as tight as either input.

    This is the mathematical foundation for effective envelope computation
    in TODO-3004 (walk the hierarchy, intersect all applicable envelopes).
    """
    # Financial
    financial = _intersect_financial(a.config.financial, b.config.financial)
    # Operational
    operational = _intersect_operational(a.config.operational, b.config.operational)
    # Temporal
    temporal = _intersect_temporal(a.config.temporal, b.config.temporal)
    # Data access
    data_access = _intersect_data_access(a.config.data_access, b.config.data_access)
    # Communication
    communication = _intersect_communication(a.config.communication, b.config.communication)
    # Confidentiality clearance: min of the two
    a_lvl = CONFIDENTIALITY_ORDER[a.config.confidentiality_clearance]
    b_lvl = CONFIDENTIALITY_ORDER[b.config.confidentiality_clearance]
    clearance = (
        a.config.confidentiality_clearance if a_lvl <= b_lvl
        else b.config.confidentiality_clearance
    )

    config = ConstraintEnvelopeConfig(
        id=f"{a.id}+{b.id}",
        description=f"Intersection of {a.id} and {b.id}",
        confidentiality_clearance=clearance,
        financial=financial,
        operational=operational,
        temporal=temporal,
        data_access=data_access,
        communication=communication,
    )
    return ConstraintEnvelope(config=config)
```

Implement the `_intersect_*` helpers for each dimension as private functions in `envelopes.py`. The time window overlap logic needs care for overnight windows (reuse or adapt `_is_time_window_tighter` from `envelope.py`).

Approximate size: ~250 LOC implementation + ~300 LOC tests.
