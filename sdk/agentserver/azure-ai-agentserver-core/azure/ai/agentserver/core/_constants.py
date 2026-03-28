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

    # Tracing
    APPLICATIONINSIGHTS_CONNECTION_STRING = "APPLICATIONINSIGHTS_CONNECTION_STRING"
    OTEL_EXPORTER_OTLP_ENDPOINT = "OTEL_EXPORTER_OTLP_ENDPOINT"

    # Session identity
    FOUNDRY_AGENT_SESSION_ID = "FOUNDRY_AGENT_SESSION_ID"
