# The PACT Paradigm Shift: Structure IS Architecture

**Date**: 2026-03-21
**Source**: Astra development team
**Status**: Core design insight — governs all PACT framework decisions

---

## The Traditional Pattern (What Everyone Does Today)

1. Design domain modules (Trading, Risk, Compliance, Settlement, Advisory)
2. Build each module (domain logic, database models, API endpoints)
3. Bolt on permissions (RBAC: "traders can see trades, advisors can see advisory data")
4. Bolt on approval workflows ("trades over $X need manager sign-off")
5. Bolt on audit logging (sprinkle `audit_log.record(...)` everywhere)
6. Bolt on compliance checks (pre-trade compliance middleware)
7. Bolt on information barriers (compliance team manually reviews access logs)

**Why this fails**: Governance is separate from application architecture. Every new feature is a new surface where someone might forget to add the permission check, the audit log, the compliance gate. Information barriers are policy, not architecture.

---

## What PACT Changes

**The org structure IS the application architecture.**

When you define:

```
D1-R1-D2 (Advisory Division)  ← INFORMATION BARRIER →  D1-R1-D3 (Trading Division)
```

You haven't just defined an org chart. You've defined:

- **The module boundary** — Advisory and Trading are separate containment zones
- **The data access model** — no KSP means no data flows between them, architecturally
- **The API contract** — the only way data crosses is through a Bridge with scoped permissions
- **The audit trail** — any attempt to cross is logged automatically
- **The compliance evidence** — regulation is enforced by construction, not by policy

---

## The Mapping

| Traditional Pattern                        | PACT-Native Equivalent                                           |
| ------------------------------------------ | ---------------------------------------------------------------- |
| Microservice boundaries                    | D/T containment boundaries                                       |
| Inter-service APIs                         | Bridges and KSPs (scoped, audited, bilateral)                    |
| RBAC (role → permission → resource)        | Containment + clearance + envelope (structural, not conditional) |
| Approval workflows (coded step-by-step)    | Verification gradient (auto-surfaces held actions)               |
| Rate limiting middleware                   | Operational dimension of the operating envelope                  |
| Budget controls                            | Financial dimension of the operating envelope                    |
| Audit logging (`log.info(...)` everywhere) | EATP records by construction                                     |
| Data classification labels                 | Knowledge clearance framework (enforced, not labelled)           |
| "Chinese walls" (policy, hoped-for)        | Information barriers (architectural, enforced)                   |

**You stop building five separate cross-cutting concerns** (permissions, audit, approval workflows, rate limits, data classification) **and replace them with one coherent model** that handles all of them.

---

## What a Developer Actually Builds

Three things only:

### 1. Domain Logic (the actual work)

Pure domain code. No permission checks. No audit logging. No approval gates. The agent just does its job. PACT handles everything else.

### 2. Agent Capabilities (tools for each role)

Each role's agent gets tools that match its function. The agent can only USE these tools within its operating envelope.

### 3. Configuration (the governance structure)

- The org chart (D/T/R structure)
- Envelope definitions (per role, per supervisor relationship)
- Clearance assignments (per role, with compartments)
- Barrier definitions (which KSPs exist, which don't, which bridges)
- Gradient calibration (thresholds → zones)

**You do NOT build**: Permission systems, approval workflow engines, audit logging infrastructure, data access control layers, rate limiting middleware, budget tracking systems. Those are all PACT.

---

## The Mental Model Shift

**Traditional**: Think feature-first → "I need a trading module, so I'll build models, services, APIs, then add permissions."

**PACT-native**: Think structure-first → "I need a Trading Division with these roles, these envelopes, these clearances, and these bridges. Then I build domain agents that operate within that structure."

The application emerges from agents doing domain work within governance structures. The governance isn't a layer on top of the application — it's the skeleton the application grows on.

**The org chart is the architecture diagram. The envelopes are the capability contracts. The bridges are the integration points. The gradient is the workflow engine.**
