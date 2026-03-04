# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for get_invocation and cancel_invocation."""
import json
import uuid

import pytest


@pytest.mark.asyncio
async def test_get_invocation_after_invoke(async_storage_client):
    """Invoke, then GET /invocations/{id} returns stored result."""
    resp = await async_storage_client.post("/invocations", content=b'{"key":"value"}')
    invocation_id = resp.headers["x-agent-invocation-id"]

    get_resp = await async_storage_client.get(f"/invocations/{invocation_id}")
    assert get_resp.status_code == 200
    data = json.loads(get_resp.content)
    assert "echo" in data


@pytest.mark.asyncio
async def test_get_invocation_unknown_id_returns_404(async_storage_client):
    """GET /invocations/{unknown} returns 404."""
    resp = await async_storage_client.get(f"/invocations/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cancel_invocation_after_invoke(async_storage_client):
    """Invoke, then POST /invocations/{id}/cancel returns cancelled status."""
    resp = await async_storage_client.post("/invocations", content=b'{"key":"value"}')
    invocation_id = resp.headers["x-agent-invocation-id"]

    cancel_resp = await async_storage_client.post(f"/invocations/{invocation_id}/cancel")
    assert cancel_resp.status_code == 200
    data = json.loads(cancel_resp.content)
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_invocation_unknown_id_returns_404(async_storage_client):
    """POST /invocations/{unknown}/cancel returns 404."""
    resp = await async_storage_client.post(f"/invocations/{uuid.uuid4()}/cancel")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_after_cancel_returns_404(async_storage_client):
    """Cancel, then get same ID returns 404."""
    resp = await async_storage_client.post("/invocations", content=b'{"key":"value"}')
    invocation_id = resp.headers["x-agent-invocation-id"]

    await async_storage_client.post(f"/invocations/{invocation_id}/cancel")
    get_resp = await async_storage_client.get(f"/invocations/{invocation_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_invocation_error_returns_500():
    """GET /invocations/{id} returns 500 when customer code raises an error."""
    import httpx
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

    from azure.ai.agentserver import AgentServer

    class BuggyGetAgent(AgentServer):
        async def invoke(self, request: Request) -> Response:
            return JSONResponse({})

        async def get_invocation(self, request: Request) -> Response:
            raise RuntimeError("storage unavailable")

    agent = BuggyGetAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/some-id")
        assert resp.status_code == 500
        assert "Internal server error" in resp.json()["error"]


@pytest.mark.asyncio
async def test_cancel_invocation_error_returns_500():
    """POST /invocations/{id}/cancel returns 500 when customer code raises an error."""
    import httpx
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

    from azure.ai.agentserver import AgentServer

    class BuggyCancelAgent(AgentServer):
        async def invoke(self, request: Request) -> Response:
            return JSONResponse({})

        async def cancel_invocation(self, request: Request) -> Response:
            raise RuntimeError("cancel failed")

    agent = BuggyCancelAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
        assert resp.status_code == 500
        assert "Internal server error" in resp.json()["error"]
