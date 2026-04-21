# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with WebsocketAgentServerHost."""
import uuid

from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
)

from conftest import SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# WebSocket connection /websocket/ws
# ---------------------------------------------------------------------------

def test_websocket_invoke_returns_result(echo_client):
    """Invoke via WebSocket returns a result."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"test": True}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Websocket ID is valid UUID
# ---------------------------------------------------------------------------

def test_invoke_returns_uuid_websocket_id(echo_client):
    """Invoke returns a valid UUID websocket ID."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    inv_id = resp["websocket_id"]
    parsed = uuid.UUID(inv_id)
    assert str(parsed) == inv_id


# ---------------------------------------------------------------------------
# GET openapi spec returns 404 when not set
# ---------------------------------------------------------------------------

def test_get_openapi_spec_returns_404_when_not_set(no_spec_client):
    """GET /websocket/docs/openapi.json returns 404 when no spec registered."""
    resp = no_spec_client.get("/websocket/docs/openapi.json")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET openapi spec returns spec when registered
# ---------------------------------------------------------------------------

def test_get_openapi_spec_returns_spec_when_registered():
    """GET /websocket/docs/openapi.json returns the spec when registered."""
    app = WebsocketAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/websocket/docs/openapi.json")
    assert resp.status_code == 200
    assert resp.json() == SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# get_websocket returns not_found error by default
# ---------------------------------------------------------------------------

def test_get_websocket_returns_not_found_default(echo_client):
    """get_websocket without handler returns not_found error."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "get_websocket", "websocket_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# cancel returns not_found error by default
# ---------------------------------------------------------------------------

def test_cancel_websocket_returns_not_found_default(echo_client):
    """cancel_websocket without handler returns not_found error."""
    with echo_client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "cancel_websocket", "websocket_id": "some-id"})
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
