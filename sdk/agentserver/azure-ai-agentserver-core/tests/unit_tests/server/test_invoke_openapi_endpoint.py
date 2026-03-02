# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Unit tests for the ``GET /invoke/docs/openapi.json`` endpoint on :class:`FoundryCBAgent`."""
from unittest.mock import MagicMock, patch

import httpx
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_agent(openapi_spec=None):
    """Return a concrete :class:`FoundryCBAgent` with Azure dependencies patched out.

    :param openapi_spec: Value returned by ``agent_openapi_spec``. ``None`` (the default)
        exercises the default implementation and causes the endpoint to respond with 404.
        Pass a :class:`dict` to exercise the 200 success path.
    :type openapi_spec: dict or None
    :return: A :class:`FoundryCBAgent` subclass instance whose ``.app`` is ready for testing.
    """
    from azure.ai.agentserver.core.server.base import FoundryCBAgent

    class _TestAgent(FoundryCBAgent):
        async def agent_run(self, context):  # pragma: no cover
            raise NotImplementedError("agent_run is not exercised in these tests")

        def agent_openapi_spec(self):
            return openapi_spec  # None → 404; dict → 200

    with (
        patch("azure.ai.agentserver.core.server.base.AgentServerContext"),
        patch("azure.ai.agentserver.core.server.base.create_tool_runtime"),
        patch("azure.ai.agentserver.core.tools.UserInfoContextMiddleware.install"),
    ):
        return _TestAgent(credentials=MagicMock(), project_endpoint="http://fake-endpoint")


def _client(agent) -> httpx.AsyncClient:
    """Create an ``httpx.AsyncClient`` wired to the agent's ASGI app."""
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
        base_url="http://test",
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openapi_returns_404_when_not_overridden():
    """GET /invoke/docs/openapi.json — default implementation returns 404."""
    agent = _build_agent(openapi_spec=None)
    async with _client(agent) as client:
        response = await client.get("/invoke/docs/openapi.json")
    assert response.status_code == 404
    assert response.json() == {"error": "OpenAPI spec not available"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openapi_returns_spec_when_overridden():
    """GET /invoke/docs/openapi.json — overridden method returns 200 with the spec dict."""
    spec = {"openapi": "3.1.0", "info": {"title": "My Agent", "version": "1.0.0"}}
    agent = _build_agent(openapi_spec=spec)
    async with _client(agent) as client:
        response = await client.get("/invoke/docs/openapi.json")
    assert response.status_code == 200
    assert response.json() == spec


@pytest.mark.unit
@pytest.mark.asyncio
async def test_openapi_response_content_type_is_json():
    """GET /invoke/docs/openapi.json — response Content-Type is application/json."""
    spec = {"openapi": "3.1.0", "info": {"title": "My Agent", "version": "1.0.0"}}
    agent = _build_agent(openapi_spec=spec)
    async with _client(agent) as client:
        response = await client.get("/invoke/docs/openapi.json")
    assert "application/json" in response.headers["content-type"]
