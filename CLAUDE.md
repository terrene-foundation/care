# Terrene — Foundation Ecosystem Orchestrator

**Terrene** is the orchestration layer for the Terrene Foundation ecosystem. It coordinates content, artifacts, and cross-functional work across all Foundation repositories — from corporate governance to open-source stacks.

No domain work happens here. Terrene manages the ecosystem infrastructure.

## Naming

- **Atelier** — designs the methodology patterns (CC + CO authority)
- **Loom** — weaves codegen artifacts (COC authority)
- **Terrene** (this repo) — orchestrates the Foundation ecosystem (publications, website, open-source stacks)
- Each child repo does its own domain work

## Architecture

```
Terrene (this repo)                 ← Ecosystem orchestrator
├── foundation/                     ← Corporate, strategy, governance, constitution
├── publications/                   ← All white papers, theses, specifications
├── website/                        ← terrene.foundation public site (Astro + Starlight)
├── arbor/                          ← OSS: Knowledge graph framework
├── astra/                          ← OSS: AI platform
├── care/                           ← Planned: Governance framework (not yet a git repo)
├── pact/                           ← OSS: Trust protocol implementation (Python, Kailash SDK)
└── praxis/                         ← OSS: Practice layer
```

## Content Flow

```
foundation/                         publications/
  (strategy, constitution,            (white papers, theses,
   governance, standards)              arXiv submissions)
        │                                   │
        └──────────┐     ┌─────────────────┘
                   ▼     ▼
                 website/
                (terrene.foundation)
                   ▲     ▲
        ┌──────────┘     └─────────────────┐
        │                                   │
atelier/                             loom/
  (CO methodology,                    (COC, Kailash SDK,
   domain applications)                tech stack details)
```

**foundation → website**: Vision, mission, governance, constitution, partnerships, strategy
**publications → website**: CARE, EATP, CO, PACT specs; Constraint Theater thesis; Governance Layer thesis
**atelier → website**: CO methodology, domain applications (COE, COG, COF, COR)
**loom → website**: Kailash SDK architecture, primitives, engine, entrypoints

## Absolute Directives

### 0. Orchestration Only

No domain work. Work here: coordinate content flow, sync artifacts, cross-repo analysis, ecosystem health checks.

### 1. Foundation Independence

The Terrene Foundation is a sovereign, independent entity. No commercial coupling. See `foundation/.claude/rules/terrene-naming.md` for canonical terminology.

### 2. Child Repo Autonomy

Each child repo has its own `.claude/` artifacts, CLAUDE.md, and development workflow. Terrene orchestrates across them but does not override their internal governance.

### 3. Content Accuracy

When coordinating content flow (especially foundation → website and publications → website), source material is authoritative. Website content must accurately reflect source specifications.

## Commands

### Orchestration (this repo)

| Command    | Purpose                                                            |
| ---------- | ------------------------------------------------------------------ |
| `/sync`    | Sync content or artifacts between child repos (read-only analysis) |
| `/analyze` | Cross-repo analysis (content gaps, consistency, dependency health) |

### CO-Tier (inherited from atelier)

| Command       | Purpose                                                  |
| ------------- | -------------------------------------------------------- |
| `/start`      | New session orientation                                  |
| `/ws`         | Workspace status dashboard                               |
| `/checkpoint` | Review progress and learning                             |
| `/journal`    | View, create, or search the project journal              |
| `/wrapup`     | Session notes with context files and oversight checklist |
| `/learn`      | Process observations into instincts                      |
| `/evolve`     | Evolve artifacts based on learned patterns               |

## Repository Responsibilities

