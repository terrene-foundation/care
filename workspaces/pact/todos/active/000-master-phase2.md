# PACT Framework — Master Todo List (Phase 2: v0.2.0)

**Supersedes**: `000-master-pact-framework.md` (which was scope-bloated, had security bolted on at the end, and used wrong package name)

**Package**: `kailash-pact` (NOT `pact` — conflicts with pact-python, 1,800 stars, 2.2M+ downloads)

**Architecture**: Option B — build all primitives + integration adapters HERE, perfect them, then migrate to `kailash-py/packages/kailash-pact/`. This repo becomes the reference platform (dashboard, examples, deployment).

**Starting state**: M0-M6 complete. `src/pact/governance/` has 9 modules (~2,800 LOC), 488 governance tests, 4,036 total tests passing. University example with 14 E2E scenarios. Trust layer, build layer, use layer, and Next.js dashboard exist.

**End state**: `pip install kailash-pact` gives verticals (Astra, Arbor) a complete governance framework with single-call `GovernanceEngine`, governed agent runtime, comprehensive documentation, and security baked into every layer.

**Real consumers**: Astra (`~/repos/terrene/astra` — MAS financial services) and Arbor (`~/repos/terrene/arbor` — Singapore HRIS) are waiting to import `kailash_pact`. They need: positional addressing, information barriers, 3-layer envelopes, knowledge clearance, governance persistence, EATP audit integration.

---

## Critical Path and Dependency Graph

```
M7 (Infrastructure + Security Fixes)
 |
 v
M8 (GovernanceEngine Facade) ----+-----> M13 (Frontend Dashboard)
 |                                |
 +---> M9 (Envelope Unification)  +-----> M12 (Nexus API + Governance Endpoints)
 |      |                         |
 |      v                         +-----> M11 (DataFlow Persistence)
 |     M10 (PactGovernedAgent)    |
 |      |                         |
 +------+-------------------------+-----> M14 (Documentation + Examples)
 |
 v
M15 (Red Team + Hardening) --- tests ALREADY-HARDENED code
 |
 v
M16 (Ship Readiness)
```

**Parallel opportunities after M8**:

- M9, M10, M11, M12, M13, M14 can all start after M8
- M9 and M10 have a dependency (PactGovernedAgent uses envelopes)
- M12 benefits from M11 (API endpoints query persistent stores) but can use in-memory stores
- M13 depends on M12 (frontend needs API endpoints)
- M14 can start early (quickstart, guides)

**Serial constraint**: M7 -> M8 -> M15 -> M16 is the spine. Everything else hangs off M8.

---

## Milestone 7: COC Infrastructure + Critical Security Fixes (7001-7009)

COC hooks are broken, governance rules are missing, and 5 CRITICAL security vulnerabilities exist in the already-shipped governance layer. Fix the foundation before building on it.

---

### 7001 — Fix Ghost Hook: validate-hierarchy-grammar.js

- **What**: `.claude/settings.json` references `scripts/hooks/validate-hierarchy-grammar.js` which does not exist. This fires on every file change and silently fails. Either create the hook (validates D/T/R grammar in changed governance files) or remove the reference. Decision: create it -- grammar validation on every change catches tightening violations early.
- **Where**: `scripts/hooks/validate-hierarchy-grammar.js`, `.claude/settings.json`
- **Evidence**: `node scripts/hooks/validate-hierarchy-grammar.js` exits 0 on valid files, exits 2 on grammar violations. No more "file not found" errors in hook output.
- **Dependencies**: None
- **Complexity**: M

### 7002 — Fix session-start.js Governance Detection

- **What**: `session-start.js` always detects "core-sdk" because it does not check for `src/pact/governance/` files. Add governance detection: if `src/pact/governance/engine.py` exists, report "governance framework" context. Inject relevant rules (`rules/governance.md`, `rules/boundary-test.md`).
- **Where**: `scripts/hooks/session-start.js`
- **Evidence**: Running `node scripts/hooks/session-start.js` in this repo detects "governance framework" (not "core-sdk"). Injects governance context into session.
- **Dependencies**: 7003 (rules/governance.md must exist)
- **Complexity**: S

### 7003 — Create rules/governance.md

- **What**: Governance development conventions: GovernanceEngine is the single entry point, all governance state access goes through engine methods, all mutations emit audit anchors, frozen dataclasses for immutable governance state, thread-safe stores, fail-closed on all error paths, NaN/Inf guards on all numeric fields, boundary test compliance.
- **Where**: `.claude/rules/governance.md`
- **Evidence**: File exists with MUST/MUST NOT rules. Agents reference it during governance work. `validate-workflow.js` checks compliance.
- **Dependencies**: None
- **Complexity**: S

### 7004 — Create integration-decisions.md for Anti-Amnesia

- **What**: Document all governance-era architectural decisions that are NOT in the old `decisions.yml` (which has zero entries from governance milestones M1-M6). Key decisions: Option B architecture, D/T/R grammar invariant, 5-step access algorithm design, frozen dataclass pattern, bounded stores, university example as canonical reference, three-layer envelope model.
- **Where**: `workspaces/pact/decisions.yml` (append new entries), `workspaces/pact/briefs/integration-decisions.md`
- **Evidence**: `decisions.yml` has entries for governance-era decisions. Future sessions can query decisions and find governance context.
- **Dependencies**: None
- **Complexity**: S

### 7005 — CRITICAL: NaN/Inf Bypass in intersect_envelopes()

- **What**: `_min_optional()` in `envelopes.py` calls `min(a, b)` without NaN/Inf guards. `min(NaN, 5.0)` returns `NaN` on most platforms, poisoning the accumulator. All subsequent envelope checks pass because `NaN < X` is always `False`. Fix: add `math.isfinite()` guards in `_min_optional()`, `_min_optional_int()`, and all `FinancialConstraintConfig` / `OperationalConstraintConfig` / `ConstraintEnvelopeConfig` numeric fields at construction time (`__post_init__` for dataclasses, `model_validator` for Pydantic). Also guard `RoleEnvelope.validate_tightening()` comparisons.
- **Where**: `src/pact/governance/envelopes.py`, `src/pact/build/config/schema.py`
- **Evidence**: `intersect_envelopes(envelope_with_nan, normal_envelope)` raises `ValueError("non-finite value")`. `FinancialConstraintConfig(max_spend_usd=float('nan'))` raises `ValueError`. `RoleEnvelope.validate_tightening()` with NaN inputs raises `ValueError`. Regression tests in `tests/unit/governance/test_security.py`.
- **Dependencies**: None
- **Complexity**: M

### 7006 — CRITICAL: Freeze RoleDefinition

- **What**: `RoleDefinition` is `@dataclass` (mutable). An agent with a reference to its own `RoleDefinition` can modify `is_external`, `reports_to_role_id`, or `agent_id` at runtime, bypassing compilation-time validation. Fix: change to `@dataclass(frozen=True)`. Use `object.__setattr__` during compilation for the `address` field (same pattern as `OrgNode`). Update all code that mutates `RoleDefinition` after construction.
- **Where**: `src/pact/governance/compilation.py`, `src/pact/governance/store.py`, `tests/unit/governance/test_compilation.py`
- **Evidence**: `role.is_external = True` raises `FrozenInstanceError`. All existing tests pass. New regression test verifies immutability.
- **Dependencies**: None
- **Complexity**: M

