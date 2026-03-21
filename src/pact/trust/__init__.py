# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Trust layer — postures, attestations, scoring, credentials, revocation, reasoning, messaging, integrity, and bridge trust."""

from pact.trust.attestation import CapabilityAttestation
from pact.trust.authorization import AuthorizationCheck, AuthorizationResult
from pact.trust.bridge_posture import bridge_verification_level, effective_posture
from pact.trust.bridge_trust import (
    BridgeDelegation,
    BridgeTrustManager,
    BridgeTrustRecord,
)
from pact.trust.credentials import CredentialManager, VerificationToken
from pact.trust.decorators import (
    CareTrustOpsProvider,
    care_audited,
    care_shadow,
    care_verified,
)
from pact.trust.delegation import ChainStatus, ChainWalkResult, DelegationManager
from pact.trust.dual_binding import DualBinding
from pact.trust.eatp_bridge import EATPBridge
from pact.trust.genesis import GenesisManager
from pact.trust.integrity import (
    IntegrityCheckResult,
    IntegrityViolation,
    TrustChainIntegrity,
    TrustRecordHash,
)
from pact.trust.jcs import canonical_hash, canonical_serialize
from pact.trust.messaging import (
    AgentMessage,
    MessageChannel,
    MessageRouter,
    MessageType,
)
from pact.trust.posture import (
    NEVER_DELEGATED_ACTIONS,
    PostureChange,
    PostureEvidence,
    TrustPosture,
)
from pact.trust.reasoning import (
    ConfidentialityLevel,
    ReasoningTrace,
    ReasoningTraceStore,
)
from pact.trust.revocation import RevocationManager, RevocationRecord
from pact.trust.scoring import (
    TrustFactors,
    TrustGrade,
    TrustScore,
    calculate_trust_score,
)
from pact.trust.sd_jwt import SDJWTBuilder, SelectiveDisclosureJWT
from pact.trust.shadow_enforcer import (
    ShadowEnforcer,
    ShadowMetrics,
    ShadowReport,
    ShadowResult,
)
from pact.trust.uncertainty import (
    ActionMetadata,
    ClassificationResult,
    UncertaintyClassifier,
    UncertaintyLevel,
)

__all__ = [
    "ActionMetadata",
    "AgentMessage",
    "AuthorizationCheck",
    "AuthorizationResult",
    "BridgeDelegation",
    "BridgeTrustManager",
    "BridgeTrustRecord",
    "CapabilityAttestation",
    "CareTrustOpsProvider",
    "ChainStatus",
    "ChainWalkResult",
    "ClassificationResult",
    "ConfidentialityLevel",
    "CredentialManager",
    "DelegationManager",
    "DualBinding",
    "EATPBridge",
    "GenesisManager",
    "IntegrityCheckResult",
    "IntegrityViolation",
    "TrustChainIntegrity",
    "TrustRecordHash",
    "MessageChannel",
    "MessageRouter",
    "MessageType",
    "NEVER_DELEGATED_ACTIONS",
    "PostureChange",
    "PostureEvidence",
    "ReasoningTrace",
    "ReasoningTraceStore",
    "RevocationManager",
    "RevocationRecord",
    "SDJWTBuilder",
    "SelectiveDisclosureJWT",
    "ShadowEnforcer",
    "ShadowMetrics",
    "ShadowReport",
    "ShadowResult",
    "TrustFactors",
    "TrustGrade",
    "TrustPosture",
    "TrustScore",
    "UncertaintyClassifier",
    "UncertaintyLevel",
    "VerificationToken",
    "bridge_verification_level",
    "calculate_trust_score",
    "canonical_hash",
    "canonical_serialize",
    "care_audited",
    "care_shadow",
    "care_verified",
    "effective_posture",
]