| Repo              | Owns                                                     | Feeds Into     |
| ----------------- | -------------------------------------------------------- | -------------- |
| **foundation/**   | Constitution, strategy, governance, partnerships, naming | website        |
| **publications/** | White papers, theses, arXiv submissions, PDFs            | website        |
| **website/**      | Public site (terrene.foundation), developer docs         | —              |
| **arbor/**        | Knowledge graph framework (Python + JS, Kailash SDK)     | website (docs) |
| **astra/**        | AI platform (Python, Kailash SDK)                        | website (docs) |
| **care/**         | CARE governance implementation (planned, not yet a repo) | —              |
| **pact/**         | PACT trust protocol implementation (Python, Kailash SDK) | website (docs) |
| **praxis/**       | Practice layer (Kailash SDK)                             | website (docs) |

## Upstream Dependencies

```
atelier/                            ← CC + CO methodology (Terrene inherits CO patterns)
    ↓
loom/                               ← COC artifacts (OSS stacks inherit via /sync)
    ↓
terrene/                            ← Ecosystem orchestration
    ├── foundation/                 ← CO-managed (COG: CO for Governance)
    ├── publications/               ← CO-managed (COR: CO for Research, no .claude/ yet)
    ├── website/                    ← COC-managed (synced from loom via kailash-coc-claude-py)
    ├── arbor/, astra/, pact/,      ← COC-managed (synced from loom via kailash-coc-claude-py)
    │   praxis/
    └── care/                       ← Planned (not yet initialized as repo)
```

## Rules

### Orchestration Rules (this repo)

| Concern                 | Rule File                          |
| ----------------------- | ---------------------------------- |
| Cross-repo operations   | `rules/cross-repo.md`              |
| Content flow governance | `rules/content-flow.md`            |
| Foundation independence | `rules/foundation-independence.md` |

### CO-Tier Rules (inherited from atelier/loom via foundation)

| Concern                       | Rule File                       |
| ----------------------------- | ------------------------------- |
| Plain-language communication  | `rules/communication.md`        |
| Agent orchestration & reviews | `rules/agents.md`               |
| Git commits, branches, PRs    | `rules/git.md`                  |
| Branch protection             | `rules/branch-protection.md`    |
| Security (secrets in docs)    | `rules/security.md`             |
| No stubs or placeholders      | `rules/no-stubs.md`             |
| Terrene naming & terminology  | `rules/terrene-naming.md`       |
| Autonomous execution          | `rules/autonomous-execution.md` |
| Journal knowledge trail       | `rules/journal.md`              |
| Zero tolerance                | `rules/zero-tolerance.md`       |
| Foundation independence       | `rules/independence.md`         |
| Artifact flow authority chain | `rules/artifact-flow.md`        |

## Agents

### Standards Experts (`agents/standards/`) — CO-tier, inherited

- **co-expert** — CO methodology (8 principles, 5 layers, 6 phases)
- **care-expert** — CARE governance framework (Dual Plane Model, Mirror Thesis)
- **eatp-expert** — Enterprise Agent Trust Protocol (trust lineage, verification gradient)
- **coc-expert** — COC: CO applied to Codegen (5-layer architecture, anti-amnesia)
- **coe-expert** — COE: CO for Education (Mirror Thesis for assessment)
- **cog-expert** — COG: CO for Governance (Foundation methodology)
- **constitution-expert** — Constitution (77 clauses, phased governance)

### Analysis & Review (inherited)

- **deep-analyst** — Failure analysis, complexity assessment
- **requirements-analyst** — Requirements breakdown, systematic analysis
- **intermediate-reviewer** — Document and content review
- **security-reviewer** — Security audit for sensitive content
- **gold-standards-validator** — Naming, licensing, terminology compliance
- **open-source-strategist** — Licensing, positioning, community strategy
- **publication-expert** — Academic publication preparation, venue selection
- **governance-layer-expert** (`standards/`) — Governance Layer Thesis, positioning

### Orchestration (this repo)

- **ecosystem-coordinator** — Cross-repo orchestration, content flow, dependency tracking
- **content-flow-coordinator** — Website content sourcing from foundation, publications, atelier, loom
- **oss-coordinator** — OSS stack health, COC sync status, release coordination

### Management (`agents/management/`)

- **todo-manager** — Ecosystem-level work item tracking
- **gh-manager** — GitHub issue/project management across terrene-foundation org

## Skills

### CO-Tier (inherited)

- `skills/co-reference/` — CO methodology reference (8 principles, 5 layers, domain apps)
- `skills/26-eatp-reference/` — EATP technical reference (5 elements, verification gradient)
- `skills/27-care-reference/` — CARE framework reference (Dual Plane, Mirror Thesis)
- `skills/29-constitution-reference/` — Constitution reference (77 clauses, governance phases)
- `skills/29-pact/` — PACT governance framework (D/T/R grammar, operating envelopes)

## Guides

### Orchestration (this repo)

- `guides/orchestration/content-flow.md` — Content flow map and verification process
- `guides/orchestration/ecosystem-structure.md` — Repository hierarchy and governance models

### Management (`agents/management/`) — inherited

- **git-release-specialist** — Git workflows, version management

## Child Repo Git Remotes

| Repo          | Remote                                                   |
| ------------- | -------------------------------------------------------- |
| foundation/   | `git@github.com:terrene-foundation/foundation.git`       |
| publications/ | `https://github.com/terrene-foundation/publications.git` |
| website/      | `git@github.com:terrene-foundation/terrene-website.git`  |
| arbor/        | `https://github.com/terrene-foundation/arbor.git`        |
| astra/        | `git@github.com:terrene-foundation/astra.git`            |
| pact/         | `git@github.com:terrene-foundation/pact.git`             |
| praxis/       | `git@github.com:terrene-foundation/praxis.git`           |
