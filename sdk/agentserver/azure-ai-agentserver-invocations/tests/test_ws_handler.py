# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the ``@app.ws_handler`` decorator and ``/invocations_ws`` route.

The tests use Starlette's :class:`~starlette.testclient.TestClient` which
supports WebSocket connections in-process, so the SDK's accept / handler
dispatch / close-code mapping / close-event log all run end-to-end without
needing a real network listener.
"""
import logging

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

def _make_echo_ws(**kwargs) -> InvocationAgentServerHost:
    """Build a host whose ws handler echoes every text frame back."""
    app = InvocationAgentServerHost(**kwargs)

    @app.ws_handler
    async def echo(websocket: WebSocket) -> None:
        async for message in websocket.iter_text():
            await websocket.send_text(message)

    return app


def _make_failing_ws(exc_factory=ValueError) -> InvocationAgentServerHost:
    """Build a host whose ws handler raises after one received frame."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def boom(websocket: WebSocket) -> None:
        await websocket.receive_text()
        raise exc_factory("boom")

    return app


# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------

def test_ws_route_is_registered():
    """The /invocations_ws route exists alongside HTTP routes."""
    app = InvocationAgentServerHost()
    paths = [getattr(r, "path", None) for r in app.routes]
    assert "/invocations_ws" in paths
    assert "/invocations" in paths
    assert "/readiness" in paths


def test_readiness_still_works_with_ws_registered():
    """Adding the WS route doesn't break /readiness."""
    app = _make_echo_ws()
    client = TestClient(app)
    resp = client.get("/readiness")
    assert resp.status_code == 200
    # x-platform-server header still applied via core middleware
    assert "x-platform-server" in resp.headers


# ---------------------------------------------------------------------------
# Decorator validation
# ---------------------------------------------------------------------------

def test_ws_handler_rejects_sync_function():
    """``@app.ws_handler`` must be applied to ``async def`` callables."""
    app = InvocationAgentServerHost()

    with pytest.raises(TypeError, match="async function"):
        @app.ws_handler  # type: ignore[arg-type]
        def sync_handler(websocket):  # noqa: ARG001
            pass


