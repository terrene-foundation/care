# RT19: Entry Points, Boundaries, and Alternative Development Paths

**Date**: 2026-03-21
**Question**: Given PACT + Kailash (Core, DataFlow, Nexus, Kaizen) + EATP, who starts where?

---

## The Confusion

A developer sees 6 packages:

| Package            | What It Does                                    |
| ------------------ | ----------------------------------------------- |
| `kailash`          | Workflow orchestration (140+ nodes, runtime)    |
| `kailash-dataflow` | Zero-config database (models → CRUD nodes)      |
| `kailash-nexus`    | Multi-channel deployment (API + CLI + MCP)      |
| `kailash-kaizen`   | AI agent framework (BaseAgent, signatures)      |
| `eatp`             | Trust protocol (trust chains, verification)     |
| `pact`             | Governance framework (D/T/R, envelopes, access) |

Their question: **"I want to build an AI-powered application with governed agents. Where do I start?"**

The answer depends on what they're building and their role.

---

## Three Entry Points (Three Doors)

### Door 1: "I'm building governed agents" → Start with PACT

**Who**: A team building a regulated application where organizational governance is a first-class requirement (financial services, healthcare, government, legal).

**Entry point**: `pip install pact`

**What they do**:

1. Define their org in D/T/R grammar (PACT)
2. Configure envelopes, clearances, barriers (PACT)
3. Write domain tools as pure functions (their code)
4. Wrap tools in governed agents (PACT + Kaizen)
5. Deploy as API (PACT + Nexus)
6. Persist governance state (PACT + DataFlow)

**PACT is the starting framework. Kailash is the execution substrate underneath.**

```python
# Step 1: Define the organization (PACT)
from pact.governance import compile_org, RoleDefinition, GovernanceEngine
org = compile_org(my_org_definition)
engine = GovernanceEngine(org, stores)

# Step 2: Create a governed agent (PACT + Kaizen)
from kailash_kaizen import BaseAgent
from pact.integration.kaizen import PactGovernedAgent

class TradingAgent(PactGovernedAgent):
    """Every tool call is checked against the agent's effective envelope."""
    role_address = "D1-R1-D3-R1-T1-R1"

    @tool
    def execute_trade(self, instrument: str, qty: int) -> TradeResult:
        # Pure domain logic — PACT handles governance
        return broker.submit(instrument, qty)

# Step 3: Deploy (Nexus)
from kailash_nexus import Platform
platform = Platform()
platform.register_agent(TradingAgent, governance_engine=engine)
platform.serve()  # API + CLI + MCP simultaneously
```

**The boundary**: PACT defines WHAT agents can do. Kaizen defines HOW agents work. Nexus defines WHERE agents are accessible. DataFlow defines HOW governance state persists.

---

### Door 2: "I'm building AI agents, governance is secondary" → Start with Kaizen

**Who**: A team building AI agents where governance is important but not the primary architectural driver (internal tools, content generation, data analysis, automation).

**Entry point**: `pip install kailash-kaizen`

**What they do**:

1. Build agents with Kaizen (BaseAgent, signatures, tools)
2. Add PACT governance as a constraint layer AFTER the agents work
3. The governance layer wraps the agent execution, not the other way around

```python
# Step 1: Build agents (Kaizen — no PACT yet)
from kailash_kaizen import BaseAgent

class ResearchAgent(BaseAgent):
    @tool
    def search_documents(self, query: str) -> list[Document]:
        return vector_store.search(query)

# Step 2: Add governance LATER (PACT wraps Kaizen)
from pact.integration.kaizen import govern_agent

governed_research = govern_agent(
    agent=ResearchAgent(),
    role_address="D1-R1-D2-R1-T1-R1",
    engine=governance_engine,
)
# Now every tool call is checked against the envelope
```

**The boundary**: Kaizen agents work without PACT (ungoverned). PACT is a governance overlay that constrains them. The developer can add governance incrementally — start ungoverned, add PACT when compliance requires it.

**This is the migration path** for existing Kaizen applications.

---

### Door 3: "I'm building an API/service, agents are one component" → Start with Nexus

**Who**: A team building a multi-channel service where some endpoints use AI agents and some don't. The service needs governance but is not agent-first.

**Entry point**: `pip install kailash-nexus`

**What they do**:

