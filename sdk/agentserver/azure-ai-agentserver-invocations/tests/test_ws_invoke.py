# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the WebSocket request/response lifecycle on ``/invocations_ws``.

Parity with :mod:`tests.test_invoke` — covers the happy path (accept, echo,
clean close), the unhappy path (handler exception → 1011), and the
WebSocket-only bidirectional streaming property.
"""
import asyncio

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants

from conftest import _make_echo_ws_app, _make_failing_ws_app


# ---------------------------------------------------------------------------
# Accept happens automatically
# ---------------------------------------------------------------------------

def test_ws_sdk_accepts_connection_before_handler_runs():
    """The SDK calls ``websocket.accept()`` before invoking the user handler.

    The handler in this test never calls ``accept`` itself; the connection
    must still be usable, which proves the SDK accepted it on the user's
    behalf.
    """
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.send_text("ready")

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_text() == "ready"


# ---------------------------------------------------------------------------
# Echo round-trip
# ---------------------------------------------------------------------------

def test_ws_echo_round_trip():
    """End-to-end: send a frame, receive it echoed back."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hello")
        assert ws.receive_text() == "hello"
        ws.send_text("world")
        assert ws.receive_text() == "world"


def test_ws_multiple_frames_per_connection():
    """Multiple frames flow through one connection (parity with streaming chunks)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        for i in range(5):
            await websocket.send_text(f"chunk-{i}")

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        for i in range(5):
            assert ws.receive_text() == f"chunk-{i}"


# ---------------------------------------------------------------------------
# Close codes
# ---------------------------------------------------------------------------

def test_ws_handler_exception_maps_to_close_code_1011():
    """Uncaught handler exceptions must surface as RFC 6455 close code 1011."""
    app = _make_failing_ws_app()
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("trigger")
            # Server closes after the handler raises; receiving forces
            # the close frame to surface as WebSocketDisconnect.
            ws.receive_text()

    assert excinfo.value.code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR
    assert excinfo.value.code == 1011


def test_ws_clean_return_uses_close_code_1000():
    """A handler that returns normally yields a 1000 (normal) close code."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        # Receive once, then return — SDK closes cleanly.
        await websocket.receive_text()

    client = TestClient(app)
    # Starlette TestClient surfaces *any* close (including a clean 1000) via
    # ``WebSocketDisconnect`` when ``receive_text()`` is called after the
    # server sends a close frame — this is the documented client API for
    # observing the close, not an indication of error.
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("done")
            ws.receive_text()  # Forces the close to surface.

    assert excinfo.value.code == InvocationsWSConstants.CLOSE_NORMAL


# ---------------------------------------------------------------------------
# Bidirectional streaming (WebSocket-only feature)
# ---------------------------------------------------------------------------

def test_ws_bidirectional_concurrent_send_receive():
    """Reader and writer coroutines run concurrently on the same socket."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        async def reader():
            async for msg in websocket.iter_text():
                if msg == "bye":
                    return

        async def writer():
            for i in range(3):
                await websocket.send_text(f"server-{i}")
                await asyncio.sleep(0)  # yield to reader

        # Run reader + writer in parallel — the defining property of WS.
        await asyncio.gather(reader(), writer())

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        # Mix inbound and outbound frames to prove they're not lock-stepped.
        ws.send_text("client-a")
        assert ws.receive_text() == "server-0"
        ws.send_text("client-b")
        assert ws.receive_text() == "server-1"
        assert ws.receive_text() == "server-2"
        ws.send_text("bye")
