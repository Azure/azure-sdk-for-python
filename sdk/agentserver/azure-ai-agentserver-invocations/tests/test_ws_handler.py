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


# ---------------------------------------------------------------------------
# Decorator state (parity with test_decorator_pattern.test_invoke_handler_stores_function)
# ---------------------------------------------------------------------------

def test_ws_handler_stores_function():
    """``@app.ws_handler`` stores the registered function on the host."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.send_text("ok")

    assert app._ws_fn is handler  # noqa: SLF001


def test_ws_handler_default_is_none():
    """Without ``@ws_handler`` the slot stays None."""
    app = InvocationAgentServerHost()
    assert app._ws_fn is None  # noqa: SLF001


def test_ws_handler_last_registration_wins():
    """Re-applying ``@ws_handler`` replaces the previous function."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def first(websocket: WebSocket) -> None:  # noqa: ARG001
        return

    @app.ws_handler
    async def second(websocket: WebSocket) -> None:  # noqa: ARG001
        return

    assert app._ws_fn is second  # noqa: SLF001


# ---------------------------------------------------------------------------
# Message variations (parity with test_invoke / test_edge_cases payload tests)
# ---------------------------------------------------------------------------

def test_ws_binary_frame_round_trip():
    """Binary frames round-trip without corruption (parity with test_binary_payload)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        data = await websocket.receive_bytes()
        await websocket.send_bytes(data)

    client = TestClient(app)
    payload = bytes(range(256))
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_bytes(payload)
        assert ws.receive_bytes() == payload


def test_ws_unicode_text_round_trip():
    """Unicode text frames are preserved (parity with test_unicode_payload)."""
    app = _make_echo_ws()
    client = TestClient(app)
    text = "Hello, 世界! 🌍 — naïve façade"
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text(text)
        assert ws.receive_text() == text


def test_ws_large_text_frame_round_trip():
    """A ~1 MB text frame round-trips successfully (parity with test_large_payload)."""
    app = _make_echo_ws()
    client = TestClient(app)
    payload = "x" * (1024 * 1024)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text(payload)
        assert ws.receive_text() == payload


def test_ws_json_frame_round_trip():
    """``send_json`` / ``receive_json`` round-trip JSON payloads."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        msg = await websocket.receive_json()
        await websocket.send_json({"echo": msg})

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_json({"hello": "world", "n": 42})
        assert ws.receive_json() == {"echo": {"hello": "world", "n": 42}}


def test_ws_multiple_frames_per_connection():
    """Multiple frames flow through one connection (parity with streaming chunks)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        for i in range(5):
            await websocket.send_text(f"chunk-{i}")

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        for i in range(5):
            assert ws.receive_text() == f"chunk-{i}"


# ---------------------------------------------------------------------------
# Session ID behavior (parity with test_session_id)
# ---------------------------------------------------------------------------

def _session_ids_from_records(records):
    """Pull ``ws.session_id`` from each structured close-event record."""
    return [getattr(r, "ws.session_id") for r in _records_with_ws_extras(records)]


def test_ws_session_id_is_uuid(caplog):
    """The per-connection session ID is a valid UUID string."""
    import uuid

    app = _make_echo_ws()
    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("hi")
            ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert session_ids
    # Each must parse as a UUID — the WS endpoint generates one server-side.
    parsed = uuid.UUID(session_ids[-1])
    assert str(parsed) == session_ids[-1]


def test_ws_session_id_is_unique_per_connection(caplog):
    """Each WS connection gets its own session ID (parity with test_invoke_unique_invocation_ids)."""
    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        for _ in range(5):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("ping")
                ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert len(session_ids) == 5
    assert len(set(session_ids)) == 5


def test_ws_session_id_ignores_query_param(caplog):
    """Unlike HTTP, the WS endpoint always generates its own session ID."""
    import uuid

    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect(
            "/invocations_ws?agent_session_id=my-custom-session",
        ) as ws:
            ws.send_text("x")
            ws.receive_text()

    session_ids = _session_ids_from_records(caplog.records)
    assert session_ids
    # The client's value MUST NOT leak into the session ID — the WS spec
    # generates a fresh server-side UUID per connection.
    assert session_ids[-1] != "my-custom-session"
    uuid.UUID(session_ids[-1])


# ---------------------------------------------------------------------------
# Client-initiated close with custom code
# ---------------------------------------------------------------------------

def test_ws_client_initiated_close_with_custom_code_is_reported(caplog):
    """When the client closes with a non-1000 code, the server surfaces the client's code (not 1011)."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        # Use receive_text directly so WebSocketDisconnect propagates with
        # the client's close code — ``iter_text`` swallows it.
        while True:
            await websocket.receive_text()

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("warm-up")
            ws.close(code=4001)

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    rec = matches[-1]
    close_code = getattr(rec, "ws.close_code")
    # Server surfaces the client's code — NOT 1011.
    assert close_code == 4001
    # No ERROR-level records — a client disconnect is normal.
    assert not [r for r in caplog.records if r.levelno >= logging.ERROR]


# ---------------------------------------------------------------------------
# Handler-explicit close
# ---------------------------------------------------------------------------

