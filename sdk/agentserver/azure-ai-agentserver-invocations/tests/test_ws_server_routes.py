# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with InvocationWSAgentServerHost."""
import uuid

from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
)

from conftest_ws import WS_SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# WebSocket connection /invocations_ws/ws
# ---------------------------------------------------------------------------

def test_ws_invoke_returns_result(ws_echo_client):
    """Invoke via WebSocket returns a result."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"test": True}})
        resp = ws.receive_json()
    assert resp["type"] == "result"


# ---------------------------------------------------------------------------
# Invocation ID is valid UUID
# ---------------------------------------------------------------------------

def test_ws_invoke_returns_uuid_invocation_id(ws_echo_client):
    """Invoke returns a valid UUID invocation ID."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    inv_id = resp["invocation_id"]
    parsed = uuid.UUID(inv_id)
    assert str(parsed) == inv_id


# ---------------------------------------------------------------------------
# GET openapi spec returns 404 when not set
# ---------------------------------------------------------------------------

def test_ws_get_openapi_spec_returns_404_when_not_set(ws_no_spec_client):
    """GET /invocations_ws/docs/openapi.json returns 404 when no spec registered."""
    resp = ws_no_spec_client.get("/invocations_ws/docs/openapi.json")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET openapi spec returns spec when registered
# ---------------------------------------------------------------------------

def test_ws_get_openapi_spec_returns_spec_when_registered():
    """GET /invocations_ws/docs/openapi.json returns the spec when registered."""
    app = InvocationWSAgentServerHost(openapi_spec=WS_SAMPLE_OPENAPI_SPEC)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/invocations_ws/docs/openapi.json")
    assert resp.status_code == 200
    assert resp.json() == WS_SAMPLE_OPENAPI_SPEC


# ---------------------------------------------------------------------------
# get_invocation returns not_found error by default
# ---------------------------------------------------------------------------

def test_ws_get_invocation_returns_not_found_default(ws_echo_client):
    """get_invocation without handler returns not_found error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "get_invocation", "invocation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# cancel returns not_found error by default
# ---------------------------------------------------------------------------

def test_ws_cancel_invocation_returns_not_found_default(ws_echo_client):
    """cancel_invocation without handler returns not_found error."""
    with ws_echo_client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "cancel_invocation", "invocation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Unknown HTTP route returns 404
# ---------------------------------------------------------------------------

def test_ws_unknown_route_returns_404(ws_echo_client):
    """Unknown route returns 404."""
    resp = ws_echo_client.get("/nonexistent")
    assert resp.status_code == 404
