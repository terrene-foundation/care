# TODO-5005: Public API Surface

Status: pending
Priority: high
Dependencies: [1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005, 2006, 3001, 3002, 3003, 3004, 3005, 3006, 4001, 4002, 4003, 4004]
Milestone: M5

## What

Define and export the clean public API surface for the PACT governance layer. Update `src/pact/__init__.py` to re-export governance primitives alongside the existing EATP/trust exports. Define what `from pact.governance import ...` exposes with a curated `__all__`.

The goal is a stable, minimal public surface: importers should be able to use PACT with only the symbols in `__all__`. Internal implementation details (`_BoundedDict`, `_ALLOWED_TRANSITIONS`, protocol internals) must not appear in `__all__`.

## Where

- `src/pact/governance/__init__.py` — curated `__all__` exporting the full governance API
- `src/pact/__init__.py` — add governance re-exports under a `governance` namespace comment
- `tests/unit/governance/test_public_api.py` — import surface tests

## Evidence

All of the following imports work without error:

```python
from pact.governance import (
    # Addressing
    Address,
    CompiledOrg,
    compile_org,
    # Clearance
    RoleClearance,
    VettingStatus,
    effective_clearance,
    # Knowledge items
    KnowledgeItem,
    ConfidentialityLevel,   # re-exported from pact.build.config.schema
    # Access policies
    KnowledgeSharePolicy,
    PactBridge,
    BridgeType,
    # Access enforcement
    can_access,
    AccessDecision,
    # Envelopes
    RoleEnvelope,
    TaskEnvelope,
    compute_effective_envelope,
    # Stores (protocols)
    OrgStore,
    EnvelopeStore,
    ClearanceStore,
    AccessPolicyStore,
    # Stores (in-memory implementations)
    InMemoryOrgStore,
    InMemoryEnvelopeStore,
    InMemoryClearanceStore,
    InMemoryAccessPolicyStore,
    # Audit
    PactAuditAction,
    BarrierEnforcedDetails,
    create_pact_audit_anchor,
    # Exceptions
    PactGovernanceError,
    OrgNotFoundError,
    EnvelopeNotFoundError,
    ClearanceNotFoundError,
    ClearanceStateError,
    PolicyNotFoundError,
    BridgeNotFoundError,
)
```

And from the top level:

```python
from pact.governance import Address, CompiledOrg, RoleClearance, KnowledgeSharePolicy, PactBridge, can_access, RoleEnvelope, TaskEnvelope, compute_effective_envelope
```

No internal implementation details leaked: `_BoundedDict`, `_ALLOWED_TRANSITIONS`, `_MAX_ENTRIES`, `SQLiteGovernanceStore` internal methods are NOT in `__all__`.

`SQLiteGovernanceStore` itself IS exported (users need to instantiate it for production). Its internal methods are not.

Import test: `import pact.governance as gov; dir(gov)` contains no symbols starting with `_`.

`pytest tests/unit/governance/test_public_api.py` passes.

## Details

### src/pact/governance/**init**.py

