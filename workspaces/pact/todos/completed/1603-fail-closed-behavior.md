# M16-T03: Fail-closed behavior — TrustStore unreachable

**Status**: ACTIVE
**Priority**: High
**Milestone**: M16 — Gap Closure: Runtime Enforcement
**Dependencies**: 1301-1304

## What

Define and implement fail-closed when TrustStore unreachable:
1. `TrustStoreHealthCheck` validates store connectivity
2. Circuit-breaker activation when store unreachable
3. All actions BLOCKED when trust store is down

## Where

- Modify: `src/pact/persistence/store.py` (add `health_check()` to protocol)
- Modify: `src/pact/persistence/sqlite_store.py` (implement)
- New: `src/pact/persistence/health.py` (TrustStoreHealthCheck)
- Modify: `src/pact/constraint/middleware.py` (check health)

## Evidence

- Test: simulate store failure → all actions BLOCKED
- Test: store recovery → actions resume
