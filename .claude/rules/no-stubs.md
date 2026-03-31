# No Placeholders or Incomplete Content

## Scope

These rules apply to all Foundation documents and specifications.

## RECOMMENDED Rules

### 1. Avoid Placeholder Content

Documents SHOULD NOT contain:

- `[TODO]`, `[TBD]`, `[INSERT HERE]` markers left as final content
- Empty sections with only headers and no substance
- "This section will be completed later" without a tracking reference

**Note**: `TODO` markers are acceptable during drafting but should be tracked and resolved before publication.

### 2. Avoid Vague Assertions

Specifications and governance documents SHOULD NOT contain:

- Claims without supporting rationale ("This is best practice")
- References to undefined processes ("As per the standard process")
- Unsubstantiated comparisons ("Better than existing solutions")

### 3. Complete What You Start

When creating a document section:

- If a clause is referenced, it should exist
- If a process is described, it should be complete enough to follow
- If a comparison is made, it should cite specifics

**Note**: Iterative drafting is fine — incomplete sections are acceptable when tracked as follow-up work.

## Why This Matters

Placeholder content in governance documents creates ambiguity. In a constitution, an undefined clause is a potential attack vector. In a specification, a vague process cannot be implemented.

## Exceptions

Working drafts in `workspaces/` are excluded — they are explicitly in-progress.
