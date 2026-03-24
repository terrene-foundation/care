# RT18: Development Lifecycle Red Team Report

**Date**: 2026-03-21
**Scope**: How PACT changes development at three scales + framework completeness

---

## The Core Finding

**The governance primitives are solid. The integration layer is the gap.**

The `pact.governance` package (488 tests, ~2,800 LOC) correctly implements the PACT thesis. But the governance layer and the execution layer are two disconnected systems that were built at different times. The old `pact.trust/` + `pact.use/` layer predates the governance layer and doesn't use it. There are two parallel envelope systems that don't talk to each other.

This is the single blocker preventing verticals from using PACT in production.

---

## How PACT Changes Development at Three Scales

### Scale 1: Single Feature

**Traditional** (7 steps, governance scattered):
Write service → add endpoint → add RBAC → add budget check → add audit → add compliance → add data guard

**PACT-native** (3 steps, governance structural):
Write pure domain function → register as agent tool → governance already configured in org structure

The developer writes ZERO permission code, ZERO audit code, ZERO approval workflow code. Those emerge from the organizational structure. When a feature needs cross-boundary access, the developer escalates to the governance architect — they cannot create ad-hoc permissions.

### Scale 2: Single Vertical Application

A vertical (Astra, Arbor) creates 5 things:

1. `org.py` — D/T/R structure (the skeleton)
2. `clearances.py` — Per-role clearance with compartments
3. `barriers.py` — KSPs and bridges
4. `tools/` — Pure domain functions
5. `agents/` — Agent configs binding tools to roles

Everything else — access enforcement, envelope composition, audit trails, gradient classification — is PACT.

**Current gap**: No `GovernanceEngine` facade to wire these together. The vertical must manually compose 6+ objects for every access check.

### Scale 3: Ecosystem

- **Shared**: D/T/R grammar, access algorithm, envelope model, clearance framework, store protocols
- **Vertical-specific**: Domain org charts, domain clearance mappings, domain tools, domain API
- **Ambiguous**: Store backends, agent runtime, dashboard shell, CLI tools, event system

Cross-vertical sharing works at the structural level (governance templates like "information barrier pattern") but not at the semantic level (Astra's CONFIDENTIAL ≠ Arbor's CONFIDENTIAL in domain meaning).

No cross-org federation exists. Two PACT-governed organizations cannot interact.

---

## 12 Gaps Identified (Consolidated from both reports)

### MUST-HAVE (4 gaps — blocks vertical development)

| #     | Gap                                                                                                   | Impact                                         | Kailash Integration                                       |
| ----- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------- |
| GAP-1 | **GovernanceEngine facade** — no single entry point; 6+ objects wired manually                        | Every vertical reimplements the same wiring    | Kaizen middleware pattern                                 |
| GAP-2 | **Gradient integration** — can_access() is binary ALLOW/DENY; thesis requires 4 zones                 | Governance is approve/reject, not graduated    | Connect to existing GradientEngine                        |
| GAP-3 | **Envelope unification** — two parallel systems (governance RoleEnvelope vs trust ConstraintEnvelope) | Verticals don't know which to use              | governance.compute_effective_envelope() becomes canonical |
| GAP-4 | **Governance management API** — no CRUD for orgs, envelopes, clearances, KSPs, bridges                | Supervisors need developer access to configure | Nexus multi-channel endpoints                             |

### SHOULD-HAVE (4 gaps — verticals will build themselves)

| #     | Gap                                                              | Kailash Integration          |
| ----- | ---------------------------------------------------------------- | ---------------------------- |
| GAP-5 | **Agent middleware** — `@pact_check` decorator for tool wrapping | Kaizen BaseAgent integration |
| GAP-6 | **Event/notification system** — governance decisions are silent  | Core SDK workflow triggers   |
| GAP-7 | **Persistent stores** — only memory implementations              | DataFlow models              |
| GAP-8 | **Emergency bypass** — thesis Section 9 not implemented          | Core SDK workflow with timer |

### NICE-TO-HAVE (4 gaps — ecosystem maturity)

| #      | Gap                                  |
| ------ | ------------------------------------ |
| GAP-9  | YAML/JSON org definition format      |
| GAP-10 | Org visualization / address explorer |
| GAP-11 | Clearance review workflow            |
| GAP-12 | Multi-org federation support         |

---

## What Happens to Old Artifacts

| Artifact                           | Decision                                              | Reason                                                           |
| ---------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------- |
| `src/pact/governance/`             | **KEEP — this IS the framework**                      | New, clean, 488 tests                                            |
| `src/pact/build/`                  | **KEEP**                                              | Config schema, org builder                                       |
| `src/pact/trust/`                  | **BRIDGE to governance, then deprecate old envelope** | Trust primitives are valuable; old envelope system is superseded |
| `src/pact/use/api/`                | **Replace with Nexus**                                | Hand-rolled FastAPI → Nexus multi-channel                        |
| `src/pact/use/execution/`          | **Rewire to governance**                              | Runtime is valuable but uses old types                           |
| `src/pact/use/execution/backends/` | **Keep as optional extras**                           | `pact[anthropic]`, `pact[openai]`                                |
| `apps/web/`                        | **Extract as `pact-dashboard` template**              | Dashboard is application, not framework                          |
| `apps/mobile/`                     | **Remove**                                            | Incomplete, not framework concern                                |
| `src/pact/examples/`               | **Keep and expand**                                   | University example is best onboarding material                   |

---

## Kailash Stack Integration Plan

```
┌─────────────────────────────────────────────┐
│  Vertical (Astra, Arbor)                    │  Domain: org.py, tools/, agents/
├─────────────────────────────────────────────┤
│  GovernanceEngine (GAP-1)                   │  Facade: check_access(), get_envelope()
│  + @pact_check middleware (GAP-5)           │  Agent wrapping: Kaizen BaseAgent
├─────────────────────────────────────────────┤
│  pact.governance                            │  D/T/R grammar, access, envelopes,
│  (what exists today)                        │  clearance, barriers, audit
├─────────────────────────────────────────────┤
│  pact.trust                                 │  EATP bridge, constraint evaluation,
│  (unified envelope — GAP-3)                 │  GradientEngine (GAP-2), audit chains
├─────────────────────────────────────────────┤
│  Kailash Kaizen     │  Kailash Nexus        │  Agent runtime with │ Governance API
│  (agent execution)  │  (API + CLI + MCP)    │  envelope awareness │ (GAP-4)
├─────────────────────┼───────────────────────┤
│  Kailash DataFlow   │  Kailash Core SDK     │  Governance stores  │ Governance
│  (GAP-7)            │  (GAP-8)              │  (persistent)       │ workflows
├─────────────────────────────────────────────┤
│  EATP SDK                                   │  Cryptographic trust verification
└─────────────────────────────────────────────┘
```

---

## Recommended Next Phase

**Phase 7: Integration Layer** (unblocks verticals)

1. GAP-3: Envelope unification → governance envelope becomes canonical
2. GAP-1: GovernanceEngine facade → single entry point for verticals
3. GAP-2: Gradient integration → 4-zone graduated governance
4. GAP-5: Agent middleware → `@pact_check` for Kaizen

**Phase 8: Platform Layer** (production readiness)

5. GAP-4: Nexus-based governance API → supervisor configuration
6. GAP-7: DataFlow persistence → production stores
7. GAP-6: Event system → governance observability
8. GAP-8: Emergency bypass → compliance readiness

After Phase 7: Astra and Arbor can `pip install pact` and build.
After Phase 8: Production deployment with full Kailash stack.
