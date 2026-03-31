---
description: Check if atelier or loom have released new versions of CO/COC artifacts
---

# /check-upstream

Check upstream artifact currency for the Terrene ecosystem orchestrator.

## What This Does

Reads `.claude/VERSION` and compares the tracked upstream versions (atelier for CO, loom for COC) against their actual current versions on GitHub.

## Process

1. Read `.claude/VERSION` to get the `upstream[]` array
2. For each upstream entry:
   - Fetch the remote VERSION file from `version_url` (3-second timeout)
   - Compare `upstream[].version` (what we last synced) against `remote.version` (actual current)
   - If versions differ, extract changelog entries newer than what we track
3. Report per-upstream status with actionable next steps

## Usage

```
/check-upstream           # Check all upstreams (atelier + loom)
/check-upstream atelier   # Check CO tier only
/check-upstream loom      # Check COC tier only
```

## Expected Output

```
[UPSTREAM] Checking CO/COC artifact currency...

[UPSTREAM] atelier v1.0.0 — current (CO tier: hooks, rules, commands, learning)
[UPSTREAM] loom v1.1.0 → v1.2.0 available (COC tier: agents, skills, rules, variants)
  Changes:
    v1.2.0 (2026-03-31): Ruby variant support, nested department rules
  Next steps:
    1. Review changes in ~/repos/loom/
    2. Run /sync to update terrene orchestrator artifacts
    3. Distribute to child repos via their own /sync commands
```

## Rules

- **Read-only**: This command reports status. It does not modify any files.
- **Offline-safe**: Network failures timeout in 3 seconds. Offline status is reported, not treated as error.
- **Both tiers checked**: Always check atelier (CO) and loom (COC) unless a specific upstream is requested.
- **Actionable output**: Every "update-available" result must include what changed and what to do next.

## After Running

If updates are available:

1. Review the changelog to understand what changed upstream
2. Decide whether to update (not all upstream changes require terrene sync)
3. If updating: manually sync the changed artifacts from atelier/loom into terrene
4. Update `.claude/VERSION` upstream version entries to reflect the new tracked versions
5. For COC changes that affect child repos: coordinate child repo updates via their own /sync commands

## Technical Details

Uses `scripts/hooks/lib/version-utils.js` functions:

- `readLocalVersion()` reads `.claude/VERSION`
- `fetchUpstreamVersion()` fetches remote VERSION via curl (3s timeout)
- `checkMultipleUpstreams()` compares all upstream entries
