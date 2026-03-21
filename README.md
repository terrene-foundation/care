# PACT

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-active%20development-orange.svg)]()

**Governance framework for running organizations with AI agents under constrained trust.**

PACT is the Terrene Foundation's reference implementation of Principled Architecture for Constrained Trust -- an open-source framework for organizations that want AI agents operating within defined boundaries: who can do what, how much they can spend, and what information they can access.

> **What it is NOT**: A generic agent orchestrator. PACT is _governed orchestration_ -- every agent action passes through a governance pipeline that checks permissions, budgets, and information access before execution.

---

## 5-Line Quickstart

```python
from pact.governance.yaml_loader import load_org_yaml
from pact.governance.engine import GovernanceEngine

loaded = load_org_yaml("my-org.yaml")
engine = GovernanceEngine(loaded.org_definition)
verdict = engine.verify_action("D1-R1-T1-R1", "write", {"cost": 500})
print(f"{verdict.level}: {verdict.reason}")
```

---

## What PACT Provides

### D/T/R Organizational Grammar

Define organizations as Departments, Teams, and Roles with positional addresses:

```
D1-R1                    President
D1-R1-D1-R1              Provost
D1-R1-D1-R1-D1-R1        Dean of Engineering
D1-R1-D1-R1-D1-R1-T1-R1  CS Chair
```

Every D or T has exactly one R (head) -- guaranteeing single accountability at every level.

### Five-Dimension Operating Envelopes

Every role operates within a constraint envelope:

| Dimension     | What It Controls                     | Example                        |
| ------------- | ------------------------------------ | ------------------------------ |
| Financial     | Spending limits, approval thresholds | max_spend_usd: 10000           |
| Operational   | Allowed/blocked actions              | allowed_actions: [read, write] |
| Temporal      | Active hours, blackout periods       | 09:00-17:00 UTC                |
| Data Access   | Read/write paths                     | read_paths: [/data/public]     |
| Communication | Channel restrictions                 | internal_only: true            |

Envelopes compose through **monotonic tightening** -- a child role's envelope can only be equal to or more restrictive than its parent's.

### Knowledge Clearance Independent of Authority

Clearance is orthogonal to seniority. A junior IRB Director can hold SECRET clearance with the "human-subjects" compartment while the Dean of Engineering holds only CONFIDENTIAL:

```yaml
clearances:
  - role: r-irb-director
    level: secret
    compartments: [human-subjects]
  - role: r-dean-eng
    level: confidential
```

### Verification Gradient

Every action gets classified:

- **AUTO_APPROVED** -- within all constraints, proceed
- **FLAGGED** -- near a boundary, proceed with warning
- **HELD** -- exceeds soft limit, queued for human approval
- **BLOCKED** -- violates hard constraint, denied

### Cross-Functional Bridges and Knowledge Share Policies

Controlled exceptions to information barriers:

- **Bridges** connect two roles across boundaries (Standing, Scoped, Ad-Hoc)
- **KSPs** grant one-way unit-level data access

---

## Installation

```bash
pip install pact
```

For development:

```bash
git clone https://github.com/terrene-foundation/pact.git
cd pact
pip install -e ".[dev]"
```

---

## Define Your Organization in YAML

```yaml
org_id: "my-org"
name: "My Organization"

departments:
  - id: d-executive
    name: Executive
  - id: d-operations
    name: Operations

roles:
  - id: r-ceo
    name: CEO
    heads: d-executive
  - id: r-ops-lead
    name: Operations Lead
    reports_to: r-ceo
    heads: d-operations

envelopes:
  - target: r-ops-lead
    defined_by: r-ceo
    financial:
      max_spend_usd: 25000
    operational:
      allowed_actions: [read, write, approve]
```

Validate with the CLI:

```bash
python -m pact.governance.cli validate my-org.yaml
```

---

## The Quartet

PACT implements four open specifications published by the Terrene Foundation:

| Standard | Full Name                                      | Type         | License   |
| -------- | ---------------------------------------------- | ------------ | --------- |
| **CARE** | Collaborative Autonomous Reflective Enterprise | Philosophy   | CC BY 4.0 |
| **PACT** | Principled Architecture for Constrained Trust  | Architecture | CC BY 4.0 |
| **EATP** | Enterprise Agent Trust Protocol                | Protocol     | CC BY 4.0 |
| **CO**   | Cognitive Orchestration                        | Methodology  | CC BY 4.0 |

---

## Built On

| Framework            | Purpose                | Install                        |
| -------------------- | ---------------------- | ------------------------------ |
| **Kailash Core**     | Workflow orchestration | `pip install kailash`          |
| **Kailash DataFlow** | Database operations    | `pip install kailash-dataflow` |
| **Kailash Nexus**    | API deployment         | `pip install kailash-nexus`    |
| **Kailash Kaizen**   | AI agents              | `pip install kailash-kaizen`   |
| **EATP SDK**         | Trust chains           | `pip install eatp`             |

---

## Documentation

- [Getting Started](docs/getting-started.md) -- What PACT is and when to use it
- [Quickstart](docs/quickstart.md) -- From zero to running governance in 10 minutes
- [Architecture](docs/architecture.md) -- Engine internals, addressing, envelopes, clearance
- [Vertical Guide](docs/vertical-guide.md) -- Build your own domain on PACT
- [YAML Schema](docs/yaml-schema.md) -- Complete YAML format reference
- [Cookbook](docs/cookbook.md) -- Recipes for common tasks
- [REST API](docs/api.md) -- HTTP endpoints with curl examples

---

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Run the university demo:

```bash
python -m pact.examples.university.demo
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contributor guide.

---

## License

Copyright 2026 Terrene Foundation

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

PACT is Foundation-owned, Apache 2.0 licensed, and irrevocably open. The Foundation has no structural relationship with any commercial entity. Anyone can build commercial implementations on top of the Foundation's open standards and SDKs.

**Specifications** (CARE, PACT, EATP, CO): CC BY 4.0
**Code** (PACT, Kailash SDK, EATP SDK): Apache 2.0
