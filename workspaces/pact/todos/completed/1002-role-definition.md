# TODO-1002: RoleDefinition as First-Class Node

Status: pending
Priority: critical
Dependencies: []
Milestone: M1

## What

Add `RoleDefinition` as a new dataclass to `src/pact/build/config/schema.py` and add
an optional `roles` field to `OrgDefinition` in `src/pact/build/org/builder.py`.

This is the schema layer for M1 — before `compile_org` can assign addresses (TODO-1003),
the org definition must be able to express which roles exist and how they relate to each
other via `reports_to_role_id`. Currently `OrgDefinition` models teams and agents but has
no first-class concept of roles as nodes in the org hierarchy.

`RoleDefinition` is a pure data model with no behavior. It is a `@dataclass`, not a
Pydantic model, consistent with EATP SDK conventions. It serializes via `to_dict()` /
`from_dict()`.

## Where

- `src/pact/build/config/schema.py` — add `RoleDefinition` dataclass
- `src/pact/build/org/builder.py` — add `roles: list[RoleDefinition]` to `OrgDefinition`
- `tests/unit/org/test_builder.py` — extend with RoleDefinition tests (existing file)

Note: `OrgDefinition` lives in `src/pact/build/org/builder.py`, not in `schema.py`.
`RoleDefinition` is added to `schema.py` because it is a configuration schema type
(like `AgentConfig`, `TeamConfig`) that is used as input to the builder.

## Evidence

- `from pact.build.config.schema import RoleDefinition` works
- `RoleDefinition(role_id="cfo", name="Chief Financial Officer", reports_to_role_id="ceo",
 is_primary_for_unit=True, unit_id="finance-dept")` constructs without error
- `RoleDefinition` with `is_vacant=True` and no `agent_id` constructs without error
- `OrgDefinition` with `roles=[]` (default) constructs — existing tests still pass
- `OrgDefinition` with a populated `roles` list constructs
- `RoleDefinition.to_dict()` returns a dict with all fields
- `RoleDefinition.from_dict(d)` round-trips correctly
- `pytest tests/unit/org/test_builder.py -x` passes (existing tests unbroken)
- New tests for `RoleDefinition` pass

## Details

### RoleDefinition fields

```python
@dataclass
class RoleDefinition:
    """A role node in the organizational hierarchy.

    Roles are the accountability atoms of PACT: every Department and Team
    must have exactly one head role that occupies it, and every action taken
    by an agent is attributed to the role that agent occupies.
    """

    role_id: str
    # Unique identifier within the org, e.g. "cfo", "ceo", "team-lead-equities"

    name: str
    # Human-readable role title, e.g. "Chief Financial Officer"

    reports_to_role_id: str | None = None
    # role_id of the role this role directly reports to.
    # None means this is a root role (e.g., the BOD chair or CEO).
    # Multiple roles may report to the same parent — that is the tree structure.

    is_primary_for_unit: bool = False
    # When True, this role is the head role that "fills" a D or T unit.
    # D/T/R grammar requires exactly one primary role per unit.
    # The compile_org function uses this flag to assign addresses.

    unit_id: str | None = None
    # The department_id or team_id that this role heads (when is_primary_for_unit=True).
    # None for non-head roles.

    is_vacant: bool = False
    # True when no agent is currently assigned to this role.
    # The address is still assigned; the role still exists in the hierarchy.
    # Vacancy rules (thesis Section 5.5) apply when is_vacant=True.

    is_external: bool = False
    # True for roles held by external parties (contractors, board observers)
    # who operate under different clearance and envelope rules.

    agent_id: str | None = None
    # The agent currently occupying this role.
    # None when is_vacant=True or when the role is held by a human.

    address: str | None = None
    # The computed positional address (e.g., "D1-R1-D2-R3").
    # None before compile_org runs. compile_org populates this field.
    # Stored as a string here; the Address value type is in pact.governance.

    def to_dict(self) -> dict[str, Any]: ...
    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RoleDefinition": ...
```

### OrgDefinition extension

Add to the existing `OrgDefinition` class (or `@dataclass` — check the actual type):

```python
roles: list[RoleDefinition] = field(default_factory=list)
```

This field is optional with an empty default so that all existing `OrgDefinition`
usages (which don't provide `roles`) continue to work without modification.

The `roles` list contains all `RoleDefinition` instances for the org in no particular
order. `compile_org` (TODO-1003) is responsible for building the tree from
`reports_to_role_id` links and assigning addresses.

### Validation

Add a validator to `OrgDefinition` (or a method called from `__post_init__`) that
checks:

1. No duplicate `role_id` values across the `roles` list
2. Every `reports_to_role_id` references an existing `role_id` in the same list
   (except `None` which is valid for root roles)
3. At most one root role (role with `reports_to_role_id=None`) per org — this is the
   BOD chair or equivalent

These validations run only when `roles` is non-empty, so they don't affect existing
tests that construct `OrgDefinition` without a `roles` argument.

### to_dict / from_dict

Standard EATP SDK convention:

- `to_dict()` serializes all fields, with `None` values included as `None` (not omitted)
- `from_dict(d)` accepts the dict produced by `to_dict()` and reconstructs the object
- Boolean fields serialize as Python `bool`, not as 0/1

### Scope constraints

This task does NOT:

- Assign addresses to roles (that is TODO-1003)
- Implement any grammar validation on the role tree (that is TODO-1003)
- Change any existing schema class (`PlatformConfig`, `AgentConfig`, etc.)
- Depend on `pact.governance` in any way — `RoleDefinition` is a pure data model
  in `pact.build.config.schema`
