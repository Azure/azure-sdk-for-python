# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the invoke action over WebSocket (invocations_ws protocol)."""
import uuid

from azure.ai.agentserver.invocations import InvocationWSContext


# ---------------------------------------------------------------------------
# Echo payload
# ---------------------------------------------------------------------------

def test_ws_invoke_echo_payload(ws_echo_client):
    """Invoke echoes the payload back."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"msg": "hello world"}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["echo"]["msg"] == "hello world"


# ---------------------------------------------------------------------------
# IDs
# ---------------------------------------------------------------------------

def test_ws_invoke_returns_invocation_id(ws_echo_client):
    """Response includes a valid UUID invocation_id."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "invocation_id" in resp
    uuid.UUID(resp["invocation_id"])


def test_ws_invoke_returns_session_id(ws_echo_client):
    """Response includes a valid UUID session_id."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "session_id" in resp
    uuid.UUID(resp["session_id"])


def test_ws_invoke_unique_invocation_ids(ws_echo_client):
    """Each invoke gets a unique invocation ID."""
    ids = set()
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        for _ in range(5):
            ws.send_json({"action": "invoke", "payload": {}})
            resp = ws.receive_json()
            ids.add(resp["invocation_id"])
    assert len(ids) == 5


def test_ws_invoke_accepts_custom_invocation_id(ws_echo_client):
    """If the message includes invocation_id, the server uses it."""
    custom_id = str(uuid.uuid4())
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "invocation_id": custom_id, "payload": {}})
        resp = ws.receive_json()
    assert resp["invocation_id"] == custom_id


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def test_ws_streaming_returns_chunks(ws_streaming_client):
    """Streaming handler yields 3 chunks then stream_end."""
    with ws_streaming_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        chunks = []
        while True:
            resp = ws.receive_json()
            if resp["type"] == "stream_chunk":
                chunks.append(resp["payload"])
            elif resp["type"] == "stream_end":
                break
    assert len(chunks) == 3
    for i, chunk in enumerate(chunks):
        assert chunk == {"chunk": i}


def test_ws_streaming_has_invocation_id(ws_streaming_client):
    """Streaming messages include invocation_id."""
    with ws_streaming_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "invocation_id" in resp
    uuid.UUID(resp["invocation_id"])


# ---------------------------------------------------------------------------
# Empty payload
# ---------------------------------------------------------------------------

def test_ws_invoke_empty_payload(ws_echo_client):
    """Empty payload doesn't crash the server."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_ws_invoke_error_returns_error(ws_failing_client):
    """Handler exception returns error message."""
    with ws_failing_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "internal_error"
    assert resp["error"]["message"] == "Internal server error"


def test_ws_invoke_error_has_invocation_id(ws_failing_client):
    """Error response still includes invocation_id."""
    with ws_failing_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "invocation_id" in resp


def test_ws_error_hides_details_by_default(ws_failing_client):
    """Exception message is hidden in error responses."""
    with ws_failing_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "something went wrong" not in resp["error"]["message"]
