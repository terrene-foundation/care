# TODO-3006: Degenerate envelope detection

Status: pending
Priority: medium
Dependencies: [3004]
Milestone: M3

## What

Implement degenerate envelope detection per thesis Section 12.3. A degenerate envelope occurs when the effective envelope's constraints have been tightened so aggressively (through a deep hierarchy or many intersections) that the agent cannot perform any meaningful work. The system should warn about this condition before it causes confusing denials in production.

A degenerate envelope is one where the effective operating space on any dimension drops below 20% of the functional minimum for that posture level. This is a warning, not an error — the envelope is still valid and will be enforced. The warning allows operators to diagnose over-constrained configurations.

Detection rules per thesis Section 12.3:

**Financial dimension degenerate condition:**

- `max_spend_usd < functional_minimum * 0.20`
- `functional_minimum` for financial: $1.00 per action (the minimum cost of a real LLM call)
- Trigger: `max_spend_usd < 0.20` (agent cannot afford a single API call)
- Exception: `financial=None` is not degenerate — it means no financial capability, which is intentional

**Operational dimension degenerate condition:**

- `max_actions_per_day` is set and `max_actions_per_day < 5`
- An agent with fewer than 5 actions per day cannot carry out meaningful work
- Also degenerate: `allowed_actions` is non-empty and has 0 members after intersection (empty allowed_actions list means "all blocked")

**Temporal dimension degenerate condition:**

- Active hours window spans less than 1 hour (start and end are within 60 minutes of each other, or the intersection of windows produced zero overlap)
- A window of less than 1 hour leaves no meaningful operating time

**Data Access dimension degenerate condition:**

- `read_paths` is non-empty but every path in `read_paths` is narrower than any real resource path (e.g., paths like `"nonexistent/path/that/does/not/match/anything"` — this is hard to detect generically; instead, check if `read_paths` contains paths that are subsets of the parent's `read_paths` but no parent's paths exist to match against)
- More practical check: if `read_paths` is non-empty after intersection and `write_paths` is non-empty after intersection, but both have zero overlap with each other and with "workspace/\*", flag as possibly degenerate

**Communication dimension degenerate condition:**

- `internal_only=True` AND `allowed_channels` is non-empty AND `allowed_channels` is empty after intersection — agent has no channels to communicate through

The `check_degenerate_envelope()` function returns a `DegenerateWarning` list. An empty list means no degenerate conditions found. `compute_effective_envelope()` (TODO-3004) calls this and logs a WARNING for each condition found.

```python
@dataclass
class DegenerateWarning:
    dimension: str
    condition: str
    severity: str = "warning"   # "warning" or "critical"
    threshold_used: float | None = None
    actual_value: float | None = None

def check_degenerate_envelope(
    envelope: ConstraintEnvelope,
    posture: TrustPostureLevel,
) -> list[DegenerateWarning]:
    """Check for degenerate conditions in an effective envelope.

    Returns a list of DegenerateWarning instances.
    Empty list means no issues found.
    """
    warnings = []
    # financial check
    # operational check
    # temporal check
    # communication check
    return warnings
```

## Where

- `src/pact/governance/envelopes.py` — `check_degenerate_envelope()`, `DegenerateWarning` (added to same module, called from `compute_effective_envelope()`)
- Tests: included in `tests/unit/governance/test_effective_envelope.py` (not a separate file — test the detection via the effective envelope computation path)

## Evidence

- A 10-level hierarchy where each level halves `max_spend_usd` (starting at $100, ending at ~$0.10 after 10 halvings) triggers a financial degenerate warning when `max_spend_usd < 0.20`.
- A normal 3-level hierarchy with reasonable constraints does not trigger any warning.
- Temporal degenerate: envelope with `active_hours_start="09:00"`, `active_hours_end="09:30"` (30-minute window) triggers temporal warning.
- Operational degenerate: envelope with `max_actions_per_day=2` triggers operational warning.
- `financial=None` does NOT trigger a warning (intentional absence of financial capability).
- `DegenerateWarning.dimension` identifies which dimension triggered the warning.

## Details

Severity classification:

- `"warning"`: condition noted, agent can still operate (just barely).
- `"critical"`: agent effectively cannot operate at all on that dimension (e.g., zero actions per day, zero overlap in time windows).

The threshold values (20% of functional minimum) are defined as module-level constants for easy adjustment:

```python
# Degenerate thresholds — from thesis Section 12.3
_DEGENERATE_MIN_SPEND_USD: float = 0.20
_DEGENERATE_MIN_ACTIONS_PER_DAY: int = 5
_DEGENERATE_MIN_ACTIVE_HOURS: float = 1.0   # in hours
```

`compute_effective_envelope()` (TODO-3004) must call `check_degenerate_envelope()` and log warnings using the module logger:

```python
warnings = check_degenerate_envelope(intersected, default_posture)
for w in warnings:
    logger.warning(
        "Degenerate envelope for role %r: %s dimension — %s",
        role_address, w.dimension, w.condition
    )
```

Keep this function lightweight. It runs on every `compute_effective_envelope()` call. No external I/O, no blocking operations.
