---
type: DECISION
date: 2026-03-31
created_at: 2026-03-31T22:00:00Z
author: co-authored
session_id: initial-bootstrap
session_turn: 25
project: care
topic: Text-first with voice enhancement, not voice-first
phase: redteam
tags: [ux, voice, privacy, architecture]
---

## Decision

CARE uses text as the default input modality. Voice is an opt-in enhancement with explicit privacy disclosure. This reverses the initial "voice-first" direction.

## Rationale

Red team analysis identified voice-first as the single biggest technical risk:

- Web Speech API sends audio to Google servers — governance officers describing internal authority structures is sensitive corporate intelligence
- Domain terms (D/T/R, PACT, constraint envelope) have poor recognition accuracy
- Accents and background noise compound the problem
- The target audience (senior leaders) has the lowest tolerance for friction

## Consequences

- CLAUDE.md Directive 8 updated from "Voice-First Design" to "Text-First, Voice-Enhanced"
- useVoice hook requires explicit privacy acceptance before activating
- Privacy dialog has separate "enable voice" and "use text only" buttons with distinct behaviors
- Self-hosted mode can use local Whisper for full privacy

## For Discussion

- If browser speech recognition improves significantly (e.g., on-device processing), should the default flip back to voice-first?
- Should the privacy disclosure mention Google by name, or is "external servers" sufficient?
