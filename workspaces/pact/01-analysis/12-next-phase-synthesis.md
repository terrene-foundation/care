# Next Phase Synthesis: Unified Recommendation

**Date**: 2026-03-16
**Agents**: deep-analyst, requirements-analyst, value-auditor, framework-advisor
**Decision**: Sequence all four options as a unified roadmap

---

## The Verdict

All four agents converge on the same insight: **the platform has enough substance to be credible. What it lacks is accessibility and polish.**

The PACT has 101 Python source files, 17 dashboard pages, 3,070 tests, and a complete governance architecture. But it only runs on one developer's machine. No one else can evaluate, install, or deploy it. The ShadowEnforcer page — the showcase of trust governance — displays mock data with wrong agent names. The CI pipeline may be checking the wrong directory.

**The path forward is not more features. It is deployment, consistency, and proof.**

---

## Recommended Sequence

### Phase A: Polish & Deploy (Options D + B combined)

Fix the known issues and make the platform deployable in one combined push. These are inseparable — fixing a broken demo that nobody can access is pointless, and deploying a broken demo is worse.

**Estimated effort**: 2-3 weeks
**Tasks**: ~34 (15 Small, 16 Medium, 0 Large)
**Delivers**: A platform anyone can evaluate at a URL, install via pip, or run via Docker Compose

### Phase B: Organization Builder Capstone (Option A)

With a deployed, consistent platform, complete the Org Builder as the strategic differentiator. This is the feature that transforms CARE from "a collection of governance libraries" into "a platform that generates governed organizations."

**Estimated effort**: 3-4 weeks
**Tasks**: ~20 (5 Small, 9 Medium, 3 Large)
**Delivers**: Any organization can define its structure and auto-generate a fully governed PACT

### Phase C: DM Team Vertical (Option C)

With the Org Builder capable of provisioning teams and the platform deployed where people can see it, launch the DM team as the first live proof of governed agents.

**Estimated effort**: 4-6 weeks
**Tasks**: ~15 (4 Small, 8 Medium, 1 Large)
**Delivers**: Real agents doing real work under real governance — the ultimate proof

---

## Why This Order

| Question        | Answer                                                                                                                                                                             |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Why D before A? | A demo with broken data destroys the credibility that working features built. Fix first, build second.                                                                             |
| Why B before A? | The Org Builder is an internal capability. Deployment is external credibility. Pre-incorporation, external credibility matters more.                                               |
| Why A before C? | The Org Builder provisions agent teams. The DM vertical IS an agent team. Build the factory before the first product.                                                              |
| Why C last?     | It's the highest-risk, highest-cost option. It requires working deployment (B), fixed data (D), and team provisioning (A). Starting it before the others creates compounding risk. |

---

## Key Architecture Decisions

1. **Keep FastAPI, don't migrate to Nexus** — The existing API layer has 10 rounds of red team hardening. Nexus migration is a lateral move with regression risk.

2. **Adopt DataFlow in Phase B for org persistence** — The first real Kailash framework adoption. OrgDefinition persistence through DataFlow's auto-generated nodes.

3. **Adopt Kaizen TrustedAgent in Phase C** — The second framework adoption. DM agents as Kaizen TrustedAgent subclasses with CARE constraint verification as pre-execution hooks.

4. **AsyncLocalRuntime in Docker** — Mandatory per deployment rules. Set up in Phase A even before workflows exist.

5. **Start DM agents in dry-run mode** — Avoid LLM cost risk by proving governance works with structured outputs before connecting real LLM backends.

---

## Total Scope

| Phase              | Tasks   | Effort         | Cumulative |
| ------------------ | ------- | -------------- | ---------- |
| A: Polish & Deploy | ~34     | 2-3 weeks      | 2-3 weeks  |
| B: Org Builder     | ~20     | 3-4 weeks      | 5-7 weeks  |
| C: DM Vertical     | ~15     | 4-6 weeks      | 9-13 weeks |
| **Total**          | **~69** | **9-13 weeks** | —          |

---

## Risk Register (Cross-Cutting)

| Risk                                               | Impact   | Phase | Mitigation                                      |
| -------------------------------------------------- | -------- | ----- | ----------------------------------------------- |
| CI paths broken — lint/type checks may not run     | Critical | A     | Fix immediately (30 minutes)                    |
| PyPI `pact` name taken                    | Major    | A     | Check availability; fallback to `terrene-pact`  |
| ShadowEnforcer mock data destroys demo credibility | High     | A     | Wire real backend endpoints                     |
| LLM cost runaway with 5 DM agents                  | Critical | C     | Start with dry-run mode, then calibrate budgets |
| Approval flood (SUPERVISED = every action held)    | Major    | C     | Start with 1-2 agents, measure review rate      |
| Foundation dog-fooding reveals structural issues   | Medium   | B     | Desirable — that's the point                    |
