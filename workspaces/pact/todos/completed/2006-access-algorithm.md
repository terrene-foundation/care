# TODO-2006: Access Enforcement Algorithm (5-step)

Status: pending
Priority: critical
Dependencies: [2001, 2002, 2003, 2004, 2005, 1003]
Milestone: M2

## What

Implement the 5-step Access Enforcement Algorithm per PACT-REQ-007. This is the central function of M2. It is the decision point that all knowledge access flows through. Every access to a `KnowledgeItem` by a role must pass through `can_access()` — there is no side-door.

The algorithm is strictly sequential. A failure at any step terminates the chain and returns `AccessDecision(allowed=False, step_failed=N, ...)`. The algorithm never continues past a failure.

**Step 1: Effective Clearance**
Compute `effective_clearance(role_clearance, current_posture)` (from TODO-2001). If the requester has no active clearance record (vetting_status != ACTIVE), deny immediately. If the role's vetting status is SUSPENDED or REVOKED, deny.

**Step 2: Classification Check**
Compare the item's `classification` against the effective clearance from Step 1. If `item.classification > effective_clearance`, deny with reason "clearance insufficient". This is the hard ceiling — no bridge or KSP can override a clearance ceiling.

**Step 3: Compartment Check**
If the item has compartments (meaning it is SECRET or TOP_SECRET with specific compartment labels), verify the requester's clearance includes all required compartments via `role_clearance.has_compartment()`. If any compartment is missing, deny.

**Step 4: Containment Check (5 sub-steps)**
Call `cascade_check()` from TODO-2005. This handles:

- 4a: Same-unit check (Rule 1)
- 4b: T-inherits-D check (Rule 3)
- 4c: KSP cross-unit check (Rule 2)
- 4d: Bridge cross-unit check (Rule 2, bridge variant)
- 4e: Deny (no path found)

If `cascade_check()` returns `allowed=False`, deny with the cascade reason.

**Step 5: Deny (unreachable in practice)**
This step exists as a fail-closed default. If any prior step produced an ambiguous result (which should not happen in a correct implementation), deny. The algorithm must never return `allowed=True` by default.

`AccessDecision` return type:

```python
@dataclass
class AccessDecision:
    allowed: bool
    reason: str
    step_failed: int | None     # 1-4, or None if allowed
    rule_applied: str           # same_unit / t_inherits_d / ksp / bridge / clearance / compartment / posture_gate / denied
    audit_details: dict         # All inputs for audit anchoring
```

The flagship scenario (thesis Section 7.1) provides the primary regression test:

- **Advisory analyst blocked from trading data**: Step 2 (clearance) or Step 4 (no KSP to trading). Expected: denied at step 4.
- **CCO reads Advisory via bridge**: Step 4d (bridge). Expected: allowed.
- **AML officer reads AML data via compartment clearance**: Step 3 (compartment match). Expected: allowed.
- **Head of Trading cannot see AML investigations**: Step 3 (compartment missing). Expected: denied at step 3.

## Where

- `src/pact/governance/access.py` — `can_access()`, `AccessDecision`
- `tests/unit/governance/test_access_algorithm.py` — each step tested independently and in combination

## Evidence

All five steps tested independently:

- Step 1: role with REVOKED vetting status → denied at step 1.
- Step 2: role with RESTRICTED clearance tries to access SECRET item → denied at step 2.
- Step 3: role with SECRET clearance but wrong compartment tries to access SECRET/[TRADING] item → denied at step 3.
- Step 4: cross-unit access with no KSP and no bridge → denied at step 4 (cascade denied).
- Step 4 (KSP): cross-unit with valid KSP → allowed.
- Step 4 (bridge): cross-unit with no KSP but valid bridge → allowed for read, denied for write.
- Step 5 fail-closed: function never returns `allowed=True` by default.

Flagship scenario tests (from TODO-2007 perspective — 2006 must support all these cases):

- Advisory analyst (D1-R1-T1-R1, RESTRICTED clearance) accessing trading blotter (D1-R1-T2-R1, CONFIDENTIAL/[TRADING]): denied at step 2 (RESTRICTED < CONFIDENTIAL).
- CCO (D1-R1-R1, SECRET clearance, SUPERVISED posture) accessing advisory report (D1-R1-T1-R1, CONFIDENTIAL): allowed via bridge (Step 4d).
- AML officer (D1-R1-T3-R1, SECRET/[AML] compartment) accessing AML investigation file (D1-R1-T3-R1, SECRET/[AML]): allowed (Step 3 passes — same unit, compartment matches).
- Head of Trading (D1-R1-T2-R1, SECRET/[TRADING]) accessing AML investigation (SECRET/[AML]): denied at step 3 (TRADING compartment does not include AML).

