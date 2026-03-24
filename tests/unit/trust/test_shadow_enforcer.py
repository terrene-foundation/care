# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Tests for the ShadowEnforcer — parallel trust evaluation without enforcement.

Covers: verdict mapping (auto_approved, blocked, held, flagged), halt check,
posture enforcement, fail-safe on exception, metrics tracking, windowed
metrics, report generation, posture evidence conversion, result trimming,
agent eviction, and unknown agent KeyError.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from pact_platform.build.config.schema import TrustPostureLevel, VerificationLevel
from pact_platform.trust.shadow_enforcer import (
    ShadowEnforcer,
    ShadowMetrics,
    ShadowReport,
    ShadowResult,
)


# ---------------------------------------------------------------------------
# Mock governance engine
# ---------------------------------------------------------------------------


class _MockVerdict:
    """Minimal verdict returned by the mock governance engine."""

    def __init__(self, level: str, reason: str = "", audit_details: dict[str, Any] | None = None):
        self.level = level
        self.reason = reason
        self.audit_details = audit_details if audit_details is not None else {}


class _MockGovernanceEngine:
    """Mock GovernanceEngine that returns a configurable verdict.

    Set ``verdict`` before calling ``verify_action`` to control the response.
    Set ``should_raise`` to make it raise on the next call.
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
def engine() -> _MockGovernanceEngine:
    return _MockGovernanceEngine()


@pytest.fixture()
def enforcer(engine: _MockGovernanceEngine) -> ShadowEnforcer:
    return ShadowEnforcer(governance_engine=engine, role_address="D1-R1")


# ---------------------------------------------------------------------------
# Test: verdict mapping
# ---------------------------------------------------------------------------


class TestShadowVerdictMapping:
    """Verify that each governance verdict level maps to the correct ShadowResult flags."""

    def test_auto_approved_action(self, engine: _MockGovernanceEngine) -> None:
        engine.verdict = _MockVerdict("auto_approved")
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate("read_report", "agent-1")

        assert result.would_be_auto_approved is True
        assert result.would_be_blocked is False
        assert result.would_be_held is False
        assert result.would_be_flagged is False
        assert result.verification_level == VerificationLevel.AUTO_APPROVED

    def test_blocked_action(self, engine: _MockGovernanceEngine) -> None:
        engine.verdict = _MockVerdict("blocked", reason="budget exceeded")
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate("expensive_action", "agent-2")

        assert result.would_be_blocked is True
        assert result.would_be_auto_approved is False
        assert result.would_be_held is False
        assert result.would_be_flagged is False
        assert result.verification_level == VerificationLevel.BLOCKED

    def test_held_action(self, engine: _MockGovernanceEngine) -> None:
        engine.verdict = _MockVerdict("held", reason="needs approval")
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate("modify_constraints", "agent-3")

        assert result.would_be_held is True
        assert result.would_be_auto_approved is False
        assert result.would_be_blocked is False
        assert result.would_be_flagged is False
        assert result.verification_level == VerificationLevel.HELD

    def test_flagged_action(self, engine: _MockGovernanceEngine) -> None:
        engine.verdict = _MockVerdict("flagged", reason="unusual pattern")
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate("send_email", "agent-4")

        assert result.would_be_flagged is True
        assert result.would_be_auto_approved is False
        assert result.would_be_blocked is False
        assert result.would_be_held is False
        assert result.verification_level == VerificationLevel.FLAGGED


# ---------------------------------------------------------------------------
# Test: halt and posture escalations
# ---------------------------------------------------------------------------


class TestShadowEscalations:
    """Verify halt check and PSEUDO_AGENT posture produce BLOCKED results."""

    def test_halt_check_blocks_all(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(
            governance_engine=engine,
            role_address="D1-R1",
            halted_check=lambda: True,
        )

        result = enforcer.evaluate("any_action", "agent-1")

        assert result.would_be_blocked is True
        assert result.verification_level == VerificationLevel.BLOCKED
        assert "halt" in result.dimension_results
        # The governance engine should NOT have been called since halt short-circuits
        assert engine.call_count == 0

    def test_pseudo_agent_posture_blocks(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate(
            "any_action",
            "agent-pseudo",
            agent_posture=TrustPostureLevel.PSEUDO_AGENT,
        )

        assert result.would_be_blocked is True
        assert result.verification_level == VerificationLevel.BLOCKED
        assert "posture" in result.dimension_results
        assert result.dimension_results["posture"] == "pseudo_agent_blocked"
        # Engine should NOT have been called since posture check short-circuits
        assert engine.call_count == 0


# ---------------------------------------------------------------------------
# Test: fail-safe behavior
# ---------------------------------------------------------------------------


class TestShadowFailSafe:
    """ShadowEnforcer must never crash the caller; on exception it returns auto_approved."""

    def test_exception_returns_safe_result(self, engine: _MockGovernanceEngine) -> None:
        engine.should_raise = RuntimeError("engine on fire")
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        result = enforcer.evaluate("action_during_error", "agent-err")

        assert result.would_be_auto_approved is True
        assert result.would_be_blocked is False
        assert result.would_be_held is False
        assert result.would_be_flagged is False
        assert result.verification_level == VerificationLevel.AUTO_APPROVED
        assert result.dimension_results == {}


# ---------------------------------------------------------------------------
# Test: metrics tracking
# ---------------------------------------------------------------------------


class TestShadowMetricsTracking:
    """Verify that repeated evaluations produce correct aggregate metrics."""

    def test_metrics_tracking(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        # 3 auto_approved
        engine.verdict = _MockVerdict("auto_approved")
        for _ in range(3):
            enforcer.evaluate("read", "agent-m")

        # 2 blocked
        engine.verdict = _MockVerdict("blocked")
        for _ in range(2):
            enforcer.evaluate("write", "agent-m")

        # 1 held
        engine.verdict = _MockVerdict("held")
        enforcer.evaluate("delete", "agent-m")

        # 1 flagged
        engine.verdict = _MockVerdict("flagged")
        enforcer.evaluate("update", "agent-m")

        metrics = enforcer.get_metrics("agent-m")

        assert metrics.total_evaluations == 7
        assert metrics.auto_approved_count == 3
        assert metrics.blocked_count == 2
        assert metrics.held_count == 1
        assert metrics.flagged_count == 1
        assert metrics.agent_id == "agent-m"

    def test_metrics_window(self, engine: _MockGovernanceEngine) -> None:
        """get_metrics_window filters results to the specified time window."""
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        engine.verdict = _MockVerdict("auto_approved")
        # Produce at least one evaluation so the agent exists
        enforcer.evaluate("action", "agent-w")

        # get_metrics_window should succeed (even if there is only one evaluation,
        # it should be within a 30-day window)
        windowed = enforcer.get_metrics_window("agent-w", days=30)

        assert isinstance(windowed, ShadowMetrics)
        assert windowed.agent_id == "agent-w"
        assert windowed.total_evaluations >= 1


# ---------------------------------------------------------------------------
# Test: report generation
# ---------------------------------------------------------------------------


class TestShadowReport:
    """Verify generate_report produces a well-formed ShadowReport."""

    def test_generate_report(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        engine.verdict = _MockVerdict("auto_approved")
        for _ in range(5):
            enforcer.evaluate("action", "agent-r")

        report = enforcer.generate_report("agent-r")

        assert isinstance(report, ShadowReport)
        assert report.agent_id == "agent-r"
        assert report.total_evaluations == 5
        assert report.pass_rate == pytest.approx(1.0)
        assert report.block_rate == pytest.approx(0.0)
        assert report.hold_rate == pytest.approx(0.0)
        assert report.flag_rate == pytest.approx(0.0)
        assert isinstance(report.upgrade_blockers, list)
        assert isinstance(report.recommendation, str)
        assert report.evaluation_period_days >= 1


# ---------------------------------------------------------------------------
# Test: posture evidence
# ---------------------------------------------------------------------------


class TestPostureEvidence:
    """Verify to_posture_evidence maps metrics correctly."""

    def test_to_posture_evidence(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")

        engine.verdict = _MockVerdict("auto_approved")
        for _ in range(4):
            enforcer.evaluate("action", "agent-p")

        engine.verdict = _MockVerdict("blocked")
        enforcer.evaluate("bad_action", "agent-p")

        evidence = enforcer.to_posture_evidence("agent-p")

        assert evidence.successful_operations == 4
        assert evidence.total_operations == 5
        assert evidence.shadow_blocked_count == 1
        assert evidence.incidents == 0
        assert evidence.shadow_enforcer_pass_rate == pytest.approx(4 / 5)


# ---------------------------------------------------------------------------
# Test: result trimming
# ---------------------------------------------------------------------------


class TestShadowTrimming:
    """Verify bounded memory enforcement on the results list."""

    def test_trimming(self, engine: _MockGovernanceEngine) -> None:
        """With maxlen=5, adding 10 results should trim to at most 5."""
        enforcer = ShadowEnforcer(
            governance_engine=engine,
            role_address="D1-R1",
            maxlen=5,
        )

        engine.verdict = _MockVerdict("auto_approved")
        for i in range(10):
            enforcer.evaluate(f"action-{i}", f"agent-trim-{i % 3}")

        # Internal _results list must be bounded
        assert len(enforcer._results) <= 5


# ---------------------------------------------------------------------------
# Test: _MAX_AGENTS eviction
# ---------------------------------------------------------------------------


class TestShadowMetricsBounded:
    """Verify that _metrics dict evicts oldest agents when _MAX_AGENTS is reached."""

    def test_metrics_bounded(self, engine: _MockGovernanceEngine) -> None:
        enforcer = ShadowEnforcer(governance_engine=engine, role_address="D1-R1")
        # Lower the limit for testing
        enforcer._MAX_AGENTS = 3

        engine.verdict = _MockVerdict("auto_approved")
        enforcer.evaluate("a", "agent-0")
        enforcer.evaluate("a", "agent-1")
        enforcer.evaluate("a", "agent-2")

        # All three agents should be present
        assert "agent-0" in enforcer._metrics
        assert "agent-1" in enforcer._metrics
        assert "agent-2" in enforcer._metrics

        # Adding a 4th should evict the oldest
        enforcer.evaluate("a", "agent-3")

        assert len(enforcer._metrics) == 3
        assert "agent-3" in enforcer._metrics
        # agent-0 was the earliest (oldest window_end) and should be evicted
        assert "agent-0" not in enforcer._metrics


# ---------------------------------------------------------------------------
# Test: unknown agent KeyError
# ---------------------------------------------------------------------------


class TestUnknownAgent:
    """get_metrics for a never-seen agent must raise KeyError."""

    def test_unknown_agent_raises_keyerror(self, enforcer: ShadowEnforcer) -> None:
        with pytest.raises(KeyError, match="No shadow metrics found for agent"):
            enforcer.get_metrics("nonexistent-agent")
