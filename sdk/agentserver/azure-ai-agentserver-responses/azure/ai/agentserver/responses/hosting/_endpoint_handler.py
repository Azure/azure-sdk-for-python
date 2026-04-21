# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
# pylint: disable=too-many-return-statements
"""HTTP endpoint handler for the Responses server.

This module owns all Starlette I/O: ``Request`` parsing, route-level
validation, header propagation, and ``Response`` construction.  Business
logic lives in :class:`_ResponseOrchestrator`.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import contextvars
import logging
import threading
from typing import TYPE_CHECKING, Any, cast

from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.core import (  # pylint: disable=import-error,no-name-in-module
    detach_context,
    end_span,
    flush_spans,
    set_current_span,
    trace_stream,
)
from azure.ai.agentserver.responses.models._generated import (
    AgentReference,
    CreateResponse,
    ResponseStreamEventType,
)

from .._id_generator import IdGenerator
from .._options import ResponsesServerOptions
from .._platform_headers import (
    CHAT_ISOLATION_KEY,
    CLIENT_HEADER_PREFIX,
    REQUEST_ID_ITEM_KEY,
    SESSION_ID,
    USER_ISOLATION_KEY,
)
from .._response_context import IsolationContext, ResponseContext
from ..models._helpers import get_input_expanded, to_output_item
from ..models.errors import RequestValidationError
from ..models.runtime import ResponseExecution, ResponseModeFlags, build_cancelled_response, build_failed_response
from ..store._base import ResponseProviderProtocol, ResponseStreamProviderProtocol
from ..store._foundry_errors import FoundryApiError, FoundryBadRequestError, FoundryResourceNotFoundError
from ..streaming._helpers import _encode_sse
from ..streaming._sse import encode_sse_any_event
from ..streaming._state_machine import _normalize_lifecycle_events
from ._execution_context import _ExecutionContext
from ._observability import (
    CreateSpan,
    _initial_create_span_tags,
    build_create_otel_attrs,
    build_create_span_tags,
    extract_request_id,
    start_create_span,
)
from ._orchestrator import _HandlerError, _refresh_background_status, _ResponseOrchestrator
from ._request_parsing import (
    _apply_item_cursors,
    _extract_item_id,
    _prevalidate_identity_payload,
    _resolve_conversation_id,
    _resolve_identity_fields,
    _resolve_session_id,
)
from ._runtime_state import _RuntimeState
from ._validation import (
    deleted_response as _deleted_response,
)
from ._validation import (
    error_response as _error_response,
)
from ._validation import (
    invalid_mode_response as _invalid_mode,
)
from ._validation import (
    invalid_parameters_response as _invalid_parameters,
)
from ._validation import (
    invalid_request_response as _invalid_request,
)
from ._validation import (
    not_found_response as _not_found,
)
from ._validation import parse_and_validate_create_response
from ._validation import (
    service_unavailable_response as _service_unavailable,
)

if TYPE_CHECKING:
    from ._routing import ResponsesAgentServerHost

logger = logging.getLogger("azure.ai.agentserver")

# OTel span attribute keys for error tagging (§7.2)
_ATTR_ERROR_CODE = "azure.ai.agentserver.responses.error.code"
_ATTR_ERROR_MESSAGE = "azure.ai.agentserver.responses.error.message"


def _classify_error_code(exc: BaseException) -> str:
    """Return an error code string for an exception, matching API error classification.

    :param exc: The exception to classify.
    :type exc: BaseException
    :return: An error code string.
    :rtype: str
    """
    if isinstance(exc, RequestValidationError):
        return exc.code
    if isinstance(exc, ValueError):
        return "invalid_request"
    return "internal_error"


def _extract_isolation(request: Request) -> IsolationContext:
    """Build an ``IsolationContext`` from platform-injected request headers.

    Returns the isolation keys from ``x-agent-user-isolation-key`` and
    ``x-agent-chat-isolation-key``.  Keys are ``None`` when the header
    is absent (e.g. local development) and empty string when sent
    with no value.

    :param request: The incoming Starlette HTTP request.
    :type request: Request
    :return: An isolation context with user and chat keys.
    :rtype: IsolationContext
    """
    return IsolationContext(
        user_key=request.headers.get(USER_ISOLATION_KEY),
        chat_key=request.headers.get(CHAT_ISOLATION_KEY),
    )


def _validate_response_id_format(
    response_id: str, headers: dict[str, str] | None = None, *, request_id: str | None = None
) -> Response | None:
    """Validate that a response_id path parameter has the expected ID format.

    Returns a 400 error response if the ID is malformed, or ``None`` if valid.
    The error shape follows spec rule B40: ``code: "invalid_parameters"``,
    ``param: "responseId{<value>}"``.

    :param response_id: The response ID from the URL path.
    :type response_id: str
    :param headers: Optional HTTP headers to include on the error response.
    :type headers: dict[str, str] | None
    :keyword request_id: Resolved ``x-request-id`` for error enrichment.
    :return: A 400 error response if invalid, or ``None`` if valid.
    :rtype: Response | None
    """
    is_valid, _ = IdGenerator.is_valid(response_id, allowed_prefixes=["caresp"])
    if not is_valid:
        return _invalid_parameters(
            "Malformed identifier.",
            headers or {},
            param=f"responseId{{{response_id}}}",
            request_id=request_id,
        )
    return None


def _get_scope_request_id(request: Request) -> str | None:
    """Extract the resolved ``x-request-id`` from the ASGI scope state.

    The value is set by :class:`~azure.ai.agentserver.core.RequestIdMiddleware`
    during request processing.  Returns ``None`` when the middleware is not
    installed or the value is absent.

    :param request: The Starlette HTTP request.
    :type request: Request
    :return: The resolved request ID, or ``None``.
    :rtype: str | None
    """
    state = request.scope.get("state")
    if isinstance(state, dict):
        return state.get(REQUEST_ID_ITEM_KEY)
    return None


# Structured log scope context variables (spec §7.4)
_response_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("ResponseId", default="")
_conversation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("ConversationId", default="")
_streaming_var: contextvars.ContextVar[str] = contextvars.ContextVar("Streaming", default="")


class _ResponseLogFilter(logging.Filter):
    """Attach response-scope IDs to every log record from context vars.

    Reads from ``contextvars`` rather than instance state, so a single
    filter instance can be installed once on the logger (not per-request).
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.response_id = _response_id_var.get("")  # type: ignore[attr-defined]
        record.conversation_id = _conversation_id_var.get("")  # type: ignore[attr-defined]
        record.streaming = _streaming_var.get("")  # type: ignore[attr-defined]
        return True


# Install once on first request — no per-request add/remove needed.
_log_filter_lock = threading.Lock()
_log_filter_installed = False


