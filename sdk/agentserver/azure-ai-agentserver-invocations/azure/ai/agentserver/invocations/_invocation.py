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
    ) -> StreamingResponse:
        """Wrap a streaming response's body iterator with span lifecycle.

        ``trace_stream`` wraps the body iterator so the OTel span covers
        the full streaming duration and is ended when iteration completes.

        :param response: The ``StreamingResponse`` returned by the user handler.
        :type response: ~starlette.responses.StreamingResponse
        :param otel_span: The OTel span (or *None* when tracing is disabled).
        :type otel_span: any
        :return: The same response object, with its body_iterator replaced.
        :rtype: ~starlette.responses.StreamingResponse
        """
        if self._tracing is None:
            return response

        response.body_iterator = self._tracing.trace_stream(response.body_iterator, otel_span)
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

        with self._request_span(
            request.headers, invocation_id, "invoke_agent",
            operation_name="invoke_agent", session_id=session_id,
        ) as otel_span:
            self._safe_set_attrs(otel_span, {
                InvocationConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationConstants.ATTR_SPAN_SESSION_ID: session_id,
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
                # trace_stream will end the span when streaming completes
                return self._wrap_streaming_response(response, otel_span)

            # Non-streaming: end span now
            if self._tracing is not None:
                self._tracing.end_span(otel_span)

            return response

    def _request_span(
        self,
        headers: Any,
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> Any:
        """Create a request span — returns a no-op context manager when tracing is off.

        :param headers: HTTP request headers.
        :type headers: any
        :param invocation_id: The request/invocation ID.
        :type invocation_id: str
        :param span_operation: Span operation name.
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` value.
        :type operation_name: str or None
        :param session_id: Session ID (empty string if absent).
        :type session_id: str
        :return: Context manager yielding the OTel span or *None*.
        :rtype: any
        """
        if self._tracing is not None:
            return self._tracing.request_span(
                headers, invocation_id, span_operation,
                operation_name=operation_name, session_id=session_id,
                end_on_exit=False,
            )
        return contextlib.nullcontext(None)

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
