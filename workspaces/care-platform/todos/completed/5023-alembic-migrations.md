# 5023: Set up Alembic database migrations

**Milestone**: M18 — Production Hardening
**Priority**: High
**Effort**: Medium

## What

Initialize `alembic/` directory with initial migration script. Alembic is already a dependency in pyproject.toml but no migrations directory exists. Create the initial migration matching the current database schema.

## Where

- `alembic/` — new directory with alembic.ini, env.py, versions/
- `alembic.ini` — at repo root

## Evidence

- `alembic upgrade head` creates the database schema
- `alembic downgrade base` cleanly removes all tables
- Migration matches current database schema exactly

## Dependencies

- None (can start independently)