### 7007 — CRITICAL: Protect CompiledOrg.nodes with MappingProxyType

- **What**: `CompiledOrg` is `frozen=True` but `nodes: dict` is mutable. Post-compilation code can `compiled_org.nodes["evil"] = malicious_node`. Fix: after compilation, wrap the dict in `types.MappingProxyType`. Use `object.__setattr__` to replace the mutable dict with the proxy at the end of `compile_org()`. The proxy makes the dict read-only. Internal compilation helpers use `object.__setattr__` on the CompiledOrg during the build phase.
- **Where**: `src/pact/governance/compilation.py`
- **Evidence**: `compiled_org.nodes["evil"] = OrgNode(...)` raises `TypeError`. All existing tests pass. `compiled_org.get_node("D1-R1")` still works (MappingProxyType supports read operations).
- **Dependencies**: None
- **Complexity**: M

### 7008 — CRITICAL: Depth/Breadth Limits on compile_org()

- **What**: `compile_org()` has no recursion limit. A malicious `OrgDefinition` with 1000-deep nesting or 10,000 children per node causes stack overflow or OOM. Fix: add `MAX_COMPILATION_DEPTH = 50` and `MAX_CHILDREN_PER_NODE = 500` constants. `_assign_children_addresses()` tracks depth and raises `CompilationError` when exceeded. Add `MAX_TOTAL_NODES = 100_000` check.
- **Where**: `src/pact/governance/compilation.py`
- **Evidence**: `compile_org(deeply_nested_org)` with depth 51 raises `CompilationError("max compilation depth 50 exceeded")`. `compile_org(wide_org)` with 501 children raises `CompilationError`. All existing tests pass (university org is well within limits).
- **Dependencies**: None
- **Complexity**: S

### 7009 — CRITICAL: Thread Safety for In-Memory Governance Stores

- **What**: `MemoryOrgStore`, `MemoryEnvelopeStore`, `MemoryClearanceStore`, `MemoryAccessPolicyStore` use `OrderedDict` without synchronization. Concurrent reads and writes can corrupt state. Fix: add `threading.Lock` to each store class. Acquire lock in every public method. Follow the same pattern used in the trust-plane stores (11 components already have locks from RT7-RT9).
- **Where**: `src/pact/governance/store.py`
- **Evidence**: Concurrent test: 100 threads writing to `MemoryOrgStore` simultaneously does not corrupt state or raise `RuntimeError`. All public methods acquire lock before accessing internal state.
- **Dependencies**: None
- **Complexity**: M

---

## Milestone 8: GovernanceEngine Facade (7010-7018)

The single most important deliverable. Today, consumers must manually wire 6+ components. After M8, one call does it all. Security baked in from day 1: thread-safe, NaN-guarded, fail-closed, audit-emitting.

---

### 7010 — GovernanceEngine Core Class

- **What**: Create `GovernanceEngine` that composes `CompiledOrg`, `EnvelopeStore`, `ClearanceStore`, `AccessPolicyStore`, and `AuditChain` behind a single thread-safe facade. Constructor accepts `OrgDefinition` (or `CompiledOrg`), optional store implementations (defaulting to in-memory), and optional `AuditChain`. All public methods acquire `threading.Lock`. Provides: `engine.check_access(role_address, knowledge_item, posture)`, `engine.compute_envelope(role_address, task_id=None)`, `engine.get_org()`, `engine.get_node(address)`.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `from pact.governance import GovernanceEngine; engine = GovernanceEngine(org); decision = engine.check_access(...)` works in 3 lines. Thread-safe: 100 concurrent `check_access` calls return consistent results.
- **Dependencies**: 7005-7009 (security fixes must be in place)
- **Complexity**: L

### 7011 — GovernanceEngine.from_yaml() Factory

- **What**: Factory method that loads an `OrgDefinition` from a YAML config file, compiles it, and returns a ready-to-use `GovernanceEngine`. Unified YAML format that includes departments, teams, roles, envelopes, clearances, KSPs, and bridges in a single file. Verticals call `GovernanceEngine.from_yaml("org.yaml")` to bootstrap. Validate YAML against a JSON Schema for early error detection.
- **Where**: `src/pact/governance/engine.py`, `src/pact/governance/yaml_loader.py`
- **Evidence**: `engine = GovernanceEngine.from_yaml("examples/university/org.yaml")` returns a functional engine with all roles, envelopes, and clearances populated. Invalid YAML raises `ConfigurationError` with human-readable message.
- **Dependencies**: 7010
- **Complexity**: L

### 7012 — GovernanceEngine.verify_action() — The Primary Decision API

- **What**: Implement `verify_action(role_address, action, context)` that combines envelope computation, gradient classification, and access checking into a single `GovernanceVerdict`. Returns `AUTO_APPROVED`, `FLAGGED`, `HELD`, or `BLOCKED` with structured reason, envelope snapshot, and audit details. Context dict supports `cost`, `resource`, `channel`, and domain-specific keys. Every call emits an EATP audit anchor. Fail-closed: any internal error returns `BLOCKED` with error details.
- **Where**: `src/pact/governance/engine.py`, `src/pact/governance/verdict.py`
- **Evidence**: `verdict = engine.verify_action("D1-R1-T1-R1", "write_report", {"cost": 50.0})` returns `GovernanceVerdict(level=AUTO_APPROVED, reason="...", envelope_snapshot={...})`. Test: action exceeding max_spend returns `BLOCKED`. Test: internal error returns `BLOCKED` (not exception).
- **Dependencies**: 7010
- **Complexity**: L

### 7013 — Convenience API: engine.can(), engine.explain(), engine.describe()

- **What**: Developer experience methods that make PACT usable without deep governance knowledge. (1) `engine.can(role_address_or_agent_id, action, resource=None)` returns `bool` (simple yes/no). (2) `engine.explain_envelope(role_address)` returns human-readable breakdown of effective envelope with each dimension explained. (3) `engine.explain_access(role_address, item)` returns step-by-step trace of the 5-step algorithm. (4) `engine.describe_address(address)` returns human-readable string like "CS Chair (Team: CS Department, Dept: School of Engineering)".
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine.can("D1-R1-D1-R1-T1-R1", "write_report")` returns `True`. `engine.describe_address("D1-R1-D1-R1-D1-R1-T1-R1")` returns `"CS Chair (CS Department > School of Engineering > Academic Affairs)"`. `engine.explain_envelope("D1-R1")` returns multiline string describing each constraint dimension.
- **Dependencies**: 7010, 7012
- **Complexity**: M

### 7014 — GovernanceEngine Audit Integration

- **What**: Wire `GovernanceEngine` to emit EATP Audit Anchors for every governance decision (access grant/deny, envelope computation, clearance change, bridge creation). Uses the `PactAuditAction` types from `governance/audit.py`. Optional `AuditChain` passed at construction time. When present, all mutations and decisions generate audit records. Include effective envelope snapshot in audit details per thesis requirement.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: After `engine.check_access(...)`, `engine.audit_chain.get_all()` contains an anchor with `pact_action=barrier_enforced` and the effective envelope snapshot. After `engine.grant_clearance(...)`, audit contains `pact_action=clearance_granted`.
- **Dependencies**: 7010, 7012
- **Complexity**: M

### 7015 — GovernanceEngine State Management

- **What**: Methods for runtime state mutations: `engine.grant_clearance(role_address, clearance)`, `engine.revoke_clearance(role_address)`, `engine.create_bridge(bridge)`, `engine.create_ksp(ksp)`, `engine.set_role_envelope(envelope)`, `engine.set_task_envelope(envelope)`. All mutations are thread-safe (lock acquisition). All mutations emit audit anchors. All mutations validate inputs (NaN/Inf, address format, classification levels). Expired KSPs/bridges are treated as non-existent (TOCTOU-safe reads).
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine.grant_clearance("D1-R1", clearance); decision = engine.check_access(...)` uses the newly granted clearance. Audit chain records `clearance_granted`. Concurrent mutations do not corrupt state.
- **Dependencies**: 7010, 7014
- **Complexity**: M

