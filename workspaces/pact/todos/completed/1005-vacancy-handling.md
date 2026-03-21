# TODO-1005: Vacancy Handling (Thesis Section 5.5)

Status: pending
Priority: high
Dependencies: [1003]
Milestone: M1

## What

Implement the three vacancy rules from PACT Core Thesis Section 5.5 in
`src/pact/governance/compilation.py`. Vacancy is a first-class governance state
in PACT: when a role is vacant, the org does not simply collapse — it enters a
defined degraded state with specific behavioral rules that prevent governance gaps
while preserving continuity of operations.

The three vacancy rules:

1. A vacant role's parent must designate an acting occupant within a configurable
   deadline (default: 7 days)
2. Until an acting role is designated, all direct reports use the more restrictive
   of their own operating envelope or the vacant role's operating envelope
3. If no acting role is designated within the deadline, all downstream agents are
   suspended (verification level escalates to BLOCKED for all their actions)

## Where

- `src/pact/governance/compilation.py` — add `VacancyState`, `VacancyPolicy`,
  extend `CompiledNode`, extend `CompiledOrg`
- `tests/unit/governance/test_vacancy.py` — focused test suite (~200 LOC)

## Evidence

- `CompiledOrg.get_vacancy_state(address)` returns `VacancyState` for a vacant role
- A vacant role with no acting designation and `deadline_exceeded=True` causes
  `CompiledOrg.is_downstream_suspended(agent_address)` to return `True` for all
  agents in the vacant role's subtree
- A vacant role with an active acting designation does NOT suspend downstream agents
- `CompiledOrg.get_conservative_envelope(agent_address)` returns the intersection of
  the agent's own envelope config and the vacant parent role's envelope config when
  no acting designation exists and the deadline has not been exceeded
- `VacancyState.designate_acting(role_id, acting_for_role_id)` produces a
  `VacancyState` with `acting_role_id` set
- `pytest tests/unit/governance/test_vacancy.py` passes

## Details

### VacancyPolicy

Configuration for vacancy behavior — how long before acting designation is required
and what happens if it is not provided.

```python
@dataclass(frozen=True)
class VacancyPolicy:
    """Policy governing behavior when a role is vacant."""

    acting_designation_deadline_days: int = 7
    # Number of days after a role becomes vacant before acting designation is required.

    suspend_on_deadline_exceeded: bool = True
    # When True, downstream agents are suspended if no acting designation exists
    # after the deadline. When False, the conservative envelope applies indefinitely
    # without suspension (softer mode for non-critical roles).
```

### VacancyState

Runtime state tracking the vacancy of a specific role.

```python
@dataclass
class VacancyState:
    """Tracks the vacancy state of a role node."""

    role_id: str
    # The role_id of the vacant role.

    became_vacant_at: datetime
    # When the role became vacant.

    acting_role_id: str | None = None
    # role_id of the role designated as acting occupant.
    # None means no acting designation has been made.

    acting_designated_at: datetime | None = None
    # When the acting designation was made.

    policy: VacancyPolicy = field(default_factory=VacancyPolicy)
    # Policy governing this vacancy.

    def deadline_exceeded(self, as_of: datetime | None = None) -> bool:
        """True if the acting designation deadline has passed."""
        ...

    def has_acting_designation(self) -> bool:
        """True if an acting role has been designated."""
        ...

    def is_suspended(self, as_of: datetime | None = None) -> bool:
        """True if downstream agents should be suspended (deadline exceeded and
        policy requires suspension)."""
        ...

    def designate_acting(self, acting_role_id: str) -> "VacancyState":
        """Return a new VacancyState with the acting designation set."""
        ...
```

### CompiledOrg extensions

Add the following methods and state to `CompiledOrg`:

