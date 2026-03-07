# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class Constants:
    """Well-known environment variables and defaults for AgentServer."""

    AGENT_LOG_LEVEL = "AGENT_LOG_LEVEL"
    AGENT_DEBUG_ERRORS = "AGENT_DEBUG_ERRORS"
    AGENT_ENABLE_TRACING = "AGENT_ENABLE_TRACING"
    AGENT_SERVER_PORT = "AGENT_SERVER_PORT"
    AGENT_GRACEFUL_SHUTDOWN_TIMEOUT = "AGENT_GRACEFUL_SHUTDOWN_TIMEOUT"
    AGENT_REQUEST_TIMEOUT = "AGENT_REQUEST_TIMEOUT"
    AGENT_ENABLE_REQUEST_VALIDATION = "AGENT_ENABLE_REQUEST_VALIDATION"
    APPLICATIONINSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"
    DEFAULT_PORT = 8088
    DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT = 30
    DEFAULT_REQUEST_TIMEOUT = 300  # 5 minutes
    INVOCATION_ID_HEADER = "x-agent-invocation-id"
