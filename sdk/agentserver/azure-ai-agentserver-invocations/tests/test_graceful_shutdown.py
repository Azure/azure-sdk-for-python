# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for graceful shutdown with AgentHost."""
import asyncio
import logging

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from azure.ai.agentserver.core import AgentHost
from azure.ai.agentserver.invocations import InvocationHandler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_server_with_shutdown(**kwargs) -> tuple[AgentHost, list]:
    """Create AgentHost with a tracked shutdown handler."""
    server = AgentHost(**kwargs)
    invocations = InvocationHandler(server)
    calls: list[str] = []

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def on_shutdown():
        calls.append("shutdown")

    return server, calls


# ---------------------------------------------------------------------------
# Shutdown handler registration
# ---------------------------------------------------------------------------

def test_shutdown_handler_registered():
    """Shutdown handler is stored on the server."""
    server, _ = _make_server_with_shutdown()
    assert server._shutdown_fn is not None


def test_shutdown_handler_not_registered():
    """Without @shutdown_handler, _shutdown_fn is None."""
    server = AgentHost()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    assert server._shutdown_fn is None


# ---------------------------------------------------------------------------
# ASGI lifespan helper
# ---------------------------------------------------------------------------

async def _drive_lifespan(app):
    """Drive a full ASGI lifespan startup+shutdown cycle."""
    scope = {"type": "lifespan"}
    startup_done = asyncio.Event()
    shutdown_done = asyncio.Event()

    async def receive():
        if not startup_done.is_set():
            startup_done.set()
            return {"type": "lifespan.startup"}
        await asyncio.sleep(0)
        return {"type": "lifespan.shutdown"}

    async def send(message):
        if message["type"] == "lifespan.shutdown.complete":
            shutdown_done.set()

    await app(scope, receive, send)
    return shutdown_done.is_set()


# ---------------------------------------------------------------------------
# Shutdown handler called during lifespan
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_called_on_lifespan_exit():
    """Shutdown handler runs when the ASGI lifespan exits."""
    server, calls = _make_server_with_shutdown()

    # Drive the lifespan via raw ASGI protocol
    completed = await _drive_lifespan(server.app)
    assert completed
    assert "shutdown" in calls


# ---------------------------------------------------------------------------
# Shutdown handler timeout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_timeout(caplog):
    """Shutdown handler that exceeds timeout is warned about."""
    server = AgentHost(graceful_shutdown_timeout=1)
    invocations = InvocationHandler(server)
    calls: list[str] = []

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def on_shutdown():
        await asyncio.sleep(10)
        calls.append("completed")

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        await _drive_lifespan(server.app)

    # Shutdown should have been interrupted
    assert "completed" not in calls
    # Logger should have warned about timeout
    assert any("did not complete" in r.message.lower() or "timeout" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Shutdown handler exception
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_exception(caplog):
    """Shutdown handler that raises is caught and logged."""
    server = AgentHost()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    @server.shutdown_handler
    async def on_shutdown():
        raise RuntimeError("shutdown exploded")

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        await _drive_lifespan(server.app)

    # Should have logged the exception
    assert any("on_shutdown" in r.message.lower() or "error" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Graceful shutdown timeout config
# ---------------------------------------------------------------------------

def test_default_graceful_shutdown_timeout():
    """Default graceful shutdown timeout is 30 seconds."""
    server = AgentHost()
    assert server._graceful_shutdown_timeout == 30


def test_custom_graceful_shutdown_timeout():
    """Custom graceful_shutdown_timeout is stored."""
    server = AgentHost(graceful_shutdown_timeout=60)
    assert server._graceful_shutdown_timeout == 60


def test_zero_graceful_shutdown_timeout():
    """Zero timeout disables the drain period."""
    server = AgentHost(graceful_shutdown_timeout=0)
    assert server._graceful_shutdown_timeout == 0


# ---------------------------------------------------------------------------
# Health endpoint accessible during normal operation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_endpoint_during_operation():
    """GET /readiness returns 200 during normal operation."""
    server, _ = _make_server_with_shutdown()
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/readiness")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# No shutdown handler is no-op
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_no_shutdown_handler_is_noop():
    """Without a shutdown handler, lifespan exit succeeds silently."""
    server = AgentHost()
    invocations = InvocationHandler(server)

    @invocations.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
        assert resp.status_code == 200
    # No exception means success


# ---------------------------------------------------------------------------
# Multiple requests before shutdown
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_multiple_requests_before_shutdown():
    """Multiple requests can be served, then shutdown handler runs."""
    server, calls = _make_server_with_shutdown()
    transport = ASGITransport(app=server.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        for i in range(5):
            resp = await client.post("/invocations", content=f"request-{i}".encode())
            assert resp.status_code == 200

    # Drive the lifespan to trigger shutdown
    completed = await _drive_lifespan(server.app)
    assert completed
    assert "shutdown" in calls
