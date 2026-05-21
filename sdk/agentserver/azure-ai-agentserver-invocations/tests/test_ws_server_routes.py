# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for basic server route registration with the ``/invocations_ws`` route.

Parity with :mod:`tests.test_server_routes` — covers route registration,
coexistence with the HTTP routes, and rejection of mismatched paths.
"""
import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost

from conftest import _make_echo_ws_app


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def test_ws_route_is_registered_when_handler_is_set():
    """The /invocations_ws route is registered lazily on @ws_handler."""
    app = _make_echo_ws_app()
    paths = [getattr(r, "path", None) for r in app.routes]
    assert "/invocations_ws" in paths
    assert "/invocations" in paths
    assert "/readiness" in paths


def test_ws_route_is_not_registered_without_handler():
    """Without @ws_handler the WS route is absent (upgrades return 404)."""
    app = InvocationAgentServerHost()
    paths = [getattr(r, "path", None) for r in app.routes]
    assert "/invocations_ws" not in paths
    # HTTP routes still registered.
    assert "/invocations" in paths


def test_readiness_still_works_with_ws_registered():
    """Adding the WS route doesn't break /readiness."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    resp = client.get("/readiness")
    assert resp.status_code == 200
    # x-platform-server header still applied via core middleware
    assert "x-platform-server" in resp.headers


# ---------------------------------------------------------------------------
# Coexistence with HTTP /invocations
# ---------------------------------------------------------------------------

def test_http_and_ws_share_same_host():
    """Both transports work on the same app — single session, single process."""
    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def http_handle(request: Request) -> Response:
        body = await request.json()
        return JSONResponse({"http": body})

    @app.ws_handler
    async def ws_handle(websocket: WebSocket) -> None:
        async for msg in websocket.iter_text():
            await websocket.send_text(f"ws:{msg}")

    client = TestClient(app)

    # HTTP route still works
    resp = client.post("/invocations", json={"hello": "world"})
    assert resp.status_code == 200
    assert resp.json() == {"http": {"hello": "world"}}

    # WS route works on the same host
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        assert ws.receive_text() == "ws:hi"


# ---------------------------------------------------------------------------
# Mismatched URLs (parity with test_unknown_route_returns_404)
# ---------------------------------------------------------------------------

def test_ws_upgrade_on_http_path_fails():
    """A WS upgrade to ``/invocations`` (the HTTP route) is rejected."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    # /invocations is a Route, not a WebSocketRoute — TestClient surfaces
    # this as an immediate WebSocketDisconnect rather than a connect.
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations"):
            pass


def test_ws_unknown_path_fails():
    """An unknown WS path is rejected."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/nonexistent"):
            pass
