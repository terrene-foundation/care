# PACT Core Thesis v0.7: EATP Integration Gaps

**Date**: 2026-03-21
**Scope**: Gaps in how the PACT thesis specifies its relationship with EATP
**Companion to**: 16-thesis-gaps.md (15 structural gaps)

---

## Context

The PACT thesis (Section 2.8) states: "I do not redefine EATP's constraint dimensions or verification gradient. PACT contributes the organizational architecture for how those dimensions are configured, delegated, and composed across hierarchical levels."

This is the right architectural boundary. But the thesis never formally specifies HOW PACT actions map to EATP records, creating ambiguity for independent implementers.

---

## Gap 16: No Formal PACT Action → EATP Record Mapping

The thesis mentions EATP records in passing — "creates a Delegation Record in EATP" (Section 4.4), "Fourteen EATP records formed the audit trail" (Section 8) — but never provides a systematic mapping.

An independent implementer reading the PACT thesis cannot determine which EATP record type to create for which PACT governance action. The mapping is inferable but not specified.

**What's needed**: A normative table mapping every PACT governance action to its EATP record type, fields, and lifecycle:

```
PACT Action                        → EATP Record Type
Organization created (BOD)         → Genesis Record
D/T unit created                   → Delegation Record
Role Envelope defined              → Delegation Record + Constraint Envelope
Task Envelope created              → Delegation Record + Constraint Envelope (with expiry)
Clearance granted                  → Capability Attestation
Clearance revoked                  → Capability Attestation (superseded)
Bridge established                 → Delegation Record (bilateral)
Bridge revoked                     → Revocation (cascade to bridge delegation)
KSP created                        → Delegation Record (cross-boundary)
KSP revoked                        → Revocation
Action verified (any gradient zone) → Audit Anchor
Barrier enforced (access denied)   → Audit Anchor (subtype: barrier_enforced)
Emergency bypass activated         → Audit Anchor (subtype: emergency_bypass)
Address recomputed (reorg)         → Audit Anchor (subtype: address_recomputed)
Envelope modified                  → Audit Anchor (subtype: envelope_modified)
```

Without this table, two independent PACT implementations will produce incompatible EATP records for the same governance actions — defeating interoperability.

---

## Gap 17: Capability Attestation Overloaded for Clearance

EATP's Capability Attestation was designed for "what an agent CAN DO" — its functional capabilities (e.g., "can execute trades," "can file regulatory reports"). The thesis uses it for clearance grants — "what information a role CAN ACCESS."

These are semantically different:

| Dimension   | Capability Attestation (EATP intent)     | Clearance Grant (PACT use)                   |
| ----------- | ---------------------------------------- | -------------------------------------------- |
| Subject     | Agent                                    | Role (person position)                       |
| Scope       | Functional capability                    | Information access level                     |
| Granularity | Action types                             | Classification level + compartments          |
| Lifecycle   | Tied to agent trust posture              | Tied to vetting status + review cycles       |
| Revocation  | Agent decommissioned or posture degraded | Clearance expired, NDA violated, role change |

The overloading is defensible — Capability Attestation is the closest EATP element — but it should be explicitly justified in the thesis. An alternative would be to propose a sixth EATP element type (Clearance Attestation), but that changes the EATP spec.

**What's needed**: Either (a) explicit justification for why Capability Attestation is the correct record type for clearance, with a note on the semantic stretch, or (b) a proposal for EATP extension to support clearance-specific attestations.

---

## Gap 18: Effective Envelope Has No EATP Record

EATP's Trust Lineage Chain assumes every trust relationship has a corresponding record. The chain is: Genesis → Delegation → Constraint Envelope → Capability Attestation → Audit Anchor. Every link is stored, signed, and hash-chained.

PACT's Effective Envelope is "computed, never stored" (thesis Section 5.2). It is the intersection of all ancestor Role Envelopes from root to current position. There is no EATP record for it.

This creates a verification gap:

1. Auditor asks: "What was this agent's effective envelope at 14:32 on Tuesday?"
2. The system must recompute it from the ancestor Role Envelopes that were active at that timestamp
3. If any ancestor Role Envelope was modified between 14:32 and the audit query, the recomputation uses current envelopes, not historical ones
4. Unless envelope versioning preserves historical states

The thesis says effective envelopes are "always computed" but doesn't address historical recomputation or point-in-time audit queries.

**What's needed**: Clarify whether:

- (a) Effective envelopes are ephemeral and historical queries recompute from versioned Role Envelopes (requires Role Envelope version history)
- (b) Effective envelopes are cached as Audit Anchors at verification time (the Audit Anchor records what the effective envelope WAS at the moment of verification — this is probably the right answer, since the Audit Anchor already contains the verification result)
- (c) A snapshot Constraint Envelope record is created for each effective envelope computation (expensive, creates record bloat)

