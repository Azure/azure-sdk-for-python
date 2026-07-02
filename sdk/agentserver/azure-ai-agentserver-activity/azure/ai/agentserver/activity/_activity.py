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
import re
import uuid
from collections.abc import Awaitable, Callable
from typing import Any, Optional

from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
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

# Maximum length and allowed characters for user-provided IDs (defense in depth).
_MAX_ID_LENGTH = 256
_VALID_ID_RE = re.compile(r"^[a-zA-Z0-9\-_.:]+$")


def _sanitize_id(value: str, fallback: str) -> str:
    """Validate a user-provided ID string.

    Returns *value* unchanged when it passes validation, otherwise *fallback*.
    Prevents excessively long or malformed IDs from propagating into headers,
    span attributes, and log messages.

    :param value: The raw ID from a header, query parameter, or payload.
    :type value: str
    :param fallback: A safe fallback value (typically a generated UUID).
    :type fallback: str
    :return: The validated ID or the fallback.
    :rtype: str
    """
    if not value or len(value) > _MAX_ID_LENGTH or not _VALID_ID_RE.match(value):
        return fallback
    return value


def _enrich_record(record: logging.LogRecord) -> None:
    """Populate activity scope fields on a log record from the request context.

    :param record: The log record to enrich.
    :type record: logging.LogRecord
    """
    ctx = get_request_context()
    if not hasattr(record, "SessionId"):
        setattr(record, "SessionId", ctx.session_id or "")
    if not hasattr(record, "UserId"):
        setattr(record, "UserId", ctx.user_id or "")
    if not hasattr(record, "CallId"):
        setattr(record, "CallId", ctx.call_id or "")
    if not hasattr(record, "Protocol"):
        setattr(record, "Protocol", ActivityConstants.PROTOCOL)


