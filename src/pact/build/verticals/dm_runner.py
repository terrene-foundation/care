# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""DMTeamRunner — backward-compatibility shim.

The canonical implementation has moved to ``pact.examples.foundation.dm_runner``.
This module re-exports everything from the new location.
"""

from pact.examples.foundation.dm_runner import DMTeamRunner  # noqa: F401
