---
name: constitution-reference
description: Load Terrene Foundation constitution reference. Use when discussing constitutional provisions, governance phases, entrenched provisions, board composition, membership criteria, anti-capture mechanisms, IP protection, institutional partners, or ACRA filing requirements.
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Terrene Foundation Constitution Reference

This skill provides the reference for the Terrene Foundation constitution — a Singapore CLG (Company Limited by Guarantee, non-charity) that publishes open standards for enterprise AI governance.

## Authoritative Sources

### PRIMARY: Constitution

- `docs/06-operations/constitution/terrene-foundation-constitution.md` - The authoritative text (77 clauses, 21 Parts, 1 Schedule)

### PRIMARY: Design Rationale

- `workspaces/constitution/briefs/01-constitution-design-rationale.md` - Design decisions, trade-offs, founding reality

### PRIMARY: Companion Documents

- `docs/06-operations/constitution/00-companion-overview.md` - Index and audience guide
- `docs/06-operations/constitution/01-design-philosophy.md` - Value-first mission
- `docs/06-operations/constitution/02-anti-capture-mechanisms.md` - Corporate and activist capture defenses
- `docs/06-operations/constitution/03-three-estate-board.md` - Three-estate model
- `docs/06-operations/constitution/04-phased-governance.md` - Phase transitions
- `docs/06-operations/constitution/05-ip-protection.md` - Licensing and patents
- `docs/06-operations/constitution/06-institutional-partners.md` - ASME/SBF model
- `docs/06-operations/constitution/07-singapore-clg-landscape.md` - Precedent research
- `docs/06-operations/constitution/08-entrenchment-strategy.md` - Section 26A usage
- `docs/06-operations/constitution/09-entity-independence.md` - Foundation independence and anti-capture
- `docs/06-operations/constitution/contribution-criteria.md` - Merit-based criteria

### SECONDARY: Red Team Validation

- `workspaces/constitution/04-validate/` - Three rounds of adversarial review

## Quick Reference

### Entity Type

Singapore CLG under Companies Act 1967. NOT charity. NOT IPC. Non-profit, commercially active.

### Phased Governance (Clause 75)

| Phase             | Trigger              | Board          | Key Features                                     |
| ----------------- | -------------------- | -------------- | ------------------------------------------------ |
| Phase 1: Seed     | Incorporation        | 1-3 Directors  | Founder leads; Entrenched Provisions in force    |
| Phase 2: Growth   | 10 Committer Members | 3-7 Directors  | First elections; TSC; term limits                |
| Phase 3: Maturity | 30 Members + 3 years | 7-11 Directors | Full three-estate Board; Founder cannot be Chair |

### 11 Entrenched Provisions (Clause 54)

| Provision                     | Clause | Summary                                       |
| ----------------------------- | ------ | --------------------------------------------- |
| Non-profit constraint         | 6      | Income applied solely to objects              |
| No share conversion           | 7      | Cannot become share company                   |
| Funding/governance separation | 17(d)  | Sponsorship cannot buy governance             |
| One person, one vote          | 24(a)  | Equal voting rights                           |
| Licence stability             | 50(c)  | Released versions stay under original licence |
| Contributor protection        | 52(b)  | Patent protections irrevocable                |
| Founder Chair restriction     | 29(b)  | Founder cannot be Chair from Phase 3          |
| Independent Board majority    | 26(d)  | Exactly 6 Independent Directors in Phase 3    |
| Community voice               | 61     | RFC process for Significant Changes           |
| Winding-up IP survival        | 66     | Licences survive dissolution                  |
| Anti-circumvention            | 55     | Indirect attacks trigger full process         |

### Amendment Thresholds

| Type                 | Threshold                                   | Notice                                        |
| -------------------- | ------------------------------------------- | --------------------------------------------- |
| Ordinary Amendment   | Special Resolution (75% present and voting) | 21 days + 30-day comment period               |
| Entrenched Amendment | 90% Board + 80% all seasoned Members        | 12 months + independent opinions + 90-day RFC |
| Winding Up           | 80% all Members by headcount                | 12 months + RFC                               |

### Membership Categories

- **Community Member**: Non-voting, open to all, free
- **Committer Member**: Voting (1 vote), merit-based admission, free
- **Emeritus Member**: Inactive Committer (36 months), retains Community rights

### Corporate Sponsors

Platinum/Gold/Silver/Bronze. ZERO governance rights (Entrenched). No votes, no seats, no veto. Advisory only via CAC.

### Board Composition (Phase 3)

| Estate            | Seats        | Selection                      |
| ----------------- | ------------ | ------------------------------ |
| Independent       | 6 (majority) | GNC appointed, Member ratified |
| Community-Elected | Up to 3      | Elected at General Meeting     |
| Institutional     | Up to 2      | Nominated by partners          |

### Key Anti-Capture Mechanisms

| Mechanism                   | Clause                | Effect                              |
| --------------------------- | --------------------- | ----------------------------------- |
| Membership Growth Safeguard | 12                    | Max 100% increase or 20 per year    |
| Employer Diversity          | 15                    | No employer >33% of voting Members  |
| Seasoning                   | 3 (Supermajority def) | 12-month membership before EP votes |
| Director Cooling-Off        | 31                    | 12-month post-service restriction   |
| Anti-Circumvention          | 55                    | Indirect attacks blocked            |
| Proxy Limit                 | 25(b)                 | Max 3 proxies per person            |

### Founder Restrictions Timeline

| Phase   | Restriction                                                                 |
| ------- | --------------------------------------------------------------------------- |
| Phase 1 | Must disclose all conflicts; S$10K related-party cap; S$50K expenditure cap |
| Phase 2 | Cannot chair any committee                                                  |
| Phase 3 | Cannot be Board Chair (permanent, Entrenched); community-elected only       |

## How to Use This Reference

1. For constitutional text questions → read the constitution directly
2. For "why was it designed this way" → read the design rationale brief
3. For audience-specific explanations → use the companion document index
4. For known issues → check red team validation reports
