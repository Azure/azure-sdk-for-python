# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the structured close-event log line emitted by ``/invocations_ws``.

Parity with :mod:`tests.test_request_id` — verifies the spec's required
fields (``azure.ai.agentserver.invocations_ws.session_id``, ``azure.ai.agentserver.invocations_ws.close_code``, ``azure.ai.agentserver.invocations_ws.duration_ms``) appear
on every connection close, and that handler exception details are NOT
leaked into the structured payload.
"""
import asyncio
import logging

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants

from conftest import (
    _make_echo_ws_app,
    _make_failing_ws_app,
    _records_with_ws_extras,
)


# ---------------------------------------------------------------------------
# Required fields on every close-event
# ---------------------------------------------------------------------------


def test_ws_close_event_log_contains_required_fields(caplog):
    """The close-event log line carries ws.session_id, ws.close_code, ws.duration_ms."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            assert ws.receive_text() == "ping"

    matches = _records_with_ws_extras(caplog.records)
    assert matches, "expected a structured close-event log record"
    rec = matches[-1]

    session_id = getattr(rec, "azure.ai.agentserver.invocations_ws.session_id")
    close_code = getattr(rec, "azure.ai.agentserver.invocations_ws.close_code")
    duration_ms = getattr(rec, "azure.ai.agentserver.invocations_ws.duration_ms")

    assert isinstance(session_id, str) and session_id  # generated UUID
    assert close_code == InvocationsWSConstants.CLOSE_NORMAL
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


def test_ws_close_event_duration_is_non_negative(caplog):
    """``azure.ai.agentserver.invocations_ws.duration_ms`` is a non-negative integer derived from a monotonic clock."""
    app = _make_echo_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("ping")
            ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    duration_ms = getattr(matches[-1], "azure.ai.agentserver.invocations_ws.duration_ms")
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


# ---------------------------------------------------------------------------
# Close codes on the close-event
# ---------------------------------------------------------------------------


def test_ws_close_event_on_handler_exception_records_1011(caplog):
    """Handler raising → close-event log records ws.close_code = 1011."""
    app = _make_failing_ws_app()
    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.send_text("trigger")
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "azure.ai.agentserver.invocations_ws.close_code") == 1011


def test_ws_close_event_records_application_selected_code(caplog):
    """A handler-selected wire close code is preserved in structured diagnostics."""
    app = InvocationAgentServerHost(configure_observability=None)

    @app.ws_handler
    async def handler(websocket):
        await websocket.close(code=1008, reason="Policy violation")

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                ws.receive_text()

    assert exc_info.value.code == 1008
    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "azure.ai.agentserver.invocations_ws.close_code") == 1008


def test_ws_close_event_records_peer_code_when_iter_text_swallows_disconnect(caplog):
    """The SDK tracks peer disconnects below Starlette's swallowing iterators."""
    app = InvocationAgentServerHost(configure_observability=None)

    @app.ws_handler
    async def handler(websocket):
        async for _ in websocket.iter_text():
            pass

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as websocket:
            websocket.close(code=1008)

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "azure.ai.agentserver.invocations_ws.close_code") == 1008


def test_ws_close_event_preserves_sent_code_when_handler_then_raises(caplog):
    """A successful application close remains the wire code after a later error."""
    app = InvocationAgentServerHost(configure_observability=None)

    @app.ws_handler
    async def handler(websocket):
        await websocket.close(code=1008, reason="Policy violation")
        raise RuntimeError("post-close failure")

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with client.websocket_connect("/invocations_ws") as ws:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                ws.receive_text()

    assert exc_info.value.code == 1008
    matches = _records_with_ws_extras(caplog.records)
    assert matches
    record = matches[-1]
    assert getattr(record, InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE) == 1008
    assert getattr(record, InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE_SOURCE) == "application"
    assert getattr(record, InvocationsWSConstants.ATTR_SPAN_ERROR_CODE) == "internal_error"


