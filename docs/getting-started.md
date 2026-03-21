# Getting Started with PACT

PACT (Principled Architecture for Constrained Trust) is a governance framework for running organizations with AI agents under governed autonomy. It answers the question: **How do you let AI agents do useful work without letting them do anything they shouldn't?**

## What PACT Does

PACT provides:

- **D/T/R Grammar** -- A structured way to describe who reports to whom (Departments, Teams, Roles)
- **Operating Envelopes** -- Constraint boundaries that limit what each role can do (spending caps, allowed actions, data access)
- **Knowledge Clearance** -- A classification system (PUBLIC through TOP SECRET) that controls who can see what, independent of seniority
- **Verification Gradient** -- Four levels (AUTO_APPROVED, FLAGGED, HELD, BLOCKED) that determine what happens when an agent tries to do something
- **Audit Trail** -- Every governance decision is recorded for compliance review

## Where PACT Fits

PACT is part of the Terrene Foundation's Quartet -- four open standards that work together:

| Standard | Purpose                                                         | Type         |
| -------- | --------------------------------------------------------------- | ------------ |
| **CARE** | Governance philosophy (Dual Plane Model, Mirror Thesis)         | Philosophy   |
| **PACT** | Organizational architecture (D/T/R, envelopes, clearance)       | Architecture |
| **EATP** | Trust protocol (cryptographic chains, verification, audit)      | Protocol     |
| **CO**   | Agent orchestration methodology (seven principles, five layers) | Methodology  |

PACT is the architectural layer. It defines the **structure** of a governed organization -- the org chart, the constraints, and the access rules. EATP provides the cryptographic trust enforcement underneath. CARE provides the philosophy above. CO provides the operational methodology.

## When to Use PACT

Use PACT when you need:

- **AI agents operating in a real organization** where different roles have different permissions
- **Financial controls** -- spending caps, approval thresholds, budget tracking
- **Information barriers** -- preventing data from flowing between departments that shouldn't share
- **Audit trails** -- every decision recorded with cryptographic proof
- **Posture-based access** -- agents with more trust get more autonomy

Do **not** use PACT if you just need a simple chatbot or a single-agent workflow. PACT is designed for multi-agent organizations with real governance requirements.

## The Kailash Platform

PACT is built on the Kailash Python SDK ecosystem:

| Framework            | Purpose                                    |
| -------------------- | ------------------------------------------ |
| **Kailash Core**     | Workflow orchestration (140+ node types)   |
| **Kailash DataFlow** | Zero-config database operations            |
| **Kailash Nexus**    | Multi-channel deployment (API + CLI + MCP) |
| **Kailash Kaizen**   | AI agent framework                         |

You do not need to install the full Kailash stack to use PACT governance. The core governance engine (`pact.governance`) works standalone with just the base `pact` package.

## Installation

```bash
pip install pact
```

For the full platform with Kailash SDK integration:

```bash
pip install pact[kailash]
```

## First Steps

1. **Read the [Quickstart](quickstart.md)** -- Go from zero to running governance in 10 minutes using the university example
2. **Read the [Architecture](architecture.md)** -- Understand how the GovernanceEngine, envelopes, and clearance work together
3. **Read the [Vertical Guide](vertical-guide.md)** -- Learn how to build your own domain (finance, healthcare, etc.) on PACT
4. **Browse the [Cookbook](cookbook.md)** -- Self-contained recipes for common governance tasks
5. **Check the [YAML Schema](yaml-schema.md)** -- Define your organization in a single YAML file
6. **Explore the [API Reference](api.md)** -- REST endpoints for programmatic governance

## The University Example

PACT ships with a complete university organization that demonstrates every governance concept:

- 6 departments, 5 teams, 12 roles across 5 levels of nesting
- Knowledge clearance independent of authority (IRB Director holds SECRET while Dean holds CONFIDENTIAL)
- Information barriers between Student Affairs and Academic Affairs
- Cross-Functional Bridges (Standing, Scoped)
- Knowledge Share Policies

The university domain was chosen because it requires zero domain expertise to understand -- everyone has encountered academic organizational structures. See the [Quickstart](quickstart.md) for a hands-on walkthrough.

## Building a Vertical

PACT is domain-agnostic. The framework knows nothing about finance, healthcare, education, or any other domain. Verticals -- like Astra (financial services) and Arbor (HR governance) -- import PACT and define their domain's D/T/R structure, envelope constraints, and clearance mappings as configuration.

The boundary test: if you replaced all domain vocabulary in a vertical's code with different domain terms, the `pact` library code would not change at all. Only the configuration and domain layer would change.

See the [Vertical Guide](vertical-guide.md) for a step-by-step walkthrough of building your own vertical.
