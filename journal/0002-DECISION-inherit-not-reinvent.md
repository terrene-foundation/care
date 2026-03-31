---
type: DECISION
date: 2026-03-31
created_at: 2026-03-31T17:30:00Z
author: human
session_turn: 12
project: terrene
topic: CO-tier artifacts must be inherited from upstream, never written from scratch
phase: execute
tags: [artifact-flow, co-tier, sync, atelier, loom]
---

## Decision

All CO-tier artifacts (commands, rules, agents, skills, guides) must be copied from their authoritative sources — atelier for commands, loom for rules, foundation for agents/skills. Custom orchestration artifacts are additive, never replacements.

## Alternatives Considered

1. **Write custom versions** — attempted first, failed red-team (broken reference chains, missing agent dependencies, incompatible with hooks/learning system).
2. **Full COC sync** — copy everything from kailash-coc-claude-py template. Rejected: orchestrator is CO-tier, not COC-tier. COC agents (tdd-implementer, framework-advisor) don't apply.

## Rationale

User caught the mistake during red-team: custom commands lacked the proven workspace resolution, journal protocol, oversight checklists, and hook integration of the atelier originals. The /wrapup command failed as "Unknown skill" because the custom version wasn't properly structured. Inheriting from upstream ensures compatibility with the hooks and learning system.

## Consequences

- 4 commands replaced with atelier originals (wrapup, ws, checkpoint, journal)
- 3 commands added from loom (start, learn, evolve)
- 6 rules added from loom CO-tier
- 10+ agents added to satisfy reference chains in copied rules
- COC-scope guides (co-setup, model-optimization) removed — they describe 33-agent ecosystems that don't apply to orchestrator

## For Discussion

- Should terrene have a `/sync-from-upstream` command that automates pulling CO-tier artifacts from atelier/loom, rather than manual cp?
- If foundation's agents diverge from loom's versions (because foundation does its own /codify), which source should terrene prefer — and does the answer change depending on the artifact type?
