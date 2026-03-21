# Integration Decisions — Governance-Era Architecture

Captures architectural decisions made during the PACT governance layer design phase that are not recorded in the Phase 1-2 `decisions.yml`. These are anti-amnesia records: decisions that future sessions must honour.

## 1. Option B Architecture

**Decision**: Build PACT governance primitives and integration adapters in this repo (`pact`), then migrate to `kailash-py/packages/kailash-pact/` when stable.

**Rationale**: Developing inside the application repo gives fast iteration without polluting the SDK monorepo. Migration happens once the API surface stabilises. The pact repo remains the reference implementation; the kailash-pact package becomes the reusable library.

**Alternatives rejected**: Option A (build directly in kailash-py from day one) -- too much churn in the SDK during exploratory design. Option C (keep everything in pact forever) -- prevents reuse by other verticals.

## 2. Package Name: kailash-pact

**Decision**: The eventual SDK package is `kailash-pact`, not `pact-python` or `pact`.

**Rationale**: `pact` is taken on PyPI (contract testing library). `kailash-pact` aligns with the ecosystem naming convention (`kailash`, `kailash-dataflow`, `kailash-nexus`, `kailash-kaizen`).

## 3. D/T/R Grammar Invariant

**Decision**: Every D (Department) or T (Team) MUST be immediately followed by exactly one R (Role). A D or T without an R is structurally invalid.

**Rationale**: The R is the accountability anchor. A department or team without a responsible role has no one accountable for its actions. This invariant is enforced at construction time, not validated after the fact.

**Example**: `D1-R1-T1-R1` is valid. `D1-T1-R1` is invalid (D1 has no R).

## 4. Five-Step Access Algorithm

**Decision**: Knowledge access follows a strict five-step algorithm: Clearance, Classification, Compartment, Containment, Deny.

1. **Clearance**: Does the role's clearance level meet or exceed the resource's classification?
2. **Classification**: Is the resource classification within the role's maximum allowed?
3. **Compartment**: Is the role a member of every compartment the resource requires?
4. **Containment**: Is the resource within the role's D/T/R containment boundary?
5. **Deny**: If any step fails, access is denied. No fallback, no override.

**Rationale**: Each step narrows the set independently. The order is deliberate: cheapest checks first, containment (which may require tree traversal) last.

## 5. Three-Layer Envelope Model

**Decision**: Operating envelopes have three layers:

- **Role Envelope** (standing) -- defined at role creation, persists for the role's lifetime.
- **Task Envelope** (ephemeral) -- defined per task, valid only for that task's duration.
- **Effective Envelope** (computed) -- the intersection of Role and Task envelopes, computed at execution time.

**Rationale**: Separating standing authority from task-specific delegation allows the same role to operate under different constraints for different tasks without modifying its permanent authority.

**Invariant**: The Effective Envelope can never be wider than the Role Envelope (monotonic tightening).

## 6. Frozen Dataclass Pattern

**Decision**: All governance state dataclasses use `@dataclass(frozen=True)`. No mutable governance objects after construction.

**Rationale**: Governance state represents trust decisions. Mutating a trust decision after it has been made violates auditability. If an update is needed, a new record is created. This aligns with the EATP append-only trust model.

**Implementation note**: Use `object.__setattr__` in `__post_init__` when computed fields need initialization.

## 7. Bounded Stores (maxlen=10,000)

**Decision**: All in-memory collections in long-running processes are bounded with `maxlen=10,000`. When capacity is reached, the oldest 10% is evicted.

**Rationale**: Prevents memory exhaustion in production. This applies to deques, caches, registries, and any other growing collection. The 10,000 default is configurable but must never be unbounded.

## 8. University as Canonical Example

**Decision**: The PACT example vertical uses a university domain, not a commercial domain.

**Rationale**: A university exercises all PACT concepts (departments, teams, roles, knowledge clearance, cross-functional bridges, approval workflows) without requiring domain expertise. It passes the boundary test: replacing "university" vocabulary with "hospital" or "government agency" vocabulary would not change a single line in `src/pact/`.

## 9. Governance to build.config Dependency Direction

**Decision**: `src/pact/governance/` imports from `src/pact/build/config/`. Never the reverse.

**Rationale**: The config layer defines the schema (what an envelope looks like, what a D/T/R address contains). The governance layer implements the rules (how envelopes compose, how addresses validate). Config is pure data; governance is behaviour. Circular imports between them would indicate a layer violation.

## 10. GovernanceEngine as Facade

**Decision**: `GovernanceEngine` is the single entry point that composes all governance components (grammar validation, envelope composition, knowledge clearance, verification gradient).

**Rationale**: External code should never wire governance subsystems together manually. The facade ensures all invariants are enforced in the correct order and prevents partial initialization.

## 11. Security Baked In, Not Bolted On

**Decision**: Every milestone includes its own security requirements. Security is not a separate phase.

**Rationale**: Ten red team rounds proved that bolting security on after the fact creates gaps. Each feature is designed, implemented, and validated with its security properties as part of the acceptance criteria.

## 12. EATP Merging into Kailash Core

**Decision**: The standalone EATP SDK is being merged into the Kailash core SDK. Workspaces have been created in both `kailash-py` and `kailash-rs`.

**Rationale**: EATP trust operations (genesis, delegation, verification, audit) are foundational to the Kailash platform, not an optional add-on. Keeping them in a separate package created unnecessary dependency management and version coordination.

## 13. Transitional Dependency Model

**Decision**: PACT currently depends on both `kailash` and `eatp`. After the EATP merge, PACT will depend only on `kailash`.

**Rationale**: During the merge, both packages exist. PACT imports from `eatp` for trust operations and `kailash` for everything else. Once EATP is fully absorbed into kailash, the `eatp` dependency is dropped and all imports move to `kailash.trust` (or equivalent namespace). The transition must be atomic -- no intermediate state where imports are split across both locations.
