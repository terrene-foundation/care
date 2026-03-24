# RT21: Governance Framework Red Team Report

**Date**: 2026-03-21
**Scope**: PACT Governance Framework (M15 hardening)
**Status**: ALL FINDINGS RESOLVED
**Test Count**: 40 adversarial tests across 10 categories

## Executive Summary

This red team round targeted the PACT governance framework with adversarial attacks across access control, envelope bypass, store security, agent self-modification, API authentication, TOCTOU defense, multi-level verification, audit chain integrity, fail-closed behavior, and snapshot versioning. All 40 adversarial tests pass. Two pre-existing failures (backup module and audit integrity method) were resolved before testing began.

## Pre-Existing Failures (Resolved)

| ID   | Issue                                            | Resolution                                                                                   |
| ---- | ------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| PE-1 | `pact.governance.stores.backup` module missing   | Created `stores/backup.py` with `backup_governance_store()` and `restore_governance_store()` |
| PE-2 | `engine.verify_audit_integrity()` method missing | Added method to GovernanceEngine, wired to SqliteAuditLog                                    |

## Findings by Category

### A. Access Bypass Attempts (6 tests)

| Test                            | Attack Vector                                               | Result           | Defense                                            |
| ------------------------------- | ----------------------------------------------------------- | ---------------- | -------------------------------------------------- |
| Forged address outside org tree | Create D99-R99 address not in org                           | BLOCKED (step 1) | No clearance for non-existent address              |
| None posture injection          | Pass None as TrustPostureLevel                              | REJECTED         | TypeError/KeyError on enum lookup                  |
| Empty compartments bypass       | Empty compartments on role vs SECRET item with compartments | BLOCKED (step 3) | frozenset difference catches missing compartments  |
| KSP for non-existent unit       | KSP source_unit_address=D999                                | DENIED           | Source doesn't match item owner                    |
| Bridge to self                  | role_a = role_b = same address                              | DENIED           | Self-bridge doesn't extend domain to foreign units |
| Expired KSP                     | KSP with expires_at in the past                             | DENIED           | Expiry check before access grant                   |

### B. Envelope Bypass Attempts (5 tests)

| Test                  | Attack Vector                  | Result  | Defense                                                           |
| --------------------- | ------------------------------ | ------- | ----------------------------------------------------------------- |
| NaN cost              | float("nan") in action cost    | BLOCKED | math.isfinite() guard in \_evaluate_against_envelope              |
| Inf cost              | float("inf") in action cost    | BLOCKED | math.isfinite() guard                                             |
| Negative cost         | -100.0 cost to reduce spend    | BLOCKED | Explicit negative check                                           |
| Empty allowed_actions | allowed_actions=[] on envelope | BLOCKED | Changed from `if allowed_actions and` to always enforce allowlist |
| Zero max_spend        | $0 budget with $0.01 action    | BLOCKED | cost > max_spend comparison                                       |

**Security Fix Applied**: The `_evaluate_against_envelope` method previously treated empty `allowed_actions` as "no restriction" (`if allowed_actions and action not in allowed_actions`). This was changed to always enforce the allowlist when an envelope exists. The existence of an envelope means constraints are explicitly defined; `allowed_actions=[]` means no actions are allowed.

### C. Store Bypass Attempts (4 tests)

| Test                  | Attack Vector                          | Result         | Defense                                  |
| --------------------- | -------------------------------------- | -------------- | ---------------------------------------- |
| Path traversal in IDs | ../../etc/passwd, /etc/shadow, etc.    | REJECTED       | _validate_id regex: `^[a-zA-Z0-9_-]+$`   |
| SQL injection         | `'; DROP TABLE pact_orgs; --`          | REJECTED       | \_validate_id + parameterized queries    |
| Concurrent writes     | Two threads writing same key 100x each | NO CORRUPTION  | threading.Lock on all store methods      |
| Exceed MAX_STORE_SIZE | 10,010 entries (limit=10,000)          | EVICTED OLDEST | OrderedDict.popitem(last=False) eviction |

### D. Agent Bypass Attempts (4 tests)

| Test                            | Attack Vector                | Result                 | Defense                                   |
| ------------------------------- | ---------------------------- | ---------------------- | ----------------------------------------- |
| Modify GovernanceContext fields | ctx.posture = DELEGATED      | REJECTED               | frozen=True dataclass                     |
| Access engine through agent     | agent.context.engine         | NO ATTRIBUTE           | GovernanceContext has no engine field     |
| Call unregistered tool          | execute_tool("unregistered") | GovernanceBlockedError | DEFAULT-DENY tool access                  |
| NaN cost in tool call           | register_tool(cost=NaN)      | GovernanceBlockedError | NaN caught in \_evaluate_against_envelope |

### E. API Bypass Attempts (4 tests)

