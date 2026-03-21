# PACT Framework — Master Todo List

## Overview

Complete todo list for making PACT a shippable, importable governance framework.

**Starting state**: M0-M6 complete. Governance layer (`src/pact/governance/`) has addressing, compilation, clearance, knowledge, access enforcement, envelopes, audit, and in-memory stores. University example with 14 E2E scenarios passes. Trust layer, build layer, use layer, and web dashboard exist from care-platform era. 4,036 tests passing.

**End state**: `pip install pact` gives verticals (astra, arbor) a complete governance framework with a single-call `GovernanceEngine`, persistent stores, REST API, governed agent runtime, and comprehensive documentation.

---

## Milestone 7: GovernanceEngine Facade (7001-7006)

The single most important deliverable. Today, consumers must manually wire 6+ components to get a governance decision. After M7, one call does it all.

---

## Milestone 8: Envelope Unification (7010-7014)

Two parallel envelope systems exist: governance `compute_effective_envelope()` (the correct PACT three-layer model) and trust-layer `ConstraintEnvelope` (the legacy runtime evaluator). M8 makes governance canonical and trust-layer delegates to it.

---

## Milestone 9: PactGovernedAgent + Kaizen Integration (7020-7025)

Bridge between "AI agent framework" (Kaizen) and "governed organization" (PACT). When an agent calls a tool, governance checks happen BEFORE execution.

---

## Milestone 10: DataFlow Persistence (7030-7035)

Replace in-memory governance stores with DataFlow-backed SQLite/PostgreSQL persistence. Production-ready storage for compiled orgs, envelopes, clearances, and access policies.

---

## Milestone 11: Nexus API — Governance Endpoints (7040-7046)

Expose governance operations as REST API endpoints. Replace the legacy trust-plane API surface with governance-native endpoints.

---

## Milestone 12: Frontend Dashboard Update (7050-7055)

Wire the existing Next.js dashboard to the new governance API. Replace legacy trust-plane data sources with governance-native data.

---

## Milestone 13: Documentation + Examples (7060-7067)

Quickstart guide, vertical integration guide, API reference, and a polished university example that serves as the canonical "how to use PACT" tutorial.

---

## Milestone 14: Red Team + Hardening (7070-7078)

Thesis gap fixes, security hardening, TOCTOU treatment, and formal PACT-to-EATP record mapping.

---

## Milestone 15: Ship Readiness (7080-7087)

PyPI packaging, CI hardening, version consistency, changelog, and final validation.

---

## Detailed Todos

### Milestone 7: GovernanceEngine Facade

#### 7001 — GovernanceEngine Core Class

- **What**: Create `GovernanceEngine` class that composes `CompiledOrg`, `EnvelopeStore`, `ClearanceStore`, `AccessPolicyStore`, and `GradientEngine` behind a single facade. Constructor accepts an `OrgDefinition` (or YAML path) and optional store implementations (defaulting to in-memory). Provides: `engine.check_access(role_address, knowledge_item, posture)`, `engine.compute_envelope(role_address, task_id?)`, `engine.verify_action(role_address, action, context)`, `engine.get_org()`.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `from pact.governance import GovernanceEngine; engine = GovernanceEngine(org_config); decision = engine.check_access(...)` works in a single import + two lines.
- **Dependencies**: None (uses existing governance components)
- **Complexity**: L

#### 7002 — GovernanceEngine.from_yaml() Factory

- **What**: Factory method that loads an `OrgDefinition` from a YAML config file, compiles it, and returns a ready-to-use `GovernanceEngine`. Verticals call `GovernanceEngine.from_yaml("org.yaml")` to bootstrap.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine = GovernanceEngine.from_yaml("examples/university/org.yaml")` returns a functional engine. Test loads YAML and verifies access decisions match in-memory construction.
- **Dependencies**: 7001
- **Complexity**: M

#### 7003 — GovernanceEngine.verify_action() Integration

- **What**: Implement `verify_action(role_address, action, context)` that combines envelope computation, gradient classification, and access checking into a single `GovernanceVerdict` result. Returns `AUTO_APPROVED`, `FLAGGED`, `HELD`, or `BLOCKED` with structured reason and audit details. This is the primary call for agent middleware.
- **Where**: `src/pact/governance/engine.py`, `src/pact/governance/verdict.py`
- **Evidence**: `verdict = engine.verify_action("D1-R1-D1-R1-T1-R1", "write_report", {"cost": 50.0})` returns a `GovernanceVerdict` with level, reason, envelope snapshot, and audit details.
- **Dependencies**: 7001
- **Complexity**: L

#### 7004 — GovernanceEngine Audit Integration

- **What**: Wire `GovernanceEngine` to emit EATP Audit Anchors for every governance decision (access grant/deny, envelope computation, clearance check). Uses the `PactAuditAction` types from `governance/audit.py`. Optional `AuditChain` passed at construction time.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: After `engine.check_access(...)`, `engine.audit_chain.get_all()` contains an anchor with `pact_action=barrier_enforced` and structured details.
- **Dependencies**: 7001, 7003
- **Complexity**: M

#### 7005 — GovernanceEngine State Management

- **What**: Methods for runtime state mutations: `engine.grant_clearance(role_address, clearance)`, `engine.revoke_clearance(role_address)`, `engine.create_bridge(bridge)`, `engine.create_ksp(ksp)`, `engine.set_role_envelope(envelope)`, `engine.set_task_envelope(envelope)`. All mutations emit audit anchors.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine.grant_clearance("D1-R1", clearance); decision = engine.check_access(...)` uses the newly granted clearance. Audit chain records `clearance_granted`.
- **Dependencies**: 7001, 7004
- **Complexity**: M

#### 7006 — GovernanceEngine Unit + Integration Tests

- **What**: Comprehensive test suite for `GovernanceEngine`: construction, YAML loading, access decisions, envelope computation, action verification, audit integration, state mutation, error handling (missing org, invalid config). Use university example as the primary fixture.
- **Where**: `tests/unit/governance/test_engine.py`, `tests/integration/test_governance_engine.py`
- **Evidence**: `pytest tests/unit/governance/test_engine.py tests/integration/test_governance_engine.py` passes with >90% coverage of `engine.py`.
- **Dependencies**: 7001-7005
- **Complexity**: L

---

### Milestone 8: Envelope Unification

#### 7010 — Adapter: Governance Envelope to Trust-Layer ConstraintEnvelope

- **What**: Create an adapter that converts between `governance.envelopes.RoleEnvelope`/`TaskEnvelope` and `trust.constraint.envelope.ConstraintEnvelope`. The governance layer's `compute_effective_envelope()` becomes the CANONICAL source. The trust-layer `ConstraintEnvelope.evaluate()` delegates to the governance computation when a `GovernanceEngine` is available.
- **Where**: `src/pact/governance/envelope_adapter.py`
- **Evidence**: `adapted = GovernanceEnvelopeAdapter(engine).to_constraint_envelope(role_address)` produces a `ConstraintEnvelope` with identical constraints. Round-trip test: governance -> trust-layer -> evaluate -> same result as governance direct.
- **Dependencies**: 7001
- **Complexity**: L

#### 7011 — GradientEngine Governance Integration

- **What**: Modify `GradientEngine` to accept a `GovernanceEngine` and use governance envelope computation instead of its own standalone evaluation. When governance is available, `classify_action()` calls `engine.verify_action()` under the hood. When governance is not available (backward compatibility), falls back to the existing behavior.
- **Where**: `src/pact/trust/constraint/gradient.py`
- **Evidence**: `GradientEngine(governance_engine=engine).classify_action(...)` uses governance envelopes. `GradientEngine(config=old_config).classify_action(...)` still works with legacy behavior. Both paths produce consistent results for the same constraints.
- **Dependencies**: 7010
- **Complexity**: L

#### 7012 — ExecutionRuntime Governance Integration

- **What**: Update `ExecutionRuntime` to accept a `GovernanceEngine`. When provided, the runtime uses `engine.verify_action()` for all pre-execution checks instead of the standalone gradient + envelope evaluation. The `AgentDefinition` receives its governance context (role_address, posture) from the engine.
- **Where**: `src/pact/use/execution/runtime.py`
- **Evidence**: `runtime = ExecutionRuntime(registry=reg, governance_engine=engine)` routes all verification through governance. `runtime.submit("action", agent_id="x")` triggers `engine.verify_action()`.
- **Dependencies**: 7011, 7003
- **Complexity**: L

#### 7013 — Deprecation Markers on Standalone Trust-Layer Envelope Evaluation

- **What**: Add deprecation warnings to direct `ConstraintEnvelope.evaluate()` calls and standalone `GradientEngine` construction without governance. Log warnings pointing users to `GovernanceEngine`. Do NOT remove yet -- backward compatibility for M15.
- **Where**: `src/pact/trust/constraint/envelope.py`, `src/pact/trust/constraint/gradient.py`
- **Evidence**: Calling `ConstraintEnvelope.evaluate(action_context)` without governance produces a `DeprecationWarning`. Tests capture and verify the warning.
- **Dependencies**: 7010, 7011
- **Complexity**: S

#### 7014 — Envelope Unification Tests

- **What**: Tests proving: (a) governance and trust-layer produce identical results for the same constraints; (b) three-layer envelope model (Role + Task + Effective) is correctly propagated through the adapter; (c) monotonic tightening violations caught identically in both paths; (d) backward compatibility -- old code without governance still works.
- **Where**: `tests/unit/governance/test_envelope_unification.py`
- **Evidence**: `pytest tests/unit/governance/test_envelope_unification.py` passes. Tests exercise both paths and assert identical outcomes.
- **Dependencies**: 7010-7013
- **Complexity**: M

---

### Milestone 9: PactGovernedAgent + Kaizen Integration

#### 7020 — PactGovernedAgent Base Class

- **What**: Create `PactGovernedAgent(BaseAgent)` that wraps any Kaizen agent with governance enforcement. Constructor takes `governance_engine`, `role_address`, and `posture`. Before any tool use, calls `engine.verify_action()`. BLOCKED actions raise `GovernanceBlockedError`. HELD actions raise `GovernanceHeldError` (for approval queue integration). FLAGGED actions proceed with a logged warning. AUTO_APPROVED actions proceed silently.
- **Where**: `src/pact/governance/agent.py`
- **Evidence**: `agent = PactGovernedAgent(engine=engine, role_address="D1-R1-T1-R1", base_agent=kaizen_agent)`. Calling `agent.run("write report")` triggers `engine.verify_action()` before execution. BLOCKED action raises exception. Test with mock agent confirms pre-check.
- **Dependencies**: 7003 (verify_action)
- **Complexity**: L

