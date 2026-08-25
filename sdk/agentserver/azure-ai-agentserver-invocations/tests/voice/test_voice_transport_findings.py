# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Voice-only WebSocket route and upgrade-context regressions."""

import asyncio
import json
import logging
import sys

import pytest
import opentelemetry.propagate as otel_propagate
from opentelemetry import baggage, trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from starlette.applications import Starlette
from starlette.routing import Host, Mount, WebSocketRoute
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.core import get_request_context
from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor
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


def _live_voice_send_tasks():
    return [task for task in asyncio.all_tasks() if task.get_name() == "voice_websocket_send" and not task.done()]


def _live_voice_transport_tasks():
    return [task for task in asyncio.all_tasks() if task.get_name() == "voice_websocket_transport" and not task.done()]


async def _raise_callback_local_cancellation(source):
    if source == "wait_for":
        await asyncio.wait_for(asyncio.Future(), timeout=0)
    elif source == "timeout":
        timeout = getattr(asyncio, "timeout", None)
        if timeout is None:
            pytest.skip("asyncio.timeout requires Python 3.11")
        async with timeout(0):
            await asyncio.Future()
    else:
        child = asyncio.create_task(asyncio.Future())
        child.cancel("callback-child")
        try:
            await child
        except asyncio.CancelledError as cancellation:
            raise RuntimeError("callback wrapped its child cancellation") from cancellation


def _tracks_task_cancellation_requests():
    return sys.version_info >= (3, 11)


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


def test_voice_callback_span_is_exported_with_a365_session_context(monkeypatch):
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "voice-session-1")
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(_FoundryEnrichmentSpanProcessor(project_id="project-123"))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    customer_tracer = trace.get_tracer("customer.voice.agent", tracer_provider=provider)
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        with customer_tracer.start_as_current_span("customer.voice.session_start"):
            await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "customer.voice.session_start"
    assert spans[0].attributes["microsoft.session.id"] == "voice-session-1"
    assert spans[0].attributes["microsoft.foundry.project.id"] == "project-123"


@pytest.mark.asyncio
async def test_voice_cleanup_callbacks_and_diagnostics_keep_connection_context(monkeypatch):
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "cleanup-session")
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    expected_trace_id = "11111111111111111111111111111111"
    observations = []

    async def receive():
        return inbound_events.pop(0)

    async def send(_message):
        return None

    websocket = _websocket_with_headers(
        [
            (b"x-agent-foundry-call-id", b"cleanup-call"),
            (b"x-agent-user-id", b"cleanup-user"),
            (b"x-request-id", b"cleanup-request"),
            (b"traceparent", f"00-{expected_trace_id}-2222222222222222-01".encode()),
        ]
    )
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    def observe(stage, session=None):
        platform_context = get_request_context()
        span_context = trace.get_current_span().get_span_context()
        observations.append(
            (
                stage,
                platform_context.call_id,
                platform_context.user_id,
                platform_context.session_id,
                baggage.get_baggage("x_request_id"),
                f"{span_context.trace_id:032x}",
            )
        )
        if session is not None:
            assert Session._current(websocket) is None  # pylint: disable=protected-access

    @app.on_connection_terminating
    def on_connection_terminating(session):
        observe("terminating", session)

    @app.on_disconnect
    async def on_disconnect(session, _event):
        observe("disconnect", session)

    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, _code, _duration_ms, *, error_code=None: observe("telemetry")
    )

    baseline_platform_context = get_request_context()
    baseline_trace_id = trace.get_current_span().get_span_context().trace_id
    baseline_request_id = baggage.get_baggage("x_request_id")

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert observations == [
        ("terminating", "cleanup-call", "cleanup-user", "cleanup-session", "cleanup-request", expected_trace_id),
        ("disconnect", "cleanup-call", "cleanup-user", "cleanup-session", "cleanup-request", expected_trace_id),
        ("telemetry", "cleanup-call", "cleanup-user", "cleanup-session", "cleanup-request", expected_trace_id),
    ]
    platform_context = get_request_context()
    assert (
        platform_context.call_id,
        platform_context.user_id,
        platform_context.session_id,
        trace.get_current_span().get_span_context().trace_id,
        baggage.get_baggage("x_request_id"),
    ) == (
        baseline_platform_context.call_id,
        baseline_platform_context.user_id,
        baseline_platform_context.session_id,
        baseline_trace_id,
        baseline_request_id,
    )


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
async def test_voice_accept_local_timeout_is_not_connection_cancellation(monkeypatch):
    monkeypatch.setattr(voice_host_module, "_task_cancellation_requests", lambda: None)
    app = VoiceAgentServerHost(configure_observability=None)
    close_events = []
    sent_messages = []

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.accept":
            await asyncio.wait_for(asyncio.Future(), timeout=0)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert close_events == [(1011, "accept_failed")]


@pytest.mark.asyncio
async def test_voice_accept_direct_cancellation_emits_one_diagnostic_without_cleanup_or_close_io():
    app = VoiceAgentServerHost(configure_observability=None)
    accept_started = asyncio.Event()
    close_events = []
    terminating_sessions = []
    disconnects = []
    sent_messages = []
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event)

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.accept":
            accept_started.set()
            await asyncio.Future()

    websocket = _websocket_with_headers(
        [
            (b"x-agent-foundry-call-id", b"accept-call"),
            (b"traceparent", b"00-11111111111111111111111111111111-2222222222222222-01"),
        ]
    )
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    def emit_close_event(_session_id, code, _duration_ms, *, error_code=None):
        close_events.append(
            (
                code,
                error_code,
                get_request_context().call_id,
                f"{trace.get_current_span().get_span_context().trace_id:032x}",
            )
        )

    app._emit_close_event = emit_close_event  # type: ignore[method-assign]  # pylint: disable=protected-access

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(accept_started.wait(), timeout=1)
    endpoint_task.cancel("accept-direct-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert raised.value.args == (("accept-direct-cancel",) if sys.version_info >= (3, 11) else ())
    assert close_events == [(1011, "cancelled", "accept-call", "11111111111111111111111111111111")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert terminating_sessions == []
    assert disconnects == []
    assert Session._current(websocket) is None  # pylint: disable=protected-access
    assert set(session_module._CLOSE_ATTEMPTS) == baseline_attempts  # pylint: disable=protected-access
    assert get_request_context().call_id is None


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["wait_for", "timeout", "inner_task"])
async def test_voice_callback_local_cancellation_graph_is_internal_error(source):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    close_events = []
    disconnects = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(_session, _event):
        await _raise_callback_local_cancellation(source)

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event)

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert disconnects == []
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert sent_messages[-1]["code"] == 1011
    assert close_events == [(1011, "internal_error")]


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["wait_for", "timeout"])
async def test_voice_send_local_timeout_is_internal_error(source):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    close_events = []
    disconnects = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(session, _event):
        if source == "wait_for":
            await asyncio.wait_for(session.send(SessionReady()), timeout=0.01)
            return
        timeout = getattr(asyncio, "timeout", None)
        if timeout is None:
            pytest.skip("asyncio.timeout requires Python 3.11")
        async with timeout(0.01):
            await session.send(SessionReady())

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            await asyncio.Future()

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert disconnects == []
    assert [message["type"] for message in sent_messages] == [
        "websocket.accept",
        "websocket.send",
        "websocket.close",
    ]
    assert sent_messages[-1]["code"] == 1011
    assert close_events == [(1011, "internal_error")]
    assert _live_voice_send_tasks() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ["wait_for", "timeout", "inner_task"])
async def test_voice_disconnect_local_cancellation_graph_is_internal_error(source):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        await _raise_callback_local_cancellation(source)

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert close_events == [(1001, "internal_error")]


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_wrapped_by_disconnect_callback():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    callback_started = asyncio.Event()
    captured_cancellations = []
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        callback_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            captured_cancellations.append(cancellation)
            raise RuntimeError("disconnect wrapped cancellation") from cancellation

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(callback_started.wait(), timeout=1)
    endpoint_task.cancel("disconnect-owner-cancel")

    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    if _tracks_task_cancellation_requests():
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(captured_cancellations) == 1
        assert raised.value is captured_cancellations[0]
        assert raised.value.args == ("disconnect-owner-cancel",)
        assert endpoint_task.cancelled()
        assert close_events == [(1001, "cancelled")]
    else:
        await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(captured_cancellations) == 1
        assert not endpoint_task.cancelled()
        assert close_events == [(1001, "internal_error")]


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

    assert raised.value.args == (("shutdown",) if sys.version_info >= (3, 11) else ())
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

    if sys.version_info >= (3, 11):
        assert raised.value is cancellation
    else:
        assert raised.value.args == ()
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

    assert raised.value.args == (("callback-self-cancel",) if sys.version_info >= (3, 11) else ())
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
    close_events = []
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
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(callback_started.wait(), timeout=1)
    endpoint_task.cancel("shutdown-identity")

    if _tracks_task_cancellation_requests():
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(captured_cancellations) == 1
        assert raised.value is captured_cancellations[0]
        assert raised.value.args == ("shutdown-identity",)
        assert [message["type"] for message in sent_messages] == ["websocket.accept"]
        assert close_events == [(1011, "cancelled")]
    else:
        await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(captured_cancellations) == 1
        assert not endpoint_task.cancelled()
        assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
        assert close_events == [(1011, "internal_error")]


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_wrapped_during_accept_without_task_counter(monkeypatch):
    monkeypatch.setattr(voice_host_module, "_task_cancellation_requests", lambda: None)
    app = VoiceAgentServerHost(configure_observability=None)
    accept_started = asyncio.Event()
    captured_cancellations = []
    close_events = []
    sent_messages = []

    async def receive():
        return {"type": "websocket.connect"}

    async def send(message):
        sent_messages.append(message)
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
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(accept_started.wait(), timeout=1)
    endpoint_task.cancel("accept-wrapper-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)
    assert len(captured_cancellations) == 1
    assert captured_cancellations[0].args == ("accept-wrapper-cancel",)
    assert raised.value.args == (("accept-wrapper-cancel",) if sys.version_info >= (3, 11) else ())
    if sys.version_info >= (3, 11):
        assert raised.value is captured_cancellations[0]
    assert endpoint_task.cancelled()
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert close_events == [(1011, "cancelled")]
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_voice_recovers_cancellation_wrapped_during_receive_without_task_counter(monkeypatch):
    monkeypatch.setattr(voice_host_module, "_task_cancellation_requests", lambda: None)
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [{"type": "websocket.connect"}]
    receive_started = asyncio.Event()
    captured_cancellations = []
    wrapped_errors = []
    close_events = []
    sent_messages = []

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        receive_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            captured_cancellations.append(cancellation)
        error = OSError("receive wrapped cancellation")
        wrapped_errors.append(error)
        raise error

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(receive_started.wait(), timeout=1)
    endpoint_task.cancel("receive-wrapper-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)
    assert len(captured_cancellations) == 1
    assert captured_cancellations[0].args == ("receive-wrapper-cancel",)
    assert wrapped_errors[0].__cause__ is None
    assert wrapped_errors[0].__context__ is None
    assert raised.value.args == (("receive-wrapper-cancel",) if sys.version_info >= (3, 11) else ())
    assert endpoint_task.cancelled()
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert close_events == [(1011, "cancelled")]
    assert Session._current(websocket) is None  # pylint: disable=protected-access
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_transport_operation_construction_failure_closes_coroutine_and_allows_retry(monkeypatch):
    create_task = session_module.asyncio.create_task
    close_coroutine = session_module._close_coroutine  # pylint: disable=protected-access
    closed_coroutines = []
    attempts = 0

    def fail_once(coroutine, *, name=None):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("transport task construction failed")
        return create_task(coroutine, name=name)

    def track_close(coroutine):
        closed_coroutines.append(coroutine)
        close_coroutine(coroutine)

    async def operation(result):
        return result

    monkeypatch.setattr(session_module.asyncio, "create_task", fail_once)
    monkeypatch.setattr(session_module, "_close_coroutine", track_close)

    with pytest.raises(RuntimeError, match="transport task construction failed"):
        await session_module._run_transport_operation(operation("first"))  # pylint: disable=protected-access

    assert len(closed_coroutines) == 1
    assert (
        await session_module._run_transport_operation(operation("retry")) == "retry"
    )  # pylint: disable=protected-access
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_transport_operation_repeated_cancellation_drains_to_latest_owner():
    operation_started = asyncio.Event()
    first_cancellation_caught = asyncio.Event()
    captured_cancellations = []
    wrappers = []

    async def operation():
        operation_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as first_cancellation:
            captured_cancellations.append(first_cancellation)
            first_cancellation_caught.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as second_cancellation:
            captured_cancellations.append(second_cancellation)
            wrapper = OSError("transport wrapped terminal cancellation")
            wrappers.append(wrapper)
            raise wrapper from second_cancellation

    owner = asyncio.create_task(
        session_module._run_transport_operation(operation())  # pylint: disable=protected-access
    )
    await asyncio.wait_for(operation_started.wait(), timeout=1)
    owner.cancel("first-cancel")
    await asyncio.wait_for(first_cancellation_caught.wait(), timeout=1)
    owner.cancel("terminal-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(owner, timeout=1)

    assert [cancellation.args for cancellation in captured_cancellations] == [
        ("first-cancel",),
        ("terminal-cancel",),
    ]
    assert raised.value.args == (("terminal-cancel",) if sys.version_info >= (3, 11) else ())
    assert wrappers[0].__cause__ is captured_cancellations[-1]
    assert owner.cancelled()
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_transport_operation_repeated_cancellation_ignores_stale_explicit_cause():
    operation_started = asyncio.Event()
    first_cancellation_caught = asyncio.Event()
    captured_cancellations = []
    wrappers = []

    async def operation():
        operation_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as first_cancellation:
            captured_cancellations.append(first_cancellation)
            first_cancellation_caught.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as latest_cancellation:
            captured_cancellations.append(latest_cancellation)
            wrapper = OSError("transport selected stale cancellation")
            wrappers.append(wrapper)
            raise wrapper from captured_cancellations[0]

    owner = asyncio.create_task(
        session_module._run_transport_operation(operation())  # pylint: disable=protected-access
    )
    await asyncio.wait_for(operation_started.wait(), timeout=1)
    owner.cancel("first-cancel")
    await asyncio.wait_for(first_cancellation_caught.wait(), timeout=1)
    owner.cancel("latest-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(owner, timeout=1)

    assert [cancellation.args for cancellation in captured_cancellations] == [
        ("first-cancel",),
        ("latest-cancel",),
    ]
    assert wrappers[0].__cause__ is captured_cancellations[0]
    assert wrappers[0].__context__ is captured_cancellations[1]
    assert raised.value.args == (("latest-cancel",) if sys.version_info >= (3, 11) else ())
    assert owner.cancelled()
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_transport_operation_late_owner_cancellation_supersedes_completed_child_cancellation(monkeypatch):
    operation_started = asyncio.Event()
    transfer_ready = asyncio.Event()
    captured_cancellations = []
    wrappers = []
    pending_transfer = []
    transfer_result = session_module._transfer_transport_result  # pylint: disable=protected-access

    def hold_transfer(operation, waiter):
        pending_transfer.append((operation, waiter))
        transfer_ready.set()

    async def operation():
        operation_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            captured_cancellations.append(cancellation)
            wrapper = OSError("transport wrapped first cancellation")
            wrappers.append(wrapper)
            raise wrapper from cancellation

    monkeypatch.setattr(session_module, "_transfer_transport_result", hold_transfer)
    owner = asyncio.create_task(
        session_module._run_transport_operation(operation())  # pylint: disable=protected-access
    )
    await asyncio.wait_for(operation_started.wait(), timeout=1)
    owner.cancel("first-cancel")
    await asyncio.wait_for(transfer_ready.wait(), timeout=1)
    assert len(pending_transfer) == 1
    operation_task, waiter = pending_transfer[0]
    assert operation_task.done()
    assert not owner.done()

    owner.cancel("latest-cancel")
    transfer_result(operation_task, waiter)

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(owner, timeout=1)

    assert captured_cancellations[0].args == ("first-cancel",)
    assert raised.value.args == (("latest-cancel",) if sys.version_info >= (3, 11) else ())
    assert wrappers[0].__cause__ is captured_cancellations[0]
    assert owner.cancelled()
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_phase", ["before-transfer", "after-transfer"])
async def test_transport_operation_cancellation_at_result_transfer_boundary(monkeypatch, cancel_phase):
    transfer_ready = asyncio.Event()
    pending_transfer = []
    transfer_result = session_module._transfer_transport_result  # pylint: disable=protected-access

    def hold_transfer(operation, waiter):
        pending_transfer.append((operation, waiter))
        transfer_ready.set()

    async def operation():
        return "transport-result"

    monkeypatch.setattr(session_module, "_transfer_transport_result", hold_transfer)
    owner = asyncio.create_task(
        session_module._run_transport_operation(operation())  # pylint: disable=protected-access
    )
    await asyncio.wait_for(transfer_ready.wait(), timeout=1)
    assert len(pending_transfer) == 1
    operation_task, waiter = pending_transfer[0]
    assert operation_task.done()
    assert not owner.done()

    if cancel_phase == "before-transfer":
        owner.cancel("before-transfer-cancel")
        await asyncio.sleep(0)
        assert not owner.done()
        transfer_result(operation_task, waiter)
        expected_message = "before-transfer-cancel"
    else:
        transfer_result(operation_task, waiter)
        owner.cancel("after-transfer-cancel")
        expected_message = "after-transfer-cancel"

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(owner, timeout=1)

    assert raised.value.args == ((expected_message,) if sys.version_info >= (3, 11) else ())
    assert owner.cancelled()
    assert _live_voice_transport_tasks() == []


@pytest.mark.asyncio
async def test_voice_accept_cannot_consume_owner_cancellation():
    app = VoiceAgentServerHost(configure_observability=None)
    accept_started = asyncio.Event()
    consumed_cancellations = []
    terminating_sessions = []
    close_events = []
    sent_messages = []
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": "not-json"},
    ]

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.accept":
            accept_started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError as cancellation:
                consumed_cancellations.append(cancellation)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(accept_started.wait(), timeout=1)
    endpoint_task.cancel("accept-consumed-owner-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)
    assert raised.value.args == (("accept-consumed-owner-cancel",) if sys.version_info >= (3, 11) else ())
    assert endpoint_task.cancelled()
    assert terminating_sessions == []
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert len(consumed_cancellations) == 1
    assert consumed_cancellations[0].args == ("accept-consumed-owner-cancel",)
    assert Session._current(websocket) is None  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_voice_receive_cannot_consume_owner_cancellation():
    app = VoiceAgentServerHost(configure_observability=None)
    receive_started = asyncio.Event()
    consumed_cancellations = []
    terminating_sessions = []
    close_events = []
    sent_messages = []
    inbound_events = [{"type": "websocket.connect"}]

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    async def receive():
        if inbound_events:
            return inbound_events.pop(0)
        receive_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            consumed_cancellations.append(cancellation)
            return {"type": "websocket.receive", "text": "not-json"}

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(receive_started.wait(), timeout=1)
    endpoint_task.cancel("receive-consumed-owner-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)
    assert raised.value.args == (("receive-consumed-owner-cancel",) if sys.version_info >= (3, 11) else ())
    assert endpoint_task.cancelled()
    assert close_events == [(1011, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert len(consumed_cancellations) == 1
    assert consumed_cancellations[0].args == ("receive-consumed-owner-cancel",)
    assert len(terminating_sessions) == 1
    assert Session._current(websocket) is None  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_python310_application_callback_may_suppress_owner_cancellation(monkeypatch):
    monkeypatch.setattr(voice_host_module, "_task_cancellation_requests", lambda: None)
    app = VoiceAgentServerHost(configure_observability=None)
    callback_started = asyncio.Event()
    consumed_cancellations = []
    terminating_sessions = []
    close_events = []
    sent_messages = []
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]

    @app.on_session_start
    async def on_session_start(_session, _event):
        callback_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            consumed_cancellations.append(cancellation)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(callback_started.wait(), timeout=1)
    endpoint_task.cancel("event-consumed-owner-cancel")

    await asyncio.wait_for(endpoint_task, timeout=1)
    assert not endpoint_task.cancelled()
    assert close_events == [(1002, None)]
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert len(consumed_cancellations) == 1
    assert consumed_cancellations[0].args == ("event-consumed-owner-cancel",)
    assert len(terminating_sessions) == 1
    assert Session._current(websocket) is None  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_voice_send_recovers_caller_cancellation_before_disconnect_classification():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    send_started = asyncio.Event()
    captured_cancellations = []
    application_cancellations = []
    close_events = []
    disconnects = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(session, _event):
        try:
            await session.send(SessionReady())
        except asyncio.CancelledError as cancellation:
            application_cancellations.append(cancellation)
            raise

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            send_started.set()
            try:
                await asyncio.Future()
            except asyncio.CancelledError as cancellation:
                captured_cancellations.append(cancellation)
                raise OSError("send wrapped cancellation") from cancellation

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(send_started.wait(), timeout=1)
    endpoint_task.cancel("send-owner-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert len(captured_cancellations) == 1
    assert application_cancellations == captured_cancellations
    assert captured_cancellations[0].args == ("send-owner-cancel",)
    if _tracks_task_cancellation_requests():
        assert raised.value is captured_cancellations[0]
        assert raised.value.args == ("send-owner-cancel",)
    else:
        assert raised.value.args == ()
    assert endpoint_task.cancelled()
    assert disconnects == []
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.send"]
    assert close_events == [(1011, "cancelled")]
    assert _live_voice_send_tasks() == []


@pytest.mark.asyncio
async def test_voice_send_repeated_cancellation_drains_to_terminal_owner():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    send_started = asyncio.Event()
    first_cancellation_caught = asyncio.Event()
    captured_cancellations = []
    close_events = []
    disconnects = []

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        if message["type"] != "websocket.send":
            return
        send_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as first_cancellation:
            captured_cancellations.append(first_cancellation)
            first_cancellation_caught.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as second_cancellation:
            captured_cancellations.append(second_cancellation)
            raise OSError("send wrapped terminal cancellation") from second_cancellation

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(send_started.wait(), timeout=1)
    endpoint_task.cancel("first-cancel")
    await asyncio.wait_for(first_cancellation_caught.wait(), timeout=1)
    endpoint_task.cancel("terminal-cancel")

    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert [cancellation.args for cancellation in captured_cancellations] == [
        ("first-cancel",),
        ("terminal-cancel",),
    ]
    if _tracks_task_cancellation_requests():
        assert raised.value is captured_cancellations[-1]
    else:
        assert raised.value.args == ()
    assert disconnects == []
    assert close_events == [(1011, "cancelled")]
    assert _live_voice_send_tasks() == []


@pytest.mark.asyncio
async def test_voice_send_side_peer_loss_dispatches_disconnect_once():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]
    terminating_sessions = []
    disconnects = []
    close_events = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    @app.on_disconnect
    async def on_disconnect(session, event):
        disconnects.append((session, event.code, event.reason))

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            raise OSError("peer transport closed")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert len(terminating_sessions) == 1
    assert disconnects == [(terminating_sessions[0], 1006, None)]
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.send"]
    assert close_events == [(1006, None)]
    assert Session._current(websocket) is None  # pylint: disable=protected-access
    assert _live_voice_send_tasks() == []


@pytest.mark.asyncio
async def test_voice_send_side_peer_loss_wins_later_receive_disconnect():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.disconnect", "code": 1001, "reason": "later receive"},
    ]
    observed_send_errors = []
    disconnects = []
    close_events = []
    sent_messages = []

    @app.on_session_start
    async def on_session_start(session, _event):
        with pytest.raises(WebSocketDisconnect) as raised:
            await session.send(SessionReady())
        observed_send_errors.append(raised.value.code)

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append((event.code, event.reason))

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            raise OSError("peer transport closed")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert observed_send_errors == [1006]
    assert disconnects == [(1006, None)]
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.send"]
    assert close_events == [(1006, None)]
    assert _live_voice_send_tasks() == []


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
@pytest.mark.parametrize(
    ("peer_loss", "close_failure"),
    [(True, False), (False, False), (True, True)],
    ids=["peer-loss", "successful-send-negative-control", "peer-loss-close-failure"],
)
async def test_voice_teardown_observes_in_flight_send_outcome_before_disconnect_dispatch(peer_loss, close_failure):
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    send_started = asyncio.Event()
    release_send = asyncio.Event()
    retained_sessions = []
    send_tasks = []
    termination_calls = []
    disconnects = []
    close_events = []
    sent_messages = []
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    @app.on_session_start
    async def on_session_start(session, _event):
        retained_sessions.append(session)
        send_tasks.append(asyncio.create_task(session.send(SessionReady())))
        await asyncio.wait_for(send_started.wait(), timeout=1)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        termination_calls.append(session)
        release_send.set()

    @app.on_disconnect
    async def on_disconnect(session, event):
        disconnects.append((session, event.code, event.reason))

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if message["type"] == "websocket.send":
            send_started.set()
            await release_send.wait()
            if peer_loss:
                raise OSError("peer transport closed during teardown")
        elif message["type"] == "websocket.close" and close_failure:
            raise OSError("close transport failed after peer loss")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        await asyncio.wait_for(endpoint_task, timeout=1)
        send_results = await asyncio.wait_for(asyncio.gather(*send_tasks, return_exceptions=True), timeout=1)

        assert termination_calls == retained_sessions
        if peer_loss:
            assert len(send_results) == 1
            assert isinstance(send_results[0], WebSocketDisconnect)
            assert send_results[0].code == 1006
            assert disconnects == [(retained_sessions[0], 1006, None)]
        else:
            assert send_results == [None]
            assert disconnects == []

        disconnect_key = session_module._VOICE_DISCONNECT_EVENT_SCOPE_KEY  # pylint: disable=protected-access
        assert disconnect_key not in websocket.scope
        assert [message["type"] for message in sent_messages] == [
            "websocket.accept",
            "websocket.send",
            "websocket.close",
        ]
        assert sent_messages[-1]["code"] == 1002
        assert close_events == [(1002, None)]
        assert Session._current(websocket) is None  # pylint: disable=protected-access
        with pytest.raises(RuntimeError, match="terminating"):
            await retained_sessions[0].send(SessionReady())
        assert _live_voice_send_tasks() == []
    finally:
        release_send.set()
        if not endpoint_task.done():
            endpoint_task.cancel()
            await asyncio.gather(endpoint_task, return_exceptions=True)
        await asyncio.gather(*send_tasks, return_exceptions=True)
        await _finish_close_attempts(baseline_attempts)


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

        assert raised.value.args == (("shutdown",) if sys.version_info >= (3, 11) else ())
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


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal_source", ["peer", "protocol", "accept_failure"])
@pytest.mark.parametrize("termination_error_kind", ["exception", "cancellation"])
async def test_voice_termination_callback_failure_is_internal_error(
    terminal_source,
    termination_error_kind,
):
    app = VoiceAgentServerHost(configure_observability=None)
    if terminal_source == "peer":
        inbound_events = [
            {"type": "websocket.connect"},
            {"type": "websocket.disconnect", "code": 1001},
        ]
        expected_code = 1001
        expected_message_types = ["websocket.accept"]
    elif terminal_source == "protocol":
        inbound_events = [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": "not-json"},
        ]
        expected_code = 1002
        expected_message_types = ["websocket.accept", "websocket.close"]
    else:
        inbound_events = [{"type": "websocket.connect"}]
        expected_code = 1011
        expected_message_types = ["websocket.accept", "websocket.close"]

    terminating_sessions = []
    disconnects = []
    close_events = []
    sent_messages = []

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)
        if termination_error_kind == "cancellation":
            raise asyncio.CancelledError("termination hook cancellation")
        raise RuntimeError("termination hook failed")

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnects.append(event.code)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)
        if terminal_source == "accept_failure" and message["type"] == "websocket.accept":
            raise OSError("accept failed after commit")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append((code, error_code))
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert len(terminating_sessions) == 1
    assert disconnects == ([1001] if terminal_source == "peer" else [])
    assert [message["type"] for message in sent_messages] == expected_message_types
    assert close_events == [(expected_code, "internal_error")]


@pytest.mark.asyncio
async def test_voice_termination_failure_wins_classification_during_endpoint_cancellation():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": "not-json"},
    ]
    termination_contexts = []
    close_events = []
    sent_messages = []
    endpoint_task = None
    baseline_attempts = set(session_module._CLOSE_ATTEMPTS)  # pylint: disable=protected-access

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        termination_contexts.append(get_request_context().call_id)
        assert endpoint_task is asyncio.current_task()
        endpoint_task.cancel("cleanup-cancel")
        raise RuntimeError("termination hook failed")

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([(b"x-agent-foundry-call-id", b"cleanup-cancel-call")])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access
    app._emit_close_event = (  # type: ignore[method-assign]  # pylint: disable=protected-access
        lambda _session_id, code, _duration_ms, *, error_code=None: close_events.append(
            (code, error_code, get_request_context().call_id)
        )
    )

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    try:
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(endpoint_task, timeout=1)
    finally:
        await _finish_close_attempts(baseline_attempts)

    assert raised.value.args == (("cleanup-cancel",) if sys.version_info >= (3, 11) else ())
    assert termination_contexts == ["cleanup-cancel-call"]
    assert close_events == [(1002, "internal_error", "cleanup-cancel-call")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert get_request_context().call_id is None


@pytest.mark.asyncio
async def test_voice_both_cleanup_hook_failures_preserve_peer_code():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    close_events = []
    sent_messages = []

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        raise RuntimeError("termination hook failed")

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        raise RuntimeError("disconnect hook failed")

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
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_direct_disconnect_hook_cancellation_is_internal_error():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        raise asyncio.CancelledError("hook-local cancellation")

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(endpoint_task, timeout=1)

    assert not endpoint_task.cancelled()
    assert close_events == [(1001, "internal_error")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_disconnect_callback_self_cancellation_is_diagnosed():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        asyncio.current_task().cancel("disconnect-self-cancel")

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(endpoint_task, timeout=1)

    assert raised.value.args == (("disconnect-self-cancel",) if sys.version_info >= (3, 11) else ())
    assert endpoint_task.cancelled()
    assert close_events == [(1001, "cancelled")]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]


@pytest.mark.asyncio
async def test_voice_disconnect_callback_cannot_consume_owner_cancellation():
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1001},
    ]
    callback_started = asyncio.Event()
    consumed_cancellations = []
    close_events = []
    sent_messages = []

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        callback_started.set()
        try:
            await asyncio.Future()
        except asyncio.CancelledError as cancellation:
            consumed_cancellations.append(cancellation)

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

    endpoint_task = asyncio.create_task(app._ws_endpoint(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(callback_started.wait(), timeout=1)
    endpoint_task.cancel("consumed-owner-cancel")

    if _tracks_task_cancellation_requests():
        with pytest.raises(asyncio.CancelledError) as raised:
            await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(consumed_cancellations) == 1
        assert consumed_cancellations[0].args == ("consumed-owner-cancel",)
        assert raised.value.args == ()
        assert endpoint_task.cancelled()
        assert close_events == [(1001, "cancelled")]
    else:
        await asyncio.wait_for(endpoint_task, timeout=1)
        assert len(consumed_cancellations) == 1
        assert not endpoint_task.cancelled()
        assert close_events == [(1001, None)]
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
