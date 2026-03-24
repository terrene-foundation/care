# Copyright 2026 Terrene Foundation
# Licensed under the Apache License, Version 2.0
"""Integration tests for the PACT API server.

Tests the FastAPI server with real seeded data (no mocks). Validates
endpoint behavior, response structure, authentication enforcement,
and data consistency using httpx.AsyncClient with ASGITransport.

Tier 2 integration tests — real components, no mocking.
"""

from __future__ import annotations

import httpx

from tests.integration.conftest import TEST_API_TOKEN

# ---------------------------------------------------------------------------
# Health & Readiness
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Test the /health endpoint returns service status."""

    async def test_health_returns_200(self, client: httpx.AsyncClient):
        """GET /health returns 200 with healthy status."""
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert body["service"] == "pact"

    async def test_health_returns_json_content_type(self, client: httpx.AsyncClient):
        """GET /health returns application/json content type."""
        response = await client.get("/health")
        assert "application/json" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------


class TestTeamsEndpoint:
    """Test the /api/v1/teams endpoint with seeded team data."""

    async def test_list_teams_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/teams returns 200 with ok status."""
        response = await client.get("/api/v1/teams")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_list_teams_returns_seeded_teams(self, client: httpx.AsyncClient):
        """GET /api/v1/teams returns all 4 seeded teams."""
        response = await client.get("/api/v1/teams")
        body = response.json()
        teams = body["data"]["teams"]
        # Seed data creates 4 teams: dm-team, governance-team, community-team, standards-team
        assert len(teams) == 4
        assert "dm-team" in teams
        assert "governance-team" in teams
        assert "community-team" in teams
        assert "standards-team" in teams

    async def test_teams_are_sorted(self, client: httpx.AsyncClient):
        """GET /api/v1/teams returns teams in sorted order."""
        response = await client.get("/api/v1/teams")
        body = response.json()
        teams = body["data"]["teams"]
        assert teams == sorted(teams)


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


class TestAgentsEndpoint:
    """Test the /api/v1/teams/{team_id}/agents endpoint with seeded data."""

    async def test_list_agents_for_dm_team(self, client: httpx.AsyncClient):
        """GET /api/v1/teams/dm-team/agents returns DM team agents."""
        response = await client.get("/api/v1/teams/dm-team/agents")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        agents = body["data"]["agents"]
        # DM team has 5 agents in seed data
        assert len(agents) >= 3, f"Expected at least 3 agents in dm-team, got {len(agents)}"
        agent_ids = [a["agent_id"] for a in agents]
        assert "dm-team-lead" in agent_ids

    async def test_list_agents_for_governance_team(self, client: httpx.AsyncClient):
        """GET /api/v1/teams/governance-team/agents returns governance agents."""
        response = await client.get("/api/v1/teams/governance-team/agents")
        assert response.status_code == 200
        body = response.json()
        agents = body["data"]["agents"]
        agent_ids = [a["agent_id"] for a in agents]
        assert "policy-reviewer" in agent_ids
        assert "compliance-checker" in agent_ids

    async def test_agent_response_structure(self, client: httpx.AsyncClient):
        """Each agent in the response has the expected fields."""
        response = await client.get("/api/v1/teams/dm-team/agents")
        body = response.json()
        agents = body["data"]["agents"]
        assert len(agents) > 0, "Expected at least one agent in dm-team"
        for agent in agents:
            assert "agent_id" in agent, f"Missing 'agent_id' in agent: {agent}"
            assert "name" in agent, f"Missing 'name' in agent: {agent}"
            assert "role" in agent, f"Missing 'role' in agent: {agent}"
            assert "posture" in agent, f"Missing 'posture' in agent: {agent}"
            assert "status" in agent, f"Missing 'status' in agent: {agent}"

    async def test_nonexistent_team_returns_empty_agents(self, client: httpx.AsyncClient):
        """GET /api/v1/teams/nonexistent/agents returns empty list, not error."""
        response = await client.get("/api/v1/teams/nonexistent-team/agents")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["data"]["agents"] == []


# ---------------------------------------------------------------------------
# Verification Stats
# ---------------------------------------------------------------------------