#### 7021 — Governance Middleware for Kaizen

- **What**: Create a Kaizen middleware/hook that can be registered on any Kaizen agent to enforce PACT governance without subclassing. `PactGovernanceMiddleware(engine, role_address)` registers as a pre-execution hook. This is the lighter-weight alternative to `PactGovernedAgent` -- works with any existing agent.
- **Where**: `src/pact/governance/middleware.py`
- **Evidence**: `middleware = PactGovernanceMiddleware(engine, "D1-R1"); agent.add_middleware(middleware)`. Agent tool use triggers governance check. Test confirms middleware intercepts and blocks governed actions.
- **Dependencies**: 7003
- **Complexity**: M

#### 7022 — Agent-to-Address Mapping

- **What**: Create `AgentRoleMapping` that maps agent IDs to D/T/R role addresses. This is the bridge between "agent X is running" and "agent X occupies role D1-R1-D2-R1-T1-R1". Populated from `OrgDefinition` (roles with `agent_id` field) or configured explicitly. Integrated into `GovernanceEngine`.
- **Where**: `src/pact/governance/agent_mapping.py`
- **Evidence**: `mapping = AgentRoleMapping.from_org(compiled_org); addr = mapping.get_address("agent-cs-chair")` returns `"D1-R1-D1-R1-D1-R1-T1-R1"`. Test with university org.
- **Dependencies**: 7001
- **Complexity**: M

#### 7023 — GovernedAgent Tool Wrapper

- **What**: A tool decorator `@governed_tool(action_name, cost=0.0)` that wraps Kaizen tool functions with governance checks. The decorator reads the governance context from the agent's session and calls `engine.verify_action()` before the tool executes. Returns `GovernanceBlockedError` if blocked.
- **Where**: `src/pact/governance/decorators.py`
- **Evidence**: `@governed_tool("write_report", cost=50.0) def write_report(content): ...`. When called by a governed agent, the tool checks governance before executing. Test verifies blocked tool raises, approved tool executes.
- **Dependencies**: 7020, 7021
- **Complexity**: M

#### 7024 — Approval Queue Integration

- **What**: Wire `GovernanceEngine` HELD verdicts to the existing `ApprovalQueue`. When `verify_action()` returns HELD, the action enters the approval queue with its governance context (role_address, action, envelope snapshot, reason). Approved actions resume execution. Rejected actions are recorded in the audit chain.
- **Where**: `src/pact/governance/engine.py`, `src/pact/use/execution/approval.py`
- **Evidence**: `verdict = engine.verify_action(...)` returns HELD. `approval_queue.get_pending()` contains the action. `approval_queue.approve(action_id)` allows execution to resume. Audit chain records both the hold and the resolution.
- **Dependencies**: 7003, 7004
- **Complexity**: M

#### 7025 — Kaizen Integration Tests

- **What**: Integration tests proving: (a) PactGovernedAgent blocks actions exceeding envelope; (b) middleware intercepts governed tool calls; (c) agent-to-address mapping resolves correctly; (d) HELD actions enter approval queue; (e) audit chain records all governance decisions from agent execution; (f) backward compatibility -- agents without governance still work.
- **Where**: `tests/unit/governance/test_governed_agent.py`, `tests/integration/test_kaizen_governance.py`
- **Evidence**: Full test suite passes. Tests use university example with mock Kaizen agents.
- **Dependencies**: 7020-7024
- **Complexity**: L

---

### Milestone 10: DataFlow Persistence

#### 7030 — SQLite Governance Store

- **What**: Implement `SqliteOrgStore`, `SqliteEnvelopeStore`, `SqliteClearanceStore`, `SqliteAccessPolicyStore` that persist governance state to SQLite. Follow the existing trust-plane SQLite store patterns (parameterized queries, atomic writes, bounded collections, file permissions). Each store implements the corresponding Protocol from `governance/store.py`.
- **Where**: `src/pact/governance/stores/sqlite.py`
- **Evidence**: `store = SqliteOrgStore("governance.db"); store.save_org(compiled_org); loaded = store.load_org("university-001")` round-trips correctly. All store protocol methods implemented and tested.
- **Dependencies**: 7001
- **Complexity**: XL

#### 7031 — PostgreSQL Governance Store

- **What**: Implement PostgreSQL versions of all four governance stores. Follow the existing trust-plane PostgreSQL store patterns. Use parameterized queries, connection pooling safety, and the `?` canonical placeholder convention from infrastructure-sql rules.
- **Where**: `src/pact/governance/stores/postgresql.py`
- **Evidence**: Tests pass with a PostgreSQL test fixture (or are skipped when PostgreSQL is unavailable). All protocol methods work identically to SQLite.
- **Dependencies**: 7030
- **Complexity**: L

#### 7032 — Schema Migration for Governance Tables

