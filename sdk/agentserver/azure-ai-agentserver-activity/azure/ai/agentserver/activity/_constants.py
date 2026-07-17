# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol constants.

All domain/magic strings used by the activity host live here: header names,
routing, M365 connection-manager configuration keys, outbound-auth scopes and
claims, the digital-worker MSAL patch, OpenTelemetry baggage keys, log-record
field names, error classification values, and inbound activity field names.

Cross-cutting header names (for example the session ID header) are imported
from :mod:`azure.ai.agentserver.core._platform_headers`.
"""

from azure.ai.agentserver.core._platform_headers import (  # pylint: disable=import-error,no-name-in-module
    SESSION_ID as _SESSION_ID,
)


class ActivityConstants:
    """Activity protocol header, routing, and query-parameter constants."""

    PROTOCOL: str = "activity"

    # Request / response headers
    ACTIVITY_ID_HEADER: str = "x-agent-activity-id"
    SESSION_ID_HEADER: str = _SESSION_ID
    CONVERSATION_ID_HEADER: str = "x-agent-conversation-id"
    REQUEST_ID_HEADER: str = "x-request-id"

    # Query parameters
    SESSION_ID_QUERY_PARAM: str = "agent_session_id"

    # Routing
    ACTIVITY_MESSAGES_PATH: str = "/activity/messages"
    API_MESSAGES_PATH: str = "/api/messages"
    ACTIVITY_ROUTE_NAME: str = "create_activity"
    API_MESSAGES_ROUTE_NAME: str = "create_activity_api_messages"


class FoundryEnv:
    """Foundry-native environment variable names read directly by the activity host.

    Tenant ID and blueprint client ID are resolved via the core helpers
    (``resolve_agent_tenant_id`` / ``resolve_agent_blueprint_id``). Only the
    instance client ID is read here, because the core resolver
    (``resolve_agent_id``) applies a ``name:version`` fallback that is not
    appropriate for the outbound Bot Connector credential.
    """

    INSTANCE_CLIENT_ID: str = "FOUNDRY_AGENT_INSTANCE_CLIENT_ID"


class ConnectionSettings:
    """M365 connection-manager configuration keys and values.

    The M365 SDK reads these ``CONNECTIONS__*`` / ``CONNECTIONSMAP__*`` keys from
    its configuration mapping to build the Bot Connector connection manager.
    """

    # Keys
    CLIENT_ID: str = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__CLIENTID"
    TENANT_ID: str = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__TENANTID"
    AUTHORITY: str = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHORITY"
    AUTH_TYPE: str = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__AUTHTYPE"
    SCOPE_0: str = "CONNECTIONS__SERVICE_CONNECTION__SETTINGS__SCOPES__0"
    MAP_0_SERVICE_URL: str = "CONNECTIONSMAP__0__SERVICEURL"
    MAP_0_CONNECTION: str = "CONNECTIONSMAP__0__CONNECTION"

    # Values
    AUTH_TYPE_USER_MANAGED_IDENTITY: str = "UserManagedIdentity"
    MAP_SERVICE_URL_WILDCARD: str = "*"
    SERVICE_CONNECTION_NAME: str = "SERVICE_CONNECTION"
    AUTHORITY_TEMPLATE: str = "https://login.microsoftonline.com/{tenant_id}"


class OutboundAuth:
    """Outbound Bot Connector auth scopes and claims constants."""

    # Token scopes per auth model
    BOTFRAMEWORK_SCOPE: str = "https://api.botframework.com/.default"
    AGENTIC_SCOPE: str = "5a807f24-c9de-44ee-a3a7-329e88a00ffc/.default"

    # Claim keys / authentication types
    CLAIM_APP_ID: str = "appid"
    CLAIM_AUDIENCE: str = "aud"
    AUTH_TYPE_ANONYMOUS: str = "Anonymous"
    AUTH_TYPE_BEARER: str = "Bearer"


class MsalPatch:
    """Constants for the digital-worker MSAL federated-identity (FMI) patch."""

    PATCH_FLAG: str = "_activity_sdk_msal_patched"
    TOKEN_EXCHANGE_SCOPE: str = "api://AzureADTokenExchange/.default"
    FMI_PATH_KEY: str = "fmi_path"
    MSAL_CONFIGURATION_ATTR: str = "_msal_configuration"
    MSAL_CLIENT_ID_ATTR: str = "CLIENT_ID"


class BaggageKeys:
    """OpenTelemetry baggage keys promoted onto spans/logs by the core stack."""

    SESSION_ID: str = "azure.ai.agentserver.session_id"
    CONVERSATION_ID: str = "azure.ai.agentserver.conversation_id"


class SpanAttributes:
    """Attribute keys and values for the per-turn ``invoke_agent`` span.

    Each turn is wrapped in one ``invoke_agent`` span so the turn shows up as a
    single row in the trace list and becomes the parent of the spans the M365
    SDK creates. The agent name / version / id and the project id are set here
    directly (not left to the shared stack) so they are guaranteed to be on this
    one span together with the per-turn id — that combination is what makes the
    turn appear in the trace list.
    """

    GEN_AI_OPERATION_NAME: str = "gen_ai.operation.name"
    GEN_AI_SYSTEM: str = "gen_ai.system"
    GEN_AI_AGENT_NAME: str = "gen_ai.agent.name"
    GEN_AI_AGENT_VERSION: str = "gen_ai.agent.version"
    GEN_AI_AGENT_ID: str = "gen_ai.agent.id"
    GEN_AI_CONVERSATION_ID: str = "gen_ai.conversation.id"
    FOUNDRY_PROJECT_ID: str = "microsoft.foundry.project.id"
    SESSION_ID: str = "microsoft.session.id"
    # Per-turn identifier used to give the turn its own row in the trace list.
    # The activity turn has no response/invocation id of its own, so the
    # activity id is used.
    RESPONSE_ID: str = "azure.ai.agentserver.response_id"

    # Fixed attribute values.
    GEN_AI_SYSTEM_VALUE: str = "activity"
    OPERATION_NAME_VALUE: str = "invoke_agent"
    SPAN_NAME: str = "invoke_agent"


class LogRecordFields:
    """Log-record attribute names populated by the activity log enrichment."""

    SESSION_ID: str = "SessionId"
    USER_ID: str = "UserId"
    CALL_ID: str = "CallId"
    PROTOCOL: str = "Protocol"
    ENRICHER_FLAG: str = "_activity_enricher"


class ErrorSource:
    """Error-source classification values for the ``ERROR_SOURCE`` header."""

    USER: str = "user"
    UPSTREAM: str = "upstream"
    PLATFORM: str = "platform"


class ErrorCode:
    """Error codes used in activity error responses."""

    INVALID_REQUEST: str = "invalid_request"
    INTERNAL_ERROR: str = "internal_error"


class ActivityFields:
    """Inbound activity payload / turn field names and values."""

    TYPE: str = "type"
    ID: str = "id"
    CONVERSATION: str = "conversation"
    FROM: str = "from"
    RECIPIENT: str = "recipient"
    CHANNEL_ID: str = "channelId"
    SERVICE_URL: str = "serviceUrl"
    LOCALE: str = "locale"
    UNKNOWN_TYPE: str = "unknown"
    INVOKE_TYPE: str = "invoke"
    DELIVERY_MODE_EXPECT_REPLIES: str = "expectReplies"


# ID validation (defense in depth): bound length and allowed characters for
# user-provided IDs before they reach headers, span attributes, and logs.
MAX_ID_LENGTH: int = 256
VALID_ID_PATTERN: str = r"^[a-zA-Z0-9\-_.:]+\Z"
