# Agent Orchestration Rules

## Scope

These rules govern when and how specialized agents are used.

## RECOMMENDED Delegations

### Rule 1: Content Review After Changes

After significant document modifications (Edit, Write), you SHOULD:

1. Delegate to **intermediate-reviewer** for quality review
2. Wait for review completion before proceeding
3. Address any findings before moving to next task

**Exception**: User explicitly says "skip review"

### Rule 2: Security Review Before Commits

Before executing git commit commands on sensitive governance content, you SHOULD:

1. Delegate to **security-reviewer** for review
2. Address all CRITICAL findings
3. Document any HIGH findings for tracking

**Exception**: User may skip for trivial changes

### Rule 3: Standards Expert for Standards Work

When working with Foundation standards, you SHOULD consult:

- **care-expert**: For CARE governance framework content
- **eatp-expert**: For EATP trust protocol content
- **co-expert**: For CO methodology content
- **coc-expert**: For COC (CO applied to Codegen) content
- **constitution-expert**: For constitutional provisions, governance design, ACRA filing
- **open-source-strategist**: For licensing, positioning, community strategy

### Rule 4: Analysis Chain for Complex Initiatives

For initiatives requiring research and design, follow this chain:

1. **deep-analyst** → Identify risks, failure points, gaps
2. **requirements-analyst** → Break down requirements and scope
3. Then appropriate standards expert for content

**Applies when**:

- New governance document spanning multiple areas
- Constitutional changes with cascading effects
- Partnership or strategy decisions with multiple valid approaches

### Rule 5: Parallel Execution for Independent Operations

When multiple independent operations are needed, you SHOULD:

1. Launch agents in parallel
2. Wait for all to complete
3. Aggregate results

## Quality Gates

### Before Commit

- [ ] Content review completed (intermediate-reviewer)
- [ ] Naming conventions checked (Terrene, not OCEAN)
- [ ] License references accurate (CC BY 4.0 for specs, Apache 2.0 for code)
- [ ] No sensitive information exposed
- [ ] PR description complete