def test_ws_close_event_preserves_code_when_cancelled_during_transport():
    """Cancellation after ASGI close handoff preserves the ambiguous committed code."""

    async def scenario() -> None:
        app = InvocationAgentServerHost(configure_observability=None)

        @app.ws_handler
        async def handler(websocket):
            await websocket.close(code=4321, reason="Application shutdown")

        close_started = asyncio.Event()
        sent: list[dict] = []

        async def send(message):
            sent.append(dict(message))
            if message["type"] == "websocket.close":
                close_started.set()
                await asyncio.Event().wait()

        async def receive():
            return {"type": "websocket.connect"}

        scope = {
            "type": "websocket",
            "path": "/invocations_ws",
            "headers": [],
            "query_string": b"",
            "scheme": "ws",
            "server": ("test", 80),
            "client": ("test", 1),
            "root_path": "",
            "subprotocols": [],
            "state": {},
        }
        websocket = WebSocket(scope, receive, send)
        close_events: list[tuple[int, str, str | None]] = []
        app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
            lambda _session_id, close_code, _duration_ms, *, close_code_source="unknown", error_code=None: close_events.append(
                (close_code, close_code_source, error_code)
            )
        )

        endpoint = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
        await close_started.wait()
        endpoint.cancel()
        with pytest.raises(asyncio.CancelledError):
            await endpoint

        assert sent[-1]["type"] == "websocket.close"
        assert sent[-1]["code"] == 4321
        assert close_events == [(4321, "application_ambiguous", "cancelled")]

    asyncio.run(scenario())


def test_ws_close_event_first_terminal_source_wins() -> None:
    """A peer disconnect observed before an application close remains authoritative."""

    async def scenario() -> None:
        app = InvocationAgentServerHost(configure_observability=None)

        @app.ws_handler
        async def handler(websocket):
            await websocket.receive()
            await websocket.close(code=4321)

        incoming = iter(
            (
                {"type": "websocket.connect"},
                {"type": "websocket.disconnect", "code": 1001},
            )
        )

        async def receive():
            return next(incoming)

        async def send(_message):
            return None

        scope = {
            "type": "websocket",
            "path": "/invocations_ws",
            "headers": [],
            "query_string": b"",
            "scheme": "ws",
            "server": ("test", 80),
            "client": ("test", 1),
            "root_path": "",
            "subprotocols": [],
            "state": {},
        }
        websocket = WebSocket(scope, receive, send)
        close_events: list[tuple[int, str]] = []
        app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
            lambda _session_id, close_code, _duration_ms, *, close_code_source="unknown", error_code=None: close_events.append(
                (close_code, close_code_source)
            )
        )

        await app._ws_endpoint(websocket)  # pylint: disable=protected-access

        assert close_events == [(1001, "peer")]

    asyncio.run(scenario())


# ---------------------------------------------------------------------------
# Exception details are NOT leaked into the structured payload
# (parity with test_error_hides_details_by_default)
# ---------------------------------------------------------------------------


def test_ws_close_event_log_does_not_leak_exception_message(caplog):
    """The close-event log line does NOT carry the handler exception text."""
    app = _make_failing_ws_app()
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
    assert not hasattr(rec, "azure.ai.agentserver.invocations_ws.error.message")
    # And the message itself does not embed the raw exception text.
    assert "boom" not in rec.getMessage()


def test_ws_disconnect_with_code_zero_falls_back_to_normal_close(caplog):
    """A ``WebSocketDisconnect(code=0)`` is reported as the normal close code (1000).

    Some clients/proxies surface a falsy ``code`` on the disconnect; the SDK
    treats it as a clean close rather than as 1011.
    """
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket):  # noqa: ARG001
        raise WebSocketDisconnect(code=0)

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "azure.ai.agentserver.invocations_ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL


def test_ws_disconnect_with_code_none_falls_back_to_normal_close(caplog):
    """A ``WebSocketDisconnect(code=None)`` is reported as 1000."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket):  # noqa: ARG001
        raise WebSocketDisconnect(code=None)  # type: ignore[arg-type]

    client = TestClient(app)
    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invocations_ws") as ws:
                ws.receive_text()

    matches = _records_with_ws_extras(caplog.records)
    assert matches
    assert getattr(matches[-1], "azure.ai.agentserver.invocations_ws.close_code") == InvocationsWSConstants.CLOSE_NORMAL
