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
from starlette.routing import Route, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations.voice import VoiceAgentServerHost

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


def test_voice_host_rejects_preexisting_invocations_ws_route():
    """The typed host must not silently run an unrelated endpoint at its owned route."""

    async def preexisting_endpoint(_websocket):
        return None

    with pytest.raises(RuntimeError, match="cannot own /invocations_ws"):
        VoiceAgentServerHost(
            routes=[WebSocketRoute("/invocations_ws", preexisting_endpoint)],
            configure_observability=None,
        )


def test_voice_host_allows_http_route_at_same_path():
    """HTTP and WebSocket routes may share a path because ASGI scopes differ."""

    async def http_endpoint(_request):
        return Response("ok")

    app = VoiceAgentServerHost(
        routes=[Route("/invocations_ws", http_endpoint, methods=["GET"])],
        configure_observability=None,
    )

    websocket_routes = [
        route for route in app.routes if isinstance(route, WebSocketRoute) and route.path == "/invocations_ws"
    ]
    assert len(websocket_routes) == 1
    assert getattr(websocket_routes[0].endpoint, "__self__", None) is app


def test_readiness_still_works_with_ws_registered():
    """Adding the WS route doesn't break /readiness."""
    app = _make_echo_ws_app()
    client = TestClient(app)
    resp = client.get("/readiness")
    assert resp.status_code == 200
    # x-platform-server header still applied via core middleware
    assert "x-platform-server" in resp.headers


def test_ws_upgrade_includes_combined_platform_server_header():
    """The WebSocket acceptance carries both Core and Invocations identities."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with client.websocket_connect("/invocations_ws") as ws:
        headers = {key.decode("latin-1").lower(): value.decode("latin-1") for key, value in (ws.extra_headers or [])}

    server_header = headers.get("x-platform-server")
    assert server_header is not None
    assert "azure-ai-agentserver-core/" in server_header
    assert "azure-ai-agentserver-invocations/" in server_header


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
