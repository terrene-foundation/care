# 5038: Custom template from YAML file

**Milestone**: M20 — Template Library Expansion
**Priority**: High
**Effort**: Medium

## What

Enable loading a `TeamTemplate` from a YAML file matching the TeamTemplate Pydantic model schema. CLI: `care-platform org create --template-file path/to/template.yaml`. This lets users define their own team types without modifying the registry code.

## Where

- `src/care_platform/templates/registry.py` — add `load_from_yaml()` method
- `src/care_platform/cli/__init__.py` — add `--template-file` option to `org create`
- `tests/unit/templates/test_registry.py` — add YAML loading tests

## Evidence

- `care-platform org create --template-file custom.yaml --name "My Team"` works
- YAML schema validated against TeamTemplate model
- Clear error messages for invalid YAML

## Dependencies

- 5036 (template system working)
