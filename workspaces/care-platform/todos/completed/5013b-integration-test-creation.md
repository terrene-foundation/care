# 5013b: Create integration test suite

**Milestone**: M15 — CI/CD Pipeline
**Priority**: High
**Effort**: Medium

## What

Create actual integration tests that exercise the FastAPI server via HTTP. Currently `tests/integration/` has only empty **init**.py files. Use `httpx.AsyncClient` (FastAPI TestClient) to test the full request path: authentication, CORS, endpoint logic, response format.

Minimum coverage:

- `/health` returns 200
- Bearer token auth rejects bad tokens
- `/api/v1/verification/stats` returns valid JSON
- `/api/v1/teams` returns seeded team data
- `/api/v1/agents` returns seeded agent data

## Where

- `tests/integration/test_api_server.py` — new test file
- `tests/integration/conftest.py` — TestClient fixture with seeded data

## Evidence

- `pytest tests/integration/` passes with 5+ tests
- Tests exercise real HTTP paths (not just imported functions)
- CI integration test job has real tests to run

## Dependencies

- 5001-5004 (data wiring — tests need real data)