- **What**: Create Alembic migration(s) for governance tables: `pact_orgs`, `pact_org_nodes`, `pact_role_envelopes`, `pact_task_envelopes`, `pact_clearances`, `pact_ksps`, `pact_bridges`. Tables are dialect-agnostic (works with SQLite and PostgreSQL). Include indexes on address columns for prefix queries.
- **Where**: `alembic/versions/YYYYMMDD_governance_tables.py`
- **Evidence**: `alembic upgrade head` creates all tables. `alembic downgrade -1` removes them cleanly. Schema matches the Protocol field requirements.
- **Dependencies**: 7030
- **Complexity**: M

#### 7033 — GovernanceEngine Store Backend Configuration

- **What**: Update `GovernanceEngine` constructor to accept store backend configuration: `GovernanceEngine(org_config, store_backend="sqlite", store_url="governance.db")` or `GovernanceEngine(org_config, store_backend="memory")`. Factory pattern creates the appropriate store implementations. Default is in-memory for development.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: `engine = GovernanceEngine(config, store_backend="sqlite", store_url="test.db"); engine.grant_clearance(...); engine2 = GovernanceEngine(config, store_backend="sqlite", store_url="test.db")` -- second engine loads persisted clearance.
- **Dependencies**: 7001, 7030
- **Complexity**: M

#### 7034 — Store Backup and Restore

- **What**: Governance store backup/restore utilities mirroring the existing trust-plane backup patterns. `backup_governance_store(engine, path)` creates a portable JSON snapshot. `restore_governance_store(engine, path)` loads it.
- **Where**: `src/pact/governance/stores/backup.py`
- **Evidence**: `backup_governance_store(engine, "backup.json"); engine2 = GovernanceEngine(config); restore_governance_store(engine2, "backup.json")` -- engine2 has identical state to engine.
- **Dependencies**: 7030, 7033
- **Complexity**: M

#### 7035 — DataFlow Persistence Tests

- **What**: Tests for all persistence stores (SQLite, PostgreSQL, backup/restore): round-trip for all four store types, concurrent access, bounded collection eviction, migration up/down, factory configuration, backup fidelity.
- **Where**: `tests/unit/governance/test_sqlite_stores.py`, `tests/unit/governance/test_postgresql_stores.py`, `tests/unit/governance/test_backup.py`
- **Evidence**: `pytest tests/unit/governance/test_sqlite_stores.py tests/unit/governance/test_backup.py` passes. PostgreSQL tests skip gracefully when unavailable.
- **Dependencies**: 7030-7034
- **Complexity**: L

---

### Milestone 11: Nexus API -- Governance Endpoints

#### 7040 — Governance API Schema Models

- **What**: Pydantic request/response models for all governance endpoints: `CheckAccessRequest/Response`, `ComputeEnvelopeRequest/Response`, `VerifyActionRequest/Response`, `GrantClearanceRequest`, `CreateBridgeRequest`, `CreateKSPRequest`, `OrgSummaryResponse`, `RoleDetailResponse`. Follow the existing `ApiResponse` wrapper pattern.
- **Where**: `src/pact/governance/api/schemas.py`
- **Evidence**: All schema models have `.model_json_schema()` and produce valid OpenAPI definitions.
- **Dependencies**: 7001
- **Complexity**: M

#### 7041 — Core Governance Endpoints

- **What**: Implement REST endpoints: `POST /api/v1/governance/check-access`, `POST /api/v1/governance/compute-envelope`, `POST /api/v1/governance/verify-action`. Each endpoint accepts a JSON request body matching the schema models and delegates to `GovernanceEngine`. Returns structured responses with audit details.
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `curl -X POST /api/v1/governance/check-access -d '{"role_address":"D1-R1-D1-R1-T1-R1","item_id":"...","posture":"shared_planning"}'` returns `{"allowed":true,"reason":"...","audit_details":{...}}`.
- **Dependencies**: 7040, 7001
- **Complexity**: L

#### 7042 — Organization Query Endpoints

- **What**: Implement: `GET /api/v1/governance/org` (org summary: node count, depth, departments), `GET /api/v1/governance/org/nodes?prefix=D1-R1` (prefix query), `GET /api/v1/governance/org/nodes/{address}` (single node detail), `GET /api/v1/governance/org/tree` (full tree structure for visualization).
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `GET /api/v1/governance/org/nodes/D1-R1` returns the President node with address, name, type, children.
- **Dependencies**: 7040, 7001
- **Complexity**: M

#### 7043 — State Management Endpoints

- **What**: Implement: `POST /api/v1/governance/clearances` (grant clearance), `DELETE /api/v1/governance/clearances/{address}` (revoke), `GET /api/v1/governance/clearances/{address}` (get), `POST /api/v1/governance/bridges` (create bridge), `POST /api/v1/governance/ksps` (create KSP), `GET /api/v1/governance/bridges` (list), `GET /api/v1/governance/ksps` (list).
- **Where**: `src/pact/governance/api/endpoints.py`
- **Evidence**: `POST /api/v1/governance/clearances` with a clearance body returns 201. Subsequent `GET /api/v1/governance/clearances/{address}` returns the clearance. `POST /api/v1/governance/check-access` now uses the new clearance.
- **Dependencies**: 7041, 7005
- **Complexity**: M

#### 7044 — Mount Governance API on FastAPI Server

