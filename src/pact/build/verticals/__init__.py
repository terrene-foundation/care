# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Verticals — backward-compatibility shim.

All domain-specific vertical code has been moved to ``pact.examples.foundation``.
This module re-exports everything from the new location so that existing imports
continue to work.
"""

# Re-export from the canonical location
from pact.examples.foundation.dm_prompts import DM_AGENT_PROMPTS, get_system_prompt  # noqa: F401
from pact.examples.foundation.dm_runner import DMTeamRunner  # noqa: F401
from pact.examples.foundation.dm_team import (  # noqa: F401
    DM_ANALYTICS,
    DM_ANALYTICS_ENVELOPE,
    DM_COMMUNITY_ENVELOPE,
    DM_COMMUNITY_MANAGER,
    DM_CONTENT_CREATOR,
    DM_CONTENT_ENVELOPE,
    DM_LEAD_ENVELOPE,
    DM_SEO_ENVELOPE,
    DM_SEO_SPECIALIST,
    DM_TEAM,
    DM_TEAM_LEAD,
    DM_VERIFICATION_GRADIENT,
    get_dm_team_config,
    validate_dm_team,
)
from pact.examples.foundation.org import (  # noqa: F401
    FOUNDATION_BRIDGES,
    FOUNDATION_ORG_CONFIG,
    generate_foundation_org,
)
