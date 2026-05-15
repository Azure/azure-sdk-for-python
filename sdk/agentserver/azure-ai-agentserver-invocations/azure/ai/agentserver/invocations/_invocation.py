# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocation protocol host for Azure AI Hosted Agents.

Provides the invocation protocol endpoints and handler decorators
as a :class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""
import contextvars
import inspect
import logging
import re
import threading
import uuid
from collections.abc import Awaitable, Callable  # pylint: disable=import-error
from typing import Any, Optional

from opentelemetry import baggage as _otel_baggage, context as _otel_context
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
    create_error_response,
    detach_context,
    end_span,
    record_error,
    set_current_span,
    trace_stream,
)
from azure.ai.agentserver.core._platform_headers import (  # pylint: disable=import-error,no-name-in-module
    CHAT_ISOLATION_KEY,
    ERROR_DETAIL,
    ERROR_SOURCE,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    USER_ISOLATION_KEY,
)

from ._constants import InvocationConstants

logger = logging.getLogger("azure.ai.agentserver")

# ---------------------------------------------------------------------------
# Internal error-source classification
# ---------------------------------------------------------------------------

_ERROR_SOURCE_UPSTREAM: str = "upstream"
_ERROR_SOURCE_PLATFORM: str = "platform"


def _apply_error_source_headers(
    headers: dict[str, str],
    error_source: str,
    error_detail: Optional[str] = None,
) -> dict[str, str]:
    """Return a new dict with error source classification headers merged in.

    :param headers: Base headers to merge into.
    :type headers: dict[str, str]
    :param error_source: The error source value (user/platform/upstream).
    :type error_source: str
    :param error_detail: Optional detail string for platform errors.
    :type error_detail: str or None
    :return: A new dict containing the original headers plus error source headers.
    :rtype: dict[str, str]
    """
    merged = {**headers, ERROR_SOURCE: error_source}
    if error_detail:
        merged[ERROR_DETAIL] = error_detail
    return merged


def _classify_error(exc: BaseException) -> tuple[str, Optional[str]]:
    """Classify an exception: platform-tagged → (platform, detail), else → (upstream, None).

    :param exc: The exception to classify.
    :type exc: BaseException
    :return: A tuple of (error_source, error_detail).
    :rtype: tuple[str, str or None]
    """
    if getattr(exc, PLATFORM_ERROR_TAG, False) is True:
        detail = f"{type(exc).__name__}: {exc}"
        if len(detail) > MAX_ERROR_DETAIL_LENGTH:
            suffix = "...[truncated]"
            detail = detail[: MAX_ERROR_DETAIL_LENGTH - len(suffix)] + suffix
        return _ERROR_SOURCE_PLATFORM, detail
    return _ERROR_SOURCE_UPSTREAM, None

# Maximum length and allowed characters for user-provided IDs (defense in depth).
_MAX_ID_LENGTH = 256
_VALID_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")


# Context variables for structured logging — concurrency-safe alternative to logger filters.
_invocation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("invocation_id", default="")
_session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("session_id", default="")


