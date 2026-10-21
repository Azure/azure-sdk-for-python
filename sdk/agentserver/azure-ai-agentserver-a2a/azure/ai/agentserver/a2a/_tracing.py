# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""OpenTelemetry semantic tracing for inbound A2A operations."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
from collections.abc import Awaitable, Callable
from contextvars import Token
from dataclasses import dataclass, field
from typing import Any, MutableMapping, Optional

from a2a.types import AgentCard
from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
from opentelemetry import trace as _otel_trace
from opentelemetry.context import Context
from opentelemetry.trace import Span, SpanKind, Status, StatusCode
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

from azure.ai.agentserver.core import schedule_flush_spans

from ._version import VERSION as _A2A_VERSION

_INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.A2A"
_BAGGAGE_CONVERSATION_ID = "azure.ai.agentserver.conversation_id"
_MAX_JSON_RESPONSE_BYTES = 1024 * 1024

_ATTR_METHOD = "a2a.method.name"
_ATTR_MESSAGE_ID = "a2a.message.id"
_ATTR_REFERENCE_TASK_IDS = "a2a.message.reference_task_ids"
_ATTR_PROTOCOL_VERSION = "a2a.protocol.version"
_ATTR_TASK_ID = "a2a.task.id"
_ATTR_TASK_STATE = "a2a.task.state"
_ATTR_TENANT = "a2a.tenant"
_ATTR_AGENT_NAME = "gen_ai.agent.name"
_ATTR_AGENT_DESCRIPTION = "gen_ai.agent.description"
_ATTR_AGENT_VERSION = "gen_ai.agent.version"
_ATTR_CONVERSATION_ID = "gen_ai.conversation.id"
_ATTR_ERROR_TYPE = "error.type"


@dataclass
class _OperationMetadata:
    method: str
    protocol_version: str
    message_id: Optional[str] = None
    reference_task_ids: list[str] = field(default_factory=list)
    tenant: Optional[str] = None
    task_ids: set[str] = field(default_factory=set)
    context_ids: set[str] = field(default_factory=set)


class _ResponseObserver:
    def __init__(self, metadata: _OperationMetadata) -> None:
        self._metadata = metadata
        self._status_code: Optional[int] = None
        self._media_type = ""
        self._json_body = bytearray()
        self._sse_buffer = ""
        self._task_states: set[str] = set()
        self._error_type: Optional[str] = None

    def observe(self, message: MutableMapping[str, Any]) -> None:
        if message["type"] == "http.response.start":
            self._status_code = int(message.get("status", 0))
            for name, value in message.get("headers", []):
                if name.lower() == b"content-type":
                    self._media_type = value.decode("latin-1").lower()
                    break
            return

        if message["type"] != "http.response.body":
            return

        body = message.get("body", b"")
        if not body:
            return

        if self._media_type.startswith("text/event-stream"):
            self._observe_sse_chunk(body)
        elif len(self._json_body) < _MAX_JSON_RESPONSE_BYTES:
            remaining = _MAX_JSON_RESPONSE_BYTES - len(self._json_body)
            self._json_body.extend(body[:remaining])

    def finish(self, span: Span) -> None:
        if self._json_body:
            try:
                self._observe_payload(json.loads(self._json_body))
            except (UnicodeDecodeError, json.JSONDecodeError):
                pass

        if self._status_code is not None and self._status_code >= 400:
            self._error_type = str(self._status_code)

        all_task_ids = self._metadata.task_ids
        if len(all_task_ids) == 1:
            span.set_attribute(_ATTR_TASK_ID, next(iter(all_task_ids)))
        if len(self._task_states) == 1:
            span.set_attribute(_ATTR_TASK_STATE, next(iter(self._task_states)))
        if len(self._metadata.context_ids) == 1:
            span.set_attribute(
                _ATTR_CONVERSATION_ID,
                next(iter(self._metadata.context_ids)),
            )
        if self._error_type is not None:
            span.set_attribute(_ATTR_ERROR_TYPE, self._error_type)
            span.set_status(Status(StatusCode.ERROR))

    def record_exception(self, span: Span, error: BaseException) -> None:
        span.record_exception(error)
        span.set_attribute(_ATTR_ERROR_TYPE, type(error).__name__)
        span.set_status(Status(StatusCode.ERROR, str(error)))

    def _observe_sse_chunk(self, body: bytes) -> None:
        self._sse_buffer += body.decode("utf-8", errors="replace")
        while "\n\n" in self._sse_buffer or "\r\n\r\n" in self._sse_buffer:
            normalized = self._sse_buffer.replace("\r\n", "\n")
            event, separator, remainder = normalized.partition("\n\n")
            if not separator:
                return
            self._sse_buffer = remainder
            data = "\n".join(line[5:].lstrip() for line in event.splitlines() if line.startswith("data:"))
            if not data:
                continue
            try:
                self._observe_payload(json.loads(data))
            except json.JSONDecodeError:
                continue

    def _observe_payload(self, payload: object) -> None:
        if not isinstance(payload, dict):
            return

        error = payload.get("error")
        if isinstance(error, dict) and error.get("code") is not None:
            self._error_type = str(error["code"])

        result = payload.get("result")
        if isinstance(result, dict):
            self._collect_values(result)

    def _collect_values(self, value: object, parent_key: str = "") -> None:
        if isinstance(value, list):
            for item in value:
                self._collect_values(item, parent_key)
            return
        if not isinstance(value, dict):
            return

        context_id = value.get("contextId")
        if isinstance(context_id, str) and context_id:
            self._metadata.context_ids.add(context_id)

        task_id = value.get("taskId")
        if isinstance(task_id, str) and task_id:
            self._metadata.task_ids.add(task_id)

        identifier = value.get("id")
        if (
            isinstance(identifier, str)
            and identifier
            and (parent_key == "task" or isinstance(value.get("status"), dict))
        ):
            self._metadata.task_ids.add(identifier)

        status = value.get("status")
        if isinstance(status, dict):
            state = status.get("state")
            if isinstance(state, str) and state:
                self._task_states.add(state)

        for key, item in value.items():
            self._collect_values(item, key)


class _TracedResponse(Response):
    def __init__(
        self,
        response: Response,
        span: Span,
        context_token: Token[Context],
        observer: _ResponseObserver,
    ) -> None:
        super().__init__()
        self._response = response
        self._span = span
        self._context_token = context_token
        self._observer = observer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_with_observation(message: MutableMapping[str, Any]) -> None:
            self._observer.observe(message)
            await send(message)

        error: Optional[BaseException] = None
        try:
            await self._response(scope, receive, send_with_observation)
        except BaseException as exc:
            error = exc
            if not isinstance(exc, asyncio.CancelledError):
                self._observer.record_exception(self._span, exc)
            raise
        finally:
            if error is None:
                self._observer.finish(self._span)
            try:
                _otel_context.detach(self._context_token)
            finally:
                self._span.end()
                schedule_flush_spans()


def trace_jsonrpc_endpoint(
    endpoint: Callable[[Request], Awaitable[Response]],
    agent_card: AgentCard,
) -> Callable[[Request], Awaitable[Response]]:
    """Wrap a native A2A JSON-RPC endpoint with semantic operation tracing.

    :param endpoint: Native A2A JSON-RPC route endpoint.
    :type endpoint: Callable[[Request], Awaitable[Response]]
    :param agent_card: Agent Card metadata to attach to operation spans.
    :type agent_card: AgentCard
    :return: Endpoint that emits one semantic span per valid A2A operation.
    :rtype: Callable[[Request], Awaitable[Response]]
    """

    async def traced_endpoint(request: Request) -> Response:
        metadata = await _extract_request_metadata(request)
        if metadata is None:
            return await endpoint(request)

        attributes: dict[str, Any] = {
            _ATTR_METHOD: metadata.method,
            _ATTR_PROTOCOL_VERSION: metadata.protocol_version,
        }
        if agent_card.name:
            attributes[_ATTR_AGENT_NAME] = agent_card.name
        if agent_card.description:
            attributes[_ATTR_AGENT_DESCRIPTION] = agent_card.description
        if agent_card.version:
            attributes[_ATTR_AGENT_VERSION] = agent_card.version
        if metadata.message_id:
            attributes[_ATTR_MESSAGE_ID] = metadata.message_id
        if metadata.reference_task_ids:
            attributes[_ATTR_REFERENCE_TASK_IDS] = metadata.reference_task_ids
        if metadata.tenant:
            attributes[_ATTR_TENANT] = metadata.tenant

        server = request.scope.get("server")
        if server:
            attributes["server.address"] = server[0]
            if server[1] is not None:
                attributes["server.port"] = server[1]
        client = request.scope.get("client")
        if client:
            attributes["client.address"] = client[0]
            if client[1] is not None:
                attributes["client.port"] = client[1]

        tracer = _otel_trace.get_tracer(_INSTRUMENTATION_SCOPE, _A2A_VERSION)
        span = tracer.start_span(
            metadata.method,
            kind=SpanKind.SERVER,
            attributes=attributes,
        )
        operation_context = _otel_trace.set_span_in_context(span)
        if len(metadata.context_ids) == 1:
            operation_context = _otel_baggage.set_baggage(
                _BAGGAGE_CONVERSATION_ID,
                next(iter(metadata.context_ids)),
                context=operation_context,
            )
        context_token = _otel_context.attach(operation_context)
        observer = _ResponseObserver(metadata)

        try:
            response = await endpoint(request)
        except BaseException as exc:
            if not isinstance(exc, asyncio.CancelledError):
                observer.record_exception(span, exc)
            try:
                _otel_context.detach(context_token)
            finally:
                span.end()
                schedule_flush_spans()
            raise

        return _TracedResponse(response, span, context_token, observer)

    return traced_endpoint


async def _extract_request_metadata(request: Request) -> Optional[_OperationMetadata]:
    try:
        payload = json.loads(await request.body())
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("method"), str):
        return None

    method = payload["method"]
    params = payload.get("params")
    params = params if isinstance(params, dict) else {}
    message = params.get("message")
    message = message if isinstance(message, dict) else {}

    protocol_version = request.headers.get("A2A-Version") or request.query_params.get("a2a-version") or "1.0"
    metadata = _OperationMetadata(
        method=method,
        protocol_version=protocol_version,
        message_id=_nonempty_string(message.get("messageId")),
        reference_task_ids=(
            [value for value in message.get("referenceTaskIds", []) if isinstance(value, str) and value]
            if isinstance(message.get("referenceTaskIds"), list)
            else []
        ),
        tenant=_nonempty_string(params.get("tenant")),
    )

    context_id = _nonempty_string(message.get("contextId")) or _nonempty_string(params.get("contextId"))
    if context_id:
        metadata.context_ids.add(context_id)

    task_id = (
        _nonempty_string(message.get("taskId"))
        or _nonempty_string(params.get("taskId"))
        or (
            _nonempty_string(params.get("id"))
            if method
            in {
                "GetTask",
                "CancelTask",
                "SubscribeToTask",
            }
            else None
        )
    )
    if task_id:
        metadata.task_ids.add(task_id)
    return metadata


def _nonempty_string(value: object) -> Optional[str]:
    return value if isinstance(value, str) and value else None
