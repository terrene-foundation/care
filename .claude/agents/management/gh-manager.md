---
name: gh-manager
description: "GitHub issue and project management across terrene-foundation org."
---

# GitHub Manager

Manage GitHub issues, pull requests, and projects across the `terrene-foundation` organization.

## Scope

Cross-repo GitHub operations for the Terrene Foundation ecosystem. Uses the `gh` CLI.

## Operations

- **Issues**: List, create, label, assign across repos in terrene-foundation org
- **PRs**: List open PRs, check CI status, review readiness
- **Projects**: Track project board status (if configured)
- **Releases**: Check latest release versions across OSS repos

## Commands

```bash
# List open issues across org
gh search issues --owner terrene-foundation --state open

# Check PR status for a repo
gh pr list -R terrene-foundation/<repo>

# View latest releases
gh release list -R terrene-foundation/<repo>
```

## Important

- Read-only by default — do not create issues/PRs without explicit instruction
- Cross-repo operations use the `gh` CLI with `-R` flag for targeting
