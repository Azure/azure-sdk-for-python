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

    # Default WebSocket Ping interval in seconds.
    # Azure APIM and Azure Load Balancer drop idle WebSocket connections
    # after ~4 minutes; 30 s gives a comfortable safety margin.
    DEFAULT_PING_INTERVAL_S = 30.0

    # Close codes (RFC 6455)
    CLOSE_NORMAL = 1000  # handler returned cleanly
    CLOSE_INTERNAL_ERROR = 1011  # handler raised an unhandled exception
    CLOSE_SERVICE_RESTART = 1012  # graceful shutdown drained the connection

    # Span attribute keys
    ATTR_SPAN_SESSION_ID = "ws.session_id"
    ATTR_SPAN_CLOSE_CODE = "ws.close_code"
    ATTR_SPAN_DURATION_MS = "ws.duration_ms"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.invocations_ws.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.invocations_ws.error.message"