- **What**: Create a FastAPI router for all governance endpoints and mount it on the existing `pact.use.api.server` application. The governance router is conditionally mounted -- it requires a `GovernanceEngine` to be configured. Legacy trust-plane endpoints continue to work alongside governance endpoints.
- **Where**: `src/pact/governance/api/router.py`, `src/pact/use/api/server.py`
- **Evidence**: `python -m pact.use.api.server` starts with both legacy and governance endpoints. `GET /api/v1/governance/org` returns org summary. Health endpoint still works.
- **Dependencies**: 7041-7043
- **Complexity**: M

#### 7045 — Governance WebSocket Events

- **What**: Add WebSocket event types for governance: `governance.access_decision`, `governance.envelope_computed`, `governance.clearance_changed`, `governance.bridge_created`. Push real-time governance events to connected dashboard clients.
- **Where**: `src/pact/governance/api/events.py`, `src/pact/use/api/events.py`
- **Evidence**: WebSocket client connected to `/ws` receives `governance.access_decision` events when `POST /api/v1/governance/check-access` is called.
- **Dependencies**: 7044
- **Complexity**: M

#### 7046 — API Integration Tests

- **What**: Full API integration tests using HTTPX test client: all governance endpoints, error responses (404, 400, 422), concurrent requests, WebSocket events, legacy endpoint backward compatibility.
- **Where**: `tests/integration/test_governance_api.py`
- **Evidence**: `pytest tests/integration/test_governance_api.py` passes. Tests start a test server, call all endpoints, and verify responses.
- **Dependencies**: 7040-7045
- **Complexity**: L

---

### Milestone 12: Frontend Dashboard Update

#### 7050 — Governance API Client (TypeScript)

- **What**: Create TypeScript API client for the governance endpoints. Functions: `checkAccess()`, `computeEnvelope()`, `verifyAction()`, `getOrg()`, `queryNodes()`, `grantClearance()`, `createBridge()`, `listBridges()`, etc. Type-safe with the Pydantic schemas as source of truth.
- **Where**: `apps/web/lib/governance-api.ts`
- **Evidence**: `const decision = await checkAccess({roleAddress: "D1-R1", ...})` returns typed response. Types match the Python schema models.
- **Dependencies**: 7040
- **Complexity**: M

#### 7051 — Organization Tree Visualization Page

- **What**: New dashboard page showing the D/T/R organizational tree. Interactive tree/graph visualization with nodes colored by type (D=blue, T=green, R=yellow). Click a node to see its role details, clearance, and envelope. Uses `GET /api/v1/governance/org/tree`.
- **Where**: `apps/web/app/org/page.tsx` (update existing), `apps/web/app/org/elements/OrgTree.tsx`
- **Evidence**: Page loads, renders the university org tree with all 20+ nodes, clicking a node shows detail panel.
- **Dependencies**: 7050, 7042
- **Complexity**: L

#### 7052 — Governance Dashboard Home Page

- **What**: Update the dashboard home page to show governance overview: org summary (departments, teams, roles), recent access decisions, active bridges and KSPs, clearance summary. Replace the legacy trust-plane widgets with governance-native data.
- **Where**: `apps/web/app/page.tsx`
- **Evidence**: Home page shows org statistics, recent governance decisions, and links to governance sub-pages.
- **Dependencies**: 7050
- **Complexity**: M

#### 7053 — Access Decision Testing Page

- **What**: Interactive page where users can test access decisions: select a role (from org tree dropdown), select or create a knowledge item, choose posture, and click "Check Access". Shows the 5-step decision trace. Useful for org designers validating their configuration.
- **Where**: `apps/web/app/governance/access-test/page.tsx`
- **Evidence**: Page lets user pick role and item, click "Check Access", and see `{allowed: true, reason: "Step 4a: same unit", ...}`.
- **Dependencies**: 7050, 7041
- **Complexity**: M

#### 7054 — Envelope Viewer Page

- **What**: Update the existing envelope page to show the three-layer PACT model: Role Envelope (standing) + Task Envelope (ephemeral) = Effective Envelope. Per-dimension breakdown with visual bars showing utilization. Uses `POST /api/v1/governance/compute-envelope`.
- **Where**: `apps/web/app/envelopes/page.tsx` (update), `apps/web/app/envelopes/[id]/page.tsx` (update)
- **Evidence**: Envelope page shows three-layer decomposition. Selecting a role shows its standing envelope, any active task envelope, and the computed effective envelope.
- **Dependencies**: 7050
- **Complexity**: M

#### 7055 — Frontend Tests

- **What**: Vitest tests for the governance API client, org tree component, access test page, and envelope viewer. Mock API responses.
- **Where**: `apps/web/__tests__/governance/`
- **Evidence**: `cd apps/web && npm test` passes with governance test coverage.
- **Dependencies**: 7050-7054
- **Complexity**: M

---

### Milestone 13: Documentation + Examples

#### 7060 — PACT Framework Quickstart Guide

- **What**: Step-by-step guide: install PACT, define an org in YAML, create a GovernanceEngine, check access, compute envelopes, verify actions. From zero to running in 10 minutes. Include the university example as the tutorial subject.
- **Where**: `docs/quickstart.md` (rewrite)
- **Evidence**: A new developer following the guide can `pip install pact`, define a 3-dept org, and run an access check in <10 minutes. All code examples execute without errors.
- **Dependencies**: 7001, 7002
- **Complexity**: M