## Details

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pact.build.config.schema import ConfidentialityLevel, TrustPostureLevel
from pact.governance.clearance import RoleClearance, VettingStatus, effective_clearance
from pact.governance.knowledge import KnowledgeItem
from pact.governance.access import (
    KnowledgeSharePolicy, PactBridge,
    cascade_check, find_ksp, find_bridge,
)

_CLASSIFICATION_ORDER: dict[ConfidentialityLevel, int] = { ... }  # from schema

@dataclass
class AccessDecision:
    allowed: bool
    reason: str
    step_failed: int | None = None
    rule_applied: str = ""
    audit_details: dict[str, Any] = field(default_factory=dict)


def can_access(
    requester_address: str,
    requester_clearance: RoleClearance | None,
    requester_posture: TrustPostureLevel,
    item: KnowledgeItem,
    ksp_registry: list[KnowledgeSharePolicy],
    bridge_registry: list[PactBridge],
    operation: str = "read",
) -> AccessDecision:
    """5-step access enforcement algorithm.

    Fail-closed: returns denied by default. Steps are executed sequentially.
    A failure at any step terminates evaluation.

    Args:
        requester_address: Full D/T/R positional address of the requesting role.
        requester_clearance: The RoleClearance assigned to the requesting role.
            None means no clearance record — denied at step 1.
        requester_posture: Current trust posture of the requesting agent.
        item: The KnowledgeItem being accessed.
        ksp_registry: All active KnowledgeSharePolicies.
        bridge_registry: All active PactBridges.
        operation: "read" or "write" (bridges only grant read access).

    Returns:
        AccessDecision with allowed=True only if all steps pass.
    """
    audit: dict[str, Any] = {
        "requester": requester_address,
        "item_id": item.item_id,
        "classification": item.classification.value,
        "operation": operation,
        "posture": requester_posture.value,
    }

    # Step 1: Effective clearance
    if requester_clearance is None:
        return AccessDecision(
            allowed=False, reason="No clearance record",
            step_failed=1, rule_applied="no_clearance", audit_details=audit
        )
    if requester_clearance.vetting_status != VettingStatus.ACTIVE:
        return AccessDecision(
            allowed=False,
            reason=f"Clearance vetting status is {requester_clearance.vetting_status.value}",
            step_failed=1, rule_applied="vetting_inactive", audit_details=audit
        )
    eff_clearance = effective_clearance(requester_clearance, requester_posture)
    audit["effective_clearance"] = eff_clearance.value

    # Step 2: Classification check
    if _CLASSIFICATION_ORDER[item.classification] > _CLASSIFICATION_ORDER[eff_clearance]:
        return AccessDecision(
            allowed=False,
            reason=(
                f"Item classification {item.classification.value} exceeds "
                f"effective clearance {eff_clearance.value}"
            ),
            step_failed=2, rule_applied="clearance_ceiling", audit_details=audit
        )

    # Step 3: Compartment check
    for compartment in item.compartments:
        if not requester_clearance.has_compartment(compartment):
            return AccessDecision(
                allowed=False,
                reason=f"Missing compartment: {compartment!r}",
                step_failed=3, rule_applied="compartment_missing", audit_details=audit
            )

    # Step 4: Containment check (cascade rules)
    cascade = cascade_check(
        requester_address=requester_address,
        item_owner_address=item.owning_unit_address,
        classification=item.classification,
        requester_posture=requester_posture,
        requester_clearance=requester_clearance,
        ksp_registry=ksp_registry,
        bridge_registry=bridge_registry,
        operation=operation,
    )
    if not cascade.allowed:
        return AccessDecision(
            allowed=False, reason=cascade.reason,
            step_failed=4, rule_applied=cascade.rule_applied, audit_details=audit
        )

    # All steps passed — access granted
    return AccessDecision(
        allowed=True, reason="All steps passed",
        step_failed=None, rule_applied=cascade.rule_applied, audit_details=audit
    )
```

The `audit_details` dict must contain enough information for an EATP audit anchor (TODO-4003) to reconstruct the decision later. Include: requester address, item_id, classification, effective clearance, posture, operation, step results, timestamp.

Estimated size: ~400 LOC implementation (access.py grows to ~600 LOC total across 2003/2004/2005/2006), ~500 LOC tests.
