# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
Asynchronous WebSocket connection management for the VoiceLive service.
"""

import json
import logging
import uuid
from types import TracebackType
from typing import Any, Dict, Optional, Type, cast

try:
    from websockets.asyncio.client import connect as ws_connect, ClientConnection as AsyncWebsocketConnection
except ImportError:
    AsyncWebsocketConnection = Any  # type: ignore
    # Imports will fail at runtime if websockets is not installed

from typing_extensions import Self
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ServiceRequestError

from ..models.events import BaseEvent, create_event_from_json, ErrorEvent


logger = logging.getLogger(__name__)


class AsyncVoiceLiveConnection:
    """Represents a live asynchronous WebSocket connection to the VoiceLive service.
    
    This class provides methods for sending and receiving events over a WebSocket connection.
    It is typically created by an AsyncVoiceLiveConnectionManager.
    
    :ivar connection_id: The ID of this connection.
    :vartype connection_id: str
    :ivar session_id: The session ID assigned by the service, if available.
    :vartype session_id: Optional[str]
    """
    
    def __init__(self, connection: AsyncWebsocketConnection, connection_id: Optional[str] = None):
        """Creates a new AsyncVoiceLiveConnection.
        
        :param connection: The asynchronous WebSocket connection.
        :type connection: AsyncWebsocketConnection
        :param connection_id: Optional identifier for the connection.
        :type connection_id: Optional[str]
        """
        self._connection = connection
        self.connection_id = connection_id or str(uuid.uuid4())
        self.session_id = None
    
    async def __aiter__(self):
        """Returns an asynchronous iterator for receiving events.
        
        This iterator will continue to yield events until the connection is closed.
        
        :return: An asynchronous iterator of events.
        """
        from websockets.exceptions import ConnectionClosedOK
        
        try:
            while True:
                yield await self.receive()
        except ConnectionClosedOK:
            logger.info("Connection was closed normally")
            return
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    async def receive(self) -> BaseEvent:
        """Receives the next event from the service.
        
        :return: The received event.
        :rtype: BaseEvent
        :raises: Exception if an error occurs while receiving data.
        """
        data = await self.receive_raw()
        return self.parse_event(data)
    
    async def receive_raw(self) -> bytes:
        """Receives the next raw message from the service.
        
        :return: The raw message data.
        :rtype: bytes
        :raises: Exception if an error occurs while receiving data.
        """
        message = await self._connection.recv(decode=False)
        logger.debug(f"Received websocket message: {message}")
        return message
    
    async def send(self, event: BaseEvent) -> None:
        """Sends an event to the service.
        
        :param event: The event to send.
        :type event: BaseEvent
        :raises: Exception if an error occurs while sending the event.
        """
        await self._connection.send(event.to_json())
    
    async def send_raw(self, data: str) -> None:
        """Sends raw JSON data to the service.
        
        :param data: The JSON string to send.
        :type data: str
        :raises: Exception if an error occurs while sending the data.
        """
        await self._connection.send(data)
    
    async def close(self, code: int = 1000, reason: str = "") -> None:
        """Closes the WebSocket connection.
        
        :param code: The WebSocket close code.
        :type code: int
        :param reason: The reason for closing the connection.
        :type reason: str
        """
        await self._connection.close(code=code, reason=reason)
    
    def parse_event(self, data: bytes) -> BaseEvent:
        """Parses raw WebSocket data into an event object.
        
        :param data: The raw WebSocket data.
        :type data: bytes
        :return: The parsed event.
        :rtype: BaseEvent
        """
        try:
            json_str = data.decode('utf-8')
            return create_event_from_json(json_str)
        except Exception as e:
            logger.error(f"Error parsing event data: {e}")
            return ErrorEvent(
                error_code="parse_error", 
                error_message=f"Failed to parse event: {str(e)}"
            )


class AsyncVoiceLiveConnectionManager:
    """A context manager for asynchronous WebSocket connections to the VoiceLive service.
    
    This class handles establishing and closing WebSocket connections, including
    authentication and URL construction.
    
    :ivar endpoint: The WebSocket endpoint for the VoiceLive service.
    :vartype endpoint: str
    :ivar api_version: The API version to use.
    :vartype api_version: str
    """
    
    def __init__(
        self,
        credential: TokenCredential,
        endpoint: str,
        api_version: str,
        connection_id: Optional[str] = None,
        **kwargs: Any
    ):
        """Creates a new AsyncVoiceLiveConnectionManager.
        
        :param credential: The credential to use for authentication.
        :type credential: ~azure.core.credentials.TokenCredential
        :param endpoint: The endpoint URL for the VoiceLive service.
        :type endpoint: str
        :param api_version: The API version to use.
        :type api_version: str
        :param connection_id: Optional identifier for the connection.
        :type connection_id: Optional[str]
        :keyword additional_headers: Additional headers to include in the WebSocket connection request.
        :paramtype additional_headers: Dict[str, str]
        :keyword connection_timeout: Connection timeout in seconds.
        :paramtype connection_timeout: float
        """
        self._credential = credential
        self._endpoint = endpoint
        self._api_version = api_version
        self._connection_id = connection_id or str(uuid.uuid4())
        self._connection: Optional[AsyncVoiceLiveConnection] = None
        
        # Extract keyword arguments
        self._additional_headers = kwargs.get("additional_headers", {})
        self._connection_timeout = kwargs.get("connection_timeout", 30.0)
        
        # Ensure the endpoint uses the WebSocket protocol
        if not self._endpoint.startswith(("ws://", "wss://")):
            self._endpoint = f"wss://{self._endpoint.removeprefix('https://').removeprefix('http://')}"
    
    async def __aenter__(self) -> AsyncVoiceLiveConnection:
        """Establishes a WebSocket connection and returns an AsyncVoiceLiveConnection.
        
        :return: The established connection.
        :rtype: AsyncVoiceLiveConnection
        :raises: ~azure.core.exceptions.ServiceRequestError if the connection cannot be established.
        """
        try:
            # Acquire authentication token
            token = await self._credential.get_token("https://voicelive.azure.com/.default")
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json",
                "User-Agent": f"azsdk-python-ai-voicelive/1.0.0",
                **self._additional_headers
            }
            
            # Construct the URL with query parameters
            url = f"{self._endpoint}?api-version={self._api_version}"
            
            logger.info(f"Connecting to {url}")
            
            # Establish the WebSocket connection
            connection = await ws_connect(
                url,
                additional_headers=headers,
                open_timeout=self._connection_timeout,
            )
            
            self._connection = AsyncVoiceLiveConnection(connection, self._connection_id)
            return self._connection
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {e}")
            raise ServiceRequestError(f"Failed to establish WebSocket connection: {str(e)}")
    
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType]
    ) -> None:
        """Closes the WebSocket connection when exiting the context.
        
        :param exc_type: The type of exception that was raised, if any.
        :param exc_value: The exception that was raised, if any.
        :param traceback: The traceback of the exception, if any.
        """
        if self._connection:
            try:
                await self._connection.close()
                logger.info("WebSocket connection closed")
            except Exception as e:
                logger.warning(f"Error closing WebSocket connection: {e}")
            finally:
                self._connection = None