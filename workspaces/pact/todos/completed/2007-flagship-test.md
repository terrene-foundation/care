# TODO-2007: Flagship scenario end-to-end test

Status: pending
Priority: critical
Dependencies: [2006]
Milestone: M2

## What

Implement the flagship financial services scenario from thesis Section 7.1 as a single end-to-end test module. This is the proof-of-concept that demonstrates PACT's knowledge governance in a realistic context. It builds a complete (small) financial services organisation, assigns clearances and bridges, then verifies that access decisions match the thesis-specified outcomes.

This test has no production code — it is test-only. Its purpose is:

1. Validate the correctness of the entire M2 implementation in one coherent scenario.
2. Serve as a living specification example that documents how the system behaves.
3. Detect regressions: if any M2 component changes, this test breaks immediately.

Organisation structure (thesis Section 7.1):

```
D1-R1: Chief Compliance Officer (CCO) — oversight role
  D1-R1-T1-R1: Advisory Department
    D1-R1-T1-R1-T1-R1: Advisory Analyst
  D1-R1-T2-R1: Trading Department
    D1-R1-T2-R1-T1-R1: Head of Trading
    D1-R1-T2-R1-T2-R1: Trader
  D1-R1-T3-R1: Compliance Department
    D1-R1-T3-R1-T1-R1: AML Officer
```

(Note: exact address strings depend on TODO-1001 implementation. The test constructs these using the address builder from TODO-1001, not hardcoded strings.)

Clearances:

| Role                       | Clearance Level | Compartments | Vetting |
| -------------------------- | --------------- | ------------ | ------- |
| CCO (D1-R1-R1)             | SECRET          | none         | ACTIVE  |
| Advisory Analyst (T1 leaf) | RESTRICTED      | none         | ACTIVE  |
| Head of Trading (T2 leaf)  | SECRET          | TRADING      | ACTIVE  |
| Trader (T2 leaf)           | CONFIDENTIAL    | TRADING      | ACTIVE  |
| AML Officer (T3 leaf)      | SECRET          | AML          | ACTIVE  |

Bridges (Standing, approved by CCO at D1-R1):

- CCO <-> Advisory: bilateral, max_classification=CONFIDENTIAL, scope={read, review}
- CCO <-> Trading: bilateral, max_classification=CONFIDENTIAL, scope={read, review}

Knowledge items:

| Item                  | Owner   | Classification | Compartments |
| --------------------- | ------- | -------------- | ------------ |
| advisory_report_001   | T1 dept | CONFIDENTIAL   | none         |
| trading_blotter       | T2 dept | CONFIDENTIAL   | TRADING      |
| aml_investigation_007 | T3 dept | SECRET         | AML          |
| market_news_feed      | T2 dept | PUBLIC         | none         |

Trust postures (all agents at CONTINUOUS_INSIGHT for this scenario unless otherwise specified):

| Role             | Posture                                                   |
| ---------------- | --------------------------------------------------------- |
| CCO              | SUPERVISED (SECRET clearance requires SUPERVISED ceiling) |
| Advisory Analyst | CONTINUOUS_INSIGHT                                        |
| Head of Trading  | SUPERVISED (SECRET clearance)                             |
| AML Officer      | SUPERVISED (SECRET clearance)                             |

Access assertions (all must pass):

1. Advisory Analyst reads `advisory_report_001` (own department, CONFIDENTIAL, clearance=RESTRICTED): **DENIED** at step 2 (RESTRICTED < CONFIDENTIAL).
2. Advisory Analyst reads `market_news_feed` (cross-unit, PUBLIC, no KSP): **DENIED** at step 4 (no KSP to Trading). Illustrates: PUBLIC does not mean universally accessible across boundaries.
3. CCO reads `advisory_report_001` via bridge: **ALLOWED** (bridge covers CONFIDENTIAL, CCO has SECRET).
4. CCO reads `trading_blotter` via bridge: **ALLOWED** (bridge covers CONFIDENTIAL, CCO has SECRET, compartment check: trading_blotter has TRADING compartment but CCO has no compartments — check whether CCO needs compartment or whether bridge supersedes). Per thesis: bridge does NOT grant compartment clearance. **DENIED** at step 3 unless CCO explicitly holds TRADING compartment. Use CCO with TRADING compartment to test the allowed path, and CCO without to test the denied path.
5. AML Officer reads `aml_investigation_007` (own dept, SECRET/[AML], clearance=SECRET/[AML]): **ALLOWED** at step 4 (same-unit, compartment matches).
6. Head of Trading reads `aml_investigation_007` (cross-unit, SECRET/[AML], clearance=SECRET/[TRADING]): **DENIED** at step 3 (missing AML compartment).
7. Trader reads `trading_blotter` (own dept, CONFIDENTIAL/[TRADING], clearance=CONFIDENTIAL/[TRADING], posture=CONTINUOUS_INSIGHT): **ALLOWED** (same-unit, clearance=CONFIDENTIAL matches, compartment matches, posture check: CONFIDENTIAL requires SHARED_PLANNING minimum; CONTINUOUS_INSIGHT > SHARED_PLANNING so passes).
8. Advisory Analyst attempts write to `advisory_report_001` (own dept, CONFIDENTIAL): **DENIED** at step 2 (clearance insufficient for CONFIDENTIAL).

## Where

- `tests/unit/governance/test_flagship_scenario.py`

## Evidence

All 8 access assertions pass. Test file is self-contained — it builds the entire organisation, clearances, bridges, and knowledge items from scratch using only the M2 public API. Running `pytest tests/unit/governance/test_flagship_scenario.py -v` passes with no failures.

No production code changes in this todo. If a test fails, the fix belongs in the 2001-2006 series.

## Details

Structure the test as a pytest module with a shared `@pytest.fixture` that builds the full org context (addresses, clearances, bridges, items). Individual test functions call `can_access()` with the appropriate inputs and assert the expected `AccessDecision`.

```python
# tests/unit/governance/test_flagship_scenario.py

import pytest
from pact.governance.clearance import RoleClearance, VettingStatus
from pact.governance.knowledge import KnowledgeItem
from pact.governance.access import (
    KnowledgeSharePolicy, PactBridge, BridgeType, can_access
)
from pact.build.config.schema import ConfidentialityLevel, TrustPostureLevel

@pytest.fixture
def fin_org():
    """Build the financial services org context from thesis Section 7.1."""
    # Addresses — constructed via TODO-1001 address builder
    # Clearances
    # Bridges
    # Knowledge items
    return FinOrgContext(...)

def test_advisory_analyst_blocked_from_confidential(fin_org):
    decision = can_access(
        requester_address=fin_org.advisory_analyst_addr,
        requester_clearance=fin_org.advisory_analyst_clearance,
        requester_posture=TrustPostureLevel.CONTINUOUS_INSIGHT,
        item=fin_org.advisory_report_001,
        ksp_registry=[],
        bridge_registry=[],
    )
    assert not decision.allowed
    assert decision.step_failed == 2

def test_cco_reads_advisory_via_bridge(fin_org):
    decision = can_access(
        requester_address=fin_org.cco_addr,
        requester_clearance=fin_org.cco_clearance,
        requester_posture=TrustPostureLevel.SUPERVISED,
        item=fin_org.advisory_report_001,
        ksp_registry=[],
        bridge_registry=fin_org.bridges,
    )
    assert decision.allowed
    assert decision.rule_applied == "bridge"

# ... 6 more test functions
```

Approximate size: ~300 LOC.
