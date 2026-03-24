# TODO-2002: KnowledgeItem classification type

Status: pending
Priority: high
Dependencies: [1001]
Milestone: M2

## What

Implement the `KnowledgeItem` dataclass per PACT-REQ-004. A `KnowledgeItem` is any piece of information that lives inside the governed organization — a document, dataset, report, decision record, or communication thread. Every item carries a classification label and an owning unit address so the access algorithm knows which D/T/R node is responsible.

Key fields:

- `item_id`: unique identifier (string, validated: alphanumeric + underscore/hyphen only)
- `classification`: `ConfidentialityLevel` — the sensitivity of the item
- `compartments`: `frozenset[str]` — named compartments, meaningful only at SECRET and above (at lower classifications this field is ignored by the access algorithm)
- `owning_unit_address`: D/T/R positional address (from TODO-1001) of the D or T that owns this item
- `title`: human-readable label (no PII in the title field)
- `metadata`: `dict[str, Any]` for extension fields

Validation rules:

- `item_id` must match `^[a-zA-Z0-9_-]+$` (path traversal prevention, consistent with trust-plane security rule).
- `classification` is required and has no default (fail-closed: unclassified items must be explicitly set to PUBLIC, not inferred).
- `owning_unit_address` must parse as a valid D or T address (not an R address — knowledge is owned by organisational units, not individual roles). Parsing uses the address parser from TODO-1001.
- Compartments at PUBLIC through CONFIDENTIAL must be empty (or are ignored with a warning).

This is a small, focused type. Its primary consumers are the access algorithm (TODO-2006) and the knowledge cascade rules (TODO-2005).

## Where

- `src/pact/governance/knowledge.py` — `KnowledgeItem` dataclass
- `tests/unit/governance/test_knowledge_item.py`

## Evidence

- `KnowledgeItem(item_id="rpt_001", classification=ConfidentialityLevel.PUBLIC, owning_unit_address="D1-R1")` constructs successfully.
- `KnowledgeItem(item_id="trade_blotter", classification=ConfidentialityLevel.SECRET, compartments=frozenset(["TRADING"]), owning_unit_address="D1-R1-T1-R1")` constructs successfully.
- `KnowledgeItem(item_id="../etc/passwd", ...)` raises `ValueError` (path traversal guard).
- `KnowledgeItem(classification=ConfidentialityLevel.PUBLIC, compartments=frozenset(["X"]), ...)` raises `ValueError` (compartments not valid below SECRET).
- `KnowledgeItem(owning_unit_address="D1-R1-T1-R1-R2", ...)` raises `AddressError` (R address is not a valid owner).
- `to_dict()` round-trips through `from_dict()` with identical field values.

## Details

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from pact.build.config.schema import ConfidentialityLevel

_ITEM_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")

@dataclass
class KnowledgeItem:
    item_id: str
    classification: ConfidentialityLevel
    owning_unit_address: str       # D or T address — validated via TODO-1001 parser
    compartments: frozenset[str] = field(default_factory=frozenset)
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _ITEM_ID_RE.match(self.item_id):
            raise ValueError(f"item_id must match [a-zA-Z0-9_-]+, got: {self.item_id!r}")
        # compartments only valid at SECRET+
        if self.compartments and self.classification not in (
            ConfidentialityLevel.SECRET, ConfidentialityLevel.TOP_SECRET
        ):
            raise ValueError(
                "compartments may only be set for SECRET or TOP_SECRET items"
            )
        # validate owning_unit_address is a D or T node (not R)
        # uses address parser from TODO-1001

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeItem: ...
```

Keep this module lean. Do not pull in access logic — that belongs in `access.py` (TODO-2006). The `knowledge.py` module holds only the data type and its validation.