def _install_log_enrichment() -> None:
    """Install a log-record factory that enriches records with scope fields."""
    base_factory = logging.getLogRecordFactory()
    if getattr(base_factory, "_activity_enricher", False):
        return

    def _factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = base_factory(*args, **kwargs)
        _enrich_record(record)
        return record

    setattr(_factory, "_activity_enricher", True)
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
    the activity protocol endpoint at ``POST /activity/messages``. There are
    three, mutually-exclusive ways to construct a host — each maps to a distinct
    construction path, so an invalid combination cannot be expressed:

    1. **Build the M365 stack (default).** Construct directly. The M365 Agents
       SDK is initialized eagerly from the environment (optionally overriding
       ``storage`` / ``connection_manager`` / ``adapter`` / ``authorization`` /
       ``config``). The host then acts as the underlying ``AgentApplication``
       itself — register handlers with ``@app.activity(...)`` / ``@app.error``
       and reach the rest of the M365 surface (``message``/``proactive``/``auth``
       ...) directly on the host.
    2. **Inject a pre-built ``AgentApplication``.** Use
       :meth:`from_agent_application` to host an ``AgentApplication`` you built
       yourself, as-is.
    3. **Custom request handler.** Use :meth:`from_request_handler` to own the
       request pipeline entirely; the M365 SDK is not initialized and the
       handler receives the raw Starlette ``Request`` with
       ``request.state.activity`` set to the parsed dict.

    By default the host uses the **simple** agent auth model, suitable for a
    Microsoft Teams bot whose ``msaAppId`` is the agent instance
    identity. Pass ``digital_worker=True`` to switch to the digital-worker
    (blueprint + federated-identity) model. ``digital_worker`` applies to the
    two M365 modes (default and :meth:`from_agent_application`); it has no effect
    in custom-handler mode, where no outbound auth is performed by the host.

    Usage::

        from azure.ai.agentserver.activity import ActivityAgentServerHost

        app = ActivityAgentServerHost()  # simple Teams agent (default)

        @app.activity("message")
        async def on_message(context, state):
            await context.send_activity(f"Echo: {context.activity.text}")

        app.run()

    :keyword digital_worker: Selects the outbound-auth model. ``False`` (the
        default) is the **simple** model: the agent *instance* identity mints
        the Bot Connector token directly. ``True`` is the **digital-worker**
        model: the *blueprint* identity with the federated-identity (FMI)
        token exchange.
    :paramtype digital_worker: bool
    :keyword storage: Optional storage backend for the built M365 stack.
    :paramtype storage: object or None
    :keyword connection_manager: Optional M365 connection manager.
    :paramtype connection_manager: object or None
    :keyword adapter: Optional channel adapter.
    :paramtype adapter: object or None
    :keyword authorization: Optional M365 ``Authorization`` instance.
    :paramtype authorization: object or None
    :keyword config: Optional configuration mapping for the built M365 stack.
    :paramtype config: dict or None
    """

    def __init__(
        self,
        *,
        digital_worker: bool = False,
        storage: Optional[Any] = None,
        connection_manager: Optional[Any] = None,
        adapter: Optional[Any] = None,
        authorization: Optional[Any] = None,
        config: Optional[dict] = None,
        _handler: Optional[Callable[[Request], Awaitable[Response]]] = None,
        _agent_app: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        self._digital_worker = bool(digital_worker)

        self._agent_app: Any = None
        self._adapter: Any = None

        if _handler is not None:
            # Custom-handler mode (see from_request_handler): the caller owns the
            # pipeline; the M365 SDK is not initialized and no connection env is
            # seeded (none of it would be used).
            if not inspect.iscoroutinefunction(_handler):
                raise TypeError(
                    f"handler must be an async function, got {type(_handler).__name__}. "
                    "Use 'async def' to define your handler."
                )
            self._handler = _handler
        else:
            # Build the M365 stack (default), or use the injected _agent_app as-is
            # (see from_agent_application). The host then delegates to it (__getattr__).
            # Connection env is seeded inside build_m365_app, and only when it
            # reads the configuration from the environment itself (config=None) —
            # callers who bring their own config/connection_manager seed themselves.
            from ._m365_bridge import build_m365_app, make_bridge_handler
            self._agent_app, self._adapter = build_m365_app(
                digital_worker=self._digital_worker,
                storage=storage,
                connection_manager=connection_manager,
                adapter=adapter,
                authorization=authorization,
                config=config,
                agent_app=_agent_app,
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

        mode = "custom-handler" if _handler is not None else "m365"
        logger.info(
            "ActivityAgentServerHost initialized | mode=%s | digital_worker=%s",
            mode, self._digital_worker,
        )

    @classmethod
    def from_agent_application(
        cls,
        agent_app: Any,
        *,
        digital_worker: bool = False,
        **kwargs: Any,
    ) -> "ActivityAgentServerHost":
        """Host a pre-built M365 ``AgentApplication`` as-is.

        Use this when you have already constructed an ``AgentApplication`` (with
        your own storage / connection manager / authorization / adapter) and want
        the host to drive it through the activity turn pipeline without rebuilding
        it. The channel adapter is taken from ``agent_app.adapter`` (every
        ``AgentApplication`` is built with one).

        :param agent_app: A fully-built M365 ``AgentApplication`` to host. It must
            have been constructed with an adapter
            (``AgentApplication[TurnState](..., adapter=ADAPTER)``).
        :type agent_app: ~microsoft_agents.hosting.core.AgentApplication
        :keyword digital_worker: Selects the outbound-auth model (see the class
            docstring). Defaults to the simple model.
        :paramtype digital_worker: bool
        :return: A host bound to the injected ``AgentApplication``.
        :rtype: ActivityAgentServerHost
        """
        return cls(
            digital_worker=digital_worker,
            _agent_app=agent_app,
            **kwargs,
        )

    @classmethod
    def from_request_handler(
        cls,
        handler: Callable[[Request], Awaitable[Response]],
        **kwargs: Any,
    ) -> "ActivityAgentServerHost":
        """Host a custom async request handler and own the pipeline yourself.

        The handler receives the raw Starlette ``Request`` with ``request.state.activity`` set
        to the parsed activity dict, and must return a Starlette ``Response``.

        :param handler: An ``async def`` callable ``handler(request) -> Response``.
        :type handler: Callable[[~starlette.requests.Request], Awaitable[~starlette.responses.Response]]
        :return: A host that dispatches every request to ``handler``.
        :rtype: ActivityAgentServerHost
        """
        return cls(
            _handler=handler,
            **kwargs,
        )

    @property
    def adapter(self) -> Any:
        """The channel adapter for the underlying ``AgentApplication``.

        :return: The adapter, or ``None`` when the host was created via
            :meth:`from_request_handler`.
        :rtype: object
        """
        return self._adapter

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying ``AgentApplication``
        so handlers register directly on the host (``@app.activity`` / ``@app.error``).

        :param name: The attribute name being accessed.
        :type name: str
        :return: The corresponding attribute from the ``AgentApplication``.
        :rtype: object
        :raises AttributeError: If the M365 ``AgentApplication`` is not
            initialized (the host was created via
            :meth:`from_request_handler`) or has no such attribute.
        """
        # Use __dict__ to avoid recursing through __getattr__ before _agent_app exists.
        agent_app = self.__dict__.get("_agent_app")
        if agent_app is not None:
            return getattr(agent_app, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. The M365 "
            "AgentApplication is not initialized because the host was created via "
            "from_request_handler()."
        )

    @staticmethod
    def seed_connection_env(*, digital_worker: bool = False) -> None:
        """Seed the ``CONNECTIONS__*`` env vars the M365 SDK needs, in place.

        The default construction path calls this for you before it reads the
        configuration from the environment. Call it yourself **only** when you
        build the ``MsalConnectionManager`` (or the configuration) manually —
        whether to inject them into the constructor or to host a pre-built
        ``AgentApplication`` via :meth:`from_agent_application`. Do so
        **before** constructing the connection manager, otherwise it cannot
        mint the Bot Connector token.

        Existing values are never overwritten. The identity values are derived
        from the ``FOUNDRY_AGENT_*`` env vars Foundry injects into the container.

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

        :keyword digital_worker: Selects the outbound-auth model to seed for.
            Defaults to the simple model.
        :paramtype digital_worker: bool
        """

        def _get_nonempty(name: str) -> str:
            return os.environ.get(name, "").strip()

        def _set_if_missing(name: str, value: str) -> None:
            if value and not _get_nonempty(name):
                os.environ[name] = value

        if digital_worker:
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

    def _bad_request(self, message: str, session_id: str, reason: str) -> Response:
        """Build a 400 invalid_request response and stamp the session header.

        :param message: The human-readable error message for the response body.
        :type message: str
        :param session_id: The resolved session ID to stamp on the response.
        :type session_id: str
        :param reason: A short machine-readable reason code for the rejection log.
        :type reason: str
        :return: A 400 invalid_request response with the session header set.
        :rtype: ~starlette.responses.Response
        """
        logger.warning("Activity request rejected | reason=%s | session_id=%s", reason, session_id)
        response = create_error_response(
            "invalid_request",
            message,
            status_code=400,
            headers=_apply_error_source_headers({}, _ERROR_SOURCE_UPSTREAM),
        )
        self._add_required_response_headers(response, session_id)
        return response

    @staticmethod
    def _extract_request_meta(request: Request, payload: dict) -> dict[str, str]:
        """Extract the activity fields used for state, logging, and correlation.

        :param request: The inbound request (for the conversation fallback header).
        :type request: Request
        :param payload: The parsed activity dict.
        :type payload: dict
        :return: A mapping of sanitized/normalized activity fields.
        :rtype: dict[str, str]
        """
        raw_id = payload.get("id", "") if isinstance(payload.get("id"), str) else ""
        activity_id = _sanitize_id(raw_id, str(uuid.uuid4()))

        conversation_obj = payload.get("conversation", {})
        conversation_id = conversation_obj.get("id", "") if isinstance(conversation_obj, dict) else ""
        conversation_id = conversation_id.strip() if isinstance(conversation_id, str) else ""
        if not conversation_id:
            conversation_id = request.headers.get(ActivityConstants.CONVERSATION_ID_HEADER, "").strip()

        from_obj = payload.get("from", {})
        recipient_obj = payload.get("recipient", {})
        return {
            "activity_id": activity_id,
            "conversation_id": conversation_id,
            "type": payload.get("type", "") or "",
            "from_id": from_obj.get("id", "") if isinstance(from_obj, dict) else "",
            "recipient_id": recipient_obj.get("id", "") if isinstance(recipient_obj, dict) else "",
            "channel_id": payload.get("channelId", "") or "",
            "service_url": payload.get("serviceUrl", "") or "",
            "locale": payload.get("locale", "") or "",
            "x_request_id": request.headers.get("x-request-id", "").strip(),
        }

    @staticmethod
    def _set_correlation_baggage(session_id: str, conversation_id: str) -> Any:
        """Attach the correlation baggage keys the core stack promotes onto spans/logs.

        :param session_id: The resolved session ID.
        :type session_id: str
        :param conversation_id: The resolved conversation ID (may be empty).
        :type conversation_id: str
        :return: The context token to detach when the turn completes.
        :rtype: object
        """
        ctx = _otel_baggage.set_baggage(
            "azure.ai.agentserver.session_id", session_id or "", context=_otel_context.get_current()
        )
        if conversation_id:
            ctx = _otel_baggage.set_baggage(
                "azure.ai.agentserver.conversation_id", conversation_id, context=ctx
            )
        return _otel_context.attach(ctx)

    async def _run_handler(
        self, request: Request, activity_id: str, conversation_id: str, session_id: str
    ) -> Response:
        """Invoke the registered handler and classify any failure into a 500.

        :param request: The inbound request.
        :type request: Request
        :param activity_id: The sanitized activity ID.
        :type activity_id: str
        :param conversation_id: The resolved conversation ID.
        :type conversation_id: str
        :param session_id: The resolved session ID.
        :type session_id: str
        :return: The handler's response, or a classified 500 error response.
        :rtype: Response
        """
        try:
            if self._handler is None:
                raise NotImplementedError(
                    "No activity handler registered. Register handlers via "
                    "app.activity(...), or create the host with "
                    "ActivityAgentServerHost.from_request_handler(fn)."
                )
            response = await self._handler(request)
            response.headers[ActivityConstants.ACTIVITY_ID_HEADER] = activity_id
            self._add_required_response_headers(response, session_id)
            logger.info(
                "Activity response sent | status_code=%s | activity_id=%s | "
                "conversation_id=%s | session_id=%s",
                getattr(response, "status_code", 0), activity_id, conversation_id, session_id,
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

    async def _create_activity_endpoint(self, request: Request) -> Response:
        """Handle inbound POST to ``/activity/messages`` or ``/api/messages``.

        :param request: The inbound HTTP request.
        :type request: Request
        :return: The HTTP response.
        :rtype: Response
        """
        inbound_user_id = request.headers.get(USER_ID, "")
        inbound_call_id = request.headers.get(FOUNDRY_CALL_ID, "")
        session_id = _sanitize_id(self._resolve_session_id(request), str(uuid.uuid4()))

        # Bind platform context so handler/tool code can forward the per-request
        # call ID and user ID, and so log records carry the correlation fields.
        ctx_token = set_request_context(
            FoundryAgentRequestContext(
                call_id=inbound_call_id or None,
                user_id=inbound_user_id or None,
                session_id=session_id,
            )
        )
        baggage_token: Optional[Any] = None
        try:
            try:
                payload = await request.json()
            except Exception:  # pylint: disable=broad-exception-caught
                return self._bad_request("Request body must be valid JSON", session_id, "invalid_json")
            if not isinstance(payload, dict):
                return self._bad_request(
                    "Activity payload must be a JSON object", session_id, "non_object_payload"
                )

            meta = self._extract_request_meta(request, payload)
            activity_id = meta["activity_id"]
            conversation_id = meta["conversation_id"]

            request.state.activity = payload

            logger.info(
                "Activity request received | type=%s | activity_id=%s | conversation_id=%s | "
                "session_id=%s | from=%s | recipient=%s | channelId=%s | serviceUrl=%s | "
                "locale=%s | x_request_id=%s",
                meta["type"], activity_id, conversation_id, session_id, meta["from_id"],
                meta["recipient_id"], meta["channel_id"], meta["service_url"], meta["locale"],
                meta["x_request_id"],
            )

            baggage_token = self._set_correlation_baggage(session_id, conversation_id)
            return await self._run_handler(request, activity_id, conversation_id, session_id)
        finally:
            reset_request_context(ctx_token)
            if baggage_token is not None:
                try:
                    _otel_context.detach(baggage_token)
                except ValueError:
                    pass
