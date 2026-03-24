# TODO-4003: EATP Audit Anchor Subtypes for Governance Events

Status: pending
Priority: high
Dependencies: []
Milestone: M4

## What

Extend the existing EATP audit infrastructure with PACT-specific action type constants and a helper function `create_pact_audit_anchor()`. Per thesis Section 5.7 normative mapping, every governance event that modifies trust state must produce an audit anchor. The existing `EATPBridge.create_audit_anchor()` is reused — this todo adds the action type vocabulary and a thin helper so governance code doesn't need to directly call the bridge.

The 10 action type constants:

| Constant             | Event                                                    |
| -------------------- | -------------------------------------------------------- |
| `ENVELOPE_CREATED`   | A new role or task envelope is stored                    |
| `ENVELOPE_MODIFIED`  | An existing envelope is updated (tightening only)        |
| `CLEARANCE_GRANTED`  | A clearance record is stored for a role address          |
| `CLEARANCE_REVOKED`  | A clearance record is revoked (vetting_status → REVOKED) |
| `BARRIER_ENFORCED`   | Access denied by Access Enforcement Algorithm            |
| `KSP_CREATED`        | A KnowledgeSharePolicy is stored                         |
| `KSP_REVOKED`        | A KnowledgeSharePolicy is revoked                        |
| `BRIDGE_ESTABLISHED` | A PactBridge is stored and active                        |
| `BRIDGE_REVOKED`     | A PactBridge is revoked                                  |
| `ADDRESS_COMPUTED`   | A positional address is assigned during org compilation  |

The `BARRIER_ENFORCED` anchor carries the richest payload because it is the primary accountability record for denied access. Its `details` field must include: requesting role address, target item (what was being accessed), step number in the 5-step algorithm that caused denial, and the denial reason string.

The effective envelope is captured in the audit anchor at verification time — the anchor records what constraint dimensions were in force at the moment of the decision, not just that a decision was made.

## Where

- `src/pact/governance/audit.py` — action type constants, `PactAuditAction` enum, `create_pact_audit_anchor()` helper, `BarrierEnforcedDetails` dataclass
- `tests/unit/governance/test_audit_subtypes.py` — one test per action type; BARRIER_ENFORCED payload test

## Evidence

- `from pact.governance.audit import PactAuditAction, create_pact_audit_anchor, BarrierEnforcedDetails` succeeds
- Each of the 10 action types is defined as a `PactAuditAction` enum member
- `create_pact_audit_anchor(bridge, action, agent_id, details)` calls `bridge.create_audit_anchor()` and returns an `AuditAnchor`
- `BARRIER_ENFORCED` test: `details["requesting_role"]`, `details["target_item"]`, `details["step_failed"]`, `details["reason"]` all present in the resulting anchor's details
- `ENVELOPE_CREATED` test: anchor created without error; action field equals `"envelope_created"`
- `ADDRESS_COMPUTED` test: anchor created with `details["address"]` present
- `pytest tests/unit/governance/test_audit_subtypes.py` passes

## Details

### PactAuditAction enum

```python
# src/pact/governance/audit.py
# Copyright 2026 Terrene Foundation
# SPDX-License-Identifier: Apache-2.0
"""PACT governance audit anchor subtypes.

Per thesis Section 5.7: every governance state change produces an EATP
audit anchor. The action type identifies the governance event; the details
field carries event-specific payload.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "PactAuditAction",
    "BarrierEnforcedDetails",
    "create_pact_audit_anchor",
]


class PactAuditAction(str, Enum):
    """PACT-specific action types for EATP audit anchors.

    Values are lowercase strings (JSON-serializable via .value).
    """
    ENVELOPE_CREATED = "envelope_created"
    ENVELOPE_MODIFIED = "envelope_modified"
    CLEARANCE_GRANTED = "clearance_granted"
    CLEARANCE_REVOKED = "clearance_revoked"
    BARRIER_ENFORCED = "barrier_enforced"
    KSP_CREATED = "ksp_created"
    KSP_REVOKED = "ksp_revoked"
    BRIDGE_ESTABLISHED = "bridge_established"
    BRIDGE_REVOKED = "bridge_revoked"
    ADDRESS_COMPUTED = "address_computed"
```

### BarrierEnforcedDetails dataclass

```python
@dataclass
class BarrierEnforcedDetails:
    """Structured payload for BARRIER_ENFORCED audit anchors.

    Captures the full context of an access denial so it can be reviewed
    by a governance supervisor without re-running the algorithm.
    """
    requesting_role: str        # D/T/R address of the requester
    target_item: str            # Identifier of the knowledge item requested
    target_classification: str  # ConfidentialityLevel of the item
    step_failed: int            # Which step of the 5-step algorithm (1-5)
    reason: str                 # Human-readable denial reason
    effective_envelope: dict    # Serialized effective envelope at denial time
    compartment_required: str | None = None  # If compartment check failed

    def to_dict(self) -> dict[str, Any]:
        return {
            "requesting_role": self.requesting_role,
            "target_item": self.target_item,
            "target_classification": self.target_classification,
            "step_failed": self.step_failed,
            "reason": self.reason,
            "effective_envelope": self.effective_envelope,
            "compartment_required": self.compartment_required,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BarrierEnforcedDetails":
        return cls(
            requesting_role=data["requesting_role"],
            target_item=data["target_item"],
            target_classification=data["target_classification"],
            step_failed=data["step_failed"],
            reason=data["reason"],
            effective_envelope=data["effective_envelope"],
            compartment_required=data.get("compartment_required"),
        )
```

### create_pact_audit_anchor helper

```python
def create_pact_audit_anchor(
    bridge: "EATPBridge",
    action: PactAuditAction,
    agent_id: str,
    details: dict[str, Any] | None = None,
) -> "AuditAnchor":
    """Create an EATP audit anchor for a PACT governance event.

    Wraps EATPBridge.create_audit_anchor() with PACT action type vocabulary.
    The caller is responsible for storing the returned anchor.

    Args:
        bridge: The EATPBridge instance for the org's trust authority.
        action: PactAuditAction enum member identifying the governance event.
        agent_id: EATP agent ID of the entity performing the action.
        details: Event-specific payload dict (use BarrierEnforcedDetails.to_dict()
                 for BARRIER_ENFORCED events).

    Returns:
        AuditAnchor from the EATP SDK.
    """
    return bridge.create_audit_anchor(
        agent_id=agent_id,
        action=action.value,
        details=details or {},
    )
```

### Integration with governance operations

Governance modules that change state (clearance.py, barrier.py, envelope modules) call `create_pact_audit_anchor()` after successful mutations. They do not call `EATPBridge` directly for audit purposes — all governance audit anchors go through the `PactAuditAction` vocabulary.

The `BARRIER_ENFORCED` anchor is created by the Access Enforcement Algorithm (TODO-2006) on every denied access, not just policy violations. This ensures the audit log is complete — every denial is recorded, allowing supervisors to detect patterns.

### Dependency note

This todo has no dependency on other M4 todos. It extends the existing `EATPBridge` (already in `src/pact/trust/eatp_bridge.py`). It can be implemented in parallel with TODO-4001 and TODO-4002.
