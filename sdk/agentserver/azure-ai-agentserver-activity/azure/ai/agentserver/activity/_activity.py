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

from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
from opentelemetry import trace as _otel_trace
from opentelemetry.context import Token
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from azure.ai.agentserver.core import (
    AgentServerHost,
    FoundryAgentRequestContext,
    create_error_response,
    reset_request_context,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import (
    ERROR_DETAIL,
    ERROR_SOURCE,
    FOUNDRY_CALL_ID,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    USER_ID,
)

from ._constants import ActivityConstants

logger = logging.getLogger("azure.ai.agentserver")

_ERROR_SOURCE_UPSTREAM: str = "upstream"
_ERROR_SOURCE_PLATFORM: str = "platform"


_session_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_session_id", default="")
_user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_user_id", default="")
_call_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_call_id", default="")
_protocol_var: contextvars.ContextVar[str] = contextvars.ContextVar("activity_protocol", default=ActivityConstants.PROTOCOL)


def _enrich_record(record: logging.LogRecord) -> None:
    """Populate activity scope fields on a log record from the current context.

    :param record: The log record to enrich.
    """
    if not hasattr(record, "SessionId"):
        record.SessionId = _session_id_var.get("")  # type: ignore[attr-defined]
    if not hasattr(record, "UserId"):
        record.UserId = _user_id_var.get("")  # type: ignore[attr-defined]
    if not hasattr(record, "CallId"):
        record.CallId = _call_id_var.get("")  # type: ignore[attr-defined]
    if not hasattr(record, "Protocol"):
        record.Protocol = _protocol_var.get(ActivityConstants.PROTOCOL)  # type: ignore[attr-defined]


class _ActivityLogFilter(logging.Filter):
    """Attach per-turn structured scope fields to a log record (legacy filter).

    Retained for backwards compatibility. The primary enrichment mechanism is
    the global log-record factory installed by :func:`_ensure_log_enrichment`,
    which guarantees that records emitted by *any* logger (not just this
    package's logger) carry the activity scope fields.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        _enrich_record(record)
        return True


_log_enrichment_lock = threading.Lock()
_log_enrichment_installed = False
_base_record_factory: Optional[Callable[..., logging.LogRecord]] = None


def _ensure_log_enrichment() -> None:
    """Install a global log-record factory once.

    Ensures every log record (regardless of which logger emits it) carries the
    activity scope fields read from the current context. This provides session /
    user / protocol correlation across the app logger, the M365 SDK
    loggers, azure.identity, connector clients, etc. — not just this package's
    own logger.
    """
    global _log_enrichment_installed, _base_record_factory  # pylint: disable=global-statement
    if _log_enrichment_installed:
        return
    with _log_enrichment_lock:
        if _log_enrichment_installed:
            return
        _base_record_factory = logging.getLogRecordFactory()

        def _factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = _base_record_factory(*args, **kwargs)  # type: ignore[misc]
            _enrich_record(record)
            return record

        logging.setLogRecordFactory(_factory)
        _log_enrichment_installed = True


try:  # SDK SpanProcessor provides the full interface (incl. _on_ending) the SDK calls.
    from opentelemetry.sdk.trace import SpanProcessor as _OtelSpanProcessor
except Exception:  # pylint: disable=broad-exception-caught
    _OtelSpanProcessor = object  # type: ignore[assignment, misc]


class _BaggageSpanProcessor(_OtelSpanProcessor):  # type: ignore[valid-type, misc]
    """SpanProcessor that copies OTel baggage entries onto every span at start.

    Baggage propagates request-scoped correlation values (session_id,
    conversation_id, activity_id, user/call ids, x_request_id, plus the
    platform-provided agent / tenant ids) through the context, but those
    values are *not* automatically recorded as span attributes. This processor
    promotes them so every child span produced during a turn (auth, connector,
    send-activity, GenAI, etc.) is filterable by the same correlation keys.

    Subclasses the SDK ``SpanProcessor`` so the full processor interface
    (``on_start``, ``on_end``, ``_on_ending``, ``shutdown``, ``force_flush``)
    is satisfied; the SDK invokes ``_on_ending`` on every registered processor
    during ``span.end()``.
    """

    def on_start(self, span: Any, parent_context: Optional[Any] = None) -> None:
        try:
            ctx = parent_context if parent_context is not None else _otel_context.get_current()
            for key, value in _otel_baggage.get_all(ctx).items():
                if value is not None:
                    span.set_attribute(key, value)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def on_end(self, span: Any) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=unused-argument
        return True


_baggage_processor_lock = threading.Lock()
_baggage_processor_installed = False


def _ensure_baggage_span_processor() -> None:
    """Register the baggage->span-attribute processor on the tracer provider once.

    Safe to call repeatedly; if the provider is not yet an SDK provider (e.g.
    still the API default at first request), installation is retried on a later
    call.
    """
    global _baggage_processor_installed  # pylint: disable=global-statement
    if _baggage_processor_installed:
        return
    with _baggage_processor_lock:
        if _baggage_processor_installed:
            return
        try:
            provider = _otel_trace.get_tracer_provider()
            add_span_processor = getattr(provider, "add_span_processor", None)
            if callable(add_span_processor):
                add_span_processor(_BaggageSpanProcessor())
                _baggage_processor_installed = True
        except Exception:  # pylint: disable=broad-exception-caught
            pass


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

    :param value: The ID value to sanitize.
    :return: A sanitized ID or a UUID string.
    :rtype: str
    """
    if not value or len(value) > _MAX_ID_LENGTH or not _SAFE_ID_PATTERN.match(value):
        return str(uuid.uuid4())
    return value


def _classify_error(exc: BaseException) -> tuple[str, Optional[str]]:
    """Classify an exception: platform-tagged -> (platform, detail), else -> (upstream, None).

    :param exc: The exception to classify.
    :return: A tuple of (source, detail) where source is 'platform' or 'upstream'.
    :rtype: tuple[str, Optional[str]]
    """
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

    By default the host uses the **simple** agent auth model, suitable for a
    Microsoft Teams bot whose ``msaAppId`` is the agent instance
    identity. Pass ``digital_worker=True`` to switch to the digital-worker
    (blueprint + federated-identity) model.

    Usage::

        from azure.ai.agentserver.activity import ActivityAgentServerHost

        app = ActivityAgentServerHost()  # simple Teams agent (default)

        @app.activity("message")
        async def on_message(context, state):
            await context.send_activity(f"Echo: {context.activity.text}")

        app.run()

    :param handler: Optional custom handler function.  When provided, the
        decorator API is bypassed and the handler receives the raw Starlette
        ``Request`` with ``request.state.activity`` set to the parsed
        activity dict.
    :type handler: Optional[Callable[[Request], Awaitable[Response]]]
    :keyword digital_worker: Selects the outbound-auth model. ``False`` (the
        default) uses the **simple** agent model: the agent *instance* identity
        mints the Bot Connector token directly via the Managed Identity Client
        (``UserManagedIdentity`` + the ``https://api.botframework.com/.default``
        scope), which is what a single-tenant Teams bot whose ``msaAppId`` is the
        agent instance identity requires. Set to ``True`` for the
        **digital-worker** model, which uses the blueprint identity plus the
        federated-identity (FMI) token exchange.
    :paramtype digital_worker: bool
    """

    _INSTRUMENTATION_SCOPE = "Azure.AI.AgentServer.Activity"

    def __init__(
        self,
        *,
        handler: Optional[Callable[[Request], Awaitable[Response]]] = None,
        digital_worker: bool = False,
        **kwargs: Any,
    ) -> None:
        self._digital_worker = bool(digital_worker)

        # Propagate the auth model to the bridge so it selects the matching
        # claims / MSAL-patch behavior.
        from ._m365_bridge import set_digital_worker_mode
        set_digital_worker_mode(self._digital_worker)

        # Initialize default env vars before bridge/app setup.
        self._initialize_default_env_vars()

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

    def _initialize_default_env_vars(self) -> None:
        """Initialize connection-related env vars used by the M365 SDK.

        Precedence order is:
        1. Existing explicit connection env vars
        2. Values derived from Foundry-native env vars
        3. Static defaults for non-critical options

        The defaults differ by auth model:

        * **Simple** (``digital_worker=False``, default): the *instance*
          identity (``FOUNDRY_AGENT_INSTANCE_CLIENT_ID``) mints the Bot
          Connector token directly, scoped to
          ``https://api.botframework.com/.default``.
        * **Digital worker** (``digital_worker=True``): the *blueprint*
          identity (``FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID``) is used with the
          federated-identity exchange, scoped to the agentic resource.
        """

        def _get_nonempty(name: str) -> str:
            return os.environ.get(name, "").strip()

        def _set_if_missing(name: str, value: str) -> None:
            if value and not _get_nonempty(name):
                os.environ[name] = value

        if self._digital_worker:
            scope = "5a807f24-c9de-44ee-a3a7-329e88a00ffc/.default"
            client_id_env = "FOUNDRY_AGENT_BLUEPRINT_CLIENT_ID"
        else:
            scope = "https://api.botframework.com/.default"
            client_id_env = "FOUNDRY_AGENT_INSTANCE_CLIENT_ID"

        defaults = {
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE": "UserManagedIdentity",
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__SCOPES__0": scope,
            "CONNECTIONSMAP__0__SERVICEURL": "*",
            "CONNECTIONSMAP__0__CONNECTION": "SERVICE_CONNECTION",
        }
        for key, value in defaults.items():
            _set_if_missing(key, value)

        foundry_client_id = _get_nonempty(client_id_env)
        foundry_tenant_id = _get_nonempty("FOUNDRY_AGENT_TENANT_ID")

        _set_if_missing(
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID",
            foundry_client_id,
        )
        _set_if_missing(
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID",
            foundry_tenant_id,
        )
        _set_if_missing(
            "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY",
            f"https://login.microsoftonline.com/{foundry_tenant_id}" if foundry_tenant_id else "",
        )

    def activity(self, activity_type: str):
        """Register a handler for a specific activity type.

        Usage::

            @app.activity("message")
            async def on_message(context, state):
                await context.send_activity(f"Echo: {context.activity.text}")

        :param activity_type: The activity type to handle (e.g., "message", "invoke").
        :type activity_type: str
        :return: A decorator function.
        :rtype: Callable
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
        :type fn: Callable
        :return: The error handler function.
        :rtype: Callable
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

    def _add_required_response_headers(self, response: Response, session_id: str) -> None:
        response.headers[ActivityConstants.SESSION_ID_HEADER] = session_id

    @staticmethod
    def _response_body_preview(response: Response, limit: int = 1024) -> str:
        """Return a truncated text preview of a response body for logging.

        :param response: The response object.
        :type response: Response
        :param limit: Maximum number of characters to return.
        :type limit: int
        :return: A text preview of the response body.
        :rtype: str
        """
        body = getattr(response, "body", None)
        if not body:
            return ""
        try:
            if isinstance(body, (bytes, bytearray)):
                text = bytes(body).decode("utf-8", errors="replace")
            else:
                text = str(body)
        except Exception:  # pylint: disable=broad-exception-caught
            return ""
        return text[:limit]

    async def _create_activity_endpoint(self, request: Request) -> Response:
        """Handle inbound POST to /activity/messages or /api/messages.

        Processes activity protocol requests, manages context variables,
        ensures logging enrichment, and orchestrates the activity handler.

        :param request: The inbound HTTP request.
        :type request: Request
        :return: The HTTP response.
        :rtype: Response
        """
        # Resolve correlation identifiers from headers up-front so that every
        # log line and span produced during this turn carries the values.
        inbound_conversation_id = request.headers.get(ActivityConstants.CONVERSATION_ID_HEADER, "")
        inbound_user_id = request.headers.get(USER_ID, "")
        inbound_call_id = request.headers.get(FOUNDRY_CALL_ID, "")
        session_id = _sanitize_id(self._resolve_session_id(request))
        request_trace_id = request.headers.get("x-request-id", "").strip()

        # Install global log/trace enrichment once, then bind the context vars so
        # the scope fields are populated for the very first log line of the turn.
        _ensure_log_enrichment()
        _ensure_baggage_span_processor()
        session_token = _session_id_var.set(session_id)
        user_token = _user_id_var.set(inbound_user_id)
        call_token = _call_id_var.set(inbound_call_id)
        protocol_token = _protocol_var.set(ActivityConstants.PROTOCOL)
        # Bind platform context so handler/tool code making raw outbound 1P calls
        # can forward the per-request call ID and user ID (protocol 2.0.0).
        ctx_token = set_request_context(
            FoundryAgentRequestContext(
                call_id=inbound_call_id or None,
                user_id=inbound_user_id or None,
                session_id=session_id,
            )
        )
        baggage_token: Optional[Token[Any]] = None

        try:
            logger.debug(
                "Activity endpoint hit | method=%s | path=%s | query=%s | content-type=%s",
                request.method, request.url.path, str(request.query_params),
                request.headers.get("content-type", ""),
            )
            logger.debug("Activity endpoint headers: %s", dict(request.headers))

            try:
                payload = await request.json()
            except Exception:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Activity request rejected | reason=invalid_json | session_id=%s", session_id
                )
                response = create_error_response(
                    "invalid_request",
                    "Request body must be valid JSON",
                    status_code=400,
                    headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
                )
                self._add_required_response_headers(response, session_id)
                return response

            if not isinstance(payload, dict):
                logger.warning(
                    "Activity request rejected | reason=non_object_payload | session_id=%s", session_id
                )
                response = create_error_response(
                    "invalid_request",
                    "Activity payload must be a JSON object",
                    status_code=400,
                    headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
                )
                self._add_required_response_headers(response, session_id)
                return response

            activity_id = payload.get("id", "") if isinstance(payload.get("id"), str) else ""
            if not activity_id.strip():
                activity_id = str(uuid.uuid4())
            else:
                activity_id = _sanitize_id(activity_id)

            # Extract conversation ID from Activity payload (Bot Framework schema),
            # falling back to the inbound conversation header if absent.
            conversation_obj = payload.get("conversation", {})
            conversation_id = ""
            if isinstance(conversation_obj, dict):
                conversation_id = conversation_obj.get("id", "")
            if conversation_id and isinstance(conversation_id, str):
                conversation_id = conversation_id.strip()
            if not conversation_id and inbound_conversation_id:
                conversation_id = inbound_conversation_id.strip()

            # Pull common request details for logging / span events.
            from_obj = payload.get("from", {})
            from_id = from_obj.get("id", "") if isinstance(from_obj, dict) else ""
            recipient_obj = payload.get("recipient", {})
            recipient_id = recipient_obj.get("id", "") if isinstance(recipient_obj, dict) else ""
            activity_type = payload.get("type", "") or ""
            channel_id = payload.get("channelId", "") or ""
            service_url = payload.get("serviceUrl", "") or ""
            locale = payload.get("locale", "") or ""
            request_text = str(payload.get("text", "") or "")

            request.state.activity = payload
            request.state.activity_id = activity_id
            request.state.session_id = session_id
            request.state.user_id = inbound_user_id
            request.state.call_id = inbound_call_id

            logger.info(
                "Activity request received | type=%s | activity_id=%s | conversation_id=%s | "
                "session_id=%s | from=%s | recipient=%s | channelId=%s | serviceUrl=%s | "
                "locale=%s | x_request_id=%s | text=%s",
                activity_type, activity_id, conversation_id, session_id, from_id, recipient_id,
                channel_id, service_url, locale, request_trace_id, request_text[:512],
            )

            baggage_ctx = _otel_context.get_current()
            # Set all required baggage keys per spec section 3.3.
            baggage_ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.session_id", session_id or "", context=baggage_ctx
            )
            baggage_ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.protocol", ActivityConstants.PROTOCOL, context=baggage_ctx
            )
            if conversation_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.conversation_id", conversation_id, context=baggage_ctx
                )
            if activity_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.activity_id", activity_id, context=baggage_ctx
                )
            if inbound_user_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.user_id", inbound_user_id, context=baggage_ctx
                )
            if inbound_call_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.call_id", inbound_call_id, context=baggage_ctx
                )
            if request_trace_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.x_request_id", request_trace_id, context=baggage_ctx
                )
            baggage_token = _otel_context.attach(baggage_ctx)


            try:
                if self._handler is None:
                    raise NotImplementedError(
                        "No activity handler registered. Use the @app.activity() decorator "
                        "or pass a handler= callable to ActivityAgentServerHost()."
                    )
                response = await self._handler(request)  # type: ignore[assignment]

                response.headers[ActivityConstants.ACTIVITY_ID_HEADER] = activity_id
                self._add_required_response_headers(response, session_id)

                # Record the outbound response as a structured log.
                status_code = getattr(response, "status_code", 0)
                response_text = self._response_body_preview(response)
                logger.info(
                    "Activity response sent | status_code=%s | activity_id=%s | "
                    "conversation_id=%s | session_id=%s | body=%s",
                    status_code, activity_id, conversation_id, session_id, response_text,
                )
                return response
            except Exception as exc:  # pylint: disable=broad-exception-caught
                error_source, error_detail = _classify_error(exc)
                logger.error(
                    "Activity request failed | activity_id=%s | conversation_id=%s | "
                    "session_id=%s | error_source=%s | error=%s",
                    activity_id, conversation_id, session_id, error_source, exc, exc_info=True,
                )

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
            _user_id_var.reset(user_token)
            _call_id_var.reset(call_token)
            _protocol_var.reset(protocol_token)
            reset_request_context(ctx_token)
            if baggage_token is not None:
                try:
                    _otel_context.detach(baggage_token)
                except ValueError:
                    pass
