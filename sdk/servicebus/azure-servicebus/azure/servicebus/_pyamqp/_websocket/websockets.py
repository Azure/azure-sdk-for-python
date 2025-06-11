# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Dict, Optional, List, Union, TYPE_CHECKING
from ._protocol import WebSocketProtocol, AsyncWebSocketProtocol
from ._exceptions import WebSocketConnectionError
from ._frame import Opcode, CloseReason, Frame

if TYPE_CHECKING:
    from ssl import SSLContext


class WebSocket:
    """
    A synchronous WebSocket client providing a simple interface for sending and receiving data.

    :param str url: The WebSocket server URL, starting with ws:// or wss:// in the format 
    ws://host:port/path or wss://host:port/path.
    :keyword dict[bytes, bytes] headers: HTTP headers to send during the WebSocket handshake.
    :keyword dict[str, Union[str, int]] http_proxy: HTTP proxy configuration 
    - host, port, username, password.
    :keyword list[bytes] subprotocols: Supported subprotocols.
    :keyword float timeout: Timeout value for WebSocket connection operations.
    :keyword SSLContext ssl: SSLContext object for configuring the SSL connection.
    """

    def __init__(
        self,
        url: str,
        *,
        headers: Optional[Dict[bytes, bytes]] = None,
        http_proxy: Optional[Dict[str, Union[int, str]]] = None,
        subprotocols: Optional[List[bytes]] = None,
        timeout: Optional[float] = None,
        ssl_ctx: Optional["SSLContext"] = None, # pylint: disable=unused-argument
    ) -> None:
        self._url: str = url
        self._is_open: bool = False
        self._protocol: WebSocketProtocol = WebSocketProtocol(
            url,
            headers=headers,
            subprotocols=subprotocols,
            http_proxy=http_proxy,
            ssl_ctx=ssl_ctx,
            timeout=timeout
        )
        self._headers = headers
        self._http_proxy = http_proxy
        self._subprotocols = subprotocols

    def connect(self) -> None:
        """
        Establishes a WebSocket connection with the server.
        """
        if self._is_open:
            return
        self._protocol.open_connection()
        self._is_open = True

    def send_str(self, data: str) -> None:
        """
        Sends a text message to the server. Raises a TypeError if the data is not a string.
        :param str data: The text message to send.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")
        if not isinstance(data, str):
            raise TypeError("data must be a string")

        self._protocol.send_frame(data, Opcode.TEXT)

    def send_bytes(self, data: bytes) -> None:
        """
        Sends a binary message to the server. Raises a TypeError if the data is not bytes.
        :param bytes data: The binary message to send.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        self._protocol.send_frame(data, Opcode.BINARY)

    def receive_str(self) -> str:
        """
        Receives the data from the server as a string.
        :returns: The received data as a string.
        :rtype: str
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        frame = self._protocol.receive_frame()

        if frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            return frame.data.decode("utf-8")
        return ""

    def receive_frame(self) -> Frame:
        """
        Receives the websocket frame from the server
        :returns Frame: The frame received from the server.
        :rtype: Frame
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        return self._protocol.receive_frame()

    def receive_bytes(self) -> bytes:
        """
        Receives the data from the server as bytes.
        :returns: The data received from the server as bytes.
        :rtype: bytes
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        frame = self._protocol.receive_frame()

        if frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            if isinstance(frame.data, str):
                return frame.data.encode("utf-8")
            return frame.data

        return b""

    def close(self, code: CloseReason = CloseReason.NORMAL, reason: bytes = b"") -> None:
        """
        Closes the WebSocket connection with the server.
        :param CloseReason code: The close code.
        :param bytes reason: The close reason.
        """
        if not self._is_open:
            return
        self._protocol.close(code, reason)
        self._is_open = False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def ping(self, data: bytes = b"") -> None:
        """
        Sends a ping frame to the server.
        :param bytes data: The data to send with the ping frame.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        self._protocol.send_frame(data, Opcode.PING)

    def pong(self, data: bytes = b"") -> None:
        """
        Sends a pong frame to the server.
        :param bytes data: The data to send with the pong frame.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        self._protocol.send_frame(data, Opcode.PONG)


class AsyncWebSocket:
    """
    An async WebSocket client implementation that provides a simple interface 
    for sending and receiving data.

    :param str url: The URL of the WebSocket server. It must start with either ws:// or wss://
    and in the format ws://host:port/path or wss://host:port/path.
    :keyword dict[bytes, bytes] headers: A dictionary of HTTP headers to send
    during the WebSocket handshake.
    :keyword dict[str, Union[str, int]] http_proxy: A dictionary of HTTP proxy configuration
    - host, port, username, password.
    :keyword list[bytes] subprotocols: A list of supported subprotocols
    :keyword float timeout: The timeout value for the WebSocket connection to perform send
    and receive operations.
    :keyword SSLContext ssl: An SSLContext object that is used to configure the SSL connection.
    """

    def __init__(
        self,
        url: str,
        *,
        headers: Optional[Dict[bytes, bytes]] = None,
        http_proxy: Optional[Dict[str, Union[int, str]]] = None,
        subprotocols: Optional[List[str]] = None,
        timeout: Optional[float] = None, # pylint: disable=unused-argument
        ssl_ctx: Optional["SSLContext"] = None,
    ) -> None:
        self._url: str = url
        self._is_open: bool = False
        self._protocol: AsyncWebSocketProtocol = AsyncWebSocketProtocol(
            url,
            headers=headers,
            subprotocols=subprotocols,
            http_proxy=http_proxy,
            ssl_ctx = ssl_ctx,
        )
        self._headers = headers
        self._http_proxy = http_proxy
        self._subprotocols = subprotocols

    async def connect(self) -> None:
        """
        Establishes a WebSocket connection with the server.
        """
        if self._is_open:
            return
        await self._protocol.open_connection()
        self._is_open = True

    async def send_str(self, data: str) -> None:
        """
        Sends a text message to the server. Raises a TypeError if the data is not a string.
        :param str data: The text message to send.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")
        if not isinstance(data, str):
            raise TypeError("data must be a string")

        await self._protocol.send_frame(data, Opcode.TEXT)

    async def send_bytes(self, data: bytes) -> None:
        """
        Sends a binary message to the server. Raises a TypeError if the data is not bytes.
        :param bytes data: The binary message to send.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")
        if not isinstance(data, bytes):
            raise TypeError("data must be a string")

        await self._protocol.send_frame(data, Opcode.BINARY)

    async def receive_str(self) -> str:
        """
        Receives the data from the server as a string.
        :return: The received data as a string.
        :rtype: str
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        frame = await self._protocol.receive_frame()

        if frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            return frame.data.decode("utf-8")
        return ""

    async def receive_frame(self) -> Frame:
        """
        Receives the websocket frame from the server
        :return Frame: The frame received from the server.
        :rtype: Frame
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        return await self._protocol.receive_frame()

    async def receive_bytes(self) -> bytes:
        """
        Receives the data from the server as bytes.
        :returns: The data received from the server.
        :rtype: bytes
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        frame = await self._protocol.receive_frame()

        if frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            if isinstance(frame.data, str):
                return frame.data.encode("utf-8")
            return frame.data
        if frame.opcode == Opcode.BINARY:
            return frame.data

        return b""

    async def close(self, code: CloseReason = CloseReason.NORMAL, reason: bytes = b"") -> None:
        """
        Closes the WebSocket connection with the server.
        :param CloseReason code: The close code.
        :param bytes reason: The close reason.
        """
        if not self._is_open:
            return
        await self._protocol.close(code, reason)
        self._is_open = False

    async def __aenter__(self) -> "AsyncWebSocket":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    async def ping(self, data: bytes = b"") -> None:
        """
        Sends a ping frame to the server.
        :param bytes data: The data to send with the ping frame.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        await self._protocol.send_frame(data, Opcode.PING)

    async def pong(self, data: bytes = b"") -> None:
        """
        Sends a pong frame to the server.
        :param bytes data: The data to send with the pong frame.
        """
        if not self._is_open:
            raise WebSocketConnectionError("Connection is closed")

        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")

        await self._protocol.send_frame(data, Opcode.PONG)