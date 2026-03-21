# RT17: Framework Completeness Red Team Report

**Date**: 2026-03-21
**Scope**: Can a vertical (Astra, Arbor) build on PACT without writing governance code?

---

## Verdict: Governance primitives are solid. Integration layer is missing.

The `pact.governance` package (488 tests, 2,800 LOC) correctly implements the PACT thesis: D/T/R grammar, positional addressing, 5-step access enforcement, 3-layer envelopes, clearance with compartments, information barriers. A vertical CAN define a complete org structure today.

**But**: the governance layer and the execution layer (`pact.use/`, `pact.trust/`) are two disconnected systems. The execution runtime doesn't use the governance layer. There are two parallel envelope systems that don't talk to each other. There's no single entry point for verticals.

---

## 4 MUST-HAVE Gaps (blocks vertical development)

### GAP-1: GovernanceEngine facade (the missing integration point)

No single entry point composes org + stores + clearances + envelopes into a ready-to-use engine. A vertical must manually wire 6+ objects for every access check.

**Need**: `GovernanceEngine` class exposing:

- `check_access(role_address, item, posture) -> AccessDecision`
- `get_effective_envelope(role_address) -> ConstraintEnvelopeConfig`
- `check_action(role_address, action) -> GradientResult`

### GAP-2: Verification gradient integration

`can_access()` returns binary ALLOW/DENY. The thesis specifies 4 zones (AUTO_APPROVED/FLAGGED/HELD/BLOCKED). The `GradientEngine` exists in `pact.trust.constraint.gradient` but is disconnected from governance.

**Need**: `check_action()` that evaluates against the effective envelope and returns the gradient zone.

### GAP-3: Envelope unification

Two parallel envelope systems:

- `pact.governance.envelopes.RoleEnvelope` — 3-layer PACT model, monotonic tightening
- `pact.trust.constraint.envelope.ConstraintEnvelope` — execution-layer evaluation

Neither references the other. Verticals don't know which to use.

**Need**: Bridge or unification. Governance `compute_effective_envelope()` should be canonical; execution layer should consume its output.

### GAP-4: Governance management API

No REST endpoints for creating/modifying orgs, envelopes, clearances, KSPs, bridges. A supervisor cannot configure governance without writing Python.

**Need**: CRUD endpoints via Kailash Nexus (replacing hand-rolled FastAPI).

---

## 4 SHOULD-HAVE Gaps

| #     | Gap                          | What's Needed                                                       |
| ----- | ---------------------------- | ------------------------------------------------------------------- |
| GAP-5 | Agent framework middleware   | `@pact_check(engine, role_address)` decorator for tool wrapping     |
| GAP-6 | Event/notification system    | `engine.on("access_denied", callback)` for governance observability |
| GAP-7 | Persistent stores (DataFlow) | SQLite/PostgreSQL governance stores via Kailash DataFlow            |
| GAP-8 | Emergency bypass             | Time-bounded envelope widening per thesis Section 9                 |

## 4 NICE-TO-HAVE Gaps

| #      | Gap                                  |
| ------ | ------------------------------------ |
| GAP-9  | YAML/JSON org definition format      |
| GAP-10 | Org visualization / address explorer |
| GAP-11 | Clearance review workflow            |
| GAP-12 | Multi-org support                    |

---

## Kailash Integration Map

| Kailash Framework | Resolves Gap  | How                                                                                  |
| ----------------- | ------------- | ------------------------------------------------------------------------------------ |
| **Kaizen**        | GAP-1, GAP-5  | GovernanceEngine as Kaizen middleware; `@pact_check` decorator wraps BaseAgent tools |
| **Nexus**         | GAP-4         | Governance CRUD as Nexus multi-channel endpoints (API + CLI + MCP)                   |
| **DataFlow**      | GAP-7         | Governance stores as DataFlow models with auto-generated CRUD nodes                  |
| **Core SDK**      | GAP-8, GAP-11 | Emergency bypass and clearance review as orchestrated workflows                      |

---

## What Happens to Existing `use/` Layer

| Component                        | Verdict                           | Reason                                                                        |
| -------------------------------- | --------------------------------- | ----------------------------------------------------------------------------- |
| `use/api/server.py`              | **Replace with Nexus**            | Hand-rolled FastAPI; Nexus provides multi-channel for free                    |
| `use/api/endpoints.py`           | **Evolve**                        | Dashboard endpoints are valuable; wire to governance stores                   |
| `use/execution/runtime.py`       | **Bridge to governance**          | Wire `compute_effective_envelope()` as the canonical envelope source          |
| `use/execution/kaizen_bridge.py` | **Evolve**                        | Add governance-layer checks before/after Kaizen agent actions                 |
| `use/execution/backends/`        | **Keep as optional**              | LLM backends are vertical concern; package as `pact[anthropic]`               |
| `use/execution/approval.py`      | **Bridge to governance**          | Wire HELD gradient results to the approval queue                              |
| `apps/web/`                      | **Extract to reference template** | Dashboard is application, not framework; provide as `pact-dashboard` template |
| `apps/mobile/`                   | **Remove**                        | Never completed; not framework concern                                        |

---

## Recommended Build Order

1. **GAP-3** Envelope unification (unblock everything else)
2. **GAP-1** GovernanceEngine facade (the single highest-value deliverable)
3. **GAP-2** Gradient integration (makes governance graduated, not binary)
4. **GAP-5** Agent middleware (standardize Kaizen integration)
5. **GAP-4** Nexus-based governance API
6. **GAP-7** DataFlow persistence
7. **GAP-6** Event system
8. **GAP-8** Emergency bypass

After GAP-1 through GAP-3: verticals can `pip install pact` and write only config + domain logic.
After GAP-4 through GAP-5: supervisors manage governance through UI, agents are auto-constrained.
