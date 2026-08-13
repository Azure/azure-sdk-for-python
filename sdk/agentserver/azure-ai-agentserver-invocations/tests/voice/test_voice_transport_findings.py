# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Voice-only WebSocket route and upgrade-context regressions."""

import asyncio
import json
import logging

import pytest
import opentelemetry.propagate as otel_propagate
from opentelemetry import baggage, trace
from starlette.applications import Starlette
from starlette.routing import Host, Mount, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.invocations.voice import Session, SessionReady, VoiceAgentServerHost
from azure.ai.agentserver.invocations.voice import _session as session_module
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


async def _finish_close_attempts(baseline):
    outstanding = set(session_module._CLOSE_ATTEMPTS) - baseline  # pylint: disable=protected-access
    if outstanding:
        await asyncio.wait_for(asyncio.gather(*outstanding, return_exceptions=True), timeout=1)
    await asyncio.sleep(0)
    assert set(session_module._CLOSE_ATTEMPTS) == baseline  # pylint: disable=protected-access


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


def test_voice_route_rejects_late_same_scope_exact_conflict():
    async def conflicting_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()

    app = VoiceAgentServerHost(configure_observability=None)
    app.routes.insert(0, WebSocketRoute("/invocations_ws", conflicting_endpoint))

    with pytest.raises(RuntimeError, match="route is already registered"):
        with TestClient(app).websocket_connect("/invocations_ws"):
            pass


def test_voice_route_precedes_late_same_scope_catch_all():
    selected = []

    async def catch_all(websocket: WebSocket) -> None:
        selected.append("catch_all")
        await websocket.accept()
        await websocket.send_text("catch_all")

    app = VoiceAgentServerHost(configure_observability=None)
    app.routes.insert(0, WebSocketRoute("/{path:path}", catch_all))

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


def test_voice_route_preserves_live_matching_and_nonmatching_host_authority():
    async def authority_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_text("authority")

    app = VoiceAgentServerHost(configure_observability=None)
    app.routes.insert(
        0,
        Host(
            "tenant.example",
            app=Starlette(routes=[WebSocketRoute("/invocations_ws", authority_endpoint)]),
        ),
    )

    with TestClient(app).websocket_connect("/invocations_ws", headers={"host": "tenant.example"}) as websocket:
        assert websocket.receive_text() == "authority"

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws", headers={"host": "other.example"}) as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"


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


def test_voice_upgrade_ignores_context_extraction_failure(monkeypatch):
    def fail_extract(*_args, **_kwargs):
        raise RuntimeError("context extraction failed")

    monkeypatch.setattr(otel_propagate, "extract", fail_extract)
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"


def test_voice_upgrade_ignores_context_attachment_failure(monkeypatch):
    def fail_attach(_context):
        raise RuntimeError("context attachment failed")

    monkeypatch.setattr(voice_host_module._otel_context, "attach", fail_attach)
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"


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
    close_release = asyncio.Event()
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
            await close_release.wait()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(close_started.wait(), timeout=1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=1)
    finally:
        close_release.set()
        if not task.done():
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        await _finish_close_attempts(baseline_attempts)

    wire_closes = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in wire_closes] == [expected_code]
    assert close_events == [(expected_code, "cancelled")]
    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access


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

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    wire_closes = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert [message["code"] for message in wire_closes] == [expected_code]
    assert close_events == [(expected_code, None)]


@pytest.mark.asyncio
async def test_voice_stalled_close_releases_endpoint_session_and_context(monkeypatch):
    monkeypatch.setattr(session_module, "CLOSE_TIMEOUT_SECONDS", 0.01)
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    close_started = asyncio.Event()
    close_release = asyncio.Event()
    close_cancelled = False
    close_contexts = []
    close_session_bindings = []

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        if message["type"] != "websocket.close":
            return
        close_contexts.append(get_request_context().session_id)
        close_session_bindings.append(Session._current(websocket))  # pylint: disable=protected-access
        close_started.set()
        try:
            await close_release.wait()
        except asyncio.CancelledError:
            nonlocal close_cancelled
            close_cancelled = True
            raise

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(close_started.wait(), timeout=1)
        await asyncio.wait_for(endpoint_task, timeout=1)

        outstanding = set(session_module._CLOSE_ATTEMPTS) - baseline_attempts  # pylint: disable=protected-access
        assert len(outstanding) == 1
        assert not next(iter(outstanding)).done()
        assert Session._current(websocket) is None  # pylint: disable=protected-access
        assert close_contexts == [None]
        assert close_session_bindings == [None]
        assert close_cancelled is False
    finally:
        close_release.set()
        if not endpoint_task.done():
            endpoint_task.cancel()
            await asyncio.gather(endpoint_task, return_exceptions=True)
        await _finish_close_attempts(baseline_attempts)

    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_voice_accept_unknown_commit_fails_closed():
    app = VoiceAgentServerHost(configure_observability=None)
    sent_messages = []
    close_events = []

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.accept":
            raise OSError("accept failed after commit")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert sent_messages[-1]["code"] == 1011
    assert close_events == [(1011, "accept_failed")]
    assert Session._current(websocket) is None  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_voice_peer_disconnect_closes_write_gate_before_callback():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    late_send_errors = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(session, _event):
        with pytest.raises(RuntimeError, match="terminating") as raised:
            await session.send(SessionReady())
        late_send_errors.append(raised.value)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert len(late_send_errors) == 1
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_abnormal_disconnect_code_is_observed_but_never_sent():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1006},
    ]
    observed_codes = []
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, event):
        observed_codes.append(event.code)

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

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert observed_codes == [1006]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert close_events == [(1006, None)]


