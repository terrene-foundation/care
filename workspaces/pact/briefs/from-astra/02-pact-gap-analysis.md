# PACT Core Library: Gap Analysis (Spec vs Implementation)

**Date**: 2026-03-21
**Spec**: PACT Core Specification v0.1 (1,590 lines, CC BY 4.0)
**Codebase**: `~/repos/terrene/care/src/pact/` (package name: `pact` v0.1.0)

---

## What Exists and Works

| Capability                                                    | File(s)                                | Status                                                              |
| ------------------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------- |
| **Constraint Envelope** (5 CARE dimensions)                   | `trust/constraint/envelope.py`         | Complete — evaluate_action(), is_tighter_than()                     |
| **Verification Gradient** (4 zones)                           | `trust/constraint/gradient.py`         | Complete — GradientEngine.classify() → VerificationResult           |
| **Delegation Manager** (chain walking, tightening validation) | `trust/delegation.py`                  | Complete — create_delegation(), walk_chain(), validate_tightening() |
| **Genesis Manager** (root of trust, Ed25519 keys)             | `trust/genesis.py`                     | Complete — create_genesis(), validate_genesis()                     |
| **EATP Bridge** (establish/delegate/verify/audit)             | `trust/eatp_bridge.py`                 | Complete (728 lines) — full CARE↔EATP translation                   |
| **Config Schema** (all dimensions, agents, teams)             | `build/config/schema.py`               | Complete (507 lines) — Pydantic models, correct EATP enum names     |
| **Org Builder** (fluent API, templates, validation)           | `build/org/builder.py`                 | Complete — build(), validate_org(), from_config()                   |
| **Agent Runtime** (sessions, approval queue)                  | `use/execution/runtime.py`             | Complete (1,513 lines)                                              |
| **Trust Postures** (5 levels, scoring, evidence)              | `trust/posture.py`, `trust/scoring.py` | Complete                                                            |
| **Audit Chains** (tamper-evident anchors)                     | `trust/audit/`                         | Complete                                                            |
| **Bridge Trust** (cross-boundary trust)                       | `trust/bridge_trust.py`                | Exists but NOT in public exports                                    |
| **Confidentiality Levels**                                    | `build/config/schema.py`               | PUBLIC/RESTRICTED/CONFIDENTIAL/SECRET/TOP_SECRET ✓                  |

---

## What's Missing (Spec → Implementation Gaps)

### GAP 1: Positional Addressing — ABSENT

**Spec**: Part 2 (D/T/R grammar, address computation, prefix queries, recomputation)
**Impact**: Foundational — everything else depends on it

**Missing pieces:**

- `Address` type with parse/format/validate
- D/T/R grammar validator (state machine: container → must see R next)
- Address computation from org tree
- Prefix-containment queries (`WHERE address LIKE 'D1-R1-D3%'`)
- Skeleton enforcement (auto-create vacant R when D/T created without one)
- Address recomputation pipeline for reorganizations
- `address_history` for audit continuity

**Note**: The org builder currently uses flat IDs. Positional addressing requires either extending OrgBuilder or creating a new compilation step that assigns addresses after the tree is defined.

---

### GAP 2: 3-Layer Envelope Architecture — PARTIAL

**Spec**: Part 3 (Role Envelope / Task Envelope / Effective Envelope)
**Impact**: High — the delegation model depends on this

**What exists:** `ConstraintEnvelope` with evaluation and tightening. The mechanics work.

**Missing pieces:**

- `RoleEnvelope` record type (standing, defined by supervisor for direct report, versioned)
- `TaskEnvelope` record type (ephemeral, narrows RoleEnvelope for one task, auto-expires)
- `compute_effective_envelope(role_address)` that walks the address chain and intersects all ancestors
- Default envelope profiles per trust posture level
- Acknowledgment prompt when no TaskEnvelope provided ("This task will operate under standing envelope. [Accept] / [Narrow]")
- Emergency bypass system (Tiers 1-3, auto-expiry, rate limiting, post-incident review)
- Degenerate envelope detection (effective envelope too tight to be operational)

---

### GAP 3: Knowledge Clearance Model — PARTIAL

**Spec**: Part 4 (per-role clearance, compartments, posture-capping, review cycles)
**Impact**: High — information barriers depend on clearance checks

**What exists:** `ConfidentialityLevel` enum, `_evaluate_confidentiality()` in envelope.

**Missing pieces:**

- `RoleClearance` record type (per-role, with compartments, granted_by, vetting_status, review_at)
- Posture-capping formula: `effective_clearance = min(role.max_clearance, POSTURE_CEILING[posture])`
- Compartment enforcement for SECRET/TOP_SECRET
- Clearance assignment authority rules (who can grant at each level)
- Clearance review cycle management (auto-downgrade on expiry)
- Clearance grant/revoke workflow → EATP Capability Attestation

