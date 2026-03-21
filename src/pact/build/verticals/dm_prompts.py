# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""DM Prompts — backward-compatibility shim.

The canonical implementation has moved to ``pact.examples.foundation.dm_prompts``.
This module re-exports everything from the new location.
"""

from pact.examples.foundation.dm_prompts import (  # noqa: F401
    DM_AGENT_PROMPTS,
    get_system_prompt,
)