class TestVerificationStatsEndpoint:
    """Test the /api/v1/verification/stats endpoint with seeded stats."""

    async def test_verification_stats_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/verification/stats returns 200 with ok status."""
        response = await client.get("/api/v1/verification/stats")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_verification_stats_has_all_levels(self, client: httpx.AsyncClient):
        """Verification stats include all four verification gradient levels."""
        response = await client.get("/api/v1/verification/stats")
        body = response.json()
        data = body["data"]
        # PACT defines 4 verification levels — returned at top level of data
        for level in ["AUTO_APPROVED", "FLAGGED", "HELD", "BLOCKED"]:
            assert level in data, f"Missing verification level '{level}' in data: {data}"

    async def test_verification_stats_are_non_zero(self, client: httpx.AsyncClient):
        """Seeded verification stats have non-zero total counts."""
        response = await client.get("/api/v1/verification/stats")
        body = response.json()
        data = body["data"]
        # The API returns a 'total' field alongside the individual levels
        assert "total" in data, f"Missing 'total' field in verification stats: {data}"
        assert data["total"] > 0, (
            f"Expected non-zero total verification stats, got {data['total']}. Data: {data}"
        )


# ---------------------------------------------------------------------------
# Held Actions
# ---------------------------------------------------------------------------


class TestHeldActionsEndpoint:
    """Test the /api/v1/held-actions endpoint with seeded held actions."""

    async def test_held_actions_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/held-actions returns 200 with ok status."""
        response = await client.get("/api/v1/held-actions")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_held_actions_returns_seeded_data(self, client: httpx.AsyncClient):
        """GET /api/v1/held-actions returns non-empty list of pending actions."""
        response = await client.get("/api/v1/held-actions")
        body = response.json()
        actions = body["data"]["actions"]
        assert len(actions) > 0, "Expected at least one held action from seed data, got empty list"

    async def test_held_action_structure(self, client: httpx.AsyncClient):
        """Each held action has required fields from the seed data."""
        response = await client.get("/api/v1/held-actions")
        body = response.json()
        actions = body["data"]["actions"]
        assert len(actions) > 0
        for action in actions:
            assert "action_id" in action, f"Missing 'action_id' in: {action}"
            assert "agent_id" in action, f"Missing 'agent_id' in: {action}"
            assert "action" in action, f"Missing 'action' in: {action}"
            assert "reason" in action, f"Missing 'reason' in: {action}"


# ---------------------------------------------------------------------------
# Bearer Token Authentication
# ---------------------------------------------------------------------------


class TestBearerTokenAuth:
    """Test that bearer token auth rejects requests without valid token."""

    async def test_teams_without_token_returns_401(self, auth_client: httpx.AsyncClient):
        """GET /api/v1/teams without bearer token returns 401."""
        response = await auth_client.get("/api/v1/teams")
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated request, got {response.status_code}"
        )

    async def test_teams_with_invalid_token_returns_401(self, auth_client: httpx.AsyncClient):
        """GET /api/v1/teams with wrong bearer token returns 401."""
        response = await auth_client.get(
            "/api/v1/teams",
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert response.status_code == 401

    async def test_teams_with_valid_token_returns_200(self, auth_client: httpx.AsyncClient):
        """GET /api/v1/teams with correct bearer token returns 200."""
        response = await auth_client.get(
            "/api/v1/teams",
            headers={"Authorization": f"Bearer {TEST_API_TOKEN}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_held_actions_without_token_returns_401(self, auth_client: httpx.AsyncClient):
        """GET /api/v1/held-actions without token returns 401."""
        response = await auth_client.get("/api/v1/held-actions")
        assert response.status_code == 401

    async def test_verification_stats_without_token_returns_401(
        self, auth_client: httpx.AsyncClient
    ):
        """GET /api/v1/verification/stats without token returns 401."""
        response = await auth_client.get("/api/v1/verification/stats")
        assert response.status_code == 401

    async def test_health_endpoint_does_not_require_token(self, auth_client: httpx.AsyncClient):
        """GET /health does not require authentication (public endpoint)."""
        response = await auth_client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Trust Chains
# ---------------------------------------------------------------------------


class TestTrustChainsEndpoint:
    """Test the /api/v1/trust-chains endpoint with seeded data."""

    async def test_trust_chains_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/trust-chains returns 200."""
        response = await client.get("/api/v1/trust-chains")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


class TestWorkspacesEndpoint:
    """Test the /api/v1/workspaces endpoint with seeded workspaces."""

    async def test_workspaces_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/workspaces returns 200 with workspace data."""
        response = await client.get("/api/v1/workspaces")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_workspaces_contains_seeded_data(self, client: httpx.AsyncClient):
        """GET /api/v1/workspaces returns non-empty workspace list."""
        response = await client.get("/api/v1/workspaces")
        body = response.json()
        workspaces = body["data"]["workspaces"]
        assert len(workspaces) > 0, "Expected at least one workspace from seed data"


# ---------------------------------------------------------------------------
# Bridges
# ---------------------------------------------------------------------------


class TestBridgesEndpoint:
    """Test the /api/v1/bridges endpoint with seeded bridge data."""

    async def test_bridges_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/bridges returns 200 with bridge data."""
        response = await client.get("/api/v1/bridges")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_bridges_contains_seeded_data(self, client: httpx.AsyncClient):
        """GET /api/v1/bridges returns non-empty bridge list."""
        response = await client.get("/api/v1/bridges")
        body = response.json()
        bridges = body["data"]["bridges"]
        assert len(bridges) > 0, "Expected at least one bridge from seed data"


# ---------------------------------------------------------------------------
# Cost Report
# ---------------------------------------------------------------------------


class TestCostReportEndpoint:
    """Test the /api/v1/cost/report endpoint with seeded cost data."""

    async def test_cost_report_returns_200(self, client: httpx.AsyncClient):
        """GET /api/v1/cost/report returns 200."""
        response = await client.get("/api/v1/cost/report")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_cost_report_has_spend_data(self, client: httpx.AsyncClient):
        """GET /api/v1/cost/report returns non-zero spend from seed data."""
        response = await client.get("/api/v1/cost/report")
        body = response.json()
        report = body["data"]
        assert "total_cost" in report, f"Missing 'total_cost' in report: {report}"
        assert float(report["total_cost"]) > 0, (
            f"Expected non-zero total cost from seed data, got {report['total_cost']}"
        )