---

### GAP 4: Information Barriers — ABSENT

**Spec**: Parts 2.3, 4.6, 4.7 (containment boundaries, KSP, bridges, access algorithm)
**Impact**: CRITICAL — this is Astra's flagship demonstration

**Missing pieces:**

- `KnowledgeSharePolicy` record type (source unit → target unit, conditions, classification ceiling)
- `Bridge` record type (role ↔ role, scoped envelope for what crosses, bilateral)
- Access Enforcement Algorithm (the 5-step decision tree):
  1. Effective clearance check
  2. Classification check
  3. Compartment check
  4. Containment check (same unit / downward / T-inherits-D / KSP / bridge)
  5. Audit log
- Knowledge cascade rules (within D/T: PUBLIC/RESTRICTED auto; across: KSP required)
- Trust lineage downward (posture-gated read access to subtree)
- T-inherits-D rule (team members see department knowledge)

**Note**: `bridge_trust.py` exists but is not exported. It may partially cover Bridge functionality — needs review and alignment with the spec's Bridge concept.

---

### GAP 5: Organizational Persistence — PARTIAL

**Spec**: Implied by all parts
**Impact**: High — in-memory only is insufficient

**What exists:** `OrgBuilder.save(org, store)` / `OrgBuilder.load(org_id, store)`. EATP Bridge has store backends.

**Missing pieces:**

- Store protocols for the new record types (RoleEnvelope, TaskEnvelope, RoleClearance, KSP, Bridge)
- Unified org store with address-indexed queries
- SQLite + PostgreSQL backends for the full model
- Migration support for org restructures

---

### GAP 6: EATP Record Subtypes for PACT Actions — ABSENT

**Spec**: Part 5 (mapping PACT governance actions to EATP records)
**Impact**: Medium — audit trail completeness

**Missing pieces:**

- Audit anchor subtypes: `envelope_created`, `envelope_modified`, `clearance_granted`, `clearance_revoked`, `emergency_bypass`, `gradient_held_resolved`, `barrier_enforced`, `ksp_created`, `bridge_established`, `address_recomputed`
- Capability Attestation for clearance grants/revocations
- Delegation Record for Role/Task Envelope lifecycle

---

### GAP 7: Gradient Per-Dimension Thresholds — ABSENT

**Spec**: Part 3, Section 3.5
**Impact**: Medium — refinement of existing engine

**What exists:** Rule-based pattern matching in GradientEngine.

**Missing pieces:**

- Per-dimension threshold configuration within RoleEnvelope:
  ```
  financial: auto_approved_up_to=10000, flagged_from=10001, held_from=50001, blocked_above=100000
  data_access: auto_approved=[...], flagged=[...], held=[...], blocked=[...]
  ```
- Held action decision point (bounded request to human with timeout)
- Timeout behavior (configurable: remain held, auto-approve, escalate)

---

### GAP 8: Shadow Agent Planning Process — PARTIAL

**Spec**: Part 6 (5-layer memory, 5-phase planning)
**Impact**: Low for v1 — the planning process is important but not blocking

**What exists:** Agent runtime, session management, approval queue.

**Missing pieces:**

- 5-layer memory system (org memory, role context, agent registry, knowledge base, task history)
- 5-phase planning flow (context → discovery → decomposition → recommendation → execution)
- Security invariants (read-only planning, clearance-before-retrieval, plan approval before cascade)
- Clearance-partitioned vector indices (pre-retrieval filtering, not post)

---

## Recommended Build Order

```
Phase 1: Addressing Foundation
  1. Positional Addressing (D/T/R grammar, Address type, computation, queries)
  2. Org Builder integration (extend or replace current flat-ID model)

Phase 2: Clearance & Barriers
  3. Knowledge Clearance (RoleClearance, compartments, posture-capping)
  4. Information Barriers (KSP, Bridge, Access Enforcement Algorithm)

Phase 3: Envelope Architecture
  5. 3-Layer Envelopes (RoleEnvelope, TaskEnvelope, compute_effective_envelope)
  6. Emergency Bypass (tiered, auto-expiry, rate-limited)

Phase 4: Persistence & Audit
  7. Organizational Store (all new record types, address-indexed)
  8. EATP Record Subtypes (governance action audit trail)

Phase 5: Refinements
  9. Gradient Per-Dimension Thresholds
  10. Shadow Agent Planning Process
```

Phases 1-2 are the **minimum viable PACT** for Astra. The flagship scenario (advisory analyst blocked from trading data) requires positional addressing + clearance + information barriers + access enforcement algorithm.
