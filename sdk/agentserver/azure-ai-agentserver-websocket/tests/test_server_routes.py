# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with ConversationAgentServerHost."""
import uuid

from starlette.testclient import TestClient

from azure.ai.agentserver.conversations import (
    ConversationAgentServerHost,
    ConversationContext,
)

from conftest import SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# WebSocket connection /conversations/ws
# ---------------------------------------------------------------------------

def test_websocket_invoke_returns_result(echo_client):
    """Invoke via WebSocket returns a result."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"test": True}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Conversation ID is valid UUID
# ---------------------------------------------------------------------------

def test_invoke_returns_uuid_conversation_id(echo_client):
    """Invoke returns a valid UUID conversation ID."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    inv_id = resp["conversation_id"]
    parsed = uuid.UUID(inv_id)
    assert str(parsed) == inv_id


# ---------------------------------------------------------------------------
# GET openapi spec returns 404 when not set
# ---------------------------------------------------------------------------

def test_get_openapi_spec_returns_404_when_not_set(no_spec_client):
    """GET /conversations/docs/openapi.json returns 404 when no spec registered."""
    resp = no_spec_client.get("/conversations/docs/openapi.json")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET openapi spec returns spec when registered
# ---------------------------------------------------------------------------

def test_get_openapi_spec_returns_spec_when_registered():
    """GET /conversations/docs/openapi.json returns the spec when registered."""
    app = ConversationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/conversations/docs/openapi.json")
    assert resp.status_code == 200
    assert resp.json() == SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# get_conversation returns not_found error by default
# ---------------------------------------------------------------------------

def test_get_conversation_returns_not_found_default(echo_client):
    """get_conversation without handler returns not_found error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "get_conversation", "conversation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# cancel returns not_found error by default
# ---------------------------------------------------------------------------

def test_cancel_conversation_returns_not_found_default(echo_client):
    """cancel_conversation without handler returns not_found error."""
    with echo_client.websocket_connect("/conversations/ws") as ws:
        ws.send_json({"action": "cancel_conversation", "conversation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Unknown HTTP route returns 404
# ---------------------------------------------------------------------------

def test_unknown_route_returns_404(echo_client):
    """Unknown route returns 404."""
    resp = echo_client.get("/nonexistent")
    assert resp.status_code == 404
