# TODO-4002: In-Memory Governance Store Implementations

Status: pending
Priority: high
Dependencies: [4001]
Milestone: M4

## What

Implement all 4 governance store protocols as in-memory classes backed by Python dicts with bounded collections. These implementations are the canonical choice for unit tests and for development environments that don't need durability.

Per trust-plane security rules, all collections are bounded (`maxlen` enforced). When a store reaches capacity, it evicts the oldest entry (LRU-style). The default capacity is 10,000 entries per store type.

The in-memory stores must be importable from `pact.governance.store` without any optional dependencies — no SQLite imports, no file I/O.

## Where

- `src/pact/governance/store.py` — `InMemoryOrgStore`, `InMemoryEnvelopeStore`, `InMemoryClearanceStore`, `InMemoryAccessPolicyStore` (alongside the Protocol definitions from TODO-4001)
- `tests/unit/governance/test_memory_stores.py` — full test coverage for all 4 in-memory implementations

## Evidence

- All 4 in-memory stores pass `isinstance(store, <Protocol>)` checks
- All store operations work (store, get, list, delete, update, revoke)
- Bounded collection: create 10,001 KSP records in `InMemoryAccessPolicyStore`; the oldest is evicted, only 10,000 remain
- `get_nodes_by_prefix` on `InMemoryOrgStore` returns correct subset using string prefix matching
- `find_ksp_for_pair` returns only matching policies
- `find_bridges_for_address` returns bridges where address appears as either participant
- `OrgNotFoundError`, `EnvelopeNotFoundError`, `ClearanceNotFoundError`, `PolicyNotFoundError`, `BridgeNotFoundError` raised on missing records
- `pytest tests/unit/governance/test_memory_stores.py` passes

## Details

### Bounded dict helper

Use `collections.OrderedDict` for all internal stores to maintain insertion order for LRU eviction:

```python
from collections import OrderedDict

_MAX_ENTRIES = 10_000

class _BoundedDict:
    """OrderedDict with maximum capacity and LRU eviction."""

    def __init__(self, maxsize: int = _MAX_ENTRIES) -> None:
        self._data: OrderedDict[str, dict] = OrderedDict()
        self._maxsize = maxsize

    def set(self, key: str, value: dict) -> None:
        if key in self._data:
            self._data.move_to_end(key)
        else:
            if len(self._data) >= self._maxsize:
                self._data.popitem(last=False)  # evict oldest
        self._data[key] = value

    def get(self, key: str) -> dict | None:
        return self._data.get(key)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def values(self) -> list[dict]:
        return list(self._data.values())

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def __len__(self) -> int:
        return len(self._data)
```

### InMemoryOrgStore

```python
class InMemoryOrgStore:
    def __init__(self, maxsize: int = _MAX_ENTRIES) -> None:
        self._orgs: _BoundedDict = _BoundedDict(maxsize)

    def store_org(self, org_id: str, record: dict) -> None:
        self._orgs.set(org_id, record)

    def get_org(self, org_id: str) -> dict:
        result = self._orgs.get(org_id)
        if result is None:
            raise OrgNotFoundError(org_id)
        return result

    def list_orgs(self) -> list[str]:
        return self._orgs.keys()

    def delete_org(self, org_id: str) -> None:
        if self._orgs.get(org_id) is None:
            raise OrgNotFoundError(org_id)
        self._orgs.delete(org_id)

    def get_nodes_by_prefix(self, org_id: str, address_prefix: str) -> list[dict]:
        """Return nodes from compiled org whose address starts with address_prefix."""
        org = self.get_org(org_id)
        nodes = org.get("nodes", [])
        return [n for n in nodes if n.get("address", "").startswith(address_prefix)]
```

### InMemoryEnvelopeStore

Maintains two separate `_BoundedDict` instances: one for role envelopes, one for task envelopes. The `get_role_envelope_for_address` method scans the role envelope store for a matching `role_address` field. The `list_task_envelopes_for_role` method scans task envelopes for a matching `role_address` field.

### InMemoryClearanceStore

Keyed by `role_address` (the natural key for clearances — one clearance per role). The `update_vetting_status` method validates the state transition using the `_ALLOWED_TRANSITIONS` mapping from `clearance.py` before writing; raises `ClearanceStateError` on invalid transition.

The `list_clearances` method accepts an optional `org_id` prefix: when provided, returns only clearances whose `role_address` starts with the org_id. This mirrors the prefix-query behaviour of `get_nodes_by_prefix`.

### InMemoryAccessPolicyStore

Maintains two `_BoundedDict` instances: one for KSPs, one for bridges.

`find_ksp_for_pair(requester_address, target_item_classification)`: scan all KSPs, return those where:

- `ksp["permitted_requester_prefix"]` is a prefix of `requester_address` (or exact match), AND
- `ksp["max_classification"]` >= `target_item_classification` (using `ConfidentialityLevel` ordering)

`find_bridges_for_address(address)`: scan all bridges, return those where `address` matches either `bridge["side_a"]` prefix or `bridge["side_b"]` prefix, AND `bridge["status"]` is not `"revoked"`.

`revoke_bridge(bridge_id)`: set `record["status"] = "revoked"` in the existing record. Does not delete — preserves audit trail. Raises `BridgeNotFoundError` if not present.

### Thread safety

The in-memory stores are NOT thread-safe by design (they are testing/development tools). Document this explicitly in each class docstring. Production deployments use the SQLite store (TODO-4004) which has thread-safety via `threading.local()`.

### Module-level exports

After this todo, `src/pact/governance/store.py` exports:

```python
__all__ = [
    # Protocols
    "OrgStore",
    "EnvelopeStore",
    "ClearanceStore",
    "AccessPolicyStore",
    # In-memory implementations
    "InMemoryOrgStore",
    "InMemoryEnvelopeStore",
    "InMemoryClearanceStore",
    "InMemoryAccessPolicyStore",
    # Errors (re-exported for convenience)
    "OrgNotFoundError",
    "EnvelopeNotFoundError",
    "ClearanceNotFoundError",
    "PolicyNotFoundError",
    "BridgeNotFoundError",
]
```
