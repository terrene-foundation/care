# 5039: Multi-team template composition

**Milestone**: M20 — Template Library Expansion
**Priority**: High
**Effort**: Large

## What

Compose a full OrgDefinition from multiple TeamTemplates with workspace and bridge wiring. This is the Org Builder capstone — build a complete organization from template parts. Example: combine media + governance + engineering templates into one org with cross-team bridges.

## Where

- `src/pact/org/builder.py` — add `compose_from_templates()` method to OrgBuilder
- `src/pact/templates/registry.py` — add composition support
- `tests/unit/org/test_builder.py` — add composition tests

## Evidence

- `OrgBuilder.compose_from_templates(["media", "governance", "engineering"])` produces valid OrgDefinition
- Cross-team workspace paths don't conflict
- Multi-team validation passes on composed org
- Foundation template refactored to use composition

## Dependencies

- 5034 (multi-team validation), 5036-5038 (templates exist to compose)
