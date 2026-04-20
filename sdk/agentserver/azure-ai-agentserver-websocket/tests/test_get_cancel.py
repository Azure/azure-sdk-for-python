# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for get_conversation and cancel_conversation actions over WebSocket."""
from starlette.testclient import TestClient

from azure.ai.agentserver.conversations import (
    ConversationAgentServerHost,
    ConversationContext,
    ConversationError,
)


# ---------------------------------------------------------------------------
# GET after invoke
# ---------------------------------------------------------------------------

def test_get_after_invoke_returns_stored_result(async_storage_client):
    """get_conversation after invoke returns the stored result."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "stored-data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        ws.send_json({"action": "get_conversation", "conversation_id": inv_id})
        get_resp = ws.receive_json()

    assert get_resp["type"] == "result"
    assert get_resp["payload"]["data"]["key"] == "stored-data"


# ---------------------------------------------------------------------------
# GET unknown ID
# ---------------------------------------------------------------------------

def test_get_unknown_id_returns_error(async_storage_client):
    """get_conversation with unknown ID returns error."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "get_conversation", "conversation_id": "unknown-id-12345"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Cancel after invoke
# ---------------------------------------------------------------------------

def test_cancel_after_invoke_returns_cancelled(async_storage_client):
    """cancel_conversation after invoke returns cancelled status."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "cancel-me"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        ws.send_json({"action": "cancel_conversation", "conversation_id": inv_id})
        cancel_resp = ws.receive_json()

    assert cancel_resp["type"] == "result"
    assert cancel_resp["payload"]["status"] == "cancelled"


# ---------------------------------------------------------------------------
# Cancel unknown ID
# ---------------------------------------------------------------------------

def test_cancel_unknown_id_returns_error(async_storage_client):
    """cancel_conversation with unknown ID returns error."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "cancel_conversation", "conversation_id": "unknown-id-12345"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# GET after cancel
# ---------------------------------------------------------------------------

def test_get_after_cancel_returns_error(async_storage_client):
    """get_conversation after cancel returns error (data removed)."""
    with async_storage_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "temp"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["conversation_id"]

        ws.send_json({"action": "cancel_conversation", "conversation_id": inv_id})
        ws.receive_json()  # consume cancel response

        ws.send_json({"action": "get_conversation", "conversation_id": inv_id})
        get_resp = ws.receive_json()

    assert get_resp["type"] == "error"
    assert get_resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# GET error returns internal_error
# ---------------------------------------------------------------------------

def test_get_conversation_error_returns_internal_error():
    """get_conversation handler raising an exception returns internal_error."""
    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        return {"ok": True}

    @app.get_conversation_handler
    async def get_handler(context: ConversationContext) -> dict:
        raise RuntimeError("get failed")

    client = TestClient(app)
    with client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "get_conversation", "conversation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "internal_error"


# ---------------------------------------------------------------------------
# Cancel error returns internal_error
# ---------------------------------------------------------------------------

def test_cancel_conversation_error_returns_internal_error():
    """cancel_conversation handler raising an exception returns internal_error."""
    app = ConversationAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        return {"ok": True}

    @app.cancel_conversation_handler
    async def cancel_handler(context: ConversationContext) -> dict:
        raise RuntimeError("cancel failed")

    client = TestClient(app)
    with client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "cancel_conversation", "conversation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "internal_error"
