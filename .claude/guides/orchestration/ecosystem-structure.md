# Ecosystem Structure Guide

## Repository Hierarchy

```
~/repos/
├── atelier/         ← CC + CO authority (methodology patterns)
├── loom/            ← COC authority (codegen artifacts, variant system)
└── terrene/         ← Foundation ecosystem orchestrator
    ├── foundation/  ← COG: Corporate, strategy, governance, constitution
    ├── publications/← COR: White papers, theses, arXiv submissions
    ├── website/     ← COC: terrene.foundation public site (Astro + Starlight)
    ├── arbor/       ← COC: Knowledge graph framework (Python + JS)
    ├── astra/       ← COC: AI platform (Python)
    ├── care/        ← Planned: CARE governance implementation
    ├── pact/        ← COC: Trust protocol implementation (Python)
    └── praxis/      ← COC: Practice layer (Python)
```

## Governance Models

| Model | Applies To                               | Artifacts Source            | CO Domain         |
| ----- | ---------------------------------------- | --------------------------- | ----------------- |
| COG   | foundation/                              | Own .claude/ (hand-crafted) | CO for Governance |
| COR   | publications/                            | Not yet instrumented        | CO for Research   |
| COC   | website/, arbor/, astra/, pact/, praxis/ | loom/kailash-coc-claude-py  | CO for Codegen    |

## Upstream Dependencies

- **Atelier → Terrene**: CO methodology, CC patterns (hooks inherited)
- **Loom → OSS stacks**: COC artifacts synced to arbor, astra, pact, praxis, website
- **Foundation → Website**: Content flow (governance, strategy, naming)
- **Publications → Website**: Content flow (specs, theses, PDFs)

## The Orchestrator's Role

Terrene/ is read-only by default. It:

- Analyzes ecosystem health
- Coordinates content flow
- Tracks COC sync currency
- Reports issues and recommends actions

It does NOT modify child repo files directly.
