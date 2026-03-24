# PACT Core Library: Requirements Analysis

**Date**: 2026-03-21
**Author**: Requirements Analyst
**Input**: Astra requirements brief, PACT gap analysis, PACT Core Specification v0.1
**Scope**: Minimum viable PACT framework for Astra flagship scenario

---

## 1. Scope Definition

### The Flagship Scenario

An advisory analyst's agent requests trading position data. The system must:

1. Compute positional addresses for both the advisory analyst and the trading data owner
2. Determine that these positions are in different D/T containment boundaries (Advisory vs Trading)
3. Check whether a KnowledgeSharePolicy or Bridge exists between those boundaries
4. Find none (the information barrier)
5. Return BLOCKED with an auditable reason
6. Create an EATP Audit Anchor recording the enforcement

### Minimum Viable Scope (Items 1-5 from Astra brief)

The minimum viable PACT framework requires five capabilities, in dependency order:

1. **Positional Addressing** -- D/T/R grammar, address computation, prefix queries
2. **Knowledge Clearance** -- per-role clearance, compartments, posture-capping
3. **Information Barriers** -- KSP, Bridge (PACT-native), access enforcement algorithm
4. **3-Layer Envelopes** -- RoleEnvelope, TaskEnvelope, effective envelope computation
5. **Organizational Store** -- persistence for all new record types

### Explicit Exclusions (v1)

- Emergency bypass system (Tiers 1-3) -- needed but deferred past MVP
- Shadow agent planning process (5-layer memory, 5-phase planning)
- Per-dimension gradient thresholds (existing GradientEngine is sufficient for MVP)
- Clearance review cycles (auto-downgrade on expiry) -- tracked but not blocking
- Address recomputation on reorganization -- full pipeline deferred; initial computation required

### Relationship to Existing Code

| Existing Module                                                             | Disposition | Notes                                                      |
| --------------------------------------------------------------------------- | ----------- | ---------------------------------------------------------- |
| `ConstraintEnvelope` (`trust/constraint/envelope.py`)                       | EXTEND      | Reuse evaluation logic; wrap in RoleEnvelope/TaskEnvelope  |
| `DelegationManager` (`trust/delegation.py`)                                 | EXTEND      | Tightening validation reused for envelope chain            |
| `OrgBuilder` / `OrgDefinition` (`build/org/builder.py`)                     | EXTEND      | Add address compilation step; add Role as first-class node |
| `BridgeTrustManager` (`trust/bridge_trust.py`)                              | REWORK      | Team-based bridges become address-based; add KSP concept   |
| `Bridge` / `BridgePermission` (`build/workspace/bridge.py`)                 | REWORK      | Workspace bridges evolve to PACT positional bridges        |
| `ConfidentialityLevel` / `CONFIDENTIALITY_ORDER` (`build/config/schema.py`) | KEEP        | Already correct (PUBLIC through TOP_SECRET)                |
| `GradientEngine` (`trust/constraint/gradient.py`)                           | KEEP        | Sufficient for MVP                                         |
| `EATPBridge` (`trust/eatp_bridge.py`)                                       | EXTEND      | Add new audit anchor subtypes                              |

---

## 2. Requirements Breakdown

### PACT-REQ-001: Address Type and Grammar Validator

**Title**: D/T/R Address Type with Grammar Validation

**Description**: Implement an `Address` value type that represents a positional address in the D/T/R grammar. The type must parse address strings (e.g., `"D1-R1-D3-R1-T1-R1"`), validate them against the grammar constraint (every D or T must be immediately followed by exactly one R), and support prefix-containment queries.

**Acceptance Criteria**:

- `Address.parse("D1-R1-D3-R1-T1-R1")` returns a valid Address with 6 typed segments
- `Address.parse("D1-D2-R1")` raises `GrammarError` (D followed by D, no head R for D1)
- `Address.parse("D1-T1-R1")` raises `GrammarError` (D followed by T, no head R for D1)
- `address.segments` returns `[D(1), R(1), D(3), R(1), T(1), R(1)]`
- `address.is_prefix_of(other_address)` returns True when self is a proper prefix
- `address.parent` returns the address with the last segment removed
- `address.depth` returns the number of segments
- `address.containment_unit` returns the nearest ancestor D or T address
- `address.accountability_chain` returns all R segments in order
- `str(address)` round-trips to the canonical string form
- Grammar state machine rejects all invalid sequences per spec Section 2.2
- BOD root has no address (implicit origin); first D under BOD is `D1`

**Dependencies**: None (foundational)

**Complexity**: M

---

### PACT-REQ-002: Organization Compilation with Address Assignment

**Title**: Org Tree Compilation Step that Assigns Positional Addresses

**Description**: Extend the existing `OrgBuilder` / `OrgDefinition` with a compilation step that traverses the organizational tree and assigns positional addresses to every node. The compilation step also validates grammar constraints and auto-creates vacant head roles where D or T nodes lack them (skeleton enforcement).

This is a new compilation pass, not a replacement of OrgBuilder. OrgBuilder continues to accept flat IDs; compilation materializes addresses.

**Acceptance Criteria**:

- `OrgDefinition` gains a `roles` field (list of `RoleDefinition`) as first-class nodes
- `RoleDefinition` includes: `role_id`, `name`, `reports_to_role_id`, `is_primary_for_unit`, `is_vacant`, `is_external`, `address` (computed)
- `DepartmentConfig` and `TeamConfig` gain an `address` field (computed, optional until compilation)
- `compile_org(org: OrgDefinition) -> CompiledOrg` traverses the tree, assigns addresses, validates grammar
- Skeleton enforcement: if a D or T has no primary R, compilation auto-creates a vacant role and emits a warning
- `CompiledOrg.get_node(address: str) -> OrgNode` returns any node by address
- `CompiledOrg.query_by_prefix(prefix: str) -> list[OrgNode]` returns all nodes under a prefix
- `CompiledOrg.get_subtree(address: str) -> list[OrgNode]` returns the full subtree
- The compilation step is idempotent: running it twice produces the same addresses
- BOD members get addresses `R1`, `R2`, etc. (no D/T prefix)
- Compilation rejects org trees with grammar violations (after skeleton enforcement)