```python
# Copyright 2026 Terrene Foundation
# SPDX-License-Identifier: Apache-2.0
"""PACT governance layer public API.

Provides the complete PACT governance framework:
- D/T/R positional addressing and org compilation
- Knowledge clearance with compartments
- Information barriers and Cross-Functional Bridges
- Access Enforcement Algorithm (5-step)
- Constraint envelopes (role, task, effective)
- EATP audit anchor integration
- Persistence protocols and in-memory implementations

Typical usage:
    from pact.governance import compile_org, can_access, InMemoryOrgStore
    from pact.examples.university.org import build_university_org

    compiled = compile_org(build_university_org())
    # ... populate stores ...
    decision = can_access(agent_address, knowledge_item, stores)
"""

from __future__ import annotations

# Addressing and org compilation
from pact.governance.org import Address, CompiledOrg, compile_org

# Clearance
from pact.governance.clearance import (
    RoleClearance,
    VettingStatus,
    POSTURE_CEILING,
    effective_clearance,
    ClearanceStateError,
)

# Knowledge items
from pact.governance.knowledge import KnowledgeItem

# Access policies
from pact.governance.barrier import KnowledgeSharePolicy
from pact.governance.bridge import PactBridge, BridgeType

# Access enforcement
from pact.governance.access import can_access, AccessDecision

# Envelopes
from pact.governance.envelope import RoleEnvelope, TaskEnvelope, compute_effective_envelope

# Stores — protocols
from pact.governance.store import (
    OrgStore,
    EnvelopeStore,
    ClearanceStore,
    AccessPolicyStore,
)

# Stores — in-memory implementations
from pact.governance.store import (
    InMemoryOrgStore,
    InMemoryEnvelopeStore,
    InMemoryClearanceStore,
    InMemoryAccessPolicyStore,
)

# Stores — SQLite implementation (optional import — no hard dependency on sqlite3 here,
# but sqlite3 is stdlib so it's always available)
from pact.governance.store.sqlite_store import SQLiteGovernanceStore

# Audit
from pact.governance.audit import (
    PactAuditAction,
    BarrierEnforcedDetails,
    create_pact_audit_anchor,
)

# Exceptions
from pact.governance.exceptions import (
    PactGovernanceError,
    OrgNotFoundError,
    EnvelopeNotFoundError,
    ClearanceNotFoundError,
    PolicyNotFoundError,
    BridgeNotFoundError,
)

# Re-export ConfidentialityLevel from build layer for convenience
from pact.build.config.schema import ConfidentialityLevel

__all__ = [
    # Addressing
    "Address",
    "CompiledOrg",
    "compile_org",
    # Clearance
    "RoleClearance",
    "VettingStatus",
    "POSTURE_CEILING",
    "effective_clearance",
    # Knowledge
    "KnowledgeItem",
    "ConfidentialityLevel",
    # Access policies
    "KnowledgeSharePolicy",
    "PactBridge",
    "BridgeType",
    # Access enforcement
    "can_access",
    "AccessDecision",
    # Envelopes
    "RoleEnvelope",
    "TaskEnvelope",
    "compute_effective_envelope",
    # Store protocols
    "OrgStore",
    "EnvelopeStore",
    "ClearanceStore",
    "AccessPolicyStore",
    # Store implementations
    "InMemoryOrgStore",
    "InMemoryEnvelopeStore",
    "InMemoryClearanceStore",
    "InMemoryAccessPolicyStore",
    "SQLiteGovernanceStore",
    # Audit
    "PactAuditAction",
    "BarrierEnforcedDetails",
    "create_pact_audit_anchor",
    # Exceptions
    "PactGovernanceError",
    "OrgNotFoundError",
    "EnvelopeNotFoundError",
    "ClearanceNotFoundError",
    "ClearanceStateError",
    "PolicyNotFoundError",
    "BridgeNotFoundError",
]
```

### src/pact/**init**.py additions

Add a clearly-delimited governance section to the top-level `__init__.py`:

```python
# ---------------------------------------------------------------------------
# Governance layer (D/T/R grammar, clearance, barriers, envelopes)
# ---------------------------------------------------------------------------
from pact import governance  # noqa: F401 — expose as pact.governance submodule
```

Do not re-export individual governance symbols at the `pact.*` top level (to avoid polluting the namespace). Users import from `pact.governance`, not from `pact` directly.

### Test coverage

`tests/unit/governance/test_public_api.py` must test:

1. All symbols in `__all__` are importable
2. No symbol in `__all__` starts with `_`
3. `isinstance(InMemoryOrgStore(), OrgStore)` is True (protocol check)
4. `isinstance(SQLiteGovernanceStore(":memory:"), OrgStore)` is True
5. `from pact.governance import Address, CompiledOrg` works (spot-check a few)
6. The `governance` attribute exists on the `pact` module after `import pact`
