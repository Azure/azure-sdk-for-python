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
