# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class Constants:
    """Well-known environment variables and defaults for AgentHost hosting."""

    # Foundry identity
    FOUNDRY_AGENT_NAME = "FOUNDRY_AGENT_NAME"
    FOUNDRY_AGENT_VERSION = "FOUNDRY_AGENT_VERSION"
    FOUNDRY_PROJECT_ENDPOINT = "FOUNDRY_PROJECT_ENDPOINT"
    FOUNDRY_PROJECT_ARM_ID = "FOUNDRY_PROJECT_ARM_ID"

    # Network
    PORT = "PORT"
    DEFAULT_PORT = 8088

    # Logging
    AGENT_LOG_LEVEL = "AGENT_LOG_LEVEL"

    # Tracing
    APPLICATIONINSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"
    OTEL_EXPORTER_OTLP_ENDPOINT = "OTEL_EXPORTER_OTLP_ENDPOINT"

    # Graceful shutdown
    AGENT_GRACEFUL_SHUTDOWN_TIMEOUT = "AGENT_GRACEFUL_SHUTDOWN_TIMEOUT"
    DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT = 30

    # Session identity
    FOUNDRY_AGENT_SESSION_ID = "FOUNDRY_AGENT_SESSION_ID"
