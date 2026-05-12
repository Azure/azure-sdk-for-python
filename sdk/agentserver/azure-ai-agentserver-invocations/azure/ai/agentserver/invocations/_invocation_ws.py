# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""invocations_ws (WebSocket) protocol support for ``InvocationAgentServerHost``.

Implements the ``@app.ws_handler`` decorator and the ``/invocations_ws``
route described in the ``invocations_ws`` protocol spec.  The SDK wraps
the user handler with:

* ``await websocket.accept()`` before the handler runs;
* WebSocket protocol-level Ping/Pong keep-alive (default 30 s) so idle
  connections survive Azure APIM / Azure Load Balancer's ~4-minute idle
  timeout;
* a clean close on handler return (code 1000) or a 1011 close on uncaught
  handler exceptions;
* a structured close-event log line and OTel span attributes carrying
  ``ws.session_id``, ``ws.close_code``, and ``ws.duration_ms``.
"""
from __future__ import annotations

import inspect
import logging
import math
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
    end_span,
    record_error,
)

from ._constants import InvocationsWSConstants

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


class _WSHandlerMixin(AgentServerHost):
    """Trait class that adds the ``@app.ws_handler`` decorator and ``/invocations_ws`` route.

    Inherits from :class:`~azure.ai.agentserver.core.AgentServerHost` so that
    cooperative ``super().__init__`` calls and host attribute access
    (``self.config``, ``self.request_span``) are resolved statically as well
    as at runtime.  Designed to be mixed into :class:`InvocationAgentServerHost`
    so the same host object exposes both ``POST /invocations`` (HTTP) and
    ``/invocations_ws`` (WebSocket) on the same Starlette application.

    Subclasses must append the route returned by :meth:`_build_ws_route` to
    their ``routes`` list before calling ``super().__init__``.
    """

    # Slots populated by __init__.
    _ws_fn: Optional[WSHandler]
    _ws_ping_interval: float

    def _init_ws_state(self, ws_ping_interval: Optional[float]) -> None:
        """Initialize WS handler slots.

        :param ws_ping_interval: Seconds between WS protocol Ping frames.
            ``None`` selects the default (30 s); ``0`` disables keep-alive.
        :type ws_ping_interval: Optional[float]
        :raises ValueError: If *ws_ping_interval* is negative or non-finite.
        """
        self._ws_fn = None
        if ws_ping_interval is None:
            resolved = InvocationsWSConstants.DEFAULT_PING_INTERVAL_S
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
        :raises TypeError: If *fn* is not an ``async def`` function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"ws_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._ws_fn = fn
        return fn

    # ------------------------------------------------------------------
    # Route factory (for cooperative __init__)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_ws_route(endpoint: Callable[[WebSocket], Awaitable[None]]) -> Any:
        """Return a :class:`~starlette.routing.WebSocketRoute` for ``/invocations_ws``.

        Imported lazily to avoid hard-coding the route type in the public
        module body and keep the import surface symmetric with the HTTP
        ``Route`` import in :mod:`._invocation`.

        :param endpoint: The async endpoint to wire to the route.
        :type endpoint: Callable[[WebSocket], Awaitable[None]]
        :return: A configured ``WebSocketRoute`` instance.
        :rtype: ~starlette.routing.WebSocketRoute
        """
        from starlette.routing import WebSocketRoute  # pylint: disable=import-outside-toplevel

        return WebSocketRoute(
            InvocationsWSConstants.ROUTE_PATH,
            endpoint,
            name="invocations_ws",
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
        # Per-connection identifiers.  Session ID is generated server-side;
        # the spec carries it in the close-event metric so an operator can
        # correlate logs/metrics for a given long-lived connection.
        session_id = str(uuid.uuid4())
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

        if self._ws_fn is None:
            await self._reject_no_handler(websocket, span_ctx, otel_span, session_id, start_ns)
            return

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

        close_code, handler_exc = await self._invoke_user_handler(websocket, session_id)
        await self._finalize_session(
            websocket=websocket,
            span_ctx=span_ctx,
            otel_span=otel_span,
            session_id=session_id,
            start_ns=start_ns,
            close_code=close_code,
            handler_exc=handler_exc,
            error_code="internal_error" if handler_exc is not None else None,
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
        """
        assert self._ws_fn is not None  # checked by caller
        try:
            await self._ws_fn(websocket)
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

    async def _reject_no_handler(
        self,
        websocket: WebSocket,
        span_ctx: Any,
        otel_span: Any,
        session_id: str,
        start_ns: int,
    ) -> None:
        """Refuse a WS upgrade when no ``@ws_handler`` is registered.

        :param websocket: The pending WebSocket awaiting upgrade.
        :type websocket: ~starlette.websockets.WebSocket
        :param span_ctx: The active ``request_span`` context manager.
        :type span_ctx: any
        :param otel_span: The current OTel span (or ``None``).
        :type otel_span: any
        :param session_id: Per-connection session ID.
        :type session_id: str
        :param start_ns: ``time.monotonic_ns()`` at connection start.
        :type start_ns: int
        """
        logger.error(
            "WebSocket connection on %s rejected: no @ws_handler registered",
            InvocationsWSConstants.ROUTE_PATH,
        )
        duration_ms = (time.monotonic_ns() - start_ns) // 1_000_000
        self._emit_close_event(
            otel_span,
            session_id,
            InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
            duration_ms,
            error_code="not_implemented",
            error_message="No ws_handler registered.",
        )
        try:
            span_ctx.__exit__(None, None, None)
        finally:
            end_span(otel_span)
        await websocket.close(
            code=InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
            reason="No ws_handler registered",
        )

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

        if handler_exc is not None:
            try:
                record_error(otel_span, handler_exc)
            finally:
                try:
                    span_ctx.__exit__(
                        type(handler_exc), handler_exc, handler_exc.__traceback__,
                    )
                finally:
                    end_span(otel_span)
        else:
            try:
                span_ctx.__exit__(None, None, None)
            finally:
                end_span(otel_span)

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

        The log record carries the ``ws.session_id``, ``ws.close_code``,
        and ``ws.duration_ms`` fields listed in the spec via the standard
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

        logger.info(
            "invocations_ws connection closed: session_id=%s code=%s duration_ms=%s",
            session_id,
            close_code,
            duration_ms,
            extra={
                "ws.session_id": session_id,
                "ws.close_code": close_code,
                "ws.duration_ms": duration_ms,
            },
        )
