# PACT Reference Implementation — Master Roadmap

**Date**: 2026-03-21
**Thesis**: PACT Core Thesis v0.8
**Target**: Minimum Viable PACT framework that astra/arbor can import

## Milestones

### M0: Framework Extraction (Prerequisites)

- 0001: Extract verticals to examples
- 0002: Add boundary-test rule
- 0003: Create pact.governance package scaffold
- 0004: Rename PlatformConfig/PlatformSession
- 0005: Fix remaining CARE Platform references (frontend, .env)

### M1: Positional Addressing (D/T/R Grammar Engine)

- 1001: Address type and grammar validator
- 1002: RoleDefinition as first-class node
- 1003: Org compilation with address assignment
- 1004: Prefix-containment queries
- 1005: Vacancy handling (3 rules from thesis Section 5.5)

### M2: Knowledge Clearance + Barriers (Flagship Demo)

- [ ] 2001: RoleClearance model with compartments → [2001-role-clearance.md](2001-role-clearance.md)
- [ ] 2002: KnowledgeItem classification type → [2002-knowledge-item.md](2002-knowledge-item.md)
- [ ] 2003: KnowledgeSharePolicy (KSP) → [2003-ksp.md](2003-ksp.md)
- [ ] 2004: PactBridge (address-based) → [2004-pact-bridge.md](2004-pact-bridge.md)
- [ ] 2005: Knowledge cascade rules → [2005-cascade-rules.md](2005-cascade-rules.md)
- [ ] 2006: Access Enforcement Algorithm (5-step) → [2006-access-algorithm.md](2006-access-algorithm.md)
- [ ] 2007: Flagship scenario end-to-end test → [2007-flagship-test.md](2007-flagship-test.md)

### M3: Envelope Architecture

- [ ] 3001: Envelope intersection per-dimension (thesis Section 5.3) → [3001-envelope-intersection.md](3001-envelope-intersection.md)
- [ ] 3002: RoleEnvelope (standing) → [3002-role-envelope.md](3002-role-envelope.md)
- [ ] 3003: TaskEnvelope (ephemeral) → [3003-task-envelope.md](3003-task-envelope.md)
- [ ] 3004: Effective envelope computation → [3004-effective-envelope.md](3004-effective-envelope.md)
- [ ] 3005: Default envelopes by trust posture → [3005-default-envelopes.md](3005-default-envelopes.md)
- [ ] 3006: Degenerate envelope detection → [3006-degenerate-detection.md](3006-degenerate-detection.md)

### M4: Persistence + EATP Audit

- 4001: Governance store protocols (4 stores)
- 4002: In-memory store implementations
- 4003: EATP audit anchor subtypes (Section 5.7 mapping)
- 4004: SQLite store implementation

### M5: Example Vertical + Integration

- 5001: University vertical D/T/R structure
- 5002: University clearance and barrier config
- 5003: University bridges config
- 5004: End-to-end integration test suite
- 5005: Public API surface (`from pact import ...`)

### M6: Red Team + Hardening

- 6001: Access algorithm exhaustive test matrix
- 6002: Security review (pre-retrieval clearance, fail-closed defaults)
- 6003: Adversarial threat tests (thesis Section 12.9)
- 6004: Convergence validation
