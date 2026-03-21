# TODO-6003: Adversarial Threat Tests

Status: pending
Dependencies: [1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005, 2006, 3001, 3002, 3003, 3004, 3005, 3006, 4001, 4002]
Milestone: M6
Priority: high

## What

Test the 5 adversarial threats identified in thesis Section 12.9. Each threat represents a realistic attack vector — not theoretical — that someone operating within the PACT framework could attempt. The tests verify that PACT either detects and flags the attack, or structurally prevents it.

The 5 threats:

1. **Envelope dereliction**: A supervisor sets a "pass-through" envelope that imposes no constraints, defeating the monotonic-tightening requirement. A child's envelope that equals the root (no tightening) must be detected.

2. **Compromised agent within envelope**: An agent operating within a valid envelope attempts to access data outside its envelope. This tests that the envelope is enforced at runtime, not just at setup.

3. **Bridge collusion**: Two roles in different departments attempt to create a bridge between themselves, bypassing a barrier without ancestor approval. PACT requires that bridge creation be authorized by a common ancestor with authority over both sides.

4. **Posture gaming**: An agent attempts to advance its trust posture without accumulating the required evidence. Posture advancement must require a threshold of recorded positive outcomes, not just a unilateral claim.

5. **TOCTOU in envelope computation**: An agent attempts to change its task envelope between the time the envelope is computed and the time it is enforced. The effective envelope must be computed atomically and the result must not be re-computed during a session.

## Where

- `tests/unit/governance/test_adversarial.py`

## Evidence

- All 5 adversarial tests are implemented and pass
- Threat 1: `degenerate_envelope_check(child_envelope, parent_envelope)` returns a flag when child equals parent (no tightening occurred)
- Threat 3: `create_bridge(side_a, side_b, ...)` raises `BridgeAuthorizationError` when the requester is not an ancestor of both sides
- Threat 4: `advance_posture(role_address, target_posture)` raises `PostureAdvancementError` when evidence threshold not met
- Threat 5: envelope snapshot taken at session start; re-computation attempt during session raises `EnvelopeMutationError`
- `pytest tests/unit/governance/test_adversarial.py -v` passes

## Details

### Threat 1: Envelope dereliction

```python
def test_envelope_dereliction_detected():
    """Supervisor setting pass-through envelope is detected and flagged.

    Thesis Section 12.9.1: An administrator could set a child envelope
    equal to its parent, defeating the monotonic-tightening guarantee.
    Detection: degenerate_envelope_check() flags the violation.
    """
    from pact.governance.envelope import degenerate_envelope_check, DegenerateEnvelopeWarning

    parent = RoleEnvelope(
        max_cost_usd=1000.0,
        max_calls_per_hour=100,
        allowed_data_access=frozenset(["read"]),
        max_session_duration_minutes=60,
    )
    # Pass-through: child envelope = parent envelope (no tightening)
    child = RoleEnvelope(
        max_cost_usd=1000.0,      # Same as parent — no tightening
        max_calls_per_hour=100,   # Same as parent — no tightening
        allowed_data_access=frozenset(["read"]),
        max_session_duration_minutes=60,
    )

    warning = degenerate_envelope_check(child, parent)
    assert warning is not None, (
        "Pass-through envelope (child = parent) must be flagged as degenerate. "
        "A supervisor who sets no constraints has abdicated their accountability obligation."
    )
    assert warning.warning_type == "pass_through"
```

The `degenerate_envelope_check()` function must return a `DegenerateEnvelopeWarning` dataclass when:

- All dimensions of the child envelope equal the parent envelope (complete pass-through)
- OR any single dimension is not tightened (partial dereliction — warn but don't block)

The function does NOT raise — it returns a warning object or None. The caller decides whether to block or log. The framework flags it; policy determines the response.

### Threat 2: Agent operating outside envelope

```python
def test_agent_outside_envelope_blocked():
    """Agent within a valid envelope cannot access resources outside the envelope.

    Even if `can_access()` permits access at the KSP/clearance level,
    the effective envelope's data_access constraints must be enforced.
    """
    # Role envelope: only allows read on /engineering/public/*
    role_envelope = RoleEnvelope(
        allowed_data_access=frozenset(["read"]),
        allowed_data_prefixes=frozenset(["/engineering/public/"]),
    )
    task_envelope = TaskEnvelope(
        allowed_data_prefixes=frozenset(["/engineering/public/"]),
    )
    effective = compute_effective_envelope(role_envelope, task_envelope)

    # Attempt to access /medicine/clinical/ (outside envelope scope)
    result = enforce_envelope(
        effective_envelope=effective,
        requested_action="read",
        requested_resource="/medicine/clinical/patient-001.pdf",
    )
    assert result == EnvelopeVerdict.BLOCKED, (
        "An agent may not access resources outside their effective envelope scope, "
        "even if KSP/clearance would permit it."
    )
```

### Threat 3: Bridge collusion

```python
def test_bridge_creation_requires_ancestor_authorization():
    """Two roles cannot create a bridge between themselves without ancestor approval.

    Thesis Section 12.9.3: If two roles in different departments could
    unilaterally establish a bridge, they could bypass information barriers.
    Bridge creation requires authorization from a common ancestor with
    authority over both sides.

    Property 5 from thesis: No agent may authorize access beyond their own envelope.
    """
    from pact.governance.bridge import create_bridge, BridgeAuthorizationError

    compiled_org = _build_test_org()

    # Attempt: CS faculty role creates a bridge to Student Conduct Coordinator
    # Neither side is an ancestor of the other; neither has authority to bridge.
    with pytest.raises(BridgeAuthorizationError) as exc_info:
        create_bridge(
            requestor_address="D1-R1-D2-R1",        # Dean of Engineering
            side_a="D1-R1-D2-R1",                   # Engineering
            side_b="D1-R1-D5-R1-T1-R1",             # Student Conduct
            compiled_org=compiled_org,
            bridge_type=BridgeType.STANDING,
        )

    assert "common ancestor" in str(exc_info.value).lower() or \
           "not authorized" in str(exc_info.value).lower()
```

The `create_bridge()` function must verify that the `requestor_address` is a common ancestor (in the D/T/R tree) of both `side_a` and `side_b`, OR that the requestor has been explicitly delegated bridge authority. If neither condition holds, raise `BridgeAuthorizationError`.

### Threat 4: Posture gaming

```python
def test_posture_advancement_requires_evidence():
    """Posture cannot advance without accumulated evidence.

    An agent cannot self-promote from SUPERVISED to SHARED_PLANNING
    by claiming readiness. Advancement requires a threshold of recorded
    positive outcomes (from audit anchors) at the current posture.
    """
    from pact.governance.posture import advance_posture, PostureAdvancementError

    # Agent has zero positive outcomes recorded
    result = advance_posture(
        role_address="D1-R1-D2-R1",
        current_posture=TrustPostureLevel.SUPERVISED,
        requested_posture=TrustPostureLevel.SHARED_PLANNING,
        evidence_count=0,  # No evidence
        required_evidence_count=10,  # Threshold from org config
    )
    assert result.approved is False
    assert result.reason == "insufficient_evidence"

def test_posture_advancement_with_sufficient_evidence():
    """Posture advances when evidence threshold is met."""
    result = advance_posture(
        role_address="D1-R1-D2-R1",
        current_posture=TrustPostureLevel.SUPERVISED,
        requested_posture=TrustPostureLevel.SHARED_PLANNING,
        evidence_count=10,  # Threshold met
        required_evidence_count=10,
    )
    assert result.approved is True
```

### Threat 5: TOCTOU in envelope computation

```python
def test_envelope_snapshot_immutable_during_session():
    """Effective envelope, once computed at session start, cannot be changed during session.

    Thesis Section 12.9.5: An attacker who can modify a task envelope after
    the effective envelope is computed could expand their access mid-session.
    The effective envelope must be a snapshot (frozen at computation time).
    """
    task_env = TaskEnvelope(max_cost_usd=50.0)
    role_env = RoleEnvelope(max_cost_usd=100.0)

    # Compute effective envelope (snapshot)
    effective = compute_effective_envelope(role_env, task_env)
    assert effective.max_cost_usd == 50.0  # Task is tighter

    # Attempt to mutate the task envelope after computation
    # The effective envelope must NOT change
    task_env_modified = TaskEnvelope(max_cost_usd=99999.0)

    # effective was computed from the original task_env; modifying the source
    # must not affect the already-computed effective envelope
    assert effective.max_cost_usd == 50.0, (
        "Effective envelope must be immutable after computation. "
        "Mutating the source task envelope must not change the effective envelope."
    )
```

Implementation note: `compute_effective_envelope` must return a new object (copy), not a reference to either input. Using `@dataclass(frozen=True)` for `RoleEnvelope` and `TaskEnvelope` ensures immutability. The test verifies that the returned effective envelope is independent of its source inputs.