#### 7061 — Vertical Integration Guide

- **What**: Guide for building a vertical on PACT: how to `import pact`, define domain-specific D/T/R structure, configure envelopes for domain actions, set up clearances for domain knowledge. Uses a minimal "bookstore" example (simpler than university) to show the pattern. Explains the boundary test: framework code should not change when domain vocabulary changes.
- **Where**: `docs/vertical-guide.md`
- **Evidence**: Guide includes a working bookstore vertical (3 departments, 2 teams) that passes the boundary test. All code examples execute.
- **Dependencies**: 7001
- **Complexity**: L

#### 7062 — API Reference Documentation

- **What**: Auto-generated API reference from the governance endpoint Pydantic schemas. Document all endpoints with request/response examples. Include authentication, error codes, and WebSocket events.
- **Where**: `docs/api.md` (rewrite), `docs/rest-api.md` (rewrite)
- **Evidence**: Every governance endpoint is documented with curl examples. `mkdocs build` produces clean API reference pages.
- **Dependencies**: 7040-7044
- **Complexity**: M

#### 7063 — University Example Polish

- **What**: Polish the university example into a reference-quality demonstration: add YAML config file (in addition to Python), add envelope definitions for all roles, add a README explaining the example, add a runnable script that demonstrates all 14 E2E scenarios with colored output.
- **Where**: `src/pact/examples/university/config.yaml`, `src/pact/examples/university/README.md`, `src/pact/examples/university/demo.py`, `src/pact/examples/university/envelopes.py`
- **Evidence**: `python -m pact.examples.university.demo` runs all scenarios with green/red output. YAML config produces identical org to Python construction.
- **Dependencies**: 7002 (YAML loading)
- **Complexity**: M

#### 7064 — Architecture Documentation Update

- **What**: Update `docs/architecture.md` to reflect the PACT framework architecture: GovernanceEngine as the central facade, three-layer envelope model, D/T/R addressing, clearance independence, the 5-step access algorithm, and integration with EATP trust layer. Include architecture diagrams.
- **Where**: `docs/architecture.md` (rewrite)
- **Evidence**: Architecture doc accurately describes the current implementation with no stale references to care-platform patterns.
- **Dependencies**: 7001
- **Complexity**: M

#### 7065 — Getting Started Guide Update

- **What**: Rewrite `docs/getting-started.md` to orient new users: what PACT is, what it does, how it relates to CARE/EATP/CO, when to use it, and how to get started. Clear distinction between framework (this repo) and verticals (astra, arbor).
- **Where**: `docs/getting-started.md` (rewrite)
- **Evidence**: A reader with no PACT context can understand the purpose and first steps after reading this page.
- **Dependencies**: None
- **Complexity**: S

#### 7066 — Cookbook: Common Patterns

- **What**: Cookbook of common governance patterns: "How to add a new department", "How to create a cross-functional bridge", "How to set up information barriers", "How to define role envelopes", "How to handle posture upgrades", "How to integrate with an AI agent". Each pattern is a self-contained code example.
- **Where**: `docs/cookbook.md` (rewrite)
- **Evidence**: Each cookbook recipe is a runnable Python snippet. `pytest --doctest-modules docs/cookbook.md` passes (or equivalent validation).
- **Dependencies**: 7001
- **Complexity**: M

#### 7067 — README Rewrite

- **What**: Rewrite `README.md` to present PACT as a shippable framework: what it is, installation, quickstart snippet (5 lines to a governance decision), feature overview, link to full docs. Remove all care-platform legacy language.
- **Where**: `README.md`
- **Evidence**: README accurately describes the framework, all links work, the quickstart snippet is copy-pasteable and runs.
- **Dependencies**: 7001, 7060
- **Complexity**: M

---

### Milestone 14: Red Team + Hardening

#### 7070 — Thesis Gap 7: TOCTOU Treatment for Effective Envelopes

- **What**: Address TOCTOU (time-of-check-to-time-of-use) for effective envelopes. If an envelope changes between verification and execution, the action could proceed under stale constraints. Solution: `compute_effective_envelope()` returns a snapshot with a version/timestamp. The execution runtime compares the snapshot version at execution time. If mismatched, re-verify. Add `envelope_version` field to `GovernanceVerdict`.
- **Where**: `src/pact/governance/envelopes.py`, `src/pact/governance/engine.py`, `src/pact/governance/verdict.py`
- **Evidence**: Test: change envelope between verify_action() and execution. Runtime detects stale snapshot and re-verifies. Test with matching snapshot proceeds without re-verification.
- **Dependencies**: 7003
- **Complexity**: L

#### 7071 — Thesis Gap 16: Formal PACT-to-EATP Record Mapping

- **What**: Document and implement the formal mapping between PACT governance operations and EATP trust lineage records. Each PACT governance action maps to a specific EATP record type: `compile_org` -> Genesis Record, `set_role_envelope` -> Delegation Record with constraints, `grant_clearance` -> Capability Attestation, `check_access` -> Audit Anchor. Create `PactEatpMapper` class that produces EATP records from governance operations.
- **Where**: `src/pact/governance/eatp_mapping.py`, `docs/architecture/pact-eatp-mapping.md`
- **Evidence**: `mapper = PactEatpMapper(); eatp_record = mapper.map_clearance_grant(clearance)` produces a valid EATP Capability Attestation. All 10 `PactAuditAction` types have documented EATP record mappings.
- **Dependencies**: 7004
- **Complexity**: L

