# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Tests for pact top-level package exports (Task 113).

Validates that all key public types are importable directly from pact.
"""


class TestConfigExports:
    """All config types must be importable from pact."""

    def test_pact_config(self):
        from pact import PactConfig

        assert PactConfig is not None

    def test_platform_config_backward_compat(self):
        from pact import PlatformConfig

        assert PlatformConfig is not None

    def test_agent_config(self):
        from pact import AgentConfig

        assert AgentConfig is not None

    def test_team_config(self):
        from pact import TeamConfig

        assert TeamConfig is not None

    def test_workspace_config(self):
        from pact import WorkspaceConfig

        assert WorkspaceConfig is not None

    def test_constraint_envelope_config(self):
        from pact import ConstraintEnvelopeConfig

        assert ConstraintEnvelopeConfig is not None


class TestConstraintExports:
    """Constraint types must be importable from pact."""

    def test_constraint_envelope(self):
        from pact import ConstraintEnvelope

        assert ConstraintEnvelope is not None

    def test_gradient_engine(self):
        from pact import GradientEngine

        assert GradientEngine is not None

    def test_evaluation_result(self):
        from pact import EvaluationResult

        assert EvaluationResult is not None


class TestTrustExports:
    """Trust types must be importable from pact."""

    def test_trust_posture(self):
        from pact import TrustPosture

        assert TrustPosture is not None

    def test_capability_attestation(self):
        from pact import CapabilityAttestation

        assert CapabilityAttestation is not None

    def test_trust_score(self):
        from pact import TrustScore

        assert TrustScore is not None

    def test_calculate_trust_score(self):
        from pact import calculate_trust_score

        assert callable(calculate_trust_score)


class TestAuditExports:
    """Audit types must be importable from pact."""

    def test_audit_anchor(self):
        from pact import AuditAnchor

        assert AuditAnchor is not None

    def test_audit_chain(self):
        from pact import AuditChain

        assert AuditChain is not None


class TestWorkspaceExports:
    """Workspace types must be importable from pact."""

    def test_workspace(self):
        from pact import Workspace

        assert Workspace is not None

    def test_workspace_phase(self):
        from pact import WorkspacePhase

        assert WorkspacePhase is not None

    def test_workspace_registry(self):
        from pact import WorkspaceRegistry

        assert WorkspaceRegistry is not None


class TestExecutionExports:
    """Execution types must be importable from pact."""

    def test_agent_definition(self):
        from pact import AgentDefinition

        assert AgentDefinition is not None

    def test_team_definition(self):
        from pact import TeamDefinition

        assert TeamDefinition is not None


class TestAllExportsConsistent:
    """Verify __all__ is defined and consistent."""

    def test_all_defined(self):
        import pact

        assert hasattr(pact, "__all__")

    def test_all_contains_key_types(self):
        import pact

        expected = [
            "PactConfig",
            "PlatformConfig",
            "AgentConfig",
            "TeamConfig",
            "WorkspaceConfig",
            "ConstraintEnvelopeConfig",
            "ConstraintEnvelope",
            "GradientEngine",
            "EvaluationResult",
            "TrustPosture",
            "CapabilityAttestation",
            "TrustScore",
            "calculate_trust_score",
            "AuditAnchor",
            "AuditChain",
            "Workspace",
            "WorkspacePhase",
            "WorkspaceRegistry",
            "AgentDefinition",
            "TeamDefinition",
        ]
        for name in expected:
            assert name in pact.__all__, f"{name} not in __all__"

    def test_all_entries_are_importable(self):
        import pact

        for name in pact.__all__:
            assert hasattr(pact, name), f"{name} in __all__ but not importable"
