# TODO-0001: Extract Verticals to Examples

Status: pending
Priority: critical
Dependencies: []
Milestone: M0

## What

Move `src/pact/build/verticals/` to `src/pact/examples/foundation/`. The verticals package
contains domain-specific code — DM team definitions, foundation org builder, DM prompts,
and DM runner — that belongs in examples, not in the reusable framework layer. After this
move, `src/pact/build/` must contain zero domain vocabulary (no references to DM teams,
foundation-specific orgs, or media vertical concepts).

The builtin templates in `src/pact/build/templates/builtin/` (11 YAML files: training,
website, devrel, partnerships, standards, media, community, finance, certification,
governance, legal) are also domain-specific team templates for a foundation org. They
belong in `src/pact/examples/foundation/templates/` alongside the foundation vertical code.

## Where

Source moves:

- `src/pact/build/verticals/` → `src/pact/examples/foundation/`
  - `__init__.py` (update docstring, remove "Verticals" language)
  - `dm_team.py` → kept as-is, new path
  - `dm_runner.py` → kept as-is, new path
  - `dm_prompts.py` → kept as-is, new path
  - `foundation.py` → kept as-is, new path
- `src/pact/build/templates/builtin/` → `src/pact/examples/foundation/templates/`
  - All 11 YAML files
- `src/pact/build/templates/registry.py` → `src/pact/examples/foundation/templates/registry.py`
  - Update path references inside registry.py if it uses **file** to locate YAML
- `src/pact/build/templates/__init__.py` → `src/pact/examples/foundation/templates/__init__.py`

New files to create:

- `src/pact/examples/__init__.py` — package marker, no imports
- `src/pact/examples/foundation/__init__.py` — replaces old verticals **init**.py

Test import updates:

- `tests/unit/verticals/` — all test files stay in place; update imports from
  `pact.build.verticals` to `pact.examples.foundation`
- `tests/unit/templates/` — update imports from
  `pact.build.templates` to `pact.examples.foundation.templates`

Other files that import from verticals or templates (grep confirms these exist):

- `src/pact/build/verticals/dm_team.py` imports `PlatformConfig` from
  `pact.build.config.schema` — no change needed to that import target
- Any file in `src/pact/build/` that imports from `pact.build.verticals` or
  `pact.build.templates` must have the import updated to the new path

After the move, `src/pact/build/templates/` directory is removed entirely (empty).
`src/pact/build/verticals/` directory is removed entirely (empty).

## Evidence

- `grep -r 'pact.build.verticals\|from pact.build.verticals' src/ tests/` returns 0 hits
- `grep -r 'pact.build.templates\|from pact.build.templates' src/ tests/` returns 0 hits
- `grep -r 'from pact.examples.foundation' tests/unit/verticals/` returns hits for all
  test files that previously imported from verticals
- `from pact.examples.foundation import DmTeam` works in Python
- `from pact.examples.foundation.templates import registry` works in Python
- `pytest tests/unit/verticals/ tests/unit/templates/ -x` passes (all tests pass)
- The directory `src/pact/build/verticals/` does not exist
- The directory `src/pact/build/templates/` does not exist

## Details

### Step sequence

1. Create `src/pact/examples/__init__.py` (empty package marker)
2. `mkdir -p src/pact/examples/foundation/templates`
3. Copy (then delete) all files from `src/pact/build/verticals/` into
   `src/pact/examples/foundation/`
4. Copy (then delete) `src/pact/build/templates/registry.py`,
   `src/pact/build/templates/__init__.py`, and all `builtin/*.yaml` files into
   `src/pact/examples/foundation/templates/`
5. Update `registry.py` if it uses a relative `__file__` path to locate the builtin
   YAML directory — the relative path changes from `builtin/` to `builtin/` (same
   subdirectory name, but now under `examples/foundation/templates/`)
6. Grep all files in `src/` and `tests/` for `pact.build.verticals` and
   `pact.build.templates`, update each import to the new path
7. Remove the now-empty `src/pact/build/verticals/` and
   `src/pact/build/templates/` directories
8. Run `pytest` to confirm all tests pass

### What must NOT change

- No changes to any module inside `src/pact/build/` other than removing the verticals
  and templates subdirectories
- No changes to `src/pact/trust/` or `src/pact/use/`
- `tests/unit/verticals/` stays at its current location — only the import lines change
- No test logic changes, only import path updates

### Boundary verification

After this task, the following command must return no results:

```
grep -rn 'DmTeam\|dm_team\|dm_runner\|dm_prompts\|foundation_org\|FoundationOrg' \
  src/pact/build/ src/pact/trust/ src/pact/use/
```

This confirms the boundary: domain vocabulary exists only in `src/pact/examples/`.
