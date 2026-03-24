# TODO-6004: Final Convergence Validation

Status: pending
Priority: critical
Dependencies: [0001, 0002, 0003, 0004, 0005, 1001, 1002, 1003, 1004, 1005, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 3001, 3002, 3003, 3004, 3005, 3006, 4001, 4002, 4003, 4004, 5001, 5002, 5003, 5004, 5005, 6001, 6002, 6003]
Milestone: M6

## What

Final convergence validation across the full test suite. All previous milestones are complete; this todo runs the complete suite, verifies the framework boundary, validates the public API, and confirms the flagship scenario works end-to-end. No new code is written — this is a validation and cleanup pass.

Five checks:

1. **Full test suite passes** — all existing tests (3,547+) plus all new governance tests pass with zero failures.

2. **Domain boundary clean** — `src/pact/build/`, `src/pact/trust/`, `src/pact/use/` contain zero domain-specific vocabulary. The boundary test command returns clean.

3. **Public API surface validated** — every symbol in `pact.governance.__all__` is importable and tested. No internal implementation details leaked.

4. **Flagship scenario end-to-end** — the canonical demonstration (CS-department agent denied access to student disciplinary records) runs as documented in the thesis.

5. **Lint passes** — `ruff check src/ tests/` and `ruff format --check src/ tests/` pass with zero errors.

## Where

- `tests/` (run full suite)
- No new source files — convergence is a validation task, not an implementation task

## Evidence

- `pytest --tb=short -q` exits with code 0
- Zero test failures, zero errors
- Test count is at least 3,547 + all new governance tests
- Boundary check command returns "Boundary clean":
  ```
  grep -rn 'DmTeam\|dm_team\|DigitalMedia\|digital_media\|FoundationOrg\|foundation_org\|dm_runner\|dm_prompts' \
    src/pact/build/ src/pact/trust/ src/pact/use/ \
    && echo "BOUNDARY VIOLATION" || echo "Boundary clean"
  ```
- `python -c "from pact.governance import Address, CompiledOrg, RoleClearance, KnowledgeSharePolicy, PactBridge, can_access, RoleEnvelope, TaskEnvelope, compute_effective_envelope"` exits with code 0
- Flagship scenario:
  ```python
  from pact.examples.university.org import build_university_org
  from pact.governance import compile_org, can_access, InMemoryOrgStore, InMemoryClearanceStore, InMemoryAccessPolicyStore
  from pact.examples.university.clearance import build_university_clearances
  from pact.examples.university.barriers import build_university_barriers, build_university_bridges
  # ... setup ...
  result = can_access("D1-R1-D2-R1", student_conduct_record, ...)
  assert result.decision == "DENIED"
  print("Flagship scenario: PASS")
  ```
  Running this script exits with code 0 and prints "Flagship scenario: PASS".
- `ruff check src/ tests/` exits with code 0
- `ruff format --check src/ tests/` exits with code 0

## Details

### Step-by-step validation checklist

1. Run the full test suite:

   ```bash
   cd /Users/esperie/repos/terrene/pact
   pytest --tb=short -q 2>&1 | tail -20
   ```

   Expected: last line is `X passed in Y.Ys` with no failures or errors.

2. Count governance tests:

   ```bash
   pytest tests/unit/governance/ tests/integration/governance/ --collect-only -q 2>&1 | tail -5
   ```

   Expected: at least 150 governance tests collected.

3. Run boundary check:

   ```bash
   grep -rn \
     'DmTeam\|dm_team\|DigitalMedia\|digital_media\|FoundationOrg\|foundation_org\|dm_runner\|dm_prompts' \
     src/pact/build/ src/pact/trust/ src/pact/use/ \
     && echo "BOUNDARY VIOLATION" || echo "Boundary clean"
   ```

   Expected: "Boundary clean"

4. Run public API import check:

   ```bash
   python -c "
   from pact.governance import (
       Address, CompiledOrg, compile_org,
       RoleClearance, VettingStatus, effective_clearance,
       KnowledgeItem, ConfidentialityLevel,
       KnowledgeSharePolicy, PactBridge, BridgeType,
       can_access, AccessDecision,
       RoleEnvelope, TaskEnvelope, compute_effective_envelope,
       OrgStore, EnvelopeStore, ClearanceStore, AccessPolicyStore,
       InMemoryOrgStore, InMemoryEnvelopeStore, InMemoryClearanceStore, InMemoryAccessPolicyStore,
       SQLiteGovernanceStore,
       PactAuditAction, BarrierEnforcedDetails, create_pact_audit_anchor,
       PactGovernanceError, OrgNotFoundError, EnvelopeNotFoundError,
       ClearanceNotFoundError, ClearanceStateError, PolicyNotFoundError, BridgeNotFoundError,
   )
   print('All governance imports: OK')
   "
   ```

5. Run flagship scenario script:

   ```bash
   python -c "
   from pact.examples.university.org import build_university_org
   from pact.governance import compile_org, can_access, AccessDecision
   from pact.governance import InMemoryOrgStore, InMemoryClearanceStore, InMemoryAccessPolicyStore
   from pact.governance import KnowledgeItem, ConfidentialityLevel
   from pact.examples.university.clearance import build_university_clearances
   from pact.examples.university.barriers import build_university_barriers, build_university_bridges

   compiled = compile_org(build_university_org())
   org_store = InMemoryOrgStore()
   org_store.store_org('uni', compiled.to_dict())
   clearance_store = InMemoryClearanceStore()
   for c in build_university_clearances():
       clearance_store.store_clearance(c.role_address, c.to_dict())
   policy_store = InMemoryAccessPolicyStore()
   for ksp in build_university_barriers():
       policy_store.store_ksp(ksp.policy_id, ksp.to_dict())
   for bridge in build_university_bridges():
       policy_store.store_bridge(bridge.bridge_id, bridge.to_dict())

   student_conduct_record = KnowledgeItem(
       item_id='case-2026-042',
       classification=ConfidentialityLevel.SECRET,
       item_prefix='/student-affairs/disciplinary/',
       compartments=frozenset({'student-disciplinary'}),
   )

   result = can_access(
       requester_address='D1-R1-D2-R1',
       knowledge_item=student_conduct_record,
       org_id='uni',
       org_store=org_store,
       clearance_store=clearance_store,
       policy_store=policy_store,
   )

   assert result.decision == AccessDecision.DENIED, f'Expected DENIED, got {result.decision}'
   print('Flagship scenario: PASS')
   "
   ```

6. Run lint:
   ```bash
   ruff check src/ tests/ && echo "Lint: PASS"
   ruff format --check src/ tests/ && echo "Format: PASS"
   ```

### What to fix if something fails

- **Test failures in existing tests**: These are pre-existing failures that must be fixed. Per zero-tolerance rules, "pre-existing" is not a valid skip reason.
- **Boundary violations**: Grep the violation, move the domain vocabulary to `src/pact/examples/`.
- **Import failures**: Check `pact.governance.__init__.py` exports match what's actually defined in each module.
- **Lint errors**: Run `ruff check --fix src/ tests/` to auto-fix, then manually address remaining issues.

### Definition of "done" for PACT MVP

After this convergence check passes, the PACT framework satisfies the Minimum Viable PACT definition:

- `pip install pact` (from source) works
- `from pact.governance import ...` gives access to all PACT primitives
- The university example vertical compiles and runs
- The flagship scenario (clearance-independence from authority) is demonstrable
- All tests pass
- The framework contains zero domain vocabulary (ready for astra/arbor to import)