### 7016 — Frozen GovernanceContext for Agent Consumption

- **What**: Create `GovernanceContext` frozen dataclass that agents receive as their governance snapshot. Contains: `role_address`, `posture`, `effective_envelope` (snapshot, not live reference), `clearance`, `allowed_actions`, `compartments`. Agents CANNOT modify this — `frozen=True`. Engine produces a `GovernanceContext` via `engine.get_context(role_address)`. This is the anti-self-modification defense: agents get a read-only view.
- **Where**: `src/pact/governance/context.py`
- **Evidence**: `ctx = engine.get_context("D1-R1-T1-R1"); ctx.posture = "delegated"` raises `FrozenInstanceError`. `ctx.effective_envelope.financial.max_spend_usd` returns the current limit. Agent code receives `GovernanceContext`, not `GovernanceEngine`.
- **Dependencies**: 7010, 7012
- **Complexity**: M

### 7017 — Agent-to-Address Mapping

- **What**: Create `AgentRoleMapping` that maps agent IDs to D/T/R role addresses. Bridge between "agent X is running" and "agent X occupies role D1-R1-D2-R1-T1-R1". Populated from `OrgDefinition` (roles with `agent_id` field) or configured explicitly. Integrated into `GovernanceEngine` so `engine.can("agent-cs-chair", "write_report")` resolves the agent ID to its address first.
- **Where**: `src/pact/governance/agent_mapping.py`, `src/pact/governance/engine.py`
- **Evidence**: `mapping = AgentRoleMapping.from_org(compiled_org); addr = mapping.get_address("agent-cs-chair")` returns `"D1-R1-D1-R1-D1-R1-T1-R1"`. `engine.can("agent-cs-chair", "write_report")` works by agent ID (not just address).
- **Dependencies**: 7010
- **Complexity**: M

### 7018 — GovernanceEngine Unit + Integration Tests

- **What**: Comprehensive test suite: construction from OrgDefinition and YAML, access decisions, envelope computation, verify_action verdicts, convenience API, audit integration, state management, agent mapping, frozen context, error handling (missing org, invalid config, internal error -> BLOCKED), thread safety (concurrent access). Use university example as primary fixture.
- **Where**: `tests/unit/governance/test_engine.py`, `tests/unit/governance/test_yaml_loader.py`, `tests/unit/governance/test_context.py`, `tests/unit/governance/test_agent_mapping.py`
- **Evidence**: `pytest tests/unit/governance/test_engine.py` passes with >90% coverage of `engine.py`. All convenience methods tested. Thread safety test with 100 concurrent calls.
- **Dependencies**: 7010-7017
- **Complexity**: L

---

## Milestone 9: Envelope Unification (7020-7025)

Two parallel envelope systems exist: governance `compute_effective_envelope()` (correct PACT three-layer model) and trust-layer `ConstraintEnvelope` (legacy runtime evaluator). M9 makes governance canonical and trust-layer delegates to it. Adapter is fail-closed: no fallback to legacy on failure.

---

### 7020 — Adapter: Governance Envelope to Trust-Layer ConstraintEnvelope

- **What**: Create adapter that converts between governance `RoleEnvelope`/`TaskEnvelope` and trust-layer `ConstraintEnvelope`. Governance `compute_effective_envelope()` becomes CANONICAL. Adapter is fail-closed: if conversion fails, raise `EnvelopeAdapterError` (do NOT fall back to legacy behavior). Include NaN/Inf guards on all numeric fields during conversion.
- **Where**: `src/pact/governance/envelope_adapter.py`
- **Evidence**: `adapted = GovernanceEnvelopeAdapter(engine).to_constraint_envelope("D1-R1-T1-R1")` produces a `ConstraintEnvelope`. Round-trip test: governance -> trust-layer -> evaluate -> same result as governance direct. Adapter error raises `EnvelopeAdapterError`, not silent fallback.
- **Dependencies**: 7010
- **Complexity**: L

### 7021 — GradientEngine Governance Integration

- **What**: Modify `GradientEngine` to accept a `GovernanceEngine` and use governance envelope computation instead of standalone evaluation. When governance is available, `classify_action()` calls `engine.verify_action()`. When not available (backward compatibility), uses existing behavior. Deprecation warning when using legacy path.
- **Where**: `src/pact/trust/constraint/gradient.py`
- **Evidence**: `GradientEngine(governance_engine=engine).classify_action(...)` uses governance envelopes. `GradientEngine(config=old_config).classify_action(...)` still works with deprecation warning. Both paths produce consistent results for same constraints.
- **Dependencies**: 7020
- **Complexity**: L

### 7022 — ExecutionRuntime Governance Integration

- **What**: Update `ExecutionRuntime` to accept a `GovernanceEngine`. When provided, uses `engine.verify_action()` for all pre-execution checks. `AgentDefinition` receives `GovernanceContext` (frozen, not engine). This means agents cannot call `engine.set_role_envelope()` or any mutation method -- they only get the read-only context.
- **Where**: `src/pact/use/execution/runtime.py`
- **Evidence**: `runtime = ExecutionRuntime(registry=reg, governance_engine=engine)` routes all verification through governance. Agent receives `GovernanceContext`, not `GovernanceEngine` reference.
- **Dependencies**: 7021, 7016
- **Complexity**: L

### 7023 — Deprecation Markers on Standalone Trust-Layer Envelope Evaluation

- **What**: Add deprecation warnings to direct `ConstraintEnvelope.evaluate()` calls and standalone `GradientEngine` construction without governance. Log warnings pointing users to `GovernanceEngine`. Do NOT remove yet -- backward compatibility for consumers who have not migrated.
- **Where**: `src/pact/trust/constraint/envelope.py`, `src/pact/trust/constraint/gradient.py`
- **Evidence**: `ConstraintEnvelope.evaluate(action_context)` without governance produces `DeprecationWarning`. Tests capture and verify warning.
- **Dependencies**: 7020, 7021
- **Complexity**: S

### 7024 — Property-Based Testing for Monotonic Tightening

- **What**: Use Hypothesis to generate random envelope pairs and verify the monotonic tightening invariant holds: `intersect_envelopes(a, b)` is always at most as permissive as both `a` and `b` on every dimension. Also verify: `compute_effective_envelope()` with any chain of ancestors produces an envelope that is at most as permissive as any individual ancestor.
- **Where**: `tests/unit/governance/test_envelope_properties.py`
- **Evidence**: `pytest tests/unit/governance/test_envelope_properties.py` passes with Hypothesis generating 1000+ cases. No counterexample found.
- **Dependencies**: 7005 (NaN fix), 7020
- **Complexity**: M

