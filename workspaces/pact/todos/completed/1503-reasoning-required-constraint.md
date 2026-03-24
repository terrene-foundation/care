# M15-T03: REASONING_REQUIRED constraint type

**Status**: ACTIVE
**Priority**: High
**Milestone**: M15 — EATP v2.2 Alignment
**Dependencies**: 1301-1304

## What

Add `REASONING_REQUIRED` as a meta-constraint attachable to any constraint dimension. When present, any action touching that dimension must include a reasoning trace. Inheritable: parent envelope REASONING_REQUIRED propagates to all children.

## Where

- Modify: `src/pact/config/schema.py` (add `reasoning_required: bool` per dimension)
- Modify: `src/pact/constraint/envelope.py` (check for reasoning trace)
- Modify: `src/pact/trust/delegation.py` (enforce inheritance in tightening)

## Evidence

- Tests: action without reasoning trace is HELD when REASONING_REQUIRED; action with trace passes; child inherits from parent
