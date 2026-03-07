# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import logging
import uuid
from collections.abc import AsyncGenerator, Callable  # pylint: disable=import-error
from typing import Any, Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

from .._constants import Constants
from .._errors import error_response
from .._tracing import TracingHelper, extract_w3c_carrier
from ..validation._openapi_validator import OpenApiValidator
from . import _config

logger = logging.getLogger("azure.ai.agentserver")


class AgentServer:
    """Agent server with pluggable protocol heads.

    Instantiate and register handlers with decorators::

        server = AgentServer()

        @server.invoke_handler
        async def handle(request):
            return JSONResponse({"ok": True})

    Optionally register handlers with :meth:`get_invocation_handler` and
    :meth:`cancel_invocation_handler` for additional protocol support.

    Developer receives raw Starlette ``Request`` objects and returns raw
    Starlette ``Response`` objects, giving full control over content types,
    streaming, headers, and status codes.

    :param openapi_spec: Optional OpenAPI spec dict.  When provided, the spec
        is served at ``GET /invocations/docs/openapi.json`` for documentation.
        Runtime request validation is **not** enabled by default — set
        *enable_request_validation* to opt in.
    :type openapi_spec: Optional[dict[str, Any]]
    :param enable_request_validation: When *True*, incoming ``POST /invocations``
        request bodies are validated against the *openapi_spec* before reaching
        :meth:`invoke`.  When *None* (default) the
        ``AGENT_ENABLE_REQUEST_VALIDATION`` env var is consulted (``"true"`` to
        enable).  Requires *openapi_spec* to be set.
    :type enable_request_validation: Optional[bool]
    :param enable_tracing: Enable OpenTelemetry tracing.  When *None* (default)
        the ``AGENT_ENABLE_TRACING`` env var is consulted (``"true"`` to enable).
        Requires ``opentelemetry-api`` — install with
        ``pip install azure-ai-agentserver[tracing]``.
        When an Application Insights connection string is also available,
        traces and logs are automatically exported to Azure Monitor.
    :type enable_tracing: Optional[bool]
    :param application_insights_connection_string: Application Insights
        connection string for exporting traces and logs to Azure Monitor.
        When *None* (default) the ``APPLICATIONINSIGHTS_CONNECTION_STRING``
        env var is consulted.  Only takes effect when *enable_tracing* is
        ``True``.  Requires ``opentelemetry-sdk`` and
        ``azure-monitor-opentelemetry-exporter`` (included in the
        ``[tracing]`` extras group).
    :type application_insights_connection_string: Optional[str]
    :param graceful_shutdown_timeout: Seconds to wait for in-flight requests to
        complete after receiving SIGTERM / shutdown signal.  When *None* (default)
        the ``AGENT_GRACEFUL_SHUTDOWN_TIMEOUT`` env var is consulted; if that is
        also unset the default is 30 seconds.  Set to ``0`` to disable the
        drain period.
    :type graceful_shutdown_timeout: Optional[int]
    :param request_timeout: Maximum seconds an ``invoke()`` call may run before
        being cancelled.  When *None* (default) the ``AGENT_REQUEST_TIMEOUT``
        env var is consulted; if that is also unset the default is 300 seconds
        (5 minutes).  Set to ``0`` to disable the timeout.
    :type request_timeout: Optional[int]
    :param log_level: Library log level (e.g. ``"DEBUG"``, ``"INFO"``).  When
        *None* (default) the ``AGENT_LOG_LEVEL`` env var is consulted; if that
        is also unset the default is ``"INFO"``.
    :type log_level: Optional[str]
    :param debug_errors: When *True*, error responses include the original
        exception message instead of a generic ``"Internal server error"``.
        When *None* (default) the ``AGENT_DEBUG_ERRORS`` env var is consulted
        (any truthy value enables it).  Defaults to *False*.
    :type debug_errors: Optional[bool]
    """

    def __init__(
        self,
        openapi_spec: Optional[dict[str, Any]] = None,
        enable_request_validation: Optional[bool] = None,
        enable_tracing: Optional[bool] = None,
        application_insights_connection_string: Optional[str] = None,
        graceful_shutdown_timeout: Optional[int] = None,
        request_timeout: Optional[int] = None,
        log_level: Optional[str] = None,
        debug_errors: Optional[bool] = None,
    ) -> None:
        # Decorator handler slots ------------------------------------------
        self._invoke_fn: Optional[Callable] = None
        self._get_invocation_fn: Optional[Callable] = None
        self._cancel_invocation_fn: Optional[Callable] = None
        self._shutdown_fn: Optional[Callable] = None

        # Logging & debug -------------------------------------------------
        resolved_level = _config.resolve_log_level(log_level)
        logger.setLevel(resolved_level)
        if not logger.handlers:
            _console = logging.StreamHandler()
            _console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            logger.addHandler(_console)
        self._debug_errors = _config.resolve_bool_feature(
            debug_errors, Constants.AGENT_DEBUG_ERRORS
        )

        self._openapi_spec = openapi_spec
        _validation_on = _config.resolve_bool_feature(
            enable_request_validation, Constants.AGENT_ENABLE_REQUEST_VALIDATION
        )
        self._validator: Optional[OpenApiValidator] = (
            OpenApiValidator(openapi_spec)
            if openapi_spec and _validation_on
            else None
        )
        _tracing_on = _config.resolve_bool_feature(enable_tracing, Constants.AGENT_ENABLE_TRACING)
        _conn_str = _config.resolve_appinsights_connection_string(
            application_insights_connection_string
        ) if _tracing_on else None
        self._tracing: Optional[TracingHelper] = (
            TracingHelper(connection_string=_conn_str) if _tracing_on else None
        )
        self._graceful_shutdown_timeout = _config.resolve_graceful_shutdown_timeout(
            graceful_shutdown_timeout
        )
        self._request_timeout = _config.resolve_request_timeout(request_timeout)
        self.app: Starlette
        self._build_app()

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def invoke_handler(self, fn: Callable) -> Callable:
        """Register a function as the invoke handler.

        Usage::

            @server.invoke_handler
            async def handle(request: Request) -> Response:
                ...

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._invoke_fn = fn
        return fn

    def get_invocation_handler(self, fn: Callable) -> Callable:
        """Register a function as the get-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._get_invocation_fn = fn
        return fn

    def cancel_invocation_handler(self, fn: Callable) -> Callable:
        """Register a function as the cancel-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._cancel_invocation_fn = fn
        return fn

    def shutdown_handler(self, fn: Callable) -> Callable:
        """Register a function as the shutdown handler.

        :param fn: Async function called during graceful shutdown.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        """
        self._shutdown_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Dispatch methods (internal)
    # ------------------------------------------------------------------

    async def _dispatch_invoke(self, request: Request) -> Response:
        """Dispatch to the registered invoke handler."""
        if self._invoke_fn is not None:
            return await self._invoke_fn(request)
        raise RuntimeError(
            "No invoke handler registered. Use the @server.invoke_handler decorator."
        )

    async def _dispatch_get_invocation(self, request: Request) -> Response:
        """Dispatch to the registered get-invocation handler, or return 404."""
        if self._get_invocation_fn is not None:
            return await self._get_invocation_fn(request)
        return error_response("not_supported", "get_invocation not supported", status_code=404)

    async def _dispatch_cancel_invocation(self, request: Request) -> Response:
        """Dispatch to the registered cancel-invocation handler, or return 404."""
        if self._cancel_invocation_fn is not None:
            return await self._cancel_invocation_fn(request)
        return error_response("not_supported", "cancel_invocation not supported", status_code=404)

    async def _dispatch_shutdown(self) -> None:
        """Dispatch to the registered shutdown handler, or no-op."""
        if self._shutdown_fn is not None:
            await self._shutdown_fn()

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the OpenAPI spec dict for this agent, or None.

        :return: The registered OpenAPI spec or None.
        :rtype: Optional[dict[str, Any]]
        """
        return self._openapi_spec

    # ------------------------------------------------------------------
    # Run helpers
    # ------------------------------------------------------------------

    def _build_hypercorn_config(self, host: str, port: int) -> object:
        """Create a Hypercorn config with resolved host, port and timeouts.

        :param host: Network interface to bind.
        :type host: str
        :param port: Port to bind.
        :type port: int
        :return: Configured Hypercorn config.
        :rtype: hypercorn.config.Config
        """
        from hypercorn.config import Config as HypercornConfig

        config = HypercornConfig()
        config.bind = [f"{host}:{port}"]
        config.graceful_timeout = float(self._graceful_shutdown_timeout)
        return config

    def run(self, host: str = "127.0.0.1", port: Optional[int] = None) -> None:
        """Start the server synchronously.

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``127.0.0.1``.
            Use ``"0.0.0.0"`` to listen on all interfaces.
        :type host: str
        :param port: Port to bind. Defaults to ``AGENT_SERVER_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentServer starting on %s:%s", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        asyncio.run(_hypercorn_serve(self.app, config))  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    async def run_async(self, host: str = "127.0.0.1", port: Optional[int] = None) -> None:
        """Start the server asynchronously (awaitable).

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``127.0.0.1``.
            Use ``"0.0.0.0"`` to listen on all interfaces.
        :type host: str
        :param port: Port to bind. Defaults to ``AGENT_SERVER_PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentServer starting on %s:%s (async)", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        await _hypercorn_serve(self.app, config)  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    # ------------------------------------------------------------------
    # Private: app construction
    # ------------------------------------------------------------------

    def _build_app(self) -> None:
        """Construct the Starlette ASGI application with all routes."""

        @contextlib.asynccontextmanager
        async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:  # noqa: RUF029
            logger.info("AgentServer started")
            yield

            # --- SHUTDOWN: runs once when the server is stopping ---
            logger.info(
                "AgentServer shutting down (graceful timeout=%ss)",
                self._graceful_shutdown_timeout,
            )
            try:
                await asyncio.wait_for(
                    self._dispatch_shutdown(),
                    timeout=self._graceful_shutdown_timeout or None,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "on_shutdown did not complete within %ss timeout",
                    self._graceful_shutdown_timeout,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("Error in on_shutdown")

        routes = [
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
            Route("/liveness", self._liveness_endpoint, methods=["GET"], name="liveness"),
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        ]

        self.app = Starlette(routes=routes, lifespan=_lifespan)

    # ------------------------------------------------------------------
    # Private: endpoint handlers
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
        invocation_id = str(uuid.uuid4())
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

        carrier = extract_w3c_carrier(request.headers)

        # Use manual span management so that streaming responses keep the
        # span open until the last chunk is yielded (or an error occurs).
        otel_span = (
            self._tracing.start_span(
                "AgentServer.invoke",
                attributes={"invocation.id": invocation_id},
                carrier=carrier,
            )
            if self._tracing is not None
            else None
        )
        try:
            invoke_awaitable = self._dispatch_invoke(request)
            timeout = self._request_timeout or None  # 0 → None (no limit)
            response = await asyncio.wait_for(invoke_awaitable, timeout=timeout)
        except asyncio.TimeoutError:
            if self._tracing is not None:
                self._tracing.end_span(otel_span)
            logger.error(
                "Invocation %s timed out after %ss",
                invocation_id,
                self._request_timeout,
            )
            return error_response(
                "request_timeout",
                f"Invocation timed out after {self._request_timeout}s",
                status_code=504,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if self._tracing is not None:
                self._tracing.end_span(otel_span, exc=exc)
            logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
            message = str(exc) if self._debug_errors else "Internal server error"
            return error_response(
                "internal_error",
                message,
                status_code=500,
                headers={Constants.INVOCATION_ID_HEADER: invocation_id},
            )

        # For streaming responses, wrap the body iterator so the span stays
        # open until all chunks are sent and captures any streaming errors.
        if isinstance(response, StreamingResponse) and self._tracing is not None:
            response.body_iterator = self._tracing.trace_stream(response.body_iterator, otel_span)
        elif self._tracing is not None:
            self._tracing.end_span(otel_span)

        # Auto-inject invocation_id header if developer didn't set it
        if Constants.INVOCATION_ID_HEADER not in response.headers:
            response.headers[Constants.INVOCATION_ID_HEADER] = invocation_id

        return response

    async def _get_invocation_endpoint(self, request: Request) -> Response:
        """GET /invocations/{invocation_id} — retrieve an invocation result.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The stored result or 404.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id
        carrier = extract_w3c_carrier(request.headers)
        span_cm = (
            self._tracing.span(
                "AgentServer.get_invocation",
                attributes={"invocation.id": invocation_id},
                carrier=carrier,
            )
            if self._tracing is not None
            else contextlib.nullcontext(None)
        )
        with span_cm as _otel_span:
            try:
                return await self._dispatch_get_invocation(request)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if self._tracing is not None:
                    self._tracing.record_error(_otel_span, exc)
                logger.error("Error in get_invocation %s: %s", invocation_id, exc, exc_info=True)
                message = str(exc) if self._debug_errors else "Internal server error"
                return error_response(
                    "internal_error",
                    message,
                    status_code=500,
                )

    async def _cancel_invocation_endpoint(self, request: Request) -> Response:
        """POST /invocations/{invocation_id}/cancel — cancel an invocation.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: The cancellation result or 404.
        :rtype: Response
        """
        invocation_id = request.path_params["invocation_id"]
        request.state.invocation_id = invocation_id
        carrier = extract_w3c_carrier(request.headers)
        span_cm = (
            self._tracing.span(
                "AgentServer.cancel_invocation",
                attributes={"invocation.id": invocation_id},
                carrier=carrier,
            )
            if self._tracing is not None
            else contextlib.nullcontext(None)
        )
        with span_cm as _otel_span:
            try:
                return await self._dispatch_cancel_invocation(request)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if self._tracing is not None:
                    self._tracing.record_error(_otel_span, exc)
                logger.error("Error in cancel_invocation %s: %s", invocation_id, exc, exc_info=True)
                message = str(exc) if self._debug_errors else "Internal server error"
                return error_response(
                    "internal_error",
                    message,
                    status_code=500,
                )

    async def _liveness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /liveness — health check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "alive"})

    async def _readiness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /readiness — readiness check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return JSONResponse({"status": "ready"})


