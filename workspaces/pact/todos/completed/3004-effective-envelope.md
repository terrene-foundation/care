# TODO-3004: Effective envelope computation

Status: pending
Priority: critical
Dependencies: [3001, 3002, 3003, 1003]
Milestone: M3

## What

Implement `compute_effective_envelope()` per PACT-REQ-011. The effective envelope is the actual operating boundary an agent faces at runtime. It is computed by walking the full D/T/R address chain from the root to the agent's role and intersecting all RoleEnvelopes along the path, then applying the active TaskEnvelope (if any and not expired).

Algorithm per thesis Section 5.4:

1. Parse the role address using TODO-1001 to extract the ancestor chain: e.g., `D1-R1-T1-R1-R1` → ancestors are `[D1-R1, D1-R1-T1-R1, D1-R1-T1-R1-R1]` (root to leaf inclusive).
2. For each ancestor address in root-to-leaf order, look up the `RoleEnvelope` in the registry.
3. If a `RoleEnvelope` exists for that ancestor, include its `ConstraintEnvelope` in the intersection chain.
4. If no `RoleEnvelope` exists for an ancestor, skip it (the parent's constraints pass through). Do not use a default envelope here — that would impose constraints the supervisor never set. The absence of a RoleEnvelope at an intermediate level means "unconstrained at that level".
5. After intersecting all ancestor RoleEnvelopes, check for an active TaskEnvelope for the leaf role:
   - If a non-expired TaskEnvelope exists, intersect it into the result.
   - If the TaskEnvelope is expired, skip it (fall back to the role envelope, not to "denied").
6. If no RoleEnvelopes exist at all in the chain (empty org, root with no envelopes), return the default envelope for the agent's trust posture from TODO-3005.

Gradient thresholds — IMPORTANT per thesis Section 5.4:

The verification gradient thresholds (FLAGGED/HELD/BLOCKED boundaries) come from the **immediate supervisor's RoleEnvelope only**, not from the intersection. Rationale: the supervisor sets the accountability thresholds for their direct report; grandparents do not override these thresholds. This means `compute_effective_envelope()` returns both an `EffectiveEnvelope` with the intersected constraints AND a `gradient_config` from the direct supervisor.

```python
@dataclass
class EffectiveEnvelope:
    role_address: str
    intersected: ConstraintEnvelope           # The effective constraint boundary
    gradient_source: str | None               # Address of immediate supervisor (gradient source)
    task_envelope_applied: bool               # Whether a TaskEnvelope was included
    ancestor_chain: list[str]                 # Addresses of all ancestors included in intersection
```

## Where

- `src/pact/governance/envelopes.py` — `compute_effective_envelope()`, `EffectiveEnvelope`
- `tests/unit/governance/test_effective_envelope.py`

## Evidence

- 4-level hierarchy (`D1-R1` → `D1-R1-T1-R1` → `D1-R1-T1-R1-R1`) with RoleEnvelopes at each level produces a correctly intersected `EffectiveEnvelope` where each dimension is the most restrictive across all levels.
- Missing RoleEnvelope at an intermediate level (e.g., T level has no envelope but D and leaf do): result reflects only D and leaf envelopes intersected (intermediate passes through).
- Active TaskEnvelope narrows the result further: `effective.task_envelope_applied == True`.
- Expired TaskEnvelope is skipped: `effective.task_envelope_applied == False`, result same as without task envelope.
- No RoleEnvelopes in chain: returns default envelope for the agent's posture (from TODO-3005).
- `effective.gradient_source` is the address of the leaf role's immediate supervisor (not the root).
- Deterministic: same inputs always produce same output.

## Details

```python
def compute_effective_envelope(
    role_address: str,
    role_envelope_registry: RoleEnvelopeRegistry,
    task_envelope: TaskEnvelope | None = None,
    default_posture: TrustPostureLevel = TrustPostureLevel.SUPERVISED,
) -> EffectiveEnvelope:
    """Compute the effective envelope for a role by intersecting the ancestor chain.

    Walks root-to-leaf through the D/T/R address hierarchy, intersecting
    all RoleEnvelopes found. Applies active TaskEnvelope if present and not expired.
    Falls back to posture default if no RoleEnvelopes exist.
    """
    # Step 1: Extract ancestor chain via TODO-1001 address utilities
    ancestors = address_ancestors(role_address)  # [root, ..., role_address]

    # Step 2: Collect RoleEnvelopes for ancestors
    chain: list[ConstraintEnvelope] = []
    for addr in ancestors:
        role_env = role_envelope_registry.get_active(addr)
        if role_env is not None:
            chain.append(role_env.envelope)

    # Step 3: Fall back to posture default if chain is empty
    if not chain:
        default = default_envelope_for_posture(role_address, default_posture)
        return EffectiveEnvelope(
            role_address=role_address,
            intersected=default,
            gradient_source=None,
            task_envelope_applied=False,
            ancestor_chain=[],
        )

    # Step 4: Intersect all envelopes in the chain
    from functools import reduce
    intersected = reduce(intersect_envelopes, chain)

    # Step 5: Apply TaskEnvelope if active
    task_applied = False
    if task_envelope is not None and not task_envelope.is_expired:
        intersected = intersect_envelopes(intersected, task_envelope.envelope)
        task_applied = True

    # Step 6: Identify gradient source (immediate supervisor)
    # The immediate supervisor is the last ancestor before role_address in the chain
    gradient_source = ancestors[-2] if len(ancestors) >= 2 else None

    return EffectiveEnvelope(
        role_address=role_address,
        intersected=intersected,
        gradient_source=gradient_source,
        task_envelope_applied=task_applied,
        ancestor_chain=[a for a in ancestors if role_envelope_registry.get_active(a) is not None],
    )
```

The `address_ancestors()` function is provided by TODO-1001 (prefix-containment queries / address utilities). It returns the full chain of ancestor addresses for a given address in root-to-leaf order.

Call `check_degenerate_envelope()` from TODO-3006 after computing the intersection, before returning. Log a warning if degenerate.
