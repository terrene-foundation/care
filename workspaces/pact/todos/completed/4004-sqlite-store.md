# TODO-4004: SQLite Governance Store Implementation

Status: pending
Priority: high
Dependencies: [4001]
Milestone: M4

## What

Implement all 4 governance store protocols as a SQLite-backed persistence layer. This is the durable store for production and for integration tests that need data to survive process restarts. The implementation follows the same patterns established in `src/pact/trust/store/sqlite_store.py`: per-thread connections via `threading.local()`, WAL journal mode, `PRAGMA foreign_keys=ON`, double-checked locking for table creation.

All records are stored as JSON blobs in typed tables. Address-indexed queries use SQLite `LIKE 'prefix%'` for efficient prefix matching — this is the O(n log n) approach enabled by SQLite's index support on TEXT columns.

All queries use parameterized statements (no f-string interpolation). All identifier arguments are validated before use.

## Where

- `src/pact/governance/store/sqlite_store.py` — `SQLiteGovernanceStore` class implementing all 4 protocols in one store object (simpler than 4 separate store classes that would all open the same DB file)
- `src/pact/governance/store/__init__.py` — re-exports protocols + both implementations
- `tests/unit/governance/test_sqlite_stores.py` — full test suite

## Evidence

- `SQLiteGovernanceStore(":memory:")` creates all tables without error
- `SQLiteGovernanceStore("/tmp/test_gov.db")` persists across instantiation (data survives)
- `isinstance(store, OrgStore)` is True
- `isinstance(store, EnvelopeStore)` is True
- `isinstance(store, ClearanceStore)` is True
- `isinstance(store, AccessPolicyStore)` is True
- Prefix query: `store.get_nodes_by_prefix("uni", "D1-R1-D3")` returns only nodes under that prefix via LIKE query
- Parameterized queries: no raw string interpolation in any SQL statement
- `PRAGMA foreign_keys=ON` and `PRAGMA journal_mode=WAL` set on every connection
- Schema migration: adding the store to an existing DB with tables already present does not raise
- `pytest tests/unit/governance/test_sqlite_stores.py` passes

## Details

### Single class, 4 protocols

Rather than 4 separate store classes (each opening its own connection to the same DB file), implement one `SQLiteGovernanceStore` class that satisfies all 4 protocols. This avoids the multiple-pool anti-pattern and simplifies the caller's setup.

```python
class SQLiteGovernanceStore:
    """SQLite-backed implementation of all 4 PACT governance store protocols.

    One class, one database file, four protocol implementations.
    Thread-safe via per-thread connections (threading.local()).

    Usage:
        store = SQLiteGovernanceStore("governance.db")
        store.store_org("uni-2026", org_record)
        store.store_clearance("D1-R1-D3-R1", clearance_record)
    """
```

The class satisfies `isinstance(store, OrgStore)` etc. because `OrgStore` is `@runtime_checkable Protocol` and `SQLiteGovernanceStore` has all required methods.

### Schema

