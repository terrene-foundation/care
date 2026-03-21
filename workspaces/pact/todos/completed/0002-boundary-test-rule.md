# TODO-0002: Boundary Test Rule

Status: pending
Priority: critical
Dependencies: []
Milestone: M0

## What

Create `.claude/rules/boundary-test.md` that enforces the framework/domain boundary.
The core rule: `src/pact/` (excluding `src/pact/examples/`) must contain zero
domain-specific vocabulary. This rule makes the boundary machine-checkable and gives
future implementers explicit guidance on what is forbidden inside the framework layer.

Also update `CLAUDE.md` rules index to reference the new rule file.

## Where

- `.claude/rules/boundary-test.md` — new rule file
- `CLAUDE.md` — add one row to the Rules Index table

## Evidence

- `.claude/rules/boundary-test.md` exists
- `CLAUDE.md` Rules Index table contains a row for `boundary-test.md`
- The rule file lists all forbidden domain terms by category
- The rule file specifies the exact grep command to run as a boundary check

## Details

### Rule file content

The rule file must specify:

**Scope**: Files matching `src/pact/**/*.py` excluding `src/pact/examples/**`

**What is forbidden** (these terms must not appear in `src/pact/build/`,
`src/pact/trust/`, or `src/pact/use/`):

Organization-specific terms:

- `DmTeam`, `dm_team`, `digital_media`, `DigitalMedia`
- `FoundationOrg`, `foundation_org`, `TerreneFdn`, `terrene_foundation`
- `dm_runner`, `dm_prompts`, `DmRunner`

Vertical/industry terms:

- `media_team`, `MediaTeam`, `editorial`, `Editorial`
- `content_creator`, `ContentCreator`
- Any proper noun referring to a specific organization's department

**What IS permitted** in the framework layer:

- Generic PACT architecture terms: `Department`, `Team`, `Role`, `Address`,
  `OrgDefinition`, `RoleDefinition`
- EATP terms: `genesis`, `delegation`, `attestation`, `constraint`, `envelope`
- Generic governance terms: `clearance`, `barrier`, `posture`, `verification`

**Enforcement command** (include verbatim in the rule file):

```bash
grep -rn \
  'DmTeam\|dm_team\|DigitalMedia\|digital_media\|FoundationOrg\|foundation_org\|dm_runner\|dm_prompts' \
  src/pact/build/ src/pact/trust/ src/pact/use/ \
  && echo "BOUNDARY VIOLATION" || echo "Boundary clean"
```

**When to run**: Before any commit that modifies files under `src/pact/build/`,
`src/pact/trust/`, or `src/pact/use/`.

### CLAUDE.md update

Add to the Rules Index table:

| Framework boundary enforcement | `rules/boundary-test.md` | `src/pact/build/**`, `src/pact/trust/**`, `src/pact/use/**` |

Place it near the existing "Foundation independence" row since they are related
governance concerns.

### Rationale to include in the rule file

The PACT framework is domain-agnostic governance infrastructure. If domain
vocabulary accumulates in the framework layer, it becomes impossible for a
university, a hospital, or a financial firm to use PACT without importing
Terrene Foundation-specific concepts. The `src/pact/examples/foundation/`
package is the correct home for all Foundation-specific code; the framework
layer must remain generic.
