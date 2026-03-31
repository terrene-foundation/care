# Content Flow Governance

## Scope

These rules govern how content flows between Terrene Foundation repositories.

## Principles

### 1. Source is Authoritative

When content flows from source to target (e.g., foundation → website), the source repository is the single source of truth. Target content must accurately reflect the source.

### 2. Direction Matters

Content flows in defined directions. Reversing the flow (e.g., website → foundation) requires explicit justification and user confirmation.

```
foundation/    →  website/     (governance, strategy, about)
publications/  →  website/     (standards, philosophy, research)
atelier/       →  website/     (CO methodology, domain apps)
loom/          →  website/     (SDK docs, developer content)
```

### 3. Transformation, Not Duplication

Website content is a **transformation** of source material — adapted for public consumption. It is NOT a copy-paste. The sync process verifies accuracy, not identity.

### 4. External Dependencies

Content that flows from atelier/ and loom/ (external to this ecosystem) should be treated as upstream dependencies. Changes in those repos may require website updates, but the orchestrator does not control them.

## Content Tiers

| Tier          | Source               | Destination    | Verification                |
| ------------- | -------------------- | -------------- | --------------------------- |
| Foundation    | foundation/docs/     | website/       | Naming, facts, dates        |
| Standards     | foundation/docs/02-  | website/       | Spec accuracy, terminology  |
| Publications  | publications/        | website/       | PDF links, abstracts, dates |
| Technology    | loom/ (external)     | website/       | SDK versions, architecture  |
| Methodology   | atelier/ (external)  | website/       | CO descriptions, domain apps|
