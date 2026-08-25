# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tracing contract tests for the typed Voice relay."""

import ast
import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest
from opentelemetry import baggage, metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanContext, TraceFlags, TraceState
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations._constants import InvocationsWSConstants
from azure.ai.agentserver.invocations.voice import (
    Session,
    SessionDisconnected,
    SessionReady,
    SessionTermination,
    TargetTurnOrigin,
    TargetTurnOutcome,
    VoiceAgentServerHost,
    new_response_id,
)
from azure.ai.agentserver.invocations.voice import _voice_host as voice_host_module
from azure.ai.agentserver.invocations.voice import _tracing as tracing_module
from azure.ai.agentserver.invocations.voice import _turn as turn_module


_PROVIDER = None
_EXPORTER = None
_METER_PROVIDER = None
_METRIC_READER = None


def _readme_target_turn_error_outcome():
    readme = (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8")
    voice_section = readme.split("## Typed Voice Live Bridge submodule (preview)", 1)[1]
    example = voice_section.split("```python", 1)[1].split("```", 1)[0]
    module = ast.parse(example)
    functions = [
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "target_turn_error_outcome"
    ]
    assert len(functions) == 1, "README Voice example must define target_turn_error_outcome"
    namespace = {
        "SessionTermination": SessionTermination,
        "TargetTurnOutcome": TargetTurnOutcome,
    }
    exec(
        compile(ast.Module(body=functions, type_ignores=[]), "README.md", "exec"), namespace
    )  # pylint: disable=exec-used
    return namespace["target_turn_error_outcome"]


def _readme_on_user_message():
    readme = (Path(__file__).parents[2] / "README.md").read_text(encoding="utf-8")
    voice_section = readme.split("## Typed Voice Live Bridge submodule (preview)", 1)[1]
    example = voice_section.split("```python", 1)[1].split("```", 1)[0]
    module = ast.parse(example)
    functions = {node.name: node for node in module.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "target_turn_error_outcome" in functions
    assert "on_user_message" in functions
    functions["on_user_message"].decorator_list = []
    namespace = {
        "asyncio": asyncio,
        "Session": object,
        "SessionTermination": SessionTermination,
        "TargetTurnOrigin": TargetTurnOrigin,
        "TargetTurnOutcome": TargetTurnOutcome,
        "UserMessage": object,
        "ResponseCreated": lambda **_kwargs: object(),
        "ResponseOutputTextDone": lambda **_kwargs: object(),
        "ResponseDone": lambda **_kwargs: object(),
        "new_response_id": lambda: "r_readme",
        "new_item_id": lambda: "it_readme",
    }
    exec(  # pylint: disable=exec-used
        compile(
            ast.Module(
                body=[functions["target_turn_error_outcome"], functions["on_user_message"]],
                type_ignores=[],
            ),
            "README.md",
            "exec",
        ),
        namespace,
    )
    return namespace["on_user_message"]


@pytest.fixture
def spans():
    """Capture spans without replacing a provider another test installed."""
    global _PROVIDER, _EXPORTER
    if _PROVIDER is None:
        existing = trace.get_tracer_provider()
        if hasattr(existing, "add_span_processor"):
            _PROVIDER = existing
        else:
            _PROVIDER = TracerProvider()
            trace.set_tracer_provider(_PROVIDER)
        _EXPORTER = InMemorySpanExporter()
        _PROVIDER.add_span_processor(SimpleSpanProcessor(_EXPORTER))
    _EXPORTER.clear()
    return _PROVIDER, _EXPORTER


@pytest.fixture
def metric_reader():
    """Install one in-memory reader after module-level proxy instruments exist."""
    global _METER_PROVIDER, _METRIC_READER
    if _METER_PROVIDER is None:
        _METRIC_READER = InMemoryMetricReader()
        _METER_PROVIDER = MeterProvider(metric_readers=[_METRIC_READER])
        metrics.set_meter_provider(_METER_PROVIDER)
    return _METRIC_READER


def _session_start_frame() -> dict[str, object]:
    return {
        "type": "session.start",
        "id": "m_start",
        "ts": "2026-08-17T00:00:00Z",
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {
            "first_output_ms": 1,
            "idle_ms": 2,
            "max_duration_ms": 3,
        },
    }


def _span_by_name(exporter: InMemorySpanExporter, name: str):
    matches = [span for span in exporter.get_finished_spans() if span.name == name]
    assert len(matches) == 1, [span.name for span in exporter.get_finished_spans()]
    return matches[0]


def _metric_points(reader: InMemoryMetricReader, name: str):
    data = reader.get_metrics_data()
    if data is None:
        return []
    return [
        point
        for resource_metrics in data.resource_metrics
        for scope_metrics in resource_metrics.scope_metrics
        for metric in scope_metrics.metrics
        if metric.name == name
        for point in metric.data.data_points
    ]


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


@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(None, TargetTurnOutcome.ERROR, id="no-connection-fact"),
        pytest.param(SessionTermination.CALLBACK_ERROR, TargetTurnOutcome.ERROR, id="application-error"),
        pytest.param(
            SessionTermination.PROTOCOL_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="protocol-error",
        ),
        pytest.param(
            SessionTermination.TRANSPORT_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="transport-error",
        ),
    ],
)
def test_readme_target_turn_error_outcome_preserves_committed_connection_fact(termination, expected):
    assert _readme_target_turn_error_outcome()(termination) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(None, TargetTurnOutcome.ERROR, id="application-error"),
        pytest.param(
            SessionTermination.TRANSPORT_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="transport-error",
        ),
    ],
)
async def test_readme_user_message_commits_mapped_error_outcome_once(termination, expected):
    completions = []

    class Activation:
        def __enter__(self):
            return None

        def __exit__(self, *_args):
            return False

    class Turn:
        is_completed = False

        @staticmethod
        def activate():
            return Activation()

        def complete(self, **kwargs):
            self.is_completed = True
            completions.append(kwargs)

    class FailingSession:
        def __init__(self):
            self.termination = termination
            self.turn = Turn()

        def start_target_turn(self, **_kwargs):
            return self.turn

        @staticmethod
        async def send(_message):
            raise RuntimeError("send failed")

    event = type("Event", (), {"item_id": "in_readme"})()
    with pytest.raises(RuntimeError, match="send failed"):
        await _readme_on_user_message()(FailingSession(), event)

    assert completions == [
        {
            "outcome": expected,
            "response_id": None,
            "output_item_count": 0,
        }
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(None, TargetTurnOutcome.CANCELLED, id="local-cancellation"),
        pytest.param(SessionTermination.CANCELLED, TargetTurnOutcome.CANCELLED, id="connection-cancelled"),
        pytest.param(SessionTermination.COMPLETED, TargetTurnOutcome.ABANDONED, id="clean-peer-close"),
        pytest.param(SessionTermination.ACCEPT_ERROR, TargetTurnOutcome.ERROR, id="accept-error"),
        pytest.param(SessionTermination.CALLBACK_ERROR, TargetTurnOutcome.ERROR, id="callback-error"),
        pytest.param(SessionTermination.INTERNAL_ERROR, TargetTurnOutcome.ERROR, id="internal-error"),
        pytest.param(
            SessionTermination.PROTOCOL_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="protocol-error",
        ),
        pytest.param(
            SessionTermination.TRANSPORT_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="transport-error",
        ),
    ],
)
async def test_readme_user_message_cancellation_preserves_committed_connection_fact(termination, expected):
    completions = []

    class Activation:
        def __enter__(self):
            return None

        def __exit__(self, *_args):
            return False

    class Turn:
        is_completed = False

        @staticmethod
        def activate():
            return Activation()

        def complete(self, **kwargs):
            self.is_completed = True
            completions.append(kwargs)

    class CancelledSession:
        def __init__(self):
            self.termination = termination
            self.turn = Turn()

        def start_target_turn(self, **_kwargs):
            return self.turn

        @staticmethod
        async def send(_message):
            raise asyncio.CancelledError()

    event = type("Event", (), {"item_id": "in_readme"})()
    with pytest.raises(asyncio.CancelledError):
        await _readme_on_user_message()(CancelledSession(), event)

    assert completions == [
        {
            "outcome": expected,
            "response_id": None,
            "output_item_count": 0,
        }
    ]


@pytest.mark.parametrize(
    "factory_setup",
    [
        "trace.get_tracer = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError('tracer factory'))",
        "metrics.get_meter = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError('meter factory'))",
        """
class FailingMeter:
    def create_histogram(self, *_args, **_kwargs):
        raise RuntimeError("histogram factory")

    def create_counter(self, *_args, **_kwargs):
        raise RuntimeError("counter factory")

metrics.get_meter = lambda *_args, **_kwargs: FailingMeter()
""",
        """
import logging
real_get_logger = logging.getLogger

def fail_voice_logger(name=None):
    if name == "azure.ai.agentserver":
        raise RuntimeError("logger factory")
    return real_get_logger(name)

logging.getLogger = fail_voice_logger
""",
        """
import opentelemetry.trace.propagation.tracecontext as tracecontext
tracecontext.TraceContextTextMapPropagator = lambda: (_ for _ in ()).throw(RuntimeError("propagator factory"))
""",
    ],
)
def test_first_voice_import_survives_throwing_telemetry_factories(factory_setup):
    script = f"""
from opentelemetry import metrics, trace
import azure.ai.agentserver.invocations

{factory_setup}

from azure.ai.agentserver.invocations.voice import SessionTermination, TargetTurnOutcome

print(SessionTermination.CANCELLED.value, TargetTurnOutcome.ERROR.value)
"""
    completed = subprocess.run(  # nosec B603 - fixed interpreter and script
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "cancelled error"


def test_voice_connection_and_callback_have_explicit_semantic_parents(spans):
    provider, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    customer_tracer = provider.get_tracer("customer.agent")

    @app.on_session_start
    async def on_session_start(session, _event):
        with customer_tracer.start_as_current_span("customer.callback"):
            pass
        await session.send(SessionReady())

    remote_trace_id = "11111111111111111111111111111111"
    remote_span_id = "2222222222222222"
    headers = {"traceparent": f"00-{remote_trace_id}-{remote_span_id}-01"}
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_end",
                "ts": "2026-08-17T00:00:01Z",
                "reason": "completed",
            }
        )
        assert websocket.receive()["type"] == "websocket.close"

    connection = _span_by_name(exporter, "agentserver.connection")
    callback = _span_by_name(exporter, "voice.callback")
    customer = _span_by_name(exporter, "customer.callback")

    assert f"{connection.context.trace_id:032x}" == remote_trace_id
    assert connection.parent is not None
    assert f"{connection.parent.span_id:016x}" == remote_span_id
    assert callback.parent is not None and callback.parent.span_id == connection.context.span_id
    assert customer.parent is not None and customer.parent.span_id == callback.context.span_id
    assert callback.attributes == {"voice.event.type": "session.start"}
    assert connection.attributes["bridge.outcome"] == "completed"
    assert not [span for span in exporter.get_finished_spans() if span.name == "invoke_agent"]


@pytest.mark.asyncio
async def test_disconnect_callback_is_a_connection_sibling_and_parents_customer_work(spans):
    provider, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    customer_tracer = provider.get_tracer("customer.agent")

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        with customer_tracer.start_as_current_span("customer.disconnect"):
            pass

    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.disconnect", "code": 1000},
    ]
    websocket = _websocket_with_headers([(b"traceparent", b"00-11111111111111111111111111111111-2222222222222222-01")])
    websocket._receive = lambda: asyncio.sleep(0, result=inbound_events.pop(0))  # pylint: disable=protected-access
    websocket._send = lambda _message: asyncio.sleep(0)  # pylint: disable=protected-access

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    connection = _span_by_name(exporter, "agentserver.connection")
    callbacks = [span for span in exporter.get_finished_spans() if span.name == "voice.callback"]
    disconnects = [span for span in callbacks if span.attributes.get("voice.event.type") == "disconnect"]
    assert len(disconnects) == 1, [(span.name, dict(span.attributes)) for span in exporter.get_finished_spans()]
    disconnect = disconnects[0]
    customer = _span_by_name(exporter, "customer.disconnect")
    assert disconnect.parent is not None and disconnect.parent.span_id == connection.context.span_id
    assert customer.parent is not None and customer.parent.span_id == disconnect.context.span_id


@pytest.mark.asyncio
async def test_disconnect_callback_failure_marks_only_content_free_callback_error(spans):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    @app.on_disconnect
    async def on_disconnect(_session, _event):
        raise RuntimeError("private-disconnect-sentinel")

    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
        {"type": "websocket.disconnect", "code": 1000},
    ]
    websocket = _websocket_with_headers([])
    websocket._receive = lambda: asyncio.sleep(0, result=inbound_events.pop(0))  # pylint: disable=protected-access
    websocket._send = lambda _message: asyncio.sleep(0)  # pylint: disable=protected-access

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    callbacks = [span for span in exporter.get_finished_spans() if span.name == "voice.callback"]
    disconnects = [span for span in callbacks if span.attributes.get("voice.event.type") == "disconnect"]
    assert len(disconnects) == 1, [(span.name, dict(span.attributes)) for span in exporter.get_finished_spans()]
    disconnect = disconnects[0]
    assert disconnect.attributes["error.type"] == "callback_error"
    assert disconnect.status.status_code is trace.StatusCode.ERROR
    assert "private-disconnect-sentinel" not in repr(disconnect.attributes)


def test_voice_upgrade_rebuilds_only_hosted_agents_baggage():
    websocket = _websocket_with_headers(
        [
            (
                b"traceparent",
                b"00-11111111111111111111111111111111-2222222222222222-01",
            ),
            (
                b"baggage",
                b"azure.ai.agentserver.session_id=session-safe,"
                b"microsoft.a365.agent.blueprint.id=blueprint-safe,"
                b"user.id=user-safe,gen_ai.agent.id=agent-safe,"
                b"microsoft.tenant.id=tenant-safe,customer-secret=private-sentinel",
            ),
            (b"x-request-id", b"request-safe"),
        ]
    )

    extracted = voice_host_module._extract_voice_websocket_context(websocket)  # pylint: disable=protected-access

    assert baggage.get_baggage("azure.ai.agentserver.session_id", context=extracted) == "session-safe"
    assert baggage.get_baggage("microsoft.a365.agent.blueprint.id", context=extracted) == "blueprint-safe"
    assert baggage.get_baggage("user.id", context=extracted) == "user-safe"
    assert baggage.get_baggage("gen_ai.agent.id", context=extracted) == "agent-safe"
    assert baggage.get_baggage("microsoft.tenant.id", context=extracted) == "tenant-safe"
    assert baggage.get_baggage("x_request_id", context=extracted) == "request-safe"
    assert baggage.get_baggage("customer-secret", context=extracted) is None


def test_duplicate_approved_baggage_is_dropped_and_classified(metric_reader):
    websocket = _websocket_with_headers(
        [
            (
                b"traceparent",
                b"00-11111111111111111111111111111111-2222222222222222-01",
            ),
            (
                b"baggage",
                b"azure.ai.agentserver.session_id=session-first," b"azure.ai.agentserver.session_id=session-second",
            ),
        ]
    )

    extracted = voice_host_module._extract_voice_websocket_context(websocket)  # pylint: disable=protected-access

    assert baggage.get_baggage("azure.ai.agentserver.session_id", context=extracted) is None
    points = _metric_points(
        metric_reader,
        "azure.ai.agentserver.trace_context.propagation_failures",
    )
    assert any(point.attributes["error.type"] == "invalid" for point in points)


@pytest.mark.parametrize(
    ("header_name", "header_value"),
    [
        (b"baggage", b"customer-secret-private-sentinel"),
        (b"tracestate", b"Private-Sentinel=value"),
    ],
)
def test_invalid_propagation_never_logs_raw_member(caplog, header_name, header_value):
    websocket = _websocket_with_headers(
        [
            (
                b"traceparent",
                b"00-11111111111111111111111111111111-2222222222222222-01",
            ),
            (header_name, header_value),
        ]
    )

    with caplog.at_level(logging.WARNING):
        voice_host_module._extract_voice_websocket_context(websocket)  # pylint: disable=protected-access

    assert "private-sentinel" not in caplog.text.lower()


def test_unsampled_parent_propagates_without_exporting_semantic_spans(spans):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    observed_contexts = []

    @app.on_session_start
    async def on_session_start(session, _event):
        observed_contexts.append(trace.get_current_span().get_span_context())
        await session.send(SessionReady())

    remote_trace_id = "33333333333333333333333333333333"
    remote_span_id = "4444444444444444"
    headers = {
        "traceparent": f"00-{remote_trace_id}-{remote_span_id}-00",
        "tracestate": "vendor=value",
    }
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"

    assert len(observed_contexts) == 1
    observed = observed_contexts[0]
    assert f"{observed.trace_id:032x}" == remote_trace_id
    assert f"{observed.span_id:016x}" != remote_span_id
    assert not observed.trace_flags.sampled
    assert observed.trace_state.get("vendor") == "value"
    assert exporter.get_finished_spans() == ()


def test_declared_target_turn_uses_explicit_connection_parent(spans):
    provider, exporter = spans
    tracer = provider.get_tracer("azure.ai.agentserver.invocations.voice")
    customer_tracer = provider.get_tracer("customer.agent")
    connection = tracer.start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )

    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=2)
    with turn.activate():
        with customer_tracer.start_as_current_span("customer.model"):
            pass
    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    customer = _span_by_name(exporter, "customer.model")
    assert target.parent is not None and target.parent.span_id == connection.context.span_id
    assert customer.parent is not None and customer.parent.span_id == target.context.span_id
    assert target.attributes["gen_ai.operation.name"] == "invoke_agent"
    assert target.attributes["turn.origin"] == "user"
    assert target.attributes["bridge.input.count"] == 2
    assert target.attributes["bridge.output.item_count"] == 0
    assert target.attributes["bridge.outcome"] == "none"
    assert target.status.status_code is trace.StatusCode.UNSET


@pytest.mark.asyncio
async def test_target_turn_covers_application_owned_background_work(spans):
    provider, exporter = spans
    tracer = provider.get_tracer("azure.ai.agentserver.invocations.voice")
    customer_tracer = provider.get_tracer("customer.agent")
    connection = tracer.start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
    response_id = new_response_id()
    started = asyncio.Event()
    release = asyncio.Event()

    async def background_work():
        with turn.activate():
            with customer_tracer.start_as_current_span("customer.background"):
                started.set()
                await release.wait()
        turn.complete(
            outcome=TargetTurnOutcome.RESPONSE,
            response_id=response_id,
            output_item_count=1,
        )

    task = asyncio.create_task(background_work())
    await asyncio.wait_for(started.wait(), timeout=1)
    assert not [span for span in exporter.get_finished_spans() if span.name == "invoke_agent"]

    release.set()
    await asyncio.wait_for(task, timeout=1)
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    customer = _span_by_name(exporter, "customer.background")
    assert customer.parent is not None and customer.parent.span_id == target.context.span_id
    assert target.attributes["gen_ai.response.id"] == response_id
    assert target.attributes["bridge.output.item_count"] == 1
    assert target.attributes["bridge.outcome"] == "response"


def test_target_turn_rejects_completion_while_active_and_second_activation(spans):
    provider, _ = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.NO_INPUT, input_count=1)

    with turn.activate():
        with pytest.raises(RuntimeError, match="active"):
            turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)

    with pytest.raises(RuntimeError, match="activated"):
        with turn.activate():
            pass

    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    assert turn.is_completed
    connection.end()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"outcome": TargetTurnOutcome.RESPONSE, "output_item_count": 1},
        {
            "outcome": TargetTurnOutcome.RESPONSE,
            "response_id": "r_real",
            "output_item_count": 0,
        },
        {"outcome": TargetTurnOutcome.NONE},
        {
            "outcome": TargetTurnOutcome.NONE,
            "response_id": "r_real",
            "output_item_count": 0,
        },
        {"outcome": TargetTurnOutcome.ERROR, "output_item_count": 1},
    ],
)
def test_target_turn_rejects_contradictory_completion_facts(spans, kwargs):
    provider, _ = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)

    with pytest.raises((TypeError, ValueError)):
        turn.complete(**kwargs)

    assert not turn.is_completed
    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    connection.end()


@pytest.mark.parametrize(
    ("scenario", "expected"),
    [
        ("completed", SessionTermination.COMPLETED),
        ("protocol_error", SessionTermination.PROTOCOL_ERROR),
        ("callback_error", SessionTermination.CALLBACK_ERROR),
    ],
)
def test_connection_termination_fact_is_visible_before_cleanup(spans, scenario, expected):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    observed = []

    @app.on_session_start
    async def on_session_start(session, _event):
        if scenario == "callback_error":
            raise RuntimeError("private callback detail")
        await session.send(SessionReady())

    @app.on_connection_terminating
    def on_connection_terminating(session):
        observed.append(session.termination)

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        if scenario == "protocol_error":
            websocket.send_text("not-json")
            assert websocket.receive()["code"] == 1002
        else:
            websocket.send_json(_session_start_frame())
            if scenario == "completed":
                assert websocket.receive_json()["type"] == "session.ready"
                websocket.send_json(
                    {
                        "type": "session.end",
                        "id": "m_end",
                        "ts": "2026-08-17T00:00:01Z",
                        "reason": "completed",
                    }
                )
            assert websocket.receive()["type"] == "websocket.close"

    assert observed == [expected]
    connection = _span_by_name(exporter, "agentserver.connection")
    assert connection.attributes["bridge.outcome"] == expected.value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("close_code", "expected_termination"),
    [
        pytest.param(1000, SessionTermination.COMPLETED, id="normal-baseline"),
        pytest.param(1001, SessionTermination.COMPLETED, id="going-away"),
        pytest.param(1002, SessionTermination.PROTOCOL_ERROR, id="protocol-error"),
        pytest.param(1003, SessionTermination.PROTOCOL_ERROR, id="unsupported-data"),
        pytest.param(1007, SessionTermination.PROTOCOL_ERROR, id="invalid-payload"),
        pytest.param(1008, SessionTermination.PROTOCOL_ERROR, id="policy-violation"),
        pytest.param(1009, SessionTermination.PROTOCOL_ERROR, id="message-too-big"),
        pytest.param(1010, SessionTermination.PROTOCOL_ERROR, id="mandatory-extension"),
        pytest.param(1011, SessionTermination.TRANSPORT_ERROR, id="internal-error-negative-control"),
        pytest.param(1006, SessionTermination.TRANSPORT_ERROR, id="abnormal-negative-control"),
    ],
)
async def test_peer_disconnect_classification_matches_cleanup_and_telemetry(
    spans,
    metric_reader,
    caplog,
    close_code,
    expected_termination,
):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    callback_order = []
    terminations = []
    disconnects = []
    rejected_writes = []
    later_callbacks = []
    sent_messages = []
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": close_code, "reason": "peer close"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]

    @app.on_session_start
    async def on_session_start(_session, _event):
        later_callbacks.append("session.start")

    @app.on_connection_terminating
    def on_connection_terminating(session):
        callback_order.append("terminating")
        terminations.append(session.termination)

    @app.on_disconnect
    async def on_disconnect(session, event):
        callback_order.append("disconnect")
        disconnects.append((session.termination, event.code, event.reason))
        with pytest.raises(RuntimeError, match="terminating"):
            await session.send(SessionReady())
        rejected_writes.append(True)

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        sent_messages.append(message)

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    expected_outcome = expected_termination.value
    expected_metric_attributes = {"bridge.outcome": expected_outcome}
    if expected_termination is not SessionTermination.COMPLETED:
        expected_metric_attributes["error.type"] = expected_outcome
    metric_name = "azure.ai.agentserver.voice.connection.duration"
    before_metric_count = sum(
        point.count
        for point in _metric_points(metric_reader, metric_name)
        if point.attributes == expected_metric_attributes
    )

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    assert callback_order == ["terminating", "disconnect"]
    assert terminations == [expected_termination]
    assert disconnects == [(expected_termination, close_code, "peer close")]
    assert rejected_writes == [True]
    assert later_callbacks == []
    assert len(inbound_events) == 1
    assert [message["type"] for message in sent_messages] == ["websocket.accept"]
    assert Session._current(websocket) is None  # pylint: disable=protected-access
    close_records = [record for record in caplog.records if record.getMessage() == "Voice connection closed"]
    assert len(close_records) == 1
    assert getattr(close_records[0], InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE) == close_code

    connection = _span_by_name(exporter, "agentserver.connection")
    assert connection.attributes["bridge.outcome"] == expected_outcome
    fallback_websocket = _websocket_with_headers([])
    fallback_session = Session._create(fallback_websocket)  # pylint: disable=protected-access
    try:
        voice_host_module._commit_voice_session_termination(  # pylint: disable=protected-access
            fallback_session,
            handler_error=None,
            disconnect_event=SessionDisconnected(code=close_code, reason="peer close"),
            close_code=close_code,
            accept_failed=False,
        )
        assert fallback_session.termination is expected_termination
    finally:
        Session._release(fallback_websocket, fallback_session)  # pylint: disable=protected-access
    assert tracing_module._connection_outcome(close_code, None) == expected_outcome  # pylint: disable=protected-access
    points = _metric_points(metric_reader, metric_name)
    after_metric_count = sum(point.count for point in points if point.attributes == expected_metric_attributes)
    assert after_metric_count - before_metric_count == 1
    if expected_termination is SessionTermination.COMPLETED:
        assert "error.type" not in connection.attributes
        assert connection.status.status_code is trace.StatusCode.UNSET
    else:
        assert connection.attributes["error.type"] == expected_outcome
        assert connection.status.status_code is trace.StatusCode.ERROR


def test_missing_and_invalid_context_record_sanitized_failure_metrics(metric_reader):
    metric_name = "azure.ai.agentserver.trace_context.propagation_failures"
    before = {point.attributes["error.type"]: point.value for point in _metric_points(metric_reader, metric_name)}
    voice_host_module._extract_voice_websocket_context(_websocket_with_headers([]))  # pylint: disable=protected-access
    voice_host_module._extract_voice_websocket_context(  # pylint: disable=protected-access
        _websocket_with_headers([(b"traceparent", b"private-invalid-traceparent")])
    )

    points = _metric_points(
        metric_reader,
        metric_name,
    )
    dimensions = {tuple(sorted(point.attributes.items())) for point in points}
    assert dimensions == {
        (
            (
                "azure.ai.agentserver.trace_context.propagation.hop",
                "hosted_agents_to_agentserver",
            ),
            ("error.type", "invalid"),
        ),
        (
            (
                "azure.ai.agentserver.trace_context.propagation.hop",
                "hosted_agents_to_agentserver",
            ),
            ("error.type", "missing"),
        ),
    }
    after = {point.attributes["error.type"]: point.value for point in points}
    assert after["missing"] - before.get("missing", 0) == 1
    assert after["invalid"] - before.get("invalid", 0) == 1


def test_unsampled_operations_still_record_duration_metrics(spans, metric_reader):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
        with turn.activate():
            pass
        turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
        await session.send(SessionReady())

    headers = {
        "traceparent": "00-55555555555555555555555555555555-6666666666666666-00",
    }
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_end",
                "ts": "2026-08-17T00:00:01Z",
                "reason": "completed",
            }
        )
        assert websocket.receive()["type"] == "websocket.close"

    assert exporter.get_finished_spans() == ()
    connection_points = _metric_points(
        metric_reader,
        "azure.ai.agentserver.voice.connection.duration",
    )
    target_points = _metric_points(metric_reader, "gen_ai.invoke_agent.duration")
    assert any(point.attributes == {"bridge.outcome": "completed"} for point in connection_points)
    assert any(point.attributes == {"bridge.outcome": "none", "turn.origin": "user"} for point in target_points)


def test_target_turn_projects_one_content_free_trigger_link(spans):
    provider, exporter = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    trigger = SpanContext(
        trace_id=0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
        span_id=0xBBBBBBBBBBBBBBBB,
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=TraceState.from_header(["private=value"]),
    )

    turn = session.start_target_turn(
        origin=TargetTurnOrigin.PROACTIVE,
        input_count=0,
        trigger_context=trigger,
    )
    with turn.activate():
        pass
    turn.complete(
        outcome=TargetTurnOutcome.RESPONSE,
        response_id="r_proactive",
        output_item_count=1,
    )
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    assert len(target.links) == 1
    link = target.links[0]
    assert link.context.trace_id == trigger.trace_id
    assert link.context.span_id == trigger.span_id
    assert link.context.trace_flags == trigger.trace_flags
    assert link.context.is_remote == trigger.is_remote
    assert len(link.context.trace_state) == 0
    assert not link.attributes


@pytest.mark.parametrize("constructor_name", ["SpanContext", "TraceState", "Link"])
def test_trigger_link_factory_failure_does_not_change_target_turn(monkeypatch, spans, constructor_name):
    provider, exporter = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    trigger = SpanContext(
        trace_id=0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA,
        span_id=0xBBBBBBBBBBBBBBBB,
        is_remote=True,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
        trace_state=TraceState(),
    )

    def fail_constructor(*_args, **_kwargs):
        raise RuntimeError("private link factory failure")

    monkeypatch.setattr(turn_module, constructor_name, fail_constructor)
    turn = session.start_target_turn(
        origin=TargetTurnOrigin.PROACTIVE,
        input_count=0,
        trigger_context=trigger,
    )
    with turn.activate():
        pass
    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    assert target.links == ()
    assert target.attributes["bridge.outcome"] == "none"


def test_unsafe_response_id_is_not_projected_into_target_span(spans):
    provider, exporter = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
    with turn.activate():
        pass

    turn.complete(
        outcome=TargetTurnOutcome.RESPONSE,
        response_id="r_private-secret-token",
        output_item_count=1,
    )
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    assert target.attributes["bridge.outcome"] == "response"
    assert target.attributes["bridge.output.item_count"] == 1
    assert "gen_ai.response.id" not in target.attributes
    assert "private-secret-token" not in repr(target.attributes)


def test_terminal_session_rejects_new_target_turn(spans):
    provider, _ = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    session._begin_termination(SessionTermination.TRANSPORT_ERROR)  # pylint: disable=protected-access

    with pytest.raises(RuntimeError, match="terminating"):
        session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)

    assert session._connection_context is None  # pylint: disable=protected-access
    connection.end()


def test_error_target_metric_matches_span_outcome(spans, metric_reader):
    provider, exporter = spans
    connection = provider.get_tracer("test.connection").start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
    with turn.activate():
        pass
    turn.complete(outcome=TargetTurnOutcome.TIMEOUT, output_item_count=0)
    connection.end()

    target = _span_by_name(exporter, "invoke_agent")
    assert target.attributes["bridge.outcome"] == "timeout"
    assert target.attributes["error.type"] == "timeout"
    points = _metric_points(metric_reader, "gen_ai.invoke_agent.duration")
    assert any(
        point.attributes == {"bridge.outcome": "timeout", "error.type": "timeout", "turn.origin": "user"}
        for point in points
    )


@pytest.mark.parametrize(("environment_value", "expected"), [(None, False), ("true", True)])
def test_voice_default_observability_requires_explicit_sensitive_opt_in(
    monkeypatch,
    environment_value,
    expected,
):
    calls = []
    if environment_value is None:
        monkeypatch.delenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", raising=False)
    else:
        monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", environment_value)
    monkeypatch.setattr(
        voice_host_module,
        "_CORE_CONFIGURE_OBSERVABILITY",
        lambda **kwargs: calls.append(kwargs),
        raising=False,
    )

    VoiceAgentServerHost()

    assert len(calls) == 1
    assert calls[0]["enable_sensitive_data"] is expected


def test_voice_default_observability_rejects_invalid_log_level():
    with pytest.raises(ValueError, match="Invalid log level"):
        VoiceAgentServerHost(log_level="TRACE")


def test_voice_disabled_observability_skips_log_level_validation():
    app = VoiceAgentServerHost(log_level="TRACE", configure_observability=None)
    assert isinstance(app, VoiceAgentServerHost)


def test_voice_default_observability_configuration_failure_allows_retry(monkeypatch):
    failure = ValueError("invalid observability configuration")
    observed_log_levels = []

    def configure_observability(**kwargs):
        observed_log_levels.append(kwargs["log_level"])
        if kwargs["log_level"] == "TRACE":
            raise failure

    monkeypatch.setattr(voice_host_module, "_CORE_CONFIGURE_OBSERVABILITY", configure_observability)

    with pytest.raises(ValueError) as raised:
        VoiceAgentServerHost(log_level="TRACE")

    assert raised.value is failure
    app = VoiceAgentServerHost(log_level="INFO")
    assert isinstance(app, VoiceAgentServerHost)
    assert observed_log_levels == ["TRACE", "INFO"]


@pytest.mark.parametrize(
    "failure",
    [RuntimeError("private-observability-sentinel"), asyncio.CancelledError("private-observability-sentinel")],
)
def test_voice_default_observability_failure_is_content_free_and_fail_open(monkeypatch, caplog, failure):
    def fail_observability(**_kwargs):
        raise failure

    monkeypatch.setattr(voice_host_module, "_CORE_CONFIGURE_OBSERVABILITY", fail_observability)

    with caplog.at_level(logging.WARNING):
        app = VoiceAgentServerHost()

    assert isinstance(app, VoiceAgentServerHost)
    assert "private-observability-sentinel" not in caplog.text


def test_voice_diagnostics_are_content_free(monkeypatch, caplog, spans):
    _, exporter = spans
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "private session sentinel")
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(_session, _event):
        raise RuntimeError("private-exception-sentinel")

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_session_start_frame())
            assert websocket.receive()["type"] == "websocket.close"

    assert "private session sentinel" not in caplog.text
    assert "private-exception-sentinel" not in caplog.text
    voice_records = [record for record in caplog.records if str(record.msg).startswith("Voice ")]
    assert voice_records
    for record in voice_records:
        assert record.args == ()
        assert record.exc_info is None
    connection = _span_by_name(exporter, "agentserver.connection")
    assert "private session sentinel" not in repr(connection.attributes)


def test_connection_span_carries_safe_session_and_protocol_attributes(monkeypatch, spans):
    _, exporter = spans
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "session_safe_123")
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_end",
                "ts": "2026-08-17T00:00:01Z",
                "reason": "completed",
            }
        )
        assert websocket.receive()["type"] == "websocket.close"

    connection = _span_by_name(exporter, "agentserver.connection")
    assert connection.attributes["azure.ai.agentserver.invocations_ws.session_id"] == "session_safe_123"
    assert connection.attributes["azure.ai.agentserver.invocations_ws.protocol_version"] == "1.0"
    assert connection.attributes["azure.ai.agentserver.invocations_ws.reconnect"] is False


def test_connection_span_omits_unsafe_protocol_content_without_changing_dispatch(spans):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    observed_protocols = []

    @app.on_session_start
    async def on_session_start(session, event):
        observed_protocols.append(event.protocol_version)
        await session.send(SessionReady())

    private_protocol = "private-protocol-sentinel"
    frame = _session_start_frame()
    frame["protocol_version"] = private_protocol
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(frame)
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_end",
                "ts": "2026-08-17T00:00:01Z",
                "reason": "completed",
            }
        )
        assert websocket.receive()["type"] == "websocket.close"

    assert observed_protocols == [private_protocol]
    connection = _span_by_name(exporter, "agentserver.connection")
    assert "azure.ai.agentserver.invocations_ws.protocol_version" not in connection.attributes
    assert private_protocol not in repr(connection.attributes)


@pytest.mark.parametrize("failure_stage", ["parent_attach", "connection_attach"])
def test_connection_setup_failure_disables_semantic_descendants(
    monkeypatch,
    spans,
    failure_stage,
):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    callback_count = 0

    if failure_stage == "parent_attach":
        monkeypatch.setattr(voice_host_module, "_attach_context", lambda _context: None)
    else:
        monkeypatch.setattr(tracing_module, "_attach_context", lambda _context: None)

    @app.on_session_start
    async def on_session_start(session, _event):
        nonlocal callback_count
        callback_count += 1
        turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
        with turn.activate():
            pass
        turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
        await session.send(SessionReady())

    headers = {"traceparent": "00-77777777777777777777777777777777-8888888888888888-01"}
    with TestClient(app).websocket_connect("/invocations_ws", headers=headers) as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_end",
                "ts": "2026-08-17T00:00:01Z",
                "reason": "completed",
            }
        )
        assert websocket.receive()["type"] == "websocket.close"

    assert callback_count == 1
    semantic = [
        span
        for span in exporter.get_finished_spans()
        if span.name in {"agentserver.connection", "voice.callback", "invoke_agent"}
    ]
    expected_names = [] if failure_stage == "parent_attach" else ["agentserver.connection"]
    assert [span.name for span in semantic] == expected_names


def test_context_factory_failure_disables_telemetry_without_changing_wire(monkeypatch, spans):
    _, exporter = spans

    def fail_context():
        raise RuntimeError("private context factory failure")

    monkeypatch.setattr(voice_host_module._otel_context, "Context", fail_context)
    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        websocket.send_json(_session_start_frame())
        assert websocket.receive_json()["type"] == "session.ready"

    assert not [
        span
        for span in exporter.get_finished_spans()
        if span.name in {"agentserver.connection", "voice.callback", "invoke_agent"}
    ]


@pytest.mark.asyncio
async def test_send_side_peer_loss_marks_callback_and_connection_transport_error(spans):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]

    @app.on_session_start
    async def on_session_start(session, _event):
        await session.send(SessionReady())

    async def receive():
        return inbound_events.pop(0)

    async def send(message):
        if message["type"] == "websocket.send":
            raise OSError("private peer loss detail")

    websocket = _websocket_with_headers([])
    websocket._receive = receive  # pylint: disable=protected-access
    websocket._send = send  # pylint: disable=protected-access

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    connection = _span_by_name(exporter, "agentserver.connection")
    callbacks = [span for span in exporter.get_finished_spans() if span.name == "voice.callback"]
    callback = next(span for span in callbacks if span.attributes.get("voice.event.type") == "session.start")
    assert callback.attributes["error.type"] == "transport_error"
    assert callback.status.status_code is trace.StatusCode.ERROR
    assert connection.attributes["bridge.outcome"] == "transport_error"
    assert "private peer loss detail" not in repr(callback.attributes)


@pytest.mark.asyncio
async def test_application_websocket_disconnect_is_callback_error(spans):
    _, exporter = spans
    app = VoiceAgentServerHost(configure_observability=None)
    observed_terminations = []
    disconnects = []
    sent_messages = []
    inbound_events = [
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(_session_start_frame())},
    ]

    @app.on_session_start
    async def on_session_start(_session, _event):
        raise WebSocketDisconnect(code=1000, reason="private callback detail")

    @app.on_connection_terminating
    def on_connection_terminating(session):
        observed_terminations.append(session.termination)

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

    await asyncio.wait_for(app._ws_endpoint(websocket), timeout=1)  # pylint: disable=protected-access

    connection = _span_by_name(exporter, "agentserver.connection")
    callback = next(
        span
        for span in exporter.get_finished_spans()
        if span.name == "voice.callback" and span.attributes.get("voice.event.type") == "session.start"
    )
    assert observed_terminations == [SessionTermination.CALLBACK_ERROR]
    assert disconnects == []
    assert [message["type"] for message in sent_messages] == ["websocket.accept", "websocket.close"]
    assert sent_messages[-1]["code"] == 1011
    assert callback.attributes["error.type"] == "callback_error"
    assert connection.attributes["bridge.outcome"] == "callback_error"
    assert "private callback detail" not in repr(callback.attributes)


@pytest.mark.parametrize("failure_stage", ["span_start", "span_lifecycle", "meter", "logger"])
def test_telemetry_failure_does_not_change_wire_or_next_connection(monkeypatch, failure_stage):
    class FailingTracer:
        @staticmethod
        def start_span(*_args, **_kwargs):
            raise RuntimeError("private tracer failure")

    class FailingSpan:
        def __init__(self):
            self._context = SpanContext(
                trace_id=0x99999999999999999999999999999999,
                span_id=0xAAAAAAAAAAAAAAAA,
                is_remote=False,
                trace_flags=TraceFlags(TraceFlags.SAMPLED),
                trace_state=TraceState(),
            )

        def get_span_context(self):
            return self._context

        @staticmethod
        def set_attribute(*_args, **_kwargs):
            raise RuntimeError("private attribute failure")

        @staticmethod
        def set_status(*_args, **_kwargs):
            raise RuntimeError("private status failure")

        @staticmethod
        def end(*_args, **_kwargs):
            raise RuntimeError("private end failure")

    class LifecycleTracer:
        @staticmethod
        def start_span(*_args, **_kwargs):
            return FailingSpan()

    class FailingInstrument:
        @staticmethod
        def add(*_args, **_kwargs):
            raise RuntimeError("private counter failure")

        @staticmethod
        def record(*_args, **_kwargs):
            raise RuntimeError("private histogram failure")

    class FailingHandler(logging.Handler):
        def emit(self, _record):
            raise RuntimeError("private logger failure")

    if failure_stage == "span_start":
        monkeypatch.setattr(tracing_module, "_TRACER", FailingTracer())
    elif failure_stage == "span_lifecycle":
        monkeypatch.setattr(tracing_module, "_TRACER", LifecycleTracer())
    elif failure_stage == "meter":
        monkeypatch.setattr(tracing_module, "_CONNECTION_DURATION", FailingInstrument())
        monkeypatch.setattr(tracing_module, "_TARGET_DURATION", FailingInstrument())
        monkeypatch.setattr(tracing_module, "_PROPAGATION_FAILURES", FailingInstrument())

    app = VoiceAgentServerHost(configure_observability=None)

    @app.on_session_start
    async def on_session_start(session, _event):
        turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
        with turn.activate():
            pass
        turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
        await session.send(SessionReady())

    handler = FailingHandler()
    if failure_stage == "logger":
        logging.getLogger("azure.ai.agentserver").addHandler(handler)
    try:
        for _ in range(2):
            with TestClient(app).websocket_connect("/invocations_ws") as websocket:
                websocket.send_json(_session_start_frame())
                assert websocket.receive_json()["type"] == "session.ready"
                websocket.send_json(
                    {
                        "type": "session.end",
                        "id": "m_end",
                        "ts": "2026-08-17T00:00:01Z",
                        "reason": "completed",
                    }
                )
                assert websocket.receive()["type"] == "websocket.close"
    finally:
        if failure_stage == "logger":
            logging.getLogger("azure.ai.agentserver").removeHandler(handler)


def test_target_span_end_is_attempted_after_attribute_failure(monkeypatch, metric_reader):
    class FailingSpan:
        def __init__(self):
            self.end_calls = 0
            self.status_calls = 0

        @staticmethod
        def set_attribute(*_args, **_kwargs):
            raise RuntimeError("private attribute failure")

        def set_status(self, *_args, **_kwargs):
            self.status_calls += 1
            raise RuntimeError("private status failure")

        def end(self, *_args, **_kwargs):
            self.end_calls += 1

    span = FailingSpan()

    class FailingTracer:
        @staticmethod
        def start_span(*_args, **_kwargs):
            return span

    monkeypatch.setattr(turn_module, "_TRACER", FailingTracer())
    before = sum(point.count for point in _metric_points(metric_reader, "gen_ai.invoke_agent.duration"))
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(
            trace.get_tracer("test.connection").start_span("agentserver.connection")
        ),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
    with turn.activate():
        pass

    turn.complete(outcome=TargetTurnOutcome.ERROR, output_item_count=0)
    turn.complete(outcome=TargetTurnOutcome.ERROR, output_item_count=0)

    after = sum(point.count for point in _metric_points(metric_reader, "gen_ai.invoke_agent.duration"))
    assert span.end_calls == 1
    assert span.status_calls == 1
    assert after - before == 1
    assert turn.is_completed


def test_connection_finalizer_attempts_status_and_end_after_attribute_failure(
    metric_reader,
):
    class FailingSpan:
        def __init__(self):
            self.end_calls = 0
            self.status_calls = 0

        @staticmethod
        def set_attribute(*_args, **_kwargs):
            raise RuntimeError("private attribute failure")

        def set_status(self, *_args, **_kwargs):
            self.status_calls += 1

        def end(self, *_args, **_kwargs):
            self.end_calls += 1

    span = FailingSpan()
    scope = tracing_module._SpanScope(span=span)  # pylint: disable=protected-access
    before = sum(
        point.count for point in _metric_points(metric_reader, "azure.ai.agentserver.voice.connection.duration")
    )

    scope.complete_connection("transport_error", 1006)
    scope.complete_connection("transport_error", 1006)
    scope.close()

    after = sum(
        point.count for point in _metric_points(metric_reader, "azure.ai.agentserver.voice.connection.duration")
    )
    assert span.status_calls == 1
    assert span.end_calls == 1
    assert after - before == 1


def test_target_attach_failure_falls_back_to_connection_parent(monkeypatch, spans):
    provider, exporter = spans
    tracer = provider.get_tracer("test.connection")
    customer_tracer = provider.get_tracer("customer.agent")
    connection = tracer.start_span("agentserver.connection")
    session = Session._create(  # pylint: disable=protected-access
        _websocket_with_headers([]),
        connection_context=trace.set_span_in_context(connection),
    )
    turn = session.start_target_turn(origin=TargetTurnOrigin.USER, input_count=1)
    original_attach = turn_module._attach_context  # pylint: disable=protected-access

    def fail_target_attach(candidate):
        candidate_span = trace.get_current_span(candidate)
        if candidate_span is turn._span:  # pylint: disable=protected-access
            return None
        return original_attach(candidate)

    monkeypatch.setattr(turn_module, "_attach_context", fail_target_attach)
    with turn.activate():
        with customer_tracer.start_as_current_span("customer.fallback"):
            pass
    turn.complete(outcome=TargetTurnOutcome.NONE, output_item_count=0)
    connection.end()

    customer = _span_by_name(exporter, "customer.fallback")
    assert customer.parent is not None
    assert customer.parent.span_id == connection.context.span_id