Option (b) is likely the intended design: the Audit Anchor already records the verification result, which implicitly captures the effective envelope at that moment. But the thesis should say this explicitly.

---

## Gap 19: Multi-Level VERIFY Pattern

EATP VERIFY walks one delegation chain: from the agent's Delegation Record up through parent delegations to the Genesis Record. This is a single-chain traversal.

PACT's effective envelope requires walking ALL ancestor chains simultaneously:

```
To verify action by Cash Manager (D1-R1-D1-R1-D1-R1-T1-R1-R2):
  1. VERIFY: CEO's authority (Genesis → D1-R1 delegation)
  2. VERIFY: CFO's authority (D1-R1 delegation → D1-R1-D1-R1 delegation)
  3. VERIFY: Head of Treasury's authority (→ D1-R1-D1-R1-D1-R1 delegation)
  4. VERIFY: Cash Manager's authority (→ T1-R1 delegation)
  5. VERIFY: Treasury Analyst's authority (→ R2 delegation)
  6. COLLECT: All Constraint Envelopes from steps 1-5
  7. INTERSECT: Compute effective envelope
  8. EVALUATE: Check action against effective envelope
  9. CLASSIFY: Determine gradient zone
  10. AUDIT: Create Audit Anchor with result
```

This is not a single EATP VERIFY call — it's N VERIFY calls (where N = depth of the address chain) followed by an intersection and evaluation. The thesis doesn't describe this multi-level verification pattern, leaving implementers to figure it out.

**What's needed**: Specify the multi-level VERIFY algorithm:

- How many EATP VERIFY calls are made per PACT verification?
- Are they sequential or can they be parallelized?
- What happens if one level's VERIFY fails (revoked delegation mid-chain)?
- Should the result be FULL verification at every level, or STANDARD for ancestors + FULL for the leaf?
- Performance implications: a 6-level hierarchy means 6 VERIFY calls per action. At machine speed (hundreds of actions/minute), this is 600 VERIFY calls/minute per agent.

---

## Gap 20: Bridge Creates Bilateral Delegation — But EATP Delegation Is Unilateral

EATP's Delegation Record models one party delegating authority to another: A delegates to B. It is inherently unilateral — A has authority and extends it to B.

PACT's Bridge (thesis Section 4.4) requires bilateral establishment — "both roles must agree." This means the CCO and the Head of Advisory both consent to the compliance monitoring bridge.

How does bilateral agreement map to EATP's unilateral Delegation Record?

Options:

