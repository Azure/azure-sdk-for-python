# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocation protocol host for Azure AI Hosted Agents.

Provides the invocation protocol endpoints and handler decorators
as a :class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""
import contextlib
import inspect
import os
import re
import uuid
from collections.abc import Awaitable, Callable  # pylint: disable=import-error
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
    get_logger,
    Constants,
    create_error_response,
)
from azure.ai.agentserver.core._tracing import TracingHelper

from ._constants import InvocationConstants

logger = get_logger()

# Maximum length and allowed characters for user-provided IDs (defense in depth).
_MAX_ID_LENGTH = 256
_VALID_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")


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
        return create_error_response("not_found", "get_invocation not implemented", status_code=404)

    async def _dispatch_cancel_invocation(self, request: Request) -> Response:
        if self._cancel_invocation_fn is not None:
            return await self._cancel_invocation_fn(request)
        return create_error_response("not_found", "cancel_invocation not implemented", status_code=404)

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
        baggage_token: Any,
        span_token: Any,
    ) -> StreamingResponse:
        """Wrap a streaming response's body iterator with tracing and context cleanup.

        Two layers of wrapping are applied in order:

        1. **Inner (tracing):** ``trace_stream`` wraps the body iterator so
           the OTel span covers the full streaming duration and records any
           errors that occur while yielding chunks.
        2. **Outer (context cleanup):** A second async generator detaches the
           span context and W3C Baggage context *after* all chunks have been
           sent (or an error occurs).  This ordering ensures the span is
           ended before the contexts are detached.

        :param response: The ``StreamingResponse`` returned by the user handler.
        :param otel_span: The OTel span (or *None* when tracing is disabled).
        :param baggage_token: Token from ``set_baggage`` (or *None*).
        :param span_token: Token from ``set_current_span`` (or *None*).
        :return: The same response object, with its body_iterator replaced.
        """
        # When tracing is disabled there is nothing to wrap — skip the
        # extra async-generator layer to avoid unnecessary overhead on
        # every streaming chunk.
        if self._tracing is None:
            return response

        # Inner wrap: trace_stream ends the span when iteration completes.
        response.body_iterator = self._tracing.trace_stream(response.body_iterator, otel_span)

        # Outer wrap: detach span context and baggage after all chunks are sent.
        original_iterator = response.body_iterator
        tracing = self._tracing  # capture for the closure

        async def _cleanup_iter():  # type: ignore[return-value]
            try:
                async for chunk in original_iterator:
                    yield chunk
            finally:
                tracing.detach_context(span_token)
                tracing.detach_baggage(baggage_token)

        response.body_iterator = _cleanup_iter()
        return response

    # ------------------------------------------------------------------
    # Endpoint handlers
    # ------------------------------------------------------------------

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        spec = self.get_openapi_spec()
        if spec is None:
            return create_error_response("not_found", "No OpenAPI spec registered", status_code=404)
        return JSONResponse(spec)

    async def _create_invocation_endpoint(self, request: Request) -> Response:
        generated_id = str(uuid.uuid4())
        raw_invocation_id = request.headers.get(InvocationConstants.INVOCATION_ID_HEADER) or ""
        invocation_id = _sanitize_id(raw_invocation_id, generated_id)
        request.state.invocation_id = invocation_id

        # Session ID: query param overrides env var / generated UUID
        raw_session_id = (
            request.query_params.get("agent_session_id")
            or os.environ.get(Constants.FOUNDRY_AGENT_SESSION_ID)
            or ""
        )
        session_id = _sanitize_id(raw_session_id, str(uuid.uuid4()))
        request.state.session_id = session_id

        baggage_token = None
        span_token = None
        response: Optional[Response] = None
        streaming_wrapped = False

        try:
            otel_span = None
            if self._tracing is not None:
                otel_span = self._tracing.start_request_span(
                    request.headers,
                    invocation_id,
                    span_operation="invoke_agent",
                    operation_name="invoke_agent",
                    session_id=session_id,
                )
                # Make the span the current span in context so that
                # child spans created by framework handlers are correctly
                # parented under this span instead of appearing as siblings.
                span_token = self._tracing.set_current_span(otel_span)
                self._safe_set_attrs(otel_span, {
                    InvocationConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                    InvocationConstants.ATTR_SPAN_SESSION_ID: session_id,
                })
                baggage_token = self._tracing.set_baggage({
                    InvocationConstants.ATTR_BAGGAGE_INVOCATION_ID: invocation_id,
                    InvocationConstants.ATTR_BAGGAGE_SESSION_ID: session_id,
                })

            try:
                response = await self._dispatch_invoke(request)
                response.headers[InvocationConstants.INVOCATION_ID_HEADER] = invocation_id
                response.headers[InvocationConstants.SESSION_ID_HEADER] = session_id
            except NotImplementedError as exc:
                self._safe_set_attrs(otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "not_implemented",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                if self._tracing is not None:
                    self._tracing.end_span(otel_span, exc=exc)
                logger.error("Invocation %s failed: %s", invocation_id, exc)
                return create_error_response(
                    "not_implemented",
                    str(exc),
                    status_code=501,
                    headers={
                        InvocationConstants.INVOCATION_ID_HEADER: invocation_id,
                        InvocationConstants.SESSION_ID_HEADER: session_id,
                    },
                )
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._safe_set_attrs(otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                if self._tracing is not None:
                    self._tracing.end_span(otel_span, exc=exc)
                logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
                return create_error_response(
                    "internal_error",
                    "Internal server error",
                    status_code=500,
                    headers={
                        InvocationConstants.INVOCATION_ID_HEADER: invocation_id,
                        InvocationConstants.SESSION_ID_HEADER: session_id,
                    },
                )

            if isinstance(response, StreamingResponse):
                wrapped = self._wrap_streaming_response(response, otel_span, baggage_token, span_token)
                streaming_wrapped = True
                return wrapped

            # Non-streaming: end the span immediately.
            if self._tracing is not None:
                self._tracing.end_span(otel_span)

            return response
        finally:
            # For non-streaming responses (or error paths that returned
            # before reaching _wrap_streaming_response), detach context
            # and baggage immediately.  Streaming responses handle this in
            # _wrap_streaming_response's cleanup iterator instead.
            if not streaming_wrapped:
                if self._tracing is not None:
                    self._tracing.detach_context(span_token)
                    self._tracing.detach_baggage(baggage_token)

    async def _traced_invocation_endpoint(
        self,
        request: Request,
        span_operation: str,
        dispatch: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id

        span_cm: Any = contextlib.nullcontext(None)
        if self._tracing is not None:
            span_cm = self._tracing.request_span(
                request.headers, invocation_id, span_operation,
                session_id=request.query_params.get("agent_session_id", ""),
            )
        with span_cm as _otel_span:
            self._safe_set_attrs(_otel_span, {
                InvocationConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationConstants.ATTR_SPAN_SESSION_ID: request.query_params.get("agent_session_id", ""),
            })
            try:
                response = await dispatch(request)
                response.headers[InvocationConstants.INVOCATION_ID_HEADER] = invocation_id
                return response
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._safe_set_attrs(_otel_span, {
                    InvocationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                # The exception is caught here (not re-raised), so OTel's
                # start_as_current_span won't see it.  Record it explicitly.
                if self._tracing is not None:
                    self._tracing.record_error(_otel_span, exc)
                logger.error("Error in %s %s: %s", span_operation, invocation_id, exc, exc_info=True)
                return create_error_response(
                    "internal_error",
                    "Internal server error",
                    status_code=500,
                    headers={InvocationConstants.INVOCATION_ID_HEADER: invocation_id},
                )

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        return await self._traced_invocation_endpoint(
            request, "get_invocation", self._dispatch_get_invocation
        )

    async def _cancel_invocation_endpoint(self, request: Request) -> Response:
        return await self._traced_invocation_endpoint(
            request, "cancel_invocation", self._dispatch_cancel_invocation
        )
