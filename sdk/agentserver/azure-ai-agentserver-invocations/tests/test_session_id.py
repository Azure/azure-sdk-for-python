# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for session ID resolution and x-agent-session-id header."""
import os
import uuid
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from azure.ai.agentserver.invocations._constants import InvocationConstants


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_session_id_header_constant():
    """SESSION_ID_HEADER constant is correct."""
    assert InvocationConstants.SESSION_ID_HEADER == "x-agent-session-id"


# ---------------------------------------------------------------------------
# POST /invocations response has x-agent-session-id header
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_has_session_id_header(echo_client):
    """POST /invocations response includes x-agent-session-id header."""
    resp = await echo_client.post("/invocations", content=b"test")
    assert "x-agent-session-id" in resp.headers
    # Auto-generated should be a valid UUID
    uuid.UUID(resp.headers["x-agent-session-id"])


# ---------------------------------------------------------------------------
# POST /invocations with query param uses that value
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_with_query_param():
    """POST /invocations with agent_session_id query param uses that value."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations?agent_session_id=my-custom-session",
            content=b"test",
        )
    assert resp.headers["x-agent-session-id"] == "my-custom-session"


# ---------------------------------------------------------------------------
# POST /invocations with env var
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_post_invocations_uses_env_var():
    """POST /invocations uses FOUNDRY_AGENT_SESSION_ID env var when no query param."""
    with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "env-session"}):
        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            return Response(content=b"ok")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"test")
    assert resp.headers["x-agent-session-id"] == "env-session"


# ---------------------------------------------------------------------------
# GET /invocations/{id} does NOT have x-agent-session-id header
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocation_no_session_id_header(async_storage_client):
    """GET /invocations/{id} does NOT include x-agent-session-id."""
    resp = await async_storage_client.post("/invocations", content=b"data")
    inv_id = resp.headers["x-agent-invocation-id"]

    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 200
    assert "x-agent-session-id" not in get_resp.headers


# ---------------------------------------------------------------------------
# POST /invocations/{id}/cancel does NOT have x-agent-session-id header
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_invocation_no_session_id_header(async_storage_client):
    """POST /invocations/{id}/cancel does NOT include x-agent-session-id."""
    resp = await async_storage_client.post("/invocations", content=b"data")
    inv_id = resp.headers["x-agent-invocation-id"]

    cancel_resp = await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    assert cancel_resp.status_code == 200
    assert "x-agent-session-id" not in cancel_resp.headers