| Test                   | Attack Vector          | Result                       | Defense                                      |
| ---------------------- | ---------------------- | ---------------------------- | -------------------------------------------- |
| Unauthenticated access | No bearer token        | 401 Unauthorized             | GovernanceAuth.verify_token                  |
| Wrong token            | Invalid bearer token   | 401 Unauthorized             | hmac.compare_digest constant-time comparison |
| Timing attack on token | Byte-at-a-time forgery | MITIGATED                    | Verified hmac.compare_digest in source       |
| Dev mode bypass        | No token configured    | Anonymous access (by design) | Documented dev-mode behavior                 |

### F. TOCTOU Defense (6 tests)

| Test                        | Attack Vector                          | Result  | Defense                                |
| --------------------------- | -------------------------------------- | ------- | -------------------------------------- |
| Envelope version in verdict | Verify presence of version hash        | PRESENT | SHA-256 of contributor versions + IDs  |
| Version changes on update   | Update envelope, check hash changed    | CHANGED | Envelope ID included in hash input     |
| Version in audit_details    | envelope_version must be auditable     | PRESENT | Included in verdict.audit_details      |
| valid_until from KSP        | KSP expiry reflected in AccessDecision | CORRECT | valid_until set from ksp.expires_at    |
| valid_until from bridge     | Bridge expiry reflected                | CORRECT | valid_until set from bridge.expires_at |
| Structural access no expiry | Same-unit access has no valid_until    | CORRECT | valid_until=None for structural paths  |

### G. Multi-Level VERIFY (3 tests)

| Test                           | Attack Vector                         | Result        | Defense                                       |
| ------------------------------ | ------------------------------------- | ------------- | --------------------------------------------- |
| Leaf allowed, ancestor blocked | deploy allowed at leaf, blocked by VP | BLOCKED       | Multi-level verify walks accountability chain |
| All levels allow               | read allowed everywhere               | AUTO_APPROVED | No escalation needed                          |
| Ancestor cost limit            | VP $100, leaf $1000, action $500      | BLOCKED       | Effective envelope intersection uses min()    |

### H. Audit Chain Integrity (2 tests)

| Test                     | Scenario                        | Result      | Defense                                |
| ------------------------ | ------------------------------- | ----------- | -------------------------------------- |
| Mutations create entries | grant_clearance + create_bridge | VALID CHAIN | SqliteAuditLog with hash chain         |
| Tampered entry detected  | UPDATE details_json via SQL     | DETECTED    | content_hash + chain_hash verification |

### I. Fail-Closed Behavior (2 tests)

| Test                       | Scenario               | Result  | Defense                            |
| -------------------------- | ---------------------- | ------- | ---------------------------------- |
| verify_action on exception | Broken envelope store  | BLOCKED | try/except returns BLOCKED verdict |
| check_access on exception  | Broken clearance store | DENIED  | try/except returns DENY decision   |

### J. Snapshot Versioning (4 tests)

| Test                              | Scenario            | Result            | Defense                                        |
| --------------------------------- | ------------------- | ----------------- | ---------------------------------------------- |
| Same inputs, same hash            | Identical envelopes | IDENTICAL HASH    | Deterministic SHA-256 input                    |
| Different version, different hash | Version 1 vs 2      | DIFFERENT HASH    | Version number in hash input                   |
| No envelopes, empty hash          | No contributors     | EMPTY STRING      | Correct sentinel for no-envelope case          |
| Contributor versions tracked      | Check tracking dict | CORRECTLY TRACKED | EffectiveEnvelopeSnapshot.contributor_versions |

## Implementation Changes

### New Files

- `src/pact/governance/stores/backup.py` -- Backup/restore for all governance state

### Modified Files

- `src/pact/governance/engine.py` -- Added verify_audit_integrity(), SqliteAuditLog integration, multi-level VERIFY, versioned envelope computation, empty allowed_actions fix
- `src/pact/governance/envelopes.py` -- Added EffectiveEnvelopeSnapshot, compute_effective_envelope_with_version()
- `src/pact/governance/verdict.py` -- Added envelope_version field
- `src/pact/governance/access.py` -- Added valid_until field to AccessDecision

### Security Hardening

1. Empty `allowed_actions` now blocks all actions (was previously treated as "no restriction")
2. Envelope version hash includes envelope IDs for full TOCTOU detection
3. Multi-level verify walks full accountability chain
4. AccessDecision includes temporal validity bounds from KSP/bridge expiry
5. Audit entries emitted to both EATP chain and SQLite audit log

## Conclusion

All 40 adversarial tests pass. The governance framework demonstrates defense-in-depth:

- Fail-closed on all error paths (BLOCKED/DENIED, never permissive)
- NaN/Inf rejection at every numeric boundary
- Thread-safe stores with bounded collections
- Frozen dataclasses preventing self-modification
- TOCTOU-resilient versioned envelope snapshots
- Multi-level verification preventing ancestor bypass
- Append-only audit log with cryptographic hash chain
