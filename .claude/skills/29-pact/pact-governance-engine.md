---
name: pact-governance-engine
description: "Complete GovernanceEngine API reference -- decision, query, mutation, and audit methods"
---

# GovernanceEngine API Reference

`GovernanceEngine` is the single entry point for all PACT governance decisions. All public methods are thread-safe (acquire `self._lock`). All error paths are fail-closed (return BLOCKED, not exceptions).

## Constructor

```python
from pact.governance.engine import GovernanceEngine

engine = GovernanceEngine(
    org,                        # OrgDefinition | CompiledOrg
    envelope_store=None,        # EnvelopeStore (default: MemoryEnvelopeStore)
    clearance_store=None,       # ClearanceStore (default: MemoryClearanceStore)
    access_policy_store=None,   # AccessPolicyStore (default: MemoryAccessPolicyStore)
    org_store=None,             # OrgStore (default: MemoryOrgStore)
    audit_chain=None,           # AuditChain (optional, for audit trail)
    store_backend="memory",     # "memory" or "sqlite"
    store_url=None,             # Path for sqlite backend
)
```

When `store_backend="sqlite"` and `store_url` is set, all stores are automatically created as SQLite-backed stores. All explicit `*_store` args must be `None`.

## Decision API

### verify_action()

The primary decision method. Combines envelope evaluation, multi-level verification, and access checks.

```python
verdict = engine.verify_action(
    role_address="D1-R1-T1-R1",
    action="deploy",
    context={
        "cost": 500.0,                   # Financial check
        "task_id": "task-123",           # Task envelope narrowing
        "resource": knowledge_item,       # Knowledge access check
        "posture": TrustPostureLevel.SUPERVISED,
    },
)

# GovernanceVerdict fields
verdict.level           # "auto_approved" | "flagged" | "held" | "blocked"
verdict.allowed         # True for auto_approved/flagged
verdict.reason          # Human-readable explanation
verdict.role_address    # Echo back
verdict.action          # Echo back
verdict.envelope_version  # SHA-256 for TOCTOU detection
verdict.access_decision # AccessDecision | None
verdict.to_dict()       # JSON-serializable dict
```

**Logic flow:**

1. Compute effective envelope (with version hash for TOCTOU defense)
2. Evaluate action against envelope dimensions (operational, financial)
3. Multi-level verify: walk accountability chain, most restrictive wins
4. If `context["resource"]` is a `KnowledgeItem`, run `check_access()`
5. Combine verdicts (most restrictive wins)
6. Emit audit anchor

### compute_envelope()

```python
effective = engine.compute_envelope(
    role_address="D1-R1-T1-R1",
    task_id="task-123",  # optional
)
# Returns ConstraintEnvelopeConfig | None
```

### check_access()

5-step access enforcement for knowledge items.

```python
from pact.governance.knowledge import KnowledgeItem
from pact.governance.config import ConfidentialityLevel, TrustPostureLevel

item = KnowledgeItem(
    item_id="doc-secret",
    classification=ConfidentialityLevel.SECRET,
    owning_unit_address="D1-R1-D2",
    compartments=frozenset({"project-x"}),
)

decision = engine.check_access(
    role_address="D1-R1-D2-R1-T1-R1",
    knowledge_item=item,
    posture=TrustPostureLevel.CONTINUOUS_INSIGHT,
)
decision.allowed      # bool
decision.reason       # str
decision.step_failed  # 1-5 or None if allowed
```

## Query API

```python
engine.org_name                         # str -- human-readable org name
engine.get_org()                        # CompiledOrg
engine.get_node("D1-R1-T1-R1")         # OrgNode | None
```

### get_context()

Creates a **frozen** `GovernanceContext` snapshot for agent consumption. This is the anti-self-modification defense.

```python
ctx = engine.get_context(
    role_address="D1-R1-T1-R1",
    posture=TrustPostureLevel.SUPERVISED,
)
# GovernanceContext (frozen=True)
ctx.role_address              # str
ctx.posture                   # TrustPostureLevel
ctx.effective_envelope        # ConstraintEnvelopeConfig | None
ctx.clearance                 # RoleClearance | None
ctx.effective_clearance_level # ConfidentialityLevel | None
ctx.allowed_actions           # frozenset[str]
ctx.compartments              # frozenset[str]
ctx.org_id                    # str
```

## State Mutation API

All mutations are thread-safe and emit EATP audit anchors.

### Envelopes

```python
from pact.governance.envelopes import RoleEnvelope, TaskEnvelope

engine.set_role_envelope(RoleEnvelope(
    id="env-1",
    defining_role_address="D1-R1",       # supervisor
    target_role_address="D1-R1-T1-R1",   # direct report
    envelope=constraint_config,
))

engine.set_task_envelope(TaskEnvelope(
    id="task-env-1",
    task_id="task-123",
    parent_envelope_id="env-1",
    envelope=narrowed_config,
    expires_at=datetime(2026, 12, 31, tzinfo=UTC),
))
```

### Clearance

