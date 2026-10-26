# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Request-level A2A tracing using Core's shared span lifecycle helpers."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import re
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from a2a.types import AgentCard
from opentelemetry import baggage, context, trace
from opentelemetry.trace import SpanKind, StatusCode
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message, Receive, Scope, Send

from azure.ai.agentserver.core import detach_context, end_span, schedule_flush_spans

from ._version import VERSION

_INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.A2A"
_BAGGAGE_CONVERSATION_ID = "azure.ai.agentserver.conversation_id"
_MAX_RESPONSE_BYTES = 1024 * 1024
_SSE_BOUNDARY = re.compile(rb"\r?\n\r?\n")


class _TracedResponse(Response):
    """Trace endpoint execution and response transmission under one lifecycle."""

    def __init__(
        self, endpoint: Callable[[Request], Awaitable[Response]], request: Request, attributes: dict[str, Any]
    ) -> None:
        super().__init__()
        self._endpoint, self._request, self._attributes = endpoint, request, attributes
        self._span: trace.Span = trace.INVALID_SPAN
        self._known = "a2a.task.id" in attributes
        self._buffer = b""
        self._discarding = False

    def observe_payload(self, payload: dict[str, Any]) -> None:
        if self._known or not isinstance(payload.get("result"), dict):
            return
        result = payload["result"]
        method = self._attributes["a2a.method.name"]
        if method in {"GetTask", "CancelTask"}:
            task_id = _nonempty_string(result.get("id"))
        elif method in {"SendMessage", "SendStreamingMessage", "SubscribeToTask"}:
            task_id = None
            for name in ("task", "message", "statusUpdate", "artifactUpdate"):
                value = result.get(name)
                if isinstance(value, dict):
                    task_id = _nonempty_string(value.get("id" if name == "task" else "taskId"))
                    if task_id:
                        break
        else:
            return
        if task_id:
            self._span.set_attribute("a2a.task.id", task_id)
            self._known = True

    def observe_chunk(self, body: bytes) -> None:
        if self._known:
            return
        self._buffer += body
        while boundary := _SSE_BOUNDARY.search(self._buffer):
            event, self._buffer = self._buffer[: boundary.start()], self._buffer[boundary.end() :]
            if not self._discarding and len(event) <= _MAX_RESPONSE_BYTES:
                data = b"\n".join(line[5:].lstrip(b" ") for line in event.splitlines() if line.startswith(b"data:"))
                self.observe_payload(_json_object(data))
            self._discarding = False
            if self._known:
                self._buffer = b""
                return
        if len(self._buffer) > _MAX_RESPONSE_BYTES:
            # Drop oversized events, retaining only enough bytes to recognize a split boundary.
            self._buffer, self._discarding = self._buffer[-3:], True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        attributes = self._attributes
        tracer = trace.get_tracer(_INSTRUMENTATION_SCOPE, VERSION)
        span = tracer.start_span(attributes["a2a.method.name"], kind=SpanKind.SERVER, attributes=attributes)
        self._span = span
        operation_context = trace.set_span_in_context(span)
        if "gen_ai.conversation.id" in attributes:
            operation_context = baggage.set_baggage(
                _BAGGAGE_CONVERSATION_ID, attributes["gen_ai.conversation.id"], context=operation_context
            )
        token = context.attach(operation_context)

        async def observe_send(message: Message) -> None:
            if message["type"] == "http.response.body":
                self.observe_chunk(message.get("body", b""))
            await send(message)

        error: Optional[BaseException] = None
        try:
            response = await self._endpoint(self._request)
            self._record_response(response)
            is_sse = response.headers.get("content-type", "").startswith("text/event-stream")
            await response(scope, receive, observe_send if is_sse and not self._known else send)
        except BaseException as exc:
            error = exc
            raise
        finally:
            detach_context(token)
            end_span(span, exc=None if isinstance(error, asyncio.CancelledError) else error)
            schedule_flush_spans()

    def _record_response(self, response: Response) -> None:
        error_type = None
        if response.status_code >= 400:
            error_type = str(response.status_code)
        else:
            # JSON-RPC may fail with HTTP 200. Inspect only a buffered unary body here.
            body = getattr(response, "body", None)
            if isinstance(body, bytes) and 0 < len(body) <= _MAX_RESPONSE_BYTES:
                payload = _json_object(body)
                self.observe_payload(payload)
                error = payload.get("error")
                if isinstance(error, dict) and error.get("code") is not None:
                    error_type = str(error["code"])
        if error_type is not None:
            self._span.set_attribute("error.type", error_type)
            self._span.set_status(StatusCode.ERROR)


def trace_jsonrpc_endpoint(
    endpoint: Callable[[Request], Awaitable[Response]],
    agent_card: AgentCard,
) -> Callable[[Request], Awaitable[Response]]:
    """Trace native A2A operations and correlate returned Task IDs.

    :param endpoint: Native A2A JSON-RPC route endpoint.
    :type endpoint: Callable[[Request], Awaitable[Response]]
    :param agent_card: Agent Card metadata to attach to operation spans.
    :type agent_card: AgentCard
    :return: Endpoint that emits one span per request with an A2A method.
    :rtype: Callable[[Request], Awaitable[Response]]
    """

    async def traced_endpoint(request: Request) -> Response:
        attributes = await _request_attributes(request)
        if attributes is None:
            return await endpoint(request)

        for name, value in (
            ("gen_ai.agent.name", agent_card.name),
            ("gen_ai.agent.description", agent_card.description),
            ("gen_ai.agent.version", agent_card.version),
        ):
            if value:
                attributes[name] = value

        for source in ("server", "client"):
            address = request.scope.get(source)
            if address:
                attributes[f"{source}.address"] = address[0]
                if address[1] is not None:
                    attributes[f"{source}.port"] = address[1]

        return _TracedResponse(endpoint, request, attributes)

    return traced_endpoint


async def _request_attributes(request: Request) -> Optional[dict[str, Any]]:
    payload = _json_object(await request.body())
    if not isinstance(payload.get("method"), str):
        return None

    method = payload["method"]
    params = payload.get("params")
    params = params if isinstance(params, dict) else {}
    message = params.get("message")
    message = message if isinstance(message, dict) else {}
    attributes: dict[str, Any] = {
        "a2a.method.name": method,
        "a2a.protocol.version": request.headers.get("A2A-Version") or request.query_params.get("a2a-version") or "1.0",
    }
    for name, value in (
        ("a2a.message.id", message.get("messageId")),
        ("a2a.tenant", params.get("tenant")),
        ("gen_ai.conversation.id", _nonempty_string(message.get("contextId")) or params.get("contextId")),
        (
            "a2a.task.id",
            _nonempty_string(message.get("taskId"))
            or _nonempty_string(params.get("taskId"))
            or (params.get("id") if method in {"GetTask", "CancelTask", "SubscribeToTask"} else None),
        ),
    ):
        if _nonempty_string(value):
            attributes[name] = value
    references = message.get("referenceTaskIds")
    if isinstance(references, list):
        references = [value for value in references if _nonempty_string(value)]
        if references:
            attributes["a2a.message.reference_task_ids"] = references
    return attributes


def _nonempty_string(value: object) -> Optional[str]:
    return value if isinstance(value, str) and value else None


def _json_object(body: bytes) -> dict[str, Any]:
    try:
        value = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}