def test_ws_handler_returns_function_unchanged():
    """The decorator must return the original function unmodified."""
    app = InvocationAgentServerHost()

    async def handler(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.close()

    result = app.ws_handler(handler)
    assert result is handler


# ---------------------------------------------------------------------------
# Accept happens automatically
# ---------------------------------------------------------------------------

def test_ws_sdk_accepts_connection_before_handler_runs():
    """The SDK calls ``websocket.accept()`` before invoking the user handler.

    The handler in this test never calls ``accept`` itself; the connection
    must still be usable, which proves the SDK accepted it on the user's
    behalf.
    """
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.send_text("ready")

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        assert ws.receive_text() == "ready"


# ---------------------------------------------------------------------------
# Echo round-trip
# ---------------------------------------------------------------------------

def test_ws_echo_round_trip():
    """End-to-end: send a frame, receive it echoed back."""
    app = _make_echo_ws()
    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hello")
        assert ws.receive_text() == "hello"
        ws.send_text("world")
        assert ws.receive_text() == "world"


# ---------------------------------------------------------------------------
# Handler exception → close code 1011
# ---------------------------------------------------------------------------

def test_ws_handler_exception_maps_to_close_code_1011():
    """Uncaught handler exceptions must surface as RFC 6455 close code 1011."""
    app = _make_failing_ws()
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("trigger")
            # Server closes after the handler raises; receiving forces
            # the close frame to surface as WebSocketDisconnect.
            ws.receive_text()

    assert excinfo.value.code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR
    assert excinfo.value.code == 1011


def test_ws_clean_return_uses_close_code_1000():
    """A handler that returns normally yields a 1000 (normal) close code."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        # Receive once, then return — SDK closes cleanly.
        await websocket.receive_text()

    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("done")
            ws.receive_text()  # Forces the close to surface.

    assert excinfo.value.code == InvocationsWSConstants.CLOSE_NORMAL


# ---------------------------------------------------------------------------
# No handler registered
# ---------------------------------------------------------------------------

def test_ws_with_no_handler_registered_closes_with_1011():
    """If no @ws_handler is registered, the SDK closes with 1011."""
    app = InvocationAgentServerHost()
    client = TestClient(app)

    with pytest.raises(WebSocketDisconnect) as excinfo:
        with client.websocket_connect("/invocations_ws"):
            pass

    assert excinfo.value.code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR


# ---------------------------------------------------------------------------
# Close-event log line carries ws.session_id, ws.close_code, ws.duration_ms
# ---------------------------------------------------------------------------

def _records_with_ws_extras(records):
    """Filter log records that carry the spec's ws.* extras."""
    out = []
    for rec in records:
        if hasattr(rec, "ws.session_id") and hasattr(rec, "ws.close_code"):
            out.append(rec)
    return out


def test_ws_close_event_log_contains_required_fields(caplog):
    """The close-event log line carries ws.session_id, ws.close_code, ws.duration_ms."""
    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            assert ws.receive_text() == "ping"

    matches = _records_with_ws_extras(caplog.records)
    assert matches, "expected a structured close-event log record"
    rec = matches[-1]

    session_id = getattr(rec, "ws.session_id")
    close_code = getattr(rec, "ws.close_code")
    duration_ms = getattr(rec, "ws.duration_ms")

    assert isinstance(session_id, str) and session_id  # generated UUID
    assert close_code == InvocationsWSConstants.CLOSE_NORMAL
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


def test_ws_close_event_on_handler_exception_records_1011(caplog):
    """Handler raising → close-event log records ws.close_code = 1011."""
    app = _make_failing_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("trigger")
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == 1011


# ---------------------------------------------------------------------------
# Hypercorn ws_ping_interval wiring
# ---------------------------------------------------------------------------

def test_ws_ping_interval_default_is_30_seconds():
    """Default ping interval matches the spec (30 s)."""
    app = InvocationAgentServerHost()
    assert app.ws_ping_interval == InvocationsWSConstants.DEFAULT_PING_INTERVAL_S
    assert app.ws_ping_interval == 30.0


def test_ws_ping_interval_custom_value():
    """``ws_ping_interval`` is honoured."""
    app = InvocationAgentServerHost(ws_ping_interval=15)
    assert app.ws_ping_interval == 15.0


def test_ws_ping_interval_zero_disables_keepalive():
    """``ws_ping_interval=0`` disables WS-level keep-alive."""
    app = InvocationAgentServerHost(ws_ping_interval=0)
    assert app.ws_ping_interval == 0.0


def test_ws_ping_interval_negative_rejected():
    """Negative intervals are programming errors."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=-1)


def test_ws_ping_interval_propagates_to_hypercorn_config():
    """The configured interval lands on the Hypercorn server config."""
    app = InvocationAgentServerHost(ws_ping_interval=20)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    # Hypercorn ≥0.14 exposes this attribute.
    assert getattr(config, "websocket_ping_interval", None) == 20.0


def test_ws_ping_interval_zero_does_not_override_hypercorn_default():
    """Zero leaves Hypercorn's default (None = disabled) intact."""
    app = InvocationAgentServerHost(ws_ping_interval=0)
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    # Hypercorn default is None — our wiring leaves it unset for 0.
    assert getattr(config, "websocket_ping_interval", None) is None


# ---------------------------------------------------------------------------
# Coexistence with HTTP /invocations
# ---------------------------------------------------------------------------

def test_http_and_ws_share_same_host():
    """Both transports work on the same app object — single session, single process."""
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response

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
# Client-initiated disconnect
# ---------------------------------------------------------------------------

def test_ws_client_disconnect_does_not_log_as_error(caplog):
    """A client-initiated disconnect is a normal close, not a 1011 error."""
    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("hello")
            ws.receive_text()
            # __exit__ sends websocket.disconnect — the SDK should treat
            # this as normal, not raise from the handler.

    error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
    # No ERROR-level records should be emitted for a clean client disconnect.
    assert not error_records, [r.getMessage() for r in error_records]
