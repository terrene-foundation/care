# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Foundation Full Org — backward-compatibility shim.

The canonical implementation has moved to ``pact.examples.foundation.org``.
This module re-exports everything from the new location.
"""

from pact.examples.foundation.org import (  # noqa: F401
    CERTIFICATION_TEAM,
    COMMUNITY_TEAM,
    DEVREL_TEAM,
    FINANCE_TEAM,
    FOUNDATION_BRIDGES,
    FOUNDATION_ORG_CONFIG,
    GOVERNANCE_TEAM,
    GROWTH_DEPARTMENT,
    LEGAL_TEAM,
    MEDIA_DM_TEAM,
    OPERATIONS_DEPARTMENT,
    PARTNERSHIPS_TEAM,
    STANDARDS_GOVERNANCE_DEPARTMENT,
    STANDARDS_TEAM,
    TRAINING_TEAM,
    WEBSITE_TEAM,
    generate_foundation_org,
)
