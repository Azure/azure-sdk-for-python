# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import logging
import os
import signal
import urllib.parse
from collections.abc import (  # pylint: disable=import-error
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
)
from typing import Any, MutableMapping, Optional

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from . import _config, _tracing
from ._middleware import InboundRequestLoggingMiddleware
from ._request_id import RequestIdMiddleware as _RequestIdMiddleware
from ._server_version import build_server_version
from ._types import MiddlewareFactory, P, StreamContent
from ._version import VERSION as _CORE_VERSION

logger = logging.getLogger("azure.ai.agentserver")

# Pre-built health-check response to avoid per-request allocation.
_HEALTHY_BODY = b'{"status":"healthy"}'

_NOT_SET = "(not set)"


def _read_task_manager_shutdown_grace() -> float:
    """Return TaskManager shutdown grace in seconds (env-driven, default 25.0).

    Reads ``AGENTSERVER_SHUTDOWN_GRACE_SECONDS``. Defaults to 25.0 when
    unset. Allows tests (and operators) to keep shutdown fast when no
    long-running resilient handlers need to checkpoint — for example the
    conformance suite runs with a 1s grace so the in-process shutdown
    marker fires before the handler completes naturally.

    :return: Grace period in seconds (non-negative).
    :rtype: float
    """
    raw = os.environ.get("AGENTSERVER_SHUTDOWN_GRACE_SECONDS")
    if raw is None:
        return 25.0
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 25.0


def _mask_uri(uri: str) -> str:
    """Return only the scheme and host of a URI, hiding path/query/credentials.

    Returns ``"(not set)"`` for empty or whitespace-only values, or
    ``"(redacted)"`` when the URI cannot be parsed into scheme + host.

    :param uri: The URI to mask.
    :type uri: str
    :return: ``"scheme://host[:port]"``, ``"(not set)"``, or ``"(redacted)"``.
    :rtype: str
    """
    stripped = uri.strip() if uri else ""
    if not stripped:
        return _NOT_SET
    try:
        parsed = urllib.parse.urlparse(stripped)
        scheme = parsed.scheme or ""
        host = parsed.hostname or ""
        if scheme and host:
            port_suffix = f":{parsed.port}" if parsed.port else ""
            return f"{scheme}://{host}{port_suffix}"
        # Best-effort: if parsing fails to extract components, redact entirely
        return "(redacted)"
    except Exception:  # pylint: disable=broad-exception-caught
        return "(redacted)"


