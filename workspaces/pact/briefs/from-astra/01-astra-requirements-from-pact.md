# What Astra Needs from PACT: Requirements for the Core Library

**Date**: 2026-03-21
**Purpose**: Define what the PACT core library (`pip install pact`) must provide so that Astra (financial services reference implementation) can be built on top of it.
**Audience**: PACT core library developers (care repo team)

---

## Context

**PACT** (care repo) is the domain-agnostic reference implementation of the PACT specification (Principled Architecture for Constrained Trust). It knows nothing about finance, healthcare, or any specific industry.

**Astra** is the financial services domain application. It imports `pact` and configures it with MAS-regulated financial institution structures, regulatory clearance mappings, information barriers, and compliance-calibrated verification gradients.

**The boundary test**: If you ripped out all financial vocabulary from Astra and replaced it with healthcare terms, zero lines of PACT library code would change.

This document maps each PACT specification concept to:

1. What currently exists in `src/pact/`
2. What's missing
3. What Astra needs from it (with financial services examples)

---

## Classification Level Naming

The PACT specification uses Singapore Government IM naming (OFFICIAL, SENSITIVE, etc.). The EATP SDK and the existing `schema.py` use:

| Level | EATP/PACT Library Name | Spec Name (Adjust) |
| ----- | ---------------------- | ------------------ |
| C0    | **PUBLIC**             | ~~OFFICIAL~~       |
| C1    | **RESTRICTED**         | ~~SENSITIVE~~      |
| C2    | **CONFIDENTIAL**       | CONFIDENTIAL       |
| C3    | **SECRET**             | SECRET             |
| C4    | **TOP_SECRET**         | TOP_SECRET         |

The library already uses the correct EATP names in `ConfidentialityLevel` enum. The specification text should be updated to match, but the implementation is correct.

---

## 1. Positional Addressing (D/T/R Grammar)

### Spec Reference

Part 2 (Sections 2.1–2.5) of the PACT Core Specification.

### Current State: ABSENT

The org builder uses flat IDs (`agent_id`, `team_id`, `department_id`). There is no positional address computation, no D/T/R grammar validation, no prefix-containment queries.

### What Astra Needs

**1.1 Address Computation Engine**

Given an organizational tree, compute positional addresses for every node:

```
D1-R1                     → CEO
D1-R1-D1-R1               → CCO (Compliance Division)
D1-R1-D2-R1               → Head of Advisory
D1-R1-D3-R1               → Head of Trading
D1-R1-D3-R1-T1-R1         → Senior Trader (Equities Desk)
```

Required API:

```python
# Compute address for any node in the org tree
address = org.compute_address(node_id) → "D1-R1-D3-R1-T1-R1"

# Parse an address into its typed segments
segments = Address.parse("D1-R1-D3-R1-T1-R1")
# → [D(1), R(1), D(3), R(1), T(1), R(1)]

# Prefix-containment query: everything under Trading Division
org.query_by_prefix("D1-R1-D3") → [all nodes in Trading]
```

**1.2 Grammar Validation**

The D/T/R grammar constraint must be enforced at write time:

- Every D or T must be immediately followed by exactly one R (head role)
- Invalid sequences (D-D, D-T, T-T, T-D) must be rejected
- Skeleton enforcement: creating a D/T without an R auto-creates a vacant head role

Astra example: If someone tries to create "Trading Division" without assigning a Head of Trading, the system auto-creates a vacant role and flags it.

**1.3 BOD as Governance Root**

The Board of Directors is a special root node (not a D or T). BOD members are external roles that cannot have operational agents.

Astra example: Independent Directors (R1-R5) and CEO (R6) sit at BOD level. They can observe and approve but not execute trades.

**1.4 Address Recomputation on Reorganization**

When the org tree changes (a unit moves, a role is restructured), addresses must be recomputed for all affected nodes. Old addresses should be preserved in `address_history` for audit continuity.

### Priority: CRITICAL

Without positional addressing, Astra cannot implement information barriers (which depend on containment boundary checks via address prefixes).

---

## 2. Operating Envelopes (3-Layer Architecture)

