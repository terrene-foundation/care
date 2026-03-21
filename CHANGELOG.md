# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-21

### Added

- **GovernanceEngine** — single-call facade: `engine.can(agent, action, resource)` returns a `GovernanceVerdict` with full audit trail. Supports `from_yaml()` constructor for loading org definitions directly from YAML files.
- **D/T/R Addressing** — positional address algebra (`D1-R1-T1-R1`), grammar validation (every D/T immediately followed by R), depth-limited parsing, ancestor/descendant queries.
- **Three-Layer Envelopes** — `RoleEnvelope` (standing), `TaskEnvelope` (ephemeral), effective envelope (computed intersection). Monotonic tightening enforced: child envelopes can only equal or restrict parent. Five constraint dimensions: Financial, Operational, Temporal, Data Access, Communication.
- **Knowledge Clearance Framework** — five-level classification (OFFICIAL through TOP_SECRET) independent of authority/seniority. Five-step access algorithm: clearance check, compartment check, need-to-know, bridge policy, KSP enforcement.
- **PactGovernedAgent** — base class for governance-aware AI agents with default-deny tool execution. Tools must be explicitly registered via `@governed_tool` decorator.
- **@governed_tool Decorator** — marks functions as governance-checked tools with resource/action metadata.
- **PactGovernanceMiddleware** — lightweight alternative to subclassing for adding governance to existing agents.
- **MockGovernedAgent** — testing utility for governance scenarios without LLM dependencies.
- **SQLite Governance Stores** — persistent implementations for OrgStore, ClearanceStore, EnvelopeStore, AccessPolicyStore with bounded collections and backup/restore.
- **Governance REST API** — FastAPI endpoints for org queries, envelope inspection, access checks, and audit trail retrieval. Scoped auth (governance:read, governance:write).
- **CLI Validation** — `kailash-pact validate org.yaml` command for offline org definition validation with address tree output.
- **GovernanceContext** — frozen (anti-self-modification) agent context carrying role, clearance, envelope, and bridge state.
- **AgentRoleMapping** — bidirectional agent-to-address mapping for runtime agent identity resolution.
- **GovernanceEnvelopeAdapter** — fail-closed conversion between legacy ConstraintEnvelope and governance RoleEnvelope/TaskEnvelope.
- **YAML Org Loader** — declarative org definitions with roles, clearances, envelopes, bridges, and KSPs in a single YAML file.
- **Explain API** — `describe_address()`, `explain_envelope()`, `explain_access()` for human-readable governance explanations.
- **968 governance tests** covering addressing, compilation, clearance, access, envelopes, engine, agent, middleware, stores, API, and CLI.

### Changed

- **Package renamed** from `pact` to `kailash-pact` for PyPI distribution. Import path remains `from pact.governance import GovernanceEngine`.
- **Version bumped** to 0.2.0 to reflect governance layer completion.
- **CLI entry point** changed from `pact` to `kailash-pact`.
- **Optional dependencies restructured** — `kailash`, `kaizen`, `postgres`, `firebase`, and `all` extras.
- **Legacy foundation example** moved to `archive/legacy-foundation/`.

### Security

- **NaN/Inf guards** on all numeric constraint fields (`math.isfinite()` checks).
- **Frozen dataclasses** for all constraint and policy types (prevents post-init mutation).
- **Thread safety** via `threading.Lock` on all shared mutable stores.
- **TOCTOU treatment** — atomic check-and-act in approval workflows and store operations.
- **Depth limits** on D/T/R address parsing (prevents stack overflow on malicious input).
- **Default-deny tools** — PactGovernedAgent blocks all tool calls unless explicitly registered via `@governed_tool`.

## [0.1.0] - 2026-03-18

### Added

- **Trust Plane**: Genesis Records, delegation chains, constraint envelopes (5 dimensions), verification gradient (AUTO_APPROVED / FLAGGED / HELD / BLOCKED), trust postures (PSEUDO_AGENT through DELEGATED), ShadowEnforcer, cascade revocation, audit anchors with hash chaining.
- **EATP SDK Integration**: Trust decorators, CareEnforcementPipeline with GradientEngine + StrictEnforcer, ProximityScanner, reasoning trace factories with JCS signing, SD-JWT dual binding.
- **Constraint System**: Constraint envelope signing (Ed25519), content-hash verification cache, circuit breaker, fail-closed enforcement across 43 source files.
- **Organization Builder**: OrgDefinition model, OrgBuilder fluent API, validate_org_detailed() with comprehensive semantic validation, template registry with 6 built-in templates, YAML import/export, org diff, org deploy CLI.
- **Cross-Functional Bridges**: Standing, Scoped, and Ad-Hoc bridge types, CoordinatorAgent, bridge lifecycle management, bridge trust and posture integration.
- **Agent Runtime**: Agent registry, approval queue, LLM backend abstraction (OpenAI, Anthropic, Google, local), Kaizen bridge, session management, posture enforcement.
- **API Server**: FastAPI with authentication (Firebase SSO + static token), CORS, rate limiting, security headers, WebSocket with Sec-WebSocket-Protocol auth, graceful shutdown, Prometheus metrics, structured logging.
- **Web Dashboard**: 17 Next.js pages, 30+ React components, design system, governance actions (suspend, revoke, posture change), ShadowEnforcer dashboard, cost report, audit export (CSV/JSON), posture upgrade wizard, notification system, 47 WCAG 2.1 AA accessibility fixes.
- **Flutter App**: Cross-platform mobile/desktop companion app.
- **CI/CD**: GitHub Actions for lint, test (Python 3.11/3.12/3.13 matrix, 90% coverage gate), Docker build, MkDocs deployment, PyPI publishing with trusted publisher.
- **Deployment**: Docker Compose (PostgreSQL + API + Web), Cloud Run Dockerfile, deployment configuration documentation.

### Security

- Fail-closed on all trust paths (unknown states resolve to BLOCKED).
- Thread-safe shared mutable state (11 components with threading.Lock).
- Non-root container users in all Docker images.
- No hardcoded secrets (all from .env).
- Parameterized database queries throughout.

[0.2.0]: https://github.com/terrene-foundation/pact/releases/tag/v0.2.0
[0.1.0]: https://github.com/terrene-foundation/pact/releases/tag/v0.1.0
