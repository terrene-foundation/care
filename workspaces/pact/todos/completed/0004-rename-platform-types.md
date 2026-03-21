# TODO-0004: Rename Platform Types

Status: pending
Priority: high
Dependencies: []
Milestone: M0

## What

Rename three types throughout the codebase to remove the "Platform" prefix which
implies the old CARE Platform product name rather than the PACT framework:

- `PlatformConfig` → `PactConfig`
- `PlatformSession` → `PactSession`
- `PlatformAPI` → `PactAPI`

These renames apply to class definitions, all imports, all test usages, and all
string references (docstrings, comments, error messages that name the class).

Grep confirms the types appear in 13 files in `src/`. The test suite also references
them in test files across multiple directories.

## Where

Definitions:

- `src/pact/build/config/schema.py` — `PlatformConfig` class (line ~425)
- `src/pact/use/execution/session.py` — `PlatformSession` class
- `src/pact/use/api/server.py` — likely home of `PlatformAPI` or the server class

Files with imports to update (confirmed by grep — 13 files in src/):

- `src/pact/build/verticals/dm_team.py` (will move to examples in 0001, but still
  needs the rename applied at its destination)
- `src/pact/build/cli/__init__.py`
- `src/pact/build/org/builder.py`
- `src/pact/build/config/loader.py`
- `src/pact/build/config/__init__.py`
- `src/pact/build/bootstrap.py`
- `src/pact/use/api/endpoints.py`
- `src/pact/use/api/__init__.py`
- `src/pact/use/api/server.py`
- `src/pact/use/execution/__init__.py`
- `src/pact/use/execution/session.py`
- `src/pact/__init__.py`

Test files — run the following grep to get the complete list before starting:

```bash
grep -rln 'PlatformConfig\|PlatformSession\|PlatformAPI' tests/
```

## Evidence

- `grep -r 'PlatformConfig\|PlatformSession\|PlatformAPI' src/ tests/` returns 0 hits
- `from pact.build.config.schema import PactConfig` works
- `from pact.use.execution.session import PactSession` works
- `pytest -x` passes (full test suite)
- No `PlatformConfig`, `PlatformSession`, or `PlatformAPI` in any file under `src/`
  or `tests/`

## Details

### Rename mapping

| Old name          | New name      | Defined in                                         |
| ----------------- | ------------- | -------------------------------------------------- |
| `PlatformConfig`  | `PactConfig`  | `src/pact/build/config/schema.py`                  |
| `PlatformSession` | `PactSession` | `src/pact/use/execution/session.py`                |
| `PlatformAPI`     | `PactAPI`     | `src/pact/use/api/server.py` (or wherever defined) |

### Backward compatibility aliases

To avoid breaking any external code that might already reference the old names
(unlikely at this early stage, but good practice), add module-level aliases
in the definition files after renaming:

In `schema.py`:

```python
PactConfig = PactConfig  # New canonical name
PlatformConfig = PactConfig  # Deprecated alias — remove in v1.0
```

This allows a clean cut without immediate breakage. The alias should include
a deprecation warning via `warnings.warn` if warranted, but given this is
pre-release, a plain alias is sufficient.

### Scope of change

- Class name in the `class` statement
- All `import` and `from ... import` statements referencing the old name
- All type annotations: `def foo(config: PlatformConfig)` → `def foo(config: PactConfig)`
- All docstrings and comments that name the class (e.g., "Creates a PlatformConfig
  from..." → "Creates a PactConfig from...")
- All string literals in error messages: `f"PlatformConfig requires..."` → `f"PactConfig requires..."`

### What must NOT change

- The `DepartmentConfig`, `TeamConfig`, `AgentConfig`, `WorkspaceConfig` names — these
  are already correct generic names
- The `GenesisConfig` name — already correct
- Any Pydantic `model_config` attribute (that is a Pydantic internal, not a class name)
- The session state enum `SessionState` — already a good name

### Ordering note

This task is independent of 0001, but if 0001 runs first, the verticals file will have
moved to `src/pact/examples/foundation/` before this rename runs. Either order works.
Run the rename across the new location if 0001 has already been applied.
