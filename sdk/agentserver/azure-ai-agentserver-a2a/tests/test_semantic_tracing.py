# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for proposed OpenTelemetry A2A semantic server spans."""

import json
from collections.abc import AsyncIterator
from typing import cast
from unittest.mock import patch

import pytest
from a2a.server.request_handlers import RequestHandler
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from opentelemetry import baggage as _otel_baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import SpanKind, StatusCode
from opentelemetry.sdk.trace import ReadableSpan
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from azure.ai.agentserver.a2a import A2AAgentServerHost

_RPC_PATH = "/a2a"
_FOUNDRY_COMPAT_RPC_PATH = "/invocations/a2a"
_SCOPE = "Azure.AI.AgentServer.A2A"


def _agent_card() -> AgentCard:
    return AgentCard(
        name="Tracing Agent",
        description="Agent Card description",
        version="1.2.3",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC",
                protocol_version="1.0",
                url="http://localhost:8088/a2a",
            )
        ],
        skills=[],
    )


def _host(endpoint) -> A2AAgentServerHost:
    with patch(
        "azure.ai.agentserver.a2a._host.create_jsonrpc_routes",
        return_value=[Route(_RPC_PATH, endpoint, methods=["POST"])],
    ):
        return A2AAgentServerHost(
            agent_card=_agent_card(),
            request_handler=cast(RequestHandler, object()),
            configure_observability=None,
        )


@pytest.fixture
def span_exporter(monkeypatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(
        "azure.ai.agentserver.a2a._tracing._otel_trace.get_tracer",
        provider.get_tracer,
    )
    return exporter


def _a2a_spans(exporter: InMemorySpanExporter) -> list[ReadableSpan]:
    return [
        span
        for span in exporter.get_finished_spans()
        if span.instrumentation_scope is not None and span.instrumentation_scope.name == _SCOPE
    ]


def _attributes(span: ReadableSpan):
    assert span.attributes is not None
    return span.attributes


def _application_data():
    return {
        "taskId": "application-task",
        "contextId": "application-context",
        "status": {"state": "application-state"},
        "task": {"id": "application-nested-task", "status": {"state": "application-nested-state"}},
    }


def _task_result():
    return {
        "id": "task-result",
        "contextId": "ctx-result",
        "status": {
            "state": "TASK_STATE_COMPLETED",
            "message": {"parts": [{"data": _application_data()}]},
        },
        "metadata": _application_data(),
        "artifacts": [
            {
                "artifactId": "artifact-result",
                "metadata": _application_data(),
                "parts": [{"data": _application_data()}],
            }
        ],
        "history": [{"metadata": _application_data(), "parts": [{"data": _application_data()}]}],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,result,state",
    [
        ("SendMessage", {"task": _task_result()}, "TASK_STATE_COMPLETED"),
        ("GetTask", _task_result(), "TASK_STATE_COMPLETED"),
        ("CancelTask", _task_result(), "TASK_STATE_COMPLETED"),
        ("ListTasks", {"tasks": [_task_result()]}, "TASK_STATE_COMPLETED"),
        (
            "SendMessage",
            {
                "message": {
                    "messageId": "message-result",
                    "taskId": "task-result",
                    "contextId": "ctx-result",
                    "metadata": _application_data(),
                    "parts": [{"data": _application_data()}],
                }
            },
            None,
        ),
        (
            "SubscribeToTask",
            {
                "statusUpdate": {
                    "taskId": "task-result",
                    "contextId": "ctx-result",
                    "status": {
                        "state": "TASK_STATE_COMPLETED",
                        "message": {"parts": [{"data": _application_data()}]},
                    },
                    "metadata": _application_data(),
                }
            },
            "TASK_STATE_COMPLETED",
        ),
        (
            "SendStreamingMessage",
            {
                "artifactUpdate": {
                    "taskId": "task-result",
                    "contextId": "ctx-result",
                    "artifact": {"parts": [{"data": _application_data()}], "metadata": _application_data()},
                    "metadata": _application_data(),
                }
            },
            None,
        ),
    ],
)
async def test_protocol_metadata_ignores_application_data(client_factory, span_exporter, method, result, state):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse({"jsonrpc": "2.0", "id": "rpc-result", "result": result})

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            _RPC_PATH,
            headers={"A2A-Version": "1.0"},
            json={"jsonrpc": "2.0", "id": "rpc-result", "method": method, "params": {}},
        )

    assert response.json()["result"] == result
    attributes = _attributes(_a2a_spans(span_exporter)[0])
    assert attributes["a2a.task.id"] == "task-result"
    assert attributes["gen_ai.conversation.id"] == "ctx-result"
    if state is None:
        assert "a2a.task.state" not in attributes
    else:
        assert attributes["a2a.task.state"] == state


