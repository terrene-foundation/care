# TODO-0005: Fix Remaining CARE Platform References

Status: pending
Priority: high
Dependencies: []
Milestone: M0

## What

Remove all remaining "CARE Platform" and "care-platform" references from files outside
the Python source tree. The repository was previously named care-platform; this task
completes the rename to PACT. Three areas require attention:

1. `apps/web/` — TypeScript files that import from or reference a `care-platform` module
   path, and type files that may still use the old identity (grep found 34 files)
2. `.env.example` — Header comment reads "CARE Platform - Environment Configuration"
3. `mkdocs.yml` — `site_name` already reads `PACT` (confirmed), but check for
   `site_description` or nav labels that reference "CARE Platform"

## Where

Frontend (34 files confirmed by grep):
The 34 files in `apps/web/` that contain `care-platform` are using it as a URL path
segment or API route prefix. Each file needs the string `care-platform` replaced with
`pact` in route paths and API endpoints. The specific files span:

- `apps/web/components/` — 15+ component files
- `apps/web/app/` — 10+ page files
- `apps/web/lib/` — API client files (`api.ts`, `use-api.ts`)
- `apps/web/__tests__/` — test file

Config files:

- `.env.example` line 2: `# CARE Platform - Environment Configuration Template`
  → `# PACT - Environment Configuration Template`
- `mkdocs.yml` — verify no remaining CARE Platform references in nav or description

## Evidence

- `grep -ri 'CARE Platform' apps/ .env.example mkdocs.yml` returns 0 hits
- `grep -ri 'care-platform' apps/ .env.example mkdocs.yml` returns 0 hits
- Frontend app builds without errors: `cd apps/web && npm run build` exits 0
- No TypeScript type errors on renamed paths

## Details

### Frontend approach

The `care-platform` string in the frontend is almost certainly used in two ways:

**API route prefixes** — if the backend serves routes under `/care-platform/...`,
those become `/pact/...`. Check `apps/web/lib/api.ts` and `apps/web/lib/use-api.ts`
for the base URL or API prefix constant. Change once at the source and all callers
pick it up automatically.

**Type file references** — `apps/web/tsconfig.tsbuildinfo` contains `care-platform`
but this is a build cache file; it regenerates on next build. Do not edit it manually —
running `npm run build` after the other changes regenerates it correctly.

**TypeScript path aliases** — check `apps/web/tsconfig.json` for any path alias
like `"care-platform/*": [...]`. If present, rename to `"pact/*"` and update any
imports that use the alias.

### Systematic approach

1. Run `grep -rn 'care-platform' apps/web/` (excluding `node_modules/` and
   `tsconfig.tsbuildinfo`) to get the exact line count and locations
2. For each occurrence, determine whether it is:
   - A string literal (URL/route) — update to use `pact`
   - An import path — update to new module name
   - A TypeScript type reference — update the type name
3. After changes: `cd apps/web && npm run build` to confirm no TS errors
4. After build: re-run grep to confirm 0 remaining hits

### Exclude from this task

- `apps/web/node_modules/` — third-party packages, not our code
- `apps/web/tsconfig.tsbuildinfo` — generated build cache, will update automatically
- Any URLs pointing to external documentation that happened to be hosted under a
  care-platform domain — those are documentation issues, not code issues

### .env.example change

Single-line change only:

```
# CARE Platform - Environment Configuration Template
```

becomes:

```
# PACT - Environment Configuration Template
```

Keep the rest of the file unchanged.

### mkdocs.yml

The `site_name` already reads `PACT`. Scan for any nav entries, description text,
or custom HTML in `docs/` that still says "CARE Platform". If found, update to "PACT".
The docs site is low-traffic at this stage so this is a quick scan rather than a
comprehensive audit.
