# TODO-1003: Org Compilation with Address Assignment

Status: pending
Priority: critical
Dependencies: [1001, 1002]
Milestone: M1

## What

Implement `compile_org(org: OrgDefinition) -> CompiledOrg` in
`src/pact/governance/compilation.py`. This function takes the flat list of
`RoleDefinition` objects from an `OrgDefinition` and produces a fully addressed
org tree where every node has a unique positional `Address`.

The compilation process:

1. Builds a parent-child tree from `reports_to_role_id` chains
2. Applies skeleton enforcement: if a D or T unit has no head role
   (`is_primary_for_unit=True`), auto-create a vacant head role
3. Assigns addresses via depth-first traversal — each D/T unit gets the next
   available unit number at its depth level, and each role gets the next available
   role number within its unit
4. Returns a `CompiledOrg` that supports node lookup by address

The financial services example from PACT thesis Section 7.1 must compile correctly
and produce the expected address assignments. See Details section for the expected
address mapping.

## Where

- `src/pact/governance/compilation.py` — `CompiledOrg`, `CompiledNode`, `compile_org`
- `tests/unit/governance/test_compilation.py` — test suite (~500 LOC)

## Evidence

- `compile_org(org)` where `org` has roles with valid `reports_to_role_id` chains
  returns a `CompiledOrg` without error
- The financial services example (see Details) produces correct addresses:
  - CEO role → `D1-R1`
  - CFO role → `D1-R1-D2-R1`
  - Head of Trading → `D1-R1-D2-R1-D3-R1`
  - Head of Compliance → `D1-R1-D1-R1` (or per the thesis schema — exact mapping TBD)
- Skeleton enforcement: an org where a department has no head role auto-creates
  a vacant `CompiledNode` for the head position
- Grammar violations rejected after skeleton enforcement: an org that still violates
  D/T/R grammar after auto-creation raises `CompilationError`
- `compiled.get_node(address)` returns the `CompiledNode` for a valid address
- `compiled.get_node(address)` raises `NodeNotFoundError` for unknown address
- `compiled.query_by_prefix("D1-R1")` returns all nodes whose address starts with
  `D1-R1` (all nodes in the CEO's subtree)
- `pytest tests/unit/governance/test_compilation.py` passes

## Details

### CompiledNode

```python
@dataclass
class CompiledNode:
    """A role node with a fully assigned positional address."""

    address: Address
    # The computed positional address for this role.

    role_def: RoleDefinition
    # The original role definition (may be auto-created for skeleton enforcement).

    children: list["CompiledNode"] = field(default_factory=list)
    # Direct reports in the org tree (roles that report_to this role).

    is_skeleton: bool = False
    # True when this node was auto-created by skeleton enforcement (no definition
    # existed in the OrgDefinition).

    parent: "CompiledNode | None" = None
    # Parent node in the tree. None for the root.
```

### CompiledOrg

```python
@dataclass
class CompiledOrg:
    """An organization definition with fully assigned positional addresses."""

    name: str
    root: CompiledNode
    # The root node (BOD chair or CEO, whichever is the trust root).

    _index: dict[str, CompiledNode]
    # Internal address → node lookup table. Populated during compilation.

    def get_node(self, address: Address | str) -> CompiledNode:
        """Look up a node by address. Raises NodeNotFoundError if not found."""

    def query_by_prefix(self, prefix: Address | str) -> list[CompiledNode]:
        """Return all nodes whose address starts with the given prefix,
        ordered depth-first. Includes the prefix node itself if it exists."""

    def get_subtree(self, address: Address | str) -> list[CompiledNode]:
        """Return the node at address and all its descendants, depth-first."""

    def all_nodes(self) -> list[CompiledNode]:
        """Return all nodes in the compiled org, depth-first."""
```

### Address assignment algorithm

The algorithm assigns addresses via depth-first traversal of the role tree:

1. Build the tree: for each role with `reports_to_role_id=X`, attach it as a child
   of the role with `role_id=X`
2. Identify the root role (role with `reports_to_role_id=None`)
3. Apply skeleton enforcement (see below)
4. Begin depth-first traversal from the root:
   - Each D/T node that is a `is_primary_for_unit=True` role with a `unit_id`
     gets a unit number at its depth level
   - The role within that unit gets a role number
   - Non-primary roles within a unit share the unit's D/T number but get their
     own R number

Address numbering convention:

- Unit numbers (D or T) increment depth-by-depth, left-to-right
- Role numbers (R) within a unit increment top-to-bottom among siblings in that unit
- The root unit is always D1 (or T1 if the root is a team, though this is unusual)

Example address assignment for a 3-level financial services org:

```
Root:   CEO (primary for Board D1)         → D1-R1
Level 2:
  CFO (primary for Finance Dept D2)        → D1-R1-D2-R1
  COO (primary for Operations Dept D3)     → D1-R1-D3-R1
  CRO (primary for Risk Dept D4)           → D1-R1-D4-R1
Level 3 under Finance:
  Head of FP&A (primary for FPA Team T1)   → D1-R1-D2-R1-T1-R1
  Controller (primary for Accounting T2)   → D1-R1-D2-R1-T2-R1
```

### Skeleton enforcement

If a `DepartmentConfig` or `TeamConfig` is listed in the `OrgDefinition` but no
`RoleDefinition` with `is_primary_for_unit=True` and `unit_id=<that_id>` exists,
skeleton enforcement auto-creates a `RoleDefinition` with:

- `role_id = f"auto-head-{unit_id}"`
- `name = f"Head of {unit.name} (Vacant)"`
- `is_vacant = True`
- `is_primary_for_unit = True`
- `unit_id = unit_id`
- `reports_to_role_id` = the role_id of the parent unit's head role (inferred
  from the org tree)
