# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for GET /invocations/{id} and POST /invocations/{id}/cancel."""
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.invocations import InvocationAgentServerHost



# ---------------------------------------------------------------------------
# GET after invoke
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_after_invoke_returns_stored_result(async_storage_client):
    """GET /invocations/{id} after invoke returns the stored result."""
    resp = await async_storage_client.post("/invocations", content=b"stored-data")
    assert resp.status_code == 200
    inv_id = resp.headers["x-agent-invocation-id"]

    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 200
    assert get_resp.content == b"stored-data"


# ---------------------------------------------------------------------------
# GET unknown ID
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_unknown_id_returns_404(async_storage_client):
    """GET /invocations/{unknown} returns 404."""
    resp = await async_storage_client.get("/invocations/unknown-id-12345")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Cancel after invoke
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_after_invoke_returns_cancelled(async_storage_client):
    """POST /invocations/{id}/cancel after invoke returns cancelled status."""
    resp = await async_storage_client.post("/invocations", content=b"cancel-me")
    inv_id = resp.headers["x-agent-invocation-id"]

    cancel_resp = await async_storage_client.post(f"/invocations/{inv_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Cancel unknown ID
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_unknown_id_returns_404(async_storage_client):
    """POST /invocations/{unknown}/cancel returns 404."""
    resp = await async_storage_client.post("/invocations/unknown-id-12345/cancel")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET after cancel
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_after_cancel_returns_404(async_storage_client):
    """GET after cancel returns 404 (data has been removed)."""
    resp = await async_storage_client.post("/invocations", content=b"temp")
    inv_id = resp.headers["x-agent-invocation-id"]
    await async_storage_client.post(f"/invocations/{inv_id}/cancel")

    get_resp = await async_storage_client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# GET error returns 500 (inline InvocationAgentServerHost)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocation_error_returns_500():
    """GET handler raising an exception returns 500."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        raise RuntimeError("get failed")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/some-id")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"


# ---------------------------------------------------------------------------
# Cancel error returns 500 (inline InvocationAgentServerHost)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cancel_invocation_error_returns_500():
    """Cancel handler raising an exception returns 500."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        raise RuntimeError("cancel failed")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
    assert resp.status_code == 500
    assert resp.json()["error"]["code"] == "internal_error"