#### 7072 — Thesis Gap 18: Effective Envelope Snapshot in Audit Anchors

- **What**: Every audit anchor for a governance decision must include the effective envelope that was in force at the time of the decision. This provides forensic evidence of what constraints applied. Add `effective_envelope_snapshot` to `create_pact_audit_details()`.
- **Where**: `src/pact/governance/audit.py`, `src/pact/governance/engine.py`
- **Evidence**: Audit anchor for an access decision includes `effective_envelope_snapshot` with all five constraint dimensions serialized. Test: audit anchor from `engine.check_access()` contains the envelope.
- **Dependencies**: 7004
- **Complexity**: M

#### 7073 — Thesis Gap 19: Multi-Level VERIFY Pattern

- **What**: Implement cascading verification: when a role at depth N verifies an action, the verification cascades up the accountability chain, checking each ancestor's envelope. If any ancestor's envelope would block the action, the most restrictive verdict applies. This is the "multi-level VERIFY" pattern from the thesis.
- **Where**: `src/pact/governance/engine.py`
- **Evidence**: Role at D1-R1-D1-R1-T1-R1 verifies an action. If T1's envelope allows it but D1's (ancestor) envelope blocks it, the result is BLOCKED. Test with multi-level constraints.
- **Dependencies**: 7003
- **Complexity**: M

#### 7074 — Security: NaN/Inf Guard on All Governance Numeric Fields

- **What**: Apply `math.isfinite()` guards on all numeric constraint fields in governance envelopes (max_spend_usd, max_actions_per_day, etc.). Per trust-plane security rules. Ensure that NaN/Inf cannot bypass governance checks.
- **Where**: `src/pact/governance/envelopes.py`, `src/pact/build/config/schema.py`
- **Evidence**: Test: `RoleEnvelope` with `max_spend_usd=float('nan')` raises `ValueError`. Test: `ConstraintEnvelopeConfig` with `max_spend_usd=float('inf')` raises `ValueError`.
- **Dependencies**: None
- **Complexity**: M

#### 7075 — Security: Store Input Validation

- **What**: All governance store methods that accept external input (role*address, org_id, ksp_id, bridge_id) must validate IDs against `^[a-zA-Z0-9*-]+$` pattern. Reject directory traversal, SQL injection, and null bytes. Per trust-plane security rules.
- **Where**: `src/pact/governance/stores/sqlite.py`, `src/pact/governance/stores/postgresql.py`, `src/pact/governance/store.py`
- **Evidence**: Test: `store.load_org("../../etc/passwd")` raises `ValueError`. Test: `store.get_clearance("'; DROP TABLE--")` raises `ValueError`.
- **Dependencies**: 7030
- **Complexity**: M

#### 7076 — Security: Governance API Input Validation

- **What**: All governance API endpoints validate request bodies: address format (D/T/R grammar), posture level (valid enum), classification level (valid enum), numeric constraints (finite), string lengths (bounded). Return 422 with structured error details for invalid input.
- **Where**: `src/pact/governance/api/schemas.py`, `src/pact/governance/api/endpoints.py`
- **Evidence**: Test: `POST /check-access` with `role_address="../../etc/passwd"` returns 422. Test: `POST /verify-action` with `cost=NaN` returns 422.
- **Dependencies**: 7041
- **Complexity**: M

#### 7077 — Red Team Round 1

- **What**: Full adversarial red team of the PACT governance layer: attempt to bypass access controls, forge envelopes, exploit TOCTOU gaps, inject through API, escalate clearance, traverse store paths, poison numeric fields, exhaust memory. Document all findings with severity, reproduction steps, and fixes.
- **Where**: `workspaces/pact/04-validate/rt1-governance-report.md`, `tests/unit/governance/test_redteam.py`
- **Evidence**: Red team report documents all findings. All CRITICAL and HIGH findings have regression tests. All regression tests pass.
- **Dependencies**: 7074-7076
- **Complexity**: XL

#### 7078 — Red Team Remediation

- **What**: Fix all CRITICAL and HIGH findings from RT1. Write regression tests for each fix. Re-run the red team validation to confirm fixes.
- **Where**: Various (depends on findings)
- **Evidence**: All CRITICAL and HIGH findings resolved. Regression tests pass. Re-validation confirms no regressions.
- **Dependencies**: 7077
- **Complexity**: L (depends on findings)

---

### Milestone 15: Ship Readiness

#### 7080 — Package Configuration Update

- **What**: Update `pyproject.toml` for the governance-complete PACT framework: update description, verify all dependencies, ensure `pact.governance` is included in the package, update classifiers to "Beta", verify entry points. Ensure `pact.governance` exports are in `src/pact/__init__.py`.
- **Where**: `pyproject.toml`, `src/pact/__init__.py`, `src/pact/governance/__init__.py`
- **Evidence**: `pip install -e .` installs cleanly. `from pact.governance import GovernanceEngine` works. `python -c "import pact; print(pact.__version__)"` prints the correct version.
- **Dependencies**: 7001
- **Complexity**: S

#### 7081 — Version Bump to 0.2.0