```python
from pact.governance.clearance import RoleClearance, VettingStatus

engine.grant_clearance(
    role_address="D1-R1-T1-R1",
    clearance=RoleClearance(
        role_address="D1-R1-T1-R1",
        max_clearance=ConfidentialityLevel.SECRET,
        compartments=frozenset({"project-x", "hr-data"}),
        vetting_status=VettingStatus.ACTIVE,
    ),
)

engine.revoke_clearance(role_address="D1-R1-T1-R1")
```

### Access Policies

```python
from pact.governance.access import KnowledgeSharePolicy, PactBridge

engine.create_ksp(KnowledgeSharePolicy(
    id="ksp-1",
    source_unit_address="D1-R1-D2",
    target_unit_address="D1-R1-D3",
    max_classification=ConfidentialityLevel.CONFIDENTIAL,
    created_by_role_address="D1-R1",
))

engine.create_bridge(PactBridge(
    id="bridge-1",
    role_a_address="D1-R1-D2-R1",
    role_b_address="D1-R1-D3-R1",
    bridge_type="standing",
    max_classification=ConfidentialityLevel.SECRET,
    bilateral=True,
))
```

## Audit API

```python
engine.audit_chain  # AuditChain | None

# Verify tamper-evident chain integrity (SQLite backend only)
is_valid, error_msg = engine.verify_audit_integrity()
```

## Single-Path Architecture (v0.3.0)

### GovernanceEngine Is THE One Decision Path

All governance decisions in pact_platform MUST route through `GovernanceEngine.verify_action()`. There is no parallel evaluation pipeline, no local constraint evaluation, no fallback to legacy modules.

```python
# THE decision path — no exceptions
verdict = engine.verify_action(
    role_address=role_address,
    action=action_name,
    context={
        "cost": action_cost,
        "cumulative_spend": agent_total_spend,  # injected by runtime
        "daily_calls": agent_daily_calls,        # injected by runtime
        **action_context,
    },
)
if not verdict.allowed:
    return BLOCKED
```

### L1/L3 Boundary

| Layer  | Package         | Owns                                                                                |
| ------ | --------------- | ----------------------------------------------------------------------------------- |
| **L1** | `kailash-pact`  | Governance DECISIONS — verify_action(), envelope evaluation, access checks          |
| **L3** | `pact_platform` | Operational INFRASTRUCTURE — halt, budget tracking, rate limiting, bridge envelopes |

L3 injects operational context into L1 decisions but NEVER evaluates governance rules locally.

### Cumulative Budget and Rate Limit Injection

L3 tracks per-agent spend and action counts, then injects them into every `verify_action()` call so L1 can apply financial and operational envelope limits correctly.

```python
# L3: track cumulative spend per agent
self._agent_spend[role_address] += action_cost

# L3: inject into L1 decision
verdict = engine.verify_action(
    role_address=role_address,
    action=action_name,
    context={
        "cost": action_cost,                                   # this action's cost
        "cumulative_spend": self._agent_spend[role_address],  # total so far
        "daily_calls": self._get_call_count(role_address),    # rate limit check
    },
)
```

### Rate Limiting — Rolling 24h Window

L3 enforces a rolling 24h window for per-agent action counts. The timestamp list is pruned on both read and write to prevent memory growth.

```python
_MAX_RATE = 1000  # actions per 24h per agent

def _get_call_count(self, role_address: str) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=24)
    with self._lock:
        timestamps = self._call_log.get(role_address, [])
        # Prune on read
        active = [t for t in timestamps if t > cutoff]
        self._call_log[role_address] = active
        return len(active)

def _record_call(self, role_address: str) -> None:
    with self._lock:
        self._call_log.setdefault(role_address, []).append(datetime.utcnow())
        # Prune on write — bounded to 24h window
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self._call_log[role_address] = [
            t for t in self._call_log[role_address] if t > cutoff
        ]
```

### Constraint Pipeline Retirement

In v0.3.0, the following legacy modules were retired from `pact_platform/trust/constraint/`:

- `gradient.py` — verification gradient logic (moved to L1 GovernanceEngine)
- `envelope.py` — constraint envelope evaluation (moved to L1)
- `middleware.py` — enforcement middleware (replaced by HookEnforcer/ShadowEnforcer using verify_action)

The ONLY remaining `constraint/` module at L3 is `bridge_envelopes.py` — this handles the operational bridge topology lookup that L3 owns, NOT governance decisions.

### Mock Governance Engines (Examples/Seeding Only)

For examples and database seeding, mock engines use fnmatch pattern rules. They MUST be function-scoped or underscore-prefixed and MUST NOT be exposed as public API.

```python
# OK for examples/seeding — function-scoped, never exported
def _make_mock_engine() -> GovernanceEngine:
    """Create a permissive mock engine for seeding. Never use in production."""
    ...

# Pattern-based mock rules (fnmatch)
_MOCK_RULES = {
    "read*": "auto_approved",
    "write*": "flagged",
    "*": "blocked",
}
```

## Cross-References

- `pact-envelopes.md` -- envelope model and intersection algorithm
- `pact-access-enforcement.md` -- 5-step access algorithm
- `pact-dtr-addressing.md` -- D/T/R grammar
- `pact-governed-agents.md` -- HookEnforcer/ShadowEnforcer migration patterns
- Source: `pact/governance/engine.py`
- Source: `pact/governance/verdict.py`
