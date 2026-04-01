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

### 4. Section Existence Is Not Coverage

A section heading that matches a requirement is not completion. Each section SHOULD **substantively address** the requirement it claims to cover.

- A brief header with "To be expanded" is a placeholder, not coverage
- A section that restates the requirement without adding substance is not coverage
- Verify: could someone implement or comply based solely on what is written? If not, the section is incomplete

**Why**: In specifications, a named-but-empty clause creates false confidence that a topic is handled. Downstream specs and implementations will cite it and find nothing actionable.

### 5. Re-Read the Brief Before Each Section

Before drafting any section of a specification or publication, re-read the governing brief, editorial requirements, or upstream spec that defines what this section SHOULD cover. Do not draft from memory of the brief.

**Why**: Specifications drift from their requirements the same way code drifts from its plans. The brief is the anchor. Each section should be traceable to a specific requirement, not a paraphrase of one.

### 6. Separate Drafting from Verification

Treat content creation as two distinct passes:

1. **Draft**: Write the substantive content — definitions, clauses, rationale, examples
2. **Verify**: Check cross-references resolve, terminology aligns with other Foundation publications (CARE, EATP, CO, Praxis), and downstream consumers can cite this content

Attempting both simultaneously leads to neither being done thoroughly.

**Why**: A deliverable can be internally correct but break the ecosystem — dangling cross-references, misaligned terminology, or formats that downstream consumers cannot parse.

## Why This Matters

Placeholder content in governance documents creates ambiguity. In a constitution, an undefined clause is a potential attack vector. In a specification, a vague process cannot be implemented.

## Exceptions

Working drafts in `workspaces/` are excluded — they are explicitly in-progress.