1. Build their service with Nexus (API + CLI + MCP)
2. Some workflows use Kaizen agents, some use plain Kailash workflows
3. PACT governance is attached as middleware on the Nexus platform

```python
# Step 1: Build the service (Nexus)
from kailash_nexus import Platform, workflow_route

platform = Platform()

@workflow_route("/api/reports")
def generate_report(request):
    # Plain Kailash workflow — no agent
    return core_sdk_workflow.execute(request.data)

@workflow_route("/api/trade")
def execute_trade(request):
    # Kaizen agent — governed by PACT
    return trading_agent.run(request.data)

# Step 2: Add PACT governance as platform middleware
from pact.integration.nexus import PactMiddleware

platform.add_middleware(PactMiddleware(governance_engine))
# Now ALL routes are governed — the middleware checks envelopes
```

**The boundary**: Nexus is the deployment shell. PACT is the governance middleware. Kaizen is the agent engine. Core SDK is the workflow engine. DataFlow is the persistence engine. Each is pluggable.

---

## The Decision Matrix

| I want to...                               | Start with   | Add                                        | Why                                         |
| ------------------------------------------ | ------------ | ------------------------------------------ | ------------------------------------------- |
| Build a regulated org with AI agents       | **PACT**     | + Kaizen + Nexus                           | Governance is structural, not bolted on     |
| Build AI agents, add compliance later      | **Kaizen**   | + PACT (governance overlay)                | Agents first, governance second             |
| Build a multi-channel service with some AI | **Nexus**    | + Kaizen + PACT (middleware)               | Service first, agents are one component     |
| Build a data pipeline with governance      | **DataFlow** | + PACT (access checks on data ops)         | Data first, governance on access            |
| Build a complex orchestration              | **Core SDK** | + PACT (envelope checks per workflow step) | Workflow first, governance per step         |
| Build a trust-verified system (no agents)  | **EATP**     | (standalone)                               | Cryptographic trust only, no org governance |

---

## Detailed Boundaries: What Lives Where

### PACT (governance framework)

**PACT owns**: D/T/R grammar, positional addressing, access enforcement algorithm, 3-layer envelope model, knowledge clearance, information barriers (KSPs), cross-functional bridges, monotonic tightening, degenerate envelope detection, governance audit subtypes, governance store protocols

**PACT does NOT own**: Agent execution, LLM calls, tool invocation, API routing, database schemas, workflow orchestration, UI rendering

**PACT provides to Kailash**: `GovernanceEngine` that any Kailash component can query — "can this role do this action?" "what's this role's effective envelope?" "is this knowledge item accessible?"

### Kaizen (agent framework)

**Kaizen owns**: Agent lifecycle (create, run, stop), tool registration, signature-based programming, multi-agent coordination, LLM backend abstraction, agent memory, agent-to-agent communication

**Kaizen does NOT own**: What the agent is allowed to do — that's PACT's envelope. Who the agent reports to — that's PACT's D/T/R tree. What data the agent can see — that's PACT's clearance/access.

**Kaizen provides to PACT**: The execution surface where governance is enforced. PACT says "this tool call is HELD" → Kaizen pauses the agent and routes to the approval queue.

### Nexus (deployment framework)

**Nexus owns**: API endpoints, CLI commands, MCP tools, session management, health monitoring, multi-channel deployment

**Nexus does NOT own**: Business logic, governance rules, agent behavior, data access

**Nexus provides to PACT**: The deployment surface. PACT governance endpoints (compile org, check access, manage envelopes) are deployed via Nexus as API + CLI + MCP simultaneously.

### DataFlow (persistence framework)

**DataFlow owns**: Database models, CRUD operations, migrations, query building, multi-tenancy

**DataFlow does NOT own**: What data means, who can access it, how it's classified

**DataFlow provides to PACT**: Persistent store backends. The governance store protocols (OrgStore, EnvelopeStore, ClearanceStore, AccessPolicyStore) get DataFlow model implementations that auto-generate CRUD operations.

### Core SDK (workflow framework)

**Core SDK owns**: Workflow definition, node execution, connections, runtime orchestration, cyclic patterns

**Core SDK does NOT own**: Agent reasoning, governance rules, API deployment

**Core SDK provides to PACT**: Governance process workflows. Clearance review cycles, emergency bypass approval chains, org restructure migration — these are orchestrated as Core SDK workflows with governance checks at each step.