- (a) Two Delegation Records (A→B and B→A), cross-referencing each other
- (b) One Delegation Record signed by both parties (EATP doesn't support multi-signature on a single record)
- (c) One Delegation Record from A→B with B's countersignature stored in a separate Capability Attestation
- (d) A new record type (Bridge Record) that EATP doesn't define

The existing codebase (`trust/bridge_trust.py`) creates bilateral delegation records — option (a). But the thesis doesn't specify this, and option (a) has a TOCTOU problem: what if A creates their Delegation Record but B never creates theirs? The bridge is half-established.

**What's needed**: Specify how bilateral bridge establishment maps to EATP's unilateral delegation model. Address the atomicity problem (both records must exist or neither should).

---

## Gap 21: Revocation Semantics Differ Between EATP and PACT

EATP defines cascade revocation: revoking a Delegation Record invalidates all downstream delegations. This is correct for trust chains — if the CFO's delegation is revoked, everything under the CFO is invalidated.

PACT has multiple things that can be revoked:

- A Role Envelope (standing envelope revoked → what happens to active Task Envelopes?)
- A Clearance grant (clearance revoked → what happens to in-flight operations using that clearance?)
- A Bridge (bridge revoked → what happens to operations currently crossing it?)
- A KSP (KSP revoked → information barrier is now active — what about data already shared?)

Each of these has different revocation semantics:

| What's Revoked | EATP Cascade Behavior                  | PACT-Specific Behavior                                                         |
| -------------- | -------------------------------------- | ------------------------------------------------------------------------------ |
| Role Envelope  | Cascade revokes downstream delegations | Should Task Envelopes under it be killed? Or allowed to complete?              |
| Clearance      | Cascade revokes capability attestation | Should in-flight operations be terminated? Or complete with current clearance? |
| Bridge         | Cascade revokes bridge delegation      | Should in-flight cross-boundary operations be terminated?                      |
| KSP            | Cascade revokes KSP delegation         | Data already shared cannot be un-shared — what's the governance model?         |

EATP's cascade is binary: revoke = invalidate everything downstream. PACT needs more nuanced revocation (immediate termination vs. graceful completion vs. no-new-operations-but-finish-existing).

**What's needed**: Specify revocation behavior per PACT record type. EATP cascade is the default, but the thesis should state whether PACT ever needs non-cascading revocation (e.g., "revoke this bridge but let in-flight operations complete").

---

## Gap 22: Reasoning Traces for PACT Governance Decisions

EATP v2.2 adds structured reasoning traces — "WHY a trust decision was made." These attach to Delegation Records and Audit Anchors with confidentiality classification and dual-binding signing.

PACT creates governance decisions that SHOULD have reasoning traces but the thesis never mentions them:

| PACT Decision              | Reasoning Trace Content                               | Classification           |
| -------------------------- | ----------------------------------------------------- | ------------------------ |
| Role Envelope defined      | "Why these constraints for this direct report"        | RESTRICTED (personnel)   |
| Clearance granted          | "Why this person needs this access level"             | CONFIDENTIAL (vetting)   |
| Bridge established         | "Why these two roles need cross-boundary access"      | RESTRICTED (operational) |
| KSP created                | "Why this cross-boundary knowledge sharing is needed" | CONFIDENTIAL (policy)    |
| Emergency bypass approved  | "Why normal envelope was insufficient"                | CONFIDENTIAL (incident)  |
| Action held → approved     | "Why the supervisor approved this boundary action"    | RESTRICTED               |
| Action held → denied       | "Why the supervisor denied this boundary action"      | RESTRICTED               |
| Barrier enforced (blocked) | Auto-generated: "No access path exists"               | PUBLIC (structural fact) |

The thesis uses EATP's reasoning traces but never specifies which PACT governance actions should mandate them. Section 5.4 of the EATP thesis defines a `REASONING_REQUIRED` constraint type — PACT should specify when this constraint is active.

**What's needed**: Specify which PACT governance actions require reasoning traces (mandatory vs. optional) and at what confidentiality level. Emergency bypass and clearance grants at SECRET+ should probably be mandatory.

---

## Gap 23: EATP Conformance Level for PACT

EATP defines three conformance levels (EATP thesis Section 11):

- **Compatible** (basic): Genesis Record + Audit Anchor + ≥1 constraint dimension
- **Conformant** (standard): All 5 elements, all 4 operations, full gradient, cascade revocation, reasoning traces
- **Complete** (full): All 5 postures, all 5 classification levels, StrictEnforcer + ShadowEnforcer, VerificationBundle export

The PACT thesis doesn't state which EATP conformance level it requires. Given that PACT uses:

- All 5 elements ✓
- All 4 operations ✓
- All 5 constraint dimensions ✓
- Full verification gradient ✓
- All 5 trust postures ✓
- All 5 classification levels ✓
- StrictEnforcer (production) + ShadowEnforcer (observation) ✓
- Reasoning traces (for governance decisions) ✓

PACT appears to require **EATP Complete** conformance. The thesis should state this explicitly. An implementation claiming PACT conformance with only EATP Compatible backing would be structurally unsound (no Delegation Records → no monotonic tightening verification → no accountability chain).

**What's needed**: State that PACT requires EATP Conformant at minimum, EATP Complete recommended.

---

## Summary

| Gap # | Title                                             | Severity | Implementation Impact                                               |
| ----- | ------------------------------------------------- | -------- | ------------------------------------------------------------------- |
| 16    | No formal PACT→EATP record mapping                | CRITICAL | Independent implementations produce incompatible records            |
| 17    | Capability Attestation overloaded for clearance   | MAJOR    | Semantic confusion; clearance ≠ capability                          |
| 18    | Effective Envelope has no EATP record             | MAJOR    | Historical audit queries cannot reconstruct point-in-time envelopes |
| 19    | Multi-level VERIFY pattern unspecified            | MAJOR    | Implementers must invent the N-level verification algorithm         |
| 20    | Bridge bilateral ↔ EATP unilateral mismatch       | MAJOR    | Atomicity problem in bilateral bridge establishment                 |
| 21    | Revocation semantics differ (cascade vs graceful) | MAJOR    | PACT needs nuanced revocation that EATP doesn't model               |
| 22    | Reasoning traces for PACT governance decisions    | NOTABLE  | Which decisions mandate reasoning? At what classification?          |
| 23    | EATP conformance level unspecified                | NOTABLE  | What EATP level does a PACT implementation require?                 |

**Total thesis gaps**: 15 (structural) + 8 (EATP) = **23 gaps identified**.

Gaps 16, 19, and 21 are the most implementation-critical — they affect how every PACT governance action interacts with the EATP trust store.
