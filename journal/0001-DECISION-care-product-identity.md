---
type: DECISION
date: 2026-03-31
created_at: 2026-03-31T21:00:00Z
author: co-authored
session_id: initial-bootstrap
session_turn: 15
project: care
topic: CARE product identity — assessment kit, not governance engine
phase: analyze
tags: [product, architecture, positioning, pact, care]
---

## Decision

CARE is a one-time AI-guided governance assessment and onboarding tool. It is NOT a governance engine (that's PACT), NOT a trust protocol (that's EATP). CARE fills the "discover" step: **discover (CARE) -> enforce (PACT) -> verify (EATP)**.

## Alternatives Considered

1. **Archive care/ — pact IS the CARE implementation.** Rejected: PACT already has full frontends; care/ would be redundant.
2. **Make care/ the frontend for pact.** Rejected: PACT already has Next.js + Flutter apps.
3. **Make care/ a distinct product.** Chosen: assessment & onboarding kit for non-technical leaders.

## Rationale

The gap in the market is pre-operational. Organizations don't know what governance they need. PACT assumes you've already done that hard thinking. CARE is the bridge — like "AI Verify but way better and practical." It assesses organizations (not models), uses conversation (not forms), and produces actionable PACT config (not just reports).

## Consequences

- care/ targets non-technical business leaders, not developers
- Output is OrgGeneratorConfig-compatible YAML (not full PactConfig)
- CARE is a one-time funnel — PACT owns the config after handoff
- Text-first, voice-enhanced (not voice-first — privacy and reliability concerns)
- Both hosted (care.terrene.foundation) and self-hosted (Docker)

## For Discussion

- If PACT's org builder becomes conversational in the future, does CARE become redundant? What's the long-term boundary?
- If the hosted version at care.terrene.foundation sees significant usage, how does Foundation fund ongoing LLM inference costs?
- If CARE assessment data reveals organizational dysfunction (e.g., no one knows who approves what), should CARE surface this as a governance finding or just record gaps?
