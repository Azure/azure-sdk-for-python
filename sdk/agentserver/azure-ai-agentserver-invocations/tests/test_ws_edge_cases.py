# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Edge-case tests for InvocationWSAgentServerHost over WebSocket."""
import uuid

from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
)


# ---------------------------------------------------------------------------
# Unknown action
# ---------------------------------------------------------------------------

def test_ws_unknown_action_returns_error(ws_echo_client):
    """Sending an unknown action returns an error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "unknown_action", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_action"


# ---------------------------------------------------------------------------
# Invalid JSON
# ---------------------------------------------------------------------------

def test_ws_invalid_json_returns_error(ws_echo_client):
    """Sending invalid JSON returns an error but connection stays open."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_text("not valid json {{{")
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert resp["error"]["code"] == "invalid_json"

        # Connection still works
        ws.send_json({"action": "invoke", "payload": {"key": "after-error"}})
        resp2 = ws.receive_json()
        assert resp2["type"] == "result"


def test_ws_non_object_json_returns_error(ws_echo_client):
    """Sending a JSON array instead of object returns an error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_text("[1, 2, 3]")
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_message"


# ---------------------------------------------------------------------------
# Invocation ID handling
# ---------------------------------------------------------------------------

def test_ws_invocation_id_auto_generated(ws_echo_client):
    """Invocation ID is auto-generated when not provided."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "invocation_id" in resp
    uuid.UUID(resp["invocation_id"])


def test_ws_invocation_id_accepted_from_message(ws_echo_client):
    """Server accepts invocation ID from message field."""
    custom_id = str(uuid.uuid4())
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "invocation_id": custom_id, "payload": {}})
        resp = ws.receive_json()
    assert resp["invocation_id"] == custom_id


def test_ws_invocation_id_generated_when_empty(ws_echo_client):
    """When empty invocation ID is sent, server generates one."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "invocation_id": "", "payload": {}})
        resp = ws.receive_json()
    inv_id = resp["invocation_id"]
    uuid.UUID(inv_id)


# ---------------------------------------------------------------------------
# Payload edge cases
# ---------------------------------------------------------------------------

def test_ws_large_payload(ws_echo_client):
    """Large payload (dict with big value) is handled correctly."""
    big_value = "x" * (1024 * 1024)
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"data": big_value}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert len(resp["payload"]["echo"]["data"]) == 1024 * 1024


def test_ws_unicode_payload(ws_echo_client):
    """Unicode payload is preserved."""
    text = "Hello, 世界! 🌍"
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"text": text}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["echo"]["text"] == text


# ---------------------------------------------------------------------------
# Streaming edge cases
# ---------------------------------------------------------------------------

def test_ws_empty_streaming():
    """Empty streaming response (no chunks) sends only stream_end."""
    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext):
        return
        yield  # noqa: E501 — make it a generator

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "stream_end"


def test_ws_streaming_has_invocation_id():
    """Streaming messages include invocation_id."""
    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext):
        yield {"chunk": "data"}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "invocation_id" in resp


# ---------------------------------------------------------------------------
# Invocation lifecycle
# ---------------------------------------------------------------------------

def test_ws_multiple_gets(ws_async_storage_client):
    """Multiple gets for the same invocation return the same result."""
    with ws_async_storage_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "multi-get"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        for _ in range(3):
            ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
            get_resp = ws.receive_json()
            assert get_resp["type"] == "result"
            assert get_resp["payload"]["data"]["key"] == "multi-get"


def test_ws_double_cancel(ws_async_storage_client):
    """Cancelling twice: second cancel returns error."""
    with ws_async_storage_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "cancel-twice"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        cancel1 = ws.receive_json()
        assert cancel1["type"] == "result"

        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        cancel2 = ws.receive_json()
        assert cancel2["type"] == "error"
        assert cancel2["error"]["code"] == "not_found"


def test_ws_invoke_cancel_get(ws_async_storage_client):
    """Invoke -> cancel -> get returns not_found error."""
    with ws_async_storage_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "icg"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        ws.receive_json()  # consume cancel response

        ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
        get_resp = ws.receive_json()
        assert get_resp["type"] == "error"
        assert get_resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Multiple sequential invocation calls on same connection
# ---------------------------------------------------------------------------

def test_ws_multiple_sequential_invocation_calls(ws_echo_client):
    """Multiple sequential invocation calls on the same WebSocket connection."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ids = set()
        for i in range(10):
            ws.send_json({"action": "invoke", "payload": {"idx": i}})
            resp = ws.receive_json()
            assert resp["type"] == "result"
            assert resp["payload"]["echo"]["idx"] == i
            ids.add(resp["invocation_id"])
    assert len(ids) == 10


# ---------------------------------------------------------------------------
# get/cancel without invocation_id
# ---------------------------------------------------------------------------

def test_ws_get_without_invocation_id(ws_echo_client):
    """get_invocation without invocation_id returns error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "get_invocation"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_request"


def test_ws_cancel_without_invocation_id(ws_echo_client):
    """cancel_invocation without invocation_id returns error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "cancel_invocation"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_request"
