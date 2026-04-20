# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Edge-case tests for ConversationAgentServerHost over WebSocket."""
import uuid

from starlette.testclient import TestClient

from azure.ai.agentserver.conversations import (
    ConversationAgentServerHost,
    ConversationContext,
)


# ---------------------------------------------------------------------------
# Unknown action
# ---------------------------------------------------------------------------

def test_unknown_action_returns_error(echo_client):
    """Sending an unknown action returns an error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "unknown_action", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_action"


# ---------------------------------------------------------------------------
# Invalid JSON
# ---------------------------------------------------------------------------

def test_invalid_json_returns_error(echo_client):
    """Sending invalid JSON returns an error but connection stays open."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_text("not valid json {{{")
        resp = ws.receive_json()
        assert resp["type"] == "error"
        assert resp["error"]["code"] == "invalid_json"

        # Connection still works
        ws.send_json({"action": "invoke", "payload": {"key": "after-error"}})
        resp2 = ws.receive_json()
        assert resp2["type"] == "result"


def test_non_object_json_returns_error(echo_client):
    """Sending a JSON array instead of object returns an error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_text("[1, 2, 3]")
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_message"


# ---------------------------------------------------------------------------
# Conversation ID handling
# ---------------------------------------------------------------------------

def test_conversation_id_auto_generated(echo_client):
    """Conversation ID is auto-generated when not provided."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "conversation_id" in resp
    uuid.UUID(resp["conversation_id"])


def test_conversation_id_accepted_from_message(echo_client):
    """Server accepts conversation ID from message field."""
    custom_id = str(uuid.uuid4())
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "conversation_id": custom_id, "payload": {}})
        resp = ws.receive_json()
    assert resp["conversation_id"] == custom_id


def test_conversation_id_generated_when_empty(echo_client):
    """When empty conversation ID is sent, server generates one."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "conversation_id": "", "payload": {}})
        resp = ws.receive_json()
    inv_id = resp["conversation_id"]
    uuid.UUID(inv_id)


# ---------------------------------------------------------------------------
# Payload edge cases
# ---------------------------------------------------------------------------

def test_large_payload(echo_client):
    """Large payload (dict with big value) is handled correctly."""
    big_value = "x" * (1024 * 1024)
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"data": big_value}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert len(resp["payload"]["echo"]["data"]) == 1024 * 1024


def test_unicode_payload(echo_client):
    """Unicode payload is preserved."""
    text = "Hello, 世界! 🌍"
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"text": text}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["echo"]["text"] == text


# ---------------------------------------------------------------------------
# Streaming edge cases
# ---------------------------------------------------------------------------

def test_empty_streaming():
    """Empty streaming response (no chunks) sends only stream_end."""
    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext):
        return
        yield  # noqa: E501 — make it a generator

    client = TestClient(app)
    with client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "stream_end"


def test_streaming_has_conversation_id():
    """Streaming messages include conversation_id."""
    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext):
        yield {"chunk": "data"}

    client = TestClient(app)
    with client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert "conversation_id" in resp


# ---------------------------------------------------------------------------
# Conversation lifecycle
# ---------------------------------------------------------------------------

def test_multiple_gets(async_storage_client):
    """Multiple gets for the same conversation return the same result."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "multi-get"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        for _ in range(3):
            ws.send_json({"action": "get_conversation", "conversation_id": inv_id})
            get_resp = ws.receive_json()
            assert get_resp["type"] == "result"
            assert get_resp["payload"]["data"]["key"] == "multi-get"


def test_double_cancel(async_storage_client):
    """Cancelling twice: second cancel returns error."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "cancel-twice"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        ws.send_json({"action": "cancel_conversation", "conversation_id": inv_id})
        cancel1 = ws.receive_json()
        assert cancel1["type"] == "result"

        ws.send_json({"action": "cancel_conversation", "conversation_id": inv_id})
        cancel2 = ws.receive_json()
        assert cancel2["type"] == "error"
        assert cancel2["error"]["code"] == "not_found"


def test_invoke_cancel_get(async_storage_client):
    """Invoke -> cancel -> get returns not_found error."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "icg"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        ws.send_json({"action": "cancel_conversation", "conversation_id": inv_id})
        ws.receive_json()  # consume cancel response

        ws.send_json({"action": "get_conversation", "conversation_id": inv_id})
        get_resp = ws.receive_json()
        assert get_resp["type"] == "error"
        assert get_resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Multiple sequential conversations on same connection
# ---------------------------------------------------------------------------

def test_multiple_sequential_conversations(echo_client):
    """Multiple sequential conversations on the same WebSocket connection."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ids = set()
        for i in range(10):
            ws.send_json({"action": "invoke", "payload": {"idx": i}})
            resp = ws.receive_json()
            assert resp["type"] == "result"
            assert resp["payload"]["echo"]["idx"] == i
            ids.add(resp["conversation_id"])
    assert len(ids) == 10


# ---------------------------------------------------------------------------
# get/cancel without conversation_id
# ---------------------------------------------------------------------------

def test_get_without_conversation_id(echo_client):
    """get_conversation without conversation_id returns error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "get_conversation"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_request"


def test_cancel_without_conversation_id(echo_client):
    """cancel_conversation without conversation_id returns error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "cancel_conversation"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "invalid_request"
