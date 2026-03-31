# CARE — Assessment & Onboarding Kit

**CARE** (Collaborative Autonomous Reflective Enterprise) Assessment & Onboarding Kit — a voice-first, AI-guided tool that helps non-technical leaders assess their organization's AI governance posture and generates PACT-compatible configuration.

CARE is the pre-operational layer in the Terrene Foundation governance stack: **discover** (CARE) → **enforce** (PACT) → **verify** (EATP).

## Product Identity

CARE is NOT a governance engine (that's PACT). CARE is NOT a trust protocol (that's EATP). CARE is the onboarding experience that helps organizations answer: **"What AI governance do we need?"** — then produces the configuration to operationalize it.

**Audience**: Non-technical business leaders, operations managers, governance officers.
**Interaction model**: Voice-first, AI-guided conversation. Nobody clicks through forms in 2026.
**Output**: CARE Readiness Report + PACT-compatible YAML configuration.

### Positioning

Like AI Verify (IMDA, Singapore) but fundamentally different:

- AI Verify tests **AI models** for compliance. CARE assesses **organizations** for governance readiness.
- AI Verify targets developers. CARE targets business leaders.
- AI Verify produces compliance reports. CARE produces actionable governance configuration.
- AI Verify is retrospective (is this model OK?). CARE is prospective (what governance do you need?).

## Architecture

```
apps/
├── web/                           Next.js 15 + React 19
│   ├── Voice Engine               Web Speech API + Whisper (fallback)
│   ├── Conversation UI            Streaming chat + live transcript
│   ├── Assessment Canvas          React Flow (org tree) + D3 (radar/envelopes)
│   └── PACT Config Generator      Structured output → YAML export
└── mobile/                        Flutter (future)

src/
└── care/                          Python backend
    ├── conversation/              AI conversation engine (Kaizen agents)
    ├── assessment/                Maps responses → CARE dimensions
    ├── diagnosis/                 Gap analysis, maturity scoring
    └── generator/                 PACT YAML config synthesis
```

### Deployment

- **Hosted**: `care.terrene.foundation` — zero setup, Foundation-provided LLM
- **Self-hosted**: `docker compose up` — bring your own LLM (Ollama, vLLM, or Claude API key)

## Absolute Directives

These override ALL other instructions.

### 0. Foundation Independence — No Commercial Coupling

CARE Assessment Kit is a **Terrene Foundation project** (Apache 2.0). It is fully independent. There is NO relationship between CARE and any commercial product. CARE IS the product — not a derivative of anything. See `rules/independence.md`.

### 1. Framework-First

Never write code from scratch before checking whether the Kailash frameworks already handle it.

- Instead of direct SQL/SQLAlchemy/Django ORM → check with **dataflow-specialist**
- Instead of FastAPI/custom API gateway → check with **nexus-specialist**
- Instead of custom MCP server/client → check with **mcp-specialist**
- Instead of custom agentic platform → check with **kaizen-specialist**
- Instead of custom governance/access control → check with **pact-specialist**

### 2. .env Is the Single Source of Truth

All API keys and model names MUST come from `.env`. Never hardcode model strings. See `rules/env-models.md`.

### 3. Implement, Don't Document

When you discover a missing feature, endpoint, or record — **implement or create it**. Do not note it as a gap. See `rules/no-stubs.md`.

### 4. Zero Tolerance

Pre-existing failures MUST be fixed. Stubs are BLOCKED. Naive fallbacks are BLOCKED. See `rules/zero-tolerance.md`.

### 5. Recommended Reviews

- **Code review** (intermediate-reviewer) after file changes — RECOMMENDED
- **Security review** (security-reviewer) before commits — strongly recommended
- **Real infrastructure recommended** in Tier 2/3 tests

### 6. LLM-First Agent Reasoning

The LLM does ALL reasoning. Tools are dumb data endpoints. No if-else routing in agent decision paths. See `rules/agent-reasoning.md`.

### 7. Plain Language Always

CARE's audience is non-technical. All user-facing content MUST use plain language. No jargon without immediate explanation. No code snippets in user-facing UI. See `rules/communication.md`.

