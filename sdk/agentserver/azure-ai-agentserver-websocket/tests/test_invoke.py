# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the invoke action over WebSocket."""
import uuid

from azure.ai.agentserver.websocket import WebsocketContext


# ---------------------------------------------------------------------------
# Echo payload
# ---------------------------------------------------------------------------

def test_invoke_echo_payload(echo_client):
    """Invoke echoes the payload back."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"msg": "hello world"}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["echo"]["msg"] == "hello world"


# ---------------------------------------------------------------------------
# IDs
# ---------------------------------------------------------------------------

def test_invoke_returns_websocket_id(echo_client):
    """Response includes a valid UUID websocket_id."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "websocket_id" in resp
    uuid.UUID(resp["websocket_id"])


def test_invoke_returns_session_id(echo_client):
    """Response includes a valid UUID session_id."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "session_id" in resp
    uuid.UUID(resp["session_id"])


def test_invoke_unique_websocket_ids(echo_client):
    """Each invoke gets a unique websocket ID."""
    ids = set()
    with echo_client.websocket_connect("/websocket/ws") as ws:
        for _ in range(5):
            ws.send_json({"action": "invoke", "payload": {}})
            resp = ws.receive_json()
            ids.add(resp["websocket_id"])
    assert len(ids) == 5


def test_invoke_accepts_custom_websocket_id(echo_client):
    """If the message includes websocket_id, the server uses it."""
    custom_id = str(uuid.uuid4())
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "websocket_id": custom_id, "payload": {}})
        resp = ws.receive_json()
    assert resp["websocket_id"] == custom_id


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def test_streaming_returns_chunks(streaming_client):
    """Streaming handler yields 3 chunks then stream_end."""
    with streaming_client.websocket_connect("/websocket/ws") as ws:
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


def test_streaming_has_websocket_id(streaming_client):
    """Streaming messages include websocket_id."""
    with streaming_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "websocket_id" in resp
    uuid.UUID(resp["websocket_id"])


# ---------------------------------------------------------------------------
# Empty payload
# ---------------------------------------------------------------------------

def test_invoke_empty_payload(echo_client):
    """Empty payload doesn't crash the server."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_invoke_error_returns_error(failing_client):
    """Handler exception returns error message."""
    with failing_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "internal_error"
    assert resp["error"]["message"] == "Internal server error"


def test_invoke_error_has_websocket_id(failing_client):
    """Error response still includes websocket_id."""
    with failing_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "websocket_id" in resp


def test_error_hides_details_by_default(failing_client):
    """Exception message is hidden in error responses."""
    with failing_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "something went wrong" not in resp["error"]["message"]
