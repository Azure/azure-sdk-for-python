# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for route registration and basic endpoint behavior."""
import uuid

import pytest


@pytest.mark.asyncio
async def test_post_invocations_returns_200(echo_client):
    """POST /invocations with valid body returns 200."""
    resp = await echo_client.post("/invocations", content=b'{"hello":"world"}')
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_post_invocations_returns_invocation_id_header(echo_client):
    """Response includes x-agent-invocation-id header in UUID format."""
    resp = await echo_client.post("/invocations", content=b'{"hello":"world"}')
    invocation_id = resp.headers.get("x-agent-invocation-id")
    assert invocation_id is not None
    # Validate UUID format
    uuid.UUID(invocation_id)


@pytest.mark.asyncio
async def test_get_openapi_spec_returns_404_when_not_set(echo_client):
    """GET /invocations/docs/openapi.json returns 404 if no spec registered."""
    resp = await echo_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_openapi_spec_returns_spec(validated_client):
    """GET /invocations/docs/openapi.json returns registered spec as JSON."""
    resp = await validated_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["openapi"] == "3.0.0"
    assert "/invocations" in data["paths"]


@pytest.mark.asyncio
async def test_get_invocation_returns_404_default(echo_client):
    """GET /invocations/{id} returns 404 when not overridden."""
    resp = await echo_client.get(f"/invocations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_invocation_returns_404_default(echo_client):
    """POST /invocations/{id}/cancel returns 404 when not overridden."""
    resp = await echo_client.post(f"/invocations/{uuid.uuid4()}/cancel")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unknown_route_returns_404(echo_client):
    """GET /unknown returns 404."""
    resp = await echo_client.get("/unknown")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# _resolve_port tests
# ---------------------------------------------------------------------------


class TestResolvePort:
    """Unit tests for resolve_port."""

    def test_explicit_port_wins(self):
        """Explicit port argument takes precedence over everything."""
        from azure.ai.agentserver.server._config import resolve_port
        assert resolve_port(9090) == 9090

    def test_env_var_used_when_no_explicit(self, monkeypatch):
        """AGENT_SERVER_PORT env var is used when no explicit port given."""
        from azure.ai.agentserver.server._config import resolve_port
        monkeypatch.setenv("AGENT_SERVER_PORT", "7777")
        assert resolve_port(None) == 7777

    def test_default_port_when_nothing_set(self, monkeypatch):
        """Falls back to 8088 when no explicit port and no env var."""
        from azure.ai.agentserver.server._config import resolve_port
        monkeypatch.delenv("AGENT_SERVER_PORT", raising=False)
        assert resolve_port(None) == 8088

    def test_invalid_env_var_raises(self, monkeypatch):
        """Non-numeric AGENT_SERVER_PORT env var raises ValueError."""
        from azure.ai.agentserver.server._config import resolve_port
        monkeypatch.setenv("AGENT_SERVER_PORT", "not_a_number")
        with pytest.raises(ValueError, match="AGENT_SERVER_PORT"):
            resolve_port(None)

    def test_non_int_explicit_port_raises(self):
        """Passing a non-integer port raises ValueError."""
        from azure.ai.agentserver.server._config import resolve_port
        with pytest.raises(ValueError, match="expected an integer"):
            resolve_port("sss")  # type: ignore[arg-type]

    def test_port_out_of_range_raises(self):
        """Port outside 1-65535 raises ValueError."""
        from azure.ai.agentserver.server._config import resolve_port
        with pytest.raises(ValueError, match="1-65535"):
            resolve_port(0)
        with pytest.raises(ValueError, match="1-65535"):
            resolve_port(70000)

    def test_env_var_port_out_of_range_raises(self, monkeypatch):
        """AGENT_SERVER_PORT outside 1-65535 raises ValueError."""
        from azure.ai.agentserver.server._config import resolve_port
        monkeypatch.setenv("AGENT_SERVER_PORT", "0")
        with pytest.raises(ValueError, match="1-65535"):
            resolve_port(None)
