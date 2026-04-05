# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with InvocationAgentServerHost + InvocationAgentServerHost."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from conftest import SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# POST /invocations returns 200
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_returns_200(echo_client):
    """POST /invocations returns 200 OK."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /invocations returns invocation-id header (UUID)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_returns_uuid_invocation_id(echo_client):
    """POST /invocations returns a valid UUID in x-agent-invocation-id."""
    resp = await echo_client.post("/invocations", content=b"test")
    inv_id = resp.headers["x-agent-invocation-id"]
    parsed = uuid.UUID(inv_id)
    assert str(parsed) == inv_id


# ---------------------------------------------------------------------------
# GET openapi spec returns 404 when not set
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_openapi_spec_returns_404_when_not_set(no_spec_client):
    """GET /invocations/docs/openapi.json returns 404 when no spec registered."""
    resp = await no_spec_client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET openapi spec returns spec when registered
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_openapi_spec_returns_spec_when_registered():
    """GET /invocations/docs/openapi.json returns the spec when registered."""
    app = InvocationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/docs/openapi.json")
    assert resp.status_code == 200
    assert resp.json() == SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# GET /invocations/{id} returns 404 default
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocation_returns_404_default(echo_client):
    """GET /invocations/{id} returns 404 when no get handler registered."""
    resp = await echo_client.get("/invocations/some-id")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /invocations/{id}/cancel returns 404 default
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_invocation_returns_404_default(echo_client):
    """POST /invocations/{id}/cancel returns 404 when no cancel handler."""
    resp = await echo_client.post("/invocations/some-id/cancel")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Unknown route returns 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unknown_route_returns_404(echo_client):
    """Unknown route returns 404."""
    resp = await echo_client.get("/nonexistent")
    assert resp.status_code == 404
