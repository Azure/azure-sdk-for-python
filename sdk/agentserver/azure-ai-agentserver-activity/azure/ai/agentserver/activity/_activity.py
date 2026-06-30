# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

Provides the activity protocol endpoint as a
:class:`~azure.ai.agentserver.core.AgentServerHost` subclass.
"""

import inspect
import logging
import os
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
from opentelemetry.context import Token  # pyright: ignore[reportPrivateImportUsage]
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from azure.ai.agentserver.core import (
    AgentServerHost,
    FoundryAgentRequestContext,
    create_error_response,
    get_request_context,
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


def _enrich_record(record: logging.LogRecord) -> None:
    """Populate activity scope fields on a log record from the request context.

    :param record: The log record to enrich.
    :type record: logging.LogRecord
    """
    ctx = get_request_context()
    if not hasattr(record, "SessionId"):
        record.SessionId = ctx.session_id or ""  # type: ignore[attr-defined]
    if not hasattr(record, "UserId"):
        record.UserId = ctx.user_id or ""  # type: ignore[attr-defined]
    if not hasattr(record, "CallId"):
        record.CallId = ctx.call_id or ""  # type: ignore[attr-defined]
    if not hasattr(record, "Protocol"):
        record.Protocol = ActivityConstants.PROTOCOL  # type: ignore[attr-defined]


def _install_log_enrichment() -> None:
    """Install a log-record factory that enriches records with scope fields."""
    base_factory = logging.getLogRecordFactory()
    if getattr(base_factory, "_activity_enricher", False):
        return

    def _factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = base_factory(*args, **kwargs)
        _enrich_record(record)
        return record

    _factory._activity_enricher = True  # type: ignore[attr-defined]
    logging.setLogRecordFactory(_factory)


def _apply_error_source_headers(
    headers: dict[str, str],
    error_source: str,
    error_detail: Optional[str] = None,
) -> dict[str, str]:
    """Return a new dict with error source classification headers merged in.

    :param headers: Base headers to merge into.
    :type headers: dict[str, str]
    :param error_source: The error source value (user/platform/upstream).
    :type error_source: str
    :param error_detail: Optional detail string for platform errors.
    :type error_detail: str or None
    :return: A new dict containing the original headers plus error source headers.
    :rtype: dict[str, str]
    """
    merged = {**headers, ERROR_SOURCE: error_source}
    if error_detail:
        merged[ERROR_DETAIL] = error_detail
    return merged


def _classify_error(exc: BaseException) -> tuple[str, Optional[str]]:
    """Classify an exception: platform-tagged -> (platform, detail), else -> (upstream, None).

    :param exc: The exception to classify.
    :type exc: BaseException
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
    the activity protocol endpoint at ``POST /activity/messages``.  When no
    custom ``handler`` is provided, the M365 Agents SDK is initialized eagerly
    during construction and the host acts as the underlying ``AgentApplication``
    itself: handler-registration and the full M365 surface
    (``activity``/``error``/``message``/``proactive``/``auth`` ...) are reached
    directly on the host.

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

    :param handler: Optional custom request handler. When provided, the M365
        SDK is not initialized and the handler receives the raw Starlette
        ``Request`` with ``request.state.activity`` set to the parsed dict.
    :type handler: Optional[Callable[[Request], Awaitable[Response]]]
    :keyword digital_worker: Selects the outbound-auth model. ``False`` (the
        default) is the **simple** model: the agent *instance* identity mints
        the Bot Connector token directly. ``True`` is the **digital-worker**
        model: the *blueprint* identity with the federated-identity (FMI)
        token exchange.
    :paramtype digital_worker: bool
    """

    def __init__(
        self,
        *,
        handler: Optional[Callable[[Request], Awaitable[Response]]] = None,
        digital_worker: bool = False,
        storage: Optional[Any] = None,
        connection_manager: Optional[Any] = None,
        adapter: Optional[Any] = None,
        authorization: Optional[Any] = None,
        config: Optional[dict] = None,
        agent_app: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self._digital_worker = bool(digital_worker)

        # Seed connection-related env vars before building the M365 stack.
        self._initialize_default_env_vars()

        if handler is not None and not inspect.iscoroutinefunction(handler):
            raise TypeError(
                f"handler must be an async function, got {type(handler).__name__}. "
                "Use 'async def' to define your handler."
            )

        self._agent_app: Any = None
        self._adapter: Any = None

        if handler is not None:
            # Custom handler: the caller owns the pipeline; M365 is not initialized.
            self._handler = handler
        else:
            # Build the M365 stack; the host then delegates to it (see __getattr__).
            from ._m365_bridge import build_m365_app, make_bridge_handler
            self._agent_app, self._adapter = build_m365_app(
                digital_worker=self._digital_worker,
                storage=storage,
                connection_manager=connection_manager,
                adapter=adapter,
                authorization=authorization,
                config=config,
                agent_app=agent_app,
            )
            self._handler = make_bridge_handler(
                self._agent_app, self._adapter, digital_worker=self._digital_worker
            )

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

        # Install logging enrichment for this host. The core observability stack
        # promotes session_id / conversation_id baggage onto spans and logs.
        _install_log_enrichment()

        logger.info("ActivityAgentServerHost ready | Groot30ju607p deployment")

    @property
    def adapter(self) -> Any:
        """The channel adapter for the underlying ``AgentApplication``.

        :return: The adapter, or ``None`` when a custom ``handler=`` was supplied.
        :rtype: object
        """
        return self._adapter

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attribute access to the underlying ``AgentApplication``
        so handlers register directly on the host (``@app.activity`` / ``@app.error``).

        :param name: The attribute name being accessed.
        :type name: str
        :return: The corresponding attribute from the ``AgentApplication``.
        :rtype: object
        :raises AttributeError: If the M365 ``AgentApplication`` is not
            initialized (a custom ``handler=`` was supplied) or has no such attribute.
        """
        # Use __dict__ to avoid recursing through __getattr__ before _agent_app exists.
        agent_app = self.__dict__.get("_agent_app")
        if agent_app is not None:
            return getattr(agent_app, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. The M365 "
            "AgentApplication is not initialized because a custom handler= was supplied."
        )

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

    async def _create_activity_endpoint(  # pylint: disable=too-many-locals,too-many-statements
        self, request: Request
    ) -> Response:
        """Handle inbound POST to ``/activity/messages`` or ``/api/messages``.

        :param request: The inbound HTTP request.
        :type request: Request
        :return: The HTTP response.
        :rtype: Response
        """
        # Resolve correlation identifiers from headers up-front.
        inbound_conversation_id = request.headers.get(ActivityConstants.CONVERSATION_ID_HEADER, "")
        inbound_user_id = request.headers.get(USER_ID, "")
        inbound_call_id = request.headers.get(FOUNDRY_CALL_ID, "")
        session_id = self._resolve_session_id(request)
        request_trace_id = request.headers.get("x-request-id", "").strip()

        # Bind platform context so handler/tool code can forward the per-request
        # call ID and user ID, and so log records carry the correlation fields.
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

            # Extract conversation ID from the Activity payload, falling back to
            # the inbound conversation header.
            conversation_obj = payload.get("conversation", {})
            conversation_id = ""
            if isinstance(conversation_obj, dict):
                conversation_id = conversation_obj.get("id", "")
            if conversation_id and isinstance(conversation_id, str):
                conversation_id = conversation_id.strip()
            if not conversation_id and inbound_conversation_id:
                conversation_id = inbound_conversation_id.strip()

            # Pull common request details for logging.
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
            # Set the correlation baggage keys the core observability stack
            # promotes onto spans and log records.
            baggage_ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.session_id", session_id or "", context=baggage_ctx
            )
            if conversation_id:
                baggage_ctx = _otel_baggage.set_baggage(
                    "azure.ai.agentserver.conversation_id", conversation_id, context=baggage_ctx
                )
            baggage_token = _otel_context.attach(baggage_ctx)


            try:
                if self._handler is None:
                    raise NotImplementedError(
                        "No activity handler registered. Register handlers via "
                        "app.activity(...) or pass a handler= callable to "
                        "ActivityAgentServerHost()."
                    )
                response = await self._handler(request)  # type: ignore[assignment]

                response.headers[ActivityConstants.ACTIVITY_ID_HEADER] = activity_id
                self._add_required_response_headers(response, session_id)

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
            reset_request_context(ctx_token)
            if baggage_token is not None:
                try:
                    _otel_context.detach(baggage_token)
                except ValueError:
                    pass
