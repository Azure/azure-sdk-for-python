# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable  # pylint: disable=import-error
from typing import Any, Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from . import _config
from ._logger import get_logger
from ._tracing import TracingHelper

logger = get_logger()

# Pre-built health-check response to avoid per-request allocation.
_HEALTHY_BODY = b'{"status":"healthy"}'

# Server identity header value (name only — no version to avoid information disclosure).
_PLATFORM_SERVER_VALUE = "azure-ai-agentserver-core"

# Sentinel attribute name set on the console handler to prevent adding duplicates
# across multiple AgentHost instantiations.
_CONSOLE_HANDLER_ATTR = "_agentserver_console"


class _PlatformHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware that adds x-platform-server identity header to all responses."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def, override]
        response = await call_next(request)
        response.headers["x-platform-server"] = _PLATFORM_SERVER_VALUE
        return response


class AgentHost:
    """Agent server host framework with built-in protocol endpoints.

    Provides the protocol-agnostic infrastructure required by all Azure AI
    Hosted Agent containers:

    - Health probe (``GET /readiness``)
    - Graceful shutdown handling (SIGTERM, configurable timeout)
    - OpenTelemetry tracing with Azure Monitor and OTLP exporters
    - Hypercorn-based ASGI server with HTTP/1.1

    Protocol packages (e.g. ``azure-ai-agentserver-invocations``) plug into
    this host by calling :meth:`register_routes` to add their endpoints.

    Usage::

        from azure.ai.agentserver.core import AgentHost
        from azure.ai.agentserver.invocations import InvocationHandler

        server = AgentHost()
        invocations = InvocationHandler(server)

        @invocations.invoke_handler
        async def handle(request):
            return JSONResponse({"ok": True})

        server.run()

    :param application_insights_connection_string: Application Insights
        connection string for exporting traces and logs to Azure Monitor.
        When *None* (default) the ``APPLICATIONINSIGHTS_CONNECTION_STRING``
        env var is consulted.  Tracing is automatically enabled when a
        connection string is available.  Requires ``opentelemetry-sdk`` and
        ``azure-monitor-opentelemetry-exporter`` (included in the
        ``[tracing]`` extras group).
    :type application_insights_connection_string: Optional[str]
    :param graceful_shutdown_timeout: Seconds to wait for in-flight requests to
        complete after receiving SIGTERM / shutdown signal.  When *None* (default)
        the default is 30 seconds.  Set to ``0`` to disable the drain period.
    :type graceful_shutdown_timeout: Optional[int]
    :param log_level: Library log level (e.g. ``"DEBUG"``, ``"INFO"``).  When
        *None* (default) the default is ``"INFO"``.
    :type log_level: Optional[str]
    """

    def __init__(
        self,
        *,
        application_insights_connection_string: Optional[str] = None,
        graceful_shutdown_timeout: Optional[int] = None,
        log_level: Optional[str] = None,
    ) -> None:
        # Shutdown handler slot (server-level lifecycle) -------------------
        self._shutdown_fn: Optional[Callable[[], Awaitable[None]]] = None

        # Logging ----------------------------------------------------------
        resolved_level = _config.resolve_log_level(log_level)
        logger.setLevel(resolved_level)
        if not any(getattr(h, _CONSOLE_HANDLER_ATTR, False) for h in logger.handlers):
            _console = logging.StreamHandler()
            _console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            setattr(_console, _CONSOLE_HANDLER_ATTR, True)
            logger.addHandler(_console)

        # Tracing — enabled when App Insights or OTLP endpoint is configured
        _conn_str = _config.resolve_appinsights_connection_string(application_insights_connection_string)
        _otlp_endpoint = _config.resolve_otlp_endpoint()
        _tracing_on = bool(_conn_str or _otlp_endpoint)
        self._tracing: Optional[TracingHelper] = None
        if _tracing_on:
            try:
                self._tracing = TracingHelper(connection_string=_conn_str)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to initialize tracing; continuing without tracing.", exc_info=True)
                self._tracing = None

        # Timeouts ---------------------------------------------------------
        self._graceful_shutdown_timeout = _config.resolve_graceful_shutdown_timeout(
            graceful_shutdown_timeout
        )

        # Protocol routes (registered by protocol packages via register_routes)
        self._protocol_routes: list[Route] = []

        # App is built lazily on first access
        self._app: Optional[Starlette] = None

    # ------------------------------------------------------------------
    # ASGI app accessor (lazy build)
    # ------------------------------------------------------------------

    @property
    def app(self) -> Starlette:
        """Return the Starlette ASGI application, building it on first access.

        :return: The configured Starlette application.
        :rtype: Starlette
        """
        if self._app is None:
            self._build_app()
        return self._app  # type: ignore[return-value]  # _build_app sets _app

    # ------------------------------------------------------------------
    # Tracing accessor (for protocol packages)
    # ------------------------------------------------------------------

    @property
    def tracing(self) -> Optional[TracingHelper]:
        """Return the tracing helper, or *None* when tracing is disabled.

        :return: The tracing helper instance.
        :rtype: Optional[TracingHelper]
        """
        return self._tracing

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
    # Protocol route registration
    # ------------------------------------------------------------------

    def register_routes(self, routes: list[Route]) -> None:
        """Register additional routes from a protocol package.

        Invalidates the cached Starlette app so it will be rebuilt with the
        new routes on next access.  Called by protocol packages (e.g.
        ``InvocationHandler``) during setup.

        :param routes: List of Starlette Route objects to add.
        :type routes: list[Route]
        """
        if not routes:
            return
        if self._app is not None:
            logger.warning(
                "register_routes() called after the ASGI app was already built. "
                "The new routes will be included on the next app rebuild, but "
                "will NOT affect an already-running server."
            )
        self._protocol_routes.extend(routes)
        self._app = None  # invalidate — rebuilt lazily via .app property

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

    def run(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start the server synchronously.

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``"0.0.0.0"``
            (all interfaces).
        :type host: str
        :param port: Port to bind. Defaults to ``PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentHost starting on %s:%s", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        asyncio.run(_hypercorn_serve(self.app, config))  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    async def run_async(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start the server asynchronously (awaitable).

        Uses Hypercorn as the ASGI server, which supports HTTP/1.1 and HTTP/2.

        :param host: Network interface to bind. Defaults to ``"0.0.0.0"``
            (all interfaces).
        :type host: str
        :param port: Port to bind. Defaults to ``PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentHost starting on %s:%s (async)", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        await _hypercorn_serve(self.app, config)  # type: ignore[arg-type]  # Starlette is ASGI-compatible

    # ------------------------------------------------------------------
    # Private: app construction
    # ------------------------------------------------------------------

    def _build_app(self) -> None:
        """Construct the Starlette ASGI application with all routes."""

        @contextlib.asynccontextmanager
        async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:  # noqa: RUF029
            logger.info("AgentHost started")
            yield

            # --- SHUTDOWN: runs once when the server is stopping ---
            logger.info(
                "AgentHost shutting down (graceful timeout=%ss)",
                self._graceful_shutdown_timeout,
            )
            if self._graceful_shutdown_timeout == 0:
                logger.info("Graceful shutdown drain period disabled (timeout=0)")
            else:
                try:
                    await asyncio.wait_for(
                        self._dispatch_shutdown(),
                        timeout=self._graceful_shutdown_timeout,
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        "on_shutdown did not complete within %ss timeout",
                        self._graceful_shutdown_timeout,
                    )
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.exception("Error in on_shutdown")

        # All routes: protocol routes + health
        routes: list[Any] = list(self._protocol_routes)
        routes.append(
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        )

        self._app = Starlette(
            routes=routes,
            lifespan=_lifespan,
            middleware=[Middleware(_PlatformHeaderMiddleware)],
        )

    # ------------------------------------------------------------------
    # Health endpoint
    # ------------------------------------------------------------------

    async def _readiness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /readiness — readiness check endpoint.

        Return ``200 OK`` when the process is alive and ready to serve traffic.
        The hosting platform maps this to its readiness probe.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return Response(_HEALTHY_BODY, media_type="application/json")
