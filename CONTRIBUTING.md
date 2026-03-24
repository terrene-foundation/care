# Contributing to PACT Platform

Thank you for your interest in contributing to the PACT Platform. This guide covers everything you need to set up your development environment, understand the contribution process, and submit changes.

The PACT Platform is owned by the Terrene Foundation and licensed under Apache 2.0. All contributions are welcome from anyone -- the Foundation operates under a uniform contributor framework with no special access or advantage for any contributor.

---

## Development Setup

### Prerequisites

- **Python 3.11 or later** (3.12 and 3.13 are also supported)
- **Git**
- A virtual environment tool (`venv`, `virtualenv`, or similar)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/terrene-foundation/pact.git
cd pact

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[all,dev]"
```

### Environment Configuration

Copy the environment template and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your API keys. At minimum, configure one LLM provider. The root `conftest.py` auto-loads `.env` for all pytest sessions, so no manual setup is needed for tests.

**Important**: Never commit `.env` files. The `.gitignore` already excludes them.

### Verify Your Setup

```bash
# Run the test suite
pytest

# Run with coverage
pytest --cov=src/pact_platform

# Lint
ruff check src/pact_platform/ tests/

# Type check
mypy src/pact_platform/
```

All 1838+ tests should pass. If any fail, check that your dependencies installed correctly and your `.env` is configured.

---

## Project Structure

```
src/pact_platform/       Main package
  models/                  11 DataFlow models (121 auto-generated CRUD nodes)
  use/api/routers/         7 API routers (42+ endpoints)
  use/services/            5 platform services
  use/execution/           Execution runtime, approval, enforcement
  engine/                  EnvelopeAdapter, GovernedDelegate, bridges, orchestrator
  build/config/            Organization definition schema and loader
  build/org/               Org compilation and seeding
  build/cli/               CLI subcommands
  integrations/            Notification adapters (Slack, Discord, Teams)
  examples/university/     Example vertical
apps/web/                Next.js dashboard (React 19 + TypeScript)
apps/mobile/             Flutter companion app
tests/                   Test suite (unit, integration)
docs/                    Documentation
```

---

## Running Tests

The project uses pytest with a three-tier testing strategy:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test directory
pytest tests/unit/

# Run tests matching a pattern
pytest -k "test_delegation"

# Run with coverage report
pytest --cov=src/pact_platform --cov-report=term-missing
```

### Test Requirements

- **All changes must include tests.** If you add a feature, add tests that cover it. If you fix a bug, add a test that reproduces the bug.
- Tests should be self-contained and not depend on external services unless testing integration specifically.
- Use the fixtures defined in `conftest.py` for common setup.
- Async tests are supported via `pytest-asyncio` (configured with `asyncio_mode = "auto"`).

---

## Code Style

### Formatting and Linting

The project uses **ruff** for linting with the following rules enabled:

- `E` (pycodestyle errors)
- `F` (pyflakes)
- `I` (isort)
- `UP` (pyupgrade)
- `B` (bugbear)
- `SIM` (simplify)

Line length is 100 characters.

```bash
# Check for issues
ruff check src/pact_platform/ tests/

# Auto-fix what can be fixed
ruff check --fix src/pact_platform/ tests/
```

### Type Checking

The project uses **mypy** for type checking:

```bash
mypy src/pact_platform/
```

### Conventions

- Use `@dataclass` (not Pydantic) for data structures.
- Use `from __future__ import annotations` for deferred annotation evaluation.
- All public classes and methods should have docstrings.
- Use `logging` (not `print`) for diagnostic output.
- Follow existing patterns in the codebase -- look at similar modules for guidance.

### License Headers

All Python source files must include the Apache 2.0 license header:

```python
# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
```

---

## Commit Conventions

The project uses **Conventional Commits**:

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:

- `feat` -- new feature
- `fix` -- bug fix
- `docs` -- documentation
- `style` -- formatting (no logic change)
- `refactor` -- code restructure
- `test` -- adding or updating tests
- `chore` -- maintenance

**Examples**:

```
feat(engine): add cumulative budget injection to verify_action
fix(api): handle NaN cost in objectives router
docs(readme): update quick start example
test(governance): add monotonic tightening edge cases
```

Each commit should be self-contained: tests and implementation together, building and passing on its own.

---

## Pull Request Process

### 1. Create a Feature Branch

```bash
git checkout -b feat/your-feature-name
# or: fix/your-bug-fix, docs/your-doc-update, etc.
```

### 2. Make Your Changes

- Follow the code style guidelines above.
- Include tests for new functionality.
- Update documentation if your changes affect public APIs.

### 3. Run the Full Check Suite

```bash
# Tests
pytest

# Lint
ruff check src/pact_platform/ tests/

# Type check
mypy src/pact_platform/
```

### 4. Submit a Pull Request

Push your branch and open a PR against `main`. Include:

- **Summary**: What changed and why (1-3 bullet points)
- **Test plan**: How to verify the changes
- **Related issues**: Link any relevant GitHub issues

**PR template**:

```markdown
## Summary

- [what changed and why]

## Test plan

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related issues

Fixes #123
```

### 5. Review

All PRs require review before merging. Reviewers will check:

- Code quality and style
- Test coverage
- Standards alignment (see below)
- Security considerations

---

## Standards Alignment

The PACT Platform is the reference implementation of the Quartet -- CARE, PACT, EATP, and CO. Contributions must not violate these standards:

- **CARE**: Dual Plane Model (Trust Plane + Execution Plane), Human-on-the-Loop governance
- **PACT**: D/T/R accountability grammar, operating envelopes, monotonic tightening, knowledge clearance
- **EATP**: Five-element trust lineage chains, verification gradient, trust postures
- **CO**: Seven principles, five layers of cognitive orchestration

If your change touches trust, governance, or constraint enforcement, consider consulting the specification documents at [terrene.dev](https://terrene.dev).

Key invariants that must be preserved:

- Constraint envelopes can only be tightened through delegation, never loosened
- Trust posture upgrades require evidence; downgrades are instant
- Every agent action must produce an audit anchor
- The five constraint dimensions (Financial, Operational, Temporal, Data Access, Communication) are the governance mechanism
- D/T/R grammar: every Department or Team must be immediately followed by exactly one Role

---

## Code of Conduct

Contributors are expected to act professionally and respectfully. The Terrene Foundation is committed to providing a welcoming and inclusive environment for everyone.

---

## Questions?

- **Documentation**: [terrene.dev/pact](https://terrene.dev/pact)
- **Issues**: [github.com/terrene-foundation/pact/issues](https://github.com/terrene-foundation/pact/issues)
- **Foundation**: [terrene.foundation](https://terrene.foundation)
