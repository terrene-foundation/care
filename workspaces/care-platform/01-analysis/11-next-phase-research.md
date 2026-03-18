# Next Phase Research: Four Options Analysis

**Date**: 2026-03-16
**Inputs**: 4 specialist agents (deep-analyst, requirements-analyst, value-auditor, framework-advisor)
**Scope**: All four next-phase options analyzed in parallel

---

## Option A: Phase 5 — Organization Builder (Capstone)

### What Exists (Source-Verified)

- `OrgDefinition` Pydantic model with `validate_org()` — checks duplicates and dangling references
- `OrgBuilder` fluent API with `save()`/`load()`/`from_config()` for TrustStore persistence
- `OrgTemplate` with `foundation_template()` and `minimal_template()`
- `TemplateRegistry` with 4 built-in templates: media, governance, standards, partnerships
- CLI commands: `care-platform org create`, `care-platform org validate`, `care-platform org list-templates`
- `PlatformBootstrap` initializes full trust hierarchy: genesis, workspaces, envelopes, delegations
- 60+ org builder tests passing

### Gaps Identified

1. **Validation**: No semantic validation (monotonic tightening, temporal containment, data access subsetting, capability-envelope alignment, gradient coverage)
2. **Templates**: Only 4 templates. Missing: engineering, executive, custom from YAML, multi-team composition, template versioning
3. **CLI**: No export, import, diff, deploy, or status commands
4. **Integration**: `run_seeded_server.py` discards `envelope_registry` and `verification_stats` at startup
5. **Foundation validation**: No `validate_foundation_org()` for full multi-team cross-validation

### Framework Recommendation

- Keep OrgBuilder as pure Python (no Kailash workflows for validation)
- **Adopt DataFlow for org definition persistence** — strongest framework fit
- Don't make template generation a Kaizen agent yet (deterministic, no LLM needed)

### Assessment

| Dimension       | Score                            |
| --------------- | -------------------------------- |
| Complexity      | 6/10                             |
| Effort          | Large (3-4 weeks)                |
| Risk            | Low (extends proven patterns)    |
| Strategic Value | HIGH — capstone feature          |
| Tasks           | ~20 (5 Small, 9 Medium, 3 Large) |

---

## Option B: Production Deployment

### What Exists (Source-Verified)

- `Dockerfile` — multi-stage build, non-root user, health check, AsyncLocalRuntime noted
- `docker-compose.yml` — PostgreSQL + API + Web, health checks, named volumes
- `.github/workflows/ci.yml` — lint, type check, test matrix (3.11/3.12/3.13), coverage
- `pyproject.toml` — full metadata, version 0.1.0, Apache-2.0, CLI entry point
- FastAPI server with CORS, rate limiting, security headers, bearer auth, graceful shutdown
- Health check (`/health`) and readiness probe (`/ready`) endpoints
- `EnvConfig` for environment-specific configuration

### Gaps Identified

1. **CRITICAL: CI paths wrong** — `ci.yml` references `care_platform/` not `src/care_platform/` (lines 33-34, 39)
2. No documentation site (no Sphinx/MkDocs)
3. No PyPI publishing workflow
4. No integration test job in CI
5. No container registry publishing
6. No Alembic migrations directory (despite dependency)
7. Port mismatch: Dockerfile uses 8000, dev runs on 8100

### Framework Recommendation

- **Do NOT migrate API to Nexus** — the existing FastAPI layer is well-built with security hardening from 10 red team rounds
- Use AsyncLocalRuntime in Docker (mandatory per deployment rules)
- Keep Click CLI for operator commands (not Nexus multi-channel)

### Assessment

| Dimension       | Score                             |
| --------------- | --------------------------------- |
| Complexity      | 4/10                              |
| Effort          | Medium (1-2 weeks)                |
| Risk            | Medium (external service deps)    |
| Strategic Value | CRITICAL for credibility          |
| Tasks           | ~20 (10 Small, 8 Medium, 0 Large) |

---

## Option C: DM Team Vertical

### What Exists (Source-Verified)

- 5 agent configs with 5 constraint envelopes, verification gradient, monotonic tightening
- `ExecutionRuntime` with task queue, verification pipeline, approval queue, audit chain
- `LLMBackend` abstraction with Anthropic and OpenAI backends (full implementations)
- `KaizenBridge` connecting governance to LLM execution
- `ApprovalQueue` with urgency, batch operations, expiry, capacity metrics
- `ShadowEnforcer` with metrics, reports, upgrade eligibility
- `ShadowEnforcerLive` for real vs shadow comparison
- 120+ execution/trust tests passing