class _PlatformHeaderMiddleware:
    """Pure-ASGI middleware that adds ``x-platform-server`` header to responses.

    Unlike ``BaseHTTPMiddleware``, this passes the ``receive`` callable
    through to the inner application untouched, which preserves
    ``request.is_disconnected()`` behaviour required for client disconnect detection.
    """

    def __init__(self, app: ASGIApp, *, get_server_version: Callable[[], str]) -> None:
        self.app = app
        self._get_server_version = get_server_version

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def _send_with_header(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-platform-server", self._get_server_version().encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, _send_with_header)


# Sentinel for default access_log (use module logger)
_SENTINEL_ACCESS_LOG = object()


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
    :param access_log: Logger for HTTP access logs, or *None* to disable.
        Defaults to the library logger (``azure.ai.agentserver``).
    :type access_log: Optional[logging.Logger]
    :param access_log_format: Hypercorn access-log format string.
        Supports ``%(h)s`` (remote addr), ``%(r)s`` (request line),
        ``%(s)s`` (status), ``%(b)s`` (body size), ``%(D)s`` (duration μs),
        ``%({header}i)s`` (request header), ``%({header}o)s`` (response header).
        Defaults to ``%(h)s "%(r)s" %(s)s %(b)s %(D)sμs``.
    :type access_log_format: Optional[str]
    :param configure_observability: Callable that sets up console logging,
        tracing, and OTel export.  Defaults to
        :func:`~._tracing.configure_observability` which attaches a console
        handler to the root logger and configures Azure Monitor / OTLP
        export.  Pass a custom callable to override the setup, or ``None``
        to skip all SDK-managed observability configuration.
    :type configure_observability: Optional[Callable[..., None]]
    """

    _DEFAULT_ACCESS_LOG_FORMAT = '%(h)s "%(r)s" %(s)s %(b)s %(D)sμs'

    def __init__(  # pylint: disable=too-many-statements
        self,
        *,
        applicationinsights_connection_string: Optional[str] = None,
        graceful_shutdown_timeout: Optional[int] = None,
        log_level: Optional[str] = None,
        access_log: Optional[logging.Logger] = _SENTINEL_ACCESS_LOG,  # type: ignore[assignment]
        access_log_format: Optional[str] = None,
        configure_observability: Optional[Callable[..., None]] = _tracing.configure_observability,
        routes: Optional[list[Route]] = None,
        **kwargs: Any,
    ) -> None:
        # Shutdown handler slot (server-level lifecycle) -------------------
        self._shutdown_fn: Optional[Callable[[], Awaitable[None]]] = None
        #  Pre-shutdown callbacks invoked SYNCHRONOUSLY from the
        # SIGTERM signal handler — before Hypercorn's graceful drain
        # begins. Used by responses to set ``_shutdown_requested`` early so
        # foreground handlers' disconnect-poll loop sees the shutdown
        # signal BEFORE Hypercorn waits for in-flight requests to complete.
        # Callbacks must be non-blocking and thread-safe (they run in the
        # signal handler, not on the event loop).
        self._pre_shutdown_callbacks: list[Callable[[], None]] = []

        # Server version segments for the x-platform-server header.
        # Protocol packages call register_server_version() to add their
        # own portion; the middleware joins them at response time.
        self._server_version_segments: list[str] = []
        self.register_server_version(build_server_version("azure-ai-agentserver-core", _CORE_VERSION))

        # Resolved configuration (accessible as self.config)
        self.config: _config.AgentConfig = _config.AgentConfig.from_env()

        # Observability (logging + tracing) --------------------------------
        _conn_str = applicationinsights_connection_string or self.config.appinsights_connection_string
        _env_val = os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")
        _sensitive_data = _env_val.lower() not in ("false", "0")
        if configure_observability is not None:
            try:
                configure_observability(
                    connection_string=_conn_str,
                    log_level=log_level,
                    enable_sensitive_data=_sensitive_data,
                )
            except ValueError:
                raise  # invalid log_level etc. — user should fix their config
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to initialize observability; continuing without it.", exc_info=True)

        # Access logging ---------------------------------------------------
        self._access_log: Optional[logging.Logger] = logger if access_log is _SENTINEL_ACCESS_LOG else access_log
        self._access_log_format: str = access_log_format or self._DEFAULT_ACCESS_LOG_FORMAT

        # Timeouts ---------------------------------------------------------
        self._graceful_shutdown_timeout = _config.resolve_graceful_shutdown_timeout(graceful_shutdown_timeout)

        # Build lifespan context manager
        @contextlib.asynccontextmanager
        async def _lifespan(_app: Starlette) -> AsyncGenerator[None, None]:  # noqa: RUF029
            logger.info("AgentServerHost started")

            # --- Startup configuration logging ---
            cfg = self.config
            logger.info(
                "Platform environment: is_hosted=%s, agent_name=%s, agent_version=%s, "
                "port=%s, session_id=%s, sse_keepalive_interval=%s, ws_ping_interval=%s",
                cfg.is_hosted,
                cfg.agent_name or _NOT_SET,
                cfg.agent_version or _NOT_SET,
                cfg.port,
                cfg.session_id or _NOT_SET,
                cfg.sse_keepalive_interval if cfg.sse_keepalive_interval > 0 else "disabled",
                f"{cfg.ws_ping_interval}s" if cfg.ws_ping_interval > 0 else "disabled",
            )
            logger.info(
                "Connectivity: project_endpoint=%s, otlp_endpoint=%s, appinsights_configured=%s",
                _mask_uri(cfg.project_endpoint),
                _mask_uri(cfg.otlp_endpoint),
                bool(cfg.appinsights_connection_string),
            )
            protocols = ", ".join(self._server_version_segments) if self._server_version_segments else _NOT_SET
            logger.info(
                "Host options: shutdown_timeout=%ss, protocols=%s",
                self._graceful_shutdown_timeout,
                protocols,
            )

            # --- Resilient task manager auto-initialization ---
            task_manager = None
            try:
                from .tasks._manager import (  # pylint: disable=import-outside-toplevel
                    TaskManager,
                    set_task_manager,
                )

                task_manager = TaskManager(
                    config=cfg,
                    shutdown_event=asyncio.Event(),
                    shutdown_grace_seconds=_read_task_manager_shutdown_grace(),
                )
                set_task_manager(task_manager)
                await task_manager.startup()
                logger.info("TaskManager initialized automatically")
            except ImportError:
                pass  # resilient module not available
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning("Failed to initialize TaskManager", exc_info=True)

            yield

            # --- SHUTDOWN: runs once when the server is stopping ---
            logger.info(
                "AgentServerHost shutting down (graceful timeout=%ss)",
                self._graceful_shutdown_timeout,
            )

            #  Run on_shutdown FIRST so the responses layer's
            # ``handle_shutdown`` can set ``_shutdown_requested`` and signal
            # cancellation BEFORE the TaskManager waits its grace period.
            # Without this, Row 3 (foreground) handlers can race against
            # Hypercorn's client-connection close — the disconnect-poll loop
            # stamps ``CLIENT_CANCELLED`` instead of ``SHUTTING_DOWN`` and
            # B11 emits a cancelled terminal instead of failed.
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
                    logger.warning("Error in on_shutdown", exc_info=True)

            # Shutdown task manager AFTER on_shutdown so resilient handlers
            # have had time to checkpoint via the responses layer's
            # ``handle_shutdown``.
            if task_manager is not None:
                try:
                    await task_manager.shutdown()
                    from .tasks._manager import (  # pylint: disable=import-outside-toplevel
                        set_task_manager as _clear_manager,
                    )

                    _clear_manager(None)
                    logger.info("TaskManager shut down")
                except Exception:  # pylint: disable=broad-exception-caught
                    logger.warning("Error shutting down TaskManager", exc_info=True)

        # Merge routes: subclass routes (if any) + health endpoint
        all_routes: list[Any] = list(routes or [])
        all_routes.append(
            Route("/readiness", self._readiness_endpoint, methods=["GET"], name="readiness"),
        )

        # Initialize Starlette with combined routes, lifespan, and middleware
        super().__init__(
            routes=all_routes,
            lifespan=_lifespan,
            middleware=[
                Middleware(InboundRequestLoggingMiddleware),  # type: ignore[arg-type]
                Middleware(  # type: ignore[arg-type]
                    _PlatformHeaderMiddleware,
                    get_server_version=self._build_server_version,
                ),
                Middleware(_RequestIdMiddleware),  # type: ignore[arg-type]
            ],
            **kwargs,
        )

        # Extract W3C trace context (traceparent/tracestate) and baggage
        # from incoming HTTP requests and WebSocket connections so that any
        # spans created downstream (e.g. by MAF / agent-framework) are
        # children of the caller's trace.
        # We do NOT create a SERVER span ourselves — we only propagate context.
        from azure.ai.agentserver.core._tracing import TraceContextMiddleware  # pylint: disable=import-outside-toplevel

        self.add_middleware(TraceContextMiddleware)

    def add_middleware(
        self,
        middleware_class: MiddlewareFactory[P],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """Add middleware to the host.

        This exposes Starlette's middleware extension point without leaking
        Starlette's private type aliases in this package's public API.

        :param middleware_class: Middleware class or factory to add.
        :type middleware_class: MiddlewareFactory
        :param args: Positional arguments forwarded to the middleware.
        :type args: Any
        """
        super().add_middleware(middleware_class, *args, **kwargs)

    # ------------------------------------------------------------------
    # Server version (x-platform-server header)
    # ------------------------------------------------------------------

    def register_server_version(self, version_segment: str) -> None:
        """Register a version segment for the ``x-platform-server`` header.

        Protocol packages (e.g. responses, invocations) call this in their
        ``__init__`` to add their own portion.  Handler developers can also
        call it to append a custom version string.  Duplicates are ignored.

        Use :func:`~azure.ai.agentserver.core.build_server_version` to
        build a standard segment::

            from azure.ai.agentserver.core import build_server_version

            app.register_server_version(
                build_server_version("my-library", "2.0.0")
            )

        :param version_segment: The version string to register.
        :type version_segment: str
        :raises ValueError: If *version_segment* is empty or whitespace-only.
        """
        if not version_segment or not version_segment.strip():
            raise ValueError("Version segment must not be empty.")
        normalized = version_segment.strip()
        if normalized not in self._server_version_segments:
            self._server_version_segments.append(normalized)

    def _build_server_version(self) -> str:
        """Join all registered segments into the header value.

        :return: The concatenated server version string.
        :rtype: str
        """
        return " ".join(self._server_version_segments)

    # ------------------------------------------------------------------
    # Tracing (for protocol subclasses)
    # ------------------------------------------------------------------

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

    def register_pre_shutdown_callback(self, fn: Callable[[], None]) -> None:
        """Register a synchronous callback to run on SIGTERM signal receipt.

        Callbacks run from inside the SIGTERM signal handler,
        BEFORE Hypercorn begins its graceful drain. Use this to
        set asyncio events that long-running request handlers observe via
        their cancellation-polling loops, so they can return before
        Hypercorn waits the full ``graceful_shutdown_timeout`` for the
        request to complete.

        Callbacks MUST be non-blocking and signal-safe — they execute
        synchronously on the main thread inside the signal handler. The
        typical pattern is::

            shutdown_event = asyncio.Event()
            app.register_pre_shutdown_callback(shutdown_event.set)

        Note: ``asyncio.Event.set()`` is safe to call from a signal
        handler when the event loop is running on the same thread.

        :param fn: A synchronous, non-blocking callable.
        :type fn: Callable[[], None]
        """
        self._pre_shutdown_callbacks.append(fn)

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
        # Spec requires HTTP/1.1 only — disable HTTP/2
        config.h2_max_concurrent_streams = 0
        # WebSocket Ping/Pong keep-alive (RFC 6455 opcodes 0x9/0xA).
        # ``0`` (disabled) maps to Hypercorn's ``None`` sentinel; any
        # positive value is sent verbatim to Hypercorn.
        ws_ping = self.config.ws_ping_interval
        config.websocket_ping_interval = ws_ping if ws_ping > 0 else None  # type: ignore[attr-defined]
        # Access logging
        if self._access_log is not None:
            config.accesslog = self._access_log  # type: ignore[assignment]
            config.access_log_format = self._access_log_format
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

        async def _serve_with_shutdown_trigger() -> None:
            """Wrap hypercorn.serve with a custom shutdown_trigger.

             When Hypercorn's default ``shutdown_trigger=None``
            is used, Hypercorn registers its own SIGTERM/SIGINT handler
            via ``loop.add_signal_handler`` and our ``signal.signal``
            handler is overridden. We register our own
            ``loop.add_signal_handler`` here and pass the resulting wait
            as ``shutdown_trigger`` so Hypercorn uses our event — and we
            get to fire pre-shutdown callbacks synchronously on signal
            receipt, before Hypercorn begins its graceful drain.
            """
            loop = asyncio.get_event_loop()
            signal_event = asyncio.Event()

            def _on_signal() -> None:
                # Run pre-shutdown callbacks BEFORE setting the event so
                # they fire before Hypercorn begins draining connections.
                for cb in self._pre_shutdown_callbacks:
                    try:
                        cb()
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.warning("Pre-shutdown callback raised", exc_info=True)
                signal_event.set()

            for signal_name in ("SIGINT", "SIGTERM", "SIGBREAK"):
                if hasattr(signal, signal_name):
                    try:
                        loop.add_signal_handler(getattr(signal, signal_name), _on_signal)
                    except NotImplementedError:
                        # Windows fallback — install via signal.signal directly.
                        signal.signal(getattr(signal, signal_name), lambda *_: _on_signal())

            await _hypercorn_serve(self, config, shutdown_trigger=signal_event.wait)  # type: ignore[arg-type]

        asyncio.run(_serve_with_shutdown_trigger())

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

    # ------------------------------------------------------------------
    # Streaming utilities
    # ------------------------------------------------------------------

    @staticmethod
    async def sse_keepalive_stream(
        iterator: AsyncIterable[StreamContent],
        interval: int,
    ) -> AsyncIterator[StreamContent]:
        """Interleave SSE keep-alive comment frames into a streaming body.

        Emits ``b": keep-alive\\n\\n"`` whenever the upstream iterator has not
        produced a chunk within *interval* seconds.  This prevents
        proxies/load-balancers from closing idle connections.

        :param iterator: The async iterable to wrap.
        :type iterator: AsyncIterable[~azure.ai.agentserver.core.StreamContent]
        :param interval: Seconds between keep-alive frames. Must be > 0.
        :type interval: int
        :return: An async iterator with interleaved keep-alive frames.
        :rtype: AsyncIterator[~azure.ai.agentserver.core.StreamContent]
        """
        ait = iterator.__aiter__()
        # Reuse the same __anext__ task across timeouts to avoid cancelling
        # the upstream iterator when wait_for expires.
        pending: Optional[asyncio.Task[StreamContent]] = None
        while True:
            if pending is None:
                pending = asyncio.ensure_future(ait.__anext__())
            try:
                chunk = await asyncio.wait_for(asyncio.shield(pending), timeout=interval)
                pending = None  # consumed — create new task next iteration
                yield chunk
            except asyncio.TimeoutError:
                yield b": keep-alive\n\n"
            except StopAsyncIteration:
                break
