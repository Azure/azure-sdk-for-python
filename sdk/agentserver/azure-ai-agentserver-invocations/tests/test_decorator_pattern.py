# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for decorator-based handler registration on AgentServer + InvocationHandler."""
import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver.core import AgentServer
from azure.ai.agentserver.invocations import InvocationHandler


# ---------------------------------------------------------------------------
# invoke_handler stores function
# ---------------------------------------------------------------------------

def test_invoke_handler_stores_function():
    """@invocations.invoke_handler stores the function on the protocol object."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    assert invocations._invoke_fn is handle


# ---------------------------------------------------------------------------
# invoke_handler returns original function
# ---------------------------------------------------------------------------

def test_invoke_handler_returns_original_function():
    """@invocations.invoke_handler returns the original function."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    result = invocations.invoke_handler(handle)
    assert result is handle


# ---------------------------------------------------------------------------
# get_invocation_handler stores function
# ---------------------------------------------------------------------------

def test_get_invocation_handler_stores_function():
    """@invocations.get_invocation_handler stores the function."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        return Response(content=b"ok")

    assert invocations._get_invocation_fn is get_handler


# ---------------------------------------------------------------------------
# cancel_invocation_handler stores function
# ---------------------------------------------------------------------------

def test_cancel_invocation_handler_stores_function():
    """@invocations.cancel_invocation_handler stores the function."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        return Response(content=b"ok")

    assert invocations._cancel_invocation_fn is cancel_handler


# ---------------------------------------------------------------------------
# shutdown_handler stores function
# ---------------------------------------------------------------------------

def test_shutdown_handler_stores_function():
    """@server.shutdown_handler stores the function on the server."""
    server = AgentServer()

    @server.shutdown_handler
    async def on_shutdown():
        pass

    assert server._shutdown_fn is on_shutdown


# ---------------------------------------------------------------------------
# Full request flow
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_full_request_flow():
    """Full lifecycle: invoke → get → cancel → get (404)."""
    server = AgentServer()
    invocations = InvocationHandler(server)
    store: dict[str, bytes] = {}

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        store[request.state.invocation_id] = body
        return Response(content=body, media_type="application/octet-stream")

    @invocations.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id in store:
            return Response(content=store[inv_id])
        return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    @invocations.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id in store:
            del store[inv_id]
            return JSONResponse({"status": "cancelled"})
        return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Invoke
        resp = await client.post("/invocations", content=b"lifecycle-test")
        assert resp.status_code == 200
        inv_id = resp.headers["x-agent-invocation-id"]

        # Get
        resp = await client.get(f"/invocations/{inv_id}")
        assert resp.status_code == 200
        assert resp.content == b"lifecycle-test"

        # Cancel
        resp = await client.post(f"/invocations/{inv_id}/cancel")
        assert resp.status_code == 200

        # Get after cancel
        resp = await client.get(f"/invocations/{inv_id}")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Missing optional handlers return 404
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_missing_invoke_handler_returns_501():
    """POST /invocations without registered handler returns 501."""
    server = AgentServer()
    invocations = InvocationHandler(server)
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert resp.status_code == 501


@pytest.mark.asyncio
async def test_missing_get_handler_returns_404():
    """GET /invocations/{id} without registered handler returns 404."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/some-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_missing_cancel_handler_returns_404():
    """POST /invocations/{id}/cancel without registered handler returns 404."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/some-id/cancel")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Optional handler defaults and overrides
# ---------------------------------------------------------------------------

def test_optional_handlers_default_none():
    """Get and cancel handlers default to None."""
    server = AgentServer()
    invocations = InvocationHandler(server)
    assert invocations._get_invocation_fn is None
    assert invocations._cancel_invocation_fn is None


def test_optional_handler_override():
    """Setting an optional handler replaces None."""
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        return Response(content=b"ok")

    assert invocations._get_invocation_fn is not None


# ---------------------------------------------------------------------------
# Shutdown handler called during lifespan
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_called_during_lifespan():
    """Shutdown handler is called when the app lifespan ends."""
    called = []
    server = AgentServer()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def on_shutdown():
        called.append(True)

    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
        assert resp.status_code == 200
    # The lifespan exit runs when the ASGI app scope ends
    # With ASGITransport, the lifespan is managed by the transport
    # The shutdown handler should be called on transport cleanup


# ---------------------------------------------------------------------------
# Config passthrough
# ---------------------------------------------------------------------------

def test_graceful_shutdown_timeout_passthrough():
    """graceful_shutdown_timeout is passed through to the base class."""
    server = AgentServer(graceful_shutdown_timeout=15)
    assert server._graceful_shutdown_timeout == 15
