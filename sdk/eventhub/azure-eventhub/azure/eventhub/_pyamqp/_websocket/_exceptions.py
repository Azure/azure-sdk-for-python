# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class WebSocketException(Exception):
    """
    Base exception for all WebSocket related errors.
    """

class WebSocketPayloadError(WebSocketException):
    """
    Raised when there is an error in the WebSocket payload.
    """

class WebSocketConnectionError(WebSocketException):
    """
    Raised when there is an eror while establishing a connection.
    """

class WebSocketConnectionClosed(WebSocketConnectionError):
    """
    Raised when the connection is closed.
    """

class WebSocketProtocolError(WebSocketException):
    """
    Raised when the WebSocket protocol is violated.
    """