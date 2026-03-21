# 5024: Configure structured logging with structlog

**Milestone**: M18 — Production Hardening
**Priority**: Medium
**Effort**: Small

## What

Wire structlog (already a dependency) as the default logger for production. JSON output format for production, human-readable for development. Configure via environment variable (CARE_LOG_FORMAT=json|console).

## Where

- `src/pact/observability/logging.py` — configure structlog
- `src/pact/config/env.py` — add CARE_LOG_FORMAT setting

## Evidence

- Production mode outputs JSON-formatted logs
- Development mode outputs human-readable logs
- All existing log calls work through structlog

## Dependencies

- None (independent)
