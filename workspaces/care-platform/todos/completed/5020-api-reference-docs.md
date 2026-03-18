# 5020: Auto-generate API reference documentation

**Milestone**: M17 — Documentation Site
**Priority**: Medium
**Effort**: Medium

## What

Generate API reference docs from Python docstrings using sphinx-autodoc or mkdocstrings. Also expose the FastAPI OpenAPI spec at `/docs` (FastAPI's built-in Swagger UI) for the REST API.

## Where

- `docs/api-reference/` — auto-generated module documentation
- `src/care_platform/api/server.py` — enable FastAPI `/docs` endpoint in production

## Evidence

- API reference pages generated for all public modules
- FastAPI `/docs` endpoint accessible and shows all endpoints
- Docstrings rendered correctly in docs site

## Dependencies

- 5019 (docs site must exist first)
