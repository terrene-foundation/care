# 5046: Foundation org round-trip test

**Milestone**: M22 — Integration and Dog-fooding
**Priority**: High
**Effort**: Medium

## What

Integration test that exercises the full org builder lifecycle: build Foundation org from templates using composition, export to YAML, import from YAML, validate with all rules, deploy to trust store, check status. Proves the builder is production-ready and the Foundation can dog-food its own structure.

## Where

- `tests/integration/test_org_roundtrip.py` — new integration test
- Uses all org builder features: templates, composition, validation, export, import, deploy

## Evidence

- Test passes end-to-end: compose → export → import → validate → deploy → status
- Exported and imported orgs are identical
- Trust store contains correct records after deploy
- Foundation template with all teams validates cleanly

## Dependencies

- 5039 (composition), 5041-5044 (import/export/deploy)
