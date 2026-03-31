---
name: sync
description: "Cross-repo content sync analysis. Shows status, gaps, and COC currency."
---

# /sync — Cross-Repo Content Sync

Coordinate content synchronization between Terrene Foundation repositories.

## Usage

```
/sync                          # Show sync status for all repos
/sync website                  # Check what website needs from sources
/sync coc                      # Check COC artifact currency across OSS stacks
/sync foundation → website     # Audit foundation content flow to website
/sync publications → website   # Audit publications content flow to website
```

## Process

### 1. Status Check

Read `sync-manifest.yaml` for the authoritative content flow map. For each target, check:

- Source content freshness (git log dates)
- Target content freshness
- Known discrepancies

### 2. Gap Analysis

For content flow syncs (e.g., foundation → website):

- List source content that has no corresponding target
- List target content that may be outdated
- Verify terminology and naming consistency

### 3. COC Sync

For COC artifact syncs:

- Read `.claude/VERSION` in each OSS repo
- Compare `upstream.version` against loom's template
- Report which repos need `/sync` run locally

### 4. Report

Output a structured report:

- Current / Up to date
- Needs update (with specific source → target mappings)
- Missing (content exists in source but not target)

## MUST Rules

1. **Read-only** — This command analyzes and reports. It MUST NOT modify files in child repos.
2. **COC sync includes scripts/** — When reporting COC sync status, MUST check for both `.claude/` and `scripts/hooks/` in each target. Omitting scripts/hooks/ is the #1 sync failure mode.
3. **Verify sources exist** — Before reporting a gap, MUST verify the source directory/file actually exists (don't assume paths from the manifest are still valid).
4. **Preserve target-only files** — When recommending sync actions, MUST note that sync is additive — target-only files are never deleted.
5. **Child repo sovereignty** — To actually sync COC artifacts, instruct the user to run `/sync` inside the target repo. To update website content, instruct opening a session in website/.
6. **Terminology accuracy** — All output MUST use Terrene naming conventions (Terrene Foundation, not OCEAN; CC BY 4.0 for specs; Apache 2.0 for code).