**Dependencies**: PACT-REQ-001

**Complexity**: L

---

### PACT-REQ-003: Role Clearance Model

**Title**: Per-Role Knowledge Clearance with Compartments and Posture Capping

**Description**: Implement the `RoleClearance` record type that assigns a knowledge clearance level to a specific role, independent of organizational seniority. Include compartment support for SECRET and TOP_SECRET data, and posture-capping that limits effective clearance based on the agent's current trust posture.

**Acceptance Criteria**:

- `RoleClearance` dataclass with: `role_address`, `max_clearance` (ConfidentialityLevel), `compartments` (frozenset of strings), `granted_by_role_address`, `vetting_status` (pending/active/expired/revoked), `review_at` (datetime), `nda_signed` (bool)
- `effective_clearance(role_clearance, posture)` returns `min(role_clearance.max_clearance, POSTURE_CEILING[posture])`
- `POSTURE_CEILING` mapping: PSEUDO_AGENT -> PUBLIC, SUPERVISED -> RESTRICTED, SHARED_PLANNING -> CONFIDENTIAL, CONTINUOUS_INSIGHT -> SECRET, DELEGATED -> TOP_SECRET
- Clearance grant validates that the granting role has sufficient authority (granting role's clearance >= granted clearance)
- Clearance grant for SECRET+ requires `nda_signed = True`
- Compartment assignment validates that the granting role has access to the specified compartments
- `to_dict()` and `from_dict()` round-trip correctly
- Vetting status transitions: pending -> active, active -> expired, active -> revoked (no backward transitions)

**Dependencies**: PACT-REQ-001 (uses positional addresses)

**Complexity**: M

---

### PACT-REQ-004: Knowledge Item Classification

**Title**: Knowledge Item Metadata for Access Enforcement

**Description**: Define the `KnowledgeItem` type that represents a piece of data or knowledge with its classification, compartment, and owning organizational unit. This is the target object in access enforcement decisions.

**Acceptance Criteria**:

- `KnowledgeItem` dataclass with: `item_id`, `classification` (ConfidentialityLevel), `compartments` (frozenset of strings), `owning_unit_address` (str -- the D or T address that owns this data), `description` (str)
- Classification must be one of the five ConfidentialityLevel values
- Compartments are only meaningful for SECRET and TOP_SECRET; empty set for lower levels
- `owning_unit_address` must parse as a valid address (or a valid D/T prefix)
- `to_dict()` and `from_dict()` round-trip correctly

**Dependencies**: PACT-REQ-001

**Complexity**: S

---

### PACT-REQ-005: Knowledge Share Policy (KSP)

**Title**: Explicit Cross-Boundary Knowledge Sharing Policies

**Description**: Implement the `KnowledgeSharePolicy` record type that explicitly permits knowledge sharing between two organizational units. The absence of a KSP between units IS the information barrier -- architectural enforcement, not policy.

**Acceptance Criteria**:

- `KnowledgeSharePolicy` dataclass with: `id`, `source_unit_address` (D/T prefix), `target_unit_address` (D/T prefix), `max_classification` (ConfidentialityLevel), `compartments` (frozenset -- only shares within these compartments), `conditions` (dict), `created_by_role_address`, `active` (bool), `expires_at` (datetime or None)
- KSP creation validates that `created_by_role_address` is a common ancestor of both units (or BOD-level)
- KSP `max_classification` cannot exceed the creator's own clearance
- KSP between the same unit is rejected (intra-unit sharing is governed by cascade rules, not KSP)
- `find_ksp(source_prefix, target_prefix)` returns the applicable KSP if one exists
- KSP is bidirectional only if explicitly configured (default is one-way: source shares TO target)
- `to_dict()` and `from_dict()` round-trip correctly
- Expired KSPs are treated as non-existent

**Dependencies**: PACT-REQ-001, PACT-REQ-003

**Complexity**: M

---

### PACT-REQ-006: PACT Bridge (Address-Based)

**Title**: Cross-Boundary Bridges Between Roles (Positional)

**Description**: Rework the existing `BridgeTrustManager` and workspace `Bridge` to operate on positional addresses rather than flat team IDs. A PACT Bridge connects two roles (by address) across organizational boundaries and defines what may flow between them -- classification ceiling, operational scope, and financial authority.

**Acceptance Criteria**:

- `PactBridge` dataclass with: `id`, `role_a_address`, `role_b_address`, `bridge_type` (Standing/Scoped/Ad-Hoc), `max_classification` (ConfidentialityLevel), `operational_scope` (list of permitted operations), `financial_authority` (bool), `bilateral` (bool -- both sides agreed), `standing` (bool), `expires_at` (datetime or None), `status` (reuse existing `BridgeStatus`)
- Bridge creation validates that `role_a_address` and `role_b_address` are in different containment units
- Bridge creation requires bilateral agreement when `bilateral=True`
- `find_bridge(role_a_address, role_b_address)` finds an active bridge between two roles
- A bridge between Compliance (D1-R1-D1) and Trading (D1-R1-D3) allows the CCO's agent to read Trading data up to the bridge's `max_classification`
- Existing `BridgeType` enum (Standing/Scoped/Ad-Hoc) and `BridgeStatus` enum are reused
- The existing `BridgePermission` model is mapped to the new address-based bridge
- `to_dict()` and `from_dict()` round-trip correctly

**Dependencies**: PACT-REQ-001, PACT-REQ-003

**Complexity**: M

---

### PACT-REQ-007: Access Enforcement Algorithm

**Title**: 5-Step Knowledge Access Decision Engine

**Description**: Implement the core access enforcement algorithm from spec sections 4.6-4.7. This is the engine that determines whether a role's agent can access a given knowledge item, considering clearance, classification, compartments, containment, KSPs, and bridges. This is the single most important requirement for the flagship scenario.

**Acceptance Criteria**:

- `can_access(role_address, knowledge_item, posture, compiled_org, clearance_store, ksp_store, bridge_store) -> AccessDecision`
- `AccessDecision` includes: `allowed` (bool), `reason` (str -- human-readable), `step_failed` (int or None -- which of the 5 steps caused denial), `audit_details` (dict)
- Step 1: Compute effective clearance via posture-capping. If effective clearance < item classification -> DENY ("Insufficient clearance")
- Step 2: Classification check passes if effective clearance >= item classification
- Step 3: Compartment check (SECRET/TOP_SECRET only). Role must have all compartments the item requires. Missing compartments -> DENY ("Missing compartments: {list}")
- Step 4: Containment check with 5 sub-steps:
  - 4a: Same unit (role's containment unit == item's owning unit) -> ALLOW
  - 4b: Downward (role's address is a prefix of item's owning unit) -> ALLOW (posture-gated: Shared Planning+ for RESTRICTED, Continuous Insight+ for CONFIDENTIAL, Delegated for SECRET+)
  - 4c: T-inherits-D (role is in a T under the D that owns the item) -> ALLOW at same access level
  - 4d: KSP exists from item's owning unit to role's containment unit -> ALLOW up to KSP max_classification
  - 4e: Bridge exists between a role in item's owning unit and the requesting role -> ALLOW up to bridge max_classification
- Step 5: No access path found -> DENY ("No access path: different {unit_type}, no KSP, no bridge. Information barrier enforced.")
- The flagship test: advisory analyst (D1-R1-D2-...) requesting trading data (owned by D1-R1-D3) with no KSP and no bridge -> BLOCKED with message identifying the information barrier
- Every access decision (ALLOW or DENY) produces audit details suitable for an Audit Anchor

**Dependencies**: PACT-REQ-001, PACT-REQ-002, PACT-REQ-003, PACT-REQ-004, PACT-REQ-005, PACT-REQ-006

**Complexity**: XL

---

### PACT-REQ-008: Knowledge Cascade Rules

**Title**: Intra-Unit and Cross-Unit Knowledge Flow Rules

**Description**: Implement the knowledge cascade rules that govern how knowledge flows within and across organizational boundaries. These rules feed into the access enforcement algorithm (specifically Step 4).

**Acceptance Criteria**:

- Within same D/T unit:
  - PUBLIC and RESTRICTED: automatic access for all members (no additional check beyond clearance)
  - CONFIDENTIAL and above: pre-clearance required even within same unit
- Across D/T boundaries:
  - ALL cross-boundary access requires explicit KSP plus clearance checks
  - No implicit cross-boundary grants at any classification level
- T-inherits-D rule:
  - Team members see department-level knowledge at the same access level as direct department members
  - Implemented as: if role is in T, and T's parent D owns the item, treat as same-unit access
- Trust lineage downward (posture-gated):
  - PSEUDO_AGENT / SUPERVISED: no downward read access
  - SHARED_PLANNING: read PUBLIC and RESTRICTED within subtree
  - CONTINUOUS_INSIGHT: read up to CONFIDENTIAL within subtree
  - DELEGATED: full read access up to role's own clearance within subtree
- Cascade rules are pure functions (no side effects, no persistence)

**Dependencies**: PACT-REQ-001, PACT-REQ-003

**Complexity**: M

---

### PACT-REQ-009: Role Envelope (Standing)

**Title**: Standing Operating Envelope Defined by Supervisor for Direct Report

**Description**: Implement the `RoleEnvelope` record type -- a persistent operating boundary defined by a supervisor role for a direct report role. The RoleEnvelope wraps an existing `ConstraintEnvelope` and adds supervisor/target addressing, versioning, and the link to the address tree.

**Acceptance Criteria**:

- `RoleEnvelope` dataclass with: `id`, `defining_role_address` (supervisor), `target_role_address` (direct report), `envelope` (ConstraintEnvelope), `version` (int), `created_at` (datetime), `modified_at` (datetime)
- Creation validates that `defining_role_address` is the direct supervisor of `target_role_address` in the compiled org
- Creation validates monotonic tightening: the new RoleEnvelope's constraints must be tighter than or equal to the defining role's own effective envelope
- Existing `ConstraintEnvelope.is_tighter_than()` logic is reused for the tightening check
- Versioning: modifying a RoleEnvelope increments the version and updates `modified_at`
- A role without an explicit RoleEnvelope operates under its parent's effective envelope (default behavior)
- `to_dict()` and `from_dict()` round-trip correctly

**Dependencies**: PACT-REQ-001, PACT-REQ-002

**Complexity**: M

---

### PACT-REQ-010: Task Envelope (Ephemeral)

**Title**: Per-Task Narrowing of Role Envelope with Auto-Expiry

**Description**: Implement the `TaskEnvelope` record type -- an ephemeral narrowing of a RoleEnvelope for a specific task. Task Envelopes expire when the task completes or at a configured deadline.

**Acceptance Criteria**:

- `TaskEnvelope` dataclass with: `id`, `task_id`, `parent_envelope_id` (the RoleEnvelope being narrowed), `envelope` (ConstraintEnvelope), `expires_at` (datetime), `created_at` (datetime)
- Creation validates monotonic tightening: TaskEnvelope must be tighter than or equal to the parent RoleEnvelope
- Expired TaskEnvelopes are treated as non-existent (agent falls back to RoleEnvelope)
- `is_expired` property checks against current time
- When no TaskEnvelope is active, the RoleEnvelope is the operative envelope
- `to_dict()` and `from_dict()` round-trip correctly

**Dependencies**: PACT-REQ-009

**Complexity**: S

---

### PACT-REQ-011: Effective Envelope Computation

**Title**: Compute Effective Envelope by Walking Address Chain

**Description**: Implement `compute_effective_envelope(role_address, compiled_org, envelope_store)` that walks from the organization root down to the specified role, intersecting all ancestor RoleEnvelopes (and any active TaskEnvelope) to produce the tightest applicable ConstraintEnvelope.

**Acceptance Criteria**:

- `compute_effective_envelope(role_address, ...) -> ConstraintEnvelope` returns the intersection of all envelopes in the chain
- For a role at `D1-R1-D3-R1-T1-R1-R2`, the effective envelope is the intersection of:
  - Organization envelope (from Genesis / BOD)
  - RoleEnvelope for D1-R1 (CEO)
  - RoleEnvelope for D1-R1-D3-R1 (Head of Trading)
  - RoleEnvelope for D1-R1-D3-R1-T1-R1 (Senior Trader / Equities Desk Lead)
  - RoleEnvelope for D1-R1-D3-R1-T1-R1-R2 (Junior Trader)
  - Any active TaskEnvelope for the current task
- If any ancestor lacks a RoleEnvelope, that level is skipped (the parent's effective envelope passes through)
- The effective envelope is NEVER stored -- always computed on demand
- Degenerate envelope detection: if the effective envelope is so tight that no meaningful action is possible, emit a warning (but do not block)
- The computation uses the existing `ConstraintEnvelope.is_tighter_than()` intersection logic

**Dependencies**: PACT-REQ-001, PACT-REQ-002, PACT-REQ-009, PACT-REQ-010

**Complexity**: L

---

### PACT-REQ-012: Organizational Store Protocols

**Title**: Persistence Protocols for All PACT Record Types

**Description**: Define Python `Protocol` classes for persisting the new PACT record types: compiled org (with address index), RoleEnvelopes, TaskEnvelopes, RoleClearances, KSPs, and Bridges. Provide an in-memory reference implementation.

**Acceptance Criteria**:

- `OrgStore` protocol: `save_org`, `load_org`, `get_node(address)`, `query_by_prefix(prefix)`
- `EnvelopeStore` protocol: `save_role_envelope`, `get_role_envelope(target_role_address)`, `save_task_envelope`, `get_active_task_envelope(role_address, task_id)`, `get_ancestor_envelopes(role_address)`
- `ClearanceStore` protocol: `grant_clearance`, `get_clearance(role_address)`, `revoke_clearance`, `get_expiring_clearances(before)`
- `AccessPolicyStore` protocol: `save_ksp`, `find_ksp(source_prefix, target_prefix)`, `save_bridge`, `find_bridge(role_a_address, role_b_address)`, `list_bridges_for_role(role_address)`
- In-memory implementations for all four protocols (for testing and development)
- All store operations validate inputs (address format, required fields)
- Bounded in-memory stores (maxlen per trust-plane security rules)

**Dependencies**: PACT-REQ-002, PACT-REQ-003, PACT-REQ-005, PACT-REQ-006, PACT-REQ-009, PACT-REQ-010

**Complexity**: L

---

### PACT-REQ-013: EATP Audit Anchor Subtypes

**Title**: PACT Governance Action Audit Trail via EATP Records

**Description**: Define audit anchor subtypes for PACT governance actions so that every governance event is recorded in the existing EATP audit chain. This extends the existing `AuditAnchor` and `EATPBridge` with new action types.

**Acceptance Criteria**:

- New audit anchor action types (string constants):
  - `envelope_created`, `envelope_modified` -- Role/Task Envelope lifecycle
  - `clearance_granted`, `clearance_revoked` -- Clearance changes
  - `barrier_enforced` -- Information barrier blocked an access attempt
  - `ksp_created`, `ksp_revoked` -- KnowledgeSharePolicy changes
  - `bridge_established`, `bridge_revoked` -- Bridge lifecycle
  - `address_computed` -- Address assignment during compilation
- Each action type has a defined payload schema (what fields must be in the anchor's `details`)
- `barrier_enforced` anchor includes: requesting role address, target knowledge item, step that failed, reason
- Helper function `create_pact_audit_anchor(action_type, details, ...) -> AuditAnchor` wraps the existing EATP audit infrastructure
- Existing `EATPBridge.create_audit_anchor()` is reused; new subtypes are additive

**Dependencies**: None (extends existing infrastructure)

**Complexity**: M

---

### PACT-REQ-014: Default Envelopes by Trust Posture

**Title**: Conservative Default Envelopes Based on Trust Posture Level

**Description**: When a new role is created or a new agent is attached to a role, and no explicit RoleEnvelope has been defined, provide conservative default envelopes calibrated to the agent's trust posture level.

**Acceptance Criteria**:

- `default_envelope_for_posture(posture: TrustPostureLevel) -> ConstraintEnvelopeConfig` returns sensible defaults:
  - PSEUDO_AGENT: observe only (no writes, no external communication, no financial authority, PUBLIC clearance only)
  - SUPERVISED: limited execution (write with approval, internal communication, minimal financial, RESTRICTED clearance)
  - SHARED_PLANNING: moderate execution (write within scope, internal + approved external, moderate financial, CONFIDENTIAL clearance)
  - CONTINUOUS_INSIGHT: broad execution (full write, external with notification, substantial financial, SECRET clearance)
  - DELEGATED: full role envelope (all capabilities, full communication, full financial within role, TOP_SECRET clearance if role has it)
- Defaults are overridable -- they are starting points, not hard constraints
- Defaults are used when `compute_effective_envelope` encounters a role with no explicit RoleEnvelope

**Dependencies**: PACT-REQ-009

**Complexity**: S

---

## 3. Architecture Decision Records

---

### ADR-001: Positional Address Computation Strategy

#### Status

Proposed

#### Context

The existing `OrgBuilder` and `OrgDefinition` use flat string IDs (`agent_id`, `team_id`, `department_id`) with no hierarchical addressing. The PACT specification requires globally unique positional addresses that encode the full containment and accountability path (e.g., `D1-R1-D3-R1-T1-R1`).

The key question is whether to embed address computation directly into `OrgBuilder` (making it the primary model) or to introduce a separate compilation step that takes a flat `OrgDefinition` and produces a `CompiledOrg` with materialized addresses.

There are constraints to consider:

- The existing `OrgDefinition` has no concept of `Role` as a first-class node -- roles are implied by `AgentConfig` and `team_lead` fields
- `DepartmentConfig` and `TeamConfig` use flat string IDs with no parent/child relationship beyond the `teams` list in departments
- The current model supports org -> department -> team -> agent, but the PACT specification requires arbitrary nesting (D-R-D-R-D-R-T-R-R)

#### Decision

Introduce a **two-phase model**: OrgBuilder remains the input API (how users define organizations), and a new `compile_org()` function produces a `CompiledOrg` with materialized addresses. This is a compilation pass, analogous to how compilers separate parsing from code generation.

**Phase 1: Extend OrgDefinition with Role nodes**

Add `RoleDefinition` as a first-class node type to `OrgDefinition`:

```python
class RoleDefinition(BaseModel):
    role_id: str
    name: str
    reports_to_role_id: str | None  # parent role (None = BOD-level)
    is_primary_for_unit: bool       # mandatory head role for a D or T
    unit_id: str | None             # which D or T this role heads (if primary)
    is_vacant: bool = False
    is_external: bool = False       # BOD members
    agent_id: str | None = None     # attached agent (if any)
    address: str | None = None      # computed during compilation
```

**Phase 2: compile_org() produces CompiledOrg**

```python
def compile_org(org: OrgDefinition) -> CompiledOrg:
    """
    1. Build parent-child tree from reports_to_role_id chains
    2. Validate grammar (every D/T followed by exactly one R)
    3. Auto-create vacant head roles where missing (skeleton enforcement)
    4. Assign addresses via depth-first traversal
    5. Build prefix index for efficient queries
    """
```

**Why not embed in OrgBuilder directly?**

- OrgBuilder is a configuration API; it should remain simple and forgiving during construction
- Grammar validation and address assignment are compile-time checks, not build-time checks
- Users should be able to build an org incrementally (add departments, then teams, then roles) without grammar enforcement at every step
- The compilation step is idempotent and can be re-run after any modification

#### Consequences

##### Positive

- Clean separation of concerns: OrgBuilder handles user input, compilation handles governance enforcement
- Existing OrgBuilder code remains backward compatible -- no breaking changes
- Compilation step can be extended (e.g., for address recomputation on reorganization) without touching OrgBuilder
- The `CompiledOrg` becomes the single source of truth for address-dependent operations (access enforcement, envelope computation)

##### Negative

- Two representations of the org (OrgDefinition and CompiledOrg) must be kept in sync
- Consumers must remember to compile before using address-dependent features
- The Role node adds a new first-class entity that did not exist before, increasing model surface area

##### Mitigated By

- `CompiledOrg` is always derived from `OrgDefinition` -- never independently constructed
- A `compile_and_validate()` convenience method combines both steps
- Documentation makes clear that addresses are only available after compilation

#### Alternatives Considered

**Option A: Embed addresses directly in OrgBuilder**

Modify `DepartmentConfig`, `TeamConfig`, and `AgentConfig` to carry address fields that are computed and enforced during `add_department()`, `add_team()`, etc.

Rejected because: This couples the build-time API to the grammar constraint, making incremental construction painful. Adding a department before its head role would fail, even though the user intends to add the head role next. The current OrgBuilder is intentionally lenient during construction with validation at the end (`validate_org()`).

**Option B: Replace OrgDefinition entirely with a tree-native model**

Discard the flat-ID model and design a new tree-native OrgDefinition where D/T/R nodes are nested.

Rejected because: This would break all existing configuration files, tests, and the template system. The two-phase approach preserves full backward compatibility while adding the new capability.

---

### ADR-002: 3-Layer Envelope Integration with Existing ConstraintEnvelope

#### Status

Proposed

#### Context

The existing `ConstraintEnvelope` (in `trust/constraint/envelope.py`) is a complete evaluation engine with all five constraint dimensions, tightening validation, versioning, expiry, and content hashing. It wraps a `ConstraintEnvelopeConfig` (from `build/config/schema.py`).

The PACT specification requires three envelope layers: RoleEnvelope (standing), TaskEnvelope (ephemeral), and Effective Envelope (computed intersection). The question is whether to extend `ConstraintEnvelope` to carry the layer semantics, or to create new wrapper types that compose with the existing `ConstraintEnvelope`.

#### Decision

**Create new wrapper types that compose with `ConstraintEnvelope`**. RoleEnvelope and TaskEnvelope are new record types that CONTAIN a `ConstraintEnvelope` (has-a, not is-a). The Effective Envelope is computed by intersecting multiple `ConstraintEnvelope` instances.

```python
@dataclass(frozen=True)
class RoleEnvelope:
    id: str
    defining_role_address: str      # supervisor
    target_role_address: str        # direct report
    envelope: ConstraintEnvelope    # the actual constraints (reuse existing)
    version: int
    created_at: datetime
    modified_at: datetime

@dataclass(frozen=True)
class TaskEnvelope:
    id: str
    task_id: str
    parent_envelope_id: str         # which RoleEnvelope
    envelope: ConstraintEnvelope    # tighter constraints for this task
    expires_at: datetime
    created_at: datetime
```

The `compute_effective_envelope()` function walks the address chain and intersects `ConstraintEnvelope` instances:

```python
def compute_effective_envelope(
    role_address: str,
    compiled_org: CompiledOrg,
    envelope_store: EnvelopeStore,
    task_id: str | None = None,
) -> ConstraintEnvelope:
    """Intersect all ancestor envelopes from root to role."""
```

The intersection operation uses the existing `is_tighter_than()` logic, applied dimension by dimension. The result is a new `ConstraintEnvelope` with the tightest constraint from each dimension across all ancestors.

**Why composition over inheritance?**

- `ConstraintEnvelope` is a Pydantic `BaseModel` with `frozen=True`. Subclassing frozen Pydantic models introduces complexity with field ordering and `__init__` signatures.
- RoleEnvelope and TaskEnvelope are PACT-layer concepts; `ConstraintEnvelope` is a trust-layer primitive. Mixing layers would create confusing import paths.
- The new types are `dataclass(frozen=True)` per EATP conventions, while `ConstraintEnvelope` is a Pydantic model. Different serialization conventions.

#### Consequences

##### Positive

- Zero changes to existing `ConstraintEnvelope` code -- it continues to work as-is
- The new types add PACT semantics (supervisor, target, address) without polluting the trust-layer primitive
- `ConstraintEnvelope.evaluate_action()` remains the single evaluation entry point
- The effective envelope is just a `ConstraintEnvelope` -- all existing evaluation code works on it directly

##### Negative

- Two levels of wrapping: `RoleEnvelope.envelope.config.financial.max_spend_usd` is deep
- Intersection logic must be implemented (new function to intersect two `ConstraintEnvelopeConfig` instances)

##### Mitigated By

- Convenience properties on RoleEnvelope: `role_envelope.evaluate_action(...)` delegates to `self.envelope.evaluate_action(...)`
- `intersect_envelopes(a: ConstraintEnvelopeConfig, b: ConstraintEnvelopeConfig) -> ConstraintEnvelopeConfig` is a pure function, easy to test

#### Alternatives Considered

**Option A: Extend ConstraintEnvelope with layer fields**

Add `layer_type`, `defining_role_address`, `target_role_address` to `ConstraintEnvelope`.

Rejected because: This mixes PACT-layer concepts into a trust-layer primitive. `ConstraintEnvelope` is used throughout the codebase for non-PACT purposes (e.g., in delegation chains, in the gradient engine). Adding PACT-specific fields would confuse consumers and violate the layer boundary.

**Option B: Replace ConstraintEnvelope with a new PACT-native envelope**

Design a new envelope type from scratch that inherently supports layers.

Rejected because: The existing `ConstraintEnvelope` has 400+ lines of battle-tested evaluation logic, 10+ red team rounds of security hardening, and is deeply integrated with the delegation manager, gradient engine, and signing pipeline. Replacing it would be a massive regression risk for zero functional gain.

---

### ADR-003: Information Barrier Enforcement Architecture

#### Status

Proposed

#### Context

Information barriers are the flagship capability for Astra. The PACT specification defines barriers as the ABSENCE of access paths -- if no KSP and no Bridge exists between two organizational units, access is denied. The barrier is architectural, not policy-based.

The question is whether to build information barrier enforcement as a new subsystem, or to extend the existing `bridge_trust.py` and workspace bridge infrastructure.

The existing bridge infrastructure:

- `build/workspace/bridge.py`: Defines `Bridge`, `BridgePermission`, `BridgeType`, `BridgeStatus`, `BridgeManager` -- team-based, workspace-oriented
- `trust/bridge_trust.py`: `BridgeTrustManager` -- wraps EATP delegations for bridges, team-based
- `trust/constraint/bridge_envelope.py`: Bridge envelope evaluation

These are all team-ID-based and workspace-oriented. The PACT specification requires address-based bridges between roles, plus a new concept (KSP) that does not exist at all.

#### Decision

**Create a new `pact.governance` subpackage** that contains the access enforcement engine, KSP management, and PACT-native bridge management. This is a new subsystem that sits ABOVE the existing trust layer and USES it, but does not modify it.

```
src/pact/
  governance/                  # NEW: PACT governance enforcement
    __init__.py
    addressing.py              # Address type, grammar validator
    compilation.py             # compile_org(), CompiledOrg
    clearance.py               # RoleClearance, effective_clearance()
    knowledge.py               # KnowledgeItem, KnowledgeSharePolicy
    bridge.py                  # PactBridge (address-based)
    access.py                  # can_access(), AccessDecision
    cascade.py                 # Knowledge cascade rules
    envelopes.py               # RoleEnvelope, TaskEnvelope, compute_effective_envelope()
    defaults.py                # default_envelope_for_posture()
    audit.py                   # PACT-specific audit anchor subtypes
    store/
      __init__.py              # Store protocols
      memory.py                # In-memory implementations
```

The new `governance` package:

- IMPORTS from `trust/constraint/envelope.py` (uses `ConstraintEnvelope` as-is)
- IMPORTS from `trust/eatp_bridge.py` (uses `EATPBridge` for audit anchors)
- IMPORTS from `build/config/schema.py` (uses `ConfidentialityLevel`, `TrustPostureLevel`, config types)
- IMPORTS from `build/org/builder.py` (uses `OrgDefinition` as input)
- Does NOT modify any existing module

**Why not extend bridge_trust.py?**

The existing bridge infrastructure is fundamentally team-ID-based. Refactoring it to be address-based would require changing its API surface, breaking all existing bridge tests and consumers. The PACT bridge concept is semantically different: it connects roles (not teams), operates on positional addresses (not flat IDs), and is part of the access enforcement algorithm (not just trust establishment).

**Why a new subpackage rather than scattered files?**

All the new PACT governance concepts are tightly coupled: access enforcement calls clearance checks, which call cascade rules, which reference KSPs and bridges, which use addresses. Putting them in a single package makes the dependency graph clean and allows the package to be imported as a unit.

#### Consequences

##### Positive

- Zero changes to existing code -- no risk of regression in the trust layer
- Clean package boundary: `pact.governance` is the PACT specification implementation; everything else is infrastructure
- The existing bridge infrastructure continues to work for its current consumers
- The new package can be tested in isolation with no infrastructure dependencies
- Astra imports from `pact.governance` -- clear public API surface

##### Negative

- Two bridge concepts exist in the codebase (workspace bridges and PACT bridges)
- Some conceptual overlap between `DelegationManager.validate_tightening()` and envelope composition

##### Mitigated By

- Documentation makes clear that `pact.governance.bridge` is the PACT-native bridge; `build.workspace.bridge` is the workspace-level bridge (pre-PACT infrastructure)
- Future consolidation can migrate workspace bridges to PACT bridges if needed
- `compute_effective_envelope()` delegates to existing tightening validation rather than reimplementing

#### Alternatives Considered

**Option A: Extend bridge_trust.py and workspace bridge.py in place**

Refactor existing bridge infrastructure to support positional addresses and add KSP as a new bridge type.

Rejected because: The refactoring scope is large (BridgeTrustManager, BridgeManager, BridgePermission all need address-based rework), the risk of breaking existing consumers is high, and KSP is NOT a bridge -- it is a different concept (unit-to-unit policy vs. role-to-role channel). Forcing KSP into the bridge model would create a leaky abstraction.

**Option B: Extend OrgDefinition to embed barriers and access rules**

Add KSPs, bridges, and access rules as fields on OrgDefinition.

Rejected because: OrgDefinition is a configuration model (how the org is DEFINED). Access policies and bridges are runtime governance concepts (how the org OPERATES). Mixing definition and governance in one model violates separation of concerns and makes it impossible to change access policies without recompiling the org.

---

## 4. Interface Contracts (Public API for Verticals)

These are the Python protocols and types that Astra (and any other vertical) would import from `pact.governance`. This is the public API surface.

### 4.1 Core Types

```python
# pact.governance.addressing

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class SegmentType(str, Enum):
    D = "D"  # Department
    T = "T"  # Team
    R = "R"  # Role

@dataclass(frozen=True)
class Segment:
    type: SegmentType
    index: int  # 1-based sequence number

@dataclass(frozen=True)
class Address:
    segments: tuple[Segment, ...]

    @classmethod
    def parse(cls, address_str: str) -> Address: ...

    def is_prefix_of(self, other: Address) -> bool: ...

    @property
    def parent(self) -> Address | None: ...

    @property
    def depth(self) -> int: ...

    @property
    def containment_unit(self) -> Address | None:
        """Nearest ancestor D or T address."""
        ...

    @property
    def accountability_chain(self) -> tuple[Segment, ...]:
        """All R segments in order."""
        ...

    def __str__(self) -> str: ...
```

### 4.2 Organization Compilation

```python
# pact.governance.compilation

from typing import Protocol

@dataclass(frozen=True)
class OrgNode:
    """A node in the compiled org tree."""
    address: Address
    node_id: str           # original flat ID
    name: str
    node_type: SegmentType # D, T, or R
    parent_address: Address | None
    is_vacant: bool
    is_external: bool

class CompiledOrg:
    """Immutable compiled organization with address index."""

    @property
    def root_roles(self) -> list[OrgNode]:
        """BOD-level roles."""
        ...

    def get_node(self, address: str | Address) -> OrgNode: ...

    def query_by_prefix(self, prefix: str | Address) -> list[OrgNode]: ...

    def get_subtree(self, address: str | Address) -> list[OrgNode]: ...

    def is_direct_supervisor(
        self, supervisor_address: str | Address, report_address: str | Address
    ) -> bool: ...

    def get_reporting_chain(self, address: str | Address) -> list[OrgNode]:
        """From role up to BOD root."""
        ...

def compile_org(org: OrgDefinition) -> CompiledOrg: ...
```

### 4.3 Clearance

```python
# pact.governance.clearance

@dataclass(frozen=True)
class RoleClearance:
    role_address: str
    max_clearance: ConfidentialityLevel
    compartments: frozenset[str]
    granted_by_role_address: str
    vetting_status: str  # "pending" | "active" | "expired" | "revoked"
    review_at: datetime
    nda_signed: bool

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoleClearance: ...

def effective_clearance(
    role_clearance: RoleClearance,
    posture: TrustPostureLevel,
) -> ConfidentialityLevel:
    """Posture-capped effective clearance."""
    ...

POSTURE_CEILING: dict[TrustPostureLevel, ConfidentialityLevel]
```

### 4.4 Knowledge and Access

```python
# pact.governance.knowledge

@dataclass(frozen=True)
class KnowledgeItem:
    item_id: str
    classification: ConfidentialityLevel
    compartments: frozenset[str]
    owning_unit_address: str
    description: str

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeItem: ...


@dataclass(frozen=True)
class KnowledgeSharePolicy:
    id: str
    source_unit_address: str
    target_unit_address: str
    max_classification: ConfidentialityLevel
    compartments: frozenset[str]
    conditions: dict[str, Any]
    created_by_role_address: str
    active: bool
    expires_at: datetime | None

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeSharePolicy: ...
```

### 4.5 Access Enforcement

```python
# pact.governance.access

@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    reason: str
    step_failed: int | None  # 1-5 or None if allowed
    audit_details: dict[str, Any]

def can_access(
    role_address: str,
    knowledge_item: KnowledgeItem,
    posture: TrustPostureLevel,
    compiled_org: CompiledOrg,
    clearance_store: ClearanceStore,
    ksp_store: AccessPolicyStore,
    bridge_store: AccessPolicyStore,
) -> AccessDecision:
    """
    The 5-step access enforcement algorithm.

    Step 1: Compute effective clearance (posture-capped)
    Step 2: Classification check
    Step 3: Compartment check (SECRET/TOP_SECRET only)
    Step 4: Containment check (same unit / downward / T-inherits-D / KSP / bridge)
    Step 5: Return ALLOW or DENY with audit trail
    """
    ...
```

### 4.6 PACT Bridge

```python
# pact.governance.bridge

@dataclass(frozen=True)
class PactBridge:
    id: str
    role_a_address: str
    role_b_address: str
    bridge_type: BridgeType  # Standing / Scoped / Ad-Hoc
    max_classification: ConfidentialityLevel
    operational_scope: tuple[str, ...]
    financial_authority: bool
    bilateral: bool
    standing: bool
    status: BridgeStatus
    expires_at: datetime | None

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PactBridge: ...
```

### 4.7 Envelopes

```python
# pact.governance.envelopes

@dataclass(frozen=True)
class RoleEnvelope:
    id: str
    defining_role_address: str
    target_role_address: str
    envelope: ConstraintEnvelope
    version: int
    created_at: datetime
    modified_at: datetime

    def evaluate_action(self, **kwargs) -> EnvelopeEvaluation:
        """Delegates to self.envelope.evaluate_action()."""
        ...

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RoleEnvelope: ...


@dataclass(frozen=True)
class TaskEnvelope:
    id: str
    task_id: str
    parent_envelope_id: str
    envelope: ConstraintEnvelope
    expires_at: datetime
    created_at: datetime

    @property
    def is_expired(self) -> bool: ...

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TaskEnvelope: ...


def compute_effective_envelope(
    role_address: str,
    compiled_org: CompiledOrg,
    envelope_store: EnvelopeStore,
    task_id: str | None = None,
) -> ConstraintEnvelope:
    """Walk from root to role, intersecting all ancestor envelopes."""
    ...

def intersect_envelopes(
    a: ConstraintEnvelopeConfig,
    b: ConstraintEnvelopeConfig,
) -> ConstraintEnvelopeConfig:
    """Produce the tightest envelope from two envelopes (dimension-wise min)."""
    ...
```

### 4.8 Store Protocols

```python
# pact.governance.store

from typing import Protocol

class OrgStore(Protocol):
    async def save_org(self, org: CompiledOrg) -> None: ...
    async def load_org(self, org_id: str) -> CompiledOrg: ...
    async def get_node(self, address: str) -> OrgNode: ...
    async def query_by_prefix(self, prefix: str) -> list[OrgNode]: ...

class EnvelopeStore(Protocol):
    async def save_role_envelope(self, envelope: RoleEnvelope) -> None: ...
    async def get_role_envelope(self, target_role_address: str) -> RoleEnvelope | None: ...
    async def save_task_envelope(self, envelope: TaskEnvelope) -> None: ...
    async def get_active_task_envelope(self, role_address: str, task_id: str) -> TaskEnvelope | None: ...
    async def get_ancestor_envelopes(self, role_address: str) -> list[RoleEnvelope]: ...

class ClearanceStore(Protocol):
    async def grant_clearance(self, clearance: RoleClearance) -> None: ...
    async def get_clearance(self, role_address: str) -> RoleClearance | None: ...
    async def revoke_clearance(self, role_address: str) -> None: ...
    async def get_expiring_clearances(self, before: datetime) -> list[RoleClearance]: ...

class AccessPolicyStore(Protocol):
    async def save_ksp(self, ksp: KnowledgeSharePolicy) -> None: ...
    async def find_ksp(self, source_prefix: str, target_prefix: str) -> KnowledgeSharePolicy | None: ...
    async def save_bridge(self, bridge: PactBridge) -> None: ...
    async def find_bridge(self, role_a_address: str, role_b_address: str) -> PactBridge | None: ...
    async def list_bridges_for_role(self, role_address: str) -> list[PactBridge]: ...
```

---

## 5. Dependency Graph

```
PACT-REQ-001 (Address Type)
    |
    +-- PACT-REQ-002 (Org Compilation)
    |       |
    |       +-- PACT-REQ-011 (Effective Envelope) --+
    |       |                                        |
    |       +-- PACT-REQ-012 (Store Protocols) ------+
    |
    +-- PACT-REQ-003 (Role Clearance)
    |       |
    |       +-- PACT-REQ-005 (KSP)
    |       |
    |       +-- PACT-REQ-006 (PACT Bridge)
    |
    +-- PACT-REQ-004 (Knowledge Item)
    |
    +-- PACT-REQ-008 (Cascade Rules)

PACT-REQ-009 (Role Envelope)
    |
    +-- PACT-REQ-010 (Task Envelope)
    |
    +-- PACT-REQ-011 (Effective Envelope)
    |
    +-- PACT-REQ-014 (Default Envelopes)

PACT-REQ-007 (Access Enforcement) -- depends on ALL of 001-006, 008

PACT-REQ-013 (EATP Audit Subtypes) -- independent, extends existing infrastructure
```

## 6. Implementation Roadmap

### Phase 1: Addressing Foundation (est. 3-4 days)

- PACT-REQ-001: Address Type and Grammar Validator
- PACT-REQ-002: Organization Compilation with Address Assignment
- PACT-REQ-004: Knowledge Item Classification

### Phase 2: Clearance and Barriers (est. 4-5 days)

- PACT-REQ-003: Role Clearance Model
- PACT-REQ-005: Knowledge Share Policy
- PACT-REQ-006: PACT Bridge (Address-Based)
- PACT-REQ-008: Knowledge Cascade Rules
- PACT-REQ-007: Access Enforcement Algorithm (the capstone)

### Phase 3: Envelope Architecture (est. 3-4 days)

- PACT-REQ-009: Role Envelope
- PACT-REQ-010: Task Envelope
- PACT-REQ-011: Effective Envelope Computation
- PACT-REQ-014: Default Envelopes by Trust Posture

### Phase 4: Persistence and Audit (est. 2-3 days)

- PACT-REQ-012: Organizational Store Protocols (+ in-memory implementations)
- PACT-REQ-013: EATP Audit Anchor Subtypes

### Phase 5: Integration Test -- Flagship Scenario (est. 1-2 days)

- End-to-end test: Build financial org with Advisory and Trading divisions, compile addresses, assign clearances, configure absence of KSP, execute access request, verify BLOCKED with correct audit trail.

**Total estimated effort: 13-18 days**

## 7. Success Criteria

- [ ] `Address.parse()` correctly parses and validates all address formats from the PACT spec
- [ ] Grammar validator rejects all invalid D/T/R sequences per spec Section 2.2
- [ ] `compile_org()` assigns correct addresses matching the spec examples
- [ ] `effective_clearance()` correctly applies posture-capping
- [ ] Compartment enforcement blocks cross-compartment access for SECRET/TOP_SECRET
- [ ] KSP absence between two units constitutes an information barrier
- [ ] The 5-step access enforcement algorithm produces correct decisions for all test cases
- [ ] The flagship scenario (advisory analyst blocked from trading data) passes end-to-end
- [ ] `compute_effective_envelope()` correctly intersects ancestor envelopes
- [ ] All new types have `to_dict()` / `from_dict()` round-trip tests
- [ ] All new store protocols have in-memory implementations with bounded collections
- [ ] All governance actions produce EATP Audit Anchors
- [ ] Zero changes to existing `ConstraintEnvelope`, `DelegationManager`, or `GradientEngine` code