@pytest.mark.asyncio
async def test_stream_updates_ignore_application_data(client_factory, span_exporter):
    async def generate() -> AsyncIterator[bytes]:
        for result in (
            {
                "artifactUpdate": {
                    "taskId": "task-result",
                    "contextId": "ctx-result",
                    "artifact": {"parts": [{"data": _application_data()}]},
                }
            },
            {
                "statusUpdate": {
                    "taskId": "task-result",
                    "contextId": "ctx-result",
                    "status": {"state": "TASK_STATE_COMPLETED"},
                    "metadata": _application_data(),
                }
            },
        ):
            yield f"data: {json.dumps({'jsonrpc': '2.0', 'id': 'rpc-result', 'result': result})}\n\n".encode()

    async def endpoint(_request: Request) -> StreamingResponse:
        return StreamingResponse(generate(), media_type="text/event-stream")

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            _RPC_PATH,
            headers={"A2A-Version": "1.0"},
            json={"jsonrpc": "2.0", "id": "rpc-result", "method": "SendStreamingMessage", "params": {}},
        )

    assert response.status_code == 200
    attributes = _attributes(_a2a_spans(span_exporter)[0])
    assert attributes["a2a.task.id"] == "task-result"
    assert attributes["gen_ai.conversation.id"] == "ctx-result"
    assert attributes["a2a.task.state"] == "TASK_STATE_COMPLETED"


@pytest.mark.asyncio
async def test_list_tasks_omits_ambiguous_metadata(client_factory, span_exporter):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": "rpc-list",
                "result": {
                    "tasks": [
                        _task_result(),
                        {
                            "id": "another-task",
                            "contextId": "another-context",
                            "status": {"state": "TASK_STATE_WORKING"},
                        },
                    ]
                },
            }
        )

    async with client_factory(_host(endpoint)) as client:
        await client.post(
            _RPC_PATH,
            json={"jsonrpc": "2.0", "id": "rpc-list", "method": "ListTasks", "params": {}},
        )

    attributes = _attributes(_a2a_spans(span_exporter)[0])
    assert "a2a.task.id" not in attributes
    assert "gen_ai.conversation.id" not in attributes
    assert "a2a.task.state" not in attributes


