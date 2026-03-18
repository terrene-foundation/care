# 5043: Org diff command

**Milestone**: M21 — Import/Export and CLI
**Priority**: Medium
**Effort**: Medium

## What

Add `care-platform org diff <file1.yaml> <file2.yaml>` command. Compare two OrgDefinition files and show added/removed/changed agents, teams, envelopes. Useful for reviewing governance changes before applying them.

## Where

- `src/care_platform/org/builder.py` — add `OrgDefinition.diff()` method
- `src/care_platform/cli/__init__.py` — add `org diff` command
- `tests/unit/org/test_builder.py` — add diff tests

## Evidence

- Diff shows added agents in green, removed in red, changed in yellow
- Changes to constraint envelopes show which dimensions changed
- Empty diff when comparing identical files

## Dependencies

- 5041, 5042 (export/import for creating files to diff)
