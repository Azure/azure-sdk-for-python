# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for session ID resolution over WebSocket."""
import os
import uuid
from unittest.mock import patch

from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationAgentServerHost,
    InvocationContext,
)


# ---------------------------------------------------------------------------
# Invoke response has session_id
# ---------------------------------------------------------------------------

def test_invoke_has_session_id(echo_client):
    """Invoke response includes session_id."""
    with echo_client.websocket_connect("/invocations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "session_id" in resp
    uuid.UUID(resp["session_id"])


# ---------------------------------------------------------------------------
# Invoke with session_id in message uses that value
# ---------------------------------------------------------------------------

def test_invoke_with_session_id_in_message():
    """Invoke with session_id in message uses that value."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: InvocationContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/invocations/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "session_id": "my-custom-session",
            "payload": {},
        })
        resp = ws.receive_json()
    assert resp["session_id"] == "my-custom-session"


# ---------------------------------------------------------------------------
# Invoke with env var
# ---------------------------------------------------------------------------

def test_invoke_uses_env_var():
    """Invoke uses FOUNDRY_AGENT_SESSION_ID env var when no session_id in message."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: InvocationContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with patch.dict(os.environ, {"FOUNDRY_AGENT_SESSION_ID": "env-session"}):
        with client.websocket_connect("/invocations/ws") as ws:
            ws.send_json({"action": "invoke", "payload": {}})
            resp = ws.receive_json()
    assert resp["session_id"] == "env-session"


# ---------------------------------------------------------------------------
# get_invocation does NOT include session_id (not part of get protocol)
# ---------------------------------------------------------------------------

def test_get_invocation_no_session_id(async_storage_client):
    """get_invocation response does not include session_id."""
    with async_storage_client.websocket_connect("/invocations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
        get_resp = ws.receive_json()
    assert get_resp["type"] == "result"
    assert "session_id" not in get_resp


# ---------------------------------------------------------------------------
# cancel_invocation does NOT include session_id
# ---------------------------------------------------------------------------

def test_cancel_invocation_no_session_id(async_storage_client):
    """cancel_invocation response does not include session_id."""
    with async_storage_client.websocket_connect("/invocations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        cancel_resp = ws.receive_json()
    assert cancel_resp["type"] == "result"
    assert "session_id" not in cancel_resp