def _ensure_response_log_filter() -> None:
    """Install the response log filter on first use (lazy, thread-safe)."""
    global _log_filter_installed  # pylint: disable=global-statement
    if _log_filter_installed:
        return
    with _log_filter_lock:
        if _log_filter_installed:
            return
        logger.addFilter(_ResponseLogFilter())
        _log_filter_installed = True


_CANCEL_TERMINAL_ERRORS: dict[str, str] = {
    "completed": "Cannot cancel a completed response.",
    "failed": "Cannot cancel a failed response.",
    "incomplete": "Cannot cancel a response in terminal state.",
}


def _check_cancel_terminal_status(
    status: str | None,
    headers: dict[str, str],
) -> Response | None:
    """Return an error response if *status* is terminal, else ``None``.

    For ``"cancelled"`` the caller must handle the idempotent path itself
    (the caller decides between in-memory snapshot vs. persisted payload),
    so this helper returns a sentinel ``JSONResponse`` with status 200 and
    an empty body that the caller replaces.

    :param status: The response's current status string.
    :type status: str | None
    :param headers: Session headers to include on error responses.
    :type headers: dict[str, str]
    :return: An error response, 200 sentinel for *cancelled*, or ``None``.
    :rtype: Response | None
    """
    msg = _CANCEL_TERMINAL_ERRORS.get(status or "")
    if msg is not None:
        return _invalid_request(msg, headers, param="response_id")
    if status == "cancelled":
        # Sentinel — caller builds the idempotent 200 itself.
        return JSONResponse({}, status_code=200, headers=headers)
    return None


