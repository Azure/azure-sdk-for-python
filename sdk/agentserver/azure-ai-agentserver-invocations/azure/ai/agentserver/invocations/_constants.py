# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core._platform_headers import SESSION_ID as _SESSION_ID  # pylint: disable=import-error,no-name-in-module


class InvocationConstants:
    """Invocation protocol constants.

    Protocol-specific headers, env vars, and defaults for the invocation
    endpoints.  Cross-cutting header names (e.g. session ID) are imported
    from :mod:`azure.ai.agentserver.core._platform_headers`.
    """

    # Request / response headers
    INVOCATION_ID_HEADER = "x-agent-invocation-id"
    SESSION_ID_HEADER = _SESSION_ID

    # Span attribute keys
    ATTR_SPAN_INVOCATION_ID = "azure.ai.agentserver.invocations.invocation_id"
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.invocations.session_id"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.invocations.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.invocations.error.message"
