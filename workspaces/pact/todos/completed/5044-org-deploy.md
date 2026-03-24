# 5044: Org deploy command

**Milestone**: M21 — Import/Export and CLI
**Priority**: High
**Effort**: Large

## What

Add `pact org deploy --file <org.yaml>` command. Provision an OrgDefinition into the trust store: create genesis records, delegation records, constraint envelopes, attestations. Uses `OrgBuilder.save()` plus `PlatformBootstrap` trust chain creation. This connects the declarative org definition to the runtime trust hierarchy.

## Where

- `src/pact/cli/__init__.py` — add `org deploy` command
- `src/pact/bootstrap.py` — extend to accept OrgDefinition input
- `tests/integration/test_org_deploy.py` — integration test for full deploy cycle

## Evidence

- `pact org deploy --file org.yaml` creates all trust records
- Trust store contains genesis, delegations, envelopes matching the org definition
- `pact org status` shows deployed org health

## Dependencies

- 5042 (import — deploy reads from file), 5034 (multi-team validation)
