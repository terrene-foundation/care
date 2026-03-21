# Boundary Test Rule

## Scope

These rules apply to ALL modifications to `src/pact/` (excluding `src/pact/examples/`).

## The Boundary Test

Every change to the PACT framework layer must pass this test:

> If you replaced all domain-specific vocabulary with different domain terms, would any line in `src/pact/` (excluding `examples/`) need to change?

If yes, the change belongs in a vertical (astra, arbor, or an example), not in the framework.

## Domain Vocabulary Blacklist

The following terms MUST NOT appear in `src/pact/` (excluding `examples/`):

- Organization names: Terrene, Foundation (as org name), Aegis, Integrum, Astra, Arbor
- Industry terms: trading, advisory, compliance (as financial terms), MAS, FINRA, FCA, SFA
- Domain-specific roles: DM, Digital Marketing, AML, CFT, KYC, trader, advisor
- Specific team structures: dm-team-lead, dm-content-creator, etc.

## Framework-Appropriate Vocabulary

These terms ARE allowed in `src/pact/` — they are PACT specification terms:

- D/T/R grammar: Department, Team, Role, Address, BOD
- Governance: Envelope, Clearance, Compartment, KSP, Bridge, Gradient, Posture
- EATP: Genesis, Delegation, Attestation, Anchor, Verification
- Classification: PUBLIC, RESTRICTED, CONFIDENTIAL, SECRET, TOP_SECRET
- Gradient: AUTO_APPROVED, FLAGGED, HELD, BLOCKED
