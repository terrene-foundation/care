# TODO-2004: PactBridge (address-based)

Status: pending
Priority: high
Dependencies: [1001, 2001]
Milestone: M2

## What

Implement `PactBridge` per PACT-REQ-006. A Bridge establishes a working relationship between two D/T/R roles that are not in the same containment chain. Bridges are the mechanism by which the CCO can review Advisory data and Trading data simultaneously — not through higher clearance, but through explicit bilateral authority granted by a common ancestor.

Bridge types per thesis Section 4.4:

- **Standing**: permanent, recurring relationship (e.g., CCO reviews all business lines). Requires approval from the lowest common ancestor or a designated compliance role.
- **Scoped**: time-bounded or task-bounded relationship (e.g., M&A review committee access for 90 days). Must specify `expires_at` or `task_scope`.
- **Ad-Hoc**: immediate, short-term. Still requires ancestor approval but can be granted more quickly with automatic expiry.

Key fields:

- `bridge_id`: unique identifier
- `role_a`: D/T/R address of the first party (full role address including R terminal)
- `role_b`: D/T/R address of the second party
- `bridge_type`: `BridgeType` enum (STANDING, SCOPED, AD_HOC)
- `max_classification`: maximum `ConfidentialityLevel` accessible across this bridge
- `operational_scope`: set of operation strings the bridge permits (e.g., `{"read", "review"}` — not `"write"` or `"execute"`)
- `bilateral`: whether both parties get symmetric access (default True for Standing)
- `approved_by`: address of the role that approved — must be a common ancestor of `role_a` and `role_b`, or a designated compliance role at that level
- `expires_at`: required for SCOPED and AD_HOC; optional for STANDING

Thesis Section 4.4 property 5: **a bridge does not elevate clearance**. The bridge grants access to knowledge up to `max_classification`, but only up to the minimum clearance of either party. The effective bridge ceiling is `min(role_a_clearance, role_b_clearance, bridge.max_classification)`. This is enforced in the access algorithm (TODO-2006), not in the bridge model itself — the bridge model records intent, the access algorithm enforces constraints.

Property from thesis Section 5.3: bridge scope is subject to monotonic tightening. The bridge's `max_classification` and `operational_scope` cannot exceed either party's effective envelope classification ceiling or allowed operations. This is validated at bridge creation.

`find_bridge()` helper: searches a bridge registry for a valid (non-expired, matching operational scope) bridge between two roles.

## Where

- `src/pact/governance/access.py` — `PactBridge`, `BridgeType`, `find_bridge()`
- `tests/unit/governance/test_bridge.py`

## Evidence

- Standing bridge between CCO role (D1-R1-R1) and Advisory (D1-R1-T1-R1), approved by D1-R1, constructs successfully.
- Bridge where `approved_by` is not a common ancestor of both roles raises `BridgeApprovalError`.
- Bridge where `role_a == role_b` raises `ValueError`.
- AD_HOC bridge without `expires_at` raises `ValueError` (ad-hoc must expire).
- `find_bridge(registry, role_a="D1-R1-R1", role_b="D1-R1-T1-R1", operation="read", classification=CONFIDENTIAL)` returns the bridge.
- Expired bridge not returned by `find_bridge()`.
- Bridge with `operational_scope={"read"}` not returned for operation `"write"`.
- `find_bridge()` returns `None` when bridge scope doesn't cover the requested classification level.

## Details

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from pact.build.config.schema import ConfidentialityLevel

class BridgeType(str, Enum):
    STANDING = "standing"
    SCOPED = "scoped"
    AD_HOC = "ad_hoc"

@dataclass(frozen=True)
class PactBridge:
    bridge_id: str
    role_a: str
    role_b: str
    bridge_type: BridgeType
    max_classification: ConfidentialityLevel
    approved_by: str           # Common ancestor or compliance role
    operational_scope: frozenset[str] = field(default_factory=frozenset)
    bilateral: bool = True
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.role_a == self.role_b:
            raise ValueError("role_a and role_b must differ")
        if self.bridge_type in (BridgeType.SCOPED, BridgeType.AD_HOC) and not self.expires_at:
            raise ValueError(f"{self.bridge_type} bridges must specify expires_at")
        # validate approved_by is common ancestor — uses TODO-1001 address utilities

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def covers_operation(self, operation: str) -> bool:
        if not self.operational_scope:
            return True   # empty scope = all operations permitted
        return operation in self.operational_scope

    def covers_classification(self, classification: ConfidentialityLevel) -> bool:
        return _CLASSIFICATION_ORDER[classification] <= _CLASSIFICATION_ORDER[self.max_classification]

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PactBridge: ...


def find_bridge(
    registry: list[PactBridge],
    role_a: str,
    role_b: str,
    operation: str,
    classification: ConfidentialityLevel,
) -> PactBridge | None:
    """Find a valid bridge connecting role_a to role_b for the given operation and classification.

    Returns None when no applicable bridge exists. None means access is denied at the bridge step.
    """
    for bridge in registry:
        if bridge.is_expired():
            continue
        if not bridge.covers_operation(operation):
            continue
        if not bridge.covers_classification(classification):
            continue
        # Direct match
        if bridge.role_a == role_a and bridge.role_b == role_b:
            return bridge
        # Bilateral match
        if bridge.bilateral and bridge.role_a == role_b and bridge.role_b == role_a:
            return bridge
    return None
```

Error class: `BridgeApprovalError(PactGovernanceError)` in `src/pact/governance/exceptions.py`.

Note: `PactBridge` is distinct from the earlier Cross-Functional Bridge concept in the CARE Platform codebase. This is a pure governance data type — it carries no execution machinery. The execution bridge (Kaizen workspace coordination) is a separate concern and lives in `src/pact/use/`.