- `is_skeleton = True` (a field added to RoleDefinition, or tracked separately in
  CompiledNode.is_skeleton)

The resulting `CompiledNode` for a skeleton role has `is_skeleton=True`.

If skeleton enforcement cannot determine where to place the auto-created role
(e.g., no parent can be found), raise `CompilationError` with a message describing
which unit is orphaned.

### Error types

```python
class CompilationError(ValueError):
    """Raised when OrgDefinition cannot be compiled into a valid CompiledOrg."""

class NodeNotFoundError(KeyError):
    """Raised by CompiledOrg.get_node() when address is not in the org."""
```

### Financial services test case

The test file must include a test that constructs the financial services example
from PACT thesis Section 7.1 and verifies the address assignments. The exact
structure from the thesis is:

- Board of Directors (D) → BOD Chair role (R)
  - CEO (R, reports to BOD Chair)
    - CFO (primary for Finance Dept)
      - Head of Compliance (primary for Compliance Team)
        - AML Specialist (role in Compliance Team)
      - Head of Trading (primary for Trading Division)
        - Senior Trader (role in Trading Division)
    - COO (primary for Operations Dept)

The test must assert the full address path for at least:

- BOD Chair: the root address
- CEO: child of BOD Chair in the same D unit (or as the R-under-BOD logic works)
- CFO: `D1-R1-D2-R1` (second-level dept, first role)
- Head of Compliance: `D1-R1-D2-R1-D1-R1` (third level — check thesis for exact numbering)

Note: The thesis Section 7.1 example is the specification. Read it before implementing
and derive the expected addresses from the thesis, not from assumptions.

### Test structure

1. Minimal org (single dept, single role) — simplest possible case
2. Two-level org (CEO + 2 direct report dept heads)
3. Three-level org (the financial services example from thesis 7.1)
4. Skeleton enforcement — org with departments but missing head roles
5. get_node lookup — success and NodeNotFoundError cases
6. query_by_prefix — subtree queries matching the financial services example
7. Grammar violation — org that violates D/T/R after skeleton enforcement
8. Orphaned unit — skeleton enforcement cannot find a parent
