# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for graceful shutdown with WebsocketAgentServerHost."""
import asyncio
import logging

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_server_with_shutdown(**kwargs) -> tuple[WebsocketAgentServerHost, list]:
    """Create WebsocketAgentServerHost with a tracked shutdown handler."""
    server = WebsocketAgentServerHost(**kwargs)
    calls: list[str] = []

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

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
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    assert app._shutdown_fn is None


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
    completed = await _drive_lifespan(server)
    assert completed
    assert "shutdown" in calls


# ---------------------------------------------------------------------------
# Shutdown handler timeout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_timeout(caplog):
    """Shutdown handler that exceeds timeout is warned about."""
    server = WebsocketAgentServerHost(graceful_shutdown_timeout=1)
    calls: list[str] = []

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    @server.shutdown_handler
    async def on_shutdown():
        await asyncio.sleep(10)
        calls.append("completed")

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        await _drive_lifespan(server)

    assert "completed" not in calls
    assert any("did not complete" in r.message.lower() or "timeout" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Shutdown handler exception
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_shutdown_handler_exception(caplog):
    """Shutdown handler that raises is caught and logged."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    @app.shutdown_handler
    async def on_shutdown():
        raise RuntimeError("shutdown exploded")

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        await _drive_lifespan(app)

    assert any("on_shutdown" in r.message.lower() or "error" in r.message.lower() for r in caplog.records)


# ---------------------------------------------------------------------------
# Graceful shutdown timeout config
# ---------------------------------------------------------------------------

def test_default_graceful_shutdown_timeout():
    """Default graceful shutdown timeout is 30 seconds."""
    app = WebsocketAgentServerHost()
    assert app._graceful_shutdown_timeout == 30


def test_custom_graceful_shutdown_timeout():
    """Custom graceful_shutdown_timeout is stored."""
    server = WebsocketAgentServerHost(graceful_shutdown_timeout=60)
    assert server._graceful_shutdown_timeout == 60


def test_zero_graceful_shutdown_timeout():
    """Zero timeout disables the drain period."""
    server = WebsocketAgentServerHost(graceful_shutdown_timeout=0)
    assert server._graceful_shutdown_timeout == 0


# ---------------------------------------------------------------------------
# Health endpoint accessible during normal operation
# ---------------------------------------------------------------------------

def test_health_endpoint_during_operation():
    """GET /readiness returns 200 during normal operation."""
    server, _ = _make_server_with_shutdown()
    client = TestClient(server)
    resp = client.get("/readiness")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


# ---------------------------------------------------------------------------
# No shutdown handler is no-op
# ---------------------------------------------------------------------------

def test_no_shutdown_handler_is_noop():
    """Without a shutdown handler, WebSocket and lifespan work fine."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
        assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Multiple requests before shutdown
# ---------------------------------------------------------------------------

def test_multiple_requests_before_shutdown():
    """Multiple requests can be served on the same WebSocket connection."""
    server, _ = _make_server_with_shutdown()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        for i in range(5):
            ws.send_json({"action": "invoke", "payload": {"idx": i}})
            resp = ws.receive_json()
            assert resp["type"] == "result"
