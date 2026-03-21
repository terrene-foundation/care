# TODO-4001: Governance Store Protocols

Status: pending
Priority: high
Dependencies: [1003, 2001, 2003, 2004, 3002, 3003]
Milestone: M4

## What

Define Python `Protocol` classes for all 4 governance stores required by PACT-REQ-012. These protocols establish the typed contracts that both in-memory and SQLite implementations must satisfy. Using `typing.Protocol` (structural subtyping) means any class with the right method signatures is a valid implementation — no inheritance required.

The 4 stores and their record types:

- `OrgStore` — compiled org records (positional addresses, role hierarchy, node definitions)
- `EnvelopeStore` — role and task envelopes (standing and ephemeral constraint envelopes)
- `ClearanceStore` — role clearance records (level, compartments, vetting status)
- `AccessPolicyStore` — KnowledgeSharePolicy and PactBridge records

Each protocol defines the complete CRUD interface. No optional methods — every implementation must provide every method. The protocols live alongside the implementations in `src/pact/governance/store.py` (or `src/pact/governance/store/__init__.py` if the module is large enough to warrant a package).

## Where

- `src/pact/governance/store.py` — all 4 Protocol classes
- `tests/unit/governance/test_store_protocols.py` — protocol compliance tests via `typing.runtime_checkable` and direct method-signature inspection

## Evidence

- All 4 Protocol classes defined: `OrgStore`, `EnvelopeStore`, `ClearanceStore`, `AccessPolicyStore`
- Each protocol decorated with `@runtime_checkable` so `isinstance(impl, OrgStore)` works
- `from pact.governance.store import OrgStore, EnvelopeStore, ClearanceStore, AccessPolicyStore` succeeds
- Type checking: mypy/pyright accepts a concrete class that implements a protocol without explicit inheritance
- Unit test: a minimal inline class that satisfies each protocol passes `isinstance` check
- Unit test: a class missing one required method fails the `isinstance` check (negative test)

## Details

### OrgStore

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class OrgStore(Protocol):
    """Persistence for compiled org records (positional address tree)."""

    def store_org(self, org_id: str, record: dict) -> None:
        """Store or overwrite a compiled org record."""
        ...

    def get_org(self, org_id: str) -> dict:
        """Retrieve a compiled org record.

        Raises:
            OrgNotFoundError: if org_id does not exist.
        """
        ...

    def list_orgs(self) -> list[str]:
        """Return all stored org IDs."""
        ...

    def delete_org(self, org_id: str) -> None:
        """Delete an org record.

        Raises:
            OrgNotFoundError: if org_id does not exist.
        """
        ...

    def get_nodes_by_prefix(self, org_id: str, address_prefix: str) -> list[dict]:
        """Return all nodes whose address starts with address_prefix.

        Used for containment queries: get_nodes_by_prefix("uni", "D1-R1-D3")
        returns all descendants of D1-R1-D3.
        """
        ...
```

### EnvelopeStore

```python
@runtime_checkable
class EnvelopeStore(Protocol):
    """Persistence for role envelopes (standing) and task envelopes (ephemeral)."""

    def store_role_envelope(self, envelope_id: str, record: dict) -> None: ...

    def get_role_envelope(self, envelope_id: str) -> dict:
        """Raises EnvelopeNotFoundError if not found."""
        ...

    def get_role_envelope_for_address(self, address: str) -> dict | None:
        """Return the role envelope for the given D/T/R address, or None."""
        ...

    def store_task_envelope(self, envelope_id: str, record: dict) -> None: ...

    def get_task_envelope(self, envelope_id: str) -> dict:
        """Raises EnvelopeNotFoundError if not found."""
        ...

    def list_task_envelopes_for_role(self, role_address: str) -> list[dict]:
        """Return all task envelopes associated with a role address."""
        ...

    def delete_task_envelope(self, envelope_id: str) -> None: ...
```

### ClearanceStore

```python
@runtime_checkable
class ClearanceStore(Protocol):
    """Persistence for role clearance records."""

    def store_clearance(self, role_address: str, record: dict) -> None:
        """Store or replace the clearance for a role address."""
        ...

    def get_clearance(self, role_address: str) -> dict:
        """Raises ClearanceNotFoundError if no clearance assigned to role."""
        ...

    def list_clearances(self, org_id: str | None = None) -> list[dict]:
        """Return all clearance records, optionally filtered by org prefix."""
        ...

    def update_vetting_status(self, role_address: str, new_status: str) -> None:
        """Update vetting status only. Raises on invalid state transition."""
        ...

    def revoke_clearance(self, role_address: str) -> None:
        """Set vetting_status to REVOKED. Idempotent."""
        ...
```

### AccessPolicyStore

```python
@runtime_checkable
class AccessPolicyStore(Protocol):
    """Persistence for KnowledgeSharePolicy (KSP) and PactBridge records."""

    def store_ksp(self, policy_id: str, record: dict) -> None: ...

    def get_ksp(self, policy_id: str) -> dict:
        """Raises PolicyNotFoundError if not found."""
        ...

    def find_ksp_for_pair(
        self, requester_address: str, target_item_classification: str
    ) -> list[dict]:
        """Find all KSPs that permit the requester to access items of the given classification."""
        ...

    def store_bridge(self, bridge_id: str, record: dict) -> None: ...

    def get_bridge(self, bridge_id: str) -> dict:
        """Raises BridgeNotFoundError if not found."""
        ...

    def find_bridges_for_address(self, address: str) -> list[dict]:
        """Return bridges where address is a participant (either side)."""
        ...

    def revoke_bridge(self, bridge_id: str) -> None:
        """Mark bridge as revoked. Does not delete — preserves audit trail."""
        ...
```

### Error classes

Add to `src/pact/governance/exceptions.py` (or create if not present from TODO-0003):

```python
class OrgNotFoundError(PactGovernanceError): ...
class EnvelopeNotFoundError(PactGovernanceError): ...
class ClearanceNotFoundError(PactGovernanceError): ...
class PolicyNotFoundError(PactGovernanceError): ...
class BridgeNotFoundError(PactGovernanceError): ...
```

### Design constraints

- All protocol methods are synchronous. Async variants are a future concern.
- Record dicts use the same serialization format as the corresponding dataclass `to_dict()` methods (from M1/M2/M3 todos).
- Protocol methods must not carry default implementations — a `Protocol` method body is `...` only.
- `@runtime_checkable` is required on every protocol to enable `isinstance` checks in tests.
- The `get_nodes_by_prefix` query on `OrgStore` is the primary enabler for address-indexed containment queries needed by the Access Enforcement Algorithm (TODO-2006).
