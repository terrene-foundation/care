# CARE Platform — Next Phase Master Roadmap

**Created**: 2026-03-16
**Status**: APPROVED (2026-03-16)
**Scope**: 64 tasks across 15 milestones in 3 phases (+ 1 prerequisite)
**Continues from**: 241 completed tasks across Phases 1-4
**Red Team**: 17 gaps found, 3 critical addressed as prerequisite tasks

---

## Overview

Transition the CARE Platform from local prototype to deployable, credible, and operational platform. Three phases: polish and deploy (fix known issues + production readiness), complete the Organization Builder capstone, then launch the DM team as the first live governed agent team.

---

## M0 — Prerequisites (1 task, BLOCKER)

Must be resolved before any Phase A PR can merge.

| #    | Task                                                            | Priority | Effort |
| ---- | --------------------------------------------------------------- | -------- | ------ |
| 5000 | CI path fix + dependency cleanup + psycopg2 + .secrets.baseline | BLOCKER  | Small  |

**Key decision**: Kailash SDK packages (kailash, kailash-nexus, kailash-dataflow, kailash-kaizen) are declared as hard deps but none are imported in source code. Move to optional extras so `pip install care-platform` works without them.

---

## Phase A: Polish & Deploy (30 tasks)

Fix data inconsistencies, wire real backend endpoints, fix CI, Docker, PyPI, docs.

### M12 — API Data Wiring Fixes (4 tasks)

Wire the data that seed_demo.py produces but run_seeded_server.py currently discards.

| #    | Task                                | Priority | Effort |
| ---- | ----------------------------------- | -------- | ------ |
| 5001 | Wire verification_stats into API    | Critical | Small  |
| 5002 | Wire envelope_registry into API     | Critical | Small  |
| 5003 | Wire posture_store into API         | High     | Small  |
| 5004 | Align seed data with DM team config | Medium   | Medium |

### M13 — ShadowEnforcer Backend (4 tasks)

Add real API endpoints for the ShadowEnforcer — replace the mock data story.

| #    | Task                                 | Priority | Effort |
| ---- | ------------------------------------ | -------- | ------ |
| 5005 | Shadow metrics API endpoint          | High     | Medium |
| 5006 | Shadow report API endpoint           | High     | Medium |
| 5007 | Wire ShadowEnforcer into PlatformAPI | High     | Medium |
| 5008 | Add ShadowEnforcer seed data         | Medium   | Medium |

### M14 — Frontend Fixes (3 tasks)

Remove all mock data and synthetic values from the frontend.

| #    | Task                                   | Priority | Effort |
| ---- | -------------------------------------- | -------- | ------ |
| 5009 | Replace shadow mock data with API      | High     | Medium |
| 5010 | Fix WebSocket auth warnings            | Medium   | Small  |
| 5011 | Replace Math.random() dashboard trends | Medium   | Medium |

### M15 — CI/CD Pipeline (5 tasks)

Fix broken CI paths and add missing pipeline stages.

| #     | Task                          | Priority | Effort |
| ----- | ----------------------------- | -------- | ------ |
| 5012  | Fix CI lint/type check paths  | Critical | Small  |
| 5013  | Add integration test job      | High     | Medium |
| 5013b | Create integration test suite | High     | Medium |
| 5014  | Add Docker build test         | Medium   | Small  |
| 5015  | Add security scanning         | Medium   | Small  |
| 5016  | Add pre-commit configuration  | Medium   | Small  |

### M16 — Package Publishing (2 tasks)

Make the platform installable via pip.

| #    | Task                         | Priority | Effort |
| ---- | ---------------------------- | -------- | ------ |
| 5017 | MANIFEST.in + validate build | High     | Small  |
| 5018 | PyPI publishing workflow     | High     | Medium |

### M17 — Documentation Site (4 tasks)

Give the platform a public documentation presence.

| #    | Task                             | Priority | Effort |
| ---- | -------------------------------- | -------- | ------ |
| 5019 | Set up docs site (MkDocs/Sphinx) | High     | Medium |
| 5020 | Auto-generate API reference docs | Medium   | Medium |
| 5021 | Deploy docs to GitHub Pages      | Medium   | Small  |
| 5022 | Write quickstart tutorial        | High     | Medium |

### M18 — Production Hardening (6 tasks)

Production infrastructure: migrations, logging, metrics, health checks.

| #    | Task                           | Priority | Effort |
| ---- | ------------------------------ | -------- | ------ |
| 5023 | Alembic database migrations    | High     | Medium |
| 5024 | Structured logging (structlog) | Medium   | Small  |
| 5025 | Prometheus metrics endpoint    | Medium   | Medium |
| 5026 | Container registry publishing  | Medium   | Small  |
| 5027 | Expand health check endpoint   | Medium   | Small  |
| 5028 | Complete .env.example          | Medium   | Small  |

---

## Phase B: Organization Builder Capstone (20 tasks)

Complete the org builder as the strategic differentiator.

### M19 — Org Validation Hardening (7 tasks)

Deep semantic validation beyond structural consistency checks.

