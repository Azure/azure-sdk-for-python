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
# across multiple AgentServerHost instantiations.
_CONSOLE_HANDLER_ATTR = "_agentserver_console"


class _PlatformHeaderMiddleware(BaseHTTPMiddleware):
    """Middleware that adds x-platform-server identity header to all responses."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def, override]
        response = await call_next(request)
        response.headers["x-platform-server"] = _PLATFORM_SERVER_VALUE
        return response


class AgentServerHost(Starlette):
    """Agent server host framework for Azure AI Hosted Agent containers.

    A :class:`~starlette.applications.Starlette` subclass providing the
    protocol-agnostic infrastructure required by all hosted agent containers:

    - Health probe (``GET /readiness``)
    - Graceful shutdown handling (SIGTERM, configurable timeout)
    - OpenTelemetry tracing with Azure Monitor and OTLP exporters
    - Hypercorn-based ASGI server with HTTP/1.1

    Protocol packages subclass this host to add their own routes::

        from azure.ai.agentserver.invocations import InvocationAgentServerHost

        app = InvocationAgentServerHost()

        @app.invoke_handler
        async def handle(request):
            return JSONResponse({"ok": True})

        app.run()

    For multi-protocol agents, compose via cooperative inheritance::

        class MyHost(InvocationAgentServerHost, ResponsesAgentServerHost):
            pass

        app = MyHost()

    :param applicationinsights_connection_string: Application Insights
        connection string for exporting traces and logs to Azure Monitor.
        When *None* (default) the ``APPLICATIONINSIGHTS_CONNECTION_STRING``
        env var is consulted.  Tracing is automatically enabled when a
        connection string is available.
    :type applicationinsights_connection_string: Optional[str]
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
        applicationinsights_connection_string: Optional[str] = None,
        graceful_shutdown_timeout: Optional[int] = None,
        log_level: Optional[str] = None,
        routes: Optional[list[Route]] = None,
        **kwargs: Any,
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
        _conn_str = _config.resolve_appinsights_connection_string(applicationinsights_connection_string)
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

        # Build lifespan context manager
        @contextlib.asynccontextmanager
        async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:  # noqa: RUF029
            logger.info("AgentServerHost started")
            yield

            # --- SHUTDOWN: runs once when the server is stopping ---
            logger.info(
                "AgentServerHost shutting down (graceful timeout=%ss)",
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

        # Merge routes: subclass routes (if any) + health endpoint
        all_routes: list[Any] = list(routes or [])
        all_routes.append(
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        )

        # Initialize Starlette with combined routes, lifespan, and middleware
        super().__init__(
            routes=all_routes,
            lifespan=_lifespan,
            middleware=[Middleware(_PlatformHeaderMiddleware)],
            **kwargs,
        )

    # ------------------------------------------------------------------
    # Tracing accessor (for protocol subclasses)
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

        :param host: Network interface to bind. Defaults to ``"0.0.0.0"``.
        :type host: str
        :param port: Port to bind. Defaults to ``PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentServerHost starting on %s:%s", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        asyncio.run(_hypercorn_serve(self, config))  # type: ignore[arg-type]

    async def run_async(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Start the server asynchronously (awaitable).

        :param host: Network interface to bind. Defaults to ``"0.0.0.0"``.
        :type host: str
        :param port: Port to bind. Defaults to ``PORT`` env var or 8088.
        :type port: Optional[int]
        """
        from hypercorn.asyncio import serve as _hypercorn_serve

        resolved_port = _config.resolve_port(port)
        logger.info("AgentServerHost starting on %s:%s (async)", host, resolved_port)
        config = self._build_hypercorn_config(host, resolved_port)
        await _hypercorn_serve(self, config)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Health endpoint
    # ------------------------------------------------------------------

    async def _readiness_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        """GET /readiness — readiness check endpoint.

        :param request: The incoming Starlette request.
        :type request: Request
        :return: 200 OK response.
        :rtype: Response
        """
        return Response(_HEALTHY_BODY, media_type="application/json")
