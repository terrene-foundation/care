# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""DM Team — backward-compatibility shim.

The canonical implementation has moved to ``pact.examples.foundation.dm_team``.
This module re-exports everything from the new location.
"""

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