| #    | Task                            | Priority | Effort |
| ---- | ------------------------------- | -------- | ------ |
| 5029 | Capability-envelope alignment   | High     | Medium |
| 5030 | Monotonic tightening validation | High     | Medium |
| 5031 | Team lead capability superset   | Medium   | Small  |
| 5032 | Gradient coverage validation    | Medium   | Small  |
| 5033 | Temporal/data path consistency  | Medium   | Small  |
| 5034 | Multi-team validation           | High     | Medium |
| 5035 | Validation severity levels      | Medium   | Small  |

### M20 — Template Library Expansion (5 tasks)

Expand from 4 templates to a composable library.

| #    | Task                                | Priority | Effort |
| ---- | ----------------------------------- | -------- | ------ |
| 5036 | Engineering team template           | Medium   | Medium |
| 5037 | Executive team template             | Medium   | Medium |
| 5038 | Custom template from YAML           | High     | Medium |
| 5039 | Multi-team composition              | High     | Large  |
| 5040 | Template validation on registration | Medium   | Small  |

### M21 — Import/Export and CLI (5 tasks)

Complete CLI tooling for org lifecycle management.

| #    | Task                     | Priority | Effort |
| ---- | ------------------------ | -------- | ------ |
| 5041 | YAML export command      | High     | Medium |
| 5042 | YAML/JSON import command | High     | Medium |
| 5043 | Org diff command         | Medium   | Medium |
| 5044 | Org deploy command       | High     | Large  |
| 5045 | Org status command       | Medium   | Small  |

### M22 — Integration and Dog-fooding (3 tasks)

Prove it works end-to-end by running the Foundation through it.

| #    | Task                            | Priority | Effort |
| ---- | ------------------------------- | -------- | ------ |
| 5046 | Foundation org round-trip test  | High     | Medium |
| 5047 | Org builder dashboard page      | Medium   | Large  |
| 5048 | Phase A + B red team validation | High     | Medium |

---

## Phase C: DM Team Vertical (13 tasks)

Launch real governed agents doing real work.

### M23 — DM Team Execution Wiring (4 tasks)

Connect governance layer to actual agent execution.

| #    | Task                            | Priority | Effort |
| ---- | ------------------------------- | -------- | ------ |
| 5049 | DMTeamRunner orchestrator       | Critical | Large  |
| 5050 | Agent-specific system prompts   | High     | Medium |
| 5051 | Capability-based task routing   | High     | Medium |
| 5052 | DM task submission + status API | High     | Medium |

### M24 — ShadowEnforcer Calibration (3 tasks)

Calibrate trust monitoring before live execution.

| #    | Task                               | Priority | Effort |
| ---- | ---------------------------------- | -------- | ------ |
| 5053 | Shadow simulation runner           | High     | Medium |
| 5054 | Shadow live mode integration       | Medium   | Small  |
| 5055 | Posture upgrade recommendation API | Medium   | Small  |

### M25 — DM Dashboard and E2E (6 tasks)

Frontend, seed data, end-to-end testing, and first real LLM connection.

| #    | Task                               | Priority | Effort |
| ---- | ---------------------------------- | -------- | ------ |
| 5056 | DM team dashboard page             | Medium   | Medium |
| 5057 | DM task submission UI              | Medium   | Medium |
| 5058 | DM-specific seed data              | Medium   | Small  |
| 5059 | End-to-end DM execution test       | High     | Medium |
| 5060 | Connect real LLM backend (1 agent) | Medium   | Medium |
| 5061 | Phase C red team validation        | High     | Medium |

---

## Dependency Graph

```
Phase A (M12-M18)
  M12 (Data Wiring) ──┐
  M13 (Shadow Backend)─┤
  M14 (Frontend Fixes)─┤── All parallel after M12
  M15 (CI/CD) ─────────┤
  M16 (Publishing) ────┤── Needs M15
  M17 (Docs) ──────────┤── Independent
  M18 (Hardening) ─────┘── Independent

Phase B (M19-M22) — after Phase A
  M19 (Validation) ────┐
  M20 (Templates) ─────┤── Needs M19
  M21 (CLI) ───────────┤── Independent of M20
  M22 (Dog-fooding) ───┘── Needs M19-M21

Phase C (M23-M25) — after Phase B
  M23 (Execution) ─────┐
  M24 (Calibration) ───┤── Needs M23
  M25 (Dashboard+E2E) ─┘── Needs M23-M24
```

---

## Effort Summary

| Phase     | Tasks  | Small  | Medium | Large | Estimated      |
| --------- | ------ | ------ | ------ | ----- | -------------- |
| M0        | 1      | 1      | 0      | 0     | 1 day          |
| A         | 30     | 13     | 16     | 0     | 2-3 weeks      |
| B         | 21     | 6      | 11     | 3     | 3-4 weeks      |
| C         | 13     | 3      | 8      | 1     | 4-6 weeks      |
| **Total** | **65** | **23** | **35** | **4** | **9-13 weeks** |

---

## Red Team Findings Addressed

17 gaps found, key ones resolved:

1. **CI broken** (Critical) → Extracted as M0 prerequisite
2. **Kailash SDK deps unused** (Critical) → Move to optional extras in M0
3. **psycopg2 missing** (Critical) → Added to M0
4. **No integration tests exist** (Major) → Added 5013b
5. **posture_store no API parameter** (Critical) → Scoped in 5003
6. **No example YAML configs** (Moderate) → Added 5040b
7. **.secrets.baseline missing** (Major) → Added to M0