### Gaps Identified

1. **No end-to-end wiring**: Pieces exist in isolation. No `DMTeamRunner` that assembles everything
2. **No agent system prompts**: KaizenBridge uses generic prompts. Each DM agent needs role-specific prompts
3. **No task routing by capability**: Runtime selects agents generically, not by capability matching
4. **No ShadowEnforcer calibration workflow**: No process for calibrating thresholds from real data
5. **No DM-specific API endpoints**: No task submission, team status, or DM operations
6. **Dashboard uses mock data**: ShadowEnforcer page agents don't match seeded agents

### Framework Recommendation

- **Build real DM agents with Kaizen TrustedAgent** — highest-value framework integration across all options
- Use Supervisor-Worker pattern (Team Lead supervises 4 specialist workers)
- Bridge CARE constraint verification as pre-execution hooks in Kaizen agent lifecycle
- Workspace knowledge bases feed via Signature context fields initially, RAG later

### Assessment

| Dimension       | Score                                                     |
| --------------- | --------------------------------------------------------- |
| Complexity      | 9/10                                                      |
| Effort          | XL (4-6 weeks)                                            |
| Risk            | HIGH (real LLM integration, non-deterministic, cost risk) |
| Strategic Value | HIGH (ultimate proof) but premature without B+D           |
| Tasks           | ~15 (4 Small, 8 Medium, 1 Large)                          |

---

## Option D: Fix Known Issues

### What Exists / Root Causes (Source-Verified)

1. **verification_stats**: `run_seeded_server.py` passes `verification_stats={}` to PlatformAPI. Seed script produces the stats but they're discarded at server startup
2. **ShadowEnforcer mock data**: `mock-data.ts` uses agent IDs (`agent-ops-lead`, `agent-finance-analyst`) that don't match seed data. No shadow API endpoints exist
3. **WebSocket warnings**: Server-side warning on query-parameter auth fallback (intentional design, frontend triggers it)
4. **Dashboard trends**: Overview page generates fake 7-day trends with `Math.random()`
5. **CI paths**: `ci.yml` references wrong source directory

### Framework Recommendation

- Pure Python fixes. No framework needed.
- ShadowEnforcer endpoints could benefit from DataFlow if adopted in Option A, but this is incidental

### Assessment

| Dimension       | Score                                    |
| --------------- | ---------------------------------------- |
| Complexity      | 2/10                                     |
| Effort          | Small (1-3 days)                         |
| Risk            | LOW (known fixes with clear root causes) |
| Strategic Value | HIGH (force-multiplies everything else)  |
| Tasks           | ~14 (5 Small, 8 Medium, 0 Large)         |

---

## Key Finding: No Kailash Frameworks Used Yet

The CARE Platform declares all four Kailash frameworks as dependencies (`kailash`, `kailash-nexus`, `kailash-dataflow`, `kailash-kaizen`) in `pyproject.toml`, but currently uses none of them in source code. The entire platform is built as pure Python with Pydantic models, hand-rolled FastAPI, Click CLI, and custom persistence stores.

This is not a problem — the trust/governance layer was built first with pure domain models. But it means each option represents the first real framework adoption point:

| Option | Framework to Adopt              |
| ------ | ------------------------------- |
| A      | DataFlow (persistence)          |
| B      | AsyncLocalRuntime (Docker)      |
| C      | Kaizen (TrustedAgent execution) |
| D      | None                            |

---

## Cross-References and Inconsistencies Found

1. **DM Team config inconsistency**: `dm_team.py` sets 200 max_actions_per_day for lead. Template in `registry.py` sets 60. Template is generalized version; DM team is canonical.
2. **Port mismatch**: Dockerfile exposes 8000, dev server runs on 8100, compose maps 8000.
3. **CI path bug**: `ci.yml` lint/mypy targets `care_platform/` but source is `src/care_platform/`. Likely silently passing or not running.
4. **ShadowEnforcer dual implementations**: `shadow_enforcer.py` (hypothetical evaluation) vs `shadow_enforcer_live.py` (real vs shadow). Dashboard expects the former's models.
5. **Seed data discarded**: `seed_demo.py` produces `envelope_registry`, `verification_stats`, `posture_store` — all discarded by `run_seeded_server.py`.
