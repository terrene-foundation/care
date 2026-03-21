# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Common fixtures for governance layer tests."""

from __future__ import annotations

import pytest


@pytest.fixture
def sample_org_id() -> str:
    """A sample organization ID for governance tests."""
    return "test-org-001"


@pytest.fixture
def sample_department_name() -> str:
    """A sample department name for governance tests."""
    return "Engineering"


@pytest.fixture
def sample_team_name() -> str:
    """A sample team name for governance tests."""
    return "Backend"


@pytest.fixture
def sample_role_name() -> str:
    """A sample role name for governance tests."""
    return "developer"