- **What**: Bump version to 0.2.0 (governance layer is a significant feature addition). Update `pyproject.toml` and `src/pact/__init__.py` atomically. Update all documentation version references.
- **Where**: `pyproject.toml`, `src/pact/__init__.py`, `README.md`, `docs/`
- **Evidence**: `python -c "import pact; print(pact.__version__)"` prints `0.2.0`. All docs reference 0.2.0.
- **Dependencies**: All milestones 7-14
- **Complexity**: S

#### 7082 — CHANGELOG Creation

- **What**: Create `CHANGELOG.md` documenting all changes from 0.1.0 to 0.2.0: new governance layer, GovernanceEngine, three-layer envelopes, D/T/R addressing, 5-step access algorithm, Kaizen integration, DataFlow persistence, Nexus API, dashboard updates. Follow Keep a Changelog format.
- **Where**: `CHANGELOG.md`
- **Evidence**: Changelog accurately describes all features, fixes, and breaking changes.
- **Dependencies**: 7081
- **Complexity**: S

#### 7083 — CI Pipeline Hardening

- **What**: Ensure CI runs: unit tests, integration tests (governance + API), ruff lint, mypy type check, security scanning (detect-secrets), package build verification, documentation build. All must pass on PR.
- **Where**: `.github/workflows/ci.yml`
- **Evidence**: CI pipeline runs all checks. A PR with a failing governance test is blocked from merge.
- **Dependencies**: None (can be done in parallel)
- **Complexity**: M

#### 7084 — Legacy Cleanup: Foundation Example

- **What**: Evaluate `src/pact/examples/foundation/` (legacy care-platform). If it uses domain-specific vocabulary that violates the boundary test, either refactor to be domain-agnostic or move to an `archive/` directory. The university example is the canonical example; the foundation example should not confuse users.
- **Where**: `src/pact/examples/foundation/`
- **Evidence**: Either: (a) foundation example passes boundary test and has a clear README explaining its purpose, or (b) it is moved to `archive/legacy-foundation/` with a note explaining why.
- **Dependencies**: None
- **Complexity**: M

#### 7085 — Legacy Cleanup: API Endpoint Consolidation

- **What**: Audit all endpoints in `src/pact/use/api/endpoints.py`. Map each legacy endpoint to its governance equivalent. Add deprecation headers to legacy endpoints that are superseded by governance endpoints. Document the migration path for consumers.
- **Where**: `src/pact/use/api/endpoints.py`, `docs/migration/legacy-api.md`
- **Evidence**: Legacy endpoints emit deprecation warnings. Documentation maps each legacy endpoint to its governance replacement.
- **Dependencies**: 7044
- **Complexity**: M

#### 7086 — PyPI Publishing Workflow

- **What**: Ensure the publish workflow produces a clean PyPI package: `pact` with governance, trust, build, use, and examples sub-packages. Verify the package installs cleanly in a fresh virtual environment and all imports work. Test with `pip install pact` from the built wheel.
- **Where**: `.github/workflows/publish.yml`
- **Evidence**: `pip install dist/pact-0.2.0-py3-none-any.whl` in a clean venv. `from pact.governance import GovernanceEngine` works. `python -m pact.examples.university.demo` runs successfully.
- **Dependencies**: 7081
- **Complexity**: M

#### 7087 — Final Validation: Full Test Suite

- **What**: Run the complete test suite (unit + integration + governance + E2E scenarios) and verify all tests pass. Verify test coverage is >85% for governance package. Verify no ruff or mypy errors. This is the final gate before release.
- **Where**: All test directories
- **Evidence**: `pytest --cov=pact.governance --cov-report=term-missing` shows >85% coverage. `ruff check src/pact/governance/` clean. `mypy src/pact/governance/` clean. Zero test failures.
- **Dependencies**: All previous milestones
- **Complexity**: M

---

## Summary

| Milestone | Todos        | Description                | Est. Days      |
| --------- | ------------ | -------------------------- | -------------- |
| M7        | 7001-7006    | GovernanceEngine Facade    | 5-7            |
| M8        | 7010-7014    | Envelope Unification       | 4-5            |
| M9        | 7020-7025    | PactGovernedAgent + Kaizen | 5-7            |
| M10       | 7030-7035    | DataFlow Persistence       | 5-7            |
| M11       | 7040-7046    | Nexus API                  | 4-6            |
| M12       | 7050-7055    | Frontend Dashboard         | 4-5            |
| M13       | 7060-7067    | Documentation + Examples   | 4-5            |
| M14       | 7070-7078    | Red Team + Hardening       | 5-7            |
| M15       | 7080-7087    | Ship Readiness             | 3-4            |
| **Total** | **48 todos** |                            | **39-53 days** |

## Critical Path

```
M7 (Engine) -> M8 (Unification) -> M9 (Agents) -> M14 (Red Team) -> M15 (Ship)
                                 -> M10 (Persistence) -> M11 (API) -> M12 (Frontend)
                                 -> M13 (Docs)
```

M7 is the foundation. Everything depends on the GovernanceEngine facade.

M8, M9, M10 can proceed in parallel after M7.

M11 depends on M7 and benefits from M10.

M12 depends on M11.

M13 depends on M7 but can start early.

M14 (red team) should come after M7-M11 are stable.

M15 (ship) is the final milestone after everything else.
