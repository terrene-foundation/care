# TODO-2005: Knowledge cascade rules

Status: pending
Priority: high
Dependencies: [1001, 2001, 2003]
Milestone: M2

## What

Implement the knowledge cascade rules per PACT-REQ-008. These rules define how knowledge flows within and between organisational units before the 5-step access algorithm runs. The cascade rules are not a separate gate — they are the containment check logic called by Step 4 of the access algorithm (TODO-2006). They answer: "given the requester's position in the hierarchy and the knowledge item's position, is there a valid cascade path?"

Rules per thesis Section 6.4:

**Rule 1: Same-unit access (within same D or T)**

- PUBLIC and RESTRICTED: automatically accessible to any role in the same D or T. No KSP required.
- CONFIDENTIAL: accessible to roles in the same D or T with CONFIDENTIAL or higher clearance. No KSP required, but pre-clearance required.
- SECRET and TOP_SECRET: requires pre-clearance AND compartment match. No KSP required within the same unit.

**Rule 2: Cross-unit access (different D or T)**

- Any classification crossing a D/T boundary: requires a valid KSP (per TODO-2003).
- The KSP must cover the required classification level.
- Exception: a bridge (per TODO-2004) can substitute for a KSP for the purpose of reading; bridges never grant write access.

**Rule 3: Team-inherits-Department (T-inherits-D)**

- Team members can access department-level knowledge as if the department were their parent T.
- A role at D1-R1-T1-R1 can see PUBLIC/RESTRICTED data owned by D1-R1 without a KSP.
- The inheritance is one-way: D can see T's data only if a KSP exists (T's data is more contained).

**Rule 4: Posture-gated downward access**

- Access to CONFIDENTIAL data requires posture >= SHARED_PLANNING.
- Access to SECRET data requires posture >= SUPERVISED (i.e., always requires posture >= SUPERVISED since SUPERVISED is the ceiling for SECRET per POSTURE_CEILING in TODO-2001).
- PSEUDO_AGENT posture: read-only, PUBLIC/RESTRICTED only.
- DELEGATED posture: full clearance up to the role's ceiling.

The cascade logic returns a `CascadeResult` with `allowed: bool` and `rule_applied: str` (one of "same_unit", "t_inherits_d", "ksp", "bridge", "denied"). This becomes an input to Step 4 of the access algorithm.

## Where

- `src/pact/governance/access.py` — `cascade_check()`, `CascadeResult`
- `tests/unit/governance/test_cascade.py`

## Evidence

- Same-unit PUBLIC access granted without KSP. `cascade_check(requester="D1-R1-T1-R1", item_owner="D1-R1-T1-R1", classification=PUBLIC, ...)` returns `CascadeResult(allowed=True, rule_applied="same_unit")`.
- Cross-unit access denied without KSP. `cascade_check(requester="D1-R1-T1-R1", item_owner="D1-R1-T2-R1", classification=RESTRICTED, ksp_registry=[])` returns `CascadeResult(allowed=False, rule_applied="denied")`.
- T-inherits-D: `cascade_check(requester="D1-R1-T1-R1", item_owner="D1-R1", classification=PUBLIC, ...)` returns `CascadeResult(allowed=True, rule_applied="t_inherits_d")`.
- KSP grants cross-unit access: providing a valid KSP from T1 to T2 allows the check.
- Posture gate: PSEUDO_AGENT requester with valid KSP for CONFIDENTIAL item is denied with `rule_applied="posture_gate"`.
- SHARED_PLANNING requester with valid KSP for CONFIDENTIAL item is allowed.

## Details

```python
from __future__ import annotations
from dataclasses import dataclass
from pact.build.config.schema import ConfidentialityLevel, TrustPostureLevel
from pact.governance.access import KnowledgeSharePolicy, PactBridge, find_ksp, find_bridge
from pact.governance.clearance import RoleClearance, effective_clearance

_POSTURE_ORDER: dict[TrustPostureLevel, int] = {
    TrustPostureLevel.PSEUDO_AGENT: 0,
    TrustPostureLevel.SUPERVISED: 1,
    TrustPostureLevel.SHARED_PLANNING: 2,
    TrustPostureLevel.CONTINUOUS_INSIGHT: 3,
    TrustPostureLevel.DELEGATED: 4,
}

# Minimum posture required per classification level (from posture ceiling table inverted)
_MIN_POSTURE_FOR_CLASSIFICATION: dict[ConfidentialityLevel, TrustPostureLevel] = {
    ConfidentialityLevel.PUBLIC: TrustPostureLevel.PSEUDO_AGENT,
    ConfidentialityLevel.RESTRICTED: TrustPostureLevel.PSEUDO_AGENT,
    ConfidentialityLevel.CONFIDENTIAL: TrustPostureLevel.SHARED_PLANNING,
    ConfidentialityLevel.SECRET: TrustPostureLevel.SUPERVISED,
    ConfidentialityLevel.TOP_SECRET: TrustPostureLevel.SUPERVISED,
}

@dataclass
class CascadeResult:
    allowed: bool
    rule_applied: str   # "same_unit" | "t_inherits_d" | "ksp" | "bridge" | "posture_gate" | "denied"
    reason: str = ""


def cascade_check(
    requester_address: str,
    item_owner_address: str,
    classification: ConfidentialityLevel,
    requester_posture: TrustPostureLevel,
    requester_clearance: RoleClearance | None,
    ksp_registry: list[KnowledgeSharePolicy],
    bridge_registry: list[PactBridge],
    operation: str = "read",
) -> CascadeResult:
    """Determine whether knowledge can flow from owner to requester under cascade rules.

    This function implements Rules 1-4 above and is called by Step 4 of the access algorithm.
    Returns CascadeResult with allowed=False and rule_applied="denied" when no rule permits access.
    """
    # Rule 4: posture gate checked first — no cascade path can override it
    min_posture = _MIN_POSTURE_FOR_CLASSIFICATION[classification]
    if _POSTURE_ORDER[requester_posture] < _POSTURE_ORDER[min_posture]:
        return CascadeResult(allowed=False, rule_applied="posture_gate",
                             reason=f"Posture {requester_posture} insufficient for {classification}")

    # Rule 1: same-unit check
    # Rule 3: T-inherits-D check
    # Rule 2: cross-unit via KSP
    # Rule 2 (bridge variant): cross-unit via bridge (read-only)
    ...
```

The `cascade_check()` function should use the address utilities from TODO-1001 to determine:

- Whether `requester_address` and `item_owner_address` are in the same unit
- Whether `item_owner_address` is a direct parent department of the requester's team (T-inherits-D)
- Whether a KSP/bridge covers the cross-unit path

Keep posture ordering and cascade rules in this one function. The access algorithm (TODO-2006) calls this as Step 4 and trusts its result completely.
