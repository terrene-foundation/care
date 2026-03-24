# TODO-6002: Governance Layer Security Hardening

Status: pending
Priority: critical
Dependencies: [2006]
Milestone: M6

## What

Security review of the governance layer with dedicated tests for each security invariant. This is not a code change to the access algorithm — it is a test-driven verification that the existing implementation meets the security properties that the PACT thesis and trust-plane security rules require.

Five security invariants to verify:

1. **Pre-retrieval gate**: `can_access()` returns its decision before any data is retrieved. No data touches the requester before the algorithm completes. This prevents time-of-check/time-of-use races and ensures the access decision is not influenced by the data itself.

2. **KSP absence is fail-closed**: When no KSP covers an access request, the result must be `DENIED`, never `ALLOWED`. The absence of a policy is not permission.

3. **Compartment checks mandatory for CONFIDENTIAL+**: Per defense-in-depth beyond the spec's SECRET+ requirement: compartment checks are enforced starting at CONFIDENTIAL. An item classified CONFIDENTIAL with a required compartment cannot be accessed by a requester who lacks that compartment, even if their clearance level is sufficient.

4. **No NaN/Inf bypass in clearance comparisons**: If a clearance level comparison receives a NaN or Inf value (via a corrupted or injected record), the result must be `DENIED`. The algorithm must not silently pass a NaN comparison as True.

5. **All addresses validated before use**: Every address passed to `can_access()` or governance store methods is validated via the address grammar from TODO-1001. An address containing `../`, null bytes, or characters outside `[A-Za-z0-9-]` must raise `AddressValidationError`, not silently proceed.

## Where

- `tests/unit/governance/test_security.py`

## Evidence

- Each of the 5 invariants has at least one dedicated test function
- Pre-retrieval test: create a `can_access` call with a mock data-access layer; assert the mock is never called during the access decision
- KSP absence test: call `can_access()` with empty `AccessPolicyStore`; result is `DENIED`
- Compartment test: CONFIDENTIAL item with required compartment `foo`; requester has CONFIDENTIAL clearance but no `foo` compartment; result is `DENIED`
- NaN test: inject a clearance record with `level=float("nan")` equivalent; `can_access()` returns `DENIED`, not `ALLOWED`
- Address validation test: `can_access("../../../etc", knowledge_item, ...)` raises `AddressValidationError`
- `pytest tests/unit/governance/test_security.py` passes

## Details

### Test 1: Pre-retrieval gate

```python
def test_can_access_is_pre_retrieval_gate():
    """can_access() must make its decision before touching any data payload.

    The test verifies that the data retrieval layer (which would fetch the
    actual document content) is never called during access enforcement.
    This ensures the algorithm is a pure gate, not a filter.
    """
    retrieval_calls = []

    class SpyDataLayer:
        def retrieve(self, item_id: str) -> bytes:
            retrieval_calls.append(item_id)
            return b"sensitive data"

    spy = SpyDataLayer()
    result = can_access(
        requester_address="D1-R1-D2-R1",  # Dean of Engineering
        knowledge_item=KnowledgeItem(
            item_id="doc-001",
            classification=ConfidentialityLevel.SECRET,
            item_prefix="/student-affairs/disciplinary/",
            compartments=frozenset({"student-disciplinary"}),
        ),
        compiled_org=_minimal_compiled_org(),
        clearance_store=_engineering_clearance_store(),
        policy_store=_empty_policy_store(),
    )

    assert result.decision == AccessDecision.DENIED
    assert retrieval_calls == [], (
        "can_access() must not retrieve data before making its decision. "
        f"Retrieval was called for: {retrieval_calls}"
    )
```

### Test 2: KSP absence is default-deny

```python
def test_empty_policy_store_is_default_deny():
    """Absence of KSP must produce DENIED, not ALLOWED."""
    result = can_access(
        requester_address="D1-R1-D2-R1",
        knowledge_item=KnowledgeItem(
            item_id="any-item",
            classification=ConfidentialityLevel.PUBLIC,  # Even PUBLIC items
            item_prefix="/any/prefix/",
            compartments=frozenset(),
        ),
        compiled_org=_minimal_compiled_org(),
        clearance_store=_any_clearance_store(),
        policy_store=InMemoryAccessPolicyStore(),  # EMPTY
    )
    assert result.decision == AccessDecision.DENIED, (
        "Empty KSP store must produce DENIED (fail-closed). "
        f"Got {result.decision} — KSP absence must never be treated as permission."
    )
```

Note: PUBLIC items within the same unit may have a special rule (same-unit access). The test must verify the behavior for cross-unit access with no KSP. Create the test with a cross-unit scenario to avoid the same-unit exception.

### Test 3: Compartment mandatory at CONFIDENTIAL+

```python
def test_compartment_enforced_at_confidential():
    """Defense-in-depth: compartment check required starting at CONFIDENTIAL."""
    # Requester: CONFIDENTIAL clearance, no compartments
    # Item: CONFIDENTIAL, requires compartment 'budget-confidential'
    # Expected: DENIED (compartment check fails even though clearance level is sufficient)
    ...

def test_compartment_not_required_below_confidential():
    """RESTRICTED and PUBLIC items: compartment field is informational, not enforced."""
    # Requester: RESTRICTED clearance, no compartments
    # Item: RESTRICTED, has compartment 'routine'
    # Expected: ALLOWED (if KSP present) — compartment not enforced below CONFIDENTIAL
    ...
```

### Test 4: NaN bypass prevention

```python
def test_nan_clearance_level_produces_denied():
    """A NaN or corrupted clearance level must produce DENIED, not ALLOWED.

    NaN bypasses all numeric comparisons (NaN < X is always False).
    The access algorithm must detect and reject non-finite clearance values.
    """
    import math

    # Simulate a corrupted clearance record where the level comparison
    # would receive a NaN-equivalent value
    # The clearance implementation uses ConfidentialityLevel (enum) for level,
    # but the underlying comparison uses integer values from the enum.
    # Inject a fake clearance with a sentinel value that tests the guard.
    ...
```

Implementation note: `ConfidentialityLevel` is an enum, not a float — NaN cannot be directly injected as an enum value. The guard must be on the integer comparison path. Use `math.isfinite(level.value)` in the effective_clearance function if the enum values are integers. Or test via a corrupted JSON record deserialized by `ClearanceStore`.

### Test 5: Address validation

```python
@pytest.mark.parametrize("malicious_address", [
    "../../../etc/passwd",
    "D1-R1\x00evil",
    "/absolute/path",
    "D1-R1; DROP TABLE governance_orgs; --",
    "D1-R1-D2-R1-" + "A" * 1000,  # Excessively long
    "",  # Empty string
])
def test_malicious_address_raises_validation_error(malicious_address: str):
    """Addresses outside [A-Za-z0-9-] grammar must raise AddressValidationError."""
    with pytest.raises(AddressValidationError):
        can_access(
            requester_address=malicious_address,
            knowledge_item=_public_knowledge_item(),
            compiled_org=_minimal_compiled_org(),
            clearance_store=_any_clearance_store(),
            policy_store=_permissive_policy_store(),
        )
```

### Test organization

The test file is organized into 5 sections (one per invariant) with a clear comment header for each. Every test must have a docstring explaining which security invariant it tests and what the failure mode would be if the invariant is violated.

All helper functions (`_minimal_compiled_org()`, `_empty_policy_store()`, etc.) are module-level private functions, not fixtures — they return simple objects constructed inline, avoiding pytest fixture setup overhead.
