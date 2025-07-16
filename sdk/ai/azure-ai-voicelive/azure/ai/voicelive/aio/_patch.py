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
from typing import Any, Dict, List, Optional, Union, AsyncIterator
from typing_extensions import TypedDict

import httpx
from azure.core.credentials import AzureKeyCredential

from ._client import VoiceLiveClient as VoiceLiveClientGenerated
from ..models import VoiceLiveClientEvent, VoiceLiveServerEvent

__all__: List[str] = [
    "VoiceLiveClient",
    "WebsocketConnectionOptions",
    "VoiceLiveConnectionError",
    "VoiceLiveConnectionClosed",
    "VoiceLiveConnection",
    "VoiceLiveSessionResource",
    "VoiceLiveResponseResource",
    "VoiceLiveInputAudioBufferResource",
    "VoiceLiveOutputAudioBufferResource",
    "VoiceLiveConversationResource",
    "VoiceLiveConversationItemResource",
    "VoiceLiveTranscriptionSessionResource",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


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
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def update(self, *, session: Dict[str, Any], event_id: Optional[str] = None) -> None:
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
            
        await self._connection.send(event)


class VoiceLiveResponseResource:
    """Resource for response management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a response resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def create(self, *, response: Optional[Dict[str, Any]] = None, event_id: Optional[str] = None) -> None:
        """Create a response from the model.
        
        This event instructs the server to create a Response, which means triggering
        model inference. When in Server VAD mode, the server will create Responses
        automatically.
        
        :param response: Optional response configuration.
        :type response: Optional[Dict[str, Any]]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "response.create"}
        if response:
            event["response"] = response
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
        """Cancel an in-progress response.
        
        The server will respond with a `response.cancelled` event or an error
        if there is no response to cancel.
        
        :param response_id: Optional ID of the response to cancel.
        :type response_id: Optional[str]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "response.cancel"}
        if response_id:
            event["response_id"] = response_id
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)


class VoiceLiveInputAudioBufferResource:
    """Resource for input audio buffer management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an input audio buffer resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def append(self, *, audio: str, event_id: Optional[str] = None) -> None:
        """Append audio to the input buffer.
        
        The audio buffer is temporary storage you can write to and later commit.
        In Server VAD mode, the audio buffer is used to detect speech and the
        server will decide when to commit.
        
        :param audio: Base64-encoded audio data.
        :type audio: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "input_audio_buffer.append",
            "audio": audio
        }
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def commit(self, *, event_id: Optional[str] = None) -> None:
        """Commit the input audio buffer.
        
        This will create a new user message item in the conversation.
        When in Server VAD mode, the client does not need to send this event,
        the server will commit the audio buffer automatically.
        
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "input_audio_buffer.commit"}
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the input audio buffer.
        
        The server will respond with an `input_audio_buffer.cleared` event.
        
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "input_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)


class VoiceLiveOutputAudioBufferResource:
    """Resource for output audio buffer management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an output audio buffer resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the output audio buffer.
        
        This will trigger the server to stop generating audio and emit
        an `output_audio_buffer.cleared` event.
        
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "output_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)


class VoiceLiveConversationItemResource:
    """Resource for conversation item management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation item resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def create(
        self, 
        *, 
        item: Dict[str, Any],
        previous_item_id: Optional[str] = None,
        event_id: Optional[str] = None
    ) -> None:
        """Create a new conversation item.
        
        Add a new Item to the Conversation's context, including messages,
        function calls, and function call responses.
        
        :param item: The item to create.
        :type item: Dict[str, Any]
        :param previous_item_id: Optional ID of the item after which to insert this item.
        :type previous_item_id: Optional[str]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "conversation.item.create",
            "item": item
        }
        if previous_item_id:
            event["previous_item_id"] = previous_item_id
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete a conversation item.
        
        Remove an item from the conversation history.
        
        :param item_id: ID of the item to delete.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "conversation.item.delete",
            "item_id": item_id
        }
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Retrieve a conversation item.
        
        Get the server's representation of a specific item in the conversation history.
        
        :param item_id: ID of the item to retrieve.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "conversation.item.retrieve",
            "item_id": item_id
        }
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)
        
    async def truncate(
        self, 
        *, 
        item_id: str, 
        audio_end_ms: int, 
        content_index: int, 
        event_id: Optional[str] = None
    ) -> None:
        """Truncate a conversation item's audio.
        
        Truncate a previous assistant message's audio, useful when the user interrupts.
        
        :param item_id: ID of the item to truncate.
        :type item_id: str
        :param audio_end_ms: Time in milliseconds where to truncate the audio.
        :type audio_end_ms: int
        :param content_index: Index of the content to truncate.
        :type content_index: int
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "conversation.item.truncate",
            "item_id": item_id,
            "audio_end_ms": audio_end_ms,
            "content_index": content_index
        }
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)


class VoiceLiveConversationResource:
    """Resource for conversation management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        self.item = VoiceLiveConversationItemResource(connection)


class VoiceLiveTranscriptionSessionResource:
    """Resource for transcription session management."""
    
    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a transcription session resource.
        
        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        
    async def update(self, *, session: Dict[str, Any], event_id: Optional[str] = None) -> None:
        """Update the transcription session.
        
        :param session: Transcription session configuration.
        :type session: Dict[str, Any]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {
            "type": "transcription_session.update",
            "session": session
        }
        if event_id:
            event["event_id"] = event_id
            
        await self._connection.send(event)


class VoiceLiveConnection:
    """Represents a live WebSocket connection to the Voice Live API."""
    
    def __init__(self, connection) -> None:
        """Initialize a VoiceLiveConnection.
        
        :param connection: The underlying WebSocket connection.
        """
        self._connection = connection
        
        # Add all resource attributes
        self.session = VoiceLiveSessionResource(self)
        self.response = VoiceLiveResponseResource(self)
        self.input_audio_buffer = VoiceLiveInputAudioBufferResource(self)
        self.conversation = VoiceLiveConversationResource(self)
        self.output_audio_buffer = VoiceLiveOutputAudioBufferResource(self)
        self.transcription_session = VoiceLiveTranscriptionSessionResource(self)
        
    async def __aiter__(self) -> AsyncIterator[VoiceLiveServerEvent]:
        """Yield typed events until the connection is closed.
        
        :return: An async iterator of VoiceLiveServerEvent objects.
        :rtype: AsyncIterator[~azure.ai.voicelive.models.VoiceLiveServerEvent]
        """
        try:
            while True:
                yield await self.recv()
        except Exception as e:
            log.debug(f"Connection closed: {e}")
            return
            
    async def recv(self) -> VoiceLiveServerEvent:
        """Receive and parse the next message as a typed event.
        
        :return: A parsed server event.
        :rtype: ~azure.ai.voicelive.models.VoiceLiveServerEvent
        :raises VoiceLiveConnectionError: If the connection is closed or the message cannot be parsed.
        """
        try:
            return VoiceLiveServerEvent.deserialize(await self.recv_bytes())
        except Exception as e:
            log.error(f"Error parsing message: {e}")
            raise VoiceLiveConnectionError(f"Failed to parse message: {e}") from e
        
    async def recv_bytes(self) -> bytes:
        """Receive raw bytes from the connection.
        
        :return: The raw message bytes.
        :rtype: bytes
        :raises VoiceLiveConnectionClosed: If the connection is closed.
        """
        try:
            message = await self._connection.recv()
            log.debug(f"Received websocket message: %s", message)
            return message
        except Exception as e:
            code = getattr(e, "code", 1006)  # Default to 1006 (Abnormal Closure) if no code
            reason = str(e)
            raise VoiceLiveConnectionClosed(code, reason) from e
        
    async def send(self, event: Union[Dict[str, Any], VoiceLiveClientEvent]) -> None:
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
            await self._connection.send(data)
        except Exception as e:
            log.error(f"Failed to send event: {e}")
            raise VoiceLiveConnectionError(f"Failed to send event: {e}") from e
        
    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket connection.
        
        :param code: WebSocket close code.
        :type code: int
        :param reason: Reason for closing the connection.
        :type reason: str
        """
        try:
            await self._connection.close(code=code, reason=reason)
        except Exception as e:
            log.warning(f"Error closing connection: {e}")


class WebsocketConnectionOptions(TypedDict, total=False):
    """Websocket connection options for VoiceLive API WebSocket connections."""
    # Common websockets options
    compression: Optional[str]
    max_size: Optional[int]
    max_queue: Optional[int]
    open_timeout: Optional[float]
    close_timeout: Optional[float]
    ping_interval: Optional[float]
    ping_timeout: Optional[float]


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
        
    async def __aenter__(self) -> VoiceLiveConnection:
        """Create and return a WebSocket connection.
        
        :return: A VoiceLiveConnection instance.
        :rtype: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :raises ImportError: If the websockets package is not installed.
        :raises VoiceLiveConnectionError: If the connection cannot be established.
        """
        try:
            import websockets
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
                
            connection = await websockets.connect(
                str(url),
                extra_headers=headers,
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
        
    async def __aexit__(self, exc_type, exc, exc_tb) -> None:
        """Clean up the connection when exiting context.
        
        :param exc_type: Exception type, if any.
        :param exc: Exception value, if any.
        :param exc_tb: Exception traceback, if any.
        """
        if self.__connection is not None:
            await self.__connection.close()


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
        :rtype: ~azure.ai.voicelive.aio.VoiceLiveConnectionManager
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
