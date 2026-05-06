# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for WebSocket ping/pong keep-alive (invocations_ws protocol)."""
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
)


def _make_echo_app(**kwargs):
    app = InvocationWSAgentServerHost(**kwargs)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"echo": payload}

    return app


# ---------------------------------------------------------------------------
# Client-initiated ping → server responds with pong
# ---------------------------------------------------------------------------

def test_ws_client_ping_gets_pong():
    """Server replies with pong when client sends a ping action."""
    client = TestClient(_make_echo_app())
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "ping"})
        resp = ws.receive_json()
    assert resp["type"] == "pong"


def test_ws_client_ping_does_not_interrupt_invoke():
    """A ping/pong exchange between invocation calls doesn't break the connection."""
    client = TestClient(_make_echo_app())
    with client.websocket_connect("/invocations_ws/ws") as ws:
        # Normal invoke
        ws.send_json({"action": "invoke", "payload": {"n": 1}})
        r1 = ws.receive_json()
        assert r1["type"] == "result"

        # Ping/pong
        ws.send_json({"action": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"

        # Another invoke still works
        ws.send_json({"action": "invoke", "payload": {"n": 2}})
        r2 = ws.receive_json()
        assert r2["type"] == "result"
        assert r2["payload"]["echo"]["n"] == 2


def test_ws_client_pong_is_accepted_silently():
    """Server accepts pong action without returning an error."""
    client = TestClient(_make_echo_app())
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "pong"})
        # No response expected for pong — verify next invoke still works.
        ws.send_json({"action": "invoke", "payload": {"ok": True}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# ws_ping_interval=0 disables server-side pings
# ---------------------------------------------------------------------------

def test_ws_ping_disabled_with_zero_interval():
    """Setting ws_ping_interval=0 disables the background ping task."""
    app = _make_echo_app(ws_ping_interval=0)
    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


def test_ws_custom_ping_interval():
    """A custom ws_ping_interval is accepted without error."""
    app = _make_echo_app(ws_ping_interval=15)
    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