```python
# Internal state (populated post-compilation or via update methods)
_vacancy_states: dict[str, VacancyState]  # role_id -> VacancyState

def mark_vacant(
    self,
    address: Address | str,
    became_vacant_at: datetime,
    policy: VacancyPolicy | None = None,
) -> None:
    """Mark a role as vacant. Records vacancy state for downstream enforcement."""

def get_vacancy_state(self, address: Address | str) -> VacancyState | None:
    """Return VacancyState for the role at address, or None if not vacant."""

def designate_acting(
    self,
    vacant_address: Address | str,
    acting_role_id: str,
    designated_at: datetime | None = None,
) -> None:
    """Designate an acting occupant for a vacant role."""

def is_downstream_suspended(
    self,
    agent_address: Address | str,
    as_of: datetime | None = None,
) -> bool:
    """True if the agent at agent_address is suspended due to an ancestor vacancy
    with exceeded deadline and suspend_on_deadline_exceeded=True."""

def get_conservative_envelope_ids(
    self,
    agent_address: Address | str,
) -> list[str]:
    """Return the list of envelope IDs that must be intersected to produce the
    conservative effective envelope for the agent at agent_address.

    When an ancestor role is vacant and no acting designation exists:
    - Returns the agent's own envelope ID + the vacant ancestor role's envelope ID
    - The caller is responsible for computing the actual intersection

    When no ancestor vacancy applies, returns only the agent's own envelope ID.
    """
```

### Rule 2 — Conservative envelope computation

When a role is vacant (no acting designation, deadline not yet exceeded), direct
reports must use the intersection of their own envelope and the vacant role's envelope.
This prevents a vacancy from accidentally expanding anyone's effective authority.

The method `get_conservative_envelope_ids` returns the list of envelope IDs to
intersect. The actual envelope intersection computation is NOT done in this method —
it returns IDs for the caller (compile_org's callers, or later the envelope
intersection code from M3) to look up and intersect.

The conservative rule applies transitively: if A reports to vacant B, and B reports
to vacant C, then A must use the intersection of A's envelope, B's envelope, and C's
envelope. The method traverses the ancestry chain to collect all vacant ancestor IDs.

### Rule 3 — Suspension

Suspension means that all actions by downstream agents are automatically escalated to
`BLOCKED` verification level, regardless of their normal envelope. The
`is_downstream_suspended` method enables enforcement code to check this before
evaluating normal constraint envelopes.

Suspension propagates through the entire subtree below the suspended vacancy. If
CFO is suspended (deadline exceeded, no acting), then everyone in Finance,
including the Head of Trading and all Traders, is also suspended.

Acting designation lifts suspension immediately (no deadline for reinstatement).

### Integration with CompiledNode

`CompiledNode` gains one property:

```python
@property
def is_vacant(self) -> bool:
    return self.role_def.is_vacant
```

This is already implied by `role_def.is_vacant` but the explicit property makes
downstream code cleaner. No new fields are added to `CompiledNode` — vacancy
runtime state lives in `CompiledOrg._vacancy_states`, not in individual nodes.

### Test structure

1. Basic vacancy: mark a role vacant, verify `get_vacancy_state` returns state
2. Deadline not yet exceeded: verify `is_downstream_suspended` returns False
3. Deadline exceeded, no acting: verify suspension of all descendants
4. Acting designation: verify suspension lifted for entire subtree
5. Conservative envelope: verify correct envelope IDs returned when ancestor vacant
6. Transitive conservative envelope: two ancestors both vacant
7. Suspension propagation: suspended CFO → suspended traders (deeper descendants)
8. Acting designation scope: acting for CFO does NOT lift suspension caused by
   a different vacancy in a different branch

### Test fixtures

All test cases use a simplified 3-level org (not the full financial services org)
to keep setup compact. The fixture can be a function in `test_vacancy.py`
or in the shared `conftest.py` if it is also useful for other test files.

Use `datetime(2026, 1, 1, tzinfo=UTC)` as the "vacancy start" time and parameterize
`as_of` to simulate time advancing past the deadline. This avoids tests depending
on the real system clock.
