---
name: todo-manager
description: "Project task tracking for ecosystem-level work items."
---

# Todo Manager

Track and manage ecosystem-level work items across the Terrene Foundation repositories.

## Scope

Work items that span multiple child repos or orchestration-level concerns. Child repos manage their own todos internally.

## Todo Format

Todos live in `workspaces/<project>/todos/active/` (when workspaces exist) or are tracked via Claude Code tasks for the current session.

## Operations

- **List**: Show all active work items
- **Create**: Add a new work item with priority and scope
- **Complete**: Move to `todos/completed/` with resolution notes
- **Defer**: Move to `todos/deferred/` with reason

## Ecosystem-Level Work Items

Examples of work that belongs at the orchestration level:

- Content sync audits (foundation → website)
- COC artifact currency checks across OSS stacks
- Cross-repo naming/terminology consistency
- Release coordination across multiple repos
