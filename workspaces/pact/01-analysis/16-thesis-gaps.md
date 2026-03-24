# PACT Core Thesis v0.7: Gap Analysis

**Date**: 2026-03-21
**Reviewed by**: Implementation team during /analyze phase
**Purpose**: Identify gaps in the thesis that will surface during implementation

---

## Critical Gaps (will block implementation if unresolved)

### 1. Envelope Intersection Is Never Defined

The thesis says "envelopes compose through intersection" and "the Effective Envelope is the intersection of all ancestor envelopes." But it never defines what intersection means for each of the five dimensions.

- **Financial**: Is intersection `min(budget_a, budget_b)`? What about overlapping budget categories?
- **Operational**: Is it set intersection of allowed actions? What if `a/*` and `a/b/*` are the two sets — is the intersection `a/b/*` (prefix narrowing) or something else?
- **Temporal**: Is it overlap of time windows? What if parent says "weekdays 9-5" and grandparent says "Mon-Wed any time" — is the intersection Mon-Wed 9-5?
- **Data Access**: Is it set intersection of read/write paths? Path glob intersection is non-trivial (`data/finance/*` ∩ `data/*/q3` = ?).
- **Communication**: Is it set intersection of allowed channels?

**Why this matters**: The entire effective envelope computation depends on intersection being well-defined per dimension. Without formal semantics, two implementations could compute different effective envelopes from the same input. This is the single most important gap for implementation.

**Recommendation**: Add a formal definition of `intersect(E1, E2) → E` for each dimension, with edge cases.

---

### 2. Gradient Threshold Composition Is Ambiguous

The thesis (Section 5.4) says supervisors set per-dimension gradient thresholds within Role Envelopes. But effective envelopes are computed from the intersection of all ancestor envelopes. **Are gradient thresholds also composed, or does only the immediate supervisor's thresholds apply?**

Example: CEO sets `financial.held_from = $100,000` for CFO. CFO sets `financial.held_from = $50,000` for Head of Treasury. Head of Treasury sets `financial.held_from = $20,000` for Cash Manager.

For the Cash Manager, which held threshold applies?

- Option A: Only the immediate supervisor's ($20,000) — simple but ignores ancestor intent
- Option B: The most restrictive ancestor's ($20,000) — monotonic tightening applied to thresholds
- Option C: Each level's thresholds apply independently — action held at $20,000 by Head of Treasury AND at $50,000 by CFO AND at $100,000 by CEO

The thesis doesn't say. Option C is the most rigorous (each supervisor's gradient is honored), but it means a single action could be simultaneously held by multiple supervisors.

---

### 3. Delegation Chain Vacancy Is Underspecified

The thesis says vacant roles "cannot execute" and "satisfy the grammatical constraint." But what happens to the effective envelopes of all downstream roles when a mid-chain role becomes vacant?

Example: CEO → CFO → Head of Treasury → Cash Manager. The CFO resigns (role becomes vacant).

- Is the Head of Treasury's effective envelope suspended? They can't compute it without the CFO's Role Envelope in the chain.
- Does the CEO's envelope cascade directly to Head of Treasury (skipping the vacant CFO)?
- Are all downstream agents suspended until the vacancy is filled?

The thesis mentions "acting in two roles" (Section 2.5) as a partial solution but doesn't address the general case.

---

## Major Gaps (will cause implementation ambiguity)

### 4. T-Inherits-D Rule Is Informal

The thesis states team members see department-level knowledge. But:

- At what clearance level? All department knowledge, or only up to the team member's own clearance?
- Does a Team within a Department automatically get a KSP-equivalent, or is inheritance a different mechanism entirely?
- If a Department has CONFIDENTIAL knowledge and a Team member has only RESTRICTED clearance, does inheritance apply at all?

This matters for the Access Enforcement Algorithm (step 4c).

### 5. Bridge Lifecycle Is Incomplete

The thesis defines bridge creation (bilateral, scoped, auditable) but doesn't address:

- **Revocation**: Can a bridge be unilaterally revoked, or does it require bilateral agreement?
- **In-flight operations**: What happens to operations currently crossing a bridge when it is revoked? Are they killed? Allowed to complete?
- **Expiry**: Standing bridges are "permanent" — but do they need periodic review? The thesis doesn't mention bridge review cycles analogous to clearance review cycles.
- **Modification**: Can a bridge scope be narrowed without revocation and re-creation?

### 6. Concurrent Envelope Modification

What if a supervisor modifies a Role Envelope while a Task Envelope (derived from the old Role Envelope) is active?

- Does the Task Envelope become invalid (it was derived from a now-superseded parent)?
- Does the new Role Envelope take effect immediately, or only for new Task Envelopes?
- If the new Role Envelope is TIGHTER than the active Task Envelope, is the task killed?

The thesis is silent on envelope versioning and concurrent modification.

### 7. No TOCTOU Treatment

The effective envelope is computed at request time. The org structure could change between computation and action execution. In high-frequency scenarios (trading), this time-of-check/time-of-use gap could be exploitable:

1. Agent computes effective envelope (includes Trading position access)
2. Bridge to Trading is revoked
3. Agent executes using stale effective envelope

The thesis doesn't address whether effective envelopes are cached or recomputed per-action, or how to handle mid-action revocations.

### 8. Compartment Semantics Are Thin

Compartments are mentioned for SECRET and TOP_SECRET but:

