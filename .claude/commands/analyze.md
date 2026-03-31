---
name: analyze
description: "Ecosystem analysis for content gaps, consistency, and health."
---

# /analyze — Cross-Repo Analysis

Analyze the Terrene Foundation ecosystem for content gaps, consistency issues, and health.

## Usage

```
/analyze                       # Full ecosystem analysis
/analyze content               # Content flow analysis (sources → website)
/analyze coc                   # COC artifact currency across OSS stacks
/analyze consistency           # Naming, licensing, terminology consistency
/analyze health                # Git status, CI, dependency health
```

## Full Analysis Covers

### 1. Content Flow

- Does the website reflect current foundation/ content?
- Are all published specifications represented on the site?
- Are publication links (PDFs) working and current?

### 2. COC Currency

- Which OSS repos are behind on COC artifacts?
- Are SDK dependencies up to date?

### 3. Naming & Terminology

- "Terrene Foundation" (not OCEAN) used consistently
- License references accurate (CC BY 4.0 for specs, Apache 2.0 for code)
- Standard names match canonical definitions

### 4. Ecosystem Health

- All repos on main branch, clean working tree
- No repos significantly behind remote
- No stale branches

## Output

Structured report with:

- Summary (how many issues found, by category)
- Details (specific file paths, recommended actions)
- Priority (critical / warning / info)
