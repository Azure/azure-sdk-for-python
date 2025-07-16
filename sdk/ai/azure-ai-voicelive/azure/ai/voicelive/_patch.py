# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import logging
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union
from typing_extensions import TypedDict

import httpx
from azure.core.credentials import AzureKeyCredential

from ._client import VoiceLiveClient as VoiceLiveClientGenerated
from .models import VoiceLiveClientEvent, VoiceLiveServerEvent

__all__: List[str] = [
    "VoiceLiveClient",
    "WebsocketConnectionOptions",
    "VoiceLiveConnectionError",
    "VoiceLiveConnectionClosed",
    "VoiceLiveConnection",
    "VoiceLiveSessionResource",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


class WebsocketConnectionOptions(TypedDict, total=False):
    """Websocket connection options for VoiceLive API WebSocket connections.
    
    Based on options from the websockets library.
    """
    extensions: Optional[Sequence[Any]]
    subprotocols: Optional[Sequence[str]]
    compression: Optional[str]
    max_size: Optional[int]
    max_queue: Optional[Union[int, Tuple[Optional[int], Optional[int]]]]
    write_limit: Optional[Union[int, Tuple[int, Optional[int]]]]


class VoiceLiveConnectionError(Exception):
    """Base exception for VoiceLive WebSocket connection errors."""
    pass


class VoiceLiveConnectionClosed(VoiceLiveConnectionError):
    """Exception raised when a WebSocket connection is closed."""
    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket connection closed with code {code}: {reason}")


class VoiceLiveSessionResource:
    """Resource for session management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a session resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection
        
    def update(self, *, session: Dict[str, Any], event_id: Optional[str] = None) -> None:
        """Update the session configuration.
        
        :param session: Session configuration parameters.
        :type session: Dict[str, Any]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "session.update",
            "session": session
        }
        if event_id:
            event["event_id"] = event_id
            
        self._connection.send(event)