### Spec Reference

Part 3 (Sections 3.1–3.8) of the PACT Core Specification.

### Current State: PARTIAL

`ConstraintEnvelope` exists with all 5 dimensions and evaluation logic. `DelegationManager.validate_tightening()` validates monotonic tightening. But the 3-layer architecture (Role Envelope / Task Envelope / Effective Envelope) is not modeled explicitly.

### What Astra Needs

**2.1 Role Envelope (Standing)**

A persistent envelope defined by a supervisor for a direct report. This is a new record type:

```python
@dataclass
class RoleEnvelope:
    id: str
    defining_role_address: str    # supervisor's positional address
    target_role_address: str      # direct report's positional address
    envelope: ConstraintEnvelope  # the 5-dimension constraints
    version: int
    created_at: datetime
    modified_at: datetime
```

Astra example:

```
CEO defines RoleEnvelope for Head of Trading:
  Financial: trading within regulatory capital limits; daily VaR limit
  Operational: execution within approved instruments
  Data Access: CONFIDENTIAL for trading data; BLOCKED for advisory client profiles
  Communication: counterparty autonomous; regulatory bodies BLOCKED (all via compliance)
  Temporal: market hours for trading
```

**2.2 Task Envelope (Ephemeral)**

A per-task narrowing of the Role Envelope. Expires when the task completes or at a deadline:

```python
@dataclass
class TaskEnvelope:
    id: str
    task_id: str
    parent_envelope_id: str       # the RoleEnvelope being narrowed
    envelope: ConstraintEnvelope  # tighter constraints for this task
    expires_at: datetime
```

Astra example: "Review Q3 trading positions" task narrows Head of Trading's envelope to read-only access to Q3 data only.

**2.3 Effective Envelope (Computed)**

The intersection of ALL ancestor envelopes from org root to current role. Never stored, always computed:

```python
def compute_effective_envelope(role_address: str) -> ConstraintEnvelope:
    """Walk the address chain from root to role, intersecting all envelopes."""
    ...
```

Astra example: A Junior Trader's effective envelope is the intersection of:

- Organization envelope (from BOD Genesis)
- CEO's RoleEnvelope for Head of Trading
- Head of Trading's RoleEnvelope for Senior Trader
- Senior Trader's RoleEnvelope for Junior Trader

**2.4 Monotonic Tightening Enforcement at Write Time**

Already partially exists. Needs to work with the new RoleEnvelope/TaskEnvelope types:

- Creating a RoleEnvelope that is wider than the parent's → REJECTED with specific dimension identified
- Creating a TaskEnvelope that is wider than its RoleEnvelope → REJECTED

**2.5 Default Envelopes by Trust Posture**

New roles start with conservative defaults based on their trust posture level (Pseudo → observe only; Delegated → full role envelope). The supervisor can then customize.

**2.6 Emergency Bypass**

Tiered bypass system (Tier 1: 4hr/supervisor; Tier 2: 24hr/two-up; Tier 3: 72hr/C-Suite). With:

- Hard auto-expiry
- Rate limiting (max 2 Tier 1 per role per 30 days)
- Mandatory post-incident review within 7 days
- Distinct audit records

Astra example: Market crisis requires the CRO to temporarily expand a trader's position limits beyond normal envelope. Tier 2 bypass, 24hr duration, CEO + CRO approval.

### Priority: HIGH

The existing envelope evaluation is the core. The 3-layer architecture, effective envelope computation, and emergency bypass are new.

---

## 3. Knowledge Clearance Framework

### Spec Reference

Part 4 (Sections 4.1–4.8) of the PACT Core Specification.

### Current State: PARTIAL

`ConfidentialityLevel` enum exists with correct EATP names (PUBLIC through TOP_SECRET). The envelope evaluates `confidentiality_clearance` in `_evaluate_confidentiality()`. But the full clearance model (per-role clearance assignment, compartments, posture-capping, clearance review cycles) is not implemented.

### What Astra Needs

**3.1 RoleClearance Record**

Per-role clearance assignment, independent of organizational authority:

```python
@dataclass
class RoleClearance:
    role_address: str                     # positional address
    max_clearance: ConfidentialityLevel   # PUBLIC through TOP_SECRET
    compartments: set[str]                # e.g., {"aml-investigations", "sanctions-screening"}
    granted_by_role_address: str          # who granted this clearance
    vetting_status: str                   # "pending", "active", "expired", "revoked"
    review_at: datetime                   # when clearance must be reviewed
    nda_signed: bool                      # required for SECRET+
```

Astra example:

- AML Officer (mid-level): SECRET clearance for `aml-investigations` compartment
- Head of Trading (senior): CONFIDENTIAL clearance only — no access to regulatory investigations
- Sanctions Officer (mid-level): SECRET clearance for `sanctions-screening` compartment

**3.2 Posture-Capped Effective Clearance**

```python
POSTURE_CEILING = {
    TrustPostureLevel.PSEUDO_AGENT: ConfidentialityLevel.PUBLIC,
    TrustPostureLevel.SUPERVISED: ConfidentialityLevel.RESTRICTED,
    TrustPostureLevel.SHARED_PLANNING: ConfidentialityLevel.CONFIDENTIAL,
    TrustPostureLevel.CONTINUOUS_INSIGHT: ConfidentialityLevel.SECRET,
    TrustPostureLevel.DELEGATED: ConfidentialityLevel.TOP_SECRET,  # role's full clearance
}

def effective_clearance(role_clearance: RoleClearance, posture: TrustPostureLevel) -> ConfidentialityLevel:
    return min(role_clearance.max_clearance, POSTURE_CEILING[posture])
```

Astra example: A new agent for the AML Officer starts at Pseudo posture. Even though the role has SECRET clearance, the agent can only access PUBLIC data until trust is earned.

**3.3 Compartment Enforcement**

SECRET and TOP_SECRET data is compartmented. Holding SECRET clearance doesn't grant access to ALL secret data — only to compartments the role is cleared for.

Astra example: The AML Officer has SECRET clearance for `aml-investigations` but NOT for `sanctions-screening`. They cannot see sanctions data even though both are SECRET-level.

**3.4 Clearance Review Cycles**

| Level        | Review Cycle   |
| ------------ | -------------- |
| PUBLIC       | Never expires  |
| RESTRICTED   | Every 2 years  |
| CONFIDENTIAL | Every 2 years  |
| SECRET       | Every 1 year   |
| TOP_SECRET   | Every 6 months |

Expired clearance auto-downgrades to the next lower level pending re-review.

**3.5 Clearance Grant/Revoke Workflow**

Assignment authority varies by level (see spec section 4.3). Must create EATP Capability Attestation records.

### Priority: HIGH

Astra's entire information barrier model depends on clearance being independent of organizational rank. This is the key differentiator from traditional RBAC.

---

## 4. Information Barriers (Containment Boundaries)

### Spec Reference

Parts 2.3 (containment), 4.6 (knowledge cascade), 4.7 (access enforcement algorithm).

### Current State: ABSENT

No explicit containment boundary enforcement. Delegation chains exist but don't model D/T containment as architectural barriers.

### What Astra Needs

**4.1 KnowledgeSharePolicy (KSP)**

Explicit policy allowing cross-boundary knowledge sharing between D/T units:

```python
@dataclass
class KnowledgeSharePolicy:
    id: str
    source_unit_address: str       # D/T unit sharing knowledge
    target_unit_address: str       # D/T unit receiving access
    max_classification: ConfidentialityLevel  # up to what level
    conditions: dict               # project scope, date range, etc.
    created_by_role_address: str
    active: bool
    expires_at: datetime | None
```

Astra example: **No KSP exists between Advisory (D1-R1-D2) and Trading (D1-R1-D3)**. This IS the information barrier. The absence of a KSP is architecturally enforced — not policy.

**4.2 Bridges (Standing Cross-Boundary Coordination)**

Standing or ad-hoc coordination channels between roles in different D/T units:

```python
@dataclass
class Bridge:
    id: str
    role_a_address: str            # e.g., CCO
    role_b_address: str            # e.g., Head of Advisory
    scope_description: str         # "Compliance monitoring of advisory activities"
    max_classification: ConfidentialityLevel
    operational_scope: list[str]   # what operations may cross the bridge
    financial_authority: bool      # does financial authority cross?
    bilateral: bool                # both sides agreed
    standing: bool                 # permanent or task-specific
```

Astra examples:

- **Compliance→Advisory Bridge**: CCO reads Advisory RESTRICTED data for compliance review
- **Risk→Trading Bridge**: CRO reads Trading CONFIDENTIAL data (positions, P&L); can trigger trading halt
- **Settlement→Trading Bridge**: Settlement reads trade confirmations (RESTRICTED); cannot read strategies (CONFIDENTIAL)

**4.3 Access Enforcement Algorithm**

The 5-step decision tree from spec section 4.7. This is the core engine:

```python
def can_access(
    role: Role,
    knowledge: KnowledgeItem,
    posture: TrustPostureLevel
) -> AccessDecision:
    """
    Step 1: Compute effective clearance (posture-capped)
    Step 2: Classification check
    Step 3: Compartment check (SECRET/TOP_SECRET only)
    Step 4: Containment check (same unit / downward / T-inherits-D / KSP / bridge)
    Step 5: Return ALLOW or DENY with audit log
    """
```

Astra example — the flagship scenario:

1. Advisory Analyst (D1-R1-D2-R1-T1-R1-R2) requests trading positions
2. Trading positions are in D1-R1-D3 (Trading Division)
3. Step 4a: Same unit? No (D2 ≠ D3)
4. Step 4b: Downward? No
5. Step 4c: T-inherits-D? No
6. Step 4d: KSP? **None exists** (information barrier)
7. Step 4e: Bridge? **None** (only Compliance and Risk have bridges to Trading)
8. Result: **BLOCKED** — "No access path: different division, no KSP, no bridge. Information barrier enforced."
9. Audit Anchor created

**4.4 Knowledge Cascade Rules**

Within same D/T:

- PUBLIC, RESTRICTED: automatic for all members
- CONFIDENTIAL+: pre-clearance required even within same unit

Across D/T boundaries:

- ALL cross-boundary access requires explicit KSP plus clearance checks
- No implicit cross-boundary grants at any classification level

T inherits from parent D:

- Team members see department-level knowledge at the same access level as direct D members

Trust lineage downward (posture-gated):

- Pseudo/Supervised: no downward read
- Shared Planning: read PUBLIC and RESTRICTED within subtree
- Continuous Insight: read up to CONFIDENTIAL
- Delegated: full read access up to role's own clearance

### Priority: CRITICAL

This is the single most important capability for Astra. The information barrier between Advisory and Trading is the flagship demonstration. Without containment boundary enforcement, KSPs, and bridges, Astra cannot exist.

---

## 5. Verification Gradient Enhancements

### Spec Reference

Part 3, Section 3.5 of the PACT Core Specification.

### Current State: MOSTLY COMPLETE

`GradientEngine` exists with the 4 zones and classification logic. `VerificationResult` has the right structure.

### What Astra Needs (Incremental)

**5.1 Per-Dimension Gradient Configuration**

The spec says supervisors can set different gradient thresholds for different dimensions within a Role Envelope. The current gradient engine uses rule-based pattern matching. It needs to also support dimension-specific threshold configuration:

```python
# Within a RoleEnvelope:
gradient_config:
  financial:
    auto_approved_up_to: 10000
    flagged_from: 10001
    held_from: 50001
    blocked_above: 100000
  data_access:
    auto_approved: ["treasury_ledger", "fx_rates"]
    flagged: ["counterparty_credit_data"]
    held: ["regulatory_filings"]
    blocked: ["personnel_records"]
```

**5.2 Held Action Human Decision Point**

When an action is Held, the system must prepare a bounded decision request for the human:

1. Action requested (plain language)
2. Why it was held (which dimension, threshold, proximity)
3. Context (task, objective)
4. Agent recommendation
5. Alternatives (proceed, deny, narrow)
6. Time limit (default: 4 hours)

