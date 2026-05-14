# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class InvocationConstants:
    """Invocation protocol constants.

    Protocol-specific headers, env vars, and defaults for the invocation
    endpoints.
    """

    # Request / response headers
    INVOCATION_ID_HEADER = "x-agent-invocation-id"
    SESSION_ID_HEADER = "x-agent-session-id"

    # Span attribute keys
    ATTR_SPAN_INVOCATION_ID = "azure.ai.agentserver.invocations.invocation_id"
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.invocations.session_id"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.invocations.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.invocations.error.message"


class InvocationsWSConstants:
    """invocations_ws (WebSocket) protocol constants.

    Route, span attribute keys, and ping/pong defaults for the
    WebSocket endpoint hosted alongside the HTTP invocations protocol.
    """

    # Route
    ROUTE_PATH = "/invocations_ws"

    # Environment variable for platform-injected keep-alive override.
    # AgentService injects this into every hosted-agent container so the
    # platform can tune the WebSocket Ping cadence without redeploying
    # the agent code.
    # Resolution order: explicit ``ws_ping_interval=`` constructor arg →
    # ``WS_KEEPALIVE_INTERVAL`` env var → disabled (``0``).
    # ``0`` disables keep-alive.
    ENV_WS_KEEPALIVE_INTERVAL = "WS_KEEPALIVE_INTERVAL"

    # Close codes (RFC 6455)
    CLOSE_NORMAL = 1000  # handler returned cleanly
    CLOSE_INTERNAL_ERROR = 1011  # handler raised an unhandled exception

    # Span attribute keys
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.invocations_ws.session_id"
    ATTR_SPAN_CLOSE_CODE = "azure.ai.agentserver.invocations_ws.close_code"
    ATTR_SPAN_DURATION_MS = "azure.ai.agentserver.invocations_ws.duration_ms"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.invocations_ws.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.invocations_ws.error.message"
