# 5040: Template validation on registration

**Milestone**: M20 — Template Library Expansion
**Priority**: Medium
**Effort**: Small

## What

Run `validate_org()` on each template at TemplateRegistry load time to catch template bugs early. Any template that fails validation should be rejected with a clear error at startup.

## Where

- `src/pact/templates/registry.py` — add validation in `register()` and `__init__()`
- `tests/unit/templates/test_registry.py` — add test for invalid template rejection

## Evidence

- Invalid templates are rejected at registration with validation errors
- All built-in templates pass validation at startup
- Registration failure includes specific validation error details

## Dependencies

- 5029-5035 (validation suite complete)