### 8. Text-First, Voice-Enhanced

Text is the default input modality. Voice is an opt-in enhancement with explicit privacy disclosure (Web Speech API sends audio to external servers). Every interaction must work via text. Voice adds convenience but is never required.

## Workspace Commands

| Command      | Phase | Purpose                                            |
| ------------ | ----- | -------------------------------------------------- |
| `/analyze`   | 01    | Load analysis phase for current workspace          |
| `/todos`     | 02    | Load todos phase; stops for human approval         |
| `/implement` | 03    | Load implementation phase; repeat until todos done |
| `/redteam`   | 04    | Load validation phase; red team with MCP tools     |
| `/codify`    | 05    | Load codification phase; create agents & skills    |
| `/ws`        | —     | Read-only workspace status dashboard               |
| `/wrapup`    | —     | Write session notes before ending                  |
| `/journal`   | —     | View, create, or search project journal entries    |

## The CARE Assessment Journey

### Phase 1: Assess — "Tell us about your organization"

AI-guided conversation discovers:

- Organizational structure (maps to D/T/R grammar)
- Decision-making authority (maps to constraint envelopes)
- Data sensitivity (maps to knowledge clearance levels)
- AI usage patterns (maps to verification gradient zones)
- Communication policies (maps to bridge configurations)

### Phase 2: Diagnose — "Here's what we found"

- CARE Maturity Score across 5 constraint dimensions (Financial, Operational, Temporal, Data Access, Communication)
- Gap analysis with plain-language explanations
- Risk map highlighting undefined governance areas
- Comparison against CARE framework best practices

### Phase 3: Recommend — "Here's what to do"

- Prioritized action plan in plain language
- Phased adoption roadmap (personalized to organization)
- For each gap: what it means, why it matters, what to do

### Phase 4: Generate — "Here's your configuration"

- PACT-compatible YAML: org structure, envelope definitions, clearance matrix
- Importable into pact-platform
- Plain-language summary for the business leader; YAML for the technical team

## Tech Stack

| Layer         | Technology              | Purpose                              |
| ------------- | ----------------------- | ------------------------------------ |
| Frontend      | Next.js 15 + React 19   | Web application                      |
| Voice         | Web Speech API, Whisper | Speech-to-text input                 |
| Conversation  | Kaizen agents           | AI-guided assessment conversation    |
| Assessment    | Python + kailash        | CARE dimension mapping, gap analysis |
| Governance    | kailash-pact            | PACT config generation               |
| Visualization | React Flow, D3          | Org tree, maturity radar, envelopes  |

## Kailash Platform Dependencies

| Framework    | Purpose in CARE                        | Install                        |
| ------------ | -------------------------------------- | ------------------------------ |
| **Core SDK** | Workflow orchestration                 | `pip install kailash`          |
| **Kaizen**   | AI conversation agent framework        | `pip install kailash-kaizen`   |
| **PACT**     | Config generation, governance grammar  | `pip install kailash-pact`     |
| **DataFlow** | Assessment data persistence (optional) | `pip install kailash-dataflow` |
| **Nexus**    | API deployment                         | `pip install kailash-nexus`    |

## Rules Index

Inherited from COC template (kailash-coc-claude-py v1.2.0). See `.claude/rules/` for full rule set.

## Agents

Inherited from COC template. Key agents for CARE development:

### Framework Specialists

- **kaizen-specialist** — AI agent conversation engine
- **pact-specialist** — Governance grammar, envelope generation
- **nexus-specialist** — API deployment
- **dataflow-specialist** — Data persistence

### Frontend & Design

- **react-specialist** — Next.js frontend
- **uiux-designer** — Enterprise UI/UX
- **ai-ux-designer** — Conversational AI interaction patterns

### Standards

- **care-expert** — CARE governance framework (the spec this product implements)
- **eatp-expert** — EATP trust protocol
- **co-expert** — CO methodology
- **pact-specialist** — PACT governance architecture

### Analysis & Review

- **deep-analyst** — Risk and gap analysis
- **intermediate-reviewer** — Code review
- **security-reviewer** — Security audit