### 7025 — Envelope Unification Tests

- **What**: Tests proving: (a) governance and trust-layer produce identical results; (b) three-layer model (Role + Task + Effective) propagated through adapter; (c) tightening violations caught identically in both paths; (d) adapter failure is fail-closed; (e) backward compatibility (old code without governance still works with deprecation warning).
- **Where**: `tests/unit/governance/test_envelope_unification.py`
- **Evidence**: Full test suite passes. Both paths exercised and asserted identical.
- **Dependencies**: 7020-7024
- **Complexity**: M

---

## Milestone 10: PactGovernedAgent + Kaizen Integration (7030-7037)

Bridge between "AI agent framework" (Kaizen) and "governed organization" (PACT). When an agent calls a tool, governance checks happen BEFORE execution. Default-deny: tools without explicit governance decoration are blocked.

---

### 7030 — PactGovernedAgent Base Class

- **What**: Create `PactGovernedAgent` that wraps any Kaizen agent with governance enforcement. Constructor takes `governance_engine`, `role_address`, `posture`. Before any tool use, calls `engine.verify_action()`. BLOCKED -> raise `GovernanceBlockedError`. HELD -> raise `GovernanceHeldError` (for approval queue). FLAGGED -> proceed with logged warning. AUTO_APPROVED -> proceed. Agent receives `GovernanceContext` (frozen), NOT the engine itself.
- **Where**: `src/pact/governance/agent.py`
- **Evidence**: `agent = PactGovernedAgent(engine=engine, role_address="D1-R1-T1-R1")`. BLOCKED action raises `GovernanceBlockedError`. Agent cannot call `engine.grant_clearance()` (only has context, not engine).
- **Dependencies**: 7012 (verify_action), 7016 (GovernanceContext)
- **Complexity**: L

### 7031 — Governance Middleware for Kaizen

- **What**: Kaizen middleware/hook that can be registered on any agent to enforce PACT governance without subclassing. `PactGovernanceMiddleware(engine, role_address)` registers as a pre-execution hook. Lighter-weight alternative to `PactGovernedAgent` -- works with any existing Kaizen agent.
- **Where**: `src/pact/governance/middleware.py`
- **Evidence**: `middleware = PactGovernanceMiddleware(engine, "D1-R1"); agent.add_middleware(middleware)`. Tool use triggers governance check.
- **Dependencies**: 7012
- **Complexity**: M

### 7032 — Default-Deny Tool Access

- **What**: By default, all tools are BLOCKED unless explicitly governed. `@governed_tool(action_name, cost=0.0)` decorator marks tools as governance-aware. Undecorated tools called by a governed agent raise `GovernanceBlockedError("tool 'X' is not governance-registered")`. This is the opposite of opt-in (which would default-allow) -- it is opt-out from blocking.
- **Where**: `src/pact/governance/decorators.py`
- **Evidence**: Undecorated tool raises `GovernanceBlockedError`. `@governed_tool("write_report")` tool passes through governance check. Test: agent with mix of decorated and undecorated tools -- only decorated ones can execute.
- **Dependencies**: 7030
- **Complexity**: M

### 7033 — Governed Tool Decorator

- **What**: `@governed_tool(action_name, cost=0.0)` wraps tool functions with governance checks. Reads governance context from the agent's session. Calls `engine.verify_action()` before execution. Supports `cost` (for financial envelope), `resource` (for data access), `channel` (for communication). Returns `GovernanceBlockedError` if blocked.
- **Where**: `src/pact/governance/decorators.py`
- **Evidence**: `@governed_tool("write_report", cost=50.0) def write_report(content): ...`. When called by governed agent, checks governance. Blocked tool raises. Approved tool executes.
- **Dependencies**: 7030, 7032
- **Complexity**: M

### 7034 — Approval Queue Integration

- **What**: Wire `GovernanceEngine` HELD verdicts to existing `ApprovalQueue`. When `verify_action()` returns HELD, action enters approval queue with governance context (role_address, action, envelope snapshot, reason). Approved actions resume. Rejected actions recorded in audit. Uses existing `pact.use.execution.approval` infrastructure.
- **Where**: `src/pact/governance/engine.py`, `src/pact/use/execution/approval.py`
- **Evidence**: Verdict HELD -> action in `approval_queue.get_pending()`. Approve -> execution resumes. Audit records hold and resolution.
- **Dependencies**: 7012, 7014
- **Complexity**: M

### 7035 — MockAgent for Testing Without LLM

- **What**: `MockGovernedAgent` that implements the governed agent interface but executes tools deterministically without an LLM. Accepts a script of tool calls and expected outcomes. Essential for verticals (Astra, Arbor) to test governance without LLM API keys.
- **Where**: `src/pact/governance/testing.py`
- **Evidence**: `mock = MockGovernedAgent(engine, "D1-R1", tools=[write_report], script=["write_report"]); results = mock.run()` executes the tool through governance without any LLM call.
- **Dependencies**: 7030
- **Complexity**: M

### 7036 — Agent Self-Modification Defense Validation

- **What**: Comprehensive test proving agents CANNOT modify their own governance: (a) agent receives `GovernanceContext` (frozen), not `GovernanceEngine`; (b) `GovernanceContext.posture` is immutable; (c) `GovernanceContext.effective_envelope` is immutable; (d) agent cannot access `engine.set_role_envelope()` or `engine.grant_clearance()` through any path; (e) `RoleDefinition` is frozen (from 7006). This is the definitive anti-self-modification test.
- **Where**: `tests/unit/governance/test_self_modification_defense.py`
- **Evidence**: Every mutation attempt raises `FrozenInstanceError` or `AttributeError`. No code path from agent to engine mutation methods.
- **Dependencies**: 7006, 7016, 7030
- **Complexity**: M

### 7037 — Kaizen Integration Tests

- **What**: Integration tests: (a) `PactGovernedAgent` blocks actions exceeding envelope; (b) middleware intercepts tool calls; (c) default-deny blocks undecorated tools; (d) HELD actions enter approval queue; (e) audit chain records all governance decisions; (f) `MockGovernedAgent` executes scripted scenarios; (g) backward compatibility -- agents without governance still work.
- **Where**: `tests/unit/governance/test_governed_agent.py`, `tests/unit/governance/test_middleware.py`, `tests/unit/governance/test_decorators.py`
- **Evidence**: Full test suite passes. University example with mock agents validates all paths.
- **Dependencies**: 7030-7036
- **Complexity**: L

---

## Milestone 11: DataFlow Persistence (7040-7046)

Replace in-memory governance stores with SQLite/PostgreSQL persistence. Full trust-plane security parity: parameterized queries, file permissions, atomic writes, ID validation, bounded collections, append-only audit.

---

### 7040 — SQLite Governance Store

- **What**: Implement `SqliteOrgStore`, `SqliteEnvelopeStore`, `SqliteClearanceStore`, `SqliteAccessPolicyStore`. Follow trust-plane SQLite store patterns: parameterized `?` queries, `atomic_write()` for record storage, `validate_id()` on all external IDs, `os.chmod(0o600)` on database file, bounded result sets (`LIMIT` on queries), `threading.Lock` for concurrent access.
- **Where**: `src/pact/governance/stores/sqlite.py`
- **Evidence**: Round-trip: `store.save_org(org); store.load_org(org_id)` returns identical org. `store.load_org("../../etc/passwd")` raises `ValueError`. Database file has `0o600` permissions. All store protocol methods implemented.
- **Dependencies**: 7010
- **Complexity**: XL