class _InvocationLogFilter(logging.Filter):
    """Attach invocation and session IDs to every log record from context vars.

    Reads from ``contextvars`` rather than instance state, so a single
    filter instance can be installed once on the logger (not per-request).
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.invocation_id = _invocation_id_var.get("")  # type: ignore[attr-defined]
        record.session_id = _session_id_var.get("")  # type: ignore[attr-defined]
        return True


# Install once on first request — no per-request add/remove needed.
_log_filter_lock = threading.Lock()
_log_filter_installed = False


def _ensure_log_filter() -> None:
    """Install the log filter on first use (lazy, thread-safe)."""
    global _log_filter_installed  # pylint: disable=global-statement
    if _log_filter_installed:
        return
    with _log_filter_lock:
        if _log_filter_installed:
            return
        logger.addFilter(_InvocationLogFilter())
        _log_filter_installed = True


def _sanitize_id(value: str, fallback: str) -> str:
    """Validate a user-provided ID string.

    Returns *value* unchanged when it passes validation, otherwise returns
    *fallback*.  This prevents excessively long or malformed IDs from
    propagating into headers, span attributes, and log messages.

    :param value: The raw ID from a header or query parameter.
    :type value: str
    :param fallback: A safe fallback value (typically a generated UUID).
    :type fallback: str
    :return: The validated ID or the fallback.
    :rtype: str
    """
    if not value or len(value) > _MAX_ID_LENGTH or not _VALID_ID_RE.match(value):
        return fallback
    return value


class InvocationAgentServerHost(AgentServerHost):
    """Invocation protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    the invocation protocol endpoints.  Use the decorator methods to wire
    handler functions to the endpoints.

    For multi-protocol agents, compose via cooperative inheritance::

        class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
            pass

    Usage::

        from azure.ai.agentserver.invocations import InvocationAgentServerHost

        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def handle(request):
            return JSONResponse({"ok": True})

        app.run()

    :param openapi_spec: Optional OpenAPI spec dict.  When provided, the spec
        is served at ``GET /invocations/docs/openapi.json``.
    :type openapi_spec: Optional[dict[str, Any]]
    """

    _INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.Invocations"

    def __init__(
        self,
        *,
        openapi_spec: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self._invoke_fn: Optional[Callable] = None
        self._get_invocation_fn: Optional[Callable] = None
        self._cancel_invocation_fn: Optional[Callable] = None
        self._openapi_spec = openapi_spec

        # Build invocation routes and pass to parent via routes kwarg
        invocation_routes = [
            Route(
                "/invocations/docs/openapi.json",
                self._get_openapi_spec_endpoint,
                methods=["GET"],
                name="get_openapi_spec",
            ),
            Route(
                "/invocations",
                self._create_invocation_endpoint,
                methods=["POST"],
                name="create_invocation",
            ),
            Route(
                "/invocations/{invocation_id}",
                self._get_invocation_endpoint,
                methods=["GET"],
                name="get_invocation",
            ),
            Route(
                "/invocations/{invocation_id}/cancel",
                self._cancel_invocation_endpoint,
                methods=["POST"],
                name="cancel_invocation",
            ),
        ]

        # Merge with any routes from sibling mixins via cooperative init
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + invocation_routes, **kwargs)

        # --- Invocations startup configuration logging ---
        logger.info(
            "Invocations protocol: openapi_spec_configured=%s",
            self._openapi_spec is not None,
        )

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def invoke_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the invoke handler.

        Usage::

            @invocations.invoke_handler
            async def handle(request: Request) -> Response:
                ...

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"invoke_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._invoke_fn = fn
        return fn

    def get_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the get-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"get_invocation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._get_invocation_fn = fn
        return fn

    def cancel_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the cancel-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"cancel_invocation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._cancel_invocation_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Dispatch methods (internal)
    # ------------------------------------------------------------------

    async def _dispatch_invoke(self, request: Request) -> Response:
        if self._invoke_fn is not None:
            return await self._invoke_fn(request)
        raise NotImplementedError(
            "No invoke handler registered. Use the @invocations.invoke_handler decorator."
        )

    async def _dispatch_get_invocation(self, request: Request) -> Response:
        if self._get_invocation_fn is not None:
            return await self._get_invocation_fn(request)
        return create_error_response(
            "not_found", "get_invocation not implemented",
            status_code=404,
            headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
        )

    async def _dispatch_cancel_invocation(self, request: Request) -> Response:
        if self._cancel_invocation_fn is not None:
            return await self._cancel_invocation_fn(request)
        return create_error_response(
            "not_found", "cancel_invocation not implemented",
            status_code=404,
            headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
        )

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the stored OpenAPI spec, or None."""
        return self._openapi_spec

    # ------------------------------------------------------------------
    # Span attribute helper
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_set_attrs(span: Any, attrs: dict[str, str]) -> None:
        if span is None:
            return
        try:
            for key, value in attrs.items():
                span.set_attribute(key, value)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to set span attributes: %s", list(attrs.keys()), exc_info=True)

    # ------------------------------------------------------------------
    # Streaming response helpers
    # ------------------------------------------------------------------

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

        :param response: The ``StreamingResponse`` returned by the user handler.
        :type response: ~starlette.responses.StreamingResponse
        :param otel_span: The OTel span (or *None* when tracing is disabled).
        :type otel_span: any
        :return: The same response object, with its body_iterator replaced.
        :rtype: ~starlette.responses.StreamingResponse
        """
        if otel_span is None:
            return response

        # Inner wrap: trace_stream ends the span when iteration completes.
        traced = trace_stream(response.body_iterator, otel_span)

        # Outer wrap: re-attach span as current context during streaming
        # so child spans are correctly parented.
        async def _iter_with_context():  # type: ignore[return-value]
            token = set_current_span(otel_span)
            try:
                async for chunk in traced:
                    yield chunk
            finally:
                detach_context(token)

        response.body_iterator = _iter_with_context()
        return response

    # ------------------------------------------------------------------
    # Endpoint handlers
    # ------------------------------------------------------------------

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        spec = self.get_openapi_spec()
        if spec is None:
            return create_error_response(
                "not_found", "No OpenAPI spec registered",
                status_code=404,
                headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
            )
        return JSONResponse(spec)

    async def _create_invocation_endpoint(self, request: Request) -> Response:
        generated_id = str(uuid.uuid4())
        raw_invocation_id = request.headers.get(InvocationConstants.INVOCATION_ID_HEADER) or ""
        invocation_id = _sanitize_id(raw_invocation_id, generated_id)
        request.state.invocation_id = invocation_id

        # Session ID: query param overrides env var / generated UUID
        raw_session_id = (
            request.query_params.get("agent_session_id")
            or self.config.session_id
            or ""
        )
        session_id = _sanitize_id(raw_session_id, str(uuid.uuid4()))
        request.state.session_id = session_id

        # Platform isolation headers — expose to handlers
        request.state.user_isolation_key = request.headers.get(USER_ISOLATION_KEY, "")
        request.state.chat_isolation_key = request.headers.get(CHAT_ISOLATION_KEY, "")

        with self.request_span(
            request.headers, invocation_id, "invoke_agent",
            operation_name="invoke_agent", session_id=session_id,
            end_on_exit=False,
        ) as otel_span:
            self._safe_set_attrs(otel_span, {
                InvocationConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            # Propagate invocation/session IDs as W3C baggage so downstream
            # services receive them automatically via the baggage header.
            ctx = _otel_context.get_current()
            ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.invocation_id", invocation_id, context=ctx,
            )
            ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.session_id", session_id, context=ctx,
            )
            baggage_token = _otel_context.attach(ctx)

            # Set structured logging context (concurrency-safe via contextvars)
            _ensure_log_filter()
            inv_token = _invocation_id_var.set(invocation_id)
            session_token = _session_id_var.set(session_id)
            try:
                response = await self._dispatch_invoke(request)
                response.headers[InvocationConstants.INVOCATION_ID_HEADER] = invocation_id
                response.headers[InvocationConstants.SESSION_ID_HEADER] = session_id
            except NotImplementedError as exc:
                self._safe_set_attrs(otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "not_implemented",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                end_span(otel_span, exc=exc)
                logger.error("Invocation %s failed: %s", invocation_id, exc)
                return create_error_response(
                    "not_implemented",
                    str(exc),
                    status_code=501,
                    headers=_apply_error_source_headers(
                        {
                            InvocationConstants.INVOCATION_ID_HEADER: invocation_id,
                            InvocationConstants.SESSION_ID_HEADER: session_id,
                        },
                        _ERROR_SOURCE_UPSTREAM,
                    ),
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                error_source, error_detail = _classify_error(exc)
                self._safe_set_attrs(otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                end_span(otel_span, exc=exc)
                logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
                return create_error_response(
                    "internal_error",
                    "Internal server error",
                    status_code=500,
                    headers=_apply_error_source_headers(
                        {
                            InvocationConstants.INVOCATION_ID_HEADER: invocation_id,
                            InvocationConstants.SESSION_ID_HEADER: session_id,
                        },
                        error_source,
                        error_detail,
                    ),
                )
            finally:
                _invocation_id_var.reset(inv_token)
                _session_id_var.reset(session_token)
                try:
                    _otel_context.detach(baggage_token)
                except ValueError:
                    pass

            if isinstance(response, StreamingResponse):
                return self._wrap_streaming_response(response, otel_span)

            end_span(otel_span)
            return response

    async def _traced_invocation_endpoint(
        self,
        request: Request,
        span_operation: str,
        dispatch: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        raw_invocation_id = request.path_params["invocation_id"]
        invocation_id = _sanitize_id(raw_invocation_id, raw_invocation_id)
        request.state.invocation_id = invocation_id

        raw_session_id = request.query_params.get("agent_session_id", "")
        session_id = _sanitize_id(raw_session_id, "") if raw_session_id else ""

        with self.request_span(
            request.headers, invocation_id, span_operation,
            operation_name=span_operation, session_id=session_id,
        ) as _otel_span:
            self._safe_set_attrs(_otel_span, {
                InvocationConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationConstants.ATTR_SPAN_SESSION_ID: session_id,
            })
            _ensure_log_filter()
            inv_token = _invocation_id_var.set(invocation_id)
            session_token = _session_id_var.set(session_id)
            try:
                response = await dispatch(request)
                response.headers[InvocationConstants.INVOCATION_ID_HEADER] = invocation_id
                return response
            except Exception as exc:  # pylint: disable=broad-exception-caught
                error_source, error_detail = _classify_error(exc)
                self._safe_set_attrs(_otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                record_error(_otel_span, exc)
                logger.error("Error in %s %s: %s", span_operation, invocation_id, exc, exc_info=True)
                return create_error_response(
                    "internal_error",
                    "Internal server error",
                    status_code=500,
                    headers=_apply_error_source_headers(
                        {InvocationConstants.INVOCATION_ID_HEADER: invocation_id},
                        error_source,
                        error_detail,
                    ),
                )
            finally:
                _invocation_id_var.reset(inv_token)
                _session_id_var.reset(session_token)

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        return await self._traced_invocation_endpoint(
            request, "get_invocation", self._dispatch_get_invocation
        )

    async def _cancel_invocation_endpoint(self, request: Request) -> Response:
        return await self._traced_invocation_endpoint(
            request, "cancel_invocation", self._dispatch_cancel_invocation
        )
