# 5041: YAML export command

**Milestone**: M21 — Import/Export and CLI
**Priority**: High
**Effort**: Medium

## What

Add `pact org export --org-id <id> --output <file.yaml>` command. Serializes an OrgDefinition to YAML using Pydantic's `model_dump()` + PyYAML. Include all teams, agents, envelopes, workspaces.

## Where

- `src/pact/cli/__init__.py` — add `org export` command
- `tests/unit/cli/test_cli.py` — add export tests

## Evidence

- `pact org export --org-id terrene-foundation --output org.yaml` produces valid YAML
- YAML can be re-imported (round-trip)
- All org data preserved in export

## Dependencies

- None (CLI infrastructure exists)