class _ResponseEndpointHandler:  # pylint: disable=too-many-instance-attributes
    """HTTP-layer handler for all Responses API endpoints.

    Owns all Starlette ``Request``/``Response`` concerns.  Delegates
    event-pipeline logic to :class:`_ResponseOrchestrator`.

    Mutable shutdown state (``_is_draining``, ``_shutdown_requested``) lives
    here so every route method shares consistent drain/cancel semantics without
    needing a ``nonlocal`` closure variable.
    """

    def __init__(
        self,
        *,
        orchestrator: _ResponseOrchestrator,
        runtime_state: _RuntimeState,
        runtime_options: ResponsesServerOptions,
        response_headers: dict[str, str],
        sse_headers: dict[str, str],
        host: "ResponsesAgentServerHost",
        provider: ResponseProviderProtocol,
        stream_provider: ResponseStreamProviderProtocol | None = None,
    ) -> None:
        """Initialise the endpoint handler.

        :param orchestrator: Event-pipeline orchestrator.
        :type orchestrator: _ResponseOrchestrator
        :param runtime_state: In-memory execution record store.
        :type runtime_state: _RuntimeState
        :param runtime_options: Server runtime options.
        :type runtime_options: ResponsesServerOptions
        :param response_headers: Headers to include on all responses.
        :type response_headers: dict[str, str]
        :param sse_headers: SSE-specific headers (e.g. connection, cache-control).
        :type sse_headers: dict[str, str]
        :param host: The ``ResponsesAgentServerHost`` instance (provides ``request_span``).
        :type host: ResponsesAgentServerHost
        :param provider: Persistence provider for response envelopes and input items.
        :type provider: ResponseProviderProtocol
        :param stream_provider: Optional provider for SSE stream event persistence and replay.
        :type stream_provider: ResponseStreamProviderProtocol | None
        """
        self._orchestrator = orchestrator
        self._runtime_state = runtime_state
        self._runtime_options = runtime_options
        self._response_headers = response_headers
        self._sse_headers = sse_headers
        self._host = host
        self._provider = provider
        self._stream_provider = stream_provider
        self._shutdown_requested: asyncio.Event = asyncio.Event()
        self._is_draining: bool = False

        # Validate the lifecycle event state machine on startup so
        # misconfigured state machines surface immediately.
        _normalize_lifecycle_events(
            response_id="resp_validation",
            events=[
                {"type": ResponseStreamEventType.RESPONSE_CREATED.value, "response": {"status": "in_progress"}},
                {"type": ResponseStreamEventType.RESPONSE_COMPLETED.value, "response": {"status": "completed"}},
            ],
        )

    # ------------------------------------------------------------------
    # Span attribute helper
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_set_attrs(span: Any, attrs: dict[str, str]) -> None:
        """Safely set attributes on an OTel span.

        :param span: The OTel span, or *None*.
        :type span: Any
        :param attrs: Key-value attributes to set.
        :type attrs: dict[str, str]
        """
        if span is None:
            return
        try:
            for key, value in attrs.items():
                span.set_attribute(key, value)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to set span attributes: %s", list(attrs.keys()), exc_info=True)

    # ------------------------------------------------------------------
    # §8: Session ID response header helper
    # ------------------------------------------------------------------

    def _session_headers(self, session_id: str | None = None) -> dict[str, str]:
        """Build response headers including ``x-agent-session-id``.

        Merges the base ``_response_headers`` with the session ID header.
        For POST /responses the caller passes the per-request resolved
        session ID; other endpoints use the ``FOUNDRY_AGENT_SESSION_ID``
        environment variable via the host config (resolved lazily so the
        value is available even when the handler is constructed before the
        base class ``__init__``).

        :param session_id: Per-request session ID (overrides env var).
        :type session_id: str | None
        :return: Headers dict with ``x-agent-session-id`` when available.
        :rtype: dict[str, str]
        """
        sid = session_id or (getattr(getattr(self._host, "config", None), "session_id", "") or "")
        headers = dict(self._response_headers)
        if sid:
            headers[SESSION_ID] = sid
        return headers

    # ------------------------------------------------------------------
    # Streaming response helpers
    # ------------------------------------------------------------------

    async def _monitor_disconnect(self, request: Request, cancellation_signal: asyncio.Event) -> None:
        """Poll for client disconnect and set cancellation signal.

        Used for non-background streaming requests so that handler
        cancellation is triggered when the client drops the connection
        (spec requirement B17).

        :param request: The Starlette request to monitor.
        :type request: Request
        :param cancellation_signal: Event to set when disconnect is detected.
        :type cancellation_signal: asyncio.Event
        """
        while not cancellation_signal.is_set():
            if await request.is_disconnected():
                cancellation_signal.set()
                return
            await asyncio.sleep(0.5)

    def _wrap_streaming_response(
        self,
        response: StreamingResponse,
        otel_span: Any,
    ) -> StreamingResponse:
        """Wrap a streaming response's body iterator with span lifecycle and context.

        Two layers of wrapping are applied:

        1. **Inner (tracing):** ``trace_stream`` wraps the body iterator so
           the OTel span covers the full streaming duration and is ended
           when iteration completes.
        2. **Outer (context):** A second async generator re-attaches the span
           as the current context for the duration of streaming, so that
           child spans created by user handler code (e.g. Agent Framework)
           are correctly parented under this span.

        :param response: The ``StreamingResponse`` to wrap.
        :type response: StreamingResponse
        :param otel_span: The OTel span (or *None* when tracing is disabled).
        :type otel_span: Any
        :return: The same response object, with its body_iterator replaced.
        :rtype: StreamingResponse
        """
        if otel_span is None:
            return response

        # Inner wrap: trace_stream ends the span when iteration completes.
        traced = trace_stream(response.body_iterator, otel_span)

        # Outer wrap: re-attach span as current context during streaming
        # so child spans are correctly parented.
        async def _iter_with_context():  # type: ignore[return]
            token = set_current_span(otel_span)
            try:
                async for chunk in traced:
                    yield chunk
            finally:
                detach_context(token)

        response.body_iterator = _iter_with_context()
        return response

    # ------------------------------------------------------------------
    # ResponseContext factory
    # ------------------------------------------------------------------

    def _build_execution_context(
        self,
        *,
        parsed: CreateResponse,
        response_id: str,
        agent_reference: AgentReference | dict[str, Any],
        agent_session_id: str | None = None,
        span: CreateSpan,
        request: Request,
    ) -> _ExecutionContext:
        """Build an :class:`_ExecutionContext` from the parsed request.

        Extracts all protocol fields from *parsed* exactly once and
        creates the cancellation signal.  The companion
        :class:`ResponseContext` is derived automatically so that both
        objects share a single source of truth for mode flags, input
        items, and conversation-threading fields.
        :keyword parsed: Validated :class:`CreateResponse` model.
        :paramtype parsed: CreateResponse
        :keyword response_id: Assigned response identifier.
        :paramtype response_id: str
        :keyword agent_reference: Normalised agent reference model or dictionary.
        :paramtype agent_reference: AgentReference | dict[str, Any]
        :keyword agent_session_id: Resolved session ID (B39), or ``None``.
        :paramtype agent_session_id: str | None
        :keyword span: Active observability span for this request.
        :paramtype span: CreateSpan
        :keyword request: Starlette HTTP request (for headers / query params).
        :paramtype request: Request
        :return: A fully-populated :class:`_ExecutionContext` with its
                    ``context`` field already set.
        :rtype: _ExecutionContext
        """
        stream = bool(getattr(parsed, "stream", False))
        store = True if getattr(parsed, "store", None) is None else bool(parsed.store)
        background = bool(getattr(parsed, "background", False))
        model = getattr(parsed, "model", None) or ""
        _expanded = get_input_expanded(parsed)
        input_items = [out for item in _expanded if (out := to_output_item(item, response_id)) is not None]
        previous_response_id: str | None = (
            parsed.previous_response_id
            if isinstance(parsed.previous_response_id, str) and parsed.previous_response_id
            else None
        )
        conversation_id = _resolve_conversation_id(parsed)

        cancellation_signal = asyncio.Event()
        if self._shutdown_requested.is_set():
            cancellation_signal.set()

        ctx = _ExecutionContext(
            response_id=response_id,
            agent_reference=agent_reference,
            model=model,
            store=store,
            background=background,
            stream=stream,
            input_items=input_items,
            previous_response_id=previous_response_id,
            conversation_id=conversation_id,
            cancellation_signal=cancellation_signal,
            agent_session_id=agent_session_id,
            span=span,
            parsed=parsed,
            user_isolation_key=request.headers.get(USER_ISOLATION_KEY),
            chat_isolation_key=request.headers.get(CHAT_ISOLATION_KEY),
        )

        # Derive the public ResponseContext from the execution context.
        ctx.context = self._create_response_context(ctx, request=request)
        return ctx

    def _create_response_context(
        self,
        ctx: _ExecutionContext,
        *,
        request: Request,
    ) -> ResponseContext:
        """Derive a :class:`ResponseContext` from an :class:`_ExecutionContext`.

        All protocol fields (mode flags, input items, conversation
        threading) are read from *ctx* so that values are extracted from
        the parsed request exactly once.

        :param ctx: The execution context that owns the protocol fields.
        :type ctx: _ExecutionContext
        :keyword request: The Starlette HTTP request.
        :paramtype request: Request
        :return: A fully-populated :class:`ResponseContext`.
        :rtype: ResponseContext
        """
        mode_flags = ResponseModeFlags(stream=ctx.stream, store=ctx.store, background=ctx.background)
        client_headers = {
            k.lower(): v for k, v in request.headers.items() if k.lower().startswith(CLIENT_HEADER_PREFIX)
        }

        context = ResponseContext(
            response_id=ctx.response_id,
            mode_flags=mode_flags,
            request=ctx.parsed,
            provider=self._provider,
            input_items=ctx.input_items,
            previous_response_id=ctx.previous_response_id,
            conversation_id=ctx.conversation_id,
            history_limit=self._runtime_options.default_fetch_history_count,
            client_headers=client_headers,
            query_parameters=dict(request.query_params),
            isolation=IsolationContext(
                user_key=ctx.user_isolation_key,
                chat_key=ctx.chat_isolation_key,
            ),
            prefetched_history_ids=ctx.prefetched_history_ids,
        )
        context.is_shutdown_requested = self._shutdown_requested.is_set()
        return context

    async def _prefetch_history_ids(
        self,
        ctx: _ExecutionContext,
        *,
        span: "CreateSpan",
        agent_session_id: str | None,
    ) -> Response | None:
        """Eagerly validate conversation references and prefetch history IDs.

        Calls ``provider.get_history_item_ids()`` when the request carries
        ``previous_response_id`` or ``conversation_id``.  A nonexistent
        reference surfaces as a client-facing error *before* the handler is
        invoked.  On success the fetched IDs are cached on *ctx* and its
        ``ResponseContext`` so that ``get_history()`` skips the redundant
        provider call.

        :param ctx: The execution context for the current request.
        :type ctx: _ExecutionContext
        :keyword span: Active observability span.
        :paramtype span: CreateSpan
        :keyword agent_session_id: Resolved session ID for response headers.
        :paramtype agent_session_id: str | None
        :return: An error ``Response`` when validation fails, or ``None`` on success.
        :rtype: Response | None
        """
        if self._provider is None or (not ctx.previous_response_id and not ctx.conversation_id):
            return None

        _hdrs = self._session_headers(agent_session_id)
        try:
            _isolation = ctx.context.isolation if ctx.context else None
            prefetched = await self._provider.get_history_item_ids(
                ctx.previous_response_id,
                ctx.conversation_id,
                self._runtime_options.default_fetch_history_count,
                isolation=_isolation,
            )
            ctx.prefetched_history_ids = prefetched
            if ctx.context is not None:
                ctx.context._prefetched_history_ids = prefetched  # pylint: disable=protected-access
            return None
        except FoundryResourceNotFoundError as exc:
            span.end(exc)
            if exc.response_body is not None:
                return JSONResponse(exc.response_body, status_code=404, headers=_hdrs)
            return _not_found(str(ctx.previous_response_id or ctx.conversation_id), _hdrs)
        except FoundryBadRequestError as exc:
            span.end(exc)
            if exc.response_body is not None:
                return JSONResponse(exc.response_body, status_code=400, headers=_hdrs)
            return _invalid_request(str(exc), _hdrs)
        except FoundryApiError as exc:
            span.end(exc)
            if exc.response_body is not None:
                return JSONResponse(exc.response_body, status_code=500, headers=_hdrs)
            return _error_response(exc, _hdrs)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "Failed to validate conversation references for response %s",
                ctx.response_id,
                exc_info=exc,
            )
            span.end(exc)
            return _error_response(exc, _hdrs)

    # ------------------------------------------------------------------
    # Route handlers
    # ------------------------------------------------------------------

    async def handle_create(self, request: Request) -> Response:  # pylint: disable=too-many-locals,too-many-statements
        """Route handler for ``POST /responses``.

        Parses and validates the create request, builds an
        :class:`_ExecutionContext`, then dispatches to the appropriate
        orchestrator method (stream / sync / background).

        :param request: Incoming Starlette request.
        :type request: Request
        :return: HTTP response for the create operation.
        :rtype: Response
        """
        if self._is_draining:
            return _service_unavailable("Server is shutting down.", self._session_headers())

        # Also maintain CreateSpanHook for backward compat (tests etc.)
        span = start_create_span(
            "create_response",
            _initial_create_span_tags(),
            hook=self._runtime_options.create_span_hook,
        )
        captured_error: Exception | None = None
        scope_request_id = _get_scope_request_id(request)

        try:
            payload = await request.json()
            _prevalidate_identity_payload(payload)
            parsed = parse_and_validate_create_response(payload, options=self._runtime_options)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Failed to parse/validate create request", exc_info=exc)
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, self._session_headers(), request_id=scope_request_id)

        try:
            response_id, agent_reference = _resolve_identity_fields(
                parsed,
                request_headers=request.headers,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Failed to resolve identity fields", exc_info=exc)
            captured_error = exc
            span.end(captured_error)
            return _error_response(exc, self._session_headers(), request_id=scope_request_id)

        # B39: Resolve session ID
        config_session_id = getattr(getattr(self._host, "config", None), "session_id", "") or ""
        agent_session_id = _resolve_session_id(
            parsed, payload, env_session_id=config_session_id, agent_reference=agent_reference
        )

        ctx = self._build_execution_context(
            parsed=parsed,
            response_id=response_id,
            agent_reference=agent_reference,
            agent_session_id=agent_session_id,
            span=span,
            request=request,
        )

        logger.info(
            "Creating response %s: streaming=%s background=%s store=%s model=%s "
            "conversation_id=%s previous_response_id=%s "
            "has_user_isolation_key=%s has_chat_isolation_key=%s",
            ctx.response_id,
            ctx.stream,
            ctx.background,
            ctx.store,
            ctx.model,
            ctx.conversation_id,
            ctx.previous_response_id,
            ctx.user_isolation_key is not None,
            ctx.chat_isolation_key is not None,
        )

        # Eagerly validate conversation references before the handler runs.
        prefetch_error = await self._prefetch_history_ids(ctx, span=span, agent_session_id=agent_session_id)
        if prefetch_error is not None:
            return prefetch_error

        # Extract X-Request-Id header for request ID propagation (truncated to 256 chars).
        request_id = extract_request_id(request.headers)
        _project_id = getattr(getattr(self._host, "config", None), "project_id", "") or ""

        span.set_tags(build_create_span_tags(ctx, request_id=request_id, project_id=_project_id))

        # Start OTel request span using host's request_span context manager.
        with self._host.request_span(
            request.headers,
            response_id,
            "invoke_agent",
            operation_name="invoke_agent",
            session_id=agent_session_id or "",
            end_on_exit=False,
        ) as otel_span:
            self._safe_set_attrs(otel_span, build_create_otel_attrs(ctx, request_id=request_id, project_id=_project_id))

            # Set W3C baggage per spec §7.3
            bag_ctx = _otel_context.get_current()
            bag_ctx = _otel_baggage.set_baggage("azure.ai.agentserver.response_id", response_id, context=bag_ctx)
            bag_ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.conversation_id", ctx.conversation_id or "", context=bag_ctx
            )
            bag_ctx = _otel_baggage.set_baggage("azure.ai.agentserver.streaming", str(ctx.stream), context=bag_ctx)
            if request_id:
                bag_ctx = _otel_baggage.set_baggage("azure.ai.agentserver.x-request-id", request_id, context=bag_ctx)
            baggage_token = _otel_context.attach(bag_ctx)

            # Set structured log scope per spec §7.4
            _ensure_response_log_filter()
            rid_token = _response_id_var.set(response_id)
            cid_token = _conversation_id_var.set(ctx.conversation_id or "")
            str_token = _streaming_var.set(str(ctx.stream).lower())

            disconnect_task: asyncio.Task[None] | None = None
            try:
                if ctx.stream:
                    body_iter = self._orchestrator.run_stream(ctx)

                    # B17: monitor client disconnect for non-background streams
                    if not ctx.background:
                        disconnect_task = asyncio.create_task(
                            self._monitor_disconnect(request, ctx.cancellation_signal)
                        )
                        raw_iter = body_iter

                        async def _iter_with_cleanup():  # type: ignore[return]
                            try:
                                async for chunk in raw_iter:
                                    yield chunk
                            finally:
                                if disconnect_task and not disconnect_task.done():
                                    disconnect_task.cancel()

                        body_iter = _iter_with_cleanup()

                    sse_response = StreamingResponse(
                        body_iter,
                        media_type="text/event-stream",
                        headers={**self._sse_headers, **self._session_headers(agent_session_id)},
                    )
                    wrapped = self._wrap_streaming_response(sse_response, otel_span)
                    return wrapped

                if not ctx.background:
                    disconnect_task = asyncio.create_task(self._monitor_disconnect(request, ctx.cancellation_signal))
                    try:
                        snapshot = await self._orchestrator.run_sync(ctx)
                        logger.info(
                            "Response %s completed: status=%s output_count=%d",
                            ctx.response_id,
                            snapshot.get("status"),
                            len(snapshot.get("output", [])),
                        )
                        end_span(otel_span)
                        return JSONResponse(snapshot, status_code=200, headers=self._session_headers(agent_session_id))
                    except _HandlerError as exc:
                        logger.error(
                            "Handler error in sync create (response_id=%s)",
                            ctx.response_id,
                            exc_info=exc.original,
                        )
                        self._safe_set_attrs(
                            otel_span,
                            {
                                _ATTR_ERROR_CODE: _classify_error_code(exc.original),
                                _ATTR_ERROR_MESSAGE: str(exc.original),
                            },
                        )
                        end_span(otel_span, exc=exc.original)
                        # Handler errors are server-side faults, not client errors
                        err_body = {
                            "error": {
                                "message": "internal server error",
                                "type": "server_error",
                                "code": "server_error",
                                "param": None,
                            }
                        }
                        return JSONResponse(err_body, status_code=500, headers=self._session_headers(agent_session_id))
                    finally:
                        disconnect_task.cancel()

                snapshot = await self._orchestrator.run_background(ctx)
                logger.info(
                    "Background response created for %s: status=%s",
                    ctx.response_id,
                    snapshot.get("status"),
                )
                end_span(otel_span)
                return JSONResponse(snapshot, status_code=200, headers=self._session_headers(agent_session_id))
            except _HandlerError as exc:
                logger.error("Handler error in create (response_id=%s)", ctx.response_id, exc_info=exc.original)
                self._safe_set_attrs(
                    otel_span,
                    {
                        _ATTR_ERROR_CODE: _classify_error_code(exc.original),
                        _ATTR_ERROR_MESSAGE: str(exc.original),
                    },
                )
                end_span(otel_span, exc=exc)
                # Handler errors are server-side faults, not client errors
                err_body = {
                    "error": {
                        "message": "internal server error",
                        "type": "server_error",
                        "code": "server_error",
                        "param": None,
                    }
                }
                return JSONResponse(
                    err_body,
                    status_code=500,
                    headers=self._session_headers(agent_session_id),
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                logger.error("Unexpected error in create (response_id=%s)", ctx.response_id, exc_info=exc)
                self._safe_set_attrs(
                    otel_span,
                    {
                        _ATTR_ERROR_CODE: _classify_error_code(exc),
                        _ATTR_ERROR_MESSAGE: str(exc),
                    },
                )
                end_span(otel_span, exc=exc)
                raise
            finally:
                _response_id_var.reset(rid_token)
                _conversation_id_var.reset(cid_token)
                _streaming_var.reset(str_token)
                # Flush pending spans before the response is sent.
                # BatchSpanProcessor exports on a timer; in hosted sandboxes
                # the platform may freeze the process after the HTTP response,
                # losing any buffered spans (e.g. LangGraph per-node spans).
                flush_spans()
                try:
                    _otel_context.detach(baggage_token)
                except ValueError:
                    pass

    async def handle_get(self, request: Request) -> Response:  # pylint: disable=too-many-branches
        """Route handler for ``GET /responses/{response_id}``.

        Returns the response snapshot or replays SSE events if
        ``stream=true`` is in the query parameters.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: JSON snapshot or SSE replay streaming response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        _hdrs = self._session_headers()
        format_error = _validate_response_id_format(response_id, _hdrs)
        if format_error is not None:
            return format_error

        stream_replay_param = request.query_params.get("stream", "false").lower() == "true"
        _isolation = _extract_isolation(request)
        if stream_replay_param:
            logger.info(
                "Getting response %s with SSE replay, has_user_isolation_key=%s has_chat_isolation_key=%s",
                response_id,
                _isolation.user_key is not None,
                _isolation.chat_key is not None,
            )
        else:
            logger.info(
                "Getting response %s, has_user_isolation_key=%s has_chat_isolation_key=%s",
                response_id,
                _isolation.user_key is not None,
                _isolation.chat_key is not None,
            )
        record = await self._runtime_state.get(response_id)
        if record is None:
            return await self._handle_get_fallback(
                request,
                response_id,
                stream_replay_param,
                _isolation,
                _hdrs,
            )

        # Chat isolation enforcement on in-flight response
        if not _RuntimeState.check_chat_isolation(record.chat_isolation_key, _isolation.chat_key):
            return _not_found(response_id, _hdrs)

        _refresh_background_status(record)

        if stream_replay_param:
            return self._handle_get_stream(request, record, _hdrs)

        if not record.visible_via_get:
            return _not_found(response_id, _hdrs)

        snapshot = _RuntimeState.to_snapshot(record)
        logger.info(
            "Retrieved response %s: status=%s output_count=%d",
            response_id,
            snapshot.get("status"),
            len(snapshot.get("output", [])),
        )
        return JSONResponse(snapshot, status_code=200, headers=_hdrs)

    def _handle_get_stream(
        self,
        request: Request,
        record: ResponseExecution,
        _hdrs: dict[str, str],
    ) -> Response:
        """Handle the ``stream=true`` path for an in-flight response.

        :param request: Incoming Starlette request.
        :type request: Request
        :param record: The in-flight execution record.
        :type record: ResponseExecution
        :param _hdrs: Session headers to include on the response.
        :type _hdrs: dict[str, str]
        :return: SSE streaming response or error.
        :rtype: Response
        """
        response_id = record.response_id
        # B14: store=false responses are never persisted — return 404.
        if not record.mode_flags.store:
            return _not_found(response_id, _hdrs)
        if not record.replay_enabled:
            if not record.mode_flags.background:
                return _invalid_mode(
                    "This response cannot be streamed because it was not created with background=true.",
                    _hdrs,
                    param="stream",
                )
            return _invalid_mode(
                "This response cannot be streamed because it was not created with stream=true.",
                _hdrs,
                param="stream",
            )

        parsed_cursor = self._parse_starting_after(request, _hdrs)
        if isinstance(parsed_cursor, Response):
            return parsed_cursor

        return self._build_live_stream_response(record, parsed_cursor, _hdrs)

    async def _handle_get_fallback(  # pylint: disable=too-many-return-statements
        self,
        request: Request,
        response_id: str,
        stream_replay: bool,
        _isolation: "IsolationContext",
        _hdrs: dict[str, str],
    ) -> Response:
        """Provider fallback for GET when the record is not in runtime state.

        Handles both JSON snapshot and SSE replay paths when the response
        has been evicted from memory or the server has restarted.

        :param request: Incoming Starlette request.
        :type request: Request
        :param response_id: The response ID to retrieve.
        :type response_id: str
        :param stream_replay: Whether the client requested SSE replay.
        :type stream_replay: bool
        :param _isolation: Isolation context from the request.
        :type _isolation: IsolationContext
        :param _hdrs: Session headers to include on the response.
        :type _hdrs: dict[str, str]
        :return: Response.
        :rtype: Response
        """
        if await self._runtime_state.is_deleted(response_id):
            return _deleted_response(response_id, _hdrs)

        if not stream_replay:
            # Provider fallback: serve completed responses that are no longer in runtime state
            # (e.g., after a process restart).
            try:
                response_obj = await self._provider.get_response(response_id, isolation=_isolation)
                snapshot = response_obj.as_dict()
                logger.info(
                    "Retrieved response %s: status=%s output_count=%d",
                    response_id,
                    snapshot.get("status"),
                    len(snapshot.get("output", [])),
                )
                return JSONResponse(snapshot, status_code=200, headers=_hdrs)
            except FoundryResourceNotFoundError:
                pass  # Fall through to 404 below
            except FoundryBadRequestError as exc:
                return _invalid_request(str(exc), _hdrs, param="response_id")
            except FoundryApiError as exc:
                logger.error("Storage API error for GET response_id=%s: %s", response_id, exc, exc_info=True)
                return _error_response(exc, _hdrs)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Provider fallback failed for GET response_id=%s", response_id, exc_info=True)
        else:
            # Validate starting_after cursor early — invalid cursors must
            # always get param=starting_after regardless of stream availability.
            parsed_cursor = self._parse_starting_after(request, _hdrs)
            if isinstance(parsed_cursor, Response):
                return parsed_cursor

            # Stream provider fallback: replay persisted SSE events when runtime state is gone.
            replay_response = await self._try_replay_persisted_stream(
                request,
                response_id,
                isolation=_isolation,
                headers=_hdrs,
            )
            if replay_response is not None:
                return replay_response

            # No stream events available.  Check the persisted response's
            # background flag; if not bg, give the clear non-bg error.
            # Otherwise, we can't distinguish bg+non-stream from
            # bg+stream-with-expired-TTL (we don't persist the stream flag),
            # so use a combined message.
            try:
                persisted = await self._provider.get_response(response_id, isolation=_isolation)
                persisted_dict = persisted.as_dict()
                # B2: SSE replay requires background mode.
                if persisted_dict.get("background") is not True:
                    return _invalid_mode(
                        "This response cannot be streamed because it was not created with background=true.",
                        _hdrs,
                        param="stream",
                    )
                # TODO: The container spec prescribes distinct error messages for
                # "not created with stream=true" vs "stream TTL expired", but after
                # eager eviction the persisted response does not carry the stream
                # mode flag — we cannot distinguish the two cases.  Until the
                # provider surfaces the reason, we use a combined message.
                return _invalid_mode(
                    "This response cannot be streamed because it was not created "
                    "with stream=true or the stream TTL has expired.",
                    _hdrs,
                    param="stream",
                )
            except FoundryResourceNotFoundError:
                pass  # Response doesn't exist in provider either — fall through to 404
            except FoundryBadRequestError as exc:
                return _invalid_request(str(exc), _hdrs, param="response_id")
            except FoundryApiError as exc:
                logger.error(
                    "Storage API error for GET SSE replay response_id=%s: %s",
                    response_id,
                    exc,
                    exc_info=True,
                )
                return _error_response(exc, _hdrs)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # Response doesn't exist in provider either — fall through to 404

        return _not_found(response_id, _hdrs)

    @staticmethod
    def _parse_starting_after(request: Request, headers: dict[str, str] | None = None) -> int | Response:
        """Parse the ``starting_after`` query parameter.

        Returns the integer cursor value (defaulting to ``-1``) or an
        error :class:`Response` when the value is not a valid integer.

        :param request: The incoming Starlette HTTP request.
        :type request: Request
        :param headers: Optional response headers to include on error responses.
        :type headers: dict[str, str] | None
        :return: The parsed cursor value or an error response.
        :rtype: int | Response
        """
        cursor_raw = request.query_params.get("starting_after")
        if cursor_raw is None:
            return -1
        try:
            return int(cursor_raw)
        except ValueError:
            return _invalid_request(
                "starting_after must be an integer",
                headers or {},
                param="starting_after",
            )

    def _build_live_stream_response(
        self,
        record: ResponseExecution,
        starting_after: int,
        headers: dict[str, str] | None = None,
    ) -> StreamingResponse:
        """Build a live SSE subscription response for an in-flight record.

        :param record: The in-flight response execution record.
        :type record: ResponseExecution
        :param starting_after: The cursor position to start streaming from.
        :type starting_after: int
        :param headers: Optional extra headers (e.g. session headers) to merge with SSE headers.
        :type headers: dict[str, str] | None
        :return: A streaming response with live SSE events.
        :rtype: StreamingResponse
        """
        _cursor = starting_after
        merged_headers = {**self._sse_headers, **(headers or {})}

        async def _stream_from_subject():
            async for event in record.subject.subscribe(cursor=_cursor):  # type: ignore[union-attr]
                yield encode_sse_any_event(event)

        return StreamingResponse(_stream_from_subject(), media_type="text/event-stream", headers=merged_headers)

    async def _try_replay_persisted_stream(
        self,
        request: Request,
        response_id: str,
        *,
        isolation: IsolationContext | None = None,
        headers: dict[str, str] | None = None,
    ) -> Response | None:
        """Try to replay persisted SSE events from the stream provider.

        Returns a ``StreamingResponse`` if replay events are available,
        an error ``Response`` for invalid query parameters, or ``None``
        when no replay data exists.

        :param request: The incoming Starlette HTTP request.
        :type request: Request
        :param response_id: The response identifier to replay.
        :type response_id: str
        :keyword isolation: Optional isolation context for multi-tenant filtering.
        :paramtype isolation: IsolationContext | None
        :keyword headers: Optional extra headers (e.g. session headers) to merge with SSE headers.
        :paramtype headers: dict[str, str] | None
        :return: A streaming replay response, an error response, or ``None``.
        :rtype: Response | None
        """
        if self._stream_provider is None:
            return None
        try:
            replay_events = await self._stream_provider.get_stream_events(response_id, isolation=isolation)
            if replay_events is None:
                return None
            parsed_cursor = self._parse_starting_after(request, headers)
            if isinstance(parsed_cursor, Response):
                return parsed_cursor
            filtered = [e for e in replay_events if e["sequence_number"] > parsed_cursor]
            merged_headers = {**self._sse_headers, **(headers or {})}
            return StreamingResponse(
                _encode_sse(filtered),
                media_type="text/event-stream",
                headers=merged_headers,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to replay persisted stream for response_id=%s", response_id, exc_info=True)
            return None

    async def handle_delete(self, request: Request) -> Response:
        """Route handler for ``DELETE /responses/{response_id}``.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Deletion confirmation or error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        _hdrs = self._session_headers()
        format_error = _validate_response_id_format(response_id, _hdrs)
        if format_error is not None:
            return format_error

        _isolation = _extract_isolation(request)
        logger.info(
            "Deleting response %s, has_user_isolation_key=%s has_chat_isolation_key=%s",
            response_id,
            _isolation.user_key is not None,
            _isolation.chat_key is not None,
        )
        record = await self._runtime_state.get(response_id)
        if record is None:
            # Provider fallback: response may have been evicted from memory after
            # reaching terminal state, or the server restarted since creation.
            if await self._runtime_state.is_deleted(response_id):
                return _not_found(response_id, _hdrs)

            result = await self._provider_delete_response(response_id, _isolation, _hdrs)
            if result is not None:
                return result

            return _not_found(response_id, _hdrs)

        # Chat isolation enforcement
        if not _RuntimeState.check_chat_isolation(record.chat_isolation_key, _isolation.chat_key):
            return _not_found(response_id, _hdrs)

        # store=false responses are not deletable (FR-014)
        if not record.mode_flags.store:
            return _not_found(response_id, _hdrs)

        _refresh_background_status(record)

        if record.mode_flags.background and record.status in {"queued", "in_progress"}:
            return _invalid_request(
                "Cannot delete an in-flight response.",
                _hdrs,
                param="response_id",
            )

        deleted = await self._runtime_state.delete(response_id)
        if not deleted:
            # Race: the background task's eager eviction (try_evict) removed
            # the record between our get() and delete() calls. Eviction for
            # terminal responses typically happens after a provider
            # persistence attempt, but persistence is best-effort and may not
            # have succeeded, so delegate to the provider path as a fallback.
            if record.mode_flags.store:
                result = await self._provider_delete_response(response_id, _isolation, _hdrs)
                if result is not None:
                    return result
            return _not_found(response_id, _hdrs)

        if record.mode_flags.store:
            try:
                await self._provider.delete_response(response_id, isolation=_extract_isolation(request))
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Best-effort provider delete failed for response_id=%s", response_id, exc_info=True)
            # Clean up persisted stream events
            if self._stream_provider is not None:
                try:
                    await self._stream_provider.delete_stream_events(
                        response_id,
                        isolation=_extract_isolation(request),
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Best-effort stream event delete failed for response_id=%s",
                        response_id,
                        exc_info=True,
                    )

        logger.info("Deleted response %s", response_id)
        return JSONResponse(
            {"id": response_id, "object": "response", "deleted": True},
            status_code=200,
            headers=_hdrs,
        )

    async def _provider_delete_response(
        self,
        response_id: str,
        isolation: "IsolationContext",
        headers: dict[str, str],
    ) -> Response | None:
        """Delete a response from the durable provider (storage).

        Used by :meth:`handle_delete` in both the provider-fallback path
        (record already evicted from memory) and the eviction-race recovery
        path (record evicted between ``get()`` and ``delete()``).

        Returns a :class:`Response` on success or on a deterministic error
        (bad request, API error).  Returns ``None`` when the provider
        reports the response as not found **or** when an unexpected error
        occurs (logged at DEBUG), so the caller can fall through to 404.

        :param response_id: The response ID to delete.
        :type response_id: str
        :param isolation: Isolation context extracted from the request.
        :type isolation: IsolationContext
        :param headers: Session headers to include on the response.
        :type headers: dict[str, str]
        :return: A success/error response, or ``None`` if not found.
        :rtype: Response | None
        """
        try:
            await self._provider.delete_response(response_id, isolation=isolation)
            # Clean up persisted stream events
            if self._stream_provider is not None:
                try:
                    await self._stream_provider.delete_stream_events(response_id, isolation=isolation)
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.debug(
                        "Best-effort stream event delete failed for response_id=%s",
                        response_id,
                        exc_info=True,
                    )
            # Mark as deleted in runtime state so subsequent requests get 404
            await self._runtime_state.mark_deleted(response_id)
            logger.info("Deleted response %s via provider", response_id)
            return JSONResponse(
                {"id": response_id, "object": "response", "deleted": True},
                status_code=200,
                headers=headers,
            )
        except (FoundryResourceNotFoundError, KeyError):
            return None  # Caller falls through to 404
        except FoundryBadRequestError as exc:
            return _invalid_request(str(exc), headers, param="response_id")
        except FoundryApiError as exc:
            logger.error("Storage API error for DELETE response_id=%s: %s", response_id, exc, exc_info=True)
            return _error_response(exc, headers)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "Provider fallback failed for DELETE response_id=%s",
                response_id,
                exc_info=True,
            )
            return None

    async def handle_cancel(self, request: Request) -> Response:
        """Route handler for ``POST /responses/{response_id}/cancel``.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Cancelled snapshot or error response.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        _hdrs = self._session_headers()
        format_error = _validate_response_id_format(response_id, _hdrs)
        if format_error is not None:
            return format_error

        _isolation = _extract_isolation(request)
        logger.info(
            "Cancelling response %s, has_user_isolation_key=%s has_chat_isolation_key=%s",
            response_id,
            _isolation.user_key is not None,
            _isolation.chat_key is not None,
        )
        record = await self._runtime_state.get(response_id)
        if record is None:
            return await self._handle_cancel_fallback(response_id, _isolation, _hdrs)

        # Chat isolation enforcement on in-flight response
        if not _RuntimeState.check_chat_isolation(record.chat_isolation_key, _isolation.chat_key):
            return _not_found(response_id, _hdrs)

        _refresh_background_status(record)

        if not record.mode_flags.background:
            return _invalid_request(
                "Cannot cancel a synchronous response.",
                _hdrs,
                param="response_id",
            )

        terminal_error = _check_cancel_terminal_status(record.status, _hdrs)
        if terminal_error is not None:
            if record.status == "cancelled":
                record.set_response_snapshot(
                    build_cancelled_response(record.response_id, record.agent_reference, record.model)
                )
                return JSONResponse(_RuntimeState.to_snapshot(record), status_code=200, headers=_hdrs)
            return terminal_error

        # B11: initiate cancellation winddown
        record.cancel_requested = True
        record.cancel_signal.set()

        # Wait for handler task to finish (up to 10s grace period).
        if record.execution_task is not None:
            try:
                await asyncio.wait_for(asyncio.shield(record.execution_task), timeout=10.0)
            except (asyncio.TimeoutError, asyncio.CancelledError, Exception):  # pylint: disable=broad-exception-caught
                pass  # Handler may throw or timeout — already handled by the task itself

        # Set cancelled snapshot and transition
        record.set_response_snapshot(build_cancelled_response(record.response_id, record.agent_reference, record.model))
        # Stamp mode flags so the provider fallback can enforce B1/B2 checks
        # after eager eviction removes the in-memory record.
        if record.response is not None:
            record.response.background = record.mode_flags.background
        record.transition_to("cancelled")

        # Persist cancelled state to durable store (B11: cancellation always wins)
        try:
            if record.response is not None:
                await self._provider.update_response(record.response, isolation=_extract_isolation(request))
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Best-effort cancel persist failed for response_id=%s", record.response_id, exc_info=True)

        # Build snapshot before eviction removes the record from memory
        snapshot = _RuntimeState.to_snapshot(record)

        # Eager eviction: free memory now that the terminal state is persisted
        await self._runtime_state.try_evict(record.response_id)

        logger.info("Cancelled response %s, status=%s", response_id, snapshot.get("status"))
        return JSONResponse(snapshot, status_code=200, headers=_hdrs)

    async def _handle_cancel_fallback(
        self,
        response_id: str,
        _isolation: "IsolationContext",
        _hdrs: dict[str, str],
    ) -> Response:
        """Provider fallback for cancel when the record is not in runtime state.

        After a restart, stored terminal responses lose their runtime records.
        Check the provider so we return the correct 400 error instead of a
        misleading 404.

        :param response_id: The response ID to cancel.
        :type response_id: str
        :param _isolation: Isolation context from the request.
        :type _isolation: IsolationContext
        :param _hdrs: Session headers to include on the response.
        :type _hdrs: dict[str, str]
        :return: Error or idempotent response.
        :rtype: Response
        """
        try:
            response_obj = await self._provider.get_response(response_id, isolation=_isolation)
            persisted = response_obj.as_dict()

            # B1: background check comes first — non-bg responses always
            # get the "synchronous" message regardless of terminal status.
            if persisted.get("background") is not True:
                return _invalid_request(
                    "Cannot cancel a synchronous response.",
                    _hdrs,
                    param="response_id",
                )

            stored_status = persisted.get("status")
            terminal_error = _check_cancel_terminal_status(stored_status, _hdrs)
            if terminal_error is not None:
                if stored_status == "cancelled":
                    return JSONResponse(persisted, status_code=200, headers=_hdrs)
                return terminal_error
        except FoundryResourceNotFoundError:
            pass  # Fall through to 404 below
        except FoundryBadRequestError as exc:
            return _invalid_request(str(exc), _hdrs, param="response_id")
        except FoundryApiError as exc:
            logger.error("Storage API error for cancel response_id=%s: %s", response_id, exc, exc_info=True)
            return _error_response(exc, _hdrs)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug(
                "Provider fallback failed for cancel response_id=%s",
                response_id,
                exc_info=True,
            )
        return _not_found(response_id, _hdrs)

    async def handle_input_items(self, request: Request) -> Response:
        """Route handler for ``GET /responses/{response_id}/input_items``.

        Returns a paginated list of input items for the given response.

        :param request: Incoming Starlette request.
        :type request: Request
        :return: Paginated input items list.
        :rtype: Response
        """
        response_id = request.path_params["response_id"]
        _hdrs = self._session_headers()
        format_error = _validate_response_id_format(response_id, _hdrs)
        if format_error is not None:
            return format_error

        _isolation = _extract_isolation(request)
        logger.info(
            "Getting input items for response %s, has_user_isolation_key=%s has_chat_isolation_key=%s",
            response_id,
            _isolation.user_key is not None,
            _isolation.chat_key is not None,
        )

        # Chat isolation enforcement for in-flight responses.  After eviction,
        # the provider (Foundry storage) enforces isolation server-side.
        record = await self._runtime_state.get(response_id)
        if record is not None:
            if not _RuntimeState.check_chat_isolation(record.chat_isolation_key, _isolation.chat_key):
                return _not_found(response_id, _hdrs)

        limit_raw = request.query_params.get("limit", "20")
        try:
            limit = int(limit_raw)
        except ValueError:
            return _invalid_request("limit must be an integer between 1 and 100", _hdrs, param="limit")

        if limit < 1 or limit > 100:
            return _invalid_request("limit must be between 1 and 100", _hdrs, param="limit")

        order = request.query_params.get("order", "desc").lower()
        if order not in {"asc", "desc"}:
            return _invalid_request("order must be 'asc' or 'desc'", _hdrs, param="order")

        after = request.query_params.get("after")
        before = request.query_params.get("before")

        try:
            items = await self._provider.get_input_items(response_id, limit=100, ascending=True, isolation=_isolation)
        except ValueError:
            return _deleted_response(response_id, _hdrs)
        except FoundryResourceNotFoundError:
            return _not_found(response_id, _hdrs)
        except FoundryBadRequestError as exc:
            return _invalid_request(str(exc), _hdrs, param="response_id")
        except FoundryApiError as exc:
            logger.error("Storage API error for input_items response_id=%s: %s", response_id, exc, exc_info=True)
            return _error_response(exc, _hdrs)
        except KeyError:
            # Fall back to runtime_state for in-flight responses not yet persisted to provider.
            # Chat isolation was already checked above when the record is in-flight.
            try:
                items = await self._runtime_state.get_input_items(response_id)
            except ValueError:
                return _deleted_response(response_id, _hdrs)
            except KeyError:
                return _not_found(response_id, _hdrs)

        ordered_items = items if order == "asc" else list(reversed(items))
        ordered_dicts: list[dict[str, Any]] = [
            item.as_dict() if hasattr(item, "as_dict") else cast("dict[str, Any]", item) for item in ordered_items
        ]
        scoped_items = _apply_item_cursors(ordered_dicts, after=after, before=before)

        page = scoped_items[:limit]
        has_more = len(scoped_items) > limit

        first_id = _extract_item_id(page[0]) if page else None
        last_id = _extract_item_id(page[-1]) if page else None

        page_data = page

        return JSONResponse(
            {
                "object": "list",
                "data": page_data,
                "first_id": first_id,
                "last_id": last_id,
                "has_more": has_more,
            },
            status_code=200,
            headers=_hdrs,
        )

    async def handle_shutdown(self) -> None:
        """Graceful shutdown handler.

        Signals all active responses to cancel and waits for in-flight
        background executions to complete within the configured grace period.

        :return: None
        :rtype: None
        """
        self._is_draining = True
        self._shutdown_requested.set()

        records = await self._runtime_state.list_records()
        for record in records:
            if record.response_context is not None:
                record.response_context.is_shutdown_requested = True

            record.cancel_signal.set()

            if record.mode_flags.background and record.status in {"queued", "in_progress"}:
                record.set_response_snapshot(
                    build_failed_response(record.response_id, record.agent_reference, record.model)
                )
                record.transition_to("failed")

        deadline = asyncio.get_running_loop().time() + float(self._runtime_options.shutdown_grace_period_seconds)
        while True:
            pending = [
                record
                for record in records
                if record.mode_flags.background
                and record.execution_task is not None
                and record.status in {"queued", "in_progress"}
            ]
            if not pending:
                break
            if asyncio.get_running_loop().time() >= deadline:
                break
            await asyncio.sleep(0.05)
