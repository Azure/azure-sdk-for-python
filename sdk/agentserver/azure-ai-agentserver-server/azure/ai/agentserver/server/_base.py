# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable  # pylint: disable=import-error
from typing import Any, Optional

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from ._constants import Constants
from ._logger import get_logger
from ._tracing import _TracingHelper
from ._openapi_validator import _OpenApiValidator
from ._invocation import _InvocationProtocol
from ._server_context import _ServerContext
from . import _config

logger = get_logger()

# Pre-built health-check responses to avoid per-request allocation.
_LIVENESS_BODY = b'{"status":"alive"}'
_READINESS_BODY = b'{"status":"ready"}'


class AgentServer:  # pylint: disable=too-many-instance-attributes
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
        ``pip install azure-ai-agentserver-server[tracing]``.
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
        *,
        openapi_spec: Optional[dict[str, Any]] = None,
        enable_request_validation: Optional[bool] = None,
        enable_tracing: Optional[bool] = None,
        application_insights_connection_string: Optional[str] = None,
        graceful_shutdown_timeout: Optional[int] = None,
        request_timeout: Optional[int] = None,
        log_level: Optional[str] = None,
        debug_errors: Optional[bool] = None,
    ) -> None:
        # Shutdown handler slot (server-level lifecycle) -------------------
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

        # OpenAPI validation -----------------------------------------------
        _validation_on = _config.resolve_bool_feature(
            enable_request_validation, Constants.AGENT_ENABLE_REQUEST_VALIDATION
        )
        validator: Optional[_OpenApiValidator] = (
            _OpenApiValidator(openapi_spec)
            if openapi_spec and _validation_on
            else None
        )

        # Tracing ----------------------------------------------------------
        _tracing_on = _config.resolve_bool_feature(enable_tracing, Constants.AGENT_ENABLE_TRACING)
        _conn_str = _config.resolve_appinsights_connection_string(
            application_insights_connection_string
        ) if _tracing_on else None
        self._tracing: Optional[_TracingHelper] = (
            _TracingHelper(connection_string=_conn_str) if _tracing_on else None
        )

        # Timeouts ---------------------------------------------------------
        self._graceful_shutdown_timeout = _config.resolve_graceful_shutdown_timeout(
            graceful_shutdown_timeout
        )
        self._request_timeout = _config.resolve_request_timeout(request_timeout)

        # Invocation protocol (composed) -------------------------------------
        ctx = _ServerContext(
            tracing=self._tracing,
            debug_errors=self._debug_errors,
            request_timeout=self._request_timeout,
        )
        self._invocation = _InvocationProtocol(ctx, openapi_spec, validator)

        self.app: Starlette
        self._build_app()

    # ------------------------------------------------------------------
    # Shutdown handler (server-level lifecycle)
    # ------------------------------------------------------------------

    def shutdown_handler(self, fn: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        """Register a function as the shutdown handler.

        :param fn: Async function called during graceful shutdown.
        :type fn: Callable[[], Awaitable[None]]
        :return: The original function (unmodified).
        :rtype: Callable[[], Awaitable[None]]
        """
        self._shutdown_fn = fn
        return fn

    async def _dispatch_shutdown(self) -> None:
        """Dispatch to the registered shutdown handler, or no-op."""
        if self._shutdown_fn is not None:
            await self._shutdown_fn()

    # ------------------------------------------------------------------
    # Invocation protocol delegates
    # ------------------------------------------------------------------

    def invoke_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the invoke handler.

        Usage::

            @server.invoke_handler
            async def handle(request: Request) -> Response:
                ...

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        return self._invocation.invoke_handler(fn)

    def get_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the get-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        return self._invocation.get_invocation_handler(fn)

    def cancel_invocation_handler(
        self, fn: Callable[[Request], Awaitable[Response]]
    ) -> Callable[[Request], Awaitable[Response]]:
        """Register a function as the cancel-invocation handler.

        :param fn: Async function accepting a Starlette Request and returning a Response.
        :type fn: Callable[[Request], Awaitable[Response]]
        :return: The original function (unmodified).
        :rtype: Callable[[Request], Awaitable[Response]]
        """
        return self._invocation.cancel_invocation_handler(fn)

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the OpenAPI spec dict for this agent, or None.

        :return: The registered OpenAPI spec or None.
        :rtype: Optional[dict[str, Any]]
        """
        return self._invocation.get_openapi_spec()

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

        routes = list(self._invocation.routes)
        routes.extend([
            Route("/liveness", self._liveness_endpoint, methods=["GET"], name="liveness"),
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        ])

        self.app = Starlette(routes=routes, lifespan=_lifespan)

    # ------------------------------------------------------------------
    # Health endpoints
    # ------------------------------------------------------------------

    async def _liveness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /liveness — health check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return Response(_LIVENESS_BODY, media_type="application/json")

    async def _readiness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /readiness — readiness check.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return Response(_READINESS_BODY, media_type="application/json")
