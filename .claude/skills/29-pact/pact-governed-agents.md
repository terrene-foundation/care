---
name: pact-governed-agents
description: "PactGovernedAgent, @governed_tool decorator, middleware, and anti-self-modification defense"
---

# PACT Governed Agents

PACT wraps agent execution with governance enforcement. Agents receive a frozen `GovernanceContext` (read-only), NOT the `GovernanceEngine`. Tool access is DEFAULT-DENY.

## PactGovernedAgent

```python
from pact.governance.agent import PactGovernedAgent, GovernanceBlockedError, GovernanceHeldError
from pact.governance.config import TrustPostureLevel

agent = PactGovernedAgent(
    engine=engine,
    role_address="D1-R1-T1-R1",
    posture=TrustPostureLevel.SUPERVISED,
)

# Agent gets a frozen context -- cannot modify constraints
ctx = agent.context                        # GovernanceContext (frozen=True)
ctx.allowed_actions                        # frozenset({"read", "write"})
ctx.posture                                # TrustPostureLevel.SUPERVISED
ctx.effective_clearance_level              # ConfidentialityLevel.RESTRICTED
# ctx.posture = TrustPostureLevel.DELEGATED  -> FrozenInstanceError
```

### Tool Registration (Default-Deny)

Tools must be explicitly registered. Unregistered tools are blocked.

```python
# Register tools with governance metadata
agent.register_tool("read", cost=0.0)
agent.register_tool("write", cost=10.0)
agent.register_tool("analyze", cost=25.0, resource="reports")
```

### Tool Execution

Governance verification happens BEFORE the tool function runs. If blocked or held, the tool function is NEVER called.

```python
def read_data():
    return {"data": [1, 2, 3]}

# Execute through governance
result = agent.execute_tool("read", _tool_fn=read_data)
# Governance checks: registered? -> envelope ok? -> financial ok? -> execute

# Unregistered tool -> GovernanceBlockedError
try:
    agent.execute_tool("deploy", _tool_fn=lambda: None)
except GovernanceBlockedError as e:
    print(e.verdict.reason)  # "Tool 'deploy' is not governance-registered"

# Over financial limit -> GovernanceBlockedError or GovernanceHeldError
try:
    agent.execute_tool("write", _tool_fn=lambda: None)
except GovernanceHeldError as e:
    print(e.verdict.reason)  # "... exceeds approval threshold ... held for human approval"
```

### Verdict Flow

| Verdict Level   | Agent Behavior                                   |
| --------------- | ------------------------------------------------ |
| `auto_approved` | Tool executes silently                           |
| `flagged`       | Warning logged, tool executes                    |
| `held`          | `GovernanceHeldError` raised, tool NOT called    |
| `blocked`       | `GovernanceBlockedError` raised, tool NOT called |

## GovernanceContext (Frozen)

The anti-self-modification defense: agents get an immutable snapshot of their governance state.

```python
from pact.governance.context import GovernanceContext

# Created by engine.get_context() -- NOT by agents
ctx = engine.get_context(
    role_address="D1-R1-T1-R1",
    posture=TrustPostureLevel.SUPERVISED,
)

# Read-only fields
ctx.role_address              # "D1-R1-T1-R1"
ctx.posture                   # TrustPostureLevel.SUPERVISED
ctx.effective_envelope        # ConstraintEnvelopeConfig | None
ctx.clearance                 # RoleClearance | None
ctx.effective_clearance_level # ConfidentialityLevel | None
ctx.allowed_actions           # frozenset({"read", "write"})
ctx.compartments              # frozenset({"project-x"})
ctx.org_id                    # "acme-corp"
ctx.created_at                # datetime

# Serialization
d = ctx.to_dict()
ctx2 = GovernanceContext.from_dict(d)
```

## @governed_tool Decorator

Marks functions with governance metadata for auto-registration.

