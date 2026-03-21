# PACT Framework: Deep Analysis Synthesis

**Date**: 2026-03-21
**Phase**: 01-analysis (fresh analysis for the PACT framework pivot)
**Inputs**: 5 parallel research agents (deep-analyst, requirements-analyst, coc-expert, market-researcher, sdk-navigator), 3 Astra briefs (requirements, gap analysis, paradigm shift)

---

## The Core Insight: Structure IS Architecture

PACT is not "add governance to an application." PACT replaces how applications are architected.

When you define `D1-R1-D2 (Advisory) ← barrier → D1-R1-D3 (Trading)`, you have simultaneously defined:

- The module boundary (containment zones)
- The data access model (no KSP = no data flow, architecturally)
- The API contract (Bridges are the only cross-boundary path)
- The audit trail (every crossing attempt is logged by construction)
- The compliance evidence (regulation enforced by structure, not policy)

A developer using PACT builds three things: (1) domain logic, (2) agent capabilities, (3) governance configuration. They do NOT build permission systems, approval workflows, audit logging, access control, rate limiting, or budget tracking. Those are all PACT.

---

## What Exists (3,547 tests, 10+ red team rounds)

| Capability                                      | Status                  | LOC    |
| ----------------------------------------------- | ----------------------- | ------ |
| Constraint Envelope (5 dimensions)              | Complete                | ~400   |
| Verification Gradient (4 zones)                 | Complete                | ~300   |
| Delegation Manager (chain walking, tightening)  | Complete                | ~500   |
| Genesis Manager (root of trust, Ed25519)        | Complete                | ~300   |
| EATP Bridge (establish/delegate/verify/audit)   | Complete                | ~730   |
| Org Builder (fluent API, templates, validation) | Complete                | ~600   |
| Agent Runtime (sessions, approval queue)        | Complete                | ~1,500 |
| Trust Postures (5 levels, scoring, evidence)    | Complete                | ~400   |
| Audit Chains (tamper-evident anchors)           | Complete                | ~350   |
| Bridge Trust (cross-boundary trust)             | Complete (not exported) | ~200   |
| Confidentiality Levels (5 EATP levels)          | Complete                | Schema |

---

## What's Missing (8 gaps, ~3,100 LOC new production code)

| #   | Gap                                                  | Complexity | LOC  | Priority | Dependencies      |
| --- | ---------------------------------------------------- | ---------- | ---- | -------- | ----------------- |
| 1   | Positional Addressing (D/T/R grammar)                | HARD       | ~800 | CRITICAL | None (foundation) |
| 4   | Information Barriers (KSP, Bridge, access algorithm) | HARD       | ~600 | CRITICAL | Gaps 1, 3         |
| 2   | 3-Layer Envelopes (Role/Task/Effective)              | MOD-HARD   | ~500 | HIGH     | Gap 1             |
| 3   | Knowledge Clearance (per-role, compartments)         | MODERATE   | ~350 | HIGH     | Gap 1 (light)     |
| 5   | Organizational Store (persistence)                   | MODERATE   | ~400 | HIGH     | Gaps 1-4          |
| 7   | Gradient Per-Dimension Thresholds                    | MODERATE   | ~250 | MEDIUM   | Gap 2             |
| 6   | EATP Record Subtypes                                 | SIMPLE     | ~200 | MEDIUM   | Gaps 1-4          |
| 8   | Shadow Agent Planning                                | HARD       | ~800 | LOW (v1) | All + RAG         |

**Total: ~3,100 LOC production + ~5,000 LOC tests for gaps 1-7**

---

## Architecture Decision: New `pact.governance` Package

The requirements analyst proposed — and I endorse — putting all new PACT-specific code into a new `src/pact/governance/` subpackage. This means:

- **Zero modifications** to existing modules in `trust/`, `build/`, or `use/`
- **Zero regression risk** in the existing 80+ module codebase
- New code USES existing primitives (ConstraintEnvelope, DelegationManager, EATPBridge)
- Clean separation: `governance/` is the PACT spec layer; `trust/` is the EATP engine; `build/` is config

The `governance/` package contains:

- `addressing.py` — Address type, grammar validator, computation
- `compilation.py` — OrgBuilder → CompiledOrg with materialized addresses
- `clearance.py` — RoleClearance, posture-capping, compartments
- `access.py` — Access Enforcement Algorithm (5-step), KSP, Bridges
- `envelopes.py` — RoleEnvelope, TaskEnvelope, effective computation
- `store.py` — Persistence protocols for all governance records

---

## Competitive Landscape

**No direct competitor exists.** PACT occupies a unique position: organizational governance infrastructure for AI agents.

| Category             | Leaders                      | What They Do                  | What PACT Uniquely Adds                  |
| -------------------- | ---------------------------- | ----------------------------- | ---------------------------------------- |
| Agent orchestration  | LangChain, CrewAI            | Task routing, tool access     | Org structure as architecture            |
| Cloud guardrails     | AWS Bedrock, Google Vertex   | Content safety, PII filtering | Five-dimensional constraint envelopes    |
| Enterprise IAM       | Microsoft Entra              | Agent identity lifecycle      | D/T/R grammar, monotonic tightening      |
| Governance platforms | Galileo Agent Control, Airia | Policy enforcement            | Information barriers, clearance, bridges |
| Standards            | CSA ATF, NIST initiative     | Security frameworks           | Formal accountability grammar            |

**Closest competitor**: Airia Agent Constraints — has Organization > Department > Team > Agent hierarchy with inheritance. But it's a policy cascade, not a governance grammar. No accountability invariant (every D/T must have one R). Proprietary.

