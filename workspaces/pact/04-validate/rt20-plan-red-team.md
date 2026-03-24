# RT20: Plan Red Team — M7-M15 Roadmap Review

**Date**: 2026-03-21
**Agents**: deep-analyst (scope+value), security-reviewer, deep-analyst (consumer view), coc-expert
**Target**: 48-todo plan across 9 milestones (M7-M15)
**Verdict**: PLAN NEEDS RESTRUCTURING — cut scope, fix security timing, address PyPI naming

## Critical Findings (4 agents converge)

### 1. SCOPE IS 2-3x TOO LARGE (deep-analyst)

- 48 todos / 39-53 days when verticals need ~18 todos / 20 days
- M10 (DataFlow), M11 (Nexus API), M12 (Frontend) are premature — no consumer needs them yet
- In-memory stores work for v0.2.0; persistence is v0.3.0
- Verticals call Python functions, not REST APIs

### 2. SECURITY DEFERRED TO M14 (security-reviewer)

- 5 CRITICAL findings: NaN bypass in envelopes (existing), thread safety absent, no API auth model, agent self-modification possible, bolt-on security pattern
- 7 HIGH findings: envelope adapter fallback, store security parity, audit integrity, rate limiting, unbounded recursion, mutable RoleDefinition, KSP/bridge TOCTOU
- Security must be baked into each milestone, not bolted on at the end

### 3. NO REAL CONSUMER VALIDATES THE API (deep-analyst consumer view)

- University example is internal — author-tested, not consumer-tested
- `can_access()` requires 7 parameters manually wired
- No `engine.can("agent-id", "read", "trading/positions")` convenience
- Two config formats (PactConfig vs OrgDefinition) — neither complete
- PyPI name "pact" conflicts with pact-python (1,800 stars, 2.2M+ downloads) — SHIP BLOCKER

### 4. COC INFRASTRUCTURE IS STALE (coc-expert)

- Ghost hook `validate-hierarchy-grammar.js` fires on every file change (doesn't exist)
- `session-start.js` always detects "core-sdk" — never governance
- Zero governance patterns in learning pipeline after 36 milestones
- No `rules/governance.md` — convention drift guaranteed across 4 framework integrations
- `decisions.yml` has zero entries from the governance era

## Recommended Plan: v0.2.0 in ~20 Days

### Phase 0: Infrastructure (2 days)

- Fix ghost hook, session-start detection, boundary-test automation
- Create `rules/governance.md` with GovernanceEngine conventions
- Create `integration-decisions.md` for anti-amnesia
- Fix existing NaN/Inf bypass and mutable RoleDefinition

### Phase 1: GovernanceEngine (5-7 days)

- Facade with single-call API
- YAML org loader (unified format)
- Convenience methods: `engine.can()`, `engine.explain_envelope()`
- Address-to-human-readable resolver
- Security baked in (finite guards, thread safety, fail-closed)

### Phase 2: Envelope Unification (3-4 days)

- Adapter pattern (governance canonical, trust delegates)
- Fail-closed on adapter failure (no fallback to legacy)
- Property-based testing for tightening invariant

### Phase 3: PactGovernedAgent (4-5 days)

- Kaizen integration with frozen GovernanceContext
- Default-deny tool access (not opt-in decoration)
- Agent-to-address mapping
- MockAgent for testing without LLM

### Phase 4: Docs + Red Team + Ship (4-5 days)

- Vertical integration guide
- CLI validation: `pact validate org.yaml`
- Security red team of core (M7-M9 only)
- Resolve PyPI naming
- Version bump, changelog, tag

**Total: ~18-20 todos, ~20 days. Then start Astra. Let Astra drive v0.3.0.**

## Deferred to v0.3.0

- M10: DataFlow persistence (SQLite/PostgreSQL)
- M11: Nexus API endpoints
- M12: Frontend dashboard
- Emergency bypass system
- Audit export format
- Multi-tenancy

## Decision Points for User

1. **Cut to 18 todos?** Or keep the full 48?
2. **PyPI name**: `pact-governance`, `terrene-pact`, or something else?
3. **Repo question**: Standalone, monorepo (kailash-py), or decide after v0.2.0?
4. **Design spike first?** Write Astra's ideal setup code before building GovernanceEngine?
