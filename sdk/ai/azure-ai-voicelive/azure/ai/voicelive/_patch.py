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

__all__: List[str] = ["VoiceLiveClient", "WebsocketConnectionOptions"]  # Add all objects you want publicly available to users at this package level

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


class VoiceLiveConnection:
    """Represents a live WebSocket connection to the Voice Live API"""
    
    def __init__(self, connection) -> None:
        self._connection = connection
        
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Yield events until the connection is closed."""
        try:
            while True:
                yield self.recv()
        except Exception as e:
            log.debug(f"Connection closed: {e}")
            return
            
    def recv(self) -> Dict[str, Any]:
        """Receive and parse the next message."""
        message = self.recv_bytes()
        if isinstance(message, bytes):
            message = message.decode("utf-8")
        return json.loads(message)
        
    def recv_bytes(self) -> bytes:
        """Receive raw bytes from the connection."""
        message = self._connection.recv(decode=False)
        log.debug(f"Received websocket message: %s", message)
        return message
        
    def send(self, event: Dict[str, Any]) -> None:
        """Send an event to the server."""
        data = json.dumps(event)
        self._connection.send(data)
        
    def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket connection."""
        self._connection.close(code=code, reason=reason)


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
        """Create and return a WebSocket connection."""
        try:
            from websockets.sync.client import connect
        except ImportError as exc:
            raise ImportError("You need to install `websockets` to use WebSocket functionality") from exc
            
        url = self._prepare_url()
        log.debug("Connecting to %s", url)
        
        if self.__websocket_connection_options:
            log.debug("Connection options: %s", self.__websocket_connection_options)
            
        # Get auth headers
        auth_headers = {"Authorization": f"Bearer {self.__client._config.credential.key}"}
        headers = {**auth_headers, **self.__extra_headers}
            
        self.__connection = VoiceLiveConnection(
            connect(
                str(url),
                additional_headers=headers,
                **self.__websocket_connection_options,
            )
        )
        
        return self.__connection
        
    def _prepare_url(self) -> httpx.URL:
        """Prepare the WebSocket URL."""
        base_url = httpx.URL(self.__client._config.endpoint)
        # Ensure WebSocket scheme
        if base_url.scheme.startswith('http'):
            base_url = base_url.copy_with(scheme="wss" if base_url.scheme == "https" else "ws")
        
        # Add query parameters
        params = {"model": self.__model}
        params.update(self.__extra_query)
        
        return base_url.copy_with(params=params)
        
    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """Clean up the connection when exiting context."""
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
        :param extra_query: Additional query parameters to include in the WebSocket URL.
        :param extra_headers: Additional headers to include in the WebSocket handshake.
        :param websocket_connection_options: Options for the WebSocket connection.
        :return: A connection manager that can be used as a context manager.
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
