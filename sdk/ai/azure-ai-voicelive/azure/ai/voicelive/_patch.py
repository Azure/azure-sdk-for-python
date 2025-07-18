# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import asyncio
import json
import logging
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union
from typing_extensions import TypedDict

import aiohttp
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
    "VoiceLiveResponseResource",
    "VoiceLiveInputAudioBufferResource",
    "VoiceLiveOutputAudioBufferResource",
    "VoiceLiveConversationResource",
    "VoiceLiveConversationItemResource",
    "VoiceLiveTranscriptionSessionResource",
]  # Add all objects you want publicly available to users at this package level

log = logging.getLogger(__name__)


class WebsocketConnectionOptions(TypedDict, total=False):
    """Websocket connection options for VoiceLive API WebSocket connections.

    Based on options compatible with aiohttp library.
    """

    # Common websocket options
    compression: Optional[bool]
    max_msg_size: Optional[int]  # Replaces max_size from websockets
    timeout: Optional[float]  # Replaces close_timeout from websockets
    heartbeat: Optional[float]  # Replaces ping_interval from websockets
    autoclose: Optional[bool]  # Whether to automatically close the connection
    autoping: Optional[bool]  # Whether to automatically respond to pings


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
        event = {"type": "session.update", "session": session}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)


class VoiceLiveResponseResource:
    """Resource for response management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a response resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def create(self, *, response: Optional[Dict[str, Any]] = None, event_id: Optional[str] = None) -> None:
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

        self._connection.send(event)

    def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
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

        self._connection.send(event)


class VoiceLiveInputAudioBufferResource:
    """Resource for input audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an input audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def append(self, *, audio: str, event_id: Optional[str] = None) -> None:
        """Append audio to the input buffer.

        The audio buffer is temporary storage you can write to and later commit.
        In Server VAD mode, the audio buffer is used to detect speech and the
        server will decide when to commit.

        :param audio: Base64-encoded audio data.
        :type audio: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "input_audio_buffer.append", "audio": audio}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)

    def commit(self, *, event_id: Optional[str] = None) -> None:
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

        self._connection.send(event)

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the input audio buffer.

        The server will respond with an `input_audio_buffer.cleared` event.

        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "input_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)


class VoiceLiveOutputAudioBufferResource:
    """Resource for output audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an output audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the output audio buffer.

        This will trigger the server to stop generating audio and emit
        an `output_audio_buffer.cleared` event.

        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "output_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)


class VoiceLiveConversationItemResource:
    """Resource for conversation item management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation item resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def create(
        self, *, item: Dict[str, Any], previous_item_id: Optional[str] = None, event_id: Optional[str] = None
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
        event = {"type": "conversation.item.create", "item": item}
        if previous_item_id:
            event["previous_item_id"] = previous_item_id
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)

    def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete a conversation item.

        Remove an item from the conversation history.

        :param item_id: ID of the item to delete.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "conversation.item.delete", "item_id": item_id}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)

    def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Retrieve a conversation item.

        Get the server's representation of a specific item in the conversation history.

        :param item_id: ID of the item to retrieve.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "conversation.item.retrieve", "item_id": item_id}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)

    def truncate(self, *, item_id: str, audio_end_ms: int, content_index: int, event_id: Optional[str] = None) -> None:
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
            "content_index": content_index,
        }
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)


class VoiceLiveConversationResource:
    """Resource for conversation management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection
        self.item = VoiceLiveConversationItemResource(connection)


class VoiceLiveTranscriptionSessionResource:
    """Resource for transcription session management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a transcription session resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def update(self, *, session: Dict[str, Any], event_id: Optional[str] = None) -> None:
        """Update the transcription session.

        :param session: Transcription session configuration.
        :type session: Dict[str, Any]
        :param event_id: Optional ID for the event.
        :type event_id: Optional[str]
        """
        event = {"type": "transcription_session.update", "session": session}
        if event_id:
            event["event_id"] = event_id

        self._connection.send(event)


class _AsyncWebSocketConnection:
    """Internal class for managing async WebSocket connection in a sync context."""

    def __init__(self, session, connection):
        self._session = session
        self._connection = connection
        self._loop = asyncio.new_event_loop()
        self._queue = asyncio.Queue()
        self._running = True
        self._thread = None

    async def _receiver(self):
        """Background task to receive messages from the WebSocket."""
        try:
            while self._running:
                msg = await self._connection.receive()

                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._queue.put(("text", msg.data.encode("utf-8")))
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    await self._queue.put(("binary", msg.data))
                elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    code = self._connection.close_code or 1000
                    reason =  ""
                    await self._queue.put(("close", (code, reason)))
                    break
        except Exception as e:
            if self._running:
                await self._queue.put(("error", e))

    def start(self):
        """Start the background receiving task."""

        def run_loop():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        import threading

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

        # Start the receiver task
        asyncio.run_coroutine_threadsafe(self._receiver(), self._loop)

    def recv(self, decode=True):
        """Receive a message from the WebSocket."""
        future = asyncio.run_coroutine_threadsafe(self._queue.get(), self._loop)
        msg_type, msg_data = future.result()

        if msg_type == "close":
            code, reason = msg_data
            raise VoiceLiveConnectionClosed(code, reason)
        elif msg_type == "error":
            raise VoiceLiveConnectionError(f"WebSocket error: {msg_data}")
        else:
            return msg_data  # Return bytes data

    def send(self, data):
        """Send a message to the WebSocket."""
        if isinstance(data, str):
            coro = self._connection.send_str(data)
        else:
            coro = self._connection.send_bytes(data)
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        future.result()  # Wait for the send to complete

    def close(self, code=1000, reason=""):
        """Close the WebSocket connection."""
        self._running = False

        async def _close():
            await self._connection.close(code=code, message=reason)
            await self._session.close()

        future = asyncio.run_coroutine_threadsafe(_close(), self._loop)
        future.result()  # Wait for close to complete

        # Stop the event loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=5.0)


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
        api_version: str = "2024-10-01",
        extra_query: Dict[str, Any],
        extra_headers: Dict[str, Any],
        websocket_connection_options: Dict[str, Any],
    ) -> None:
        self.__client = client
        self.__model = model
        self.__apiVersion = api_version
        self.__connection = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__websocket_connection_options = self._map_websocket_options(websocket_connection_options)

    def _map_websocket_options(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """Map websockets options to aiohttp options.

        :param options: The original websockets options.
        :type options: Dict[str, Any]
        :return: Mapped aiohttp options.
        :rtype: Dict[str, Any]
        """
        mapped_options = {}

        # Map options with different names
        if "max_size" in options:
            mapped_options["max_msg_size"] = options.pop("max_size")
        if "close_timeout" in options:
            mapped_options["timeout"] = options.pop("close_timeout")
        if "ping_interval" in options:
            mapped_options["heartbeat"] = options.pop("ping_interval")

        # Add compatible options that can be used directly
        if "compression" in options:
            mapped_options["compress"] = options.pop("compression")

        # Add any remaining options that might be directly compatible
        for key, value in options.items():
            if key not in ("ping_timeout", "open_timeout", "max_queue"):  # Skip options that aren't supported
                mapped_options[key] = value

        return mapped_options

    def __enter__(self) -> VoiceLiveConnection:
        """Create and return a WebSocket connection.

        :return: A VoiceLiveConnection instance.
        :rtype: ~azure.ai.voicelive.VoiceLiveConnection
        :raises ImportError: If the aiohttp package is not installed.
        :raises VoiceLiveConnectionError: If the connection cannot be established.
        """
        loop = asyncio.new_event_loop()

        try:
            url = self._prepare_url()
            log.debug("Connecting to %s", url)

            if self.__websocket_connection_options:
                log.debug("Connection options: %s", self.__websocket_connection_options)

            # Get auth headers
            auth_headers = {"api-key": self.__client._config.credential.key}
            headers = {**auth_headers, **self.__extra_headers}

            async def setup_connection():
                session = aiohttp.ClientSession()
                try:
                    ws_connection = await session.ws_connect(
                        str(url),
                        headers=headers,
                        **self.__websocket_connection_options,
                        proxy="http://localhost:8888"
                    )
                    return session, ws_connection
                except Exception as e:
                    await session.close()
                    raise e

            session, ws_connection = loop.run_until_complete(setup_connection())

            # Create the async connection wrapper
            async_connection = _AsyncWebSocketConnection(session, ws_connection)
            async_connection.start()

            self.__connection = VoiceLiveConnection(async_connection)
            return self.__connection

        except Exception as e:
            loop.close()
            raise VoiceLiveConnectionError(f"Failed to establish WebSocket connection: {e}") from e

    def _prepare_url(self) -> httpx.URL:
        """Prepare the WebSocket URL.

        :return: The prepared URL.
        :rtype: httpx.URL
        """
        base_url = httpx.URL(self.__client._config.endpoint)
        # Ensure WebSocket scheme
        if base_url.scheme.startswith("http"):
            base_url = base_url.copy_with(scheme="wss" if base_url.scheme == "https" else "ws")

        # Add query parameters
        params = {"model": self.__model, "api-version": self.__apiVersion}
        params.update(self.__extra_query)
        merge_raw_path = base_url.raw_path.rstrip(b"/") + b"/voice-agent/realtime"

        url = base_url.copy_with(raw_path=merge_raw_path)
        url = url.copy_with(params=params)
        return url

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
        api_version: str = "2024-10-01",
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
            api_version=api_version,
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
