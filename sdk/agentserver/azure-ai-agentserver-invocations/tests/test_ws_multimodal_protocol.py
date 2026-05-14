# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for multi-modality payloads sent through ``/invocations_ws``.

Parity with :mod:`tests.test_multimodal_protocol` — covers binary frames,
text frames (unicode + large), and JSON frames over WebSocket.
"""
import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from conftest import _make_echo_ws_app


# ---------------------------------------------------------------------------
# Binary frames
# ---------------------------------------------------------------------------

def test_ws_binary_frame_round_trip():
    """Binary frames round-trip without corruption (parity with test_binary_payload)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        data = await websocket.receive_bytes()
        await websocket.send_bytes(data)

    client = TestClient(app)
    payload = bytes(range(256))
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_bytes(payload)
        assert ws.receive_bytes() == payload


# ---------------------------------------------------------------------------
# Text frames — unicode and large payloads
# ---------------------------------------------------------------------------

def test_ws_unicode_text_round_trip():
    """Unicode text frames are preserved (parity with test_unicode_payload)."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    text = "Hello, 世界! 🌍 — naïve façade"
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text(text)
        assert ws.receive_text() == text


@pytest.mark.slow
def test_ws_large_text_frame_round_trip():
    """A ~1 MB text frame round-trips successfully (parity with test_large_payload)."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    payload = "x" * (1024 * 1024)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text(payload)
        assert ws.receive_text() == payload


# ---------------------------------------------------------------------------
# JSON frames (``send_json`` / ``receive_json``)
# ---------------------------------------------------------------------------

def test_ws_json_frame_round_trip():
    """``send_json`` / ``receive_json`` round-trip JSON payloads."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        msg = await websocket.receive_json()
        await websocket.send_json({"echo": msg})

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_json({"hello": "world", "n": 42})
        assert ws.receive_json() == {"echo": {"hello": "world", "n": 42}}
