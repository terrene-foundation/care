# 5028: Complete .env.example with all config vars

**Milestone**: M18 — Production Hardening
**Priority**: Medium
**Effort**: Small

## What

Ensure `.env.example` documents all required and optional environment variables: CARE_API_TOKEN, POSTGRES_PASSWORD, ANTHROPIC_API_KEY, OPENAI_API_KEY, CARE_LOG_FORMAT, CARE_ENV, etc. Docker Compose references this for setup instructions.

## Where

- `.env.example` — update with all variables and documentation comments

## Evidence

- Every env var used in the codebase is documented in .env.example
- Each variable has a comment explaining its purpose
- `cp .env.example .env` + fill values = working setup

## Dependencies

- 5024 (structured logging adds CARE_LOG_FORMAT)
