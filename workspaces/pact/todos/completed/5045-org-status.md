# 5045: Org status command

**Milestone**: M21 — Import/Export and CLI
**Priority**: Medium
**Effort**: Small

## What

Add `pact org status` command showing runtime org health: active agents, pending approvals, trust chain validity, last verification time, constraint envelope coverage.

## Where

- `src/pact/cli/__init__.py` — add `org status` command
- `tests/unit/cli/test_cli.py` — add tests

## Evidence

- Shows team count, agent count, active/suspended breakdown
- Shows pending approval count
- Trust chain validation status (all valid / N issues)

## Dependencies

- 5044 (deploy must work — status checks deployed org)
