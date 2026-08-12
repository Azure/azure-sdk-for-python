# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Voice-only WebSocket route and upgrade-context regressions."""

import asyncio
import json
import logging

import pytest
from opentelemetry import baggage, trace
from starlette.applications import Starlette
from starlette.routing import Host, Mount, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.invocations.voice import Session, SessionReady, VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice import _voice_host as voice_host_module
from azure.ai.agentserver.invocations.voice._codec import MAX_FRAME_BYTES


class _LoggingBaseException(BaseException):
    pass


class _RaisingLogHandler(logging.Handler):
    def __init__(self, failure):
        super().__init__()
        self.failure = failure

    def emit(self, _record):
        raise self.failure


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


def test_voice_route_tracks_live_authority_add_remove_and_reorder():
    async def first_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("first")

    async def second_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("second")

    first = Mount("/", app=Starlette(routes=[WebSocketRoute("/invocations_ws", first_endpoint)]))
    second = Mount("/", app=Starlette(routes=[WebSocketRoute("/invocations_ws", second_endpoint)]))
    app = VoiceAgentServerHost(configure_observability=None)

    app.routes.extend((first, second))
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        assert websocket.receive_text() == "first"

    app.routes.remove(first)
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        assert websocket.receive_text() == "second"

    app.routes.insert(1, first)
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        assert websocket.receive_text() == "first"


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
    assert close_events == [(expected_code, None)]


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
async def test_voice_handler_cancellation_does_not_start_new_close_io():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [{"type": "websocket.connect"}]
    handler_waiting = asyncio.Event()
    close_events = []
    sent_messages = []

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        handler_waiting.set()
        await asyncio.Future()

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(handler_waiting.wait(), timeout=1)
        task.cancel("shutdown")
        with pytest.raises(asyncio.CancelledError) as raised:
            await task
    finally:
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    assert raised.value.args == ("shutdown",)
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_preserves_explicit_handler_cancellation_identity():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    cancellation = asyncio.CancelledError("handler cancellation")
    close_events = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(_session, _event):
        raise cancellation

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await app._ws_endpoint(websocket)  # pylint: disable=protected-access

    assert raised.value is cancellation
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_materializes_callback_self_cancellation_before_finalization():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    close_events = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(_session, _event):
        asyncio.current_task().cancel("callback-self-cancel")

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    with pytest.raises(asyncio.CancelledError) as raised:
        await app._ws_endpoint(websocket)  # pylint: disable=protected-access

    assert raised.value.args == ("callback-self-cancel",)
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_converted_to_transport_error():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    close_started = asyncio.Event()
    close_events = []

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        if message["type"] == "websocket.close":
            close_started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError as exc:
                raise OSError("transport converted cancellation") from exc

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(close_started.wait(), timeout=1)
    task.cancel("during-close")
    with pytest.raises(asyncio.CancelledError) as raised:
        await task

    assert raised.value.args == ("during-close",)
    transport_wrapper = raised.value.__cause__
    assert isinstance(transport_wrapper, WebSocketDisconnect)
    transport_error = transport_wrapper.__context__
    assert isinstance(transport_error, OSError)
    assert transport_error.__cause__ is None
    assert transport_error.__context__ is None
    assert close_events == [(1002, None)]


@pytest.mark.asyncio
@pytest.mark.parametrize("telemetry_error", [RuntimeError("telemetry"), asyncio.CancelledError("telemetry")])
async def test_voice_telemetry_failure_does_not_prevent_internal_error_close(telemetry_error):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    sent_messages = []

    @app.on_session_start
    async def on_session_start(_session, _event):
        raise RuntimeError("callback failed")

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    def fail_telemetry(*_args, **_kwargs):
        raise telemetry_error

    app._emit_close_event = fail_telemetry  # type: ignore[method-assign]  # pylint: disable=protected-access

    await app._ws_endpoint(websocket)  # pylint: disable=protected-access

    close_messages = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in close_messages] == [1011]


@pytest.mark.asyncio
@pytest.mark.parametrize("callback_kind", ["event", "disconnect"])
@pytest.mark.parametrize(
    "logging_failure",
    [RuntimeError("logging"), _LoggingBaseException("logging"), asyncio.CancelledError("logging")],
)
async def test_voice_logging_failure_preserves_callback_outcome(callback_kind, logging_failure):
    app = VoiceAgentServerHost(configure_observability=None)
    if callback_kind == "event":
        inbound_events = [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        ]
        expected_code = 1011

        @app.on_session_start
        async def on_session_start(_session, _event):
            raise ValueError("callback failed")

    else:
        inbound_events = [
            {"type": "websocket.connect"},
            {"type": "websocket.disconnect", "code": 1001},
        ]
        expected_code = 1001

        @app.on_disconnect
        async def on_disconnect(_session, _event):
            raise ValueError("callback failed")

    close_events = []
    sent_messages = []

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )
    handler = _RaisingLogHandler(logging_failure)
    old_level = voice_host_module.logger.level
    voice_host_module.logger.setLevel(logging.ERROR)
    voice_host_module.logger.addHandler(handler)
    try:
        await app._ws_endpoint(websocket)  # pylint: disable=protected-access
    finally:
        voice_host_module.logger.removeHandler(handler)
        voice_host_module.logger.setLevel(old_level)

    assert close_events == [(expected_code, "internal_error")]
    close_messages = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in close_messages] == [expected_code]


@pytest.mark.asyncio
async def test_voice_cleanup_precedes_close_serialized_behind_application_send():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    send_started = asyncio.Event()
    release_send = asyncio.Event()
    close_started = asyncio.Event()
    terminating = asyncio.Event()
    sent_messages = []
    generation_tasks = []
    active_writes = 0
    maximum_active_writes = 0

    @app.on_session_start
    async def on_session_start(session, _event):
        generation_tasks.append(asyncio.create_task(session.send(SessionReady())))
        await asyncio.wait_for(send_started.wait(), timeout=1)

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        terminating.set()

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        await asyncio.Future()

    async def send(message):
        nonlocal active_writes, maximum_active_writes
        active_writes += 1
        maximum_active_writes = max(maximum_active_writes, active_writes)
        sent_messages.append(message)
        try:
            if message["type"] == "websocket.send":
                send_started.set()
                await release_send.wait()
            elif message["type"] == "websocket.close":
                close_started.set()
        finally:
            active_writes -= 1

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(terminating.wait(), timeout=1)
        await asyncio.sleep(0)
        assert not close_started.is_set()

        release_send.set()
        await asyncio.wait_for(endpoint_task, timeout=1)
        await asyncio.gather(*generation_tasks)
    finally:
        release_send.set()
        if not endpoint_task.done():
            endpoint_task.cancel()
            await asyncio.gather(endpoint_task, return_exceptions=True)
        await asyncio.gather(*generation_tasks, return_exceptions=True)

    assert maximum_active_writes == 1
    assert [message["type"] for message in sent_messages] == [
        "websocket.accept",
        "websocket.send",
        "websocket.close",
    ]
    assert sent_messages[-1]["code"] == 1002


@pytest.mark.asyncio
async def test_voice_endpoint_cancellation_does_not_wait_for_blocked_application_send():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    send_started = asyncio.Event()
    release_send = asyncio.Event()
    terminating = asyncio.Event()
    close_events = []
    sent_messages = []
    generation_tasks = []
    retained_sessions = []

    @app.on_session_start
    async def on_session_start(session, _event):
        retained_sessions.append(session)
        generation_tasks.append(asyncio.create_task(session.send(SessionReady())))
        await asyncio.wait_for(send_started.wait(), timeout=1)

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        terminating.set()

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        await asyncio.Future()

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            send_started.set()
            await release_send.wait()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(terminating.wait(), timeout=1)
        endpoint_task.cancel("shutdown")
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(endpoint_task, timeout=1)

        assert raised.value.args == ("shutdown",)
        assert Session._current(websocket) is None  # pylint: disable=protected-access
        assert close_events == [(1002, "cancelled")]
        assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.send"]
        with pytest.raises(RuntimeError, match="terminating"):
            await retained_sessions[0].send(SessionReady())
    finally:
        release_send.set()
        if not endpoint_task.done():
            endpoint_task.cancel()
            await asyncio.gather(endpoint_task, return_exceptions=True)
        await asyncio.gather(*generation_tasks, return_exceptions=True)


@pytest.mark.asyncio
async def test_voice_disconnect_callback_failure_preserves_peer_close_code():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001, "reason": "going away"},
    ]
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        raise RuntimeError("disconnect callback failed")

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    await app._ws_endpoint(websocket)  # pylint: disable=protected-access

    assert close_events == [(1001, "internal_error")]
    close_messages = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in close_messages] == [1001]
