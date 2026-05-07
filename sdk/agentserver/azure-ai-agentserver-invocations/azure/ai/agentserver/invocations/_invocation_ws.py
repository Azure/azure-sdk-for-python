# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""WebSocket invocation protocol host for Azure AI Hosted Agents.

Provides the invocation protocol over WebSocket long connections
as a :class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""
import asyncio  # pylint: disable=do-not-import-asyncio
import contextlib
import inspect
import json
import logging
import os
import re
import uuid
from collections.abc import Callable  # pylint: disable=import-error
from dataclasses import dataclass
from typing import Any, Optional

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.core import (  # pylint: disable=no-name-in-module
    AgentServerHost,
    create_error_response,
    end_span,
    record_error,
)

from ._ws_constants import InvocationWSConstants

logger = logging.getLogger("azure.ai.agentserver")

# Maximum length and allowed characters for user-provided IDs (defense in depth).
_MAX_ID_LENGTH = 256
_VALID_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")


def _sanitize_id(value: str, fallback: str) -> str:
    """Validate a user-provided ID string.

    Returns *value* unchanged when it passes validation, otherwise returns
    *fallback*.  This prevents excessively long or malformed IDs from
    propagating into span attributes and log messages.

    :param value: The raw ID from a message field.
    :type value: str
    :param fallback: A safe fallback value (typically a generated UUID).
    :type fallback: str
    :return: The validated ID or the fallback.
    :rtype: str
    """
    if not value or len(value) > _MAX_ID_LENGTH or not _VALID_ID_RE.match(value):
        return fallback
    return value


@dataclass
class InvocationWSContext:
    """Contextual information for a WebSocket invocation request.

    Passed to handler functions registered via :meth:`ws_invoke_handler`,
    :meth:`ws_get_invocation_handler`, and :meth:`ws_cancel_invocation_handler`.

    :param invocation_id: Unique identifier for this invocation.
    :type invocation_id: str
    :param session_id: Session identifier for this invocation.
    :type session_id: str
    """

    invocation_id: str
    session_id: str


