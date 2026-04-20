# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Conversation protocol host for Azure AI Hosted Agents (WebSocket).

Provides the conversation protocol over WebSocket long connections
as a :class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""
import asyncio
import contextlib
import inspect
import json
import logging
import os
import re
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable  # pylint: disable=import-error
from dataclasses import dataclass
from typing import Any, Optional, Union

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

from ._constants import ConversationConstants

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
class ConversationContext:
    """Contextual information for a conversation request.

    Passed to handler functions registered via :meth:`invoke_handler`,
    :meth:`get_conversation_handler`, and :meth:`cancel_conversation_handler`.

    :param conversation_id: Unique identifier for this conversation.
    :type conversation_id: str
    :param session_id: Session identifier for this conversation.
    :type session_id: str
    """

    conversation_id: str
    session_id: str


class ConversationError(Exception):
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


class ConversationAgentServerHost(AgentServerHost):
    """Conversation protocol host for Azure AI Hosted Agents over WebSocket.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    a WebSocket endpoint for the conversation protocol.  Use the decorator
    methods to wire handler functions to messages.

    WebSocket endpoint: ``/conversations/ws``

    **Client → Server messages** (JSON text frames)::

        {"action": "invoke", "conversation_id": "opt", "session_id": "opt", "payload": {...}}
        {"action": "get_conversation", "conversation_id": "required"}
        {"action": "cancel_conversation", "conversation_id": "required"}

    **Server → Client messages** (JSON text frames)::

        {"type": "result", "conversation_id": "...", "session_id": "...", "payload": {...}}
        {"type": "stream_chunk", "conversation_id": "...", "session_id": "...", "payload": {...}}
        {"type": "stream_end", "conversation_id": "...", "session_id": "..."}
        {"type": "error", "conversation_id": "...", "error": {"code": "...", "message": "..."}}

    Usage::

        from azure.ai.agentserver.conversations import ConversationAgentServerHost, ConversationContext

        app = ConversationAgentServerHost()

        @app.invoke_handler
        async def handle(payload, context):
            return {"reply": "hello"}

        app.run()

    :param openapi_spec: Optional OpenAPI spec dict.  When provided, the spec
        is served at ``GET /conversations/docs/openapi.json``.
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
        self._invoke_fn: Optional[Callable] = None
        self._get_conversation_fn: Optional[Callable] = None
        self._cancel_conversation_fn: Optional[Callable] = None
        self._openapi_spec = openapi_spec
        self._ws_ping_interval: int = (
            ws_ping_interval
            if ws_ping_interval is not None
            else ConversationConstants.DEFAULT_WS_PING_INTERVAL
        )

        # Build conversation routes
        conversation_routes: list[Any] = [
            Route(
                "/conversations/docs/openapi.json",
                self._get_openapi_spec_endpoint,
                methods=["GET"],
                name="get_openapi_spec",
            ),
            WebSocketRoute(
                "/conversations/ws",
                self._websocket_endpoint,
                name="conversations_ws",
            ),
        ]

        # Merge with any routes from sibling mixins via cooperative init
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + conversation_routes, **kwargs)

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def invoke_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the invoke handler.

        The handler receives ``(payload: dict, context: ConversationContext)``
        and may be:

        - An async function returning a ``dict`` (non-streaming).
        - An async generator yielding ``dict`` chunks (streaming).

        Usage::

            @app.invoke_handler
            async def handle(payload, context):
                return {"reply": f"echo: {payload}"}

            # Streaming variant:
            @app.invoke_handler
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
                f"invoke_handler expects an async function or async generator, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._invoke_fn = fn
        return fn

    def get_conversation_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the get-conversation handler.

        The handler receives ``(context: ConversationContext)`` and returns
        a ``dict``.

        :param fn: Async function.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"get_conversation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._get_conversation_fn = fn
        return fn

    def cancel_conversation_handler(
        self, fn: Callable[..., Any]
    ) -> Callable[..., Any]:
        """Register a function as the cancel-conversation handler.

        The handler receives ``(context: ConversationContext)`` and returns
        a ``dict``.

        :param fn: Async function.
        :type fn: Callable
        :return: The original function (unmodified).
        :rtype: Callable
        :raises TypeError: If *fn* is not an async function.
        """
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(
                f"cancel_conversation_handler expects an async function, got {type(fn).__name__}. "
                "Use 'async def' to define your handler."
            )
        self._cancel_conversation_fn = fn
        return fn

    # ------------------------------------------------------------------
    # OpenAPI spec (HTTP endpoint — documentation)
    # ------------------------------------------------------------------

    def get_openapi_spec(self) -> Optional[dict[str, Any]]:
        """Return the stored OpenAPI spec, or None."""
        return self._openapi_spec

    async def _get_openapi_spec_endpoint(self, request: Request) -> Response:  # pylint: disable=unused-argument
        spec = self.get_openapi_spec()
        if spec is None:
            return create_error_response("not_found", "No OpenAPI spec registered", status_code=404)
        return JSONResponse(spec)

    # ------------------------------------------------------------------
    # Span attribute helper
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_set_attrs(span: Any, attrs: dict[str, str]) -> None:
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

    def _request_span(
        self,
        headers: Any,
        conversation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> Any:
        """Create a request span — returns a no-op context manager when tracing is off.

        :param headers: HTTP/WebSocket handshake headers.
        :type headers: any
        :param conversation_id: The request/conversation ID.
        :type conversation_id: str
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
            headers, conversation_id, span_operation,
            operation_name=operation_name, session_id=session_id,
            end_on_exit=False,
        )

    def _simple_request_span(
        self,
        headers: Any,
        conversation_id: str,
        span_operation: str,
        session_id: str = "",
    ) -> Any:
        """Create a request span that auto-ends on exit.

        Used for get/cancel operations that don't need manual span lifecycle.

        :param headers: HTTP/WebSocket handshake headers.
        :type headers: any
        :param conversation_id: The request/conversation ID.
        :type conversation_id: str
        :param span_operation: Span operation name.
        :type span_operation: str
        :param session_id: Session ID (empty string if absent).
        :type session_id: str
        :return: Context manager yielding the OTel span or *None*.
        :rtype: any
        """
        return self.request_span(
            headers, conversation_id, span_operation,
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
                await websocket.send_json({"type": ConversationConstants.MSG_TYPE_PING})
        except (WebSocketDisconnect, Exception):  # pylint: disable=broad-exception-caught
            # Connection closed or errored — let the task exit silently.
            pass

    async def _websocket_endpoint(self, websocket: WebSocket) -> None:
        """Main WebSocket endpoint for the conversation protocol.

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
                        "type": ConversationConstants.MSG_TYPE_ERROR,
                        "error": {"code": "invalid_json", "message": "Invalid JSON message"},
                    })
                    continue

                if not isinstance(message, dict):
                    await websocket.send_json({
                        "type": ConversationConstants.MSG_TYPE_ERROR,
                        "error": {"code": "invalid_message", "message": "Message must be a JSON object"},
                    })
                    continue

                action = message.get("action")
                if action == ConversationConstants.ACTION_INVOKE:
                    await self._handle_ws_invoke(websocket, message)
                elif action == ConversationConstants.ACTION_GET_CONVERSATION:
                    await self._handle_ws_get_conversation(websocket, message)
                elif action == ConversationConstants.ACTION_CANCEL_CONVERSATION:
                    await self._handle_ws_cancel_conversation(websocket, message)
                elif action == ConversationConstants.ACTION_PING:
                    # Client-initiated ping — respond with pong.
                    await websocket.send_json({"type": ConversationConstants.MSG_TYPE_PONG})
                elif action == ConversationConstants.ACTION_PONG:
                    # Client pong response — no-op, already kept connection alive.
                    pass
                else:
                    await websocket.send_json({
                        "type": ConversationConstants.MSG_TYPE_ERROR,
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
        raw_conversation_id = message.get("conversation_id") or ""
        conversation_id = _sanitize_id(raw_conversation_id, generated_id)

        raw_session_id = (
            message.get("session_id")
            or os.environ.get("FOUNDRY_AGENT_SESSION_ID")
            or ""
        )
        session_id = _sanitize_id(raw_session_id, str(uuid.uuid4()))

        context = ConversationContext(conversation_id=conversation_id, session_id=session_id)
        payload = message.get("payload", {})

        if self._invoke_fn is None:
            await websocket.send_json({
                "type": ConversationConstants.MSG_TYPE_ERROR,
                "conversation_id": conversation_id,
                "session_id": session_id,
                "error": {
                    "code": "not_implemented",
                    "message": "No invoke handler registered. Use the @app.invoke_handler decorator.",
                },
            })
            return

        with self._request_span(
            websocket.headers, conversation_id, "invoke_agent",
            operation_name="invoke_agent", session_id=session_id,
        ) as otel_span:
            self._safe_set_attrs(otel_span, {
                ConversationConstants.ATTR_SPAN_CONVERSATION_ID: conversation_id,
                ConversationConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            try:
                if inspect.isasyncgenfunction(self._invoke_fn):
                    # Streaming response
                    async for chunk in self._invoke_fn(payload, context):
                        await websocket.send_json({
                            "type": ConversationConstants.MSG_TYPE_STREAM_CHUNK,
                            "conversation_id": conversation_id,
                            "session_id": session_id,
                            "payload": chunk,
                        })
                    await websocket.send_json({
                        "type": ConversationConstants.MSG_TYPE_STREAM_END,
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                    })
                else:
                    # Non-streaming response
                    result = await self._invoke_fn(payload, context)
                    await websocket.send_json({
                        "type": ConversationConstants.MSG_TYPE_RESULT,
                        "conversation_id": conversation_id,
                        "session_id": session_id,
                        "payload": result,
                    })
            except ConversationError as exc:
                self._safe_set_attrs(otel_span, {
                    ConversationConstants.ATTR_SPAN_ERROR_CODE: exc.code,
                    ConversationConstants.ATTR_SPAN_ERROR_MESSAGE: exc.message,
                })
                end_span(otel_span, exc=exc)
                logger.error("Conversation %s failed: %s", conversation_id, exc)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
                return
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._safe_set_attrs(otel_span, {
                    ConversationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    ConversationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                end_span(otel_span, exc=exc)
                logger.error("Error processing conversation %s: %s", conversation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })
                return

            # Success — end span
            end_span(otel_span)

    # ------------------------------------------------------------------
    # Get-conversation handler
    # ------------------------------------------------------------------

    async def _handle_ws_get_conversation(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        conversation_id = message.get("conversation_id") or ""
        if not conversation_id:
            await websocket.send_json({
                "type": ConversationConstants.MSG_TYPE_ERROR,
                "error": {"code": "invalid_request", "message": "conversation_id is required"},
            })
            return

        session_id = message.get("session_id") or ""
        context = ConversationContext(conversation_id=conversation_id, session_id=session_id)

        with self._simple_request_span(
            websocket.headers, conversation_id, "get_conversation",
            session_id=session_id,
        ) as otel_span:
            self._safe_set_attrs(otel_span, {
                ConversationConstants.ATTR_SPAN_CONVERSATION_ID: conversation_id,
                ConversationConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            if self._get_conversation_fn is None:
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": "not_found", "message": "get_conversation not implemented"},
                })
                return

            try:
                result = await self._get_conversation_fn(context)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_RESULT,
                    "conversation_id": conversation_id,
                    "payload": result,
                })
            except ConversationError as exc:
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._safe_set_attrs(otel_span, {
                    ConversationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    ConversationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                record_error(otel_span, exc)
                logger.error("Error in get_conversation %s: %s", conversation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })

    # ------------------------------------------------------------------
    # Cancel-conversation handler
    # ------------------------------------------------------------------

    async def _handle_ws_cancel_conversation(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        conversation_id = message.get("conversation_id") or ""
        if not conversation_id:
            await websocket.send_json({
                "type": ConversationConstants.MSG_TYPE_ERROR,
                "error": {"code": "invalid_request", "message": "conversation_id is required"},
            })
            return

        session_id = message.get("session_id") or ""
        context = ConversationContext(conversation_id=conversation_id, session_id=session_id)

        with self._simple_request_span(
            websocket.headers, conversation_id, "cancel_conversation",
            session_id=session_id,
        ) as otel_span:
            self._safe_set_attrs(otel_span, {
                ConversationConstants.ATTR_SPAN_CONVERSATION_ID: conversation_id,
                ConversationConstants.ATTR_SPAN_SESSION_ID: session_id,
            })

            if self._cancel_conversation_fn is None:
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": "not_found", "message": "cancel_conversation not implemented"},
                })
                return

            try:
                result = await self._cancel_conversation_fn(context)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_RESULT,
                    "conversation_id": conversation_id,
                    "payload": result,
                })
            except ConversationError as exc:
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": exc.code, "message": exc.message},
                })
            except Exception as exc:  # pylint: disable=broad-exception-caught
                self._safe_set_attrs(otel_span, {
                    ConversationConstants.ATTR_SPAN_ERROR_CODE: "internal_error",
                    ConversationConstants.ATTR_SPAN_ERROR_MESSAGE: str(exc),
                })
                record_error(otel_span, exc)
                logger.error("Error in cancel_conversation %s: %s", conversation_id, exc, exc_info=True)
                await websocket.send_json({
                    "type": ConversationConstants.MSG_TYPE_ERROR,
                    "conversation_id": conversation_id,
                    "error": {"code": "internal_error", "message": "Internal server error"},
                })
