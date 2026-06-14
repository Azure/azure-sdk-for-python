# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.agentserver.core._platform_headers import SESSION_ID as _SESSION_ID  # pylint: disable=import-error,no-name-in-module


class ActivityConstants:
    """Activity protocol constants.

    Protocol-specific headers and telemetry attribute keys for activity
    endpoint handling. Cross-cutting header names (for example session ID)
    are imported from :mod:`azure.ai.agentserver.core._platform_headers`.
    """

    PROTOCOL = "activity"

    # Request / response headers
    ACTIVITY_ID_HEADER = "x-agent-activity-id"
    SESSION_ID_HEADER = _SESSION_ID
    CONVERSATION_ID_HEADER = "x-agent-conversation-id"

    # Span attribute keys
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.activity.session_id"
    ATTR_SPAN_PROTOCOL = "azure.ai.agentserver.activity.protocol"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.activity.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.activity.error.message"