### 7041 — PostgreSQL Governance Store

- **What**: PostgreSQL versions of all four governance stores. Parameterized queries with `?` canonical placeholders (translated by dialect). Connection pooling safety (shared pool, not per-store). Follow infrastructure-sql rules: `dialect.upsert()`, `dialect.blob_type()`, no `AUTOINCREMENT`.
- **Where**: `src/pact/governance/stores/postgresql.py`
- **Evidence**: Tests pass with PostgreSQL fixture (or skip when unavailable). All protocol methods identical to SQLite behavior.
- **Dependencies**: 7040
- **Complexity**: L

### 7042 — Schema Migration for Governance Tables

- **What**: Alembic migration for: `pact_orgs`, `pact_org_nodes`, `pact_role_envelopes`, `pact_task_envelopes`, `pact_clearances`, `pact_ksps`, `pact_bridges`, `pact_audit_log` (append-only with content hashes). Dialect-agnostic (SQLite + PostgreSQL). Indexes on address columns for prefix queries.
- **Where**: `alembic/versions/YYYYMMDD_governance_tables.py`
- **Evidence**: `alembic upgrade head` creates all tables. `alembic downgrade -1` removes cleanly. `pact_audit_log` has `CHECK` constraint preventing updates/deletes (append-only enforcement at DB level where supported).
- **Dependencies**: 7040
- **Complexity**: M

### 7043 — GovernanceEngine Store Backend Configuration

