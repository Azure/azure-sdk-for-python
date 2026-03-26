# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the GET /healthy health-check endpoint."""
import pytest
import httpx

from azure.ai.agentserver.core import AgentServer


@pytest.fixture()
def client() -> httpx.AsyncClient:
    agent = AgentServer()
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=agent.app),
        base_url="http://testserver",
    )


@pytest.mark.asyncio
async def test_healthy_returns_200(client: httpx.AsyncClient) -> None:
    """GET /healthy returns 200 with the expected JSON body."""
    resp = await client.get("/healthy")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_healthy_content_type(client: httpx.AsyncClient) -> None:
    """GET /healthy returns application/json content type."""
    resp = await client.get("/healthy")
    assert "application/json" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_healthy_post_returns_405(client: httpx.AsyncClient) -> None:
    """POST /healthy is not allowed — only GET is registered."""
    resp = await client.post("/healthy")
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_old_liveness_endpoint_returns_404(client: httpx.AsyncClient) -> None:
    """The old /liveness endpoint no longer exists."""
    resp = await client.get("/liveness")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_old_readiness_endpoint_returns_404(client: httpx.AsyncClient) -> None:
    """The old /readiness endpoint no longer exists."""
    resp = await client.get("/readiness")
    assert resp.status_code == 404
