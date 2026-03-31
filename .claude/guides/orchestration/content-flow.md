# Content Flow Guide

## Overview

The Terrene Foundation ecosystem has a defined content flow between repositories. Content originates in source repos and flows to the website for public consumption.

## Flow Diagram

```
foundation/ (source of truth for governance, strategy, naming)
    │
    ├── docs/00-anchor/     → website: about/
    ├── docs/01-strategy/   → website: about/
    ├── docs/02-standards/  → website: standards/
    ├── docs/04-community/  → website: governance/
    ├── docs/06-operations/ → website: governance/
    └── docs/08-research/   → website: research/

publications/ (source of truth for white papers, theses)
    │
    ├── *.md, *.pdf         → website: standards/, philosophy/, research/
    └── PDF links           → website (stable GitHub URLs)

atelier/ (external: CO methodology)
    │
    └── CO descriptions     → website: standards/co/

loom/ (external: COC, Kailash SDK)
    │
    └── SDK architecture    → website: developers/
```

## Verification Process

1. Read `sync-manifest.yaml` for authoritative mappings
2. For each website section, identify the primary source
3. Verify the source content exists and is current
4. Check that terminology matches (Terrene naming rules)
5. Flag any drift between source and website

## Key Principle

Content is **transformed** for the website, not copied. The sync process verifies accuracy and currency, not textual identity.
