# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Tests for ExecutionRuntime governance path and emergency halt.

Covers: halt blocks processing, resume unblocks, is_halted property,
empty-reason halt rejection, governance engine error fail-closed,
and missing role address fail-closed.
"""

from __future__ import annotations

from typing import Any

import pytest

from pact_platform.build.config.schema import VerificationLevel
from pact_platform.trust.audit.anchor import AuditChain
from pact_platform.use.execution.registry import AgentRegistry
from pact_platform.use.execution.runtime import (
    ExecutionRuntime,
    Task,
    TaskStatus,
)


# ---------------------------------------------------------------------------
# Mock governance engine
# ---------------------------------------------------------------------------


class _MockVerdict:
    """Minimal verdict object returned by the mock engine."""

    def __init__(self, level: str, reason: str = "", audit_details: dict[str, Any] | None = None):
        self.level = level
        self.reason = reason
        self.audit_details = audit_details if audit_details is not None else {}


class _MockGovernanceEngine:
    """Mock GovernanceEngine for testing runtime governance paths.

    Set ``verdict`` to control verify_action() responses.
    Set ``should_raise`` to make it throw on the next call.
    """

    def __init__(self, verdict: _MockVerdict | None = None) -> None:
        self.verdict = verdict or _MockVerdict("auto_approved")
        self.should_raise: Exception | None = None
        self.call_count: int = 0

    def verify_action(
        self,
        role_address: str,
        action: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> _MockVerdict:
        self.call_count += 1
        if self.should_raise is not None:
            raise self.should_raise
        return self.verdict


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry() -> AgentRegistry:
    """A fresh AgentRegistry with a single active agent."""
    reg = AgentRegistry()
    reg.register(agent_id="agent-1", name="Test Agent", role="analyst")
    return reg


@pytest.fixture()
def audit_chain() -> AuditChain:
    return AuditChain(chain_id="test-chain")


@pytest.fixture()
def runtime(registry: AgentRegistry, audit_chain: AuditChain) -> ExecutionRuntime:
    """Runtime without a governance engine (for halt tests)."""
    return ExecutionRuntime(registry=registry, audit_chain=audit_chain)


# ---------------------------------------------------------------------------
# Test: emergency halt
# ---------------------------------------------------------------------------


class TestEmergencyHalt:
    """Verify the halt/resume mechanism on ExecutionRuntime."""

    def test_halt_blocks_process_next(
        self,
        runtime: ExecutionRuntime,
    ) -> None:
        """When halted, process_next() must return None even if tasks are queued."""
        runtime.submit("read_docs", agent_id="agent-1")
        runtime.halt("security incident")

        result = runtime.process_next()

        assert result is None
        assert runtime.queue_depth == 1, "Task should remain in the queue"

    def test_resume_unblocks(
        self,
        runtime: ExecutionRuntime,
    ) -> None:
        """After halt then resume, process_next() should process the task."""
        task_id = runtime.submit("read_docs", agent_id="agent-1")
        runtime.halt("investigating")
        runtime.resume()

        task = runtime.process_next()

        assert task is not None
        assert task.task_id == task_id
        assert task.status in (TaskStatus.COMPLETED, TaskStatus.EXECUTING)

    def test_is_halted_property(
        self,
        runtime: ExecutionRuntime,
    ) -> None:
        """is_halted must reflect the current halt state."""
        assert runtime.is_halted is False

        runtime.halt("test halt")
        assert runtime.is_halted is True

        runtime.resume()
        assert runtime.is_halted is False

    def test_halt_requires_reason(
        self,
        runtime: ExecutionRuntime,
    ) -> None:
        """An empty reason string must raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            runtime.halt("")


# ---------------------------------------------------------------------------
# Test: governance error path (fail-closed)
# ---------------------------------------------------------------------------


class TestGovernanceErrorPath:
    """Verify that governance engine errors result in BLOCKED tasks."""

    def test_governance_error_returns_blocked(
        self,
        registry: AgentRegistry,
        audit_chain: AuditChain,
    ) -> None:
        """When the governance engine raises, the task must be BLOCKED (fail-closed)."""
        engine = _MockGovernanceEngine()
        engine.should_raise = RuntimeError("engine unavailable")

        rt = ExecutionRuntime(
            registry=registry,
            audit_chain=audit_chain,
            governance_engine=engine,
        )
        # Map the agent to a role address so the governance path is entered
        rt.set_agent_role_address("agent-1", "D1-R1")

        task_id = rt.submit("summarize_report", agent_id="agent-1")
        task = rt.process_next()

        assert task is not None
        assert task.status == TaskStatus.BLOCKED
        assert task.verification_level == VerificationLevel.BLOCKED
        assert task.result is not None
        assert "fail-closed" in task.result.error

    def test_missing_role_address_blocks(
        self,
        registry: AgentRegistry,
        audit_chain: AuditChain,
    ) -> None:
        """Governance engine configured but no role_address for agent -> BLOCKED."""
        engine = _MockGovernanceEngine()

        rt = ExecutionRuntime(
            registry=registry,
            audit_chain=audit_chain,
            governance_engine=engine,
        )
        # Deliberately do NOT set a role address for agent-1

        task_id = rt.submit("do_something", agent_id="agent-1")
        task = rt.process_next()

        assert task is not None
        assert task.status == TaskStatus.BLOCKED
        assert task.verification_level == VerificationLevel.BLOCKED
        assert task.result is not None
        assert "no governance role address" in task.result.error.lower()
        # The engine should NOT have been called since there is no address
        assert engine.call_count == 0
