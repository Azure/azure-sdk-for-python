# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class ConversationConstants:
    """Conversation protocol constants.

    Protocol-specific constants for the WebSocket conversation protocol.
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
    ACTION_GET_CONVERSATION = "get_conversation"
    ACTION_CANCEL_CONVERSATION = "cancel_conversation"
    ACTION_PING = "ping"
    ACTION_PONG = "pong"

    # Keep-alive defaults
    DEFAULT_WS_PING_INTERVAL = 30  # seconds

    # Span attribute keys
    ATTR_SPAN_CONVERSATION_ID = "azure.ai.agentserver.conversations.conversation_id"
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.conversations.session_id"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.conversations.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.conversations.error.message"
