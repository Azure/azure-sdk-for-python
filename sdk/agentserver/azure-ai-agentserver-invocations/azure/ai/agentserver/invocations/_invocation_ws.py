# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""invocations_ws (WebSocket) protocol support for ``InvocationAgentServerHost``.

Implements the ``@app.ws_handler`` decorator and the ``/invocations_ws``
route described in the ``invocations_ws`` protocol spec.  The SDK wraps
the user handler with:

* ``await websocket.accept()`` before the handler runs;
* WebSocket protocol-level Ping/Pong keep-alive (disabled by default;
  enable via the ``WS_KEEPALIVE_INTERVAL`` env var or the
  ``ws_ping_interval=`` constructor argument) so idle connections can
  survive Azure APIM / Azure Load Balancer's ~4-minute idle timeout;
* a clean close on handler return (code 1000) or a 1011 close on uncaught
  handler exceptions;
* a structured close-event log line and OTel span attributes carrying
  ``azure.ai.agentserver.invocations_ws.session_id``,
  ``azure.ai.agentserver.invocations_ws.close_code``, and
  ``azure.ai.agentserver.invocations_ws.duration_ms``.
"""

import inspect
import logging
import math
import os
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Optional

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
    end_span,
)

from ._constants import InvocationsWSConstants

# Type-checking only base so the mixin reads as an ``AgentServerHost`` to
# mypy / pyright (resolves ``self.config``, ``self.request_span``,
# ``self.router``) without coupling the runtime hierarchy.  At runtime the
# mixin is a plain ``object`` subclass — only the concrete
# ``InvocationAgentServerHost`` MRO actually inherits ``AgentServerHost``,
# which keeps the diamond out of the runtime class graph.
if TYPE_CHECKING:
    _MixinBase = AgentServerHost
else:
    _MixinBase = object

logger = logging.getLogger("azure.ai.agentserver")


WSHandler = Callable[[WebSocket], Awaitable[None]]


def _safe_set_attrs(span: Any, attrs: dict[str, Any]) -> None:
    """Best-effort ``span.set_attribute`` for a batch of attributes.

    :param span: The OTel span (or ``None`` when tracing is disabled).
    :type span: any
    :param attrs: Mapping of attribute keys to values.
    :type attrs: dict[str, any]
    """
    if span is None:
        return
    try:
        for key, value in attrs.items():
            span.set_attribute(key, value)
    except Exception:  # pylint: disable=broad-exception-caught
        logger.debug("Failed to set WS span attributes: %s", list(attrs.keys()), exc_info=True)


class _WSHandlerMixin(_MixinBase):
    """Pure mixin that adds the ``@app.ws_handler`` decorator and ``/invocations_ws`` route.

    Designed to be mixed into a concrete
    :class:`~azure.ai.agentserver.core.AgentServerHost` subclass (e.g.
    :class:`InvocationAgentServerHost`) so the same host object exposes
    both ``POST /invocations`` (HTTP) and ``/invocations_ws`` (WebSocket)
    on the same Starlette application.  At runtime the mixin is a plain
    ``object`` subclass — host attributes (``self.config``,
    ``self.request_span``, ``self.router``) are accessed via duck typing
    and are typed only for the static checkers (see ``_MixinBase``).
    """

    # Slots populated by __init__.
    _ws_fn: Optional[WSHandler]
    _ws_ping_interval: float

    def _init_ws_state(self, ws_ping_interval: Optional[float]) -> None:
        """Initialize WS handler slots.

        Resolution order for the keep-alive interval:

        1. Explicit *ws_ping_interval* constructor argument (when not ``None``).
        2. ``WS_KEEPALIVE_INTERVAL`` environment variable (auto-injected by
           AgentService into every hosted-agent container).
        3. Disabled (``0``) — no Ping/Pong frames are sent.

        ``0`` (from any source) disables keep-alive entirely.

        :param ws_ping_interval: Seconds between WS protocol Ping frames.
            ``None`` selects the env var or the default.
        :type ws_ping_interval: Optional[float]
        :raises ValueError: If the resolved value is negative, non-finite,
            or (for the env var) not parseable as a number.
        """
        self._ws_fn = None
        if ws_ping_interval is None:
            env_raw = os.environ.get(InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL)
            if env_raw is None or env_raw == "":
                resolved = 0.0
            else:
                try:
                    resolved = float(env_raw)
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid value for "
                        f"{InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL}: "
                        f"{env_raw!r} (expected a non-negative number)"
                    ) from exc
                if math.isnan(resolved) or math.isinf(resolved) or resolved < 0.0:
                    raise ValueError(
                        f"Invalid value for "
                        f"{InvocationsWSConstants.ENV_WS_KEEPALIVE_INTERVAL}: "
                        f"{env_raw!r} (expected a non-negative finite number)"
                    )
        else:
            try:
                resolved = float(ws_ping_interval)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"ws_ping_interval must be a number, got {ws_ping_interval!r}"
                ) from exc
            # Reject negative / NaN / inf — those are programming errors that
            # would silently mis-configure the keep-alive.
            if math.isnan(resolved) or math.isinf(resolved) or resolved < 0.0:
                raise ValueError(
                    f"ws_ping_interval must be a non-negative finite number, "
                    f"got {ws_ping_interval!r}"
                )
        self._ws_ping_interval = resolved

    # ------------------------------------------------------------------
    # Public configuration accessor
    # ------------------------------------------------------------------

    @property
    def ws_ping_interval(self) -> float:
        """Configured WebSocket Ping interval in seconds (``0`` = disabled).

        :return: The configured interval, or ``0`` when keep-alive is disabled.
        :rtype: float
        """
        return self._ws_ping_interval

    # ------------------------------------------------------------------
    # Decorator
    # ------------------------------------------------------------------

    def ws_handler(self, fn: WSHandler) -> WSHandler:
        """Register an async function as the ``/invocations_ws`` handler.

        The SDK calls ``await websocket.accept()`` before invoking *fn* and
        cleanly closes the connection on return (code 1000) or maps an
        uncaught exception to close code 1011.

        Usage::

            from starlette.websockets import WebSocket

            @app.ws_handler
            async def handle(websocket: WebSocket) -> None:
                async for msg in websocket.iter_text():
                    await websocket.send_text(msg)

        :param fn: An async function accepting a Starlette
            :class:`~starlette.websockets.WebSocket` and returning ``None``.
        :type fn: Callable[[WebSocket], Awaitable[None]]
        :return: The original function (unmodified).
        :rtype: Callable[[WebSocket], Awaitable[None]]
        :raises TypeError: If *fn* is not an ``async def`` function, or its
            signature cannot be invoked with a single positional argument
            (the WebSocket).
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"ws_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        # Validate signature at registration time (not at first request) so
        # 0-arg / 2-required-arg coroutine mistakes surface at import.
        try:
            sig = inspect.signature(fn)
            sig.bind(None)  # one positional placeholder for the WebSocket
        except TypeError as exc:
            raise TypeError(
                f"ws_handler signature must be invocable with a single "
                f"positional argument (the WebSocket); got "
                f"{fn.__qualname__}{inspect.signature(fn)}"
            ) from exc
        if self._ws_fn is not None:
            # Match the HTTP decorator's last-write-wins semantics, but log
            # so misconfigured apps that double-register a handler aren't
            # silently downgraded.
            logger.warning(
                "ws_handler overwriting previously registered handler %s with %s",
                getattr(self._ws_fn, "__qualname__", repr(self._ws_fn)),
                getattr(fn, "__qualname__", repr(fn)),
            )
        self._ws_fn = fn
        # Register the route lazily on first decoration so hosts without a
        # registered handler return HTTP 404 to a WebSocket upgrade rather than
        # accepting and immediately closing with code 1011.
        self._ensure_ws_route_registered()
        return fn

    def _ensure_ws_route_registered(self) -> None:
        """Append the ``/invocations_ws`` WebSocketRoute to the router (idempotent).

        Starlette's ``router.routes`` is a plain list and may be mutated
        between construction and first request, so deferring registration
        until ``@ws_handler`` is called is safe.
        """
        from starlette.routing import WebSocketRoute  # pylint: disable=import-outside-toplevel

        for route in self.router.routes:
            if isinstance(route, WebSocketRoute) and getattr(route, "path", None) == InvocationsWSConstants.ROUTE_PATH:
                return
        self.router.routes.append(
            WebSocketRoute(
                InvocationsWSConstants.ROUTE_PATH,
                self._ws_endpoint,
                name="invocations_ws",
            )
        )

    # ------------------------------------------------------------------
    # Endpoint
    # ------------------------------------------------------------------

    async def _ws_endpoint(self, websocket: WebSocket) -> None:
        """ASGI endpoint for ``/invocations_ws``.

        Wraps the user-registered handler with: accept, span lifecycle,
        graceful close on success, 1011 close on failure, and a structured
        close event log + span attributes.

        :param websocket: The incoming Starlette WebSocket.
        :type websocket: ~starlette.websockets.WebSocket
        """
        # Per-connection identifiers.  Honour the platform-injected
        # ``FOUNDRY_AGENT_SESSION_ID`` (surfaced via ``self.config.session_id``)
        # so HTTP and WebSocket transports on the same container report the
        # same session ID; fall back to a fresh UUID when the platform does
        # not inject one.  Matches the precedence used by the HTTP
        # ``POST /invocations`` endpoint (minus the query-param override,
        # which has no equivalent ergonomic on a long-lived WS connection).
        session_id = self.config.session_id or str(uuid.uuid4())
        start_ns = time.monotonic_ns()

        # Open the OTel span before accepting so any tracecontext header
        # the client sent is honoured for parenting child spans inside the
        # user handler.  ``end_on_exit=False`` so we can attach the close
        # code / duration before ending.
        span_ctx = self.request_span(
            websocket.headers,
            session_id,
            "websocket_session",
            operation_name="websocket_session",
            session_id=session_id,
            end_on_exit=False,
        )
        otel_span = span_ctx.__enter__()
        _safe_set_attrs(otel_span, {InvocationsWSConstants.ATTR_SPAN_SESSION_ID: session_id})

        # NOTE: when no ``@ws_handler`` is registered, the route itself is
        # not registered (see ``_ensure_ws_route_registered``), so this
        # endpoint is unreachable in that state — Starlette returns 404.

        # Accept the upgrade *before* invoking the user handler — per spec.
        try:
            await websocket.accept()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            await self._finalize_session(
                websocket=None,
                span_ctx=span_ctx,
                otel_span=otel_span,
                session_id=session_id,
                start_ns=start_ns,
                close_code=InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
                handler_exc=exc,
                error_code="accept_failed",
            )
            logger.error(
                "WebSocket accept failed for session %s: %s",
                session_id, exc, exc_info=True,
            )
            return

        close_code: int = InvocationsWSConstants.CLOSE_NORMAL
        handler_exc: Optional[BaseException] = None
        try:
            close_code, handler_exc = await self._invoke_user_handler(websocket, session_id)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            # ``_invoke_user_handler`` catches ``Exception`` but not
            # ``BaseException`` (notably ``asyncio.CancelledError``).  Capture
            # the exception so the ``finally`` block below can record it on
            # the span, then re-raise via ``finally`` so cancellation is
            # never swallowed.
            close_code = InvocationsWSConstants.CLOSE_INTERNAL_ERROR
            handler_exc = exc
            raise
        finally:
            # Always finalize \u2014 emits the close-event log line, ends the
            # span, and best-effort closes the socket \u2014 even when the
            # handler raised a ``BaseException`` like ``CancelledError``.
            error_code: Optional[str]
            if handler_exc is None:
                error_code = None
            elif isinstance(handler_exc, Exception):
                error_code = "internal_error"
            else:
                error_code = "cancelled"
            await self._finalize_session(
                websocket=websocket,
                span_ctx=span_ctx,
                otel_span=otel_span,
                session_id=session_id,
                start_ns=start_ns,
                close_code=close_code,
                handler_exc=handler_exc,
                error_code=error_code,
            )

    async def _invoke_user_handler(
        self, websocket: WebSocket, session_id: str,
    ) -> tuple[int, Optional[BaseException]]:
        """Run the registered user handler and classify the outcome.

        :param websocket: The accepted WebSocket to pass to the handler.
        :type websocket: ~starlette.websockets.WebSocket
        :param session_id: Per-connection session ID for diagnostic logs.
        :type session_id: str
        :return: ``(close_code, exception_or_None)``.  ``close_code`` is the
            RFC 6455 code that should be sent to the client; ``exception``
            is set only for an *unhandled* exception (so the caller can map
            it to span error events and a 1011 close).
        :rtype: tuple[int, Optional[BaseException]]
        :raises RuntimeError: If no handler is registered. The route is only
            registered after ``ws_handler`` is decorated, so reaching this
            method without a handler indicates a programming error in the
            SDK itself rather than a user misconfiguration.
        """
        ws_fn = self._ws_fn
        if ws_fn is None:
            raise RuntimeError("_invoke_user_handler called with no registered ws_handler")
        try:
            await ws_fn(websocket)
            return InvocationsWSConstants.CLOSE_NORMAL, None
        except WebSocketDisconnect as exc:
            # Client (or proxy) closed first — surface their code, not 1011.
            return (
                int(exc.code) if exc.code else InvocationsWSConstants.CLOSE_NORMAL,
                None,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "WebSocket handler raised for session %s: %s",
                session_id, exc, exc_info=True,
            )
            return InvocationsWSConstants.CLOSE_INTERNAL_ERROR, exc

    async def _finalize_session(
        self,
        *,
        websocket: Optional[WebSocket],
        span_ctx: Any,
        otel_span: Any,
        session_id: str,
        start_ns: int,
        close_code: int,
        handler_exc: Optional[BaseException],
        error_code: Optional[str],
    ) -> None:
        """Close the WS (best-effort), emit metrics, and end the span.

        Called from both the success path and the accept-failure path.

        :keyword websocket: The connected WebSocket, or ``None`` when the
            ASGI ``accept`` itself failed (no socket to close).
        :paramtype websocket: Optional[~starlette.websockets.WebSocket]
        :keyword span_ctx: The active ``request_span`` context manager.
        :paramtype span_ctx: any
        :keyword otel_span: The current OTel span (or ``None`` when tracing is off).
        :paramtype otel_span: any
        :keyword session_id: Per-connection session ID.
        :paramtype session_id: str
        :keyword start_ns: ``time.monotonic_ns()`` at connection start.
        :paramtype start_ns: int
        :keyword close_code: The RFC 6455 code to report to the client.
        :paramtype close_code: int
        :keyword handler_exc: Unhandled exception raised by the user handler,
            or ``None`` for a clean close.
        :paramtype handler_exc: Optional[BaseException]
        :keyword error_code: Short error tag for span / log; ``None`` for success.
        :paramtype error_code: Optional[str]
        """
        duration_ms = (time.monotonic_ns() - start_ns) // 1_000_000

        # Best-effort clean close: only send a close frame if the
        # application hasn't already done so (e.g. the user handler
        # may have called ``websocket.close`` itself, or the client
        # may have disconnected).
        if (
            websocket is not None
            and websocket.application_state != WebSocketState.DISCONNECTED
        ):
            reason = (
                "Internal server error"
                if close_code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR
                else ""
            )
            try:
                await websocket.close(code=close_code, reason=reason)
            except Exception:  # pylint: disable=broad-exception-caught
                # Connection already gone — nothing to recover here.
                logger.debug(
                    "Error closing WebSocket session %s", session_id, exc_info=True,
                )

        self._emit_close_event(
            otel_span,
            session_id,
            close_code,
            duration_ms,
            error_code=error_code,
            error_message=str(handler_exc) if handler_exc is not None else None,
        )

        # Always exit the context manager with ``(None, None, None)``:
        # OpenTelemetry's ``start_as_current_span`` records an exception
        # event whenever ``__exit__`` is given exception info, so passing
        # the user exception there *and* calling ``end_span(span, exc=...)``
        # would double-record.  We take ownership of error recording and
        # ending via ``end_span`` instead.
        try:
            span_ctx.__exit__(None, None, None)
        finally:
            end_span(otel_span, exc=handler_exc)

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    @staticmethod
    def _emit_close_event(
        otel_span: Any,
        session_id: str,
        close_code: int,
        duration_ms: int,
        *,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Record close-event span attributes and emit a structured log line.

        The log record carries the ``azure.ai.agentserver.invocations_ws.session_id``,
        ``azure.ai.agentserver.invocations_ws.close_code``, and
        ``azure.ai.agentserver.invocations_ws.duration_ms`` fields listed in the spec via the standard
        ``logging`` ``extra`` dict — a structured-logging formatter or an
        OTel logging bridge can pick them up directly without having to
        parse the message.

        :param otel_span: The connection span (or ``None`` when tracing is off).
        :type otel_span: any
        :param session_id: Per-connection session ID.
        :type session_id: str
        :param close_code: The RFC 6455 close code reported to the client.
        :type close_code: int
        :param duration_ms: Connection duration in milliseconds (monotonic).
        :type duration_ms: int
        :keyword error_code: Optional short error tag for span attribute.
        :paramtype error_code: Optional[str]
        :keyword error_message: Optional human-readable error message for
            span attribute (NOT included in the log line — exception details
            are logged separately by ``logger.error(..., exc_info=True)``).
        :paramtype error_message: Optional[str]
        """
        attrs: dict[str, Any] = {
            InvocationsWSConstants.ATTR_SPAN_SESSION_ID: session_id,
            InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE: close_code,
            InvocationsWSConstants.ATTR_SPAN_DURATION_MS: duration_ms,
        }
        if error_code:
            attrs[InvocationsWSConstants.ATTR_SPAN_ERROR_CODE] = error_code
        if error_message:
            attrs[InvocationsWSConstants.ATTR_SPAN_ERROR_MESSAGE] = error_message
        _safe_set_attrs(otel_span, attrs)

        # NOTE: ``extra`` keys deliberately use dotted names (``azure.ai.agentserver.invocations_ws.session_id``
        # etc.) so they line up 1:1 with the OTel span-attribute keys defined
        # in :class:`InvocationsWSConstants`.  This makes log<->trace
        # correlation trivial in OTel logging bridges.  The trade-off is that
        # ``%(azure.ai.agentserver.invocations_ws.session_id)s`` printf-style formatters can't address them
        # directly — use a structured formatter (JSON, OTel) or access via
        # ``LogRecord.__dict__["azure.ai.agentserver.invocations_ws.session_id"]`` if you need them in plain
        # ``logging`` output.
        logger.info(
            "invocations_ws connection closed: session_id=%s code=%s duration_ms=%s",
            session_id,
            close_code,
            duration_ms,
            extra={
                InvocationsWSConstants.ATTR_SPAN_SESSION_ID: session_id,
                InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE: close_code,
                InvocationsWSConstants.ATTR_SPAN_DURATION_MS: duration_ms,
            },
        )
