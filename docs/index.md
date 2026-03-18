# CARE Platform

**Governed operational model for running organizations with AI agents under EATP trust governance.**

The CARE Platform is the Terrene Foundation's open-source (Apache 2.0) reference implementation of the [CARE specification](https://terrene.foundation). It operationalizes organizations as agent-orchestrated systems where every agent action is governed by cryptographic trust chains, constraint envelopes, and a verification gradient.

## What CARE Platform Does

- **Trust governance**: Every agent action traces back to human authority through EATP trust chains
- **Constraint envelopes**: Five-dimensional boundaries (financial, operational, temporal, data access, communication) limit what agents can do
- **Verification gradient**: Actions are classified as AUTO_APPROVED, FLAGGED, HELD, or BLOCKED based on risk
- **ShadowEnforcer**: Monitor what agents _would_ do before granting them autonomy
- **Organization builder**: Define your org structure in YAML, auto-generate governed agent teams

## Quick Start

```bash
pip install care-platform
care-platform org create --template media --name "My Team"
```

Or run the full platform with Docker:

```bash
git clone https://github.com/terrene-foundation/care.git
cd care
docker compose up
```

## Documentation

| Section                               | Description                                     |
| ------------------------------------- | ----------------------------------------------- |
| [Getting Started](getting-started.md) | Installation, setup, first agent team           |
| [Architecture](architecture.md)       | Platform design, trust model, constraint system |
| [API Reference](api.md)               | REST API endpoints and authentication           |
| [Cookbook](cookbook.md)               | Recipes for common tasks                        |

## The Trinity

CARE Platform implements three open standards published by the Terrene Foundation:

| Standard | Role                                                    | License   |
| -------- | ------------------------------------------------------- | --------- |
| **CARE** | Governance philosophy (Dual Plane Model, Mirror Thesis) | CC BY 4.0 |
| **EATP** | Trust protocol (trust lineage, verification gradient)   | CC BY 4.0 |
| **CO**   | Methodology (7 principles, 5 layers)                    | CC BY 4.0 |

## License

Apache 2.0 — Foundation-owned, irrevocably open.