```sql
-- Orgs table: stores compiled org JSON blobs
CREATE TABLE IF NOT EXISTS governance_orgs (
    org_id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Org nodes: denormalized for prefix queries
-- Each row is one node from a compiled org's node list
CREATE TABLE IF NOT EXISTS governance_org_nodes (
    org_id TEXT NOT NULL,
    address TEXT NOT NULL,
    data TEXT NOT NULL,
    PRIMARY KEY (org_id, address)
);
CREATE INDEX IF NOT EXISTS idx_gov_nodes_address
    ON governance_org_nodes(org_id, address);

-- Role envelopes (standing)
CREATE TABLE IF NOT EXISTS governance_role_envelopes (
    envelope_id TEXT PRIMARY KEY,
    role_address TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_gov_role_env_address
    ON governance_role_envelopes(role_address);

-- Task envelopes (ephemeral)
CREATE TABLE IF NOT EXISTS governance_task_envelopes (
    envelope_id TEXT PRIMARY KEY,
    role_address TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_gov_task_env_role
    ON governance_task_envelopes(role_address);

-- Clearance records (one per role_address)
CREATE TABLE IF NOT EXISTS governance_clearances (
    role_address TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- KnowledgeSharePolicy records
CREATE TABLE IF NOT EXISTS governance_ksps (
    policy_id TEXT PRIMARY KEY,
    permitted_requester_prefix TEXT NOT NULL,
    max_classification TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_gov_ksp_requester
    ON governance_ksps(permitted_requester_prefix);

-- Bridge records (status column for revocation without deletion)
CREATE TABLE IF NOT EXISTS governance_bridges (
    bridge_id TEXT PRIMARY KEY,
    side_a TEXT NOT NULL,
    side_b TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    data TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_gov_bridge_side_a ON governance_bridges(side_a);
CREATE INDEX IF NOT EXISTS idx_gov_bridge_side_b ON governance_bridges(side_b);
```

### Prefix query implementation

`get_nodes_by_prefix` uses the `governance_org_nodes` denormalized table:

```python
def get_nodes_by_prefix(self, org_id: str, address_prefix: str) -> list[dict]:
    conn = self._get_connection()
    cursor = conn.execute(
        "SELECT data FROM governance_org_nodes "
        "WHERE org_id = ? AND address LIKE ?",
        (org_id, address_prefix + "%"),
    )
    return [json.loads(row[0]) for row in cursor.fetchall()]
```

The `store_org` method must populate `governance_org_nodes` from `record["nodes"]` when storing an org. This is a write-time denormalization to enable fast prefix reads.

### store_org atomicity

`store_org` must be atomic: it updates both `governance_orgs` and `governance_org_nodes` in one transaction. If the node population fails, the org record must not be written.

```python
def store_org(self, org_id: str, record: dict) -> None:
    conn = self._get_connection()
    with conn:  # transaction
        conn.execute(
            "INSERT OR REPLACE INTO governance_orgs (org_id, data, updated_at) "
            "VALUES (?, ?, datetime('now'))",
            (org_id, json.dumps(record)),
        )
        # Delete existing nodes for this org (full replace)
        conn.execute(
            "DELETE FROM governance_org_nodes WHERE org_id = ?", (org_id,)
        )
        for node in record.get("nodes", []):
            conn.execute(
                "INSERT INTO governance_org_nodes (org_id, address, data) "
                "VALUES (?, ?, ?)",
                (org_id, node["address"], json.dumps(node)),
            )
```

### find_ksp_for_pair implementation

`find_ksp_for_pair` must handle the prefix relationship between requester address and KSP prefix. The query fetches candidates by requester prefix match and then filters by classification in Python (since classification ordering is not representable as a simple SQL predicate without a lookup table):

```python
def find_ksp_for_pair(
    self, requester_address: str, target_item_classification: str
) -> list[dict]:
    conn = self._get_connection()
    # Fetch all KSPs where the stored prefix is a prefix of the requester address
    # Note: this requires scanning, but KSP tables are small
    cursor = conn.execute("SELECT data FROM governance_ksps")
    results = []
    for row in cursor.fetchall():
        ksp = json.loads(row[0])
        prefix = ksp.get("permitted_requester_prefix", "")
        if requester_address.startswith(prefix):
            results.append(ksp)
    return results
```

### Thread safety

Follow `src/pact/trust/store/sqlite_store.py` pattern exactly:

- `threading.local()` for per-thread connections
- `threading.Lock()` for write serialization in shared-cache mode
- Double-checked locking in `_ensure_tables()`
- WAL mode + `busy_timeout=5000`

### Security requirements

- No f-string SQL interpolation anywhere in this file
- `PRAGMA foreign_keys=ON` on every connection
- Parameterized queries for all user-supplied values
- File permissions: set `0o600` on the DB file at creation time (owner read/write only)
