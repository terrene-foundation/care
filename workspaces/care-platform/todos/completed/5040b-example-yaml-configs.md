# 5040b: Ship example YAML org configurations

**Milestone**: M21 — Import/Export and CLI
**Priority**: Medium
**Effort**: Small

## What

Generate and commit `examples/` directory with reference YAML org definitions that users can use with `care-platform org import`. Include: foundation org (full multi-team), minimal org (single team), and one custom template example.

## Where

- `examples/foundation-org.yaml` — full Foundation org definition
- `examples/minimal-org.yaml` — single team starter
- `examples/custom-template.yaml` — example custom team template

## Evidence

- `care-platform org import --file examples/foundation-org.yaml` succeeds
- `care-platform org validate --file examples/minimal-org.yaml` passes
- Examples documented in quickstart tutorial

## Dependencies

- 5041, 5042 (import/export commands must work)
