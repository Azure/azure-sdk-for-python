# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class WebsocketConstants:
    """Websocket protocol constants.

    Protocol-specific constants for the WebSocket websocket protocol.
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
    ACTION_GET_WEBSOCKET = "get_websocket"
    ACTION_CANCEL_WEBSOCKET = "cancel_websocket"
    ACTION_PING = "ping"
    ACTION_PONG = "pong"

    # Keep-alive defaults
    DEFAULT_WS_PING_INTERVAL = 30  # seconds

    # Span attribute keys
    ATTR_SPAN_WEBSOCKET_ID = "azure.ai.agentserver.websocket.websocket_id"
    ATTR_SPAN_SESSION_ID = "azure.ai.agentserver.websocket.session_id"
    ATTR_SPAN_ERROR_CODE = "azure.ai.agentserver.websocket.error.code"
    ATTR_SPAN_ERROR_MESSAGE = "azure.ai.agentserver.websocket.error.message"