class VoiceLiveConnection:
    """Represents a live WebSocket connection to the Voice Live API."""
    
    def __init__(self, connection) -> None:
        """Initialize a VoiceLiveConnection.
        
        :param connection: The underlying WebSocket connection.
        """
        self._connection = connection
        self.session = VoiceLiveSessionResource(self)
        
    def __iter__(self) -> Iterator[VoiceLiveServerEvent]:
        """Yield typed events until the connection is closed.
        
        :return: An iterator of VoiceLiveServerEvent objects.
        :rtype: Iterator[~azure.ai.voicelive.models.VoiceLiveServerEvent]
        """
        try:
            while True:
                yield self.recv()
        except Exception as e:
            log.debug(f"Connection closed: {e}")
            return
            
    def recv(self) -> VoiceLiveServerEvent:
        """Receive and parse the next message as a typed event.
        
        :return: A parsed server event.
        :rtype: ~azure.ai.voicelive.models.VoiceLiveServerEvent
        :raises VoiceLiveConnectionError: If the connection is closed or the message cannot be parsed.
        """
        try:
            return VoiceLiveServerEvent.deserialize(self.recv_bytes())
        except Exception as e:
            log.error(f"Error parsing message: {e}")
            raise VoiceLiveConnectionError(f"Failed to parse message: {e}") from e
        
    def recv_bytes(self) -> bytes:
        """Receive raw bytes from the connection.
        
        :return: The raw message bytes.
        :rtype: bytes
        :raises VoiceLiveConnectionClosed: If the connection is closed.
        """
        try:
            message = self._connection.recv(decode=False)
            log.debug(f"Received websocket message: %s", message)
            return message
        except Exception as e:
            code = getattr(e, "code", 1006)  # Default to 1006 (Abnormal Closure) if no code
            reason = str(e)
            raise VoiceLiveConnectionClosed(code, reason) from e
        
    def send(self, event: Union[Dict[str, Any], VoiceLiveClientEvent]) -> None:
        """Send an event to the server.
        
        :param event: The event to send, either as a dictionary or a VoiceLiveClientEvent.
        :type event: Union[Dict[str, Any], ~azure.ai.voicelive.models.VoiceLiveClientEvent]
        :raises VoiceLiveConnectionError: If the event cannot be sent.
        """
        try:
            if isinstance(event, dict):
                data = json.dumps(event)
            else:
                data = event.serialize()
            self._connection.send(data)
        except Exception as e:
            log.error(f"Failed to send event: {e}")
            raise VoiceLiveConnectionError(f"Failed to send event: {e}") from e
        
    def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket connection.
        
        :param code: WebSocket close code.
        :type code: int
        :param reason: Reason for closing the connection.
        :type reason: str
        """
        try:
            self._connection.close(code=code, reason=reason)
        except Exception as e:
            log.warning(f"Error closing connection: {e}")


class VoiceLiveConnectionManager:
    """Manager for VoiceLive WebSocket connections."""
    
    def __init__(
        self,
        *,
        client: "VoiceLiveClient",
        model: str,
        extra_query: Dict[str, Any],
        extra_headers: Dict[str, Any],
        websocket_connection_options: Dict[str, Any],
    ) -> None:
        self.__client = client
        self.__model = model
        self.__connection = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = websocket_connection_options
        
    def __enter__(self) -> VoiceLiveConnection:
        """Create and return a WebSocket connection.
        
        :return: A VoiceLiveConnection instance.
        :rtype: ~azure.ai.voicelive.VoiceLiveConnection
        :raises ImportError: If the websockets package is not installed.
        :raises VoiceLiveConnectionError: If the connection cannot be established.
        """
        try:
            from websockets.sync.client import connect
            from websockets.exceptions import WebSocketException
        except ImportError as exc:
            raise ImportError("You need to install `websockets` to use WebSocket functionality") from exc
            
        try:
            url = self._prepare_url()
            log.debug("Connecting to %s", url)
            
            if self.__websocket_connection_options:
                log.debug("Connection options: %s", self.__websocket_connection_options)
                
            # Get auth headers
            auth_headers = {"Authorization": f"Bearer {self.__client._config.credential.key}"}
            headers = {**auth_headers, **self.__extra_headers}
                
            connection = connect(
                str(url),
                additional_headers=headers,
                **self.__websocket_connection_options,
            )
            
            self.__connection = VoiceLiveConnection(connection)
            return self.__connection
        except WebSocketException as e:
            raise VoiceLiveConnectionError(f"Failed to establish WebSocket connection: {e}") from e
        
    def _prepare_url(self) -> httpx.URL:
        """Prepare the WebSocket URL.
        
        :return: The prepared URL.
        :rtype: httpx.URL
        """
        base_url = httpx.URL(self.__client._config.endpoint)
        # Ensure WebSocket scheme
        if base_url.scheme.startswith('http'):
            base_url = base_url.copy_with(scheme="wss" if base_url.scheme == "https" else "ws")
        
        # Add query parameters
        params = {"model": self.__model}
        params.update(self.__extra_query)
        
        return base_url.copy_with(params=params)
        
    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """Clean up the connection when exiting context.
        
        :param exc_type: Exception type, if any.
        :param exc: Exception value, if any.
        :param exc_tb: Exception traceback, if any.
        """
        if self.__connection is not None:
            self.__connection.close()


class VoiceLiveClient(VoiceLiveClientGenerated):
    """Extended VoiceLiveClient with WebSocket support."""
    
    def connect(
        self,
        *,
        model: str,
        extra_query: Dict[str, Any] = {},
        extra_headers: Dict[str, Any] = {},
        websocket_connection_options: Dict[str, Any] = {},
    ) -> VoiceLiveConnectionManager:
        """Connect to the VoiceLive API via WebSocket.
        
        :param model: The model to use for the connection.
        :type model: str
        :param extra_query: Additional query parameters to include in the WebSocket URL.
        :type extra_query: Dict[str, Any]
        :param extra_headers: Additional headers to include in the WebSocket handshake.
        :type extra_headers: Dict[str, Any]
        :param websocket_connection_options: Options for the WebSocket connection.
        :type websocket_connection_options: Dict[str, Any]
        :return: A connection manager that can be used as a context manager.
        :rtype: ~azure.ai.voicelive.VoiceLiveConnectionManager
        """
        return VoiceLiveConnectionManager(
            client=self,
            model=model,
            extra_query=extra_query,
            extra_headers=extra_headers,
            websocket_connection_options=websocket_connection_options,
        )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
