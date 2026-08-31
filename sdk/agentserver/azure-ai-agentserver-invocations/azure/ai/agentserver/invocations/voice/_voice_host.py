# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Typed event relay over the existing Invocations WebSocket transport."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import inspect
import logging
import os
import re
import time
import uuid
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any, NoReturn, TypeVar, cast
from urllib.parse import unquote_to_bytes

from opentelemetry import (
    baggage as _otel_baggage,
    context as _otel_context,
    trace as _otel_trace,
)
from opentelemetry.propagators.textmap import Getter
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from starlette.routing import Host, Match, Mount, Router, WebSocketRoute
from starlette.types import Receive, Scope, Send
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.core import (
    FoundryAgentRequestContext,
    configure_observability as _CORE_CONFIGURE_OBSERVABILITY,
    experimental,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import (  # pylint: disable=import-error,no-name-in-module
    FOUNDRY_CALL_ID,
    REQUEST_ID,
    SERVER_VERSION,
    USER_ID,
)
from azure.ai.agentserver.core._tracing import _BAGGAGE_SESSION_ID

from .._constants import InvocationsWSConstants, _classify_websocket_close_code
from .._invocation import InvocationAgentServerHost
from .._invocation_ws import _websocket_session_context
from . import _session as _session_transport
from ._codec import MAX_FRAME_BYTES, VoiceProtocolError, decode_inbound_message
from ._models import (
    BargeIn,
    InboundVoiceMessage,
    ResponseAccepted,
    ResponseCancelled,
    ResponseDropped,
    ResponseTimeout,
    SessionDisconnected,
    SessionEnd,
    SessionStart,
    UserMessage,
    UserNoInput,
    UserSpeechStarted,
)
from ._session import Session, SessionTermination
from ._tracing import (
    _SpanScope,
    _attach_context,
    _connection_outcome,
    _record_propagation_failure,
    _reset_context,
)

SessionStartCallback = Callable[[Session, SessionStart], Awaitable[None]]
UserMessageCallback = Callable[[Session, UserMessage], Awaitable[None]]
UserNoInputCallback = Callable[[Session, UserNoInput], Awaitable[None]]
UserSpeechStartedCallback = Callable[[Session, UserSpeechStarted], Awaitable[None]]
BargeInCallback = Callable[[Session, BargeIn], Awaitable[None]]
ResponseAcceptedCallback = Callable[[Session, ResponseAccepted], Awaitable[None]]
ResponseDroppedCallback = Callable[[Session, ResponseDropped], Awaitable[None]]
ResponseCancelledCallback = Callable[[Session, ResponseCancelled], Awaitable[None]]
ResponseTimeoutCallback = Callable[[Session, ResponseTimeout], Awaitable[None]]
SessionEndCallback = Callable[[Session, SessionEnd], Awaitable[None]]
DisconnectCallback = Callable[[Session, SessionDisconnected], Awaitable[None]]
ConnectionTerminatingCallback = Callable[[Session], None]

_CallbackT = TypeVar("_CallbackT", bound=Callable[..., Awaitable[None]])
_AwaitedT = TypeVar("_AwaitedT")
_VoiceCallback = Callable[[Session, Any], Awaitable[None]]


class _NoOpVoiceLogger:
    @staticmethod
    def debug(*_args: Any, **_kwargs: Any) -> None:
        return None

    @staticmethod
    def info(*_args: Any, **_kwargs: Any) -> None:
        return None

    @staticmethod
    def error(*_args: Any, **_kwargs: Any) -> None:
        return None


def _get_voice_logger() -> Any:
    try:
        return logging.getLogger("azure.ai.agentserver")
    except BaseException:  # pylint: disable=broad-exception-caught
        return _NoOpVoiceLogger()


def _get_voice_trace_propagator() -> Any:
    try:
        return TraceContextTextMapPropagator()
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _new_voice_context() -> Any:
    try:
        return _otel_context.Context()
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


logger = _get_voice_logger()
# Voice host and Session intentionally cooperate through package-private transport hooks.
# pylint: disable=protected-access
_VOICE_AUTHORITY_ROUTE = object()
_VOICE_CLOSE_CODE = _session_transport._VOICE_CLOSE_CODE_SCOPE_KEY  # pylint: disable=protected-access
_VOICE_DISCONNECT_EVENT = _session_transport._VOICE_DISCONNECT_EVENT_SCOPE_KEY  # pylint: disable=protected-access
_VOICE_TERMINATION_DEADLINE = "azure.ai.agentserver.invocations.voice.termination_deadline"
_VOICE_CONNECTION_TRACE = "azure.ai.agentserver.invocations.voice.connection_trace"
_VOICE_CONNECTION_CONTEXT = "azure.ai.agentserver.invocations.voice.connection_context"
_VOICE_PROPAGATION_HEADERS = "azure.ai.agentserver.invocations.voice.propagation_headers"
_VOICE_ROUTE_CONFLICT = "VoiceAgentServerHost cannot own /invocations_ws because the route is already registered"
_VOICE_TRACE_PROPAGATOR = _get_voice_trace_propagator()
_VOICE_BAGGAGE_KEYS = frozenset(
    {
        "azure.ai.agentserver.session_id",
        "microsoft.a365.agent.blueprint.id",
        "user.id",
        "gen_ai.agent.id",
        "microsoft.tenant.id",
    }
)
_VOICE_SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
_VOICE_OPAQUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]*$")
_VOICE_PROTOCOL_VERSION = re.compile(r"^[0-9]{1,3}(?:\.[0-9]{1,3}){1,2}$")
_TRACESTATE_KEY = r"[a-z][_0-9a-z\-*\/]{0,255}|" + r"[a-z0-9][_0-9a-z\-*\/]{0,240}@[a-z][_0-9a-z\-*\/]{0,13}"
_TRACESTATE_VALUE = r"[\x20-\x2b\x2d-\x3c\x3e-\x7e]{0,255}[\x21-\x2b\x2d-\x3c\x3e-\x7e]"
_TRACESTATE_MEMBER = re.compile(rf"({_TRACESTATE_KEY})=({_TRACESTATE_VALUE})[ \t]*")
_VALID_PERCENT_ESCAPE = re.compile(r"%(?:[0-9A-Fa-f]{2})")


def _configure_voice_observability(
    *,
    connection_string: str | None = None,
    log_level: str | None = None,
    enable_sensitive_data: bool = False,
) -> None:
    # AgentServerHost derives this callback argument from the same environment
    # variable, defaulting it to True when unset. Voice requires an explicit
    # environment opt-in for sensitive Agent Framework instrumentation, so
    # ignore the inherited value and resolve the variable with default False.
    del enable_sensitive_data
    configured = os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false")
    try:
        _CORE_CONFIGURE_OBSERVABILITY(
            connection_string=connection_string,
            log_level=log_level,
            enable_sensitive_data=configured.strip().lower() in {"1", "true"},
        )
    except ValueError:
        raise
    except BaseException:  # pylint: disable=broad-exception-caught
        pass


def _is_async_callable(callback: Callable[..., Any]) -> bool:
    for candidate in (callback, getattr(callback, "__call__", None)):
        if candidate is None:
            continue
        unwrapped = inspect.unwrap(candidate)
        if inspect.iscoroutinefunction(unwrapped) or inspect.isasyncgenfunction(unwrapped):
            return True
    return False


class _VoiceWebSocketRoute(WebSocketRoute):
    """Reserved Voice route that preserves matching Host and Mount authority."""

    def __init__(self, endpoint: Callable[..., Any], *, router: Router) -> None:
        super().__init__(InvocationsWSConstants.ROUTE_PATH, endpoint, name="invocations_ws")
        self._router = router

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        match, child_scope = super().matches(scope)
        if match is not Match.FULL:
            return match, child_scope
        for route in tuple(self._router.routes):
            if route is self or not isinstance(route, (Host, Mount)):
                continue
            authority_match, authority_scope = route.matches(scope)
            if authority_match is Match.FULL:
                selected_scope: dict[Any, Any] = dict(authority_scope)
                selected_scope[_VOICE_AUTHORITY_ROUTE] = route
                return Match.FULL, cast(Scope, selected_scope)
        return match, child_scope

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        authority_route = scope.pop(cast(Any, _VOICE_AUTHORITY_ROUTE), None)
        if isinstance(authority_route, (Host, Mount)):
            await authority_route.handle(scope, receive, send)
            return
        await super().handle(scope, receive, send)


class _VoiceHeaderGetter(Getter[list[tuple[bytes, bytes]]]):
    """Read raw Voice upgrade headers with W3C multi-value semantics."""

    def get(self, carrier: list[tuple[bytes, bytes]], key: str) -> list[str] | None:
        normalized_key = key.lower().encode("latin-1")
        values = [value.decode("latin-1") for name, value in carrier if name.lower() == normalized_key]
        if not values:
            return None
        if key.lower() == "traceparent":
            return values if len(values) == 1 else None
        if key.lower() in ("baggage", "tracestate"):
            return [",".join(values)]
        return values

    def keys(self, carrier: list[tuple[bytes, bytes]]) -> list[str]:
        return list(dict.fromkeys(name.decode("latin-1").lower() for name, _ in carrier))


_VOICE_HEADER_GETTER = _VoiceHeaderGetter()


def _is_valid_voice_correlation_id(key: str, value: str) -> bool:
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError:
        return False
    if key == "azure.ai.agentserver.session_id":
        return _VOICE_SESSION_ID.fullmatch(value) is not None
    return len(encoded) <= 256 and _VOICE_OPAQUE_ID.fullmatch(value) is not None


def _decode_voice_baggage_value(value: str) -> str | None:
    without_escapes = _VALID_PERCENT_ESCAPE.sub("", value)
    if "%" in without_escapes:
        return None
    try:
        return unquote_to_bytes(value).decode("utf-8", errors="strict")
    except (UnicodeDecodeError, ValueError):
        return None


def _copy_voice_baggage(raw_headers: list[tuple[bytes, bytes]], context: Any) -> tuple[Any, bool]:
    raw_values = [value.decode("latin-1") for name, value in raw_headers if name.lower() == b"baggage"]
    if not raw_values:
        return context, False
    header = ",".join(raw_values)
    if len(header.encode("latin-1")) > 8192:
        return context, True
    members = header.split(",")
    if len(members) > 180:
        return context, True
    approved_members: dict[str, list[str]] = {}
    invalid = False
    for member in members:
        candidate = member.strip()
        if "=" not in candidate:
            if candidate in _VOICE_BAGGAGE_KEYS:
                invalid = True
            continue
        key, encoded_value = candidate.split("=", 1)
        if key not in _VOICE_BAGGAGE_KEYS:
            continue
        approved_members.setdefault(key, []).append(encoded_value)

    for key, encoded_values in approved_members.items():
        if len(encoded_values) != 1:
            invalid = True
            continue
        encoded_value = encoded_values[0]
        if ";" in encoded_value:
            invalid = True
            continue
        value = _decode_voice_baggage_value(encoded_value)
        if value is not None and _is_valid_voice_correlation_id(key, value):
            context = _otel_baggage.set_baggage(key, value, context=context)
        else:
            invalid = True
    return context, invalid


def _has_valid_tracestate(raw_headers: list[tuple[bytes, bytes]]) -> bool:
    values = [value.decode("latin-1") for name, value in raw_headers if name.lower() == b"tracestate"]
    if not values:
        return True
    header = ",".join(values)
    if len(header.encode("latin-1")) > 512:
        return False
    members = re.split(r"[ \t]*,[ \t]*", header)
    if len(members) > 32:
        return False
    keys: set[str] = set()
    for member in members:
        if not member:
            return False
        match = _TRACESTATE_MEMBER.fullmatch(member)
        if match is None or match.group(1) in keys:
            return False
        keys.add(match.group(1))
    return True


def _extract_voice_websocket_context(websocket: WebSocket) -> Any:
    failure: str | None = None
    try:
        base_context = _new_voice_context()
        if base_context is None or _VOICE_TRACE_PROPAGATOR is None:
            _record_propagation_failure("extraction_error")
            return None
        raw_headers: list[tuple[bytes, bytes]] = websocket.scope.get(
            _VOICE_PROPAGATION_HEADERS,
            websocket.scope.get("headers", []),
        )
        traceparents = [value for name, value in raw_headers if name.lower() == b"traceparent"]
        if not traceparents:
            failure = "missing"
        elif len(traceparents) != 1:
            failure = "invalid"
        trace_headers = raw_headers
        valid_tracestate = _has_valid_tracestate(raw_headers)
        if not valid_tracestate:
            failure = "invalid"
            trace_headers = [(name, value) for name, value in raw_headers if name.lower() != b"tracestate"]
        context = _VOICE_TRACE_PROPAGATOR.extract(
            carrier=trace_headers,
            context=base_context,
            getter=_VOICE_HEADER_GETTER,
        )
        if context is None:
            _record_propagation_failure("extraction_error")
            return None
        if traceparents and not _otel_trace.get_current_span(context).get_span_context().is_valid:
            failure = "invalid"
        context, invalid_baggage = _copy_voice_baggage(raw_headers, context)
        if invalid_baggage:
            failure = "invalid"
        request_ids = _VOICE_HEADER_GETTER.get(raw_headers, REQUEST_ID) or []
        request_id = request_ids[0] if len(request_ids) == 1 else None
        if request_ids and (
            request_id is None or not request_id or not _is_valid_voice_correlation_id("x_request_id", request_id)
        ):
            failure = "invalid"
            request_id = None
        if request_id:
            context = _otel_baggage.set_baggage("x_request_id", request_id, context=context)
        if failure is not None:
            _record_propagation_failure(failure)
        return context
    except BaseException:  # pylint: disable=broad-exception-caught
        _record_propagation_failure("extraction_error")
        return None


def _selected_voice_close_code(websocket: WebSocket, default_code: int) -> int:
    scope = getattr(websocket, "scope", None)
    if not isinstance(scope, MutableMapping):
        return default_code
    selected = scope.get(_VOICE_CLOSE_CODE)
    return int(selected) if isinstance(selected, int) else default_code


def _select_voice_close_code(websocket: WebSocket, code: int) -> None:
    scope = getattr(websocket, "scope", None)
    if isinstance(scope, MutableMapping):
        scope.setdefault(_VOICE_CLOSE_CODE, code)


def _raise_voice_disconnect(websocket: WebSocket, code: int, reason: str) -> NoReturn:
    _select_voice_close_code(websocket, code)
    session = Session._current(websocket)  # pylint: disable=protected-access
    if session is not None:
        session._begin_termination(SessionTermination.PROTOCOL_ERROR)  # pylint: disable=protected-access
    raise WebSocketDisconnect(code=code, reason=reason)


def _raise_wrapped_cancellation(
    error: BaseException,
    cancellation_requests: int | None,
) -> None:
    _session_transport._raise_task_cancellation(error, cancellation_requests)  # pylint: disable=protected-access


def _task_cancellation_requests() -> int | None:
    return _session_transport._task_cancellation_requests()  # pylint: disable=protected-access


def _begin_voice_termination(
    websocket: WebSocket,
    session: Session,
    termination: SessionTermination | None = None,
) -> float:
    session._begin_termination(termination)  # pylint: disable=protected-access
    loop = asyncio.get_running_loop()
    scope = getattr(websocket, "scope", None)
    if isinstance(scope, MutableMapping):
        selected = scope.get(_VOICE_TERMINATION_DEADLINE)
        if isinstance(selected, (int, float)):
            return float(selected)
        deadline = loop.time() + _session_transport.CLOSE_TIMEOUT_SECONDS
        scope[_VOICE_TERMINATION_DEADLINE] = deadline
        return deadline
    return loop.time() + _session_transport.CLOSE_TIMEOUT_SECONDS


def _selected_voice_termination_deadline(websocket: WebSocket) -> float:
    scope = getattr(websocket, "scope", None)
    if isinstance(scope, MutableMapping):
        selected = scope.get(_VOICE_TERMINATION_DEADLINE)
        if isinstance(selected, (int, float)):
            return float(selected)
    return asyncio.get_running_loop().time() + _session_transport.CLOSE_TIMEOUT_SECONDS


def _commit_voice_session_termination(
    session: Session,
    *,
    handler_error: BaseException | None,
    disconnect_event: SessionDisconnected | None,
    close_code: int,
    accept_failed: bool,
) -> None:
    if session.termination is not None:
        return
    if accept_failed:
        termination = SessionTermination.ACCEPT_ERROR
    elif isinstance(handler_error, asyncio.CancelledError):
        termination = SessionTermination.CANCELLED
    elif handler_error is not None:
        termination = SessionTermination.INTERNAL_ERROR
    elif disconnect_event is not None:
        termination = SessionTermination(_classify_websocket_close_code(int(disconnect_event.code)))
    else:
        termination = SessionTermination(_classify_websocket_close_code(close_code))
    session._begin_termination(termination)


def _peek_voice_disconnect_event(websocket: WebSocket) -> SessionDisconnected | None:
    scope = getattr(websocket, "scope", None)
    if not isinstance(scope, MutableMapping):
        return None
    event = scope.get(_VOICE_DISCONNECT_EVENT)
    return event if isinstance(event, SessionDisconnected) else None


def _take_voice_disconnect_event(websocket: WebSocket) -> SessionDisconnected | None:
    scope = getattr(websocket, "scope", None)
    if not isinstance(scope, MutableMapping):
        return None
    event = scope.pop(_VOICE_DISCONNECT_EVENT, None)
    return event if isinstance(event, SessionDisconnected) else None


async def _raise_pending_cancellation() -> None:
    await asyncio.sleep(0)


async def _raise_pending_or_consumed_cancellation(
    cancellation_requests: int | None,
) -> None:
    await _raise_pending_cancellation()
    current_requests = _task_cancellation_requests()
    if cancellation_requests is not None and current_requests is not None and current_requests > cancellation_requests:
        raise asyncio.CancelledError()


async def _await_with_cancellation_guard(
    awaitable: Awaitable[_AwaitedT],
    *,
    on_success: Callable[[], object] | None = None,
) -> _AwaitedT:
    cancellation_requests = _task_cancellation_requests()
    result = await awaitable
    if on_success is not None:
        on_success()
    await _raise_pending_or_consumed_cancellation(cancellation_requests)
    return result


async def _receive_voice_transport_message(
    websocket: WebSocket,
) -> MutableMapping[str, Any]:
    message = await _session_transport._run_transport_operation(websocket.receive())  # pylint: disable=protected-access
    await _raise_pending_cancellation()
    return message


async def _receive_voice_event(
    websocket: WebSocket,
    session: Session,
) -> InboundVoiceMessage | None:
    try:
        raw_message = await _receive_voice_transport_message(websocket)
    except OSError as error:
        code = 1006
        _select_voice_close_code(websocket, code)
        session._begin_termination(SessionTermination.TRANSPORT_ERROR)  # pylint: disable=protected-access
        _begin_voice_termination(websocket, session)
        websocket.scope.setdefault(
            _VOICE_DISCONNECT_EVENT,
            SessionDisconnected(code=code),
        )
        raise WebSocketDisconnect(code=code) from error
    raw_type = raw_message.get("type")
    if raw_type == "websocket.disconnect":
        code = int(raw_message.get("code") or 1000)
        raw_reason = raw_message.get("reason")
        reason = raw_reason if isinstance(raw_reason, str) else None
        _select_voice_close_code(websocket, code)
        session._begin_termination(  # pylint: disable=protected-access
            SessionTermination(_classify_websocket_close_code(code))
        )
        _begin_voice_termination(websocket, session)
        websocket.scope.setdefault(
            _VOICE_DISCONNECT_EVENT,
            SessionDisconnected(code=code, reason=reason),
        )
        raise WebSocketDisconnect(code=code, reason=reason)
    if raw_type != "websocket.receive":
        _raise_voice_disconnect(websocket, 1002, "Invalid Voice WebSocket event")
    frame = raw_message.get("text")
    if frame is None:
        _raise_voice_disconnect(websocket, 1003, "Voice messages must be text frames")
    try:
        return decode_inbound_message(frame)
    except VoiceProtocolError as exc:
        try:
            _raise_voice_disconnect(websocket, exc.close_code, "Invalid Voice message")
        except WebSocketDisconnect as disconnect:
            raise disconnect from exc


@experimental
class VoiceAgentServerHost(InvocationAgentServerHost):
    """Invocations host with typed Voice event decorators.

    The host performs only per-frame decoding and static callback dispatch.
    Agent code owns IDs, application tasks, response lifecycle, terminal-event
    correlation, cancellation, history, and reconnect restoration.

    Default Voice observability enables sensitive Agent Framework
    instrumentation only when
    ``OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`` is explicitly set to
    ``true`` or ``1``. Pass a custom ``configure_observability`` callable in
    ``kwargs`` to use a different policy.

    :param openapi_spec: Optional OpenAPI document inherited from Invocations.
    :param asyncapi_spec_json: Optional AsyncAPI JSON document.
    :param asyncapi_spec_yaml: Optional AsyncAPI YAML document.
    :param kwargs: Remaining :class:`InvocationAgentServerHost` options.
    """

    def __init__(
        self,
        *,
        openapi_spec: dict[str, Any] | None = None,
        asyncapi_spec_json: dict[str, Any] | None = None,
        asyncapi_spec_yaml: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._voice_callbacks: dict[str, _VoiceCallback] = {}
        self._connection_terminating_callback: ConnectionTerminatingCallback | None = None
        self._voice_route: _VoiceWebSocketRoute | None = None
        if "configure_observability" not in kwargs:
            kwargs["configure_observability"] = _configure_voice_observability
        super().__init__(
            openapi_spec=openapi_spec,
            asyncapi_spec_json=asyncapi_spec_json,
            asyncapi_spec_yaml=asyncapi_spec_yaml,
            **kwargs,
        )
        super().ws_handler(self._handle_voice_connection)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            scope = dict(scope)
            raw_headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
            scope[_VOICE_PROPAGATION_HEADERS] = raw_headers
            propagation_headers = {
                b"baggage",
                b"traceparent",
                b"tracestate",
                REQUEST_ID.encode("ascii"),
            }
            scope["headers"] = [
                (name, value) for name, value in raw_headers if name.lower() not in propagation_headers
            ]
            self._ensure_ws_route_registered()
        await super().__call__(scope, receive, send)

    def _ensure_ws_route_registered(self) -> None:
        voice_route = self._voice_route
        if voice_route is None:
            voice_route = _VoiceWebSocketRoute(self._ws_endpoint, router=self.router)
            self._voice_route = voice_route
        routes = self.router.routes
        for route in routes:
            if (
                route is not voice_route
                and isinstance(route, WebSocketRoute)
                and getattr(route, "path", None) == InvocationsWSConstants.ROUTE_PATH
            ):
                raise RuntimeError(_VOICE_ROUTE_CONFLICT)
        if voice_route in routes:
            routes.remove(voice_route)
        routes.insert(0, voice_route)

    async def _ws_endpoint(self, websocket: WebSocket) -> None:
        session_id = self.config.session_id or str(uuid.uuid4())
        start_ns = time.monotonic_ns()
        parent_attachment = None
        connection_trace = _SpanScope()
        scope = getattr(websocket, "scope", None)
        try:
            extracted_context = _extract_voice_websocket_context(websocket)
            if extracted_context is not None and _is_valid_voice_correlation_id(
                "azure.ai.agentserver.session_id", session_id
            ):
                try:
                    extracted_context = _websocket_session_context(
                        session_id,
                        context=extracted_context,
                    )
                except BaseException:  # pylint: disable=broad-exception-caught
                    pass
            parent_attachment = _attach_context(extracted_context)
            if parent_attachment is not None:
                connection_attributes: dict[str, Any] = {"network.protocol.name": "websocket"}
                if _is_valid_voice_correlation_id("azure.ai.agentserver.session_id", session_id):
                    connection_attributes[InvocationsWSConstants.ATTR_SPAN_SESSION_ID] = session_id
                connection_trace = _SpanScope.start(
                    "agentserver.connection",
                    kind=_otel_trace.SpanKind.SERVER,
                    parent_context=extracted_context,
                    attributes=connection_attributes,
                )
            if isinstance(scope, MutableMapping):
                scope[_VOICE_CONNECTION_TRACE] = connection_trace
                scope[_VOICE_CONNECTION_CONTEXT] = connection_trace.context if connection_trace.is_active else None
            platform_token = set_request_context(
                FoundryAgentRequestContext(
                    call_id=websocket.headers.get(FOUNDRY_CALL_ID) or None,
                    user_id=websocket.headers.get(USER_ID) or None,
                    session_id=session_id,
                )
            )
            try:
                await self._run_voice_endpoint(websocket, session_id, start_ns, connection_trace)
            finally:
                platform_token.var.reset(platform_token)
        finally:
            if isinstance(scope, MutableMapping):
                scope.pop(_VOICE_CONNECTION_TRACE, None)
                scope.pop(_VOICE_CONNECTION_CONTEXT, None)
            if not connection_trace.is_completed:
                connection_trace.complete_connection("internal_error", InvocationsWSConstants.CLOSE_INTERNAL_ERROR)
            connection_trace.close()
            _reset_context(parent_attachment)

    async def _run_voice_endpoint(
        self,
        websocket: WebSocket,
        session_id: str,
        start_ns: int,
        connection_trace: _SpanScope,
    ) -> None:
        try:
            accept_error, voice_session, close_code, handler_exc, pending_error = (
                await self._run_voice_connection_context(
                    websocket,
                    session_id,
                )
            )
        except asyncio.CancelledError:
            self._emit_voice_close_event(
                session_id=session_id,
                start_ns=start_ns,
                close_code=InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
                error_code="cancelled",
                connection_trace=connection_trace,
                outcome="cancelled",
            )
            raise

        if accept_error is not None:
            if voice_session is not None:
                await self._complete_voice_endpoint(
                    websocket=websocket,
                    voice_session=voice_session,
                    session_id=session_id,
                    start_ns=start_ns,
                    close_code=close_code,
                    handler_exc=None,
                    pending_error=None,
                    error_code_override="accept_failed",
                    connection_trace=connection_trace,
                )
            self._report_voice_accept_failure(
                session_id,
                start_ns,
                emit_event=voice_session is None,
                connection_trace=connection_trace,
            )
            return

        if voice_session is None:
            raise RuntimeError("Voice WebSocket accepted without a Session")
        await self._complete_voice_endpoint(
            websocket=websocket,
            voice_session=voice_session,
            session_id=session_id,
            start_ns=start_ns,
            close_code=close_code,
            handler_exc=handler_exc,
            pending_error=pending_error,
            connection_trace=connection_trace,
        )

    async def _run_voice_connection_context(
        self,
        websocket: WebSocket,
        session_id: str,
    ) -> tuple[
        Exception | None,
        Session | None,
        int,
        BaseException | None,
        BaseException | None,
    ]:
        accept_error: Exception | None = None
        voice_session: Session | None = None
        close_code = InvocationsWSConstants.CLOSE_NORMAL
        handler_exc: BaseException | None = None
        pending_error: BaseException | None = None
        try:
            accept_error = await self._accept_voice_websocket(websocket)
            if accept_error is None:
                voice_session, close_code, handler_exc, pending_error = await self._run_accepted_voice_handler(
                    websocket,
                    session_id,
                )
            elif websocket.application_state == WebSocketState.CONNECTED:
                voice_session = Session._create(  # pylint: disable=protected-access
                    websocket,
                    connection_context=websocket.scope.get(_VOICE_CONNECTION_CONTEXT),
                )
                voice_session._begin_termination(SessionTermination.ACCEPT_ERROR)  # pylint: disable=protected-access
                _begin_voice_termination(websocket, voice_session)
                close_code = InvocationsWSConstants.CLOSE_INTERNAL_ERROR
        finally:
            if voice_session is not None:
                Session._release(websocket, voice_session)  # pylint: disable=protected-access
        return accept_error, voice_session, close_code, handler_exc, pending_error

    async def _accept_voice_websocket(
        self,
        websocket: WebSocket,
    ) -> Exception | None:
        try:
            await _session_transport._run_transport_operation(  # pylint: disable=protected-access
                websocket.accept(
                    headers=[
                        (
                            SERVER_VERSION.encode("latin-1"),
                            self._build_server_version().encode("latin-1"),  # pylint: disable=protected-access
                        )
                    ]
                )
            )
            await _raise_pending_cancellation()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return exc
        return None

    async def _run_accepted_voice_handler(
        self,
        websocket: WebSocket,
        session_id: str,
    ) -> tuple[Session, int, BaseException | None, BaseException | None]:
        voice_session = Session._create(  # pylint: disable=protected-access
            websocket,
            connection_context=websocket.scope.get(_VOICE_CONNECTION_CONTEXT),
        )
        close_code = InvocationsWSConstants.CLOSE_NORMAL
        handler_exc: BaseException | None = None
        pending_error: BaseException | None = None
        cancellation_requests = _task_cancellation_requests()
        try:
            close_code, handler_exc = await self._invoke_user_handler(websocket, session_id)
            await _raise_pending_cancellation()
            close_code = _selected_voice_close_code(websocket, close_code)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            if isinstance(exc, Exception):
                try:
                    _raise_wrapped_cancellation(exc, cancellation_requests)
                except asyncio.CancelledError as cancellation:
                    exc = cancellation
            close_code = _selected_voice_close_code(websocket, InvocationsWSConstants.CLOSE_INTERNAL_ERROR)
            handler_exc = exc
            pending_error = exc
        return voice_session, close_code, handler_exc, pending_error

    async def _complete_voice_endpoint(
        self,
        *,
        websocket: WebSocket,
        voice_session: Session,
        session_id: str,
        start_ns: int,
        close_code: int,
        handler_exc: BaseException | None,
        pending_error: BaseException | None,
        connection_trace: _SpanScope,
        error_code_override: str | None = None,
    ) -> None:
        deadline = _selected_voice_termination_deadline(websocket)
        cancellation = handler_exc if isinstance(handler_exc, asyncio.CancelledError) else None
        disconnect_event = _peek_voice_disconnect_event(websocket)
        close_attempt: asyncio.Task[None] | None = None
        close_error: Exception | None = None
        if error_code_override is not None:
            error_code = error_code_override
        elif handler_exc is None:
            error_code = None
        elif isinstance(handler_exc, asyncio.CancelledError):
            error_code = "cancelled"
        else:
            error_code = "internal_error"
        _commit_voice_session_termination(
            voice_session,
            handler_error=handler_exc,
            disconnect_event=disconnect_event,
            close_code=close_code,
            accept_failed=error_code_override == "accept_failed",
        )
        if cancellation is None and disconnect_event is None and close_code not in {1005, 1006, 1015}:
            reason = "Internal server error" if close_code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR else ""
            try:
                close_attempt = voice_session._start_close(close_code, reason)  # pylint: disable=protected-access
            except Exception as exc:  # pylint: disable=broad-exception-caught
                close_error = exc

        termination_error = self._notify_connection_terminating(voice_session)
        disconnect_error: BaseException | None = None
        try:
            await _raise_pending_cancellation()
            if close_attempt is not None:
                try:
                    await voice_session._wait_close(close_attempt, deadline)  # pylint: disable=protected-access
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    close_error = exc
            disconnect_event = _take_voice_disconnect_event(websocket)
            disconnect_error = await self._notify_peer_disconnect(
                websocket,
                voice_session,
                disconnect_event,
            )
            await _raise_pending_cancellation()
        except asyncio.CancelledError:
            error_code = "cancelled"
            raise
        finally:
            self._emit_voice_close_event(
                session_id=session_id,
                start_ns=start_ns,
                close_code=close_code,
                error_code=(
                    "internal_error" if termination_error is not None or disconnect_error is not None else error_code
                ),
                connection_trace=connection_trace,
                outcome=(voice_session.termination.value if voice_session.termination is not None else None),
            )

        if pending_error is not None:
            raise pending_error
        self._report_voice_endpoint_errors(
            handler_error=handler_exc if isinstance(handler_exc, Exception) else None,
            termination_error=termination_error,
            disconnect_error=disconnect_error,
            close_error=close_error,
        )

    @staticmethod
    def _report_voice_endpoint_errors(
        *,
        handler_error: Exception | None,
        termination_error: BaseException | None,
        disconnect_error: BaseException | None,
        close_error: Exception | None,
    ) -> None:
        if handler_error is not None:
            try:
                logger.error("Voice WebSocket handler failed")
            except BaseException:  # pylint: disable=broad-exception-caught
                pass
        if termination_error is not None:
            try:
                logger.error("Voice connection termination callback failed")
            except BaseException:  # pylint: disable=broad-exception-caught
                pass
        if disconnect_error is not None:
            try:
                logger.error("Voice disconnect callback failed")
            except BaseException:  # pylint: disable=broad-exception-caught
                pass
        if close_error is not None:
            try:
                logger.debug("Voice WebSocket close failed")
            except BaseException:  # pylint: disable=broad-exception-caught
                pass

    def _report_voice_accept_failure(
        self,
        session_id: str,
        start_ns: int,
        *,
        emit_event: bool,
        connection_trace: _SpanScope,
    ) -> None:
        if emit_event:
            self._emit_voice_close_event(
                session_id=session_id,
                start_ns=start_ns,
                close_code=InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
                error_code="accept_failed",
                connection_trace=connection_trace,
                outcome="accept_error",
            )
        try:
            logger.error("Voice WebSocket accept failed")
        except BaseException:  # pylint: disable=broad-exception-caught
            pass

    async def _invoke_traced_voice_callback(
        self,
        websocket: WebSocket,
        session: Session,
        event: InboundVoiceMessage,
        callback: _VoiceCallback,
    ) -> None:
        callback_trace = self._start_voice_callback_trace(websocket, event.type)
        cancellation_requests = _task_cancellation_requests()

        async def invoke_callback() -> None:
            try:
                await callback(session, event)
            except asyncio.CancelledError:
                raise
            except BaseException as exc:  # pylint: disable=broad-exception-caught
                _raise_wrapped_cancellation(exc, cancellation_requests)
                _begin_voice_termination(websocket, session, SessionTermination.CALLBACK_ERROR)
                raise

        try:
            await _await_with_cancellation_guard(
                invoke_callback(),
                on_success=(
                    (lambda: _begin_voice_termination(websocket, session, SessionTermination.COMPLETED))
                    if isinstance(event, SessionEnd)
                    else None
                ),
            )
        except asyncio.CancelledError:
            callback_trace.record_callback_error("cancelled")
            raise
        except BaseException:  # pylint: disable=broad-exception-caught
            if session.termination is SessionTermination.TRANSPORT_ERROR:
                error_type = "transport_error"
            elif session.termination is SessionTermination.CALLBACK_ERROR:
                error_type = "callback_error"
            else:
                error_type = "internal_error"
            callback_trace.record_callback_error(error_type)
            raise
        finally:
            callback_trace.close()

    @staticmethod
    def _start_voice_callback_trace(websocket: WebSocket, event_type: str) -> _SpanScope:
        connection_context = websocket.scope.get(_VOICE_CONNECTION_CONTEXT)
        if connection_context is None:
            return _SpanScope()
        return _SpanScope.start(
            "voice.callback",
            kind=_otel_trace.SpanKind.INTERNAL,
            parent_context=connection_context,
            attributes={"voice.event.type": event_type},
        )

    async def _invoke_user_handler(
        self,
        websocket: WebSocket,
        session_id: str,
    ) -> tuple[int, BaseException | None]:
        ws_fn = self._ws_fn
        if ws_fn is None:
            raise RuntimeError("_invoke_user_handler called with no registered ws_handler")
        cancellation_requests = _task_cancellation_requests()
        try:
            await ws_fn(websocket)
            return InvocationsWSConstants.CLOSE_NORMAL, None
        except WebSocketDisconnect as exc:
            _raise_wrapped_cancellation(exc, cancellation_requests)
            session = Session._current(websocket)  # pylint: disable=protected-access
            if (
                session is None
                or session.termination is SessionTermination.CALLBACK_ERROR
                or (session.termination is None and _peek_voice_disconnect_event(websocket) is None)
            ):
                return InvocationsWSConstants.CLOSE_INTERNAL_ERROR, exc
            return (int(exc.code) if exc.code else InvocationsWSConstants.CLOSE_NORMAL), None
        except Exception as exc:  # pylint: disable=broad-exception-caught
            _raise_wrapped_cancellation(exc, cancellation_requests)
            return InvocationsWSConstants.CLOSE_INTERNAL_ERROR, exc

    def _emit_voice_close_event(
        self,
        *,
        session_id: str,
        start_ns: int,
        close_code: int,
        error_code: str | None,
        connection_trace: _SpanScope,
        outcome: str | None = None,
    ) -> None:
        duration_ms = (time.monotonic_ns() - start_ns) // 1_000_000
        connection_trace.complete_connection(
            outcome or _connection_outcome(close_code, error_code),
            close_code,
        )
        try:
            self._emit_close_event(session_id, close_code, duration_ms, error_code=error_code)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass

    @staticmethod
    def _emit_close_event(
        session_id: str,
        close_code: int,
        duration_ms: int,
        *,
        error_code: str | None = None,
    ) -> None:
        extra: dict[str, Any] = {
            InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE: close_code,
            InvocationsWSConstants.ATTR_SPAN_DURATION_MS: duration_ms,
        }
        if _is_valid_voice_correlation_id("azure.ai.agentserver.session_id", session_id):
            extra[_BAGGAGE_SESSION_ID] = session_id
            extra[InvocationsWSConstants.ATTR_SPAN_SESSION_ID] = session_id
        if error_code is not None:
            extra[InvocationsWSConstants.ATTR_SPAN_ERROR_CODE] = error_code
        logger.info("Voice connection closed", extra=extra)

    def ws_handler(self, fn: Any) -> NoReturn:
        """Reject raw-handler registration on the typed Voice host.

        :param fn: Raw handler supplied by the caller.
        :type fn: Any
        :raises RuntimeError: Always; the typed host owns ``/invocations_ws``.
        """
        del fn
        raise RuntimeError("VoiceAgentServerHost owns /invocations_ws; use on_<event> decorators")

    def on_session_start(self, callback: SessionStartCallback) -> SessionStartCallback:
        """Register the ``session.start`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: SessionStartCallback
        :return: The callback, unchanged.
        :rtype: SessionStartCallback
        """
        return self._register_voice_callback(SessionStart.type, callback)

    def on_user_message(self, callback: UserMessageCallback) -> UserMessageCallback:
        """Register the ``user.message`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserMessageCallback
        :return: The callback, unchanged.
        :rtype: UserMessageCallback
        """
        return self._register_voice_callback(UserMessage.type, callback)

    def on_user_no_input(self, callback: UserNoInputCallback) -> UserNoInputCallback:
        """Register the ``user.no_input`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserNoInputCallback
        :return: The callback, unchanged.
        :rtype: UserNoInputCallback
        """
        return self._register_voice_callback(UserNoInput.type, callback)

    def on_user_speech_started(self, callback: UserSpeechStartedCallback) -> UserSpeechStartedCallback:
        """Register the ``user.speech_started`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: UserSpeechStartedCallback
        :return: The callback, unchanged.
        :rtype: UserSpeechStartedCallback
        """
        return self._register_voice_callback(UserSpeechStarted.type, callback)

    def on_barge_in(self, callback: BargeInCallback) -> BargeInCallback:
        """Register the ``barge_in`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: BargeInCallback
        :return: The callback, unchanged.
        :rtype: BargeInCallback
        """
        return self._register_voice_callback(BargeIn.type, callback)

    def on_response_accepted(self, callback: ResponseAcceptedCallback) -> ResponseAcceptedCallback:
        """Register the ``response.accepted`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseAcceptedCallback
        :return: The callback, unchanged.
        :rtype: ResponseAcceptedCallback
        """
        return self._register_voice_callback(ResponseAccepted.type, callback)

    def on_response_dropped(self, callback: ResponseDroppedCallback) -> ResponseDroppedCallback:
        """Register the ``response.dropped`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseDroppedCallback
        :return: The callback, unchanged.
        :rtype: ResponseDroppedCallback
        """
        return self._register_voice_callback(ResponseDropped.type, callback)

    def on_response_cancelled(self, callback: ResponseCancelledCallback) -> ResponseCancelledCallback:
        """Register the ``response.cancelled`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseCancelledCallback
        :return: The callback, unchanged.
        :rtype: ResponseCancelledCallback
        """
        return self._register_voice_callback(ResponseCancelled.type, callback)

    def on_response_timeout(self, callback: ResponseTimeoutCallback) -> ResponseTimeoutCallback:
        """Register the ``response.timeout`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: ResponseTimeoutCallback
        :return: The callback, unchanged.
        :rtype: ResponseTimeoutCallback
        """
        return self._register_voice_callback(ResponseTimeout.type, callback)

    def on_session_end(self, callback: SessionEndCallback) -> SessionEndCallback:
        """Register the ``session.end`` callback.

        :param callback: Async callback receiving the thin Session and event.
        :type callback: SessionEndCallback
        :return: The callback, unchanged.
        :rtype: SessionEndCallback
        """
        return self._register_voice_callback(SessionEnd.type, callback)

    def on_disconnect(self, callback: DisconnectCallback) -> DisconnectCallback:
        """Register the peer transport-disconnect callback.

        :param callback: Async callback receiving the thin Session and transport event.
        :type callback: DisconnectCallback
        :return: The callback, unchanged.
        :rtype: DisconnectCallback
        """
        return self._register_voice_callback("disconnect", callback)

    def on_connection_terminating(self, callback: ConnectionTerminatingCallback) -> ConnectionTerminatingCallback:
        """Register a synchronous signal that the connection handler is exiting.

        The host invokes the callback once whenever the connection handler
        unwinds in process. The callback must return promptly, be idempotent,
        and must not send frames. Applications can use it to synchronously
        cancel their connection-owned tasks or set their own stop signals. The
        SDK does not wait for those tasks to finish.

        :param callback: Synchronous callback receiving the thin Session.
        :type callback: ConnectionTerminatingCallback
        :return: The callback, unchanged.
        :rtype: ConnectionTerminatingCallback
        :raises TypeError: If the callback is async or cannot accept Session.
        :raises RuntimeError: If a callback is already registered.
        """
        try:
            is_async = _is_async_callable(callback)
        except ValueError as exc:
            raise TypeError("on_connection_terminating expects a synchronous function") from exc
        if is_async:
            raise TypeError("on_connection_terminating expects a synchronous function")
        try:
            inspect.signature(callback).bind(None)
        except TypeError as exc:
            raise TypeError("Connection terminating callback must accept Session") from exc
        if self._connection_terminating_callback is not None:
            raise RuntimeError("A callback is already registered for connection termination")
        self._connection_terminating_callback = callback
        return callback

    def _register_voice_callback(self, message_type: str, callback: _CallbackT) -> _CallbackT:
        if not inspect.iscoroutinefunction(callback):
            raise TypeError(f"on_{message_type.replace('.', '_')} expects an async function")
        try:
            inspect.signature(callback).bind(None, None)
        except TypeError as exc:
            raise TypeError("Voice callbacks must accept Session and event positional arguments") from exc
        if message_type in self._voice_callbacks:
            raise RuntimeError(f"A callback is already registered for {message_type}")
        self._voice_callbacks[message_type] = cast(_VoiceCallback, callback)
        return cast(_CallbackT, callback)

    def _notify_connection_terminating(self, session: Session) -> BaseException | None:
        terminating_callback = self._connection_terminating_callback
        if terminating_callback is None:
            return None
        try:
            result = terminating_callback(session)
            if result is not None:
                raise TypeError("Connection terminating callback must return None")
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            return exc
        return None

    async def _notify_peer_disconnect(
        self,
        websocket: WebSocket,
        session: Session,
        event: SessionDisconnected | None,
    ) -> BaseException | None:
        callback = self._voice_callbacks.get("disconnect")
        if callback is None or event is None:
            return None
        callback_trace = self._start_voice_callback_trace(websocket, "disconnect")
        cancellation_requests = _task_cancellation_requests()
        try:
            try:
                await callback(session, event)
            except asyncio.CancelledError as exc:
                callback_trace.record_callback_error("cancelled")
                current_requests = _task_cancellation_requests()
                if (
                    cancellation_requests is not None
                    and current_requests is not None
                    and current_requests > cancellation_requests
                ):
                    raise
                return exc
            except Exception as exc:  # pylint: disable=broad-exception-caught
                callback_trace.record_callback_error("callback_error")
                _raise_wrapped_cancellation(exc, cancellation_requests)
                return exc
            except BaseException as exc:  # pylint: disable=broad-exception-caught
                callback_trace.record_callback_error("callback_error")
                _raise_wrapped_cancellation(exc, cancellation_requests)
                return exc
            try:
                await _raise_pending_or_consumed_cancellation(cancellation_requests)
            except asyncio.CancelledError:
                callback_trace.record_callback_error("cancelled")
                raise
            return None
        finally:
            callback_trace.close()

    async def _handle_voice_connection(self, websocket: WebSocket) -> None:
        bound_session = Session._current(websocket)  # pylint: disable=protected-access
        session = bound_session or Session._create(websocket)  # pylint: disable=protected-access
        try:
            while True:
                event = await _receive_voice_event(websocket, session)
                if event is None:
                    continue
                if isinstance(event, SessionStart):
                    scope = getattr(websocket, "scope", None)
                    connection_trace = scope.get(_VOICE_CONNECTION_TRACE) if isinstance(scope, MutableMapping) else None
                    if isinstance(connection_trace, _SpanScope):
                        attributes: dict[str, Any] = {
                            "azure.ai.agentserver.invocations_ws.reconnect": event.reconnect,
                        }
                        if _VOICE_PROTOCOL_VERSION.fullmatch(event.protocol_version) is not None:
                            attributes["azure.ai.agentserver.invocations_ws.protocol_version"] = event.protocol_version
                        connection_trace.set_attributes(attributes)
                callback = self._voice_callbacks.get(event.type)
                if callback is not None:
                    await self._invoke_traced_voice_callback(
                        websocket,
                        session,
                        cast(InboundVoiceMessage, event),
                        callback,
                    )
                if isinstance(event, SessionEnd):
                    if callback is None:
                        _begin_voice_termination(websocket, session, SessionTermination.COMPLETED)
                    return
        finally:
            _begin_voice_termination(websocket, session)
            if bound_session is None:
                Session._release(websocket, session)  # pylint: disable=protected-access
                termination_error = self._notify_connection_terminating(session)
                disconnect_error = await self._notify_peer_disconnect(
                    websocket,
                    session,
                    _take_voice_disconnect_event(websocket),
                )
                if termination_error is not None:
                    try:
                        logger.error("Voice connection termination callback failed")
                    except BaseException:  # pylint: disable=broad-exception-caught
                        pass
                if disconnect_error is not None:
                    try:
                        logger.error("Voice disconnect callback failed")
                    except BaseException:  # pylint: disable=broad-exception-caught
                        pass

    def _build_hypercorn_config(self, host: str, port: int) -> object:
        """Create a Hypercorn config with the Voice frame admission limit.

        :param host: Network interface to bind.
        :type host: str
        :param port: Port to bind.
        :type port: int
        :return: Configured Hypercorn config.
        :rtype: hypercorn.config.Config
        """
        config = super()._build_hypercorn_config(host, port)
        setattr(config, "websocket_max_message_size", MAX_FRAME_BYTES)
        return config
