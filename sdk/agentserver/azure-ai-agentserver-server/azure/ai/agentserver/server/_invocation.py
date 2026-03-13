# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Invocation protocol for AgentServer.

Encapsulates the ``/invocations`` REST endpoints, handler decorators,
dispatch methods, and OpenAPI spec serving.  Designed as a standalone
composed object so that ``AgentServer`` can compose multiple protocol
heads (invocation, chat, etc.) without inheritance conflicts.

Shared server state (tracing, error handling, timeouts) is received
via a :class:`~._server_context._ServerContext` instance.
"""
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import uuid
from collections.abc import Awaitable, Callable  # pylint: disable=import-error
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from ._constants import Constants
from ._errors import error_response
from ._logger import get_logger
from ._openapi_validator import _OpenApiValidator
from ._server_context import _ServerContext

logger = get_logger()


class _InvocationProtocol:
    """Invocation protocol implementation.

    Receives shared server state via a :class:`_ServerContext` and manages
    its own handler slots, agent identity, and endpoint handlers.

    **Not intended for direct instantiation.**  Use via
    :class:`~azure.ai.agentserver.server.AgentServer`, which creates and
    delegates to this object.
    """

    def __init__(
        self,
        ctx: _ServerContext,
        openapi_spec: Optional[dict[str, Any]],
        validator: Optional[_OpenApiValidator],
    ) -> None:
        """Initialise the invocation protocol.

        :param ctx: Shared server context (tracing, debug_errors, request_timeout).
        :type ctx: _ServerContext
        :param openapi_spec: Optional OpenAPI spec dict for documentation.
        :type openapi_spec: Optional[dict[str, Any]]
        :param validator: Optional request validator built from the spec.
        :type validator: Optional[_OpenApiValidator]
        """
        self._ctx = ctx
        self._invoke_fn: Optional[Callable] = None
        self._get_invocation_fn: Optional[Callable] = None
        self._cancel_invocation_fn: Optional[Callable] = None
        self._openapi_spec = openapi_spec
        self._validator = validator

    # ------------------------------------------------------------------
    # Route registration
    # ------------------------------------------------------------------

    @property
    def routes(self) -> list[Route]:
        """Starlette routes for the invocation protocol.

        :return: A list of four Route objects for the invocation endpoints.
        :rtype: list[Route]
        """
        return [
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

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def invoke_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Store *fn* as the invoke handler.  See :meth:`AgentServer.invoke_handler`.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        self._invoke_fn = fn
        return fn

    def get_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Store *fn* as the get-invocation handler.  See :meth:`AgentServer.get_invocation_handler`.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        self._get_invocation_fn = fn
        return fn

    def cancel_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Store *fn* as the cancel-invocation handler.  See :meth:`AgentServer.cancel_invocation_handler`.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        self._cancel_invocation_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Dispatch methods (internal)
    # ------------------------------------------------------------------

    async def _dispatch_invoke(self, request: Request) -> Response:
        """Dispatch to the registered invoke handler.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The response from the invoke handler.
        :rtype: Response
        :raises NotImplementedError: If no invoke handler has been registered.
        """
        if self._invoke_fn is not None:
            return await self._invoke_fn(request)
        raise NotImplementedError(
            "No invoke handler registered. Use the @server.invoke_handler decorator."
        )

    async def _dispatch_get_invocation(self, request: Request) -> Response:
        """Dispatch to the registered get-invocation handler, or return 501.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The response from the get-invocation handler.
        :rtype: Response
        """
        if self._get_invocation_fn is not None:
            return await self._get_invocation_fn(request)
        return error_response("not_supported", "get_invocation not supported", status_code=501)

    async def _dispatch_cancel_invocation(self, request: Request) -> Response:
        """Dispatch to the registered cancel-invocation handler, or return 501.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The response from the cancel-invocation handler.
        :rtype: Response
        """
        if self._cancel_invocation_fn is not None:
            return await self._cancel_invocation_fn(request)
        return error_response("not_supported", "cancel_invocation not supported", status_code=501)

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the stored OpenAPI spec.  See :meth:`AgentServer.get_openapi_spec`.

        :return: The registered OpenAPI spec or None.
        :rtype: Optional[dict[str, Any]]
        """
        return self._openapi_spec

    # ------------------------------------------------------------------
    # Endpoint handlers
    # ------------------------------------------------------------------

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /invocations/docs/openapi.json — return registered spec or 404.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: JSON response with the spec or 404.
        :rtype: Response
        """
        spec = self.get_openapi_spec()
        if spec is None:
            return error_response("not_found", "No OpenAPI spec registered", status_code=404)
        return JSONResponse(spec)

    async def _create_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations — create and process an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The invocation result or error response.
        :rtype: Response
        """
        invocation_id = (
            request.headers.get(Constants.INVOCATION_ID_HEADER)
            or str(uuid.uuid4())
        )
        request.state.invocation_id = invocation_id

        # Validate request body against OpenAPI spec
        if self._validator is not None:
            content_type = request.headers.get("content-type", "application/json")
            body = await request.body()
            errors = self._validator.validate_request(body, content_type)
            if errors:
                return error_response(
                    "invalid_payload",
                    "Request validation failed",
                    status_code=400,
                    details=[
                        {"code": "validation_error", "message": e}
                        for e in errors
                    ],
                )

        # Use manual span management so that streaming responses keep the
        # span open until the last chunk is yielded (or an error occurs).
        otel_span = None
        if self._ctx.tracing is not None:
            otel_span = self._ctx.tracing.start_request_span(
                request.headers,
                invocation_id,
                span_operation="execute_agent",
                operation_name="invoke_agent",
            )
        try:
            invoke_awaitable = self._dispatch_invoke(request)
            timeout = self._ctx.request_timeout or None  # 0 → None (no limit)
            response = await asyncio.wait_for(invoke_awaitable, timeout=timeout)
        except NotImplementedError as exc:
            if self._ctx.tracing is not None:
                self._ctx.tracing.end_span(otel_span, exc=exc)
            logger.error("Invocation %s failed: %s", invocation_id, exc)
            return error_response(
                "not_implemented",
                str(exc),
                status_code=501,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )
        except asyncio.TimeoutError as exc:
            if self._ctx.tracing is not None:
                self._ctx.tracing.end_span(otel_span, exc=exc)
            logger.error(
                "Invocation %s timed out after %ss",
                invocation_id,
                self._ctx.request_timeout,
            )
            return error_response(
                "request_timeout",
                f"Invocation timed out after {self._ctx.request_timeout}s",
                status_code=504,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if self._ctx.tracing is not None:
                self._ctx.tracing.end_span(otel_span, exc=exc)
            logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
            message = str(exc) if self._ctx.debug_errors else "Internal server error"
            return error_response(
                "internal_error",
                message,
                status_code=500,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )

        # For streaming responses, wrap the body iterator so the span stays
        # open until all chunks are sent and captures any streaming errors.
        if isinstance(response, StreamingResponse) and self._ctx.tracing is not None:
            response.body_iterator = self._ctx.tracing.trace_stream(response.body_iterator, otel_span)
        elif self._ctx.tracing is not None:
            self._ctx.tracing.end_span(otel_span)

        # Always set invocation_id header (overrides any handler-set value)
        response.headers[Constants.INVOCATION_ID_HEADER] = invocation_id

        return response

    async def _traced_invocation_endpoint(
        self,
        request: Request,
        span_operation: str,
        dispatch: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Shared implementation for get/cancel invocation endpoints.

        Extracts the invocation ID from path params, optionally creates a
        tracing span, dispatches to the handler, and handles errors.

        :param request: The incoming Starlette request.
        :type request: Request
        :param span_operation: Span operation name (e.g.
            ``"get_invocation"``).
        :type span_operation: str
        :param dispatch: The dispatch method to invoke.
        :type dispatch: Callable[[Request], Awaitable[Response]]
        :return: The handler response or an error response.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id

        span_cm: Any = contextlib.nullcontext(None)
        if self._ctx.tracing is not None:
            span_cm = self._ctx.tracing.request_span(
                request.headers, invocation_id, span_operation
            )
        with span_cm as _otel_span:
            try:
                response = await dispatch(request)
                response.headers[Constants.INVOCATION_ID_HEADER] = invocation_id
                return response
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if self._ctx.tracing is not None:
                    self._ctx.tracing.record_error(_otel_span, exc)
                logger.error("Error in %s %s: %s", span_operation, invocation_id, exc, exc_info=True)
                message = str(exc) if self._ctx.debug_errors else "Internal server error"
                return error_response(
                    "internal_error",
                    message,
                    status_code=500,
                    headers={Constants.INVOCATION_ID_HEADER: invocation_id},
                )

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        """GET /invocations/{invocation_id} — retrieve an invocation result.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The stored result or 501.
        :rtype: Response
        """
        return await self._traced_invocation_endpoint(
            request, "get_invocation", self._dispatch_get_invocation
        )

    async def _cancel_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations/{invocation_id}/cancel — cancel an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The cancellation result or 501.
        :rtype: Response
        """
        return await self._traced_invocation_endpoint(
            request, "cancel_invocation", self._dispatch_cancel_invocation
        )