```python
from pact.governance.decorators import governed_tool

@governed_tool("write_report", cost=50.0)
def write_report(content: str) -> str:
    return f"Report: {content}"

@governed_tool("read_data", cost=0.0, resource="customer-db")
def read_data(query: str) -> list:
    return [{"id": 1}]

# Metadata is attached to the function
write_report._governed           # True
write_report._governance_action  # "write_report"
write_report._governance_cost    # 50.0

# The function remains directly callable
result = write_report("Q4 Summary")

# For governance enforcement, use PactGovernedAgent.execute_tool()
agent.register_tool("write_report", cost=50.0)
agent.execute_tool("write_report", _tool_fn=lambda: write_report("Q4 Summary"))
```

## PactGovernanceMiddleware

Low-level building block that returns verdicts (does NOT raise exceptions). Use this for integration with custom agent frameworks.

```python
from pact.governance.middleware import PactGovernanceMiddleware

middleware = PactGovernanceMiddleware(
    engine=engine,
    role_address="D1-R1-T1-R1",
)

# Returns GovernanceVerdict -- caller decides how to handle
verdict = middleware.pre_execute(
    action_name="deploy",
    context={"cost": 500.0},
)

if verdict.level == "blocked":
    # Framework-specific blocking logic
    raise RuntimeError(verdict.reason)
elif verdict.level == "held":
    # Queue for human approval
    approval_queue.submit(verdict)
elif verdict.level == "flagged":
    logger.warning("Flagged: %s", verdict.reason)
# auto_approved -> proceed
```

### PactGovernedAgent vs PactGovernanceMiddleware

| Feature           | PactGovernedAgent                      | PactGovernanceMiddleware |
| ----------------- | -------------------------------------- | ------------------------ |
| Raises exceptions | Yes (GovernanceBlockedError/HeldError) | No (returns verdict)     |
| Tool registration | Built-in default-deny                  | Caller manages           |
| Frozen context    | Exposed via `.context`                 | Not exposed              |
| Use case          | Direct agent wrapping                  | Framework integration    |

## HookEnforcer and ShadowEnforcer (v0.3.0)

These are the two pact_platform (L3) consumers of GovernanceEngine that replaced the retired legacy constraint pipeline.

### HookEnforcer

Hooks into agent execution at the point of action — called BEFORE an action runs. Blocks if governance is missing or verdict is non-permissive. Fail-closed on every error path.

```python
class HookEnforcer:
    def __init__(
        self,
        governance_engine: GovernanceEngine,
        role_address: str,
    ) -> None:
        if governance_engine is None:
            raise ValueError("governance_engine is required")
        if not role_address:
            raise ValueError("role_address is required")
        self._engine = governance_engine
        self._role_address = role_address
        self._lock = threading.Lock()
        self._results: deque = deque(maxlen=10_000)  # bounded

    def enforce(self, action: str, context: dict) -> GovernanceVerdict:
        try:
            verdict = self._engine.verify_action(
                role_address=self._role_address,
                action=action,
                context=context,
            )
        except Exception:
            logger.exception("HookEnforcer.enforce failed — fail closed")
            return GovernanceVerdict(level="blocked", reason="enforcer error — fail closed")
        self._record_result(verdict)
        return verdict

    def _record_result(self, verdict: GovernanceVerdict) -> None:
        with self._lock:
            self._results.append(verdict)  # deque(maxlen=10_000) — no trimming needed
```

**Key invariants**:

- Missing `governance_engine` → raise at construction (not at enforce time)
- Missing `role_address` → raise at construction
- Engine exception during verify_action → return BLOCKED (never re-raise)
- Results bounded by `deque(maxlen=10_000)`

### ShadowEnforcer

Runs governance checks in "shadow mode" — checks what WOULD be blocked without actually blocking. Used for monitoring, testing, and gradual migration validation. Also fail-closed but records shadow verdicts separately.

