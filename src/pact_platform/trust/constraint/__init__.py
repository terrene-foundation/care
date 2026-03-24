# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Constraint infrastructure — bridge envelope intersection for cross-functional bridges.

Governance decisions are made by GovernanceEngine (kailash-pact).
This package provides the bridge envelope intersection logic for
cross-functional bridge constraint composition.
"""

from pact_platform.trust.constraint.bridge_envelope import (
    BridgeSharingPolicy,
    FieldSharingRule,
    SharingMode,
    compute_bridge_envelope,
    validate_bridge_tightening,
)

__all__ = [
    "BridgeSharingPolicy",
    "FieldSharingRule",
    "SharingMode",
    "compute_bridge_envelope",
    "validate_bridge_tightening",
]
