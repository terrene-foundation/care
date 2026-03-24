# M17-T04: Management/data plane isolation

**Status**: ACTIVE
**Priority**: Medium
**Milestone**: M17 — Gap Closure: Integrity & Resilience
**Dependencies**: 1601-1605

## What

Management plane (config, bootstrap, org builder) and data plane (runtime, middleware, audit) currently share everything. Introduce logical plane isolation: separate store interfaces for management vs data operations, with explicit boundary crossing points.

## Where

- New: `src/pact/store_isolation/__init__.py` (NOT `planes/` — avoid confusion with CARE's Trust Plane / Execution Plane)
- New: `src/pact/store_isolation/management.py`
- New: `src/pact/store_isolation/data.py`
- Modify: `src/pact/bootstrap.py` (use management plane)
- Modify: `src/pact/execution/runtime.py` (use data plane)

## Evidence

- Test: data plane cannot write to management-only tables
- Test: management plane cannot bypass data plane constraints