```python
class ShadowEnforcer:
    def __init__(
        self,
        governance_engine: GovernanceEngine,
        role_address: str,
    ) -> None:
        if governance_engine is None:
            raise ValueError("governance_engine is required")
        self._engine = governance_engine
        self._role_address = role_address
        self._lock = threading.Lock()
        self._shadow_results: deque = deque(maxlen=10_000)

    def shadow_check(self, action: str, context: dict) -> GovernanceVerdict:
        """Run governance check without enforcing — for observability."""
        try:
            verdict = self._engine.verify_action(
                role_address=self._role_address,
                action=action,
                context=context,
            )
        except Exception:
            logger.exception("ShadowEnforcer.shadow_check failed")
            verdict = GovernanceVerdict(level="blocked", reason="shadow enforcer error")
        with self._lock:
            self._shadow_results.append(verdict)
        return verdict  # Caller decides whether to enforce
```

### Constructor API (Both Enforcers)

Both enforcers take `governance_engine` + `role_address` as required constructor arguments. There is no "lazy initialization" or "set engine later" pattern — failing at construction is safer than failing silently at enforce time.

```python
# DO: inject at construction
enforcer = HookEnforcer(governance_engine=engine, role_address="D1-R1-T1-R1")

# DO NOT: set after construction
enforcer = HookEnforcer()
enforcer.engine = engine  # No such pattern — raises AttributeError
```

### Thread Safety and Bounded Collections

Both enforcers use:

- `threading.Lock` for all shared state (`_results`, `_shadow_results`, `_metrics`)
- `deque(maxlen=N)` for result lists — bounded automatically, no manual trimming needed
- Metrics dicts (agent spend, call counts) bounded to `MAX_AGENTS = 10_000` entries; when full, evict oldest

```python
MAX_AGENTS = 10_000

def _record_spend(self, role_address: str, amount: float) -> None:
    with self._lock:
        if len(self._agent_spend) >= MAX_AGENTS and role_address not in self._agent_spend:
            # Evict oldest entry
            oldest = next(iter(self._agent_spend))
            del self._agent_spend[oldest]
        self._agent_spend[role_address] = self._agent_spend.get(role_address, 0.0) + amount
```

## Emergency Halt (ExecutionRuntime)

`ExecutionRuntime` has an emergency halt mechanism that gates ALL task processing. The halt check runs FIRST in `process_next()`, before any governance check.

```python
class ExecutionRuntime:
    def __init__(self, governance_engine: GovernanceEngine, ...) -> None:
        self._halted = False
        self._lock = threading.Lock()

    def halt(self) -> None:
        with self._lock:
            self._halted = True

    def resume(self) -> None:
        with self._lock:
            self._halted = False

    def is_halted(self) -> bool:
        with self._lock:
            return self._halted

    def process_next(self, task: Task) -> TaskResult:
        # FIRST check — before any governance evaluation
        if self.is_halted():
            return TaskResult(blocked=True, reason="runtime halted")
        # Then governance check
        verdict = self._hook_enforcer.enforce(task.action, task.context)
        if not verdict.allowed:
            return TaskResult(blocked=True, reason=verdict.reason)
        # Then execute
        return self._execute(task)
```

**Why halt first**: Emergency halt is a safety override. It must preempt governance checks, not be gated by them. A halted runtime stops ALL work regardless of what governance would permit.

## Cross-References

- `pact-governance-engine.md` -- engine.get_context(), engine.verify_action(), single-path architecture
- `pact-envelopes.md` -- effective envelope in context
- `pact-kaizen-integration.md` -- wrapping Kaizen agents
- Source: `pact/governance/agent.py`
- Source: `pact/governance/decorators.py`
- Source: `pact/governance/middleware.py`
- Source: `pact/governance/context.py`
- Source: `pact_platform/engine/hook_enforcer.py`
- Source: `pact_platform/engine/shadow_enforcer.py`
- Source: `pact_platform/engine/execution_runtime.py`