class InvocationWSError(Exception):
    """Raised by handlers to signal a domain-specific error.

    :param code: Machine-readable error code.
    :type code: str
    :param message: Human-readable error message.
    :type message: str
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class InvocationWSAgentServerHost(AgentServerHost):
    """WebSocket invocation protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    a WebSocket endpoint for the ``invocations_ws`` protocol.  Use the decorator
    methods to wire handler functions to messages.

    WebSocket endpoint: ``/invocations_ws/ws``

    **Client → Server messages** (JSON text frames)::

        {"action": "invoke", "invocation_id": "opt", "session_id": "opt", "payload": {...}}
        {"action": "get_invocation", "invocation_id": "required"}
        {"action": "cancel_invocation", "invocation_id": "required"}

    **Server → Client messages** (JSON text frames)::

        {"type": "result", "invocation_id": "...", "session_id": "...", "payload": {...}}
        {"type": "stream_chunk", "invocation_id": "...", "session_id": "...", "payload": {...}}
        {"type": "stream_end", "invocation_id": "...", "session_id": "..."}
        {"type": "error", "invocation_id": "...", "error": {"code": "...", "message": "..."}}

    Usage::

        from azure.ai.agentserver.invocations import InvocationWSAgentServerHost, InvocationWSContext

        app = InvocationWSAgentServerHost()

        @app.ws_invoke_handler
        async def handle(payload, context):
            return {"reply": "hello"}

        app.run()

    :param openapi_spec: Optional OpenAPI spec dict.  When provided, the spec
        is served at ``GET /invocations_ws/docs/openapi.json``.
    :type openapi_spec: Optional[dict[str, Any]]
    :param ws_ping_interval: Interval in seconds between keep-alive ping
        frames sent to each connected WebSocket client.  Keeps the
        connection alive through Azure APIM / Load Balancer which silently
        drop idle connections after ~4 minutes.  Set to ``0`` to disable.
        Defaults to ``30``.
    :type ws_ping_interval: Optional[int]
    """

    def __init__(
        self,
        *,
        openapi_spec: Optional[dict[str, Any]] = None,
        ws_ping_interval: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        self._ws_invoke_fn: Optional[Callable] = None
        self._ws_get_invocation_fn: Optional[Callable] = None
        self._ws_cancel_invocation_fn: Optional[Callable] = None
        self._ws_openapi_spec = openapi_spec
        self._ws_ping_interval: int = (
            ws_ping_interval
            if ws_ping_interval is not None
            else InvocationWSConstants.DEFAULT_WS_PING_INTERVAL
        )

        # Build WebSocket routes
        ws_routes: list[Any] = [
            Route(
                "/invocations_ws/docs/openapi.json",
                self._ws_get_openapi_spec_endpoint,
                methods=["GET"],
                name="ws_get_openapi_spec",
            ),
            WebSocketRoute(
                "/invocations_ws/ws",
                self._websocket_endpoint,
                name="invocations_ws",
            ),
        ]

        # Merge with any routes from sibling mixins via cooperative init
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + ws_routes, **kwargs)

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def ws_invoke_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the WebSocket invoke handler.

        The handler receives ``(payload: dict, context: InvocationWSContext)``
        and may be:

        - An async function returning a ``dict`` (non-streaming).
        - An async generator yielding ``dict`` chunks (streaming).

        Usage::

            @app.ws_invoke_handler
            async def handle(payload, context):
                return {"reply": f"echo: {payload}"}

            # Streaming variant:
            @app.ws_invoke_handler
            async def handle(payload, context):
                for token in tokens:
                    yield {"token": token}

        :param fn: Async function or async generator function.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        :raises TypeError: If *fn* is not async.
        """
        if not (inspect.iscoroutinefunction(fn) or inspect.isasyncgenfunction(fn)):
            raise TypeError(
                f"ws_invoke_handler expects an async function or async generator, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._ws_invoke_fn = fn
        return fn

    def ws_get_invocation_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the WebSocket get-invocation handler.

        The handler receives ``(context: InvocationWSContext)`` and returns
        a ``dict``.

        :param fn: Async function.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"ws_get_invocation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._ws_get_invocation_fn = fn
        return fn

    def ws_cancel_invocation_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the WebSocket cancel-invocation handler.

        The handler receives ``(context: InvocationWSContext)`` and returns
        a ``dict``.

        :param fn: Async function.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"ws_cancel_invocation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._ws_cancel_invocation_fn = fn
        return fn

    # ------------------------------------------------------------------
    # OpenAPI spec (HTTP endpoint — documentation)
    # ------------------------------------------------------------------

    def get_ws_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the stored WebSocket OpenAPI spec, or None."""
        return self._ws_openapi_spec

    async def _ws_get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        spec = self.get_ws_openapi_spec()
        if spec is None:
            return create_error_response("not_found", "No OpenAPI spec registered", status_code=404)
        return JSONResponse(spec)

    # ------------------------------------------------------------------
    # Span attribute helper
    # ------------------------------------------------------------------

    @staticmethod
    def _ws_safe_set_attrs(span: Any, attrs: dict[str, str]) -> None:
        if span is None:
            return
        try:
            for key, value in attrs.items():
                span.set_attribute(key, value)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to set span attributes: %s", list(attrs.keys()), exc_info=True)

    # ------------------------------------------------------------------
    # Span context manager
    # ------------------------------------------------------------------

    def _ws_request_span(
        self,
        headers: Any,
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> Any:
        """Create a request span — returns a no-op context manager when tracing is off.

        :param headers: HTTP/WebSocket handshake headers.
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
        return self.request_span(
            headers, invocation_id, span_operation,
            operation_name=operation_name, session_id=session_id,
            end_on_exit=False,
        )

    def _ws_simple_request_span(
        self,
        headers: Any,
        invocation_id: str,
        span_operation: str,
        session_id: str = "",
    ) -> Any:
        """Create a request span that auto-ends on exit.

        Used for get/cancel operations that don't need manual span lifecycle.

        :param headers: HTTP/WebSocket handshake headers.
        :type headers: any
        :param invocation_id: The request/invocation ID.
        :type invocation_id: str
        :param span_operation: Span operation name.
        :type span_operation: str
        :param session_id: Session ID (empty string if absent).
        :type session_id: str
        :return: Context manager yielding the OTel span or *None*.
        :rtype: any
        """
        return self.request_span(
            headers, invocation_id, span_operation,
            session_id=session_id,
        )

    # ------------------------------------------------------------------
    # WebSocket endpoint
    # ------------------------------------------------------------------

    async def _ws_ping_loop(self, websocket: WebSocket) -> None:
        """Send periodic ping frames to keep the WebSocket alive.

        Azure APIM and Azure Load Balancer silently kill idle WebSocket
        connections after ~4 minutes.  This background task sends a
        lightweight ``{"type": "ping"}`` message at a configurable
        interval (default 30 s) so the connection is never considered idle.

        :param websocket: The WebSocket connection to keep alive.
        :type websocket: ~starlette.websockets.WebSocket
        """
        try:
            while True:
                await asyncio.sleep(self._ws_ping_interval)
                await websocket.send_json({"type": InvocationWSConstants.MSG_TYPE_PING})
        except (WebSocketDisconnect, Exception):  # pylint: disable=broad-exception-caught
            # Connection closed or errored — let the task exit silently.
            pass

    async def _websocket_endpoint(self, websocket: WebSocket) -> None:
        """Main WebSocket endpoint for the invocations_ws protocol.

        Accepts a WebSocket connection and processes JSON messages in a loop.
        Each message must contain an ``action`` field.

        A background keep-alive task sends periodic ping messages to prevent
        Azure APIM / Load Balancer from dropping idle connections.

        :param websocket: The WebSocket connection.
        :type websocket: ~starlette.websockets.WebSocket
        """
        await websocket.accept()

        # Start keep-alive ping task (disabled when interval is 0).
        ping_task: Optional[asyncio.Task] = None
        if self._ws_ping_interval > 0:
            ping_task = asyncio.create_task(self._ws_ping_loop(websocket))

        try:
            while True:
                raw = await websocket.receive_text()

                try:
                    message = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    await websocket.send_json({
                        "type": InvocationWSConstants.MSG_TYPE_ERROR,
                        "error": {"code": "invalid_json", "message": "Invalid JSON message"},
                    })
                    continue

                if not isinstance(message, dict):
                    await websocket.send_json({
                        "type": InvocationWSConstants.MSG_TYPE_ERROR,
                        "error": {"code": "invalid_message", "message": "Message must be a JSON object"},
                    })
                    continue

                action = message.get("action")
                if action == InvocationWSConstants.ACTION_INVOKE:
                    await self._handle_ws_invoke(websocket, message)
                elif action == InvocationWSConstants.ACTION_GET_INVOCATION:
                    await self._handle_ws_get_invocation(websocket, message)
                elif action == InvocationWSConstants.ACTION_CANCEL_INVOCATION:
                    await self._handle_ws_cancel_invocation(websocket, message)
                elif action == InvocationWSConstants.ACTION_PING:
                    # Client-initiated ping — respond with pong.
                    await websocket.send_json({"type": InvocationWSConstants.MSG_TYPE_PONG})
                elif action == InvocationWSConstants.ACTION_PONG:
                    # Client pong response — no-op, already kept connection alive.
                    pass
                else:
                    await websocket.send_json({
                        "type": InvocationWSConstants.MSG_TYPE_ERROR,
                        "error": {
                            "code": "invalid_action",
                            "message": f"Unknown action: {action}",
                        },
                    })
        except WebSocketDisconnect:
            logger.debug("WebSocket client disconnected")
        except Exception:  # pylint: disable=broad-exception-caught
            logger.exception("Unexpected WebSocket error")
        finally:
            if ping_task is not None:
                ping_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await ping_task

    # ------------------------------------------------------------------
    # Invoke handler
    # ------------------------------------------------------------------

    async def _handle_ws_invoke(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        generated_id = str(uuid.uuid4())
        raw_invocation_id = message.get("invocation_id") or ""
        invocation_id = _sanitize_id(raw_invocation_id, generated_id)

        raw_session_id = (
            message.get("session_id")
            or os.environ.get("FOUNDRY_AGENT_SESSION_ID")
            or ""
        )
        session_id = _sanitize_id(raw_session_id, str(uuid.uuid4()))

        context = InvocationWSContext(invocation_id=invocation_id, session_id=session_id)
        payload = message.get("payload", {})

        if self._ws_invoke_fn is None:
            await websocket.send_json({
                "type": InvocationWSConstants.MSG_TYPE_ERROR,
                "invocation_id": invocation_id,
                "session_id": session_id,
                "error": {
                    "code": "not_implemented",
                    "message": "No invoke handler registered. Use the @app.ws_invoke_handler decorator.",
                },
            })
            return

        with self._ws_request_span(
            websocket.headers, invocation_id, "invoke_agent",
            operation_name="invoke_agent", session_id=session_id,
        ) as otel_span:
            self._ws_safe_set_attrs(otel_span, {
                InvocationWSConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationWSConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            try:
                if inspect.isasyncgenfunction(self._ws_invoke_fn):
                    # Streaming response
                    async for chunk in self._ws_invoke_fn(payload, context):
                        await websocket.send_json({
                            "type": InvocationWSConstants.MSG_TYPE_STREAM_CHUNK,
                            "invocation_id": invocation_id,
                            "session_id": session_id,
                            "payload": chunk,
                        })
                    await websocket.send_json({
                        "type": InvocationWSConstants.MSG_TYPE_STREAM_END,
                        "invocation_id": invocation_id,
                        "session_id": session_id,
                    })
                else:
                    # Non-streaming response
                    result = await self._ws_invoke_fn(payload, context)
                    await websocket.send_json({
                        "type": InvocationWSConstants.MSG_TYPE_RESULT,
                        "invocation_id": invocation_id,
                        "session_id": session_id,
                        "payload": result,
                    })
            except InvocationWSError as exc:
                self._ws_safe_set_attrs(otel_span, {
                    InvocationWSConstants.ATTR_SPAN_ERROR_CODE: exc.code,
                    InvocationWSConstants.ATTR_SPAN_ERROR_MESSAGE: exc.message,
                })
                end_span(otel_span, exc=exc)
                logger.error("Invocation %s failed: %s", invocation_id, exc)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "session_id": session_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
                return
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._ws_safe_set_attrs(otel_span, {
                    InvocationWSConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationWSConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                end_span(otel_span, exc=exc)
                logger.error("Error processing invocation %s: %s", invocation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "session_id": session_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })
                return

            # Success — end span
            end_span(otel_span)

    # ------------------------------------------------------------------
    # Get-invocation handler
    # ------------------------------------------------------------------

    async def _handle_ws_get_invocation(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        invocation_id = message.get("invocation_id") or ""
        if not invocation_id:
            await websocket.send_json({
                "type": InvocationWSConstants.MSG_TYPE_ERROR,
                "error": {"code": "invalid_request", "message": "invocation_id is required"},
            })
            return

        session_id = message.get("session_id") or ""
        context = InvocationWSContext(invocation_id=invocation_id, session_id=session_id)

        with self._ws_simple_request_span(
            websocket.headers, invocation_id, "get_invocation",
            session_id=session_id,
        ) as otel_span:
            self._ws_safe_set_attrs(otel_span, {
                InvocationWSConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationWSConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            if self._ws_get_invocation_fn is None:
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": "not_found", "message": "get_invocation not implemented"},
                })
                return

            try:
                result = await self._ws_get_invocation_fn(context)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_RESULT,
                    "invocation_id": invocation_id,
                    "payload": result,
                })
            except InvocationWSError as exc:
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._ws_safe_set_attrs(otel_span, {
                    InvocationWSConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationWSConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                record_error(otel_span, exc)
                logger.error("Error in get_invocation %s: %s", invocation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })

    # ------------------------------------------------------------------
    # Cancel-invocation handler
    # ------------------------------------------------------------------

    async def _handle_ws_cancel_invocation(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        invocation_id = message.get("invocation_id") or ""
        if not invocation_id:
            await websocket.send_json({
                "type": InvocationWSConstants.MSG_TYPE_ERROR,
                "error": {"code": "invalid_request", "message": "invocation_id is required"},
            })
            return

        session_id = message.get("session_id") or ""
        context = InvocationWSContext(invocation_id=invocation_id, session_id=session_id)

        with self._ws_simple_request_span(
            websocket.headers, invocation_id, "cancel_invocation",
            session_id=session_id,
        ) as otel_span:
            self._ws_safe_set_attrs(otel_span, {
                InvocationWSConstants.ATTR_SPAN_INVOCATION_ID: invocation_id,
                InvocationWSConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            if self._ws_cancel_invocation_fn is None:
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": "not_found", "message": "cancel_invocation not implemented"},
                })
                return

            try:
                result = await self._ws_cancel_invocation_fn(context)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_RESULT,
                    "invocation_id": invocation_id,
                    "payload": result,
                })
            except InvocationWSError as exc:
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._ws_safe_set_attrs(otel_span, {
                    InvocationWSConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    InvocationWSConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                record_error(otel_span, exc)
                logger.error("Error in cancel_invocation %s: %s", invocation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": InvocationWSConstants.MSG_TYPE_ERROR,
                    "invocation_id": invocation_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })
