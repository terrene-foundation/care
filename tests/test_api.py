"""Tests for the API server."""

import pytest
from fastapi.testclient import TestClient

from care.api.server import app


@pytest.fixture
def client():
    """Create a test client with lifespan context."""
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_session(client):
    response = client.post("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "welcome_message" in data
    assert data["state"] == "welcome"


def test_get_session(client):
    # Create first
    create_resp = client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    # Get
    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id


def test_get_nonexistent_session(client):
    response = client.get("/api/sessions/nonexistent")
    assert response.status_code == 404


def test_config_before_complete(client):
    create_resp = client.post("/api/sessions")
    session_id = create_resp.json()["session_id"]

    response = client.get(f"/api/sessions/{session_id}/config")
    assert response.status_code == 400