### EATP (trust protocol)

**EATP owns**: Genesis records, delegation records, constraint envelopes (the cryptographic kind), capability attestations, audit anchors, trust verification (QUICK/STANDARD/FULL), cascade revocation, reasoning traces, Ed25519 signing, SHA-256 hash chains

**EATP does NOT own**: Organizational structure, access decisions, envelope composition, clearance governance

**EATP provides to PACT**: The cryptographic backbone. Every PACT governance action (envelope created, clearance granted, barrier enforced) creates an EATP record. The trust chain is what makes governance auditable and tamper-evident.

---

## Integration Patterns (How They Wire Together)

### Pattern A: PACT-first (regulated vertical)

```
Developer → PACT (org, envelopes, clearances)
                → Kaizen (agents bound to roles)
                    → Core SDK (domain workflows)
                        → DataFlow (persistence)
                → Nexus (API deployment)
                → EATP (audit trail)
```

### Pattern B: Kaizen-first (agent-focused)

```
Developer → Kaizen (build agents)
                → PACT (add governance overlay)
                    → EATP (audit)
                → Nexus (deploy)
                → DataFlow (persist)
```

### Pattern C: Nexus-first (service-focused)

```
Developer → Nexus (define API surface)
                → Kaizen (some routes use agents)
                    → PACT (governance middleware)
                → Core SDK (some routes use workflows)
                    → PACT (envelope checks per step)
                → DataFlow (all routes use persistence)
```

### Pattern D: Gateway/Proxy (attach to existing system)

```
Existing System → PACT Gateway (checks access before forwarding)
                    → EATP (audit everything that passes through)
                    → existing API (unchanged)
```

This is the "attach PACT to anything" pattern. A developer builds a PACT-aware proxy/gateway that sits in front of any existing service. Every request is checked against `can_access()` before being forwarded. The existing system doesn't change — PACT is a governance filter.

---

## What PACT Needs to Provide for Each Pattern

| Pattern          | PACT Must Provide                                                     | Status                     |
| ---------------- | --------------------------------------------------------------------- | -------------------------- |
| A (PACT-first)   | GovernanceEngine, Kaizen middleware, Nexus endpoints, DataFlow stores | GAP-1, GAP-4, GAP-5, GAP-7 |
| B (Kaizen-first) | `govern_agent()` wrapper, incremental adoption (shadow mode)          | GAP-5, new                 |
| C (Nexus-first)  | `PactMiddleware` for Nexus platforms                                  | New                        |
| D (Gateway)      | Standalone `pact-gateway` that proxies HTTP with access checks        | New concept                |

---

## The "Attach to Anything" Question

You asked: "can we build anything with the foundational stacks and attach it to PACT?"

**Yes — and there are two directions:**

### Direction 1: PACT wraps your agent/service (governance first)

```python
# PACT wraps a Kaizen agent
governed_agent = PactGovernedAgent(my_kaizen_agent, role_address, engine)

# PACT wraps a Nexus platform
governed_platform = PactMiddleware(my_nexus_platform, engine)

# PACT wraps a plain function
governed_fn = pact_check(my_function, role_address, engine)
```

### Direction 2: Your agent/service queries PACT (governance as service)

```python
# Agent queries PACT before acting
decision = governance_engine.check_access(my_role, target_data, my_posture)
if decision.allowed:
    result = my_tool(target_data)
else:
    log.info(f"Blocked: {decision.reason}")

# Gateway queries PACT per request
@app.middleware
async def pact_gateway(request, call_next):
    decision = engine.check_access(request.role, request.resource, request.posture)
    if not decision.allowed:
        return Response(403, body=decision.reason)
    return await call_next(request)
```

Both directions work. The first (PACT wraps) is cleaner for new applications. The second (query PACT) is better for attaching governance to existing systems.

---

## Summary: The Rule of Thumb

- **If governance is a requirement from day one** → Start with PACT (Door 1)
- **If you're building agents and need governance later** → Start with Kaizen (Door 2)
- **If you're building a service with some AI** → Start with Nexus (Door 3)
- **If you have an existing system** → Attach PACT as gateway/middleware (Direction 2)

In ALL cases, the Kailash stack is the execution substrate. PACT is the governance layer that constrains what the execution substrate does. EATP is the cryptographic proof that the constraints were respected.
