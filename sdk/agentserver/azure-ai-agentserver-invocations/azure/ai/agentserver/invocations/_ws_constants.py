# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class InvocationWSConstants:
    """WebSocket invocation protocol constants.

    Protocol-specific constants for the WebSocket invocation protocol
    (``invocations_ws``).
    """

    # WebSocket message types (server → client)
    MSG_TYPE_RESULT = "result"
    MSG_TYPE_STREAM_CHUNK = "stream_chunk"
    MSG_TYPE_STREAM_END = "stream_end"
    MSG_TYPE_ERROR = "error"
    MSG_TYPE_PING = "ping"
    MSG_TYPE_PONG = "pong"

    # WebSocket actions (client → server)
    ACTION_INVOKE = "invoke"
    ACTION_GET_INVOCATION = "get_invocation"
    ACTION_CANCEL_INVOCATION = "cancel_invocation"
    ACTION_PING = "ping"
    ACTION_PONG = "pong"

    # Keep-alive defaults
    DEFAULT_WS_PING_INTERVAL = 30  # seconds

    # Span attribute keys
    ATTR_SPAN_INVOCATION_ID = "azure.ai.agentserver.invocations_ws.invocation_id"
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.invocations_ws.session_id"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.invocations_ws.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.invocations_ws.error.message"
