---
type: DECISION
date: 2026-03-31
created_at: 2026-03-31T16:20:00Z
author: co-authored
session_turn: 3
project: terrene
topic: Establish terrene/ as ecosystem orchestrator modeled on atelier/loom pattern
phase: execute
tags: [architecture, orchestrator, atelier, loom, co-tier]
---

## Decision

Terrene/ becomes the Foundation ecosystem orchestrator — a git repo containing `.claude/`, `scripts/hooks/`, `CLAUDE.md`, and `.gitignore` (excluding child repos). Modeled on how atelier/ orchestrates CO domains and loom/ orchestrates COC artifacts.

## Alternatives Considered

1. **No orchestrator** — keep terrene/ as a plain folder. Rejected: no session continuity, no hooks, no commands across the ecosystem.
2. **Use ~/repos level** — orchestrate from the root. Rejected: root covers ALL repos (dev/, tpc/, etc.), not just Foundation.
3. **Merge into foundation/** — make foundation/ the orchestrator. Rejected: foundation/ is COG domain work, orchestration is cross-cutting.

## Rationale

The atelier/loom pattern is proven: a git-tracked orchestrator with `.claude/` artifacts, hooks for session management, and commands for cross-repo work. Terrene needed the same treatment — it manages 7 git repos + 1 planned repo across corporate governance, publications, website, and 5 OSS stacks.

## Consequences

- Terrene/ now has its own git history, independent of child repos
- CO-tier artifacts inherited from atelier/loom (not written from scratch)
- Child repos remain autonomous — orchestrator is read-only by default
- GitHub repo renamed: terrene-foundation/terrene → terrene-foundation/foundation

## For Discussion

- If the Foundation adds more OSS stacks (e.g., a CDI implementation), what's the process for adding them to the sync-manifest — and does the current manifest structure scale beyond 10 repos?
- If atelier updates its CO-tier commands (e.g., wrapup.md gets a new section), how does terrene detect it's behind? The VERSION file tracks loom but not atelier's command versions specifically.
