# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol host for Azure AI Hosted Agents.

Home of :class:`ActivityAgentServerHost` — an
:class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds the
activity protocol endpoint (``POST /activity/messages``).

This module wires the endpoint end to end: request parsing and validation,
session / correlation resolution, log-record enrichment, OpenTelemetry baggage,
error-source classification, and dispatch to one of the three construction modes
(built M365 stack, injected ``AgentApplication``, or custom request handler). The
M365 stack build lives in :mod:`._m365_bridge` and the Starlette turn adapter in
:mod:`._cloud_adapter`.
"""

from __future__ import annotations

import inspect
import logging
import re
import uuid
from collections.abc import Awaitable, Callable, Mapping
from contextvars import Token
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from opentelemetry import baggage as _otel_baggage
from opentelemetry import context as _otel_context
from opentelemetry import trace as _otel_trace
from opentelemetry.context import Context
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from azure.ai.agentserver.core import (
    AgentServerHost,
    FoundryAgentRequestContext,
    build_server_version,
    create_error_response,
    detach_context,
    end_span,
    flush_spans,
    get_request_context,
    reset_request_context,
    set_current_span,
    set_request_context,
)
from azure.ai.agentserver.core._platform_headers import (  # pylint: disable=import-error,no-name-in-module
    ERROR_DETAIL,
    ERROR_SOURCE,
    FOUNDRY_CALL_ID,
    MAX_ERROR_DETAIL_LENGTH,
    PLATFORM_ERROR_TAG,
    USER_ID,
)

from ._config import get_hosted_agent_env
from ._constants import (
    MAX_ID_LENGTH,
    VALID_ID_PATTERN,
    ActivityConstants,
    ActivityFields,
    BaggageKeys,
    ConnectionSettings,
    ErrorCode,
    ErrorSource,
    LogRecordFields,
    SpanAttributes,
)
from ._version import VERSION as _ACTIVITY_VERSION

if TYPE_CHECKING:  # pragma: no cover - type-only imports (M365 SDK is optional)
    from microsoft_agents.hosting.core import (
        AgentApplication,
        Authorization,
        HttpAdapterBase,
        Storage,
    )
    from microsoft_agents.authentication.msal import MsalConnectionManager

logger = logging.getLogger("azure.ai.agentserver.activity.host")

_VALID_ID_RE = re.compile(VALID_ID_PATTERN)


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
    if not value or len(value) > MAX_ID_LENGTH or not _VALID_ID_RE.match(value):
        return fallback
    return value


def _scrub_for_log(value: str) -> str:
    """Strip control characters so untrusted values cannot forge log lines.

    Activity fields and request headers are written to a line-oriented log; a
    value containing ``\\r``/``\\n`` (or other control characters) could
    otherwise inject additional, attacker-controlled log records.

    :param value: The raw value to sanitize.
    :type value: str
    :return: The value with control characters removed.
    :rtype: str
    """
    if not value:
        return value
    return "".join(ch for ch in value if ch == " " or (ch.isprintable() and ch not in "\r\n\t"))


def _enrich_record(record: logging.LogRecord) -> None:
    """Populate activity scope fields on a log record from the request context.

    :param record: The log record to enrich.
    :type record: logging.LogRecord
    """
    ctx = get_request_context()
    if not hasattr(record, LogRecordFields.SESSION_ID):
        setattr(record, LogRecordFields.SESSION_ID, ctx.session_id or "")
    if not hasattr(record, LogRecordFields.USER_ID):
        setattr(record, LogRecordFields.USER_ID, ctx.user_id or "")
    if not hasattr(record, LogRecordFields.CALL_ID):
        setattr(record, LogRecordFields.CALL_ID, ctx.call_id or "")
    if not hasattr(record, LogRecordFields.PROTOCOL):
        setattr(record, LogRecordFields.PROTOCOL, ActivityConstants.PROTOCOL)


def _install_log_enrichment() -> None:
    """Install a log-record factory that enriches records with scope fields."""
    base_factory = logging.getLogRecordFactory()
    if getattr(base_factory, LogRecordFields.ENRICHER_FLAG, False):
        return

    def factory(*args: object, **kwargs: object) -> logging.LogRecord:
        record = base_factory(*args, **kwargs)
        _enrich_record(record)
        return record

    setattr(factory, LogRecordFields.ENRICHER_FLAG, True)
    logging.setLogRecordFactory(factory)


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
        # Keep only ASCII printable characters. This strips CR/LF (so request-
        # derived exception text cannot inject headers or split the response) and
        # also drops non-latin-1 code points that Starlette cannot encode into an
        # HTTP header value.
        sanitized_detail = "".join(ch for ch in error_detail if ch == " " or (ch.isascii() and ch.isprintable()))
        if sanitized_detail:
            merged[ERROR_DETAIL] = sanitized_detail
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
        return ErrorSource.PLATFORM, detail
    return ErrorSource.UPSTREAM, None


@dataclass(frozen=True)
class _RequestMeta:
    """Activity fields extracted for state, logging, and correlation.

    A typed, immutable view of the fields the host reads from an inbound activity
    (rather than a loose ``dict``), so downstream logging / correlation access
    named attributes.

    :ivar activity_id: The sanitized activity id (a generated UUID when absent).
    :vartype activity_id: str
    :ivar conversation_id: The conversation id (falls back to the request header).
    :vartype conversation_id: str
    :ivar type: The activity type.
    :vartype type: str
    :ivar from_id: The ``from`` account id.
    :vartype from_id: str
    :ivar recipient_id: The ``recipient`` account id.
    :vartype recipient_id: str
    :ivar channel_id: The channel id.
    :vartype channel_id: str
    :ivar service_url: The service URL.
    :vartype service_url: str
    :ivar locale: The activity locale.
    :vartype locale: str
    :ivar x_request_id: The inbound ``x-request-id`` correlation header.
    :vartype x_request_id: str
    """

    activity_id: str
    conversation_id: str
    type: str
    from_id: str
    recipient_id: str
    channel_id: str
    service_url: str
    locale: str
    x_request_id: str


class ActivityAgentServerHost(AgentServerHost):
    """Activity protocol host for Azure AI Hosted Agents.

    A :class:`~azure.ai.agentserver.core.AgentServerHost` subclass that adds
    the activity protocol endpoint at ``POST /activity/messages``. A single
    constructor selects one of three mutually-exclusive modes from the arguments
    you pass (an invalid combination raises ``ValueError``):

    1. **Build the M365 stack (default).** Pass neither ``agent_app`` nor
       ``request_handler``. The M365 Agents SDK is initialized eagerly from the
       environment (optionally overriding ``storage`` / ``connection_manager`` /
       ``adapter`` / ``authorization`` / ``connection_config``). The built
       ``AgentApplication`` is exposed as the :attr:`agent_app` property —
       capture it (``app = host.agent_app``) and register handlers with
       ``@app.activity(...)`` / ``@app.error``, reaching the rest of the M365
       surface (``message`` / ``proactive`` / ``auth`` ...) the same way.
    2. **Inject a pre-built ``AgentApplication``.** Pass ``agent_app=<app>`` to
       host an ``AgentApplication`` you built yourself, as-is. It is exposed as
       :attr:`agent_app`.
    3. **Custom request handler.** Pass ``request_handler=<fn>`` to own the
       request pipeline entirely; the M365 SDK is not initialized, :attr:`agent_app`
       is unavailable, and the handler receives the raw Starlette ``Request``
       with ``request.state.activity`` set to the parsed dict.

    See the package overview (:mod:`azure.ai.agentserver.activity`) for runnable
    usage examples of all three construction modes.

    :keyword agent_app: A pre-built M365 ``AgentApplication`` to host as-is
        (mode 2). Mutually exclusive with ``request_handler`` and with the
        M365-build overrides. Defaults to ``None`` (build the stack).
    :paramtype agent_app: Optional[~microsoft_agents.hosting.core.AgentApplication]
    :keyword request_handler: A custom ``async def handler(request) -> Response``
        that owns the pipeline (mode 3). Mutually exclusive with ``agent_app``
        and the M365-build overrides. Defaults to ``None``.
    :paramtype request_handler:
        Optional[Callable[[~starlette.requests.Request],
        Awaitable[~starlette.responses.Response]]]
    :keyword digital_worker: Selects the outbound-auth model. ``False`` (the
        default) is the **simple** model: the agent *instance* identity mints
        the Bot Connector token directly. ``True`` is the **digital-worker**
        model: the *blueprint* identity with the federated-identity (FMI)
        token exchange.
    :paramtype digital_worker: bool
    :keyword storage: Optional storage backend for the built M365 stack.
    :paramtype storage: Optional[~microsoft_agents.hosting.core.Storage]
    :keyword connection_manager: Optional M365 connection manager.
    :paramtype connection_manager:
        Optional[~microsoft_agents.authentication.msal.MsalConnectionManager]
    :keyword adapter: Optional channel adapter.
    :paramtype adapter: Optional[~microsoft_agents.hosting.core.HttpAdapterBase]
    :keyword authorization: Optional M365 ``Authorization`` instance.
    :paramtype authorization: Optional[~microsoft_agents.hosting.core.Authorization]
    :keyword connection_config: Optional connection config (the M365
        ``CONNECTIONS__*`` mapping) for the built M365 stack. When supplied it
        also drives the outbound-auth client id, and it is exposed after
        construction as :attr:`connection_config`.
    :paramtype connection_config: Optional[Mapping[str, str]]
    """

    def __init__(
        self,
        *,
        agent_app: Optional[AgentApplication] = None,
        request_handler: Optional[Callable[[Request], Awaitable[Response]]] = None,
        digital_worker: bool = False,
        storage: Optional[Storage] = None,
        connection_manager: Optional[MsalConnectionManager] = None,
        adapter: Optional[HttpAdapterBase] = None,
        authorization: Optional[Authorization] = None,
        connection_config: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the host, selecting the construction mode from the arguments.

        The mode is inferred from which of ``agent_app`` / ``request_handler`` is
        supplied (see the class docstring); passing an invalid combination raises
        ``ValueError`` so a bad configuration cannot be expressed.

        :keyword agent_app: A pre-built ``AgentApplication`` to host as-is, or
            ``None`` to build the M365 stack. Mutually exclusive with
            ``request_handler`` and the M365-build overrides.
        :paramtype agent_app: Optional[~microsoft_agents.hosting.core.AgentApplication]
        :keyword request_handler: A custom async request handler that owns the
            pipeline, or ``None``. Mutually exclusive with ``agent_app`` and the
            M365-build overrides.
        :paramtype request_handler:
            Optional[Callable[[~starlette.requests.Request],
            Awaitable[~starlette.responses.Response]]]
        :keyword digital_worker: Selects the outbound-auth model (see the class
            docstring). Defaults to the simple model.
        :paramtype digital_worker: bool
        :keyword storage: Optional storage backend for the built M365 stack.
        :paramtype storage: Optional[~microsoft_agents.hosting.core.Storage]
        :keyword connection_manager: Optional M365 connection manager.
        :paramtype connection_manager:
            Optional[~microsoft_agents.authentication.msal.MsalConnectionManager]
        :keyword adapter: Optional channel adapter.
        :paramtype adapter: Optional[~microsoft_agents.hosting.core.HttpAdapterBase]
        :keyword authorization: Optional M365 ``Authorization`` instance.
        :paramtype authorization: Optional[~microsoft_agents.hosting.core.Authorization]
        :keyword connection_config: Optional connection config (the M365
            ``CONNECTIONS__*`` mapping) for the built M365 stack. When supplied it
            also drives the outbound-auth client id, and it is exposed after
            construction as :attr:`connection_config`.
        :paramtype connection_config: Optional[Mapping[str, str]]
        :raises ValueError: If ``agent_app`` and ``request_handler`` are both
            supplied, or if either is combined with an M365-build override.
        :return: None.
        :rtype: None
        """
        # Validate the mode selection up front so an invalid combination is
        # rejected instead of silently ignoring the extra arguments.
        if agent_app is not None and request_handler is not None:
            raise ValueError("Pass either 'agent_app' or 'request_handler', not both.")
        build_overrides = {
            "storage": storage,
            "connection_manager": connection_manager,
            "adapter": adapter,
            "authorization": authorization,
            "connection_config": connection_config,
        }
        if request_handler is not None:
            supplied = [name for name, value in build_overrides.items() if value is not None]
            if supplied:
                raise ValueError(
                    "request_handler mode does not build the M365 stack; remove the "
                    f"M365-build override(s): {', '.join(supplied)}."
                )
        elif agent_app is not None:
            supplied = [name for name, value in build_overrides.items() if value is not None]
            if supplied:
                raise ValueError(
                    "agent_app is hosted as-is; the M365-build override(s) "
                    f"{', '.join(supplied)} would be ignored. Remove them, or drop "
                    "agent_app to let the host build the stack."
                )

        self._digital_worker: bool = bool(digital_worker)
        self._agent_app: Optional[AgentApplication] = None
        self._adapter: Optional[HttpAdapterBase] = None
        self._handler: Optional[Callable[[Request], Awaitable[Response]]] = None
        self._connection_config: Optional[Mapping[str, str]] = None

        # Register the activity routes and initialize the base host first, so the
        # core-resolved configuration (``self.config``, resolved once) is available
        # to the M365 build below.
        activity_routes: list[Route] = self._build_activity_routes()
        existing_routes: list[Route] = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing_routes + activity_routes, **kwargs)

        # Register this package's version so the ``x-platform-server`` header
        # advertises the activity protocol segment (core requires each protocol
        # package to register its own version).
        self.register_server_version(
            build_server_version("azure-ai-agentserver-activity", _ACTIVITY_VERSION)
        )

        if request_handler is not None:
            # Custom-handler mode: the caller owns the pipeline; the M365 SDK is
            # not initialized and agent_app stays unavailable.
            if not inspect.iscoroutinefunction(request_handler):
                raise TypeError(
                    f"request_handler must be an async function, got "
                    f"{type(request_handler).__name__}. Use 'async def' to define it."
                )
            self._handler = request_handler
        else:
            # Build the M365 stack (default) or host the injected agent_app as-is.
            self._build_m365_stack(
                agent_app=agent_app,
                storage=storage,
                connection_manager=connection_manager,
                adapter=adapter,
                authorization=authorization,
                connection_config=connection_config,
            )

        # Install logging enrichment for this host. The core observability stack
        # promotes session_id / conversation_id baggage onto spans and logs.
        _install_log_enrichment()

        mode = "custom-handler" if request_handler is not None else "m365"
        logger.info(
            "ActivityAgentServerHost initialized | mode=%s | digital_worker=%s",
            mode,
            self._digital_worker,
        )

    def _build_m365_stack(
        self,
        *,
        agent_app: Optional[AgentApplication],
        storage: Optional[Storage],
        connection_manager: Optional[MsalConnectionManager],
        adapter: Optional[HttpAdapterBase],
        authorization: Optional[Authorization],
        connection_config: Optional[Mapping[str, str]],
    ) -> None:
        """Build the M365 stack (default) or host the injected ``agent_app`` as-is.

        Resolves the connection config ONCE (caller-supplied ``connection_config``
        or the values derived from the Foundry-native identity), then reads the
        outbound-auth inputs from that single mapping so per-request auth never
        re-reads process-global state. Sets :attr:`_connection_config`,
        :attr:`_agent_app`, :attr:`_adapter` and :attr:`_handler`.

        :keyword agent_app: The pre-built ``AgentApplication`` to inject, or ``None``.
        :paramtype agent_app: Optional[~microsoft_agents.hosting.core.AgentApplication]
        :keyword storage: Optional storage backend for the built M365 stack.
        :paramtype storage: Optional[~microsoft_agents.hosting.core.Storage]
        :keyword connection_manager: Optional M365 connection manager.
        :paramtype connection_manager:
            Optional[~microsoft_agents.authentication.msal.MsalConnectionManager]
        :keyword adapter: Optional channel adapter.
        :paramtype adapter: Optional[~microsoft_agents.hosting.core.HttpAdapterBase]
        :keyword authorization: Optional M365 ``Authorization`` instance.
        :paramtype authorization: Optional[~microsoft_agents.hosting.core.Authorization]
        :keyword connection_config: Optional connection config for the built stack.
        :paramtype connection_config: Optional[Mapping[str, str]]
        :return: None.
        :rtype: None
        """
        from ._m365_bridge import build_bridge_handler, build_m365_app

        self._connection_config = (
            connection_config
            if connection_config is not None
            else get_hosted_agent_env(digital_worker=self._digital_worker)
        )
        bot_app_id = self._connection_config.get(ConnectionSettings.CLIENT_ID, "").strip()
        self._agent_app, self._adapter = build_m365_app(
            digital_worker=self._digital_worker,
            connection_config=self._connection_config,
            storage=self._resolve_storage(storage) if agent_app is None else storage,
            connection_manager=connection_manager,
            adapter=adapter,
            authorization=authorization,
            agent_app=agent_app,
        )
        self._handler = build_bridge_handler(
            self._agent_app,
            self._adapter,
            digital_worker=self._digital_worker,
            is_hosted=self.config.is_hosted,
            bot_app_id=bot_app_id,
        )

    def _build_activity_routes(self) -> list[Route]:
        """Build the activity protocol routes registered on the host.

        Override in a subclass to customize or extend the activity endpoints
        (for example, to add an alternate path or change the HTTP methods).

        :return: The routes to register for the activity protocol endpoint.
        :rtype: list[~starlette.routing.Route]
        """
        return [
            Route(
                ActivityConstants.ACTIVITY_MESSAGES_PATH,
                self._create_activity_endpoint,
                methods=["POST"],
                name=ActivityConstants.ACTIVITY_ROUTE_NAME,
            ),
            Route(
                ActivityConstants.API_MESSAGES_PATH,
                self._create_activity_endpoint,
                methods=["POST"],
                name=ActivityConstants.API_MESSAGES_ROUTE_NAME,
            ),
        ]

    def _resolve_storage(self, storage: Optional[Storage]) -> Storage:
        """Resolve the storage backend for the built M365 stack.

        Resolution order: the caller-supplied ``storage`` if provided, otherwise
        an in-memory store suitable for local testing. Override in a subclass to
        plug a durable backend (for example a hosted persistent store).

        :param storage: The caller-supplied storage backend, or ``None``.
        :type storage: Optional[~microsoft_agents.hosting.core.Storage]
        :return: The storage backend to use.
        :rtype: ~microsoft_agents.hosting.core.Storage
        """
        if storage is not None:
            return storage
        # TODO: use a durable hosted store (FoundryStorage) when running in a
        # Foundry-hosted container; MemoryStorage is the local-testing default.
        # pylint: disable=import-error,no-name-in-module
        from microsoft_agents.hosting.core import MemoryStorage

        return MemoryStorage()

    @property
    def connection_config(self) -> Optional[Mapping[str, str]]:
        """The resolved M365 ``CONNECTIONS__*`` mapping used to build the stack.

        Exposes the connection config the host resolved (the caller-supplied
        ``connection_config`` keyword, or the values derived from the
        Foundry-native identity) so callers can inspect the exact settings the
        M365 stack was built from. Distinct from :attr:`config` (the core Foundry
        ``AgentConfig``). ``None`` when the host was created with a custom
        ``request_handler`` (the M365 stack is not built in that mode).

        :return: The resolved connection config, or ``None`` in custom-handler mode.
        :rtype: Optional[Mapping[str, str]]
        """
        return self._connection_config

    @property
    def agent_app(self) -> AgentApplication:
        """The underlying M365 ``AgentApplication`` for handler registration.

        Capture it (``app = host.agent_app``) and register handlers on it, for
        example ``@app.activity("message")`` / ``@app.error``, or use it
        standalone.

        :return: The hosted ``AgentApplication``.
        :rtype: ~microsoft_agents.hosting.core.AgentApplication
        :raises AttributeError: When the host was created with a custom
            ``request_handler`` (custom-handler mode), where no
            ``AgentApplication`` is initialized.
        """
        agent_app = self._agent_app
        if agent_app is None:
            raise AttributeError(
                "The M365 AgentApplication is not initialized because the host was "
                "created with a custom request_handler. Construct the host without "
                "request_handler (optionally passing agent_app=<app>) to use agent_app."
            )
        return agent_app

    @property
    def adapter(self) -> Optional[HttpAdapterBase]:
        """The channel adapter for the underlying ``AgentApplication``.

        :return: The adapter, or ``None`` when the host was created with a custom
            ``request_handler``.
        :rtype: Optional[~microsoft_agents.hosting.core.HttpAdapterBase]
        """
        return self._adapter

    def _resolve_session_id(self, request: Request) -> str:
        query_session_id = request.query_params.get(ActivityConstants.SESSION_ID_QUERY_PARAM)
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

    def _build_bad_request(self, message: str, session_id: str, reason: str) -> Response:
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
            ErrorCode.INVALID_REQUEST,
            message,
            status_code=400,
            headers=_apply_error_source_headers({}, ErrorSource.USER),
        )
        self._add_required_response_headers(response, session_id)
        return response

    @staticmethod
    def _extract_request_meta(request: Request, payload: Mapping[str, object]) -> _RequestMeta:
        """Extract the activity fields used for state, logging, and correlation.

        :param request: The inbound request (for the conversation fallback header).
        :type request: ~starlette.requests.Request
        :param payload: The parsed activity dict.
        :type payload: Mapping[str, object]
        :return: The typed activity metadata.
        :rtype: _RequestMeta
        """

        def as_str(value: object) -> str:
            return value if isinstance(value, str) else ""

        def nested_id(value: object) -> str:
            return as_str(value.get(ActivityFields.ID)) if isinstance(value, dict) else ""

        activity_id = _sanitize_id(as_str(payload.get(ActivityFields.ID)), str(uuid.uuid4()))

        conversation_id = nested_id(payload.get(ActivityFields.CONVERSATION)).strip()
        if not conversation_id:
            conversation_id = request.headers.get(ActivityConstants.CONVERSATION_ID_HEADER, "").strip()

        return _RequestMeta(
            activity_id=activity_id,
            conversation_id=conversation_id,
            type=as_str(payload.get(ActivityFields.TYPE)),
            from_id=nested_id(payload.get(ActivityFields.FROM)),
            recipient_id=nested_id(payload.get(ActivityFields.RECIPIENT)),
            channel_id=as_str(payload.get(ActivityFields.CHANNEL_ID)),
            service_url=as_str(payload.get(ActivityFields.SERVICE_URL)),
            locale=as_str(payload.get(ActivityFields.LOCALE)),
            x_request_id=request.headers.get(ActivityConstants.REQUEST_ID_HEADER, "").strip(),
        )

    @staticmethod
    def _set_correlation_baggage(session_id: str, conversation_id: str) -> Token[Context]:
        """Attach the correlation baggage keys the core stack promotes onto spans/logs.

        :param session_id: The resolved session ID.
        :type session_id: str
        :param conversation_id: The resolved conversation ID (may be empty).
        :type conversation_id: str
        :return: The context token to detach when the turn completes.
        :rtype: ~contextvars.Token
        """
        ctx = _otel_baggage.set_baggage(BaggageKeys.SESSION_ID, session_id or "", context=_otel_context.get_current())
        # Always set the conversation-id baggage (even to empty) so a stale or
        # untrusted value inherited from the inbound context cannot leak into the
        # current turn's spans/logs.
        ctx = _otel_baggage.set_baggage(BaggageKeys.CONVERSATION_ID, conversation_id or "", context=ctx)
        return _otel_context.attach(ctx)

    def _build_invoke_span_attrs(self, activity_id: str, conversation_id: str, session_id: str) -> dict[str, str]:
        """Build the attributes for the per-turn ``invoke_agent`` span.

        The agent name / version / id and the project id are set here directly
        so they are guaranteed to be present on this one span, together with the
        per-turn id (the activity id). That combination is what makes the turn
        show up as a row in the trace list. Only values that are actually
        available are added, so a local run without the platform environment
        variables does not emit blank attributes.

        :param activity_id: The sanitized activity ID, used as the per-turn id.
        :type activity_id: str
        :param conversation_id: The resolved conversation ID (may be empty).
        :type conversation_id: str
        :param session_id: The resolved session ID.
        :type session_id: str
        :return: A mapping of span attribute keys to values.
        :rtype: dict[str, str]
        """
        attrs: dict[str, str] = {
            SpanAttributes.GEN_AI_OPERATION_NAME: SpanAttributes.OPERATION_NAME_VALUE,
            SpanAttributes.GEN_AI_SYSTEM: SpanAttributes.GEN_AI_SYSTEM_VALUE,
        }
        if activity_id:
            attrs[SpanAttributes.RESPONSE_ID] = activity_id
        if self.config.agent_name:
            attrs[SpanAttributes.GEN_AI_AGENT_NAME] = self.config.agent_name
        if self.config.agent_version:
            attrs[SpanAttributes.GEN_AI_AGENT_VERSION] = self.config.agent_version
        if self.config.agent_id:
            attrs[SpanAttributes.GEN_AI_AGENT_ID] = self.config.agent_id
        if self.config.project_id:
            attrs[SpanAttributes.FOUNDRY_PROJECT_ID] = self.config.project_id
        if conversation_id:
            attrs[SpanAttributes.GEN_AI_CONVERSATION_ID] = conversation_id
        if session_id:
            attrs[SpanAttributes.SESSION_ID] = session_id
        return attrs

    async def _run_handler(self, request: Request, activity_id: str, conversation_id: str, session_id: str) -> Response:
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
        tracer = _otel_trace.get_tracer("azure.ai.agentserver.activity")
        span = tracer.start_span(
            SpanAttributes.SPAN_NAME,
            attributes=self._build_invoke_span_attrs(activity_id, conversation_id, session_id),
        )
        span_token = set_current_span(span)
        error: Optional[BaseException] = None
        try:
            if self._handler is None:
                raise NotImplementedError(
                    "No activity handler registered. Register handlers on the"
                    " agent app (app = host.agent_app; @app.activity(...)), or"
                    " create the host with ActivityAgentServerHost(request_handler=fn)."
                )
            response = await self._handler(request)
            response.headers[ActivityConstants.ACTIVITY_ID_HEADER] = activity_id
            self._add_required_response_headers(response, session_id)
            # The package contract guarantees an error-source on every error
            # response. A handler (or the M365 adapter) can return a 4xx/5xx
            # directly without raising, which skips the exception path below, so
            # classify any unclassified error status as ``upstream`` here.
            status_code = getattr(response, "status_code", 0)
            if status_code >= 400 and ERROR_SOURCE not in response.headers:
                response.headers[ERROR_SOURCE] = ErrorSource.UPSTREAM
            logger.info(
                "Activity response sent | status_code=%s | activity_id=%s | conversation_id=%s | session_id=%s",
                status_code,
                activity_id,
                conversation_id,
                session_id,
            )
            return response
        except Exception as exc:  # pylint: disable=broad-exception-caught
            error = exc
            error_source, error_detail = _classify_error(exc)
            logger.error(
                "Activity request failed | activity_id=%s | conversation_id=%s | "
                "session_id=%s | error_source=%s | error=%s",
                activity_id,
                conversation_id,
                session_id,
                error_source,
                exc,
                exc_info=True,
            )
            response = create_error_response(
                ErrorCode.INTERNAL_ERROR,
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
            if span_token is not None:
                detach_context(span_token)
            end_span(span, exc=error)
            flush_spans()

    async def _create_activity_endpoint(self, request: Request) -> Response:
        """Handle inbound POST to ``/activity/messages``.

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
        baggage_token: Optional[Token[Context]] = None
        try:
            try:
                payload = await request.json()
            except Exception:  # pylint: disable=broad-exception-caught
                return self._build_bad_request("Request body must be valid JSON", session_id, "invalid_json")
            if not isinstance(payload, dict):
                return self._build_bad_request(
                    "Activity payload must be a JSON object", session_id, "non_object_payload"
                )

            meta = self._extract_request_meta(request, payload)
            activity_id = meta.activity_id
            conversation_id = meta.conversation_id

            request.state.activity = payload
            logger.info(
                "Activity request received | type=%s | activity_id=%s | conversation_id=%s | "
                "session_id=%s | from=%s | recipient=%s | channelId=%s | serviceUrl=%s | "
                "locale=%s | x_request_id=%s",
                _scrub_for_log(meta.type),
                activity_id,
                _scrub_for_log(conversation_id),
                session_id,
                _scrub_for_log(meta.from_id),
                _scrub_for_log(meta.recipient_id),
                _scrub_for_log(meta.channel_id),
                _scrub_for_log(meta.service_url),
                _scrub_for_log(meta.locale),
                _scrub_for_log(meta.x_request_id),
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