@pytest.mark.asyncio
async def test_voice_close_deadline_covers_blocked_application_send(monkeypatch):
    monkeypatch.setattr(session_module, "CLOSE_TIMEOUT_SECONDS", 0.01)
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    send_started = asyncio.Event()
    send_release = asyncio.Event()
    send_tasks = []
    retained_sessions = []
    sent_messages = []
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    @app.on_session_start
    async def on_session_start(session, _event):
        retained_sessions.append(session)
        send_tasks.append(asyncio.create_task(session.send(SessionReady())))
        await send_started.wait()

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            send_started.set()
            await send_release.wait()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    try:
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access
        assert Session._current(websocket) is None  # pylint: disable=protected-access
        with pytest.raises(RuntimeError, match="terminating"):
            await retained_sessions[0].send(SessionReady())
        assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.send"]
    finally:
        send_release.set()
        await asyncio.gather(*send_tasks, return_exceptions=True)
        await _finish_close_attempts(baseline_attempts)


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
            await asyncio.wait_for(task, timeout=1)
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
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

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
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert raised.value.args == ("callback-self-cancel",)
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_wrapped_by_handler():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    callback_started = asyncio.Event()
    captured_cancellations = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(_session, _event):
        callback_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as exc:
            captured_cancellations.append(exc)
            raise RuntimeError("handler wrapped cancellation") from exc

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(callback_started.wait(), timeout=1)
    endpoint_task.cancel("shutdown-identity")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert len(captured_cancellations) == 1
    assert raised.value is captured_cancellations[0]
    assert raised.value.args == ("shutdown-identity",)
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_wrapped_during_accept():
    app = VoiceAgentServerHost(configure_observability=None)
    accept_started = asyncio.Event()
    captured_cancellations = []

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        if message["type"] == "websocket.accept":
            accept_started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError as exc:
                captured_cancellations.append(exc)
                raise OSError("accept wrapped cancellation") from exc

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(accept_started.wait(), timeout=1)
    endpoint_task.cancel("accept-wrapper-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert len(captured_cancellations) == 1
    assert raised.value is captured_cancellations[0]
    assert raised.value.args == ("accept-wrapper-cancel",)


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

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

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
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access
    finally:
        voice_host_module.logger.removeHandler(handler)
        voice_host_module.logger.setLevel(old_level)

    assert close_events == [(expected_code, "internal_error")]
    close_messages = [message for message in sent_messages if message["type"] == "websocket.close"]
    expected_wire_codes = [expected_code] if callback_kind == "event" else []
    assert [message["code"] for message in close_messages] == expected_wire_codes


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
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

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
        await asyncio.wait_for(asyncio.gather(*generation_tasks), timeout=1)
    finally:
        release_send.set()
        if not endpoint_task.done():
            endpoint_task.cancel()
            await asyncio.wait_for(asyncio.gather(endpoint_task, return_exceptions=True), timeout=1)
        for generation_task in generation_tasks:
            if not generation_task.done():
                generation_task.cancel()
        await asyncio.wait_for(asyncio.gather(*generation_tasks, return_exceptions=True), timeout=1)
        await _finish_close_attempts(baseline_attempts)

    assert maximum_active_writes == 1
    assert [message["type"] for message in sent_messages] == [
        "websocket.accept",
        "websocket.send",
        "websocket.close",
    ]
    assert sent_messages[-1]["code"] == 1002


@pytest.mark.asyncio
async def test_voice_cleanup_marks_session_terminal_before_cancelling_application_work():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    generation_started = asyncio.Event()
    generation_tasks = []
    late_send_errors = []
    sent_messages = []
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    async def generation(session):
        generation_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            try:
                await session.send(SessionReady())
            except RuntimeError as exc:
                late_send_errors.append(exc)

    @app.on_session_start
    async def on_session_start(session, _event):
        generation_tasks.append(asyncio.create_task(generation(session)))
        await generation_started.wait()

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        for task in generation_tasks:
            task.cancel()

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    try:
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access
        await asyncio.wait_for(asyncio.gather(*generation_tasks), timeout=1)
    finally:
        for generation_task in generation_tasks:
            if not generation_task.done():
                generation_task.cancel()
        await asyncio.wait_for(asyncio.gather(*generation_tasks, return_exceptions=True), timeout=1)
        await _finish_close_attempts(baseline_attempts)

    assert len(late_send_errors) == 1
    assert str(late_send_errors[0]) == "Voice Session is terminating"
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]


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
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

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
        await _finish_close_attempts(baseline_attempts)


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

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert close_events == [(1001, "internal_error")]
    close_messages = [message for message in sent_messages if message["type"] == "websocket.close"]
    assert close_messages == []
