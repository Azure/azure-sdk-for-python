# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

Provides the activity protocol endpoint as a
:class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""

import contextvars
import inspect
import logging
import os
import re as _re
import threading
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from opentelemetry import baggage as _otel_baggage, context as _otel_context, trace as _otel_trace
from opentelemetry.trace import Status as _OtelStatus
from opentelemetry.trace import StatusCode as _OtelStatusCode
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from azure.ai.agentserver.core import AgentServerHost, create_error_response
from azure.ai.agentserver.core._platform_headers import (
    CHAT_ISOLATION_KEY,
    ERROR_DETAIL,
    ERROR_SOURCE,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    USER_ISOLATION_KEY,
)

from ._constants import ActivityConstants

logger = logging.getLogger("azure.ai.agentserver")

_ERROR_SOURCE_UPSTREAM: str = "upstream"
_ERROR_SOURCE_PLATFORM: str = "platform"


_session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_session_id", default="")
_user_isolation_key_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_user_isolation_key", default="")
_chat_isolation_key_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_chat_isolation_key", default="")
_protocol_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_protocol", default=ActivityConstants.PROTOCOL)


class _ActivityLogFilter(logging.Filter):
    """Attach per-turn structured scope fields to activity log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.SessionId = _session_id_var.get("")  # type: ignore[attr-defined]
        record.UserIsolationKey = _user_isolation_key_var.get("")  # type: ignore[attr-defined]
        record.ChatIsolationKey = _chat_isolation_key_var.get("")  # type: ignore[attr-defined]
        record.Protocol = _protocol_var.get(ActivityConstants.PROTOCOL)  # type: ignore[attr-defined]
        return True


_log_filter_lock = threading.Lock()
_log_filter_installed = False


def _ensure_log_filter() -> None:
    """Install activity log scope filter once."""
    global _log_filter_installed  # pylint: disable=global-statement
    if _log_filter_installed:
        return
    with _log_filter_lock:
        if _log_filter_installed:
            return
        logger.addFilter(_ActivityLogFilter())
        _log_filter_installed = True


def _apply_error_source_headers(
    headers: dict[str, str],
    error_source: str,
    error_detail: Optional[str] = None,
) -> dict[str, str]:
    """Return a new dict with error source classification headers merged in.

    :param headers: Base headers to merge into.
    :param error_source: The error source value (user/platform/upstream).
    :param error_detail: Optional detail string for platform errors.
    :return: A new dict containing the original headers plus error source headers.
    """
    merged = {**headers, ERROR_SOURCE: error_source}
    if error_detail:
        merged[ERROR_DETAIL] = error_detail
    return merged


_SAFE_ID_PATTERN = _re.compile(r"^[a-zA-Z0-9\-_.:]+$")
_MAX_ID_LENGTH = 256


def _sanitize_id(value: str) -> str:
    """Validate an ID for safe use in HTTP headers and logs.

    Accepts alphanumeric characters plus ``-_.:`` up to 256 characters.
    Returns a fallback UUID for invalid or oversized values.
    """
    if not value or len(value) > _MAX_ID_LENGTH or not _SAFE_ID_PATTERN.match(value):
        return str(uuid.uuid4())
    return value


def _classify_error(exc: BaseException) -> tuple[str, Optional[str]]:
    """Classify an exception: platform-tagged -> (platform, detail), else -> (upstream, None)."""
    if getattr(exc, PLATFORM_ERROR_TAG, False) is True:
        detail = f"{type(exc).__name__}: {exc}"
        if len(detail) > MAX_ERROR_DETAIL_LENGTH:
            suffix = "...[truncated]"
            detail = detail[: MAX_ERROR_DETAIL_LENGTH - len(suffix)] + suffix
        return _ERROR_SOURCE_PLATFORM, detail
    return _ERROR_SOURCE_UPSTREAM, None


class ActivityAgentServerHost(AgentServerHost):
    """Activity protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    the activity protocol endpoint at ``POST /activity/messages``.  Use the decorator
    methods to register M365 SDK activity handlers, or pass a custom
    ``handler`` callable for full control.

    When no ``handler`` is provided, the M365 Agents SDK is auto-initialized
    from environment variables.

    Usage::

        from azure.ai.agentserver.activity import ActivityAgentServerHost

        app = ActivityAgentServerHost()

        @app.activity("message")
        async def on_message(context, state):
            await context.send_activity(f"Echo: {context.activity.text}")

        app.run()

    :param handler: Optional custom handler function.  When provided, the
        decorator API is bypassed and the handler receives the raw Starlette
        ``Request`` with ``request.state.activity`` set to the parsed
        activity dict.
    :type handler: Optional[Callable[[Request], Awaitable[Response]]]
    """

    _INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.Activity"

    def __init__(
        self,
        *,
        handler: Optional[Callable[[Request], Awaitable[Response]]] = None,
        **kwargs: Any,
    ) -> None:
        if handler is not None and not inspect.iscoroutinefunction(handler):
            raise TypeError(
                f"handler must be an async function, got {type(handler).__name__}. "
                "Use 'async def' to define your handler."
            )

        # explicit handler: user owns the processing pipeline
        # no handler: use built-in M365 bridge + decorators
        self._handler = handler

        activity_routes: list[Any] = [
            Route(
                "/activity/messages",
                self._create_activity_endpoint,
                methods=["POST"],
                name="create_activity",
            ),
            Route(
                "/api/messages",
                self._create_activity_endpoint,
                methods=["POST"],
                name="create_activity_api_messages",
            ),
        ]

        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + activity_routes, **kwargs)

    # ------------------------------------------------------------------
    # Handler decorators
    # ------------------------------------------------------------------

    def activity(self, activity_type: str):
        """Register a handler for a specific activity type.

        Usage::

            @app.activity("message")
            async def on_message(context, state):
                await context.send_activity(f"Echo: {context.activity.text}")

        :param activity_type: The activity type to handle (e.g., "message", "invoke").
        :type activity_type: str
        """
        def decorator(fn):
            from ._m365_bridge import _get_or_create_lazy_app
            lazy_app = _get_or_create_lazy_app()
            lazy_app.activity(activity_type)(fn)
            # Wire up the bridge handler if not already set
            if self._handler is None:
                from ._m365_bridge import create_bridge_handler
                self._handler = create_bridge_handler
            return fn
        return decorator

    def error(self, fn):
        """Register an error handler.

        Usage::

            @app.error
            async def on_error(context, error):
                await context.send_activity(f"Error: {error}")

        :param fn: Async error handler function.
        """
        from ._m365_bridge import _get_or_create_lazy_app
        lazy_app = _get_or_create_lazy_app()
        lazy_app.error(fn)
        if self._handler is None:
            from ._m365_bridge import create_bridge_handler
            self._handler = create_bridge_handler
        return fn

    def _resolve_session_id(self, request: Request) -> str:
        query_session_id = request.query_params.get("agent_session_id")
        if query_session_id and query_session_id.strip():
            return query_session_id.strip()

        header_id = request.headers.get(ActivityConstants.SESSION_ID_HEADER)
        if header_id and header_id.strip():
            return header_id.strip()

        if self.config.session_id and self.config.session_id.strip():
            return self.config.session_id.strip()

        return str(uuid.uuid4())

    def _build_span_name(self) -> str:
        agent_name = (self.config.agent_name or "").strip()
        agent_version = (self.config.agent_version or "").strip()
        if agent_name and agent_version:
            return f"handle_activity {agent_name}:{agent_version}"
        if agent_name:
            return f"handle_activity {agent_name}"
        return "handle_activity"

    def _apply_trace_tags(self, span: Any, session_id: str) -> None:
        agent_name = (self.config.agent_name or "").strip()
        agent_version = (self.config.agent_version or "").strip()
        if agent_name and agent_version:
            agent_id = f"{agent_name}:{agent_version}"
        elif agent_name:
            agent_id = agent_name
        else:
            agent_id = ""

        span.set_attribute("service.name", "azure.ai.agentserver")
        span.set_attribute("gen_ai.provider.name", "AzureAI Hosted Agents")
        span.set_attribute("gen_ai.operation.name", "handle_activity")
        span.set_attribute("gen_ai.agent.id", agent_id)
        if agent_name:
            span.set_attribute("gen_ai.agent.name", agent_name)
        if agent_version:
            span.set_attribute("gen_ai.agent.version", agent_version)
        if session_id:
            span.set_attribute("gen_ai.conversation.id", session_id)

        span.set_attribute(ActivityConstants.ATTR_SPAN_SESSION_ID, session_id or "")
        span.set_attribute(ActivityConstants.ATTR_SPAN_PROTOCOL, ActivityConstants.PROTOCOL)
        span.set_attribute("microsoft.foundry.project.id", os.environ.get("FOUNDRY_PROJECT_ARM_ID", ""))

    def _add_required_response_headers(self, response: Response, session_id: str) -> None:
        response.headers[ActivityConstants.SESSION_ID_HEADER] = session_id

    async def _create_activity_endpoint(self, request: Request) -> Response:
        """Handle inbound POST to /activity/messages or /api/messages."""
        logger.debug(
            "Activity endpoint hit | method=%s | path=%s | query=%s | content-type=%s",
            request.method, request.url.path, str(request.query_params),
            request.headers.get("content-type", ""),
        )
        logger.debug("Activity endpoint headers: %s", dict(request.headers))

        inbound_conversation_id = request.headers.get(ActivityConstants.CONVERSATION_ID_HEADER, "")
        inbound_user_isolation_key = request.headers.get(USER_ISOLATION_KEY, "")
        inbound_chat_isolation_key = request.headers.get(CHAT_ISOLATION_KEY, "")

        try:
            payload = await request.json()
        except Exception:  # pylint: disable=broad-exception-caught
            response = create_error_response(
                "invalid_request",
                "Request body must be valid JSON",
                status_code=400,
                headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
            )
            self._add_required_response_headers(response, "")
            return response

        if not isinstance(payload, dict):
            response = create_error_response(
                "invalid_request",
                "Activity payload must be a JSON object",
                status_code=400,
                headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
            )
            self._add_required_response_headers(response, "")
            return response

        activity_id = payload.get("id", "") if isinstance(payload.get("id"), str) else ""
        if not activity_id.strip():
            activity_id = str(uuid.uuid4())
        else:
            activity_id = _sanitize_id(activity_id)

        session_id = _sanitize_id(self._resolve_session_id(request))

        logger.debug(
            "Activity parsed | type=%s | activity_id=%s | session_id=%s | text=%s | serviceUrl=%s | channelId=%s",
            payload.get("type", "?"), activity_id, session_id,
            str(payload.get("text", ""))[:100], payload.get("serviceUrl", ""), payload.get("channelId", ""),
        )

        request.state.activity = payload
        request.state.activity_id = activity_id
        request.state.session_id = session_id
        request.state.user_isolation_key = inbound_user_isolation_key
        request.state.chat_isolation_key = inbound_chat_isolation_key

        _ensure_log_filter()
        session_token = _session_id_var.set(session_id)
        user_token = _user_isolation_key_var.set(inbound_user_isolation_key)
        chat_token = _chat_isolation_key_var.set(inbound_chat_isolation_key)
        protocol_token = _protocol_var.set(ActivityConstants.PROTOCOL)

        tracer = _otel_trace.get_tracer(self._INSTRUMENTATION_SCOPE)
        baggage_ctx = _otel_context.get_current()
        baggage_ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id", session_id or "", context=baggage_ctx
        )
        baggage_ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.protocol", ActivityConstants.PROTOCOL, context=baggage_ctx
        )
        baggage_token = _otel_context.attach(baggage_ctx)

        try:
            with tracer.start_as_current_span(self._build_span_name()) as span:
                self._apply_trace_tags(span, session_id)
                try:
                    if self._handler is None:
                        raise NotImplementedError(
                            "No activity handler registered. Use the @app.activity() decorator "
                            "or pass a handler= callable to ActivityAgentServerHost()."
                        )
                    response = await self._handler(request)

                    response.headers[ActivityConstants.ACTIVITY_ID_HEADER] = activity_id
                    self._add_required_response_headers(response, session_id)
                    return response
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    error_source, error_detail = _classify_error(exc)
                    logger.error("Error processing activity %s: %s", activity_id, exc, exc_info=True)

                    # Record error on the span (still inside `with` block)
                    if span.is_recording():
                        span.set_status(_OtelStatus(_OtelStatusCode.ERROR, str(exc)))
                        span.record_exception(exc)
                        span.set_attribute("error.type", type(exc).__name__)
                        span.set_attribute("otel.status.description", str(exc))
                        span.set_attribute(ActivityConstants.ATTR_SPAN_ERROR_CODE, type(exc).__name__)
                        span.set_attribute(ActivityConstants.ATTR_SPAN_ERROR_MESSAGE, str(exc))

                    response = create_error_response(
                        "internal_error",
                        "Internal server error",
                        status_code=500,
                        headers=_apply_error_source_headers(
                            {ActivityConstants.ACTIVITY_ID_HEADER: activity_id},
                            error_source,
                            error_detail,
                        ),
                    )
                    self._add_required_response_headers(response, session_id)
                    return response
        finally:
            _session_id_var.reset(session_token)
            _user_isolation_key_var.reset(user_token)
            _chat_isolation_key_var.reset(chat_token)
            _protocol_var.reset(protocol_token)
            try:
                _otel_context.detach(baggage_token)
            except ValueError:
                pass
