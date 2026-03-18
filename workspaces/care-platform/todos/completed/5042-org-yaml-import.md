# 5042: YAML/JSON import command

**Milestone**: M21 — Import/Export and CLI
**Priority**: High
**Effort**: Medium

## What

Add `care-platform org import --file <org.yaml>` command. Parse YAML or JSON into OrgDefinition, run full `validate_org()`, report results. Supports both YAML and JSON based on file extension.

## Where

- `src/care_platform/cli/__init__.py` — add `org import` command
- `tests/unit/cli/test_cli.py` — add import tests

## Evidence

- `care-platform org import --file org.yaml` loads and validates the org
- Validation errors reported clearly
- Both YAML and JSON formats supported

## Dependencies

- 5041 (export must exist for round-trip testing)
