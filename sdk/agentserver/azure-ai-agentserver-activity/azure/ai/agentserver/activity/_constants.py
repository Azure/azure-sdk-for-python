# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity protocol header name constants."""

from azure.ai.agentserver.core._platform_headers import SESSION_ID as _SESSION_ID  # pylint: disable=import-error,no-name-in-module


class ActivityConstants:
    """Activity protocol header constants.

    Cross-cutting header names (for example session ID) are imported from
    :mod:`azure.ai.agentserver.core._platform_headers`.
    """

    PROTOCOL = "activity"

    # Request / response headers
    ACTIVITY_ID_HEADER = "x-agent-activity-id"
    SESSION_ID_HEADER = _SESSION_ID
    CONVERSATION_ID_HEADER = "x-agent-conversation-id"
