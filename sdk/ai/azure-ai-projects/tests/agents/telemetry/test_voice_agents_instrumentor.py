# pylint: disable=too-many-lines
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Deterministic sync/async lifecycle and privacy tests for Voice Agents tracing."""

import asyncio
import base64
import io
import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import requests
from urllib3.response import HTTPResponse
from opentelemetry import trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from opentelemetry.trace import StatusCode

from azure.core import MatchConditions
from azure.core.credentials import AccessToken
from azure.core.exceptions import ResourceNotFoundError

# Core conditionally re-exports this optional transport; runtime imports are covered below.
from azure.core.pipeline.transport import RequestsTransport  # pylint: disable=no-name-in-module
from azure.core.settings import settings
from azure.ai.projects import AIProjectClient, models
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.telemetry import AIProjectInstrumentor, _utils
from azure.ai.projects.telemetry import _voice_agents_instrumentor as voice
from azure.ai.projects.telemetry import _responses_instrumentor as responses
from azure.ai.projects._realtime import BetaRealtimeConnectionManager
from azure.ai.projects.aio._realtime import AsyncBetaRealtimeConnectionManager

_ENDPOINT = "https://example.test/api/projects/project-test"
_PREFIX = "az.ai.voice_agents."
_SECRET = "PRIVATE-CONTENT-DO-NOT-EXPORT"


@pytest.fixture(name="telemetry")
def _telemetry(monkeypatch):
    original_impl = settings.tracing_implementation()
    original_enabled = settings.tracing_enabled()
    provider = TracerProvider()
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(trace, "_TRACER_PROVIDER", provider)
    monkeypatch.setenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    settings.tracing_implementation = "opentelemetry"
    settings.tracing_enabled = True
    monkeypatch.setattr(_utils, "_span_impl_type", settings.tracing_implementation())
    instrumentor = AIProjectInstrumentor()
    instrumentor.uninstrument()
    instrumentor.instrument(enable_content_recording=False)
    reader = InMemoryMetricReader()
    meter_provider = MeterProvider(metric_readers=[reader])
    meter = meter_provider.get_meter(__name__)
    monkeypatch.setattr(
        responses, "_operation_duration_histogram", meter.create_histogram("gen_ai.client.operation.duration", unit="s")
    )
    monkeypatch.setattr(
        responses, "_token_usage_histogram", meter.create_histogram("gen_ai.client.token.usage", unit="token")
    )
    yield SimpleNamespace(
        instrumentor=instrumentor, exporter=exporter, provider=provider, monkeypatch=monkeypatch, metric_reader=reader
    )
    instrumentor.uninstrument()
    provider.shutdown()
    meter_provider.shutdown()
    settings.tracing_implementation = original_impl
    settings.tracing_enabled = original_enabled


def _events():
    return [
        {
            "type": "session.created",
            "session": {"id": "session-test", "model": "test-model"},
            "conversation_id": "conversation-test",
        },
        {"type": "session.updated", "session": {"id": "session-test", "model": "test-model"}},
        {"type": "response.created", "response": {"id": "response-test", "conversation_id": "conversation-test"}},
        {"type": "response.output_text.delta", "response_id": "response-test", "delta": _SECRET},
        {
            "type": "response.output_audio.delta",
            "response_id": "response-test",
            "delta": base64.b64encode(b"\x01\x00" * 12).decode(),
        },
        {
            "type": "response.function_call_arguments.done",
            "response_id": "response-test",
            "call_id": "call-test",
            "name": _SECRET,
            "arguments": _SECRET,
        },
        {
            "type": "response.output_text.done",
            "response_id": "response-test",
            "item_id": "item-test",
            "content_index": 0,
            "text": _SECRET,
        },
        {
            "type": "response.done",
            "response": {
                "id": "response-test",
                "status": "completed",
                "output_modalities": ["text"],
                "output": [
                    {
                        "id": "item-test",
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": _SECRET}],
                    }
                ],
                "usage": {"input_tokens": 3, "output_tokens": 7},
            },
        },
    ]


def _manager(monkeypatch, is_async, events=None, failure=None, headers=None):
    credential = MagicMock()
    token = AccessToken(_SECRET, 4_102_444_800)
    ws = MagicMock()
    ws.close_code = 1000
    ws.closed = False
    manager: BetaRealtimeConnectionManager | AsyncBetaRealtimeConnectionManager
    if is_async:
        import aiohttp

        messages = [
            SimpleNamespace(type=aiohttp.WSMsgType.TEXT, data=json.dumps(event)) for event in (events or _events())
        ]
        ws.receive = AsyncMock(side_effect=messages)
        ws.send_str = AsyncMock()
        ws.close = AsyncMock()
        session = MagicMock()
        session.close = AsyncMock()
        session.ws_connect = AsyncMock(side_effect=failure, return_value=ws)
        credential.get_token = AsyncMock(return_value=token)
        monkeypatch.setattr(aiohttp, "ClientSession", MagicMock(return_value=session))
        manager = AsyncBetaRealtimeConnectionManager(
            endpoint=_ENDPOINT,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
            api_version="v1",
            agent_name="agent-test",
            extra_headers=headers,
        )
        connect = session.ws_connect
    else:
        import websockets.sync.client

        ws.recv.side_effect = [json.dumps(event) for event in (events or _events())]
        credential.get_token.return_value = token
        connect = MagicMock(side_effect=failure, return_value=ws)
        monkeypatch.setattr(websockets.sync.client, "connect", connect)
        manager = BetaRealtimeConnectionManager(
            endpoint=_ENDPOINT,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
            api_version="v1",
            agent_name="agent-test",
            extra_headers=headers,
        )
    return manager, ws, connect


async def _call(connection, method, is_async, **kwargs):
    result = getattr(connection, method)(**kwargs)
    return await result if is_async else result


def _spans(telemetry, name):
    return [span for span in telemetry.exporter.get_finished_spans() if span.name == name]


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
async def test_live_protocol_hierarchy_content_and_audio_accounting(telemetry, is_async, content):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    manager, _, connect = _manager(telemetry.monkeypatch, is_async)
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("application") as parent:
        connection = await manager.enter() if is_async else manager.enter()
        assert trace.get_current_span() is parent
        await _call(
            connection,
            "send",
            is_async,
            event={"type": "input_audio_buffer.append", "audio": base64.b64encode(b"\0\0" * 8).decode()},
        )
        await _call(
            connection,
            "send",
            is_async,
            event={
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": _SECRET}],
                },
            },
        )
        for _ in _events():
            event = await _call(connection, "recv", is_async)
            assert event.get("type")
        await _call(
            connection,
            "send",
            is_async,
            event={
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": "call-test",
                    "output": _SECRET,
                },
            },
        )
        await _call(connection, "close", is_async, reason=_SECRET)
        assert trace.get_current_span() is parent
    spans = telemetry.exporter.get_finished_spans()
    (session,) = _spans(telemetry, "voice_agents.realtime.session")
    (handshake,) = _spans(telemetry, "voice_agents.realtime.connect")
    (response,) = _spans(telemetry, "invoke_agent")
    assert len(spans) == 4
    assert session.parent.span_id == parent.get_span_context().span_id
    assert handshake.parent.span_id == session.context.span_id
    assert response.parent.span_id == session.context.span_id
    assert len({span.context.trace_id for span in spans}) == 1
    assert session.attributes["gen_ai.provider.name"] == "microsoft.foundry"
    assert session.attributes["az.namespace"] == "Microsoft.CognitiveServices"
    assert session.attributes["server.address"] == "example.test"
    assert session.attributes[_PREFIX + "input.audio.bytes"] == 16
    assert session.attributes[_PREFIX + "output.audio.bytes"] == 24
    assert response.attributes[_PREFIX + "output.audio.bytes"] == 24
    assert response.attributes[_PREFIX + "response.time_to_first_audio_seconds"] >= 0
    assert response.attributes["gen_ai.usage.input_tokens"] == 3
    assert response.status.status_code is StatusCode.OK
    assert any(event.name == "voice_agents.tool.requested" for event in response.events)
    assert any(event.name == "voice_agents.tool.output_sent" for event in session.events)
    exported = json.dumps([json.loads(span.to_json()) for span in spans])
    assert (_SECRET in exported) is content
    assert base64.b64encode(b"\x01\x00" * 12).decode() not in exported
    headers = connect.call_args.kwargs["headers" if is_async else "additional_headers"]
    assert headers["traceparent"].split("-")[1] == format(session.context.trace_id, "032x")


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_disabled_and_uninstrumented_have_no_voice_spans(telemetry, is_async):
    telemetry.instrumentor.uninstrument()
    manager, _, connect = _manager(telemetry.monkeypatch, is_async)
    connection = await manager.enter() if is_async else manager.enter()
    await _call(connection, "close", is_async)
    assert not telemetry.exporter.get_finished_spans()
    assert "traceparent" not in connect.call_args.kwargs["headers" if is_async else "additional_headers"]
    assert not voice._ORIGINALS


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_connection_failure_closes_both_spans_without_error_content(telemetry, is_async):
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, failure=OSError(_SECRET))
    with pytest.raises(ConnectionError):
        if is_async:
            await manager.enter()
        else:
            manager.enter()
    spans = telemetry.exporter.get_finished_spans()
    assert {span.name for span in spans} == {"voice_agents.realtime.session", "voice_agents.realtime.connect"}
    assert all(span.status.status_code is StatusCode.ERROR for span in spans)
    assert _SECRET not in "".join(span.to_json() for span in spans)
    assert not voice._SESSIONS


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_interrupted_response_and_repeated_close_end_only_once(telemetry, is_async):
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=_events()[:3])
    connection = await manager.enter() if is_async else manager.enter()
    for _ in range(3):
        await _call(connection, "recv", is_async)
    await _call(connection, "send", is_async, event={"type": "response.cancel", "response_id": "response-test"})
    await _call(connection, "close", is_async)
    await _call(connection, "close", is_async)
    (response,) = _spans(telemetry, "invoke_agent")
    assert response.attributes[_PREFIX + "response.status"] == "interrupted"
    assert response.status.status_code is not StatusCode.ERROR
    assert len(telemetry.exporter.get_finished_spans()) == 3


def _rest_client(payload, status=200):
    response = requests.Response()
    response.status_code = status
    response.reason = "test"
    response.headers["content-type"] = "application/json"
    response._content = json.dumps(payload).encode()
    response._content_consumed = True
    response.raw = HTTPResponse(body=io.BytesIO(response._content), preload_content=False)
    transport_session = MagicMock()
    transport_session.request.return_value = response
    credential = MagicMock()
    credential.get_token.return_value = AccessToken("fake-token", 4_102_444_800)
    client = AIProjectClient(
        endpoint=_ENDPOINT,
        credential=credential,
        allow_preview=True,
        transport=RequestsTransport(session=transport_session, session_owner=False),
    )
    return client


def test_voice_creation_reuses_foundry_span_without_duplicates(telemetry):
    definition = models.VoiceAgentDefinition(model="test-model", model_type="managed", instructions=_SECRET)
    with _rest_client(
        {"id": "agent-test:1", "name": "agent-test", "version": "1", "definition": definition.as_dict()}
    ) as client:
        result = client.agents.create_version("agent-test", definition=definition)
    assert result.version == "1"
    (span,) = _spans(telemetry, "create_agent")
    assert span.attributes["gen_ai.agent.type"] == "voice"
    assert span.attributes["gen_ai.agent.version"] == "1"
    assert _SECRET not in span.to_json()
    assert not _spans(telemetry, "create_agent agent-test")
    assert not [span for span in telemetry.exporter.get_finished_spans() if span.name.endswith(".create_version")]


def test_rest_delete_error_status_has_no_raw_service_error(telemetry):
    with _rest_client({"error": {"code": "not_found", "message": _SECRET}}, status=404) as client:
        with pytest.raises(ResourceNotFoundError):
            client.beta.voice_agents.conversations.delete("agent-test", "conversation-test")
    (span,) = _spans(telemetry, "voice_agents.conversations.delete")
    assert span.status.status_code is StatusCode.ERROR
    assert span.attributes["http.response.status_code"] == 404
    assert not span.events
    assert _SECRET not in span.to_json()


def test_opt_out_per_rest_call_and_experimental_gate(telemetry):
    with _rest_client({}, status=204) as client:
        client.beta.voice_agents.conversations.delete(
            "agent-test", "conversation-test", tracing_options={"enabled": False}
        )
    assert not _spans(telemetry, "voice_agents.conversations.delete")
    telemetry.instrumentor.uninstrument()
    telemetry.monkeypatch.setenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "false")
    telemetry.instrumentor.instrument()
    assert not voice._ORIGINALS


@pytest.mark.asyncio
async def test_cross_task_response_parent_and_context_are_preserved(telemetry):
    manager, _, _ = _manager(telemetry.monkeypatch, True)
    with trace.get_tracer(__name__).start_as_current_span("application") as parent:
        connection = await manager.enter()

    async def receive():
        assert trace.get_current_span().get_span_context().span_id == 0
        for _ in _events():
            await connection.recv()
        await connection.close()

    await asyncio.create_task(receive())
    (session,) = _spans(telemetry, "voice_agents.realtime.session")
    (response,) = _spans(telemetry, "invoke_agent")
    assert session.parent.span_id == parent.get_span_context().span_id
    assert response.parent.span_id == session.context.span_id


def test_non_recording_avoids_sensitive_mutations(telemetry):
    provider = TracerProvider(sampler=ALWAYS_OFF)
    telemetry.monkeypatch.setattr(trace, "_TRACER_PROVIDER", provider)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    with manager as connection:
        for _ in _events():
            connection.recv()
    assert not telemetry.exporter.get_finished_spans()
    assert not voice._SESSIONS
    provider.shutdown()


def test_provider_failure_does_not_change_socket_results(telemetry, caplog):
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    telemetry.monkeypatch.setattr(voice, "_start", MagicMock(side_effect=RuntimeError(_SECRET)))
    with manager as connection:
        assert connection.recv().type == "session.created"
    assert "Unable to record Voice Agents telemetry." in caplog.text
    assert _SECRET not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("status", ["completed", "cancelled", "failed"])
async def test_response_status_and_shared_metrics(telemetry, is_async, status):
    events = _events()
    events[-1]["response"]["status"] = status
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    for _ in events:
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "invoke_agent")
    assert span.attributes[_PREFIX + "response.status"] == status
    assert (span.status.status_code is StatusCode.ERROR) == (status == "failed")
    if status == "cancelled":
        assert span.attributes[_PREFIX + "cancelled"] is True
    metrics_data = telemetry.metric_reader.get_metrics_data()
    metrics = {
        metric.name: metric
        for resource in metrics_data.resource_metrics
        for scope in resource.scope_metrics
        for metric in scope.metrics
    }
    (duration,) = metrics["gen_ai.client.operation.duration"].data.data_points
    assert duration.count == 1
    assert duration.sum >= 0
    assert duration.attributes["gen_ai.operation.name"] == "invoke_agent"
    usage = metrics["gen_ai.client.token.usage"].data.data_points
    assert sorted(point.sum for point in usage) == [3, 7]
    assert all("gen_ai.response.id" not in point.attributes for point in usage)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_server_errors_and_transport_errors_are_sanitized(telemetry, is_async):
    events = [
        {"type": "error", "error": {"type": _SECRET, "code": _SECRET, "message": _SECRET}},
        {"type": "error", "error": {"type": "invalid_request_error", "code": "invalid_event", "message": _SECRET}},
        {"type": "warning", "message": _SECRET},
    ]
    manager, ws, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    for _ in events:
        await _call(connection, "recv", is_async)
    if is_async:
        ws.receive.side_effect = ConnectionResetError(_SECRET)
    else:
        ws.recv.side_effect = ConnectionResetError(_SECRET)
    ws.close_code = 1011
    with pytest.raises(ConnectionResetError):
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (session,) = _spans(telemetry, "voice_agents.realtime.session")
    assert session.status.status_code is StatusCode.ERROR
    assert session.attributes[_PREFIX + "close.was_clean"] is False
    assert session.events[0].attributes["error.type"] == "Error"
    assert session.events[1].attributes[_PREFIX + "error.code"] == "invalid_event"
    assert _SECRET not in session.to_json()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_connection_context_error_and_cancellation_preserve_exception(telemetry, is_async):
    manager, _, _ = _manager(telemetry.monkeypatch, is_async)
    error = asyncio.CancelledError(_SECRET) if is_async else ValueError(_SECRET)
    with pytest.raises(type(error)):
        if is_async:
            async with manager:
                raise error
        else:
            with manager:
                raise error
    (session,) = _spans(telemetry, "voice_agents.realtime.session")
    if is_async:
        assert session.attributes[_PREFIX + "cancelled"] is True
        assert session.status.status_code is not StatusCode.ERROR
    else:
        assert session.status.status_code is StatusCode.ERROR
    assert _SECRET not in session.to_json()


def test_uninstrument_ends_open_spans_and_restores_methods(telemetry):
    manager, _, _ = _manager(telemetry.monkeypatch, False, events=_events()[:3])
    connection = manager.enter()
    for _ in range(3):
        connection.recv()
    AIProjectInstrumentor().uninstrument()
    assert len(_spans(telemetry, "invoke_agent")) == 1
    assert len(_spans(telemetry, "voice_agents.realtime.session")) == 1
    assert not voice._ORIGINALS and not voice._SESSIONS
    connection.close()
    assert len(telemetry.exporter.get_finished_spans()) == 3


def test_response_and_content_tracking_are_bounded(telemetry):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    for index in range(voice._MAX_RESPONSES + 5):
        state.received({"type": "response.created", "response": {"id": f"response-{index}"}})
    assert len(state.responses) == voice._MAX_RESPONSES
    assert state.untracked == 5
    for index in range(voice._MAX_PARTS + 5):
        state.received(
            {
                "type": "response.output_text.done",
                "response_id": "response-0",
                "item_id": f"item-{index}",
                "content_index": index,
                "text": "X" * (voice._MAX_CONTENT + 5),
            }
        )
    assert len(state.responses["response-0"].parts) == voice._MAX_PARTS
    assert all(len(part["content"]) == voice._MAX_CONTENT for part in state.responses["response-0"].parts.values())
    connection.close()
    assert not state.responses


@pytest.mark.parametrize("content", [False, True])
def test_content_environment_uses_foundry_precedence(telemetry, content):
    telemetry.monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", str(content))
    telemetry.instrumentor.instrument()
    assert telemetry.instrumentor.is_content_recording_enabled() is content
    definition = models.VoiceAgentDefinition(model="test-model", model_type="managed", instructions=_SECRET)
    with _rest_client(
        {"id": "agent-test:1", "name": "agent-test", "version": "1", "definition": definition.as_dict()}
    ) as client:
        client.agents.create_version("agent-test", definition=definition)
    (span,) = _spans(telemetry, "create_agent")
    assert (_SECRET in span.to_json()) is content


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_propagation_opt_out_and_existing_header_preserved(telemetry, is_async):
    telemetry.instrumentor.instrument(enable_trace_context_propagation=False)
    manager, _, connect = _manager(telemetry.monkeypatch, is_async)
    connection = await manager.enter() if is_async else manager.enter()
    await _call(connection, "close", is_async)
    assert "traceparent" not in connect.call_args.kwargs["headers" if is_async else "additional_headers"]
    telemetry.instrumentor.instrument(enable_trace_context_propagation=True)
    supplied = {"TraceParent": "application-provided-context"}
    manager, _, connect = _manager(telemetry.monkeypatch, is_async, headers=supplied)
    connection = await manager.enter() if is_async else manager.enter()
    await _call(connection, "close", is_async)
    sent = connect.call_args.kwargs["headers" if is_async else "additional_headers"]
    assert sent["TraceParent"] == "application-provided-context"
    assert "traceparent" not in sent
    assert supplied == {"TraceParent": "application-provided-context"}


@pytest.mark.asyncio
async def test_async_generation_rest_uses_same_span_and_no_new_public_api(telemetry):
    response = SimpleNamespace(
        status_code=200,
        headers={},
        json=lambda: {
            "id": "agent-test",
            "name": "agent-test",
            "versions": {
                "latest": {
                    "id": "agent-test:1",
                    "name": "agent-test",
                    "version": "1",
                    "definition": {"kind": "voice", "model": "test-model", "model_type": "managed"},
                }
            },
        },
    )
    credential = MagicMock()
    credential.get_token = AsyncMock(return_value=AccessToken("fake-token", 4_102_444_800))
    async with AsyncAIProjectClient(endpoint=_ENDPOINT, credential=credential, allow_preview=True) as client:
        telemetry.monkeypatch.setattr(
            client._client._pipeline, "run", AsyncMock(return_value=SimpleNamespace(http_response=response))
        )
        result = await client.beta.agents.create_from_prompt(
            models.GenerateVoiceAgentRequest(kind=models.AgentKind.VOICE, name="agent-test")
        )
    assert result.name == "agent-test"
    (span,) = _spans(telemetry, "create_agent")
    assert span.attributes["gen_ai.request.model"] == "test-model"
    assert span.attributes["gen_ai.agent.type"] == "voice"


def test_non_voice_existing_create_span_is_unchanged(telemetry):
    definition = models.PromptAgentDefinition(model="test-model", instructions="public test prompt")
    with _rest_client(
        {"id": "agent-test:1", "name": "agent-test", "version": "1", "definition": definition.as_dict()}
    ) as client:
        client.agents.create_version(agent_name="agent-test", definition=definition)
    (span,) = _spans(telemetry, "create_agent agent-test")
    assert span.attributes["gen_ai.agent.type"] == "prompt"
    assert not _spans(telemetry, "create_agent")


@pytest.mark.parametrize("backend", [None, "opentelemetry"])
@pytest.mark.parametrize("experimental", [False, True])
def test_voice_and_prompt_share_global_tracing_configuration(telemetry, backend, experimental):
    telemetry.instrumentor.uninstrument()
    settings.tracing_implementation = backend
    telemetry.monkeypatch.setenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", str(experimental).lower())
    telemetry.instrumentor.instrument()
    for definition in (
        models.VoiceAgentDefinition(model="test-model", model_type="managed", instructions="public test prompt"),
        models.PromptAgentDefinition(model="test-model", instructions="public test prompt"),
    ):
        with _rest_client(
            {"id": "agent-test:1", "name": "agent-test", "version": "1", "definition": definition.as_dict()}
        ) as client:
            client.agents.create_version(agent_name="agent-test", definition=definition)
    enabled = experimental and backend is not None
    assert len(_spans(telemetry, "create_agent")) == int(enabled)
    assert len(_spans(telemetry, "create_agent agent-test")) == int(enabled)


_MUTATIONS = [
    (
        "create_call_job",
        ("agent-test", {"binding_id": "binding-test", "phone_number": _SECRET}),
        {"idempotency_key": "key-test"},
    ),
    (
        "cancel_call_job",
        ("agent-test", "call-job-test"),
        {"etag": "etag-test", "match_condition": MatchConditions.IfNotModified},
    ),
    ("transfer_call", ("agent-test", "call-test"), {"target": _SECRET}),
    ("end_call", ("agent-test", "call-test"), {}),
    ("create_binding", ("agent-test", {"provider": "twilio", "connection_name": _SECRET, "phone_number": _SECRET}), {}),
    (
        "update_binding",
        ("agent-test", "binding-test", {"phone_number": _SECRET}),
        {"etag": "etag-test", "match_condition": MatchConditions.IfNotModified},
    ),
    (
        "delete_binding",
        ("agent-test", "binding-test"),
        {"etag": "etag-test", "match_condition": MatchConditions.IfNotModified},
    ),
    (
        "replace_transfer_targets",
        ("agent-test",),
        {"transfer_targets": [], "etag": "etag-test", "match_condition": MatchConditions.IfNotModified},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("method,args,kwargs", _MUTATIONS, ids=[item[0] for item in _MUTATIONS])
async def test_telephony_mutations_names_and_safe_errors(telemetry, is_async, method, args, kwargs):
    if is_async:
        response = SimpleNamespace(
            status_code=404,
            reason="Not Found",
            headers={},
            json=lambda: {"error": {"code": "not_found", "message": _SECRET}},
            text=lambda: _SECRET,
        )
        credential = MagicMock()
        credential.get_token = AsyncMock(return_value=AccessToken("fake-token", 4_102_444_800))
        async with AsyncAIProjectClient(endpoint=_ENDPOINT, credential=credential, allow_preview=True) as client:
            telemetry.monkeypatch.setattr(
                client._client._pipeline, "run", AsyncMock(return_value=SimpleNamespace(http_response=response))
            )
            with pytest.raises(ResourceNotFoundError):
                await getattr(client.beta.voice_agents.telephony, method)(*args, **kwargs)
    else:
        with _rest_client({"error": {"code": "not_found", "message": _SECRET}}, status=404) as client:
            with pytest.raises(ResourceNotFoundError):
                getattr(client.beta.voice_agents.telephony, method)(*args, **kwargs)
    (span,) = _spans(telemetry, "voice_agents.telephony." + method)
    assert span.attributes[_PREFIX + "operation"] == method
    assert span.attributes["http.response.status_code"] == 404
    assert span.status.status_code is StatusCode.ERROR
    assert _SECRET not in span.to_json()


def test_explicit_rest_enable_overrides_global_disable(telemetry):
    settings.tracing_enabled = False
    with _rest_client({}, status=204) as client:
        client.beta.voice_agents.conversations.delete(
            "agent-test", "conversation-test", tracing_options={"enabled": True}
        )
    assert len(_spans(telemetry, "voice_agents.conversations.delete")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("include_baggage", [False, True])
async def test_baggage_requires_existing_explicit_opt_in(telemetry, is_async, include_baggage):
    from opentelemetry import baggage, context

    telemetry.instrumentor.instrument(enable_baggage_propagation=include_baggage)
    token = context.attach(baggage.set_baggage("public-test-key", "public-test-value"))
    try:
        manager, _, connect = _manager(telemetry.monkeypatch, is_async)
        connection = await manager.enter() if is_async else manager.enter()
        await _call(connection, "close", is_async)
    finally:
        context.detach(token)
    headers = connect.call_args.kwargs["headers" if is_async else "additional_headers"]
    assert ("baggage" in headers) is include_baggage
    assert "public-test-value" not in "".join(span.to_json() for span in telemetry.exporter.get_finished_spans())


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_failed_audio_send_is_not_counted(telemetry, is_async):
    manager, ws, _ = _manager(telemetry.monkeypatch, is_async)
    connection = await manager.enter() if is_async else manager.enter()
    if is_async:
        ws.send_str.side_effect = TimeoutError(_SECRET)
    else:
        ws.send.side_effect = TimeoutError(_SECRET)
    with pytest.raises(TimeoutError):
        await _call(
            connection,
            "send",
            is_async,
            event={"type": "input_audio_buffer.append", "audio": base64.b64encode(b"\0\0" * 12).decode()},
        )
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert span.attributes[_PREFIX + "input.audio.bytes"] == 0
    assert span.events[0].name == "voice_agents.send.failed"
    assert _SECRET not in span.to_json()


def test_untrusted_close_code_and_binary_opt_in_never_export_media(telemetry):
    telemetry.monkeypatch.setenv("AZURE_TRACING_GEN_AI_INCLUDE_BINARY_DATA", "true")
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    for _ in _events():
        connection.recv()
    getattr(connection, "_voice_trace").close(code=_SECRET)
    connection.close()
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert _PREFIX + "close.code" not in span.attributes
    assert _SECRET not in span.to_json()
    assert base64.b64encode(b"\x01\x00" * 12).decode() not in "".join(
        item.to_json() for item in telemetry.exporter.get_finished_spans()
    )


@pytest.mark.parametrize("global_disable", [False, True])
def test_voice_creation_disable_does_not_fall_back_to_existing_wrapper(telemetry, global_disable):
    settings.tracing_enabled = not global_disable
    definition = models.VoiceAgentDefinition(model="test-model", model_type="managed", instructions=_SECRET)
    with _rest_client(
        {"id": "agent-test:1", "name": "agent-test", "version": "1", "definition": definition.as_dict()}
    ) as client:
        options = {} if global_disable else {"tracing_options": {"enabled": False}}
        result = client.agents.create_version(agent_name="agent-test", definition=definition, **options)
    assert result.version == "1"
    assert not [span for span in telemetry.exporter.get_finished_spans() if span.name.startswith("create_agent")]


@pytest.mark.asyncio
@pytest.mark.parametrize("audio", [False, True], ids=["tool-result", "audio"])
async def test_async_send_records_serialized_payload_not_later_mutation(telemetry, audio):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, ws, _ = _manager(telemetry.monkeypatch, True)
    connection = await manager.enter()
    sending = asyncio.Event()
    release = asyncio.Event()

    async def wait_for_send(_payload):
        sending.set()
        await release.wait()

    ws.send_str.side_effect = wait_for_send
    event: dict[str, Any] = (
        {"type": "input_audio_buffer.append", "audio": base64.b64encode(b"\0\0" * 12).decode()}
        if audio
        else {
            "type": "conversation.item.create",
            "item": {"type": "function_call_output", "call_id": "call-test", "output": "original result"},
        }
    )
    task = asyncio.create_task(connection.send(event))
    await sending.wait()
    if audio:
        event["audio"] = base64.b64encode(b"\0\0" * 36).decode()
    else:
        event["item"]["output"] = _SECRET
    release.set()
    await task
    await connection.close()
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    serialized_payload = json.loads(ws.send_str.call_args.args[0])
    if audio:
        assert len(base64.b64decode(serialized_payload["audio"])) == 24
        assert span.attributes[_PREFIX + "input.audio.bytes"] == 24
    else:
        assert serialized_payload["item"]["output"] == "original result"
        assert "original result" in span.attributes["gen_ai.input.messages"]
        assert _SECRET not in span.to_json()


def test_completed_system_tool_summary_is_not_duplicated(telemetry):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    state.received({"type": "response.created", "response": {"id": "response-test"}})
    state.received(
        {
            "type": "response.system_tool_arguments.done",
            "response_id": "response-test",
            "item_id": "item-system-test",
            "call_id": "call-test",
            "name": "end_conversation",
            "arguments": "{}",
        }
    )
    state.received(
        {
            "type": "response.done",
            "response": {
                "id": "response-test",
                "status": "completed",
                "output": [
                    {
                        "type": "system_tool",
                        "id": "item-system-test",
                        "call_id": "call-test",
                        "name": "end_conversation",
                        "arguments": "{}",
                    }
                ],
            },
        }
    )
    connection.close()
    (response,) = _spans(telemetry, "invoke_agent")
    messages = json.loads(response.attributes["gen_ai.output.messages"])
    assert len(messages) == 1
    assert len(messages[0]["parts"]) == 1
    assert messages[0]["parts"][0]["name"] == "end_conversation"


def test_output_fallback_matches_content_index_and_type(telemetry):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    state.received({"type": "response.created", "response": {"id": "response-test"}})
    state.received(
        {
            "type": "response.output_text.done",
            "response_id": "response-test",
            "item_id": "item-test",
            "content_index": 2,
            "text": "only third part",
        }
    )
    state.received(
        {
            "type": "response.done",
            "response": {
                "id": "response-test",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "id": "item-test",
                        "content": [{"type": "output_audio"}, {"type": "output_text"}, {"type": "output_text"}],
                    }
                ],
            },
        }
    )
    connection.close()
    (response,) = _spans(telemetry, "invoke_agent")
    parts = json.loads(response.attributes["gen_ai.output.messages"])[0]["parts"]
    assert "content" not in parts[0] and "content" not in parts[1]
    assert parts[2]["content"] == "only third part"


def test_tracking_keys_do_not_retain_oversized_service_identifiers(telemetry):
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    state.received({"type": "response.created", "response": {"id": "response-test"}})
    oversized = "id-" + "X" * (voice._MAX_CONTENT * 2)
    state.received(
        {
            "type": "response.output_text.done",
            "response_id": "response-test",
            "item_id": oversized,
            "content_index": 0,
            "text": "public",
        }
    )
    state.received(
        {
            "type": "response.function_call_arguments.done",
            "response_id": "response-test",
            "call_id": oversized,
            "name": "test",
            "arguments": "{}",
        }
    )
    tracked = state.responses["response-test"]
    assert all(len(key[0]) <= voice._MAX_CONTENT for key in tracked.parts)
    assert all(len(key) <= voice._MAX_CONTENT + 5 for key in tracked.messages)
    connection.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_abnormal_explicit_close_has_error_status_and_not_clean_flag(telemetry, is_async):
    manager, ws, _ = _manager(telemetry.monkeypatch, is_async)
    connection = await manager.enter() if is_async else manager.enter()
    ws.close_code = 1011
    await _call(connection, "close", is_async, code=1011)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert span.attributes[_PREFIX + "close.was_clean"] is False
    assert span.status.status_code is StatusCode.ERROR


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_context_failure_marks_pending_responses_failed(telemetry, is_async):
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=_events()[:3])
    with pytest.raises(ValueError):
        if is_async:
            async with manager as connection:
                for _ in range(3):
                    await connection.recv()
                raise ValueError(_SECRET)
        else:
            with manager as connection:
                for _ in range(3):
                    connection.recv()
                raise ValueError(_SECRET)
    (span,) = _spans(telemetry, "invoke_agent")
    assert span.attributes[_PREFIX + "response.status"] == "interrupted"
    assert span.status.status_code is StatusCode.ERROR
    assert _SECRET not in span.to_json()


@pytest.mark.asyncio
async def test_cancelled_receive_then_local_close_is_cancellation_not_failure(telemetry):
    manager, ws, _ = _manager(telemetry.monkeypatch, True)
    connection = await manager.enter()
    ws.receive.side_effect = asyncio.CancelledError(_SECRET)
    with pytest.raises(asyncio.CancelledError):
        await connection.recv()
    ws.close_code = 1006
    await connection.close()
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert span.attributes[_PREFIX + "cancelled"] is True
    assert span.attributes[_PREFIX + "close.code"] == 1006
    assert span.attributes[_PREFIX + "close.was_clean"] is False
    assert span.status.status_code is not StatusCode.ERROR
    assert span.events[0].name == "voice_agents.receive.cancelled"
    assert _SECRET not in span.to_json()


@pytest.mark.asyncio
async def test_cancelled_receive_does_not_hide_subsequent_server_failure(telemetry):
    import aiohttp

    manager, ws, _ = _manager(telemetry.monkeypatch, True)
    connection = await manager.enter()
    ws.receive.side_effect = asyncio.CancelledError()
    with pytest.raises(asyncio.CancelledError):
        await connection.recv()
    ws.receive.side_effect = None
    ws.receive.return_value = SimpleNamespace(type=aiohttp.WSMsgType.CLOSE, data=None)
    ws.close_code = 1011
    with pytest.raises(ConnectionResetError):
        await connection.recv()
    await connection.close()
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert span.status.status_code is StatusCode.ERROR
    assert span.attributes[_PREFIX + "close.code"] == 1011


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
@pytest.mark.parametrize("role", ["system", "user", "assistant"])
async def test_input_message_summary_preserves_supported_roles(telemetry, is_async, content, role):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    manager, _, _ = _manager(telemetry.monkeypatch, is_async)
    connection = await manager.enter() if is_async else manager.enter()
    await _call(
        connection,
        "send",
        is_async,
        event={
            "type": "conversation.item.create",
            "item": {"type": "message", "role": role, "content": [{"type": "input_text", "text": _SECRET}]},
        },
    )
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    (message,) = json.loads(span.attributes["gen_ai.input.messages"])
    assert message["role"] == role
    assert (_SECRET in span.to_json()) is content


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
@pytest.mark.parametrize("boundary", ["commit", "clear", "vad"])
@pytest.mark.parametrize("ending", ["pending", "failed", "completed"])
async def test_audio_turn_summary_replaces_prior_transcript(telemetry, is_async, content, boundary, ending):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    events = [
        {"type": "input_audio_buffer.committed", "item_id": "audio-first"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": "FIRST PUBLIC TURN",
        },
        {
            "type": "input_audio_buffer.speech_started" if boundary == "vad" else "input_audio_buffer.committed",
            "item_id": "audio-second",
        },
        {
            "type": "conversation.item.input_audio_transcription."
            + ("completed" if ending == "completed" else "failed"),
            "item_id": "audio-second",
            "transcript": "SECOND PUBLIC TURN",
        },
    ]
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    append = {"type": "input_audio_buffer.append", "audio": "AQABAA=="}
    await _call(connection, "send", is_async, event=append)
    if boundary != "vad":
        await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    await _call(connection, "recv", is_async)
    await _call(connection, "recv", is_async)
    if boundary == "clear":
        await _call(connection, "send", is_async, event={"type": "input_audio_buffer.clear"})
    await _call(connection, "send", is_async, event=append)
    if ending != "pending":
        await _call(connection, "recv", is_async)
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    (message,) = json.loads(span.attributes["gen_ai.input.messages"])
    assert message["role"] == "user" and message["parts"][0]["type"] == "audio"
    assert "FIRST PUBLIC TURN" not in span.attributes["gen_ai.input.messages"]
    if content and ending == "completed":
        assert message["parts"][0]["content"] == "SECOND PUBLIC TURN"
    else:
        assert "content" not in message["parts"][0]
    assert span.attributes[_PREFIX + "input.audio.bytes"] == 8


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("latest", ["text", "tool", "audio-pending", "audio-confirmed"])
async def test_late_audio_events_cannot_overwrite_newer_input(telemetry, is_async, latest):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    events = [
        {"type": "input_audio_buffer.committed", "item_id": "audio-first"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": "FIRST TURN",
        },
        {"type": "input_audio_buffer.speech_started", "item_id": "audio-second"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": _SECRET,
        },
        {"type": "conversation.item.input_audio_transcription.failed", "item_id": "audio-first"},
        {"type": "input_audio_buffer.committed", "item_id": "audio-first"},
    ]
    if latest != "audio-confirmed":
        events.pop(2)
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    append = {"type": "input_audio_buffer.append", "audio": "AQABAA=="}
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    await _call(connection, "recv", is_async)
    await _call(connection, "recv", is_async)
    if latest in ("text", "tool"):
        item = (
            {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "LATEST TEXT"}]}
            if latest == "text"
            else {"type": "function_call_output", "call_id": "call-latest", "output": "LATEST RESULT"}
        )
        await _call(connection, "send", is_async, event={"type": "conversation.item.create", "item": item})
    else:
        await _call(connection, "send", is_async, event=append)
        if latest == "audio-confirmed":
            await _call(connection, "recv", is_async)
    for _ in range(3):
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    (message,) = json.loads(span.attributes["gen_ai.input.messages"])
    assert _SECRET not in span.to_json()
    if latest == "text":
        assert message["parts"][0]["content"] == "LATEST TEXT"
    elif latest == "tool":
        assert message["parts"][0]["result"] == "LATEST RESULT"
    else:
        assert message["parts"][0] == {"type": "audio"}


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
@pytest.mark.parametrize("boundary", ["client-clear", "server-cleared", "client-commit"])
async def test_audio_summary_guard_resets_at_explicit_buffer_boundaries(telemetry, is_async, content, boundary):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    events = [
        {"type": "input_audio_buffer.speech_started", "item_id": "audio-first", "audio_start_ms": 0},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": _SECRET,
        },
        {"type": "input_audio_buffer.cleared"},
    ]
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    append = {"type": "input_audio_buffer.append", "audio": "AQABAA=="}
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "recv", is_async)
    await _call(connection, "recv", is_async)
    if boundary == "server-cleared":
        await _call(connection, "recv", is_async)
    else:
        await _call(
            connection,
            "send",
            is_async,
            event={"type": "input_audio_buffer.clear" if boundary == "client-clear" else "input_audio_buffer.commit"},
        )
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert json.loads(span.attributes["gen_ai.input.messages"]) == [{"role": "user", "parts": [{"type": "audio"}]}]
    assert span.attributes[_PREFIX + "input.audio.bytes"] == 8


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
async def test_audio_text_audio_alternation_keeps_only_latest_input(telemetry, is_async, content):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    events = [
        {"type": "input_audio_buffer.committed", "item_id": "audio-first"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": "FIRST AUDIO",
        },
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": _SECRET,
        },
        {"type": "input_audio_buffer.committed", "item_id": "audio-second"},
        {"type": "input_audio_buffer.speech_started", "item_id": "audio-first", "audio_start_ms": 0},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": _SECRET,
        },
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-second",
            "transcript": "LATEST AUDIO",
        },
    ]
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    append = {"type": "input_audio_buffer.append", "audio": "AQABAA=="}
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    for _ in range(2):
        await _call(connection, "recv", is_async)
    await _call(
        connection,
        "send",
        is_async,
        event={
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "LATEST TEXT"}],
            },
        },
    )
    await _call(connection, "recv", is_async)
    state = getattr(connection, "_voice_trace")
    expected = [{"role": "user", "parts": [{"type": "text", **({"content": "LATEST TEXT"} if content else {})}]}]
    assert json.loads(state.span.span_instance.attributes["gen_ai.input.messages"]) == expected
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    for _ in range(4):
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    part = json.loads(span.attributes["gen_ai.input.messages"])[0]["parts"][0]
    assert part == {"type": "audio", **({"content": "LATEST AUDIO"} if content else {})}
    assert span.attributes[_PREFIX + "input.audio.bytes"] == 8
    assert _SECRET not in span.to_json()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("content", [False, True])
async def test_interleaved_audio_text_outputs_stay_with_their_response(telemetry, is_async, content):
    telemetry.instrumentor.instrument(enable_content_recording=content)
    events = [
        {"type": "response.created", "response": {"id": "response-first"}},
        {"type": "response.created", "response": {"id": "response-second"}},
        {"type": "response.output_audio.delta", "response_id": "response-first", "delta": "AQABAA=="},
        {"type": "response.output_text.delta", "response_id": "response-second", "delta": "SECOND TEXT"},
        {
            "type": "response.output_audio_transcript.done",
            "response_id": "response-first",
            "item_id": "output-item",
            "content_index": 0,
            "transcript": "FIRST AUDIO",
        },
        {
            "type": "response.output_text.done",
            "response_id": "response-second",
            "item_id": "output-item",
            "content_index": 1,
            "text": "SECOND TEXT",
        },
        {"type": "response.output_audio.delta", "response_id": "response-second", "delta": "AQABAAEAAQA="},
        {"type": "response.output_text.delta", "response_id": "response-first", "delta": "FIRST TEXT"},
        {
            "type": "response.output_audio_transcript.done",
            "response_id": "response-second",
            "item_id": "output-item",
            "content_index": 0,
            "transcript": "SECOND AUDIO",
        },
        {
            "type": "response.output_text.done",
            "response_id": "response-first",
            "item_id": "output-item",
            "content_index": 1,
            "text": "FIRST TEXT",
        },
    ]
    for identifier in ("response-second", "response-first"):
        events.append(
            {
                "type": "response.output_audio.done",
                "response_id": identifier,
                "item_id": "output-item",
                "content_index": 0,
            }
        )
        events.append(
            {
                "type": "response.done",
                "response": {
                    "id": identifier,
                    "status": "completed",
                    "output": [
                        {
                            "type": "message",
                            "role": "assistant",
                            "id": "output-item",
                            "content": [{"type": "output_audio"}, {"type": "output_text"}],
                        },
                    ],
                },
            }
        )
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    for _ in events:
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (session,) = _spans(telemetry, "voice_agents.realtime.session")
    spans = {span.attributes["gen_ai.response.id"]: span for span in _spans(telemetry, "invoke_agent")}
    assert set(spans) == {"response-first", "response-second"}
    for identifier, size, prefix in (("response-first", 4, "FIRST"), ("response-second", 8, "SECOND")):
        span = spans[identifier]
        parts = json.loads(span.attributes["gen_ai.output.messages"])[0]["parts"]
        assert parts == [
            {"type": "audio", **({"content": prefix + " AUDIO"} if content else {})},
            {"type": "text", **({"content": prefix + " TEXT"} if content else {})},
        ]
        assert span.attributes[_PREFIX + "output.audio.bytes"] == size
        assert span.parent.span_id == session.context.span_id
        assert span.status.status_code is StatusCode.OK
    assert session.attributes[_PREFIX + "output.audio.bytes"] == 12


def test_audio_tracking_is_bounded_and_does_not_write_attributes_per_chunk(telemetry):
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    add_attribute = MagicMock(wraps=state.span.add_attribute)
    telemetry.monkeypatch.setattr(state.span, "add_attribute", add_attribute)
    for index in range(voice._MAX_PARTS * 2):
        state.received({"type": "input_audio_buffer.speech_started", "item_id": "audio-" + str(index)})
    assert len(state.audio_item_ids) == voice._MAX_PARTS
    assert state.input_item_id == "audio-" + str(voice._MAX_PARTS * 2 - 1)
    state.received({"type": "input_audio_buffer.speech_started", "item_id": "X" * (voice._MAX_CONTENT + 1)})
    assert len(state.input_item_id) <= voice._MAX_CONTENT
    writes = add_attribute.call_count
    for _ in range(64):
        connection.send({"type": "input_audio_buffer.append", "audio": "AQABAA=="})
    assert add_attribute.call_count == writes
    connection.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("latest", ["pending", "committed", "text"])
async def test_delayed_audio_commit_acknowledgment_does_not_claim_newer_input(telemetry, is_async, latest):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    events = [
        {"type": "input_audio_buffer.committed", "item_id": "audio-first"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-first",
            "transcript": _SECRET,
        },
        {"type": "input_audio_buffer.committed", "item_id": "audio-second"},
        {
            "type": "conversation.item.input_audio_transcription.completed",
            "item_id": "audio-second",
            "transcript": "LATEST AUDIO",
        },
    ]
    manager, _, _ = _manager(telemetry.monkeypatch, is_async, events=events)
    connection = await manager.enter() if is_async else manager.enter()
    append = {"type": "input_audio_buffer.append", "audio": "AQABAA=="}
    await _call(connection, "send", is_async, event=append)
    await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    if latest == "text":
        await _call(
            connection,
            "send",
            is_async,
            event={
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "LATEST TEXT"}],
                },
            },
        )
    else:
        await _call(connection, "send", is_async, event=append)
        if latest == "committed":
            await _call(connection, "send", is_async, event={"type": "input_audio_buffer.commit"})
    await _call(connection, "recv", is_async)
    await _call(connection, "recv", is_async)
    state = getattr(connection, "_voice_trace")
    message = json.loads(state.span.span_instance.attributes["gen_ai.input.messages"])[0]
    assert _SECRET not in state.span.span_instance.attributes["gen_ai.input.messages"]
    assert message["parts"][0] == (
        {"type": "text", "content": "LATEST TEXT"} if latest == "text" else {"type": "audio"}
    )
    if latest == "committed":
        await _call(connection, "recv", is_async)
        await _call(connection, "recv", is_async)
    await _call(connection, "close", is_async)
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    if latest == "committed":
        assert json.loads(span.attributes["gen_ai.input.messages"])[0]["parts"][0]["content"] == "LATEST AUDIO"
    assert _SECRET not in span.to_json()


def test_pending_audio_commit_tracking_is_bounded_without_misattributing_old_acks(telemetry):
    telemetry.instrumentor.instrument(enable_content_recording=True)
    manager, _, _ = _manager(telemetry.monkeypatch, False)
    connection = manager.enter()
    state = getattr(connection, "_voice_trace")
    count = voice._MAX_PARTS + 2
    for _ in range(count):
        connection.send({"type": "input_audio_buffer.append", "audio": "AQABAA=="})
        connection.send({"type": "input_audio_buffer.commit"})
    assert len(state.pending_audio_commits) == voice._MAX_PARTS
    assert state.untracked_audio_commits == 2
    for index in range(count):
        state.received({"type": "input_audio_buffer.committed", "item_id": "audio-" + str(index)})
        state.received(
            {
                "type": "conversation.item.input_audio_transcription.completed",
                "item_id": "audio-" + str(index),
                "transcript": "LATEST AUDIO" if index == count - 1 else _SECRET,
            }
        )
        assert _SECRET not in state.span.span_instance.attributes["gen_ai.input.messages"]
    assert not state.pending_audio_commits and state.untracked_audio_commits == 0
    assert len(state.audio_item_ids) == voice._MAX_PARTS
    assert len(state.committed_audio_ids) == voice._MAX_PARTS
    connection.close()
    (span,) = _spans(telemetry, "voice_agents.realtime.session")
    assert json.loads(span.attributes["gen_ai.input.messages"])[0]["parts"][0]["content"] == "LATEST AUDIO"
    assert span.attributes[_PREFIX + "input.audio.bytes"] == count * 4