- **What**: Update `GovernanceEngine` constructor: `GovernanceEngine(org, store_backend="sqlite", store_url="governance.db")` or `GovernanceEngine(org, store_backend="memory")`. Factory creates appropriate stores. Default is in-memory for development. Persists compiled org, envelopes, clearances, KSPs, bridges. Loads existing state on startup.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine1 = GovernanceEngine(org, store_backend="sqlite", store_url="test.db"); engine1.grant_clearance(...)`. New `engine2 = GovernanceEngine(org, store_backend="sqlite", store_url="test.db")` loads persisted clearance.
- **Dependencies**: 7010, 7040
- **Complexity**: M

### 7044 — Audit Log Integrity: Append-Only with Content Hashes

- **What**: Governance audit log entries include a SHA-256 content hash and a chain hash (hash of previous entry + current entry). This makes the audit log tamper-evident. Implemented in both in-memory and SQLite stores. Audit entries are immutable once written (append-only).
- **Where**: `src/pact/governance/audit.py`, `src/pact/governance/stores/sqlite.py`
- **Evidence**: Modify an audit entry in the SQLite database directly. `engine.verify_audit_integrity()` detects the tampering and returns `AuditIntegrityError`. Append-only: `UPDATE pact_audit_log` raises constraint violation.
- **Dependencies**: 7040, 7014
- **Complexity**: M

### 7045 — Store Backup and Restore

- **What**: Backup/restore utilities: `backup_governance_store(engine, path)` creates portable JSON snapshot. `restore_governance_store(engine, path)` loads it. Include audit chain in backup with integrity verification on restore.
- **Where**: `src/pact/governance/stores/backup.py`
- **Evidence**: Backup -> modify -> restore -> state matches original. Audit integrity verified after restore.
- **Dependencies**: 7040, 7043
- **Complexity**: M

### 7046 — DataFlow Persistence Tests

- **What**: Tests for all persistence stores: round-trip for all four store types, concurrent access, bounded collection eviction, migration up/down, factory configuration, backup fidelity, audit integrity, ID validation, file permissions.
- **Where**: `tests/unit/governance/test_sqlite_stores.py`, `tests/unit/governance/test_postgresql_stores.py`, `tests/unit/governance/test_backup.py`
- **Evidence**: `pytest tests/unit/governance/test_sqlite_stores.py tests/unit/governance/test_backup.py` passes. PostgreSQL tests skip when unavailable.
- **Dependencies**: 7040-7045
- **Complexity**: L

---

## Milestone 12: Nexus API + Governance Endpoints (7050-7057)

REST endpoints with authorization model, rate limiting, input validation. Pydantic schemas. Mount on existing FastAPI server.

---

### 7050 — Governance API Schema Models (Pydantic)

- **What**: Pydantic request/response models: `CheckAccessRequest/Response`, `ComputeEnvelopeRequest/Response`, `VerifyActionRequest/Response`, `GrantClearanceRequest`, `CreateBridgeRequest`, `CreateKSPRequest`, `OrgSummaryResponse`, `RoleDetailResponse`. All numeric fields validated with `math.isfinite()`. Address fields validated against D/T/R grammar. Enum fields restricted to valid values.
- **Where**: `src/pact/governance/api/schemas.py`
- **Evidence**: All schema models produce valid OpenAPI definitions. `CheckAccessRequest(role_address="../../etc", ...)` raises `ValidationError`.
- **Dependencies**: 7010
- **Complexity**: M

### 7051 — Authorization Model for Governance Endpoints

- **What**: Define authorization requirements for each endpoint. Read-only endpoints (check-access, compute-envelope, org query) require `governance:read` scope. State-mutating endpoints (grant-clearance, create-bridge, create-ksp) require `governance:write` scope. Bearer token with scope extraction. Default: all endpoints require authentication (no unauthenticated access to governance state). Uses existing `PACT_API_TOKEN` env var for now, with scope encoded in claims.
- **Where**: `src/pact/governance/api/auth.py`
- **Evidence**: Unauthenticated `POST /api/v1/governance/check-access` returns 401. Token with `governance:read` scope succeeds. Token with only `governance:read` calling `POST /clearances` returns 403.
- **Dependencies**: None
- **Complexity**: M

### 7052 — Core Governance Endpoints

- **What**: REST endpoints: `POST /api/v1/governance/check-access`, `POST /api/v1/governance/compute-envelope`, `POST /api/v1/governance/verify-action`. JSON request/response per schema models. Delegates to `GovernanceEngine`. Rate limited (configurable, default 100 req/min per token).
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `curl -X POST /api/v1/governance/check-access -H "Authorization: Bearer $TOKEN" -d '...'` returns structured response.
- **Dependencies**: 7050, 7051, 7010
- **Complexity**: L

### 7053 — Organization Query Endpoints

- **What**: `GET /api/v1/governance/org` (summary), `GET /api/v1/governance/org/nodes?prefix=D1` (prefix query), `GET /api/v1/governance/org/nodes/{address}` (single node), `GET /api/v1/governance/org/tree` (full tree for visualization).
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `GET /org/tree` returns nested JSON with all departments, teams, roles.
- **Dependencies**: 7050, 7051
- **Complexity**: M

### 7054 — State Management Endpoints

- **What**: `POST /clearances` (grant), `DELETE /clearances/{address}` (revoke), `GET /clearances/{address}` (get), `POST /bridges`, `POST /ksps`, `GET /bridges`, `GET /ksps`, `GET /envelopes/{address}`. All require `governance:write` scope for mutations. Input validation per schema models.
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `POST /clearances` with body returns 201. Subsequent `GET /clearances/{addr}` returns it. `POST /check-access` uses the new clearance.
- **Dependencies**: 7052, 7015
- **Complexity**: M

### 7055 — Mount Governance API on FastAPI Server

- **What**: FastAPI router for all governance endpoints. Conditionally mounted when `GovernanceEngine` is configured. Legacy trust-plane endpoints continue working. Rate limiting middleware. Request body size limits (1MB). Response compression.
- **Where**: `src/pact/governance/api/router.py`, `src/pact/use/api/server.py`
- **Evidence**: Server starts with both legacy and governance endpoints. Health endpoint works. Governance endpoints require auth.
- **Dependencies**: 7052-7054
- **Complexity**: M

### 7056 — Governance WebSocket Events

- **What**: WebSocket event types: `governance.access_decision`, `governance.envelope_computed`, `governance.clearance_changed`, `governance.bridge_created`. Real-time governance events pushed to connected dashboard clients. Bounded event queue (1000 max).
- **Where**: `src/pact/governance/api/events.py`
- **Evidence**: WebSocket client on `/ws` receives `governance.access_decision` when `POST /check-access` is called.
- **Dependencies**: 7055
- **Complexity**: M

### 7057 — API Integration Tests

- **What**: Full API tests with HTTPX test client: all endpoints, error responses (401, 403, 404, 422), rate limiting, concurrent requests, WebSocket events, authorization scopes, input validation (NaN, path traversal, oversized body).
- **Where**: `tests/integration/test_governance_api.py`
- **Evidence**: Full test suite passes. Coverage of all endpoints and error paths.
- **Dependencies**: 7050-7056
- **Complexity**: L

---

## Milestone 13: Frontend Dashboard (7060-7065)

Wire the existing Next.js dashboard to the new governance API. Governance-native visualization and testing tools.

---

### 7060 — Governance API Client (TypeScript)

- **What**: TypeScript client for governance endpoints. Type-safe with Pydantic schemas as source of truth. Functions: `checkAccess()`, `computeEnvelope()`, `verifyAction()`, `getOrg()`, `queryNodes()`, `grantClearance()`, `createBridge()`, `listBridges()`. Auth token management.
- **Where**: `apps/web/lib/governance-api.ts`
- **Evidence**: `const decision = await checkAccess({roleAddress: "D1-R1", ...})` returns typed response matching Python schemas.
- **Dependencies**: 7050
- **Complexity**: M

### 7061 — Organization Tree Visualization Page

- **What**: Interactive D/T/R tree visualization. Nodes colored by type (D=blue, T=green, R=yellow). Click node for details: role info, clearance, envelope. Expandable/collapsible subtrees. Uses `GET /org/tree`.
- **Where**: `apps/web/app/org/page.tsx`, `apps/web/app/org/elements/OrgTree.tsx`
- **Evidence**: Page renders university org tree with 20+ nodes. Click node shows detail panel.
- **Dependencies**: 7060, 7053
- **Complexity**: L

### 7062 — Access Decision Testing Page

- **What**: Interactive "What If" page: select role (from org tree dropdown), configure knowledge item (classification, compartments, owning unit), choose posture, click "Check Access". Shows 5-step decision trace with pass/fail per step.
- **Where**: `apps/web/app/governance/access-test/page.tsx`
- **Evidence**: User picks role, configures item, clicks check. Sees `{allowed: true, reason: "Step 4a: same unit", trace: [...]}`.
- **Dependencies**: 7060, 7052
- **Complexity**: M

### 7063 — Envelope Viewer Page

- **What**: Three-layer PACT envelope visualization: Role Envelope (standing) + Task Envelope (ephemeral) = Effective Envelope. Per-dimension visual bars showing utilization. Select role from dropdown. Shows degenerate envelope warnings.
- **Where**: `apps/web/app/envelopes/page.tsx`
- **Evidence**: Selecting a role shows three-layer decomposition with per-dimension breakdown.
- **Dependencies**: 7060
- **Complexity**: M

### 7064 — Governance Dashboard Home Page

- **What**: Dashboard overview: org summary (departments, teams, roles), recent access decisions, active bridges/KSPs, clearance summary. Replace legacy trust-plane widgets with governance-native data.
- **Where**: `apps/web/app/page.tsx`
- **Evidence**: Home page shows governance statistics, recent decisions, links to governance sub-pages.
- **Dependencies**: 7060
- **Complexity**: M

### 7065 — Frontend Tests

- **What**: Vitest tests for governance API client, org tree, access test page, envelope viewer. Mock API responses.
- **Where**: `apps/web/__tests__/governance/`
- **Evidence**: `cd apps/web && npm test` passes with governance test coverage.
- **Dependencies**: 7060-7064
- **Complexity**: M

---

## Milestone 14: Documentation + Examples (7070-7079)

Quickstart, vertical integration guide, API reference, cookbook, university example polish, CLI validation tool. Everything a consumer needs to go from zero to governed agent in 10 minutes.

---

### 7070 — PACT Framework Quickstart Guide

- **What**: Step-by-step guide: install kailash-pact, define org in YAML, create GovernanceEngine, check access, compute envelopes, verify actions. From zero to running in 10 minutes. University example as tutorial subject.
- **Where**: `docs/quickstart.md` (rewrite)
- **Evidence**: New developer following guide can `pip install kailash-pact`, define a 3-dept org, and run an access check in <10 minutes. All code examples execute.
- **Dependencies**: 7010, 7011
- **Complexity**: M

### 7071 — Vertical Integration Guide

- **What**: Guide for building a vertical on PACT: import `kailash_pact`, define D/T/R structure, configure envelopes, set up clearances, create governed agents. Uses a minimal "bookstore" example. Explains boundary test. Shows Astra/Arbor as real-world references.
- **Where**: `docs/vertical-guide.md`
- **Evidence**: Guide includes working bookstore vertical. Code examples execute. Boundary test explained with examples.
- **Dependencies**: 7010
- **Complexity**: L

### 7072 — API Reference Documentation

- **What**: Auto-generated API reference from Pydantic schemas. All governance endpoints with curl examples. Authentication, error codes, WebSocket events. OpenAPI spec export.
- **Where**: `docs/api.md` (rewrite), `docs/rest-api.md` (rewrite)
- **Evidence**: Every governance endpoint documented with curl examples. `mkdocs build` clean.
- **Dependencies**: 7050-7055
- **Complexity**: M

### 7073 — University Example Polish

- **What**: Reference-quality demonstration: YAML config file (in addition to Python), envelope definitions for all roles, README, runnable demo script with colored output showing all 14 E2E scenarios. YAML config produces identical org to Python construction.
- **Where**: `src/pact/examples/university/config.yaml`, `src/pact/examples/university/demo.py`, `src/pact/examples/university/envelopes.py`
- **Evidence**: `python -m pact.examples.university.demo` runs all scenarios with colored output. YAML and Python produce identical results.
- **Dependencies**: 7011 (YAML loading)
- **Complexity**: M

### 7074 — Architecture Documentation Update

- **What**: Update `docs/architecture.md`: GovernanceEngine as central facade, three-layer envelope model, D/T/R addressing, clearance independence, 5-step access algorithm, EATP integration. Architecture diagrams.
- **Where**: `docs/architecture.md` (rewrite)
- **Evidence**: Accurately describes current implementation. No stale references.
- **Dependencies**: 7010
- **Complexity**: M

### 7075 — Cookbook: Common Governance Patterns

- **What**: Recipes: "Add a department", "Create a cross-functional bridge", "Set up information barriers", "Define role envelopes by posture", "Handle posture upgrades", "Integrate with AI agent", "Configure knowledge clearance", "Set up approval queue". Each recipe is self-contained.
- **Where**: `docs/cookbook.md` (rewrite)
- **Evidence**: Each recipe is runnable. Code examples execute without errors.
- **Dependencies**: 7010
- **Complexity**: M

### 7076 — CLI Validation Tool

- **What**: `kailash-pact validate org.yaml` command that loads a YAML org definition, compiles it, and reports: number of nodes, depth, any grammar violations, degenerate envelopes, missing clearances, expired KSPs/bridges. Exit 0 on valid, exit 1 on errors. Colored output.
- **Where**: `src/pact/governance/cli.py`, `pyproject.toml` (entry point)
- **Evidence**: `kailash-pact validate examples/university/org.yaml` prints "Valid: 23 nodes, max depth 8, 0 issues". `kailash-pact validate bad.yaml` prints errors and exits 1.
- **Dependencies**: 7011
- **Complexity**: M

### 7077 — YAML Schema Documentation

- **What**: Document the unified YAML format with annotated examples: every field, every option, every constraint dimension. JSON Schema for editor autocompletion. Validation error messages reference the docs.
- **Where**: `docs/yaml-schema.md`, `src/pact/governance/schema.json`
- **Evidence**: YAML with typo gets error message like "Unknown field 'depratments' at line 5. Did you mean 'departments'? See docs/yaml-schema.md".
- **Dependencies**: 7011
- **Complexity**: M

### 7078 — README Rewrite

- **What**: Rewrite `README.md` for `kailash-pact`: what it is, installation (`pip install kailash-pact`), quickstart (5 lines to governance decision), features, link to docs. Remove all care-platform legacy language. Clear framework vs vertical distinction.
- **Where**: `README.md`
- **Evidence**: README accurately describes framework. Quickstart snippet is copy-pasteable. All links work.
- **Dependencies**: 7010, 7070
- **Complexity**: M

### 7079 — Getting Started Guide + Migration from Legacy

- **What**: Rewrite `docs/getting-started.md`: what PACT is, how it relates to CARE/EATP/CO, when to use it, how to start. Include migration section for existing care-platform users: mapping old APIs to GovernanceEngine methods.
- **Where**: `docs/getting-started.md` (rewrite)
- **Evidence**: New reader understands purpose and first steps. Legacy user can migrate.
- **Dependencies**: 7010
- **Complexity**: M

---

## Milestone 15: Red Team + Hardening (7080-7087)

Tests ALREADY-HARDENED code. Security was baked into M7-M12. This milestone validates that hardening, fills remaining gaps, and handles edge cases.

---

### 7080 — TOCTOU Treatment for Effective Envelopes

- **What**: If envelope changes between verification and execution, action proceeds under stale constraints. Fix: `compute_effective_envelope()` returns snapshot with version/timestamp. Execution runtime compares snapshot version. If mismatched, re-verify. Add `envelope_version` to `GovernanceVerdict`.
- **Where**: `src/pact/governance/envelopes.py`, `src/pact/governance/engine.py`, `src/pact/governance/verdict.py`
- **Evidence**: Test: change envelope between verify and execute. Runtime detects stale snapshot, re-verifies. Matching snapshot proceeds without re-verification.
- **Dependencies**: 7012
- **Complexity**: L

### 7081 — TOCTOU Treatment for KSP/Bridge Expiry

- **What**: KSP/bridge expiry check in `can_access()` is TOCTOU-vulnerable: expiry checked at decision time, but execution happens later. Fix: access decision includes `valid_until` timestamp (minimum of KSP/bridge expiry). Execution runtime checks `valid_until` before proceeding.
- **Where**: `src/pact/governance/access.py`, `src/pact/governance/engine.py`
- **Evidence**: Test: KSP expires between access check and execution. Runtime detects `valid_until` exceeded and re-checks.
- **Dependencies**: 7012
- **Complexity**: M

### 7082 — Formal PACT-to-EATP Record Mapping

- **What**: Document and implement the mapping: `compile_org` -> Genesis Record, `set_role_envelope` -> Delegation Record, `grant_clearance` -> Capability Attestation, `check_access` -> Audit Anchor. `PactEatpMapper` class produces EATP records from governance operations.
- **Where**: `src/pact/governance/eatp_mapping.py`, `docs/architecture/pact-eatp-mapping.md`
- **Evidence**: `mapper.map_clearance_grant(clearance)` produces valid EATP Capability Attestation. All 10 `PactAuditAction` types mapped.
- **Dependencies**: 7014
- **Complexity**: L

### 7083 — Multi-Level VERIFY Pattern

- **What**: Cascading verification: action at depth N cascades up accountability chain, checking each ancestor's envelope. Most restrictive verdict applies. If T1's envelope allows but D1's blocks, result is BLOCKED.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: Role at depth 4 verifies action. Ancestor at depth 1 has tighter envelope. Verdict is BLOCKED because ancestor blocks.
- **Dependencies**: 7012
- **Complexity**: M

### 7084 — Rate Limiting on Governance Operations

- **What**: Configurable rate limits on governance API endpoints and engine methods. Default: 100 decisions/min, 10 mutations/min. Rate limit state per-token for API, per-thread for direct engine calls. Return `429 Too Many Requests` with `Retry-After` header.
- **Where**: `src/pact/governance/api/rate_limit.py`, `src/pact/governance/engine.py`
- **Evidence**: 101st request in a minute returns 429. After `Retry-After` period, requests succeed.
- **Dependencies**: 7055
- **Complexity**: M

### 7085 — Adversarial Red Team

- **What**: Full adversarial red team of governance layer: bypass access controls, forge envelopes, exploit TOCTOU, inject through API, escalate clearance, traverse store paths, poison numeric fields (NaN/Inf should already be blocked), exhaust memory, self-modify governance context, concurrent race conditions. Document all findings.
- **Where**: `workspaces/pact/04-validate/rt21-governance-report.md`, `tests/unit/governance/test_redteam_rt21.py`
- **Evidence**: Red team report with all findings. All CRITICAL/HIGH have regression tests. All regression tests pass.
- **Dependencies**: 7080-7084 (hardening must be in place)
- **Complexity**: XL

### 7086 — Red Team Remediation

- **What**: Fix all CRITICAL and HIGH findings from RT21. Regression tests for each fix. Re-validate.
- **Where**: Various (depends on findings)
- **Evidence**: All CRITICAL/HIGH resolved. Regression tests pass. Re-validation confirms no regressions.
- **Dependencies**: 7085
- **Complexity**: L

### 7087 — Convergence Validation

- **What**: Final validation that all governance security invariants hold after remediation. Run full test suite. Verify no regressions from M7-M14 changes. Confirm all red team findings are addressed.
- **Where**: `workspaces/pact/04-validate/rt21-convergence.md`
- **Evidence**: Full test suite green. All security invariants documented and verified. Convergence report signed off.
- **Dependencies**: 7086
- **Complexity**: M

---

## Milestone 16: Ship Readiness (7090-7099)

Package as `kailash-pact`, publish to PyPI, CI hardening, version bump, changelog, legacy cleanup, final validation.

---

### 7090 — Rename Package to kailash-pact

- **What**: Update `pyproject.toml`: `name = "kailash-pact"`, update all import paths documentation to use `kailash_pact` (Python import name) vs `kailash-pact` (pip name). Actual source stays in `src/pact/` for now (import as `import pact` internally). The PyPI distribution name is `kailash-pact` to avoid the pact-python conflict. Add `provides-extra` for `kailash-pact[kailash]`, `kailash-pact[postgres]`.
- **Where**: `pyproject.toml`, `README.md`, `docs/quickstart.md`
- **Evidence**: `pip install kailash-pact` installs cleanly. `from pact.governance import GovernanceEngine` works. No conflict with pact-python.
- **Dependencies**: None (can be done early)
- **Complexity**: M

### 7091 — Version Bump to 0.2.0

- **What**: Bump to 0.2.0 (governance layer is major feature addition). Update `pyproject.toml` and `src/pact/__init__.py` atomically. Update all documentation version references.
- **Where**: `pyproject.toml`, `src/pact/__init__.py`, `README.md`, `docs/`
- **Evidence**: `python -c "import pact; print(pact.__version__)"` prints `0.2.0`. All docs reference 0.2.0.
- **Dependencies**: All M7-M15
- **Complexity**: S

### 7092 — CHANGELOG Creation

- **What**: `CHANGELOG.md` documenting 0.1.0 -> 0.2.0: governance layer, GovernanceEngine, three-layer envelopes, D/T/R addressing, 5-step access algorithm, governed agents, DataFlow persistence, API endpoints, dashboard, security fixes. Keep a Changelog format.
- **Where**: `CHANGELOG.md`
- **Evidence**: Changelog describes all features, fixes, breaking changes.
- **Dependencies**: 7091
- **Complexity**: S

### 7093 — CI Pipeline Hardening

- **What**: CI runs: unit tests, governance tests, integration tests, ruff lint, mypy type check, security scanning, package build, documentation build. All must pass on PR. Add governance-specific CI job.
- **Where**: `.github/workflows/ci.yml`
- **Evidence**: PR with failing governance test is blocked. CI pipeline runs all checks green.
- **Dependencies**: None (parallel)
- **Complexity**: M

### 7094 — Legacy Cleanup: Foundation Example

- **What**: `src/pact/examples/foundation/` uses Foundation-specific vocabulary (dm-team, dm-runner). Violates boundary test. Move to `archive/legacy-foundation/`. University is the canonical example.
- **Where**: `src/pact/examples/foundation/` -> `archive/legacy-foundation/`
- **Evidence**: `src/pact/examples/` contains only `university/` (and future example verticals). No boundary test violations.
- **Dependencies**: None
- **Complexity**: S

### 7095 — Legacy Cleanup: API Endpoint Consolidation

- **What**: Audit all endpoints in `src/pact/use/api/endpoints.py`. Map each legacy endpoint to governance equivalent. Add deprecation headers. Document migration path.
- **Where**: `src/pact/use/api/endpoints.py`, `docs/migration/legacy-api.md`
- **Evidence**: Legacy endpoints emit deprecation warnings. Migration documented.
- **Dependencies**: 7055
- **Complexity**: M

### 7096 — Legacy Cleanup: care-platform References

- **What**: Audit entire codebase for references to "care-platform", "care_platform", "CARE Platform" (as product name, not CARE specification). Replace with PACT references. Check imports, comments, docstrings, config files, test fixtures.
- **Where**: All files
- **Evidence**: `grep -r "care.platform\|care_platform\|CARE Platform" src/` returns zero results (excluding specification references).
- **Dependencies**: None
- **Complexity**: M

### 7097 — PyPI Publishing Workflow

- **What**: Publish workflow produces clean `kailash-pact` package. Verify installs in fresh venv. All imports work. No conflict with pact-python. Trusted publisher setup for PyPI.
- **Where**: `.github/workflows/publish.yml`
- **Evidence**: `pip install dist/kailash_pact-0.2.0-py3-none-any.whl` in clean venv. `from pact.governance import GovernanceEngine` works.
- **Dependencies**: 7090, 7091
- **Complexity**: M

### 7098 — Update decisions.yml for Phase 2

- **What**: Add all architectural decisions made during M7-M16 to `decisions.yml`. Key decisions: kailash-pact naming, Option B architecture, fail-closed adapter, default-deny tools, frozen GovernanceContext, TOCTOU treatment, append-only audit.
- **Where**: `workspaces/pact/decisions.yml`
- **Evidence**: `decisions.yml` has entries for every significant decision. Future sessions can query governance-era decisions.
- **Dependencies**: All milestones
- **Complexity**: S

### 7099 — Final Validation: Full Test Suite

- **What**: Run complete test suite (unit + governance + integration + E2E). Verify >85% coverage for `pact.governance`. Zero ruff/mypy errors. All documentation builds. Package installs. This is the final gate.
- **Where**: All test directories
- **Evidence**: `pytest --cov=pact.governance --cov-report=term-missing` >85%. `ruff check src/` clean. `mypy src/pact/governance/` clean. Zero failures.
- **Dependencies**: All previous milestones
- **Complexity**: M

---

## Summary

| Milestone | Todos        | Description                         | Est. Days |
| --------- | ------------ | ----------------------------------- | --------- |
| M7        | 7001-7009    | COC Infrastructure + Security Fixes | 3-4       |
| M8        | 7010-7018    | GovernanceEngine Facade             | 5-7       |
| M9        | 7020-7025    | Envelope Unification                | 3-4       |
| M10       | 7030-7037    | PactGovernedAgent + Kaizen          | 4-5       |
| M11       | 7040-7046    | DataFlow Persistence                | 5-7       |
| M12       | 7050-7057    | Nexus API + Governance Endpoints    | 4-6       |
| M13       | 7060-7065    | Frontend Dashboard                  | 3-4       |
| M14       | 7070-7079    | Documentation + Examples            | 4-5       |
| M15       | 7080-7087    | Red Team + Hardening                | 4-6       |
| M16       | 7090-7099    | Ship Readiness                      | 3-4       |
| **Total** | **70 todos** |                                     | **38-52** |

## Security Integration Points (Not a Separate Phase)

Security is baked into each milestone, not deferred:

| Security Concern          | Addressed In | Todo(s)   |
| ------------------------- | ------------ | --------- |
| NaN/Inf bypass            | M7           | 7005      |
| Mutable RoleDefinition    | M7           | 7006      |
| Mutable CompiledOrg.nodes | M7           | 7007      |
| Unbounded recursion       | M7           | 7008      |
| Thread safety (stores)    | M7           | 7009      |
| Thread safety (engine)    | M8           | 7010      |
| Fail-closed on error      | M8           | 7012      |
| Frozen governance context | M8           | 7016      |
| Agent self-modification   | M10          | 7036      |
| Default-deny tools        | M10          | 7032      |
| Fail-closed adapter       | M9           | 7020      |
| Store security parity     | M11          | 7040-7041 |
| Audit integrity           | M11          | 7044      |
| API authorization         | M12          | 7051      |
| API input validation      | M12          | 7050      |
| Rate limiting             | M15          | 7084      |
| TOCTOU (envelopes)        | M15          | 7080      |
| TOCTOU (KSP/bridge)       | M15          | 7081      |
| Adversarial red team      | M15          | 7085      |