def test_ws_handler_explicit_close_does_not_double_close(caplog):
    """If the handler closes the WS itself, the SDK does NOT attempt a second close."""
    app = InvocationAgentServerHost()
    closes_observed: list[int] = []

    async def handler(websocket: WebSocket) -> None:
        # Hand-roll close so we can verify the SDK skips re-closing.
        await websocket.send_text("bye")
        await websocket.close(code=1000)
        closes_observed.append(1)

    app.ws_handler(handler)

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                assert ws.receive_text() == "bye"
                ws.receive_text()  # forces the close frame to surface

    # Handler ran to completion.
    assert closes_observed == [1]
    # Close-event log line still emitted (with the handler's code).
    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL


# ---------------------------------------------------------------------------
# Empty connection (no frames sent)
# ---------------------------------------------------------------------------

def test_ws_empty_connection_closes_normally(caplog):
    """A connection that immediately disconnects closes cleanly (1000)."""
    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws"):
            pass  # Disconnect without sending anything.

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL


# ---------------------------------------------------------------------------
# Bidirectional streaming (WebSocket-only)
# ---------------------------------------------------------------------------

def test_ws_bidirectional_concurrent_send_receive():
    """Reader and writer coroutines run concurrently on the same socket."""
    import asyncio

    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        async def reader():
            async for msg in websocket.iter_text():
                if msg == "bye":
                    return

        async def writer():
            for i in range(3):
                await websocket.send_text(f"server-{i}")
                await asyncio.sleep(0)  # yield to reader

        # Run reader + writer in parallel — the defining property of WS.
        await asyncio.gather(reader(), writer())

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        # Mix inbound and outbound frames to prove they're not lock-stepped.
        ws.send_text("client-a")
        assert ws.receive_text() == "server-0"
        ws.send_text("client-b")
        assert ws.receive_text() == "server-1"
        assert ws.receive_text() == "server-2"
        ws.send_text("bye")


# ---------------------------------------------------------------------------
# Hypercorn ws_ping_interval — extra validation paths
# ---------------------------------------------------------------------------

def test_ws_ping_interval_nan_rejected():
    """``ws_ping_interval=nan`` is a programming error."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=float("nan"))


def test_ws_ping_interval_inf_rejected():
    """``ws_ping_interval=inf`` is a programming error."""
    with pytest.raises(ValueError, match="non-negative"):
        InvocationAgentServerHost(ws_ping_interval=float("inf"))


def test_ws_ping_interval_non_numeric_rejected():
    """Strings or non-numeric values surface as ``ValueError``."""
    with pytest.raises(ValueError, match="must be a number"):
        InvocationAgentServerHost(ws_ping_interval="thirty")  # type: ignore[arg-type]


def test_ws_ping_interval_float_value_accepted():
    """Fractional intervals are coerced to ``float``."""
    app = InvocationAgentServerHost(ws_ping_interval=12.5)
    assert app.ws_ping_interval == 12.5
    config = app._build_hypercorn_config("0.0.0.0", 8088)  # noqa: SLF001
    assert getattr(config, "websocket_ping_interval", None) == 12.5


def test_ws_ping_interval_property_is_read_only():
    """``ws_ping_interval`` is exposed only as a property (no setter)."""
    app = InvocationAgentServerHost(ws_ping_interval=20)
    with pytest.raises(AttributeError):
        app.ws_ping_interval = 10  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Close-event error attributes (handler exception path)
# ---------------------------------------------------------------------------

def test_ws_close_event_log_does_not_leak_exception_message(caplog):
    """The close-event log line does NOT carry the handler exception text.

    (Parity with ``test_error_hides_details_by_default`` — internal errors
    must not leak details to the structured log payload.)
    """
    app = _make_failing_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("trigger")
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    rec = matches[-1]
    # The structured close-event log line carries only the safe ws.* fields.
    assert not hasattr(rec, "ws.error_message")
    # And the message itself does not embed the raw exception text.
    assert "boom" not in rec.getMessage()


def test_ws_close_event_duration_is_non_negative(caplog):
    """``ws.duration_ms`` is a non-negative integer derived from a monotonic clock."""
    app = _make_echo_ws()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    duration_ms = getattr(matches[-1], "ws.duration_ms")
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


# ---------------------------------------------------------------------------
# Mismatched URLs and methods
# ---------------------------------------------------------------------------

def test_ws_upgrade_on_http_path_fails():
    """A WS upgrade to ``/invocations`` (the HTTP route) is rejected."""
    app = _make_echo_ws()
    client = TestClient(app)
    # /invocations is a Route, not a WebSocketRoute — TestClient surfaces
    # this as an immediate WebSocketDisconnect rather than a connect.
    with pytest.raises((WebSocketDisconnect, Exception)):  # noqa: PT011
        with client.websocket_connect("/invocations"):
            pass


def test_ws_unknown_path_fails():
    """An unknown WS path is rejected."""
    app = _make_echo_ws()
    client = TestClient(app)
    with pytest.raises((WebSocketDisconnect, Exception)):  # noqa: PT011
        with client.websocket_connect("/nonexistent"):
            pass