**Strongest validation**: Google DeepMind's "Intelligent AI Delegation" paper (Feb 2026) independently arrived at privilege attenuation, cryptographic attestation chains, and contract-first decomposition — the same concepts PACT formalizes. A major research lab confirming the architecture is sound.

**Market timing**: 82% of companies have agents, but 84% cannot pass a compliance audit. EU AI Act high-risk provisions take effect August 2026. NIST AI Agent Standards Initiative launched February 2026. The regulatory window is opening.

---

## Framework Extraction: What Must Change

The SDK navigator identified three critical changes for clean vertical imports:

1. **Extract `pact.core.types`** — Move shared enums (BridgeType, VerificationLevel, TrustPostureLevel, ConfidentialityLevel) out of `build.config.schema` to break circular dependencies
2. **Move Foundation content to `examples/`** — `build/verticals/` and `build/templates/builtin/` are Terrene-specific, not framework code
3. **Make EATP lazy** — `trust/__init__.py` re-exports 40+ symbols including EATPBridge which hard-imports eatp SDK at module load

**What astra/arbor write:**

```python
from pact import OrgGenerator, ConstraintEnvelopeConfig, EATPBridge
from astra.org import ASTRA_ORG_CONFIG  # domain config, not pact code
```

---

## COC Assessment: What's at Risk

| Fault Line             | Finding                                                                                                    | Severity |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- | -------- |
| **Amnesia**            | Frontend still says "CARE Platform" (50+ files, user-visible). Future sessions will propagate old identity | HIGH     |
| **Amnesia**            | `build/verticals/` is domain code inside framework — future sessions will extend it                        | HIGH     |
| **Amnesia**            | `bridge_trust.py` exists but gap analysis doesn't reference it — risk of rebuilding from scratch           | MEDIUM   |
| **Convention drift**   | `PlatformConfig`/`PlatformSession` naming reinforces monolith mental model                                 | MEDIUM   |
| **Convention drift**   | No naming convention for new types (Address, RoleEnvelope, etc.) before implementation                     | HIGH     |
| **Security blindness** | KSP absence must be DENY by default (fail-closed)                                                          | CRITICAL |
| **Security blindness** | Clearance must be pre-retrieval gate, not post-retrieval filter                                            | CRITICAL |
| **Security blindness** | Emergency bypass needs hard auto-expiry at enforcement layer                                               | CRITICAL |

---

## Build Order (Validated and Refined)

```
Phase 0: Framework Extraction (prerequisite)
  0a. Extract verticals/ to examples/
  0b. Add boundary-test rule to .claude/rules/
  0c. Create pact.governance package (empty, with types)

Phase 1: Addressing Foundation
  1a. Address type + parser + grammar validator (state machine)
  1b. Org compilation step (OrgBuilder → CompiledOrg with addresses)
  1c. Prefix-containment queries
  1d. Skeleton enforcement (auto-create vacant R)

Phase 2: Clearance + Barriers (the flagship demo)
  2a. RoleClearance model (per-role, compartments, posture-cap)
  2b. KnowledgeSharePolicy model
  2c. PACT Bridge model (address-based, bilateral)
  2d. Access Enforcement Algorithm (5-step decision tree)

  ✅ CHECKPOINT: Flagship scenario works
  Advisory analyst blocked from trading data.

Phase 3: Envelope Architecture
  3a. RoleEnvelope + TaskEnvelope (composition over inheritance)
  3b. ConstraintEnvelope.intersect() method
  3c. compute_effective_envelope(role_address)
  3d. Default envelopes by trust posture

Phase 4: Persistence + Audit
  4a. Store protocols for governance records
  4b. SQLite backend
  4c. EATP audit anchor subtypes

Phase 5: Example Vertical + Integration
  5a. University vertical (proves all concepts)
  5b. End-to-end integration test
```

---

## Example Vertical: University

The deep analyst rated candidates. University wins because it exercises every PACT concept:

- **D/T/R depth**: University > School > Department > Lab > Researcher (5+ levels)
- **Natural barriers**: Faculty records vs student records vs research data vs HR data
- **Clearance independence**: Junior researcher with IRB clearance has SECRET access to human subjects data; Dean of Engineering does NOT (never sat on IRB)
- **Bridges**: Interdisciplinary research = scoped bridge between departments
- **Flagship scenario**: CS faculty member's agent requests student disciplinary records (Student Affairs). BLOCKED — different division, no KSP, no bridge.

Zero domain expertise required. Everyone has attended a university.

---

## Risk Register (Top 5)

| #   | Risk                                                             | Severity | Mitigation                                                       |
| --- | ---------------------------------------------------------------- | -------- | ---------------------------------------------------------------- |
| R1  | Flat-to-tree migration breaks 200+ org tests                     | CRITICAL | Dual-model: keep OrgDefinition, add CompiledOrg in parallel      |
| R2  | Envelope intersection correctness (path globs, temporal overlap) | CRITICAL | Property-based testing (Hypothesis); formal spec per dimension   |
| R3  | Access algorithm bypass (proving a negative is hard)             | CRITICAL | Exhaustive test matrix: every combo of unit/KSP/bridge/clearance |
| R4  | Microsoft Entra as "good enough" for enterprise                  | HIGH     | Position as complementary ("org governance above IAM")           |
| R5  | Market not ready for org-level governance                        | MEDIUM   | Progressive adoption: start with envelopes, add D/T/R later      |
