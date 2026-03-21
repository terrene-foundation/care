# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""PACT governance layer -- D/T/R grammar, addressing, clearance, access enforcement, envelopes."""

from pact.governance.addressing import (
    Address,
    AddressError,
    AddressSegment,
    GrammarError,
    NodeType,
)
from pact.governance.compilation import (
    CompilationError,
    CompiledOrg,
    OrgNode,
    RoleDefinition,
    VacancyStatus,
    compile_org,
)
from pact.governance.access import (
    AccessDecision,
    KnowledgeSharePolicy,
    PactBridge,
    can_access,
)
from pact.governance.clearance import (
    POSTURE_CEILING,
    RoleClearance,
    VettingStatus,
    effective_clearance,
)
from pact.governance.envelopes import (
    MonotonicTighteningError,
    RoleEnvelope,
    TaskEnvelope,
    check_degenerate_envelope,
    compute_effective_envelope,
    default_envelope_for_posture,
    intersect_envelopes,
)
from pact.governance.knowledge import KnowledgeItem
from pact.governance.audit import (
    PactAuditAction,
    create_pact_audit_details,
)
from pact.governance.store import (
    MAX_STORE_SIZE,
    AccessPolicyStore,
    ClearanceStore,
    EnvelopeStore,
    MemoryAccessPolicyStore,
    MemoryClearanceStore,
    MemoryEnvelopeStore,
    MemoryOrgStore,
    OrgStore,
)

__all__ = [
    # Addressing (TODO-1001)
    "Address",
    "AddressError",
    "AddressSegment",
    "GrammarError",
    "NodeType",
    # Compilation (TODO-1003, 1004, 1005)
    "CompilationError",
    "CompiledOrg",
    "OrgNode",
    "RoleDefinition",
    "VacancyStatus",
    "compile_org",
    # Clearance (TODO-2001)
    "POSTURE_CEILING",
    "RoleClearance",
    "VettingStatus",
    "effective_clearance",
    # Knowledge (TODO-2002)
    "KnowledgeItem",
    # Access enforcement (TODO-2003 through 2006)
    "AccessDecision",
    "KnowledgeSharePolicy",
    "PactBridge",
    "can_access",
    # Envelopes (TODO-3001 through 3006)
    "MonotonicTighteningError",
    "RoleEnvelope",
    "TaskEnvelope",
    "check_degenerate_envelope",
    "compute_effective_envelope",
    "default_envelope_for_posture",
    "intersect_envelopes",
    # Audit (TODO-4003)
    "PactAuditAction",
    "create_pact_audit_details",
    # Store protocols and implementations (TODO-4001, 4002)
    "MAX_STORE_SIZE",
    "AccessPolicyStore",
    "ClearanceStore",
    "EnvelopeStore",
    "MemoryAccessPolicyStore",
    "MemoryClearanceStore",
    "MemoryEnvelopeStore",
    "MemoryOrgStore",
    "OrgStore",
]