- Can compartments overlap? (Can `aml-investigations` and `fraud-investigations` share data?)
- Is there a hierarchy of compartments? (Is `investigations` a parent of `aml-investigations`?)
- Are compartments scoped to a D/T unit or global across the organization?
- Can a role hold clearance for multiple compartments?

The financial services example implies yes to the last question (AML Officer has `aml-investigations`, Sanctions Officer has `sanctions-screening`), but the formal semantics are missing.

---

## Notable Gaps (worth addressing but not blocking)

### 9. Agent Self-Discovery

The thesis says agents operate within envelopes but doesn't specify how an agent knows what its effective envelope IS. Does it:

- Query the system at startup?
- Receive envelope injection as context?
- Discover boundaries by hitting them (trial and error)?

For a practical framework, agents need a `get_my_envelope()` API.

### 10. Performance/Scalability

No discussion of computational complexity. Effective envelope computation walks root-to-leaf — O(depth). Prefix queries are O(n) without indexing. The thesis's own example (Section 8) describes 47 actions in 6 days — not performance-sensitive. But the financial services example involves real-time trading where latency matters. Should effective envelopes be cached? Precomputed? The thesis doesn't say.

### 11. Multi-Organization Federation

Explicitly out of scope (single-org only), but the thesis cites AD/MIT (South et al., 2025) for cross-org authentication without discussing how two PACT-governed organizations would interact. Joint ventures, supply chains, and regulated reporting chains (MAS ← regulated entity) inherently cross organizational boundaries.

### 12. The Escalation Mechanism

The thesis says actions outside the envelope require "escalation" but doesn't specify the mechanism:

- Does the agent hold (pause execution)?
- Does it auto-deny?
- Does it escalate to the immediate supervisor only, or can it skip levels?
- What if the supervisor is unavailable?

The verification gradient covers this partially (held = pauses for approval), but the relationship between "outside the envelope" and "held" is not explicit. Is "outside the envelope" always "blocked"? Or can the gradient configuration make some out-of-envelope actions "held" instead?

### 13. The Holacracy Mapping Is Hand-Waved

The thesis says "lead links to R; circles to T" for Holacracy mapping. This is oversimplified. Holacracy has tension processing, governance meetings, distributed authority, and cross-link connections that don't map cleanly to monotonic tightening. The thesis should either engage more deeply or drop the claim and state that Holacracy is outside PACT's scope (which Section 12.2 nearly does).

### 14. Cost of Governance Quantification

Section 12.4 mentions ~125 supervisory positions needing five-dimensional configuration. Section 8 shows 3 human touch points over 6 days for one task cascade. But there's no steady-state analysis: for a 500-person org running hundreds of tasks daily, how many held events does the human layer need to process? What's the human FTE cost of being "on the loop"?

The thesis acknowledges this ("has not been empirically measured") but doesn't even provide back-of-envelope estimates.

### 15. Audit Data Volume and Retention

Every governance action creates an EATP record. For a 500-person org with agents at every role, running at machine speed, the audit volume could be enormous. The thesis doesn't discuss:

- Audit data retention policies
- Summarization/aggregation for human review
- Storage scaling characteristics
- Right to deletion (GDPR Article 17) vs. audit immutability

---

## Structural Observations

### What the Thesis Does Well

- **Honest limitations** (Section 12) are unusually candid for an academic paper — constraint theater, surveillance dual-use, single-author provenance, no formal verification
- **Falsification conditions** (Section 14) are testable and specific
- **The Architectural Inversion** (Section 10) is the thesis's strongest original contribution — it reframes PACT from "governance layer" to "application architecture model"
- **Positioning against related work** (Section 2.3) is thorough and fair — Kolt, South/AD/MIT, Tomasev/DeepMind, IMDA are all properly distinguished
- **Scope discipline** — the thesis is explicit about what PACT does NOT do (physical barriers, training, Holacracy, single-person operations)

### What's Missing from Related Work

- **OPAL (Open Algorithms)** — Pentland's data governance framework shares containment ideas with PACT. Cited indirectly through South et al. but not engaged directly.
- **Zero Trust Architecture (NIST SP 800-207)** — PACT's default-deny containment model is essentially Zero Trust applied to organizational knowledge. This connection isn't made.
- **XACML** — The eXtensible Access Control Markup Language is a policy composition standard with support for combining algorithms (deny-overrides, permit-overrides). PACT's envelope intersection is a form of policy composition — the connection to XACML's formal treatment could strengthen the intersection semantics.

---

## Impact on Implementation

| Gap #                       | Implementation Impact                                              | When It Hits |
| --------------------------- | ------------------------------------------------------------------ | ------------ |
| 1 (Intersection)            | Cannot implement `compute_effective_envelope()` without this       | Phase 3      |
| 2 (Gradient composition)    | Cannot implement per-dimension thresholds without this             | Phase 5      |
| 3 (Vacancy)                 | Edge case in effective envelope computation                        | Phase 3      |
| 4 (T-inherits-D)            | Cannot implement Access Enforcement Algorithm step 4c without this | Phase 2      |
| 5 (Bridge lifecycle)        | Cannot implement bridge revocation                                 | Phase 2      |
| 6 (Concurrent modification) | Race condition in production                                       | Phase 3+     |
| 7 (TOCTOU)                  | Security vulnerability in production                               | Phase 4+     |
| 8 (Compartments)            | Cannot implement compartment checks without semantics              | Phase 2      |

**Recommendation**: Gaps 1, 4, and 8 should be resolved in the thesis before implementation reaches Phase 2-3. Gaps 2, 3, 5, 6, 7 can be resolved during implementation with ADRs documenting the decisions.