@pytest.mark.asyncio
@pytest.mark.parametrize("path", [_RPC_PATH, _FOUNDRY_COMPAT_RPC_PATH])
async def test_send_message_emits_semantic_server_span(
    client_factory,
    span_exporter,
    path,
):
    async def endpoint(_request: Request) -> JSONResponse:
        assert _otel_baggage.get_baggage("azure.ai.agentserver.conversation_id") == "ctx-request"
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": "rpc-1",
                "result": {
                    "task": {
                        "id": "task-1",
                        "contextId": "ctx-request",
                        "status": {"state": "TASK_STATE_COMPLETED"},
                    }
                },
            }
        )

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            path,
            headers={
                "A2A-Version": "1.0",
                "traceparent": "00-0123456789abcdef0123456789abcdef-0123456789abcdef-01",
            },
            json={
                "jsonrpc": "2.0",
                "id": "rpc-1",
                "method": "SendMessage",
                "params": {
                    "message": {
                        "messageId": "message-1",
                        "contextId": "ctx-request",
                        "referenceTaskIds": ["task-prior"],
                        "role": "ROLE_USER",
                        "parts": [{"text": "hello"}],
                    }
                },
            },
        )

    assert response.status_code == 200
    spans = _a2a_spans(span_exporter)
    assert len(spans) == 1
    span = spans[0]
    attributes = _attributes(span)
    assert span.name == "SendMessage"
    assert span.kind == SpanKind.SERVER
    assert span.parent is not None
    assert span.context is not None
    assert f"{span.context.trace_id:032x}" == "0123456789abcdef0123456789abcdef"
    assert attributes["a2a.method.name"] == "SendMessage"
    assert attributes["a2a.protocol.version"] == "1.0"
    assert attributes["a2a.message.id"] == "message-1"
    assert attributes["a2a.message.reference_task_ids"] == ("task-prior",)
    assert attributes["a2a.task.id"] == "task-1"
    assert attributes["a2a.task.state"] == "TASK_STATE_COMPLETED"
    assert attributes["gen_ai.conversation.id"] == "ctx-request"
    assert attributes["gen_ai.agent.name"] == "Tracing Agent"
    assert attributes["gen_ai.agent.description"] == "Agent Card description"
    assert attributes["gen_ai.agent.version"] == "1.2.3"
    assert "gen_ai.operation.name" not in attributes
    assert span.status.status_code == StatusCode.UNSET


@pytest.mark.asyncio
async def test_jsonrpc_error_marks_http_200_span_as_error(
    client_factory,
    span_exporter,
):
    async def endpoint(_request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": "rpc-error",
                "error": {"code": -32602, "message": "Invalid params"},
            }
        )

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            _RPC_PATH,
            headers={"A2A-Version": "1.0"},
            json={
                "jsonrpc": "2.0",
                "id": "rpc-error",
                "method": "GetTask",
                "params": {"id": "task-error"},
            },
        )

    assert response.status_code == 200
    span = _a2a_spans(span_exporter)[0]
    attributes = _attributes(span)
    assert attributes["error.type"] == "-32602"
    assert attributes["a2a.task.id"] == "task-error"
    assert span.status.status_code == StatusCode.ERROR


@pytest.mark.asyncio
async def test_streaming_span_covers_stream_and_omits_ambiguous_state(
    client_factory,
    span_exporter,
):
    async def generate() -> AsyncIterator[bytes]:
        for state in ("TASK_STATE_WORKING", "TASK_STATE_COMPLETED"):
            payload = {
                "jsonrpc": "2.0",
                "id": "rpc-stream",
                "result": {
                    "task": {
                        "id": "task-stream",
                        "contextId": "ctx-stream",
                        "status": {"state": state},
                    }
                },
            }
            yield f"data: {json.dumps(payload)}\n\n".encode()

    async def endpoint(_request: Request) -> StreamingResponse:
        return StreamingResponse(generate(), media_type="text/event-stream")

    async with client_factory(_host(endpoint)) as client:
        response = await client.post(
            _RPC_PATH,
            headers={"A2A-Version": "1.0"},
            json={
                "jsonrpc": "2.0",
                "id": "rpc-stream",
                "method": "SendStreamingMessage",
                "params": {
                    "message": {
                        "messageId": "message-stream",
                        "contextId": "ctx-stream",
                        "role": "ROLE_USER",
                        "parts": [{"text": "hello"}],
                    }
                },
            },
        )

    assert response.status_code == 200
    span = _a2a_spans(span_exporter)[0]
    attributes = _attributes(span)
    assert span.name == "SendStreamingMessage"
    assert attributes["a2a.task.id"] == "task-stream"
    assert attributes["gen_ai.conversation.id"] == "ctx-stream"
    assert "a2a.task.state" not in attributes
