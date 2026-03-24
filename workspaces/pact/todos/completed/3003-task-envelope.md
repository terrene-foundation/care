# TODO-3003: TaskEnvelope (ephemeral)

Status: pending
Priority: high
Dependencies: [3002]
Milestone: M3

## What

Implement `TaskEnvelope` per PACT-REQ-010. A TaskEnvelope is an ephemeral narrowing of a RoleEnvelope for a specific task or session. It must always be at least as tight as the parent RoleEnvelope (monotonic tightening applies). It expires automatically when the task ends or its `expires_at` datetime passes.

Key properties per thesis Section 5.2:

- `task_id`: unique identifier for the task or session this envelope covers.
- `role_address`: the role this task belongs to (must have a RoleEnvelope).
- `parent_role_envelope_id`: ID of the RoleEnvelope this narrows. Links the ephemeral envelope to its standing parent.
- `envelope`: the `ConstraintEnvelope` for this specific task (must be tighter than or equal to the parent RoleEnvelope's envelope).
- `expires_at`: required. TaskEnvelopes always expire. There is no standing task envelope.
- `is_expired` property: `datetime.now(UTC) > self.expires_at`.

Fallback behaviour on expiry:

When a TaskEnvelope is expired and the agent attempts an action, the system falls back to the parent `RoleEnvelope`. This is the key difference from `ConstraintEnvelope` expiry (which causes denial). A task expiring does not block the agent — it simply reverts to their standing role constraints. The fallback must be implemented in `compute_effective_envelope()` (TODO-3004), not in TaskEnvelope itself.

Validation:

`TaskEnvelope.__post_init__()` validates that:

1. `expires_at` is in the future at construction time (raise `ValueError` if already expired — cannot create an expired task envelope).
2. The task envelope's constraints are tighter than or equal to the parent RoleEnvelope (uses `is_tighter_than()`).

```python
@dataclass
class TaskEnvelope:
    task_id: str
    role_address: str
    parent_role_envelope_id: str
    envelope: ConstraintEnvelope
    expires_at: datetime

    def __post_init__(self) -> None:
        if self.expires_at <= datetime.now(UTC):
            raise ValueError(f"TaskEnvelope expires_at must be in the future, got {self.expires_at}")

    @property
    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.expires_at

    def validate_tightening(self, parent_role_envelope: ConstraintEnvelope) -> None:
        """Validate this task envelope is tighter than or equal to the parent role envelope."""
        if not self.envelope.is_tighter_than(parent_role_envelope):
            raise EnvelopeTighteningError(
                f"TaskEnvelope {self.task_id!r} is wider than parent role envelope "
                f"for role {self.role_address!r}"
            )
```

The `task_id` is not a positional address — it is a free-form unique string (UUID or human-readable task name). Validate it matches `^[a-zA-Z0-9_-]+$` to prevent path traversal in audit records.

## Where

- `src/pact/governance/envelopes.py` — `TaskEnvelope` (added to same module as `RoleEnvelope`)
- `tests/unit/governance/test_task_envelope.py`

## Evidence

- `TaskEnvelope` with `expires_at=datetime.now(UTC) - timedelta(seconds=1)` raises `ValueError` (already expired).
- `TaskEnvelope` narrower than parent RoleEnvelope constructs successfully.
- `TaskEnvelope` wider than parent RoleEnvelope (e.g., higher spend limit) raises `EnvelopeTighteningError`.
- `is_expired` returns False immediately after construction (expires in the future).
- `is_expired` returns True after mocking time past `expires_at`.
- Fallback behavior test: `compute_effective_envelope()` (TODO-3004) uses RoleEnvelope when TaskEnvelope is expired.

## Details

TaskEnvelopes are created at session start or task assignment time. They are typically short-lived (hours, not days). The `expires_at` should default to `datetime.now(UTC) + timedelta(hours=8)` if not specified — a working day session.

Note: the existing `ConstraintEnvelope.expires_at` field (from the CARE Platform) has different semantics — it is a constraint on the envelope configuration itself. `TaskEnvelope.expires_at` is the task session deadline. They coexist without conflict: a `ConstraintEnvelope` used inside a `TaskEnvelope` may also have its own expiry (e.g., a time-limited clearance), and both expiries apply independently.
