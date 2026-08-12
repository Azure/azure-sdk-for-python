# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Voice-only WebSocket route and upgrade-context regressions."""

import asyncio
import json

import pytest
from opentelemetry import baggage, trace
from starlette.applications import Starlette
from starlette.routing import Host, Mount, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.invocations.voice import SessionReady, VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice import _voice_host as voice_host_module
from azure.ai.agentserver.invocations.voice._codec import MAX_FRAME_BYTES


def _session_start_frame() -> dict[str, object]:
    return {
        "type": "session.start",
        "id": "m_start",
        "ts": "2026-08-12T00:00:00Z",
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
    }


def _websocket_with_headers(headers: list[tuple[bytes, bytes]]) -> WebSocket:
    async def receive():
        return {"type": "websocket.disconnect", "code": 1000}

    async def send(_message):
        return None

    return WebSocket(
        {
            "type": "websocket",
            "asgi": {"version": "3.0", "spec_version": "2.4"},
            "scheme": "ws",
            "path": "/invocations_ws",
            "raw_path": b"/invocations_ws",
            "query_string": b"",
            "headers": headers,
            "client": ("test", 1),
            "server": ("testserver", 80),
            "subprotocols": [],
            "state": {},
        },
        receive,
        send,
    )


def test_voice_route_rejects_same_scope_exact_conflict():
    async def conflicting_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()

    with pytest.raises(RuntimeError, match="route is already registered"):
        VoiceAgentServerHost(
            routes=[WebSocketRoute("/invocations_ws", conflicting_endpoint)],
            configure_observability=None,
        )


def test_voice_route_precedes_same_scope_catch_all():
    selected = []

    async def catch_all(websocket: WebSocket) -> None:
        selected.append("catch_all")
        await websocket.accept()
        await websocket.send_text("catch_all")

    app = VoiceAgentServerHost(
        routes=[WebSocketRoute("/{path:path}", catch_all)],
        configure_observability=None,
    )

    @app.on_session_start
    async def on_session_start(session, _event):
        selected.append("voice")
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"

    assert selected == ["voice"]


@pytest.mark.parametrize("authority_kind", ["host", "mount"])
def test_voice_route_preserves_host_and_mount_authority(authority_kind):
    async def authority_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("authority")

    nested = Starlette(routes=[WebSocketRoute("/invocations_ws", authority_endpoint)])
    authority_route = Host("tenant.example", app=nested) if authority_kind == "host" else Mount("/", app=nested)
    app = VoiceAgentServerHost(routes=[authority_route], configure_observability=None)

    headers = {"host": "tenant.example"} if authority_kind == "host" else {}
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        assert websocket.receive_text() == "authority"


def test_voice_upgrade_binds_context_and_returns_server_header(monkeypatch):
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session-1")
    observed = []
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        platform_context = get_request_context()
        span_context = trace.get_current_span().get_span_context()
        observed.append(
            {
                "call_id": platform_context.call_id,
                "user_id": platform_context.user_id,
                "session_id": platform_context.session_id,
                "trace_id": f"{span_context.trace_id:032x}",
                "request_id": baggage.get_baggage("x_request_id"),
            }
        )
        await session.send(SessionReady())

    expected_trace_id = "11111111111111111111111111111111"
    headers = {
        "x-agent-foundry-call-id": "call-1",
        "x-agent-user-id": "user-1",
        "x-request-id": "request-1",
        "traceparent": f"00-{expected_trace_id}-2222222222222222-01",
    }
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        websocket.send_text(json.dumps(_session_start_frame()))
        assert websocket.receive_json()["type"] == "session.ready"
        response_headers = dict(websocket.extra_headers or [])
        assert response_headers[b"x-platform-server"]

    assert observed == [
        {
            "call_id": "call-1",
            "user_id": "user-1",
            "session_id": "session-1",
            "trace_id": expected_trace_id,
            "request_id": "request-1",
        }
    ]
    platform_context = get_request_context()
    assert (platform_context.call_id, platform_context.user_id, platform_context.session_id) == (None, None, None)


def test_voice_upgrade_preserves_repeated_w3c_headers():
    expected_trace_id = "11111111111111111111111111111111"
    websocket = _websocket_with_headers(
        [
            (b"traceparent", f"00-{expected_trace_id}-2222222222222222-01".encode()),
            (b"tracestate", b"vendor1=value1"),
            (b"tracestate", b"vendor2=value2"),
            (b"baggage", b"tenant.id=tenant-1"),
            (b"baggage", b"region=west"),
            (b"x-request-id", b""),
            (b"x-request-id", b"request-first"),
            (b"x-request-id", b"request-second"),
        ]
    )

    context = voice_host_module._extract_voice_websocket_context(websocket)  # pylint: disable=protected-access
    span_context = trace.get_current_span(context).get_span_context()

    assert f"{span_context.trace_id:032x}" == expected_trace_id
    assert span_context.trace_state.get("vendor1") == "value1"
    assert span_context.trace_state.get("vendor2") == "value2"
    assert baggage.get_baggage("tenant.id", context=context) == "tenant-1"
    assert baggage.get_baggage("region", context=context) == "west"
    assert baggage.get_baggage("x_request_id", context=context) == "request-first"


def test_voice_upgrade_rejects_duplicate_traceparent():
    websocket = _websocket_with_headers(
        [
            (b"traceparent", b"00-11111111111111111111111111111111-2222222222222222-01"),
            (b"traceparent", b"00-33333333333333333333333333333333-4444444444444444-01"),
        ]
    )

    context = voice_host_module._extract_voice_websocket_context(websocket)  # pylint: disable=protected-access
    assert trace.get_current_span(context).get_span_context().trace_id == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("inbound", "expected_code"),
    [
        ({"type": "websocket.receive", "text": "not-json"}, 1002),
        ({"type": "websocket.receive", "bytes": b"binary"}, 1003),
        ({"type": "websocket.receive", "text": "x" * (MAX_FRAME_BYTES + 1)}, 1009),
    ],
)
async def test_voice_selected_close_survives_cancellation_during_send(inbound, expected_code):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [{"type": "websocket.connect"}, inbound]
    close_started = asyncio.Event()
    close_events = []
    sent_messages = []

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        await asyncio.Future()

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.close":
            close_started.set()
            await asyncio.Future()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(close_started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    wire_closes = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in wire_closes] == [expected_code]
    assert close_events == [(expected_code, "cancelled")]


@pytest.mark.asyncio
@pytest.mark.parametrize("expected_code", [1002, 1003, 1009])
async def test_voice_selected_close_survives_transport_failure(expected_code):
    app = VoiceAgentServerHost(configure_observability=None)
    if expected_code == 1002:
        inbound = {"type": "websocket.receive", "text": "not-json"}
    elif expected_code == 1003:
        inbound = {"type": "websocket.receive", "bytes": b"binary"}
    else:
        inbound = {"type": "websocket.receive", "text": "x" * (MAX_FRAME_BYTES + 1)}
    inbound_events = [{"type": "websocket.connect"}, inbound]
    close_events = []
    sent_messages = []

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.close":
            raise OSError("transport close failed")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    await app._ws_endpoint(websocket)  # pylint: disable=protected-access

    wire_closes = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in wire_closes] == [expected_code]
    assert close_events == [(expected_code, None)]


@pytest.mark.asyncio
async def test_voice_close_event_precedes_repeated_cancellation_during_finalization():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [{"type": "websocket.connect"}]
    handler_waiting = asyncio.Event()
    final_close_started = asyncio.Event()
    close_events = []

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        handler_waiting.set()
        await asyncio.Future()

    async def send(message):
        if message["type"] == "websocket.close":
            final_close_started.set()
            await asyncio.Future()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(handler_waiting.wait(), timeout=1)
        task.cancel()
        await asyncio.wait_for(final_close_started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    assert close_events == [(1011, "cancelled")]
