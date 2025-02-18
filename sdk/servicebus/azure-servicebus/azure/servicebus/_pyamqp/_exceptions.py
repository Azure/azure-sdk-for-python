class WebSocketException(Exception):
    """
    Base exception for all WebSocket related errors.
    """

class WebSocketPayloadError(WebSocketException):
    """
    Raised when there is an error in the WebSocket payload.
    """
    pass

class WebSocketConnectionError(WebSocketException):
    """
    Raised when there is an eror while establishing a connection.
    """
    pass

class WebSocketConnectionClosed(WebSocketConnectionError):
    """
    Raised when the connection is closed.
    """
    pass

class WebSocketProtocolError(WebSocketException):
    """
    Raised when the WebSocket protocol is violated.
    """