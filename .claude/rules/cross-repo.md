# Cross-Repository Operations Rules

## Scope

These rules apply to ALL operations at the terrene/ orchestration level.

## MUST Rules

### 1. Read-Only by Default

Orchestration-level operations MUST NOT modify files in child repositories unless explicitly instructed. This level is for analysis, coordination, and reporting — not development.

### 2. Confirm Destructive Operations

Before any destructive operation across repos (git reset, branch deletion, force push, file deletion), MUST:
1. List exactly what will be affected
2. Get explicit user confirmation
3. Execute one repo at a time

### 3. Preserve Child Repo Governance

Each child repo has its own `.claude/` artifacts and rules. Orchestration MUST NOT override or conflict with child repo governance. When conflicts arise, the child repo's rules win for its own content.

### 4. COC Sync Includes Scripts

When recommending or coordinating COC artifact syncs to child repos, MUST ensure both are synced:
- `.claude/` directory (agents, skills, rules, commands, settings)
- `scripts/` directory (hooks and lib utilities)

Omitting `scripts/hooks/` is the #1 sync failure mode. Hooks are the runtime enforcement layer.

### 5. No Secrets in Reports

When generating cross-repo analysis reports, MUST NOT include actual secret values found during scanning. Report the file and line, not the value.

## MUST NOT Rules

### 1. No Bulk Force Operations

MUST NOT execute force-push, reset --hard, or branch -D across multiple repos in a single command.

### 2. No Cross-Repo Code Changes

MUST NOT modify source code in child repos from this level. If code changes are needed, instruct the user to open Claude Code in the target repo.

### 3. No Direct Pushes

MUST NOT push to child repo remotes from the orchestration level without explicit instruction.