**5.3 Timeout Behavior**

Configurable: default is "remain held + escalate to parent", with optional auto-approval after timeout.

### Priority: MEDIUM

The existing gradient engine works. These are refinements needed for production use.

---

## 6. EATP Integration (Governance Actions → Records)

### Spec Reference

Part 5 (Sections 5.1–5.4) of the PACT Core Specification.

### Current State: MOSTLY COMPLETE

`EATPBridge` handles establish/delegate/verify/audit. `AuditAnchor` and `AuditChain` exist.

### What Astra Needs (Incremental)

**6.1 PACT-Specific Record Subtypes**

New audit anchor subtypes for PACT governance actions:

- `envelope_created` / `envelope_modified` — Role/Task Envelope lifecycle
- `clearance_granted` / `clearance_revoked` — Clearance changes
- `emergency_bypass` — Bypass activation with tier, duration, justification
- `gradient_held_resolved` — Human decision on held action
- `gradient_flagged` — Flagged action notification
- `barrier_enforced` — Information barrier blocked an access attempt
- `ksp_created` / `ksp_revoked` — KnowledgeSharePolicy changes
- `bridge_established` / `bridge_revoked` — Bridge lifecycle
- `address_recomputed` — Org restructure

**6.2 Capability Attestation for Clearance**

When clearance is granted, create an EATP Capability Attestation. When revoked, supersede the old one.

### Priority: MEDIUM

The infrastructure exists. These are additional record types.

---

## 7. Organizational Store (Persistence)

### Spec Reference

Implied by all parts — the org structure, envelopes, clearances, KSPs, and bridges need persistence.

### Current State: PARTIAL

`OrgBuilder` can build org definitions. `EATPBridge` has store backends. But there's no unified store for the full PACT organizational model.

### What Astra Needs

**7.1 Org Structure Store**

Persistence for the D/T/R tree with positional addresses:

```python
class OrgStore(Protocol):
    async def save_org(self, org: Organization) -> None
    async def load_org(self, org_id: str) -> Organization
    async def get_node(self, address: str) -> OrgNode
    async def query_by_prefix(self, prefix: str) -> list[OrgNode]
    async def move_node(self, node_id: str, new_parent_address: str) -> None
```

**7.2 Envelope Store**

Persistence for Role Envelopes, Task Envelopes:

```python
class EnvelopeStore(Protocol):
    async def save_role_envelope(self, envelope: RoleEnvelope) -> None
    async def get_role_envelope(self, target_role_address: str) -> RoleEnvelope | None
    async def save_task_envelope(self, envelope: TaskEnvelope) -> None
    async def get_effective_envelope(self, role_address: str) -> ConstraintEnvelope
```

**7.3 Clearance Store**

Persistence for RoleClearance records:

```python
class ClearanceStore(Protocol):
    async def grant_clearance(self, clearance: RoleClearance) -> None
    async def get_clearance(self, role_address: str) -> RoleClearance | None
    async def revoke_clearance(self, role_address: str) -> None
    async def get_expiring_clearances(self, before: datetime) -> list[RoleClearance]
```

**7.4 KSP and Bridge Store**

Persistence for cross-boundary access policies:

```python
class AccessPolicyStore(Protocol):
    async def save_ksp(self, ksp: KnowledgeSharePolicy) -> None
    async def find_ksp(self, source_prefix: str, target_prefix: str) -> KnowledgeSharePolicy | None
    async def save_bridge(self, bridge: Bridge) -> None
    async def find_bridge(self, role_a_address: str, role_b_address: str) -> Bridge | None
```

### Priority: HIGH

Without persistence, the org structure lives only in memory.

---

## 8. Shadow Agent Planning Process

### Spec Reference

Part 6 (Sections 6.1–6.4) of the PACT Core Specification.

### Current State: PARTIAL

Agent runtime exists with session management and approval queues. But the structured 5-phase planning process (context gathering → capability discovery → decomposition → recommendation → execution) is not modeled explicitly.

### What Astra Needs

**8.1 Five-Layer Memory System**

The planning phase draws on:

1. **Organizational Memory** — vector store indexed by address prefix, clearance-filtered
2. **Role Context** — per-role knowledge, partitioned by classification
3. **Agent Registry** — capabilities, envelope summaries, availability
4. **Knowledge Base Search** — RAG with clearance as PRE-retrieval gate (critical security invariant)
5. **Task History** — similar past tasks, outcomes, lessons learned

**8.2 Planning Phase API**

```python
class PlanningPhase:
    async def gather_context(self, objective: str) -> PlanningContext
    async def discover_capabilities(self, context: PlanningContext) -> CapabilityMap
    async def design_decomposition(self, context, capabilities) -> TaskPlan
    async def present_recommendation(self, plan: TaskPlan) -> HumanDecision
    async def execute(self, plan: TaskPlan, decision: HumanDecision) -> TaskResult
```

**8.3 Security Invariants**

- Planning is read-only (no side effects)
- Clearance-before-retrieval (pre-filter, not post-filter)
- Registry access only (no execution access during planning)
- Plan approval before cascade (agent cannot self-authorize)
- Audit of planning phase itself

### Priority: LOW (for Astra v1)

Astra's first milestone is proving information barriers work. The planning process is important but can come after the core governance model is solid.

---

## Summary: Priority Matrix

| #   | Requirement                                                   | Priority | Spec Part | Current State   |
| --- | ------------------------------------------------------------- | -------- | --------- | --------------- |
| 1   | **Positional Addressing (D/T/R)**                             | CRITICAL | Part 2    | Absent          |
| 4   | **Information Barriers (KSP, Bridges, Access Algorithm)**     | CRITICAL | Parts 2,4 | Absent          |
| 3   | **Knowledge Clearance (per-role, compartments, posture-cap)** | HIGH     | Part 4    | Partial         |
| 2   | **Operating Envelopes (3-layer architecture)**                | HIGH     | Part 3    | Partial         |
| 7   | **Organizational Store**                                      | HIGH     | All       | Partial         |
| 5   | **Verification Gradient Enhancements**                        | MEDIUM   | Part 3    | Mostly complete |
| 6   | **EATP Record Subtypes**                                      | MEDIUM   | Part 5    | Mostly complete |
| 8   | **Shadow Agent Planning**                                     | LOW (v1) | Part 6    | Partial         |

### Suggested Build Order for PACT Core

1. **Positional Addressing** — Everything else depends on addresses
2. **Knowledge Clearance** — The per-role clearance model with compartments
3. **Information Barriers** — KSP, Bridges, and the Access Enforcement Algorithm
4. **3-Layer Envelopes** — Role/Task/Effective with address-based composition
5. **Organizational Store** — Persist all of the above
6. **EATP Record Subtypes** — Governance actions → audit trail
7. **Gradient Enhancements** — Per-dimension thresholds, held action UX
8. **Planning Process** — 5-layer memory, 5-phase planning

Items 1-5 are the **minimum viable PACT** that Astra needs to demonstrate the flagship scenario (advisory analyst blocked from trading data).

---

## Astra's Role (What We Build on Top)

Once PACT provides the above, Astra configures it with:

1. **Financial institution D/T/R structure** — the specific org chart from the brief (Board, CEO Office, Compliance, Advisory, Trading, Risk, Operations)
2. **MAS regulatory clearance mappings** — what PUBLIC/RESTRICTED/CONFIDENTIAL/SECRET/TOP_SECRET mean for financial data (published rates, client records, proprietary strategies, SAR filings, crisis plans)
3. **Financial operating envelopes** — regulatory capital limits, VaR limits, position limits, counterparty exposure, instrument restrictions
4. **MAS-specific information barriers** — Advisory-Trading separation per SFA 04-N09, with Compliance and Risk bridges
5. **Financial verification gradient calibration** — regulatory thresholds mapped to auto-approved/flagged/held/blocked
6. **Regulatory knowledge** — SFA, FAA, CDSA, PDPA mapped to PACT concepts
7. **The flagship demo** — advisory analyst's agent blocked from trading floor positions, with full audit trail

Astra is pure configuration and domain knowledge. Zero governance engine code.
