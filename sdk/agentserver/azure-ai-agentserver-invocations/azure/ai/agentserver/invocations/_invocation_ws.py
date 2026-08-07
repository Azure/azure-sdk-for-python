# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""invocations_ws (WebSocket) protocol support for ``InvocationAgentServerHost``.

Implements the ``@app.ws_handler`` decorator and the ``/invocations_ws``
route described in the ``invocations_ws`` protocol spec.  The SDK wraps
the user handler with:

* ``await websocket.accept()`` before the handler runs;
* WebSocket protocol-level Ping/Pong keep-alive (disabled by default;
  enable via the ``WS_KEEPALIVE_INTERVAL`` environment variable surfaced
  on ``AgentConfig.ws_ping_interval``) so idle connections can survive
  upstream proxy / load-balancer idle timeouts;
* a clean close on handler return (code 1000) or a 1011 close on uncaught
    handler exceptions, unless the application already sent a close frame;
* a structured close-event log line carrying
  ``azure.ai.agentserver.invocations_ws.session_id``,
  ``azure.ai.agentserver.invocations_ws.close_code``, and
  ``azure.ai.agentserver.invocations_ws.duration_ms``.
"""

import inspect
import logging
import time
import uuid
from collections.abc import Awaitable, Callable, MutableMapping
from typing import TYPE_CHECKING, Any, Optional

from opentelemetry import baggage as _otel_baggage, context as _otel_context
from opentelemetry.propagators.textmap import Getter
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
)

from ._constants import InvocationsWSConstants

# Type-checking only base so the mixin reads as an ``AgentServerHost`` to
# mypy / pyright (resolves ``self.config`` and ``self.router``) without
# coupling the runtime hierarchy.  At runtime the mixin is a plain
# ``object`` subclass — only the concrete
# ``InvocationAgentServerHost`` MRO actually inherits ``AgentServerHost``,
# which keeps the diamond out of the runtime class graph.
if TYPE_CHECKING:

    class _MixinBase(AgentServerHost):
        pass

else:

    class _MixinBase:
        pass


logger = logging.getLogger("azure.ai.agentserver")

_APPLICATION_CLOSE_CODE = "azure.ai.agentserver.invocations_ws.application_close_code"
_PEER_CLOSE_CODE = "azure.ai.agentserver.invocations_ws.peer_close_code"
_TERMINAL_CLOSE = "azure.ai.agentserver.invocations_ws.terminal_close"


def _record_terminal_close(websocket: WebSocket, code: int, source: str) -> None:
    websocket.scope.setdefault(_TERMINAL_CLOSE, (int(code), source))


def _selected_close(websocket: WebSocket, default_code: int) -> tuple[int, str]:
    selected = websocket.scope.get(_TERMINAL_CLOSE)
    if isinstance(selected, tuple) and len(selected) == 2:
        return int(selected[0]), str(selected[1])
    return default_code, "unknown"


class _WebSocketHeaderGetter(Getter[list[tuple[bytes, bytes]]]):
    """Read raw WebSocket upgrade headers with W3C multi-value semantics."""

    def get(self, carrier: list[tuple[bytes, bytes]], key: str) -> list[str] | None:
        normalized_key = key.lower().encode("latin-1")
        values = [value.decode("latin-1") for name, value in carrier if name.lower() == normalized_key]
        if not values:
            return None
        if key.lower() == "traceparent" and len(values) != 1:
            return None
        if key.lower() == "baggage":
            return [",".join(values)]
        return values

    def keys(self, carrier: list[tuple[bytes, bytes]]) -> list[str]:
        names: list[str] = []
        seen: set[str] = set()
        for name, _ in carrier:
            normalized_name = name.decode("latin-1").lower()
            if normalized_name not in seen:
                seen.add(normalized_name)
                names.append(normalized_name)
        return names


_WEBSOCKET_HEADER_GETTER = _WebSocketHeaderGetter()


def _extract_websocket_context(headers: list[tuple[bytes, bytes]]) -> _otel_context.Context:
    """Extract connection-lifetime W3C context from raw upgrade headers.

    :param headers: Raw ASGI WebSocket upgrade headers.
    :type headers: list[tuple[bytes, bytes]]
    :return: Extracted OpenTelemetry context.
    :rtype: ~opentelemetry.context.Context
    """
    from opentelemetry.propagate import extract  # pylint: disable=import-outside-toplevel

    context = extract(carrier=headers, getter=_WEBSOCKET_HEADER_GETTER)
    request_ids = _WEBSOCKET_HEADER_GETTER.get(headers, "x-request-id") or []
    request_id = next((value for value in request_ids if value), None)
    if request_id is not None:
        context = _otel_baggage.set_baggage("x_request_id", request_id, context=context)
    if len(request_ids) > 1:
        logger.debug("Ignoring duplicate WebSocket x-request-id values after the first non-empty value")
    return context


WSHandler = Callable[[WebSocket], Awaitable[None]]


class _WSHandlerMixin(_MixinBase):
    """Pure mixin that adds the ``@app.ws_handler`` decorator and ``/invocations_ws`` route.

    Designed to be mixed into a concrete
    :class:`~azure.ai.agentserver.core.AgentServerHost` subclass (e.g.
    :class:`InvocationAgentServerHost`) so the same host object exposes
    both ``POST /invocations`` (HTTP) and ``/invocations_ws`` (WebSocket)
    on the same Starlette application.  At runtime the mixin is a plain
    ``object`` subclass — host attributes (``self.config``,
    ``self.router``) are accessed via duck typing and are typed only for
    the static checkers (see ``_MixinBase``).
    """

    # Slots populated by __init__.
    _ws_fn: Optional[WSHandler]

    def _init_ws_state(self) -> None:
        """Initialize WS handler slots.

        The keep-alive interval lives on :class:`AgentConfig` and is
        wired into Hypercorn by
        :meth:`AgentServerHost._build_hypercorn_config` — there is no
        per-mixin state to populate here besides the handler slot.
        """
        self._ws_fn = None

    # ------------------------------------------------------------------
    # Public configuration accessor
    # ------------------------------------------------------------------

    @property
    def ws_ping_interval(self) -> float:
        """Configured WebSocket Ping interval in seconds (``0`` = disabled).

        Convenience alias for ``self.config.ws_ping_interval``.

        :return: The configured interval, or ``0`` when keep-alive is disabled.
        :rtype: float
        """
        return float(self.config.ws_ping_interval)

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
        """Register a first-match-reachable ``/invocations_ws`` route.

        Starlette's ``router.routes`` is a plain list and may be mutated
        between construction and first request. The exact SDK route therefore
        moves before the first catch-all route or Mount that would otherwise
        consume the WebSocket under Starlette's first-match routing.
        """
        from starlette.routing import Mount, WebSocketRoute  # pylint: disable=import-outside-toplevel

        def _join_route_path(prefix: str, path: str) -> str:
            if not prefix:
                return path or "/"
            if not path:
                return prefix or "/"
            return f"{prefix.rstrip('/')}/{path.lstrip('/')}"

        def _contains_nested_exact_route(routes: list[Any], prefix: str = "") -> bool:
            for nested_route in routes:
                if isinstance(nested_route, WebSocketRoute):
                    if _join_route_path(prefix, nested_route.path) == InvocationsWSConstants.ROUTE_PATH:
                        return True
                    continue
                nested_routes = getattr(nested_route, "routes", None)
                if not isinstance(nested_routes, list):
                    continue
                nested_prefix = prefix
                if isinstance(nested_route, Mount):
                    nested_prefix = _join_route_path(prefix, nested_route.path)
                    if nested_prefix == "/":
                        nested_prefix = ""
                if _contains_nested_exact_route(nested_routes, nested_prefix):
                    return True
            return False

        for route in self.router.routes:
            nested_routes = getattr(route, "routes", None)
            if isinstance(nested_routes, list) and _contains_nested_exact_route([route]):
                raise RuntimeError(
                    "InvocationAgentServerHost cannot own /invocations_ws because "
                    "a nested exact route is already registered"
                )

        sdk_route = None
        expected_endpoint = getattr(self._ws_endpoint, "__func__", self._ws_endpoint)
        for route in self.router.routes:
            if isinstance(route, WebSocketRoute) and getattr(route, "path", None) == InvocationsWSConstants.ROUTE_PATH:
                route_endpoint = getattr(route, "endpoint", None)
                if (
                    getattr(route_endpoint, "__self__", None) is not self
                    or getattr(route_endpoint, "__func__", route_endpoint) is not expected_endpoint
                ):
                    raise RuntimeError(
                        "InvocationAgentServerHost cannot own /invocations_ws because "
                        "the route is already registered"
                    )
                sdk_route = route

        if sdk_route is None:
            sdk_route = WebSocketRoute(
                InvocationsWSConstants.ROUTE_PATH,
                self._ws_endpoint,
                name="invocations_ws",
            )
        else:
            self.router.routes.remove(sdk_route)

        # This path is globally reserved by Invocations. Putting the exact route
        # first affects no unrelated path or HTTP scope, while guaranteeing that
        # custom matchers cannot conditionally shadow it based on headers,
        # subprotocols, or other runtime-only scope fields.
        self.router.routes.insert(0, sdk_route)

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
        raw_headers: list[tuple[bytes, bytes]] = websocket.scope.get("headers", [])
        token = _otel_context.attach(_extract_websocket_context(raw_headers))
        try:
            await self._run_ws_endpoint(websocket)
        finally:
            _otel_context.detach(token)

    async def _run_ws_endpoint(self, websocket: WebSocket) -> None:
        """Run one accepted WebSocket while the upgrade context is attached.

        :param websocket: Incoming Starlette WebSocket.
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

        # NOTE: when no ``@ws_handler`` is registered, the route itself is
        # not registered (see ``_ensure_ws_route_registered``), so this
        # endpoint is unreachable in that state — Starlette returns 404.

        # Accept the upgrade *before* invoking the user handler — per spec.
        try:
            await websocket.accept(headers=[(b"x-platform-server", self._build_server_version().encode("latin-1"))])
        except Exception as exc:  # pylint: disable=broad-exception-caught
            await self._finalize_session(
                websocket=None,
                session_id=session_id,
                start_ns=start_ns,
                close_code=InvocationsWSConstants.CLOSE_INTERNAL_ERROR,
                error_code="accept_failed",
            )
            logger.error(
                "WebSocket accept failed for session %s: %s",
                session_id,
                exc,
                exc_info=True,
            )
            return

        close_code: int = InvocationsWSConstants.CLOSE_NORMAL
        handler_exc: Optional[BaseException] = None
        original_send = websocket.send
        original_receive = websocket.receive

        async def _tracked_send(message: MutableMapping[str, Any]) -> None:
            application_close_code = (
                int(message.get("code", InvocationsWSConstants.CLOSE_NORMAL))
                if message.get("type") == "websocket.close"
                else None
            )
            state_before_send = websocket.application_state
            try:
                await original_send(message)
            except BaseException:
                if (
                    application_close_code is not None
                    and state_before_send == WebSocketState.CONNECTED
                    and websocket.application_state == WebSocketState.DISCONNECTED
                ):
                    # Starlette changes application_state immediately before
                    # invoking the underlying ASGI send. An exception or
                    # cancellation after that transition is therefore past an
                    # ambiguous transport commit boundary: preserve the first
                    # application-selected code instead of misreporting 1011.
                    websocket.scope.setdefault(_APPLICATION_CLOSE_CODE, application_close_code)
                    _record_terminal_close(websocket, application_close_code, "application_ambiguous")
                raise
            if application_close_code is not None:
                websocket.scope.setdefault(_APPLICATION_CLOSE_CODE, application_close_code)
                _record_terminal_close(websocket, application_close_code, "application")

        async def _tracked_receive() -> MutableMapping[str, Any]:
            message = await original_receive()
            if message.get("type") == "websocket.disconnect":
                peer_code = int(message.get("code") or InvocationsWSConstants.CLOSE_NORMAL)
                websocket.scope.setdefault(_PEER_CLOSE_CODE, peer_code)
                _record_terminal_close(websocket, peer_code, "peer")
            return message

        websocket.send = _tracked_send  # type: ignore[method-assign]
        websocket.receive = _tracked_receive  # type: ignore[method-assign]
        try:
            close_code, handler_exc = await self._invoke_user_handler(websocket, session_id)
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            # ``_invoke_user_handler`` catches ``Exception`` but not
            # ``BaseException`` (notably ``asyncio.CancelledError``).  Capture
            # the exception so the ``finally`` block below can record it,
            # then re-raise via ``finally`` so cancellation is never
            # swallowed.
            close_code, _ = _selected_close(websocket, InvocationsWSConstants.CLOSE_INTERNAL_ERROR)
            handler_exc = exc
            raise
        finally:
            # Always finalize — emits the close-event log line and
            # best-effort closes the socket — even when the handler
            # raised a ``BaseException`` like ``CancelledError``.
            error_code: Optional[str]
            if handler_exc is None:
                error_code = None
            elif isinstance(handler_exc, Exception):
                error_code = "internal_error"
            else:
                error_code = "cancelled"
            await self._finalize_session(
                websocket=websocket,
                session_id=session_id,
                start_ns=start_ns,
                close_code=close_code,
                close_code_source=_selected_close(websocket, close_code)[1],
                error_code=error_code,
            )

    async def _invoke_user_handler(
        self,
        websocket: WebSocket,
        session_id: str,
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
            return _selected_close(websocket, InvocationsWSConstants.CLOSE_NORMAL)[0], None
        except WebSocketDisconnect as exc:
            # Client (or proxy) closed first — surface their code, not 1011.
            return (
                int(exc.code) if exc.code else InvocationsWSConstants.CLOSE_NORMAL,
                None,
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error(
                "WebSocket handler raised for session %s: %s",
                session_id,
                exc,
                exc_info=True,
            )
            return _selected_close(websocket, InvocationsWSConstants.CLOSE_INTERNAL_ERROR)[0], exc

    async def _finalize_session(
        self,
        *,
        websocket: Optional[WebSocket],
        session_id: str,
        start_ns: int,
        close_code: int,
        close_code_source: str = "unknown",
        error_code: Optional[str],
    ) -> None:
        """Close the WS (best-effort) and emit the close-event log line.

        Called from both the success path and the accept-failure path.

        :keyword websocket: The connected WebSocket, or ``None`` when the
            ASGI ``accept`` itself failed (no socket to close).
        :paramtype websocket: Optional[~starlette.websockets.WebSocket]
        :keyword session_id: Per-connection session ID.
        :paramtype session_id: str
        :keyword start_ns: ``time.monotonic_ns()`` at connection start.
        :paramtype start_ns: int
        :keyword close_code: The RFC 6455 code to report to the client.
        :paramtype close_code: int
        :keyword close_code_source: First terminal source classification.
        :paramtype close_code_source: str
        :keyword error_code: Short error tag for the log line; ``None`` for success.
        :paramtype error_code: Optional[str]
        """
        duration_ms = (time.monotonic_ns() - start_ns) // 1_000_000

        # Best-effort clean close: only send a close frame if the
        # application hasn't already done so (e.g. the user handler
        # may have called ``websocket.close`` itself, or the client
        # may have disconnected).
        if websocket is not None and websocket.application_state != WebSocketState.DISCONNECTED:
            _record_terminal_close(websocket, close_code, "sdk")
            close_code, close_code_source = _selected_close(websocket, close_code)
            reason = "Internal server error" if close_code == InvocationsWSConstants.CLOSE_INTERNAL_ERROR else ""
            try:
                await websocket.close(code=close_code, reason=reason)
            except Exception:  # pylint: disable=broad-exception-caught
                # Connection already gone — nothing to recover here.
                logger.debug(
                    "Error closing WebSocket session %s",
                    session_id,
                    exc_info=True,
                )

        self._emit_close_event(
            session_id,
            close_code,
            duration_ms,
            close_code_source=close_code_source,
            error_code=error_code,
        )

    # ------------------------------------------------------------------
    # Close event
    # ------------------------------------------------------------------

    @staticmethod
    def _emit_close_event(
        session_id: str,
        close_code: int,
        duration_ms: int,
        *,
        close_code_source: str = "unknown",
        error_code: Optional[str] = None,
    ) -> None:
        """Emit the structured close-event log line for one WS connection.

        The log record carries ``azure.ai.agentserver.invocations_ws.session_id``,
        ``azure.ai.agentserver.invocations_ws.close_code``, and
        ``azure.ai.agentserver.invocations_ws.duration_ms`` via the standard
        ``logging`` ``extra`` dict — a structured-logging formatter or an
        OTel logging bridge can pick them up directly without parsing the
        message.  Exception details are deliberately NOT included here; they
        flow through ``logger.error(..., exc_info=True)`` in
        ``_invoke_user_handler`` instead.

        :param session_id: Per-connection session ID.
        :type session_id: str
        :param close_code: The RFC 6455 close code reported to the client.
        :type close_code: int
        :param duration_ms: Connection duration in milliseconds (monotonic).
        :type duration_ms: int
        :keyword error_code: Optional short error tag for the log record.
        :paramtype error_code: Optional[str]
        :keyword close_code_source: First terminal source classification.
        :paramtype close_code_source: str
        """
        extra: dict[str, Any] = {
            InvocationsWSConstants.ATTR_SPAN_SESSION_ID: session_id,
            InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE: close_code,
            InvocationsWSConstants.ATTR_SPAN_CLOSE_CODE_SOURCE: close_code_source,
            InvocationsWSConstants.ATTR_SPAN_DURATION_MS: duration_ms,
        }
        if error_code:
            extra[InvocationsWSConstants.ATTR_SPAN_ERROR_CODE] = error_code

        # NOTE: ``extra`` keys deliberately use dotted names
        # (``azure.ai.agentserver.invocations_ws.session_id`` etc.) so they
        # line up 1:1 with the keys defined in :class:`InvocationsWSConstants`.
        # The trade-off is that printf-style log formatters can't address
        # them directly — use a structured (JSON / OTel) formatter, or
        # access via ``LogRecord.__dict__["<key>"]`` for plain ``logging``.
        logger.info(
            "invocations_ws connection closed: session_id=%s code=%s duration_ms=%s",
            session_id,
            close_code,
            duration_ms,
            extra=extra,
        )
