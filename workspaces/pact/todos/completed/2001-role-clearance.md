# TODO-2001: RoleClearance model with compartments

Status: pending
Priority: high
Dependencies: [1001]
Milestone: M2

## What

Implement the `RoleClearance` dataclass per PACT-REQ-003. A clearance is assigned to a role (not to a person or agent) and controls the maximum classification of knowledge that role may access. Clearance is separate from authority — a senior role may have lower clearance than a junior specialist role.

Key responsibilities:

- `RoleClearance` dataclass: role address, clearance level (`ConfidentialityLevel`), optional compartments, vetting status, posture ceiling.
- `POSTURE_CEILING` mapping: for each clearance level, the maximum trust posture the role may be granted. HIGH clearance does not entitle high autonomy.
- `effective_clearance()` function: given a role's clearance and its current trust posture, return the effective (posture-capped) clearance level.
- Vetting status lifecycle: `PENDING`, `ACTIVE`, `SUSPENDED`, `REVOKED` with monotonic downgrade rules (ACTIVE can become SUSPENDED or REVOKED, never back to ACTIVE without re-vetting).
- Compartment enforcement: compartments are named access scopes meaningful only at SECRET and above. At PUBLIC through CONFIDENTIAL, compartments are ignored.

POSTURE_CEILING mapping (thesis Section 6.2):

| Clearance Level | Max Posture        |
| --------------- | ------------------ |
| PUBLIC          | CONTINUOUS_INSIGHT |
| RESTRICTED      | CONTINUOUS_INSIGHT |
| CONFIDENTIAL    | SHARED_PLANNING    |
| SECRET          | SUPERVISED         |
| TOP_SECRET      | SUPERVISED         |

Rationale: higher clearance means more sensitive knowledge, therefore tighter human oversight. An agent with SECRET clearance may not operate autonomously — it must remain under SUPERVISED or SHARED_PLANNING.

## Where

- `src/pact/governance/clearance.py` — `RoleClearance`, `VettingStatus`, `POSTURE_CEILING`, `effective_clearance()`
- `tests/unit/governance/test_clearance.py`

## Evidence

- Posture-capping works: a SUPERVISED agent with SECRET clearance has effective clearance SECRET (posture is compatible). A CONTINUOUS_INSIGHT agent with SECRET clearance has effective clearance RESTRICTED (capped because CONTINUOUS_INSIGHT exceeds the SECRET posture ceiling of SUPERVISED).
- Compartment enforcement works: a role with SECRET/[AML] compartment can access SECRET AML data; a role with SECRET but no AML compartment cannot.
- Vetting status transitions validated: PENDING → ACTIVE allowed; REVOKED → ACTIVE rejected with `ClearanceStateError`.
- `effective_clearance()` returns the minimum of the role's clearance and the posture ceiling for the agent's current posture.

## Details

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from pact.build.config.schema import ConfidentialityLevel, TrustPostureLevel

class VettingStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"

# Transitions allowed: PENDING->ACTIVE, ACTIVE->SUSPENDED, ACTIVE->REVOKED,
# SUSPENDED->REVOKED only. No upward transitions without re-vetting.
_ALLOWED_TRANSITIONS: dict[VettingStatus, set[VettingStatus]] = {
    VettingStatus.PENDING: {VettingStatus.ACTIVE},
    VettingStatus.ACTIVE: {VettingStatus.SUSPENDED, VettingStatus.REVOKED},
    VettingStatus.SUSPENDED: {VettingStatus.REVOKED},
    VettingStatus.REVOKED: set(),
}

# Thesis Section 6.2 table — higher clearance, tighter posture ceiling.
POSTURE_CEILING: dict[ConfidentialityLevel, TrustPostureLevel] = {
    ConfidentialityLevel.PUBLIC: TrustPostureLevel.CONTINUOUS_INSIGHT,
    ConfidentialityLevel.RESTRICTED: TrustPostureLevel.CONTINUOUS_INSIGHT,
    ConfidentialityLevel.CONFIDENTIAL: TrustPostureLevel.SHARED_PLANNING,
    ConfidentialityLevel.SECRET: TrustPostureLevel.SUPERVISED,
    ConfidentialityLevel.TOP_SECRET: TrustPostureLevel.SUPERVISED,
}

@dataclass
class RoleClearance:
    role_address: str          # D/T/R positional address from TODO-1001
    level: ConfidentialityLevel
    compartments: frozenset[str] = field(default_factory=frozenset)
    vetting_status: VettingStatus = VettingStatus.PENDING

    def transition(self, new_status: VettingStatus) -> None:
        """Monotonic downgrade only. Raises ClearanceStateError on invalid."""
        ...

    def has_compartment(self, compartment: str) -> bool:
        """Compartments only meaningful at SECRET and above."""
        if self.level not in (ConfidentialityLevel.SECRET, ConfidentialityLevel.TOP_SECRET):
            return True  # compartments not applicable below SECRET — vacuously true
        return compartment in self.compartments

def effective_clearance(
    clearance: RoleClearance, posture: TrustPostureLevel
) -> ConfidentialityLevel:
    """Return the posture-capped clearance for an agent at a given posture."""
    ...
```

Module layout: `src/pact/governance/clearance.py`. The `pact.governance` package is new — create `src/pact/governance/__init__.py` with `__all__` if not already present from TODO-0003.

Use `@dataclass` (not Pydantic) consistent with EATP SDK conventions. Every dataclass must have `to_dict()` and `from_dict()`.

Error class: `ClearanceStateError(PactGovernanceError)` in `src/pact/governance/exceptions.py`.
