# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import aiohttp
import json
import logging
from contextlib import AbstractAsyncContextManager
from typing import Any, Dict, List, Mapping, Optional, Union, AsyncIterator
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

import aiohttp
from typing_extensions import TypedDict

from azure.ai.voicelive.models._models import (
    ClientEventConversationItemCreate,
    ClientEventConversationItemDelete,
    ClientEventConversationItemRetrieve,
    ClientEventConversationItemTruncate,
    ClientEventInputAudioBufferAppend,
    ClientEventInputAudioBufferClear,
    ClientEventInputAudioBufferCommit,
    ClientEventResponseCancel,
    ClientEventResponseCreate,
    ClientEventSessionUpdate,
)
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline import policies
from ..models import ClientEvent, ServerEvent, RequestSession
from .._patch import ConnectionError, ConnectionClosed
try:  # Python 3.11+
    from typing import NotRequired  # type: ignore[attr-defined]
except ImportError:  # Python <=3.10
    from typing_extensions import NotRequired


__all__: List[str] = [
    "connect",
    "WebsocketConnectionOptions",
    "VoiceLiveConnection",
    "SessionResource",
    "ResponseResource",
    "InputAudioBufferResource",
    "OutputAudioBufferResource",
    "ConversationResource",
    "ConversationItemResource",
    "TranscriptionSessionResource",
]

log = logging.getLogger(__name__)


def _json_default(o: Any) -> Any:
    """
    Fallback JSON serializer for generated SDK models.

    :param o: The object to serialize.
    :type o: Any
    :return: A JSON-serializable representation of ``o``.
    :rtype: Any
+   """
    for attr in ("serialize", "as_dict", "to_dict"):
        fn = getattr(o, attr, None)
        if callable(fn):
            try:
                return fn()
            except TypeError:
                # some generators expose class/static serialize(obj)
                return getattr(o.__class__, attr)(o)
    if hasattr(o, "__dict__"):
        # strip private attrs
        return {k: v for k, v in vars(o).items() if not k.startswith("_")}
    raise TypeError(f"{type(o).__name__} is not JSON serializable")

class SessionResource:
    """Resource for session management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a session resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def update(self, *, session: Union[Mapping[str, Any], "RequestSession"], event_id: Optional[str] = None) -> None:
        """
        Update the session configuration.

        :keyword Mapping[str, Any] or ~azure.ai.voicelive.models.RequestSession session:
            Session configuration parameters.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        if isinstance(session, RequestSession):
            # overload: keyword form requires a typed RequestSession
            event = ClientEventSessionUpdate(session=session)
        else:
            # overload: mapping form takes a single Mapping argument
            event = ClientEventSessionUpdate({"session": dict(session)})
        if event_id:
            event["event_id"] = event_id

        await self._connection.send(event)


class ResponseResource:
    """Resource for response management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a response resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def create(self, *, response: Optional[Mapping[str, Any]] = None, event_id: Optional[str] = None) -> None:
        """Create a response from the model.

        This event instructs the server to create a Response (triggering model inference).
        When in Server VAD mode, the server may create responses automatically.

        :keyword Mapping[str, Any] response: Optional response configuration.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventResponseCreate()
        if response is not None:
            event["response"] = dict(response)
        if event_id:
            event["event_id"] = event_id

        await self._connection.send(event)

    async def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
        """Cancel an in-progress response.

        The server will respond with a `response.cancelled` event or an error if
        there is no response to cancel.

        :keyword str response_id: Optional ID of the response to cancel.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventResponseCancel()
        if response_id:
            event["response_id"] = response_id
        if event_id:
            event["event_id"] = event_id

        await self._connection.send(event)


class InputAudioBufferResource:
    """Resource for input audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an input audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def append(self, *, audio: str, event_id: Optional[str] = None) -> None:
        """Append audio to the input buffer.

        :keyword str audio: Base64-encoded audio data in the format declared by the session config.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventInputAudioBufferAppend(audio=audio)
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)

    async def commit(self, *, event_id: Optional[str] = None) -> None:
        """Commit the input audio buffer.

        Creates a new user message item in the conversation.

        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventInputAudioBufferCommit()
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)

    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the input audio buffer.

        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventInputAudioBufferClear()
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)


class OutputAudioBufferResource:
    """Resource for output audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an output audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the output audio buffer.

        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event: Dict[str, Any] = {"type": "output_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)


class ConversationItemResource:
    """Resource for conversation item management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation item resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def create(
        self, *, item: Mapping[str, Any], previous_item_id: Optional[str] = None, event_id: Optional[str] = None
    ) -> None:
        """Create a new conversation item.

        :keyword Mapping[str, Any] item: The item to create (message/functions/etc.).
        :keyword str previous_item_id: Optional ID of the item after which to insert this item.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventConversationItemCreate({"item": dict(item)})
        if previous_item_id:
            event["previous_item_id"] = previous_item_id
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)

    async def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete a conversation item.

        :keyword str item_id: ID of the item to delete.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventConversationItemDelete(item_id=item_id)
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)

    async def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Retrieve a conversation item.

        :keyword str item_id: ID of the item to retrieve.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventConversationItemRetrieve(item_id=item_id)
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)

    async def truncate(
        self, *, item_id: str, audio_end_ms: int, content_index: int, event_id: Optional[str] = None
    ) -> None:
        """Truncate a conversation item's audio.

        :keyword str item_id: ID of the item to truncate.
        :keyword int audio_end_ms: Time in milliseconds where to truncate the audio.
        :keyword int content_index: Index of the content to truncate.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event = ClientEventConversationItemTruncate(
            item_id=item_id, audio_end_ms=audio_end_ms, content_index=content_index
        )
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)


class ConversationResource:
    """Resource for conversation management.

    Exposes helpers for manipulating items in the active conversation.

    :ivar item: Resource for per-item operations (create, delete, retrieve, truncate)
        within the conversation.
    :vartype item: ~azure.ai.voicelive.aio.ConversationItemResource
    """

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection
        self.item: ConversationItemResource = ConversationItemResource(connection)


class TranscriptionSessionResource:
    """Resource for transcription session management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a transcription session resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def update(self, *, session: Mapping[str, Any], event_id: Optional[str] = None) -> None:
        """Update the transcription session.

        :keyword Mapping[str, Any] session: Transcription session configuration.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        event: Dict[str, Any] = {"type": "transcription_session.update", "session": dict(session)}
        if event_id:
            event["event_id"] = event_id
        await self._connection.send(event)


class VoiceLiveConnection:
    """
    Represents an active asynchronous WebSocket connection to the Azure Voice Live API.

    This class exposes resource-specific helpers for interacting with the service:
    - :attr:`session` — manage session configuration updates.
    - :attr:`response` — create or cancel model responses.
    - :attr:`input_audio_buffer` — append, commit, or clear audio data before processing.
    - :attr:`output_audio_buffer` — clear generated audio output.
    - :attr:`conversation` — manage conversation items (create, delete, truncate).
    - :attr:`transcription_session` — update transcription-specific configuration.

    Instances are yielded by the :func:`~azure.ai.voicelive.aio.connect` context manager.

    :ivar session: Resource for managing session updates.
    :vartype session: ~azure.ai.voicelive.aio.SessionResource
    :ivar response: Resource for creating and cancelling model responses.
    :vartype response: ~azure.ai.voicelive.aio.ResponseResource
    :ivar input_audio_buffer: Resource for managing input audio buffer.
    :vartype input_audio_buffer: ~azure.ai.voicelive.aio.InputAudioBufferResource
    :ivar output_audio_buffer: Resource for clearing output audio.
    :vartype output_audio_buffer: ~azure.ai.voicelive.aio.OutputAudioBufferResource
    :ivar conversation: Resource for managing the conversation and its items.
    :vartype conversation: ~azure.ai.voicelive.aio.ConversationResource
    :ivar transcription_session: Resource for updating transcription session configuration.
    :vartype transcription_session: ~azure.ai.voicelive.aio.TranscriptionSessionResource
    """

    def __init__(self, client_session: aiohttp.ClientSession, ws: aiohttp.ClientWebSocketResponse) -> None:
        """Initialize a VoiceLiveConnection instance.

        :param client_session: The active aiohttp ClientSession used for HTTP and WebSocket operations.
        :type client_session: aiohttp.ClientSession
        :param ws: The established WebSocket connection to the Voice Live service.
        :type ws: aiohttp.ClientWebSocketResponse
        """
        self._client_session: aiohttp.ClientSession = client_session
        self._connection: aiohttp.ClientWebSocketResponse = ws

        # Add all resource attributes
        self.session = SessionResource(self)
        self.response = ResponseResource(self)
        self.input_audio_buffer = InputAudioBufferResource(self)
        self.conversation = ConversationResource(self)
        self.output_audio_buffer = OutputAudioBufferResource(self)
        self.transcription_session = TranscriptionSessionResource(self)

    async def __aiter__(self) -> AsyncIterator[ServerEvent]:
        """
        Yield typed events until the connection is closed.

        :return: An async iterator over typed server events.
        :rtype: typing.AsyncIterator[~azure.ai.voicelive.models.ServerEvent]
        """
        try:
            while True:
                yield await self.recv()
        except (aiohttp.ClientError, ConnectionClosed, RuntimeError) as e:
            log.debug("Connection closed: %s", e)
            return

    async def recv(self) -> ServerEvent:
        """
        Receive and parse the next message as a typed event.

        :return: The next typed server event.
        :rtype: ~azure.ai.voicelive.models.ServerEvent
        """
        try:
            return ServerEvent.deserialize(await self.recv_bytes())
        except (ValueError, TypeError) as e:
            log.error("Error parsing message: %s", e)
            raise ConnectionError(f"Failed to parse message: {e}") from e

    async def recv_bytes(self) -> bytes:
        """
        Receive raw bytes from the connection.

        :return: The raw WebSocket message payload as bytes.
        :rtype: bytes
        """
        try:
            msg = await self._connection.receive()

            if msg.type == aiohttp.WSMsgType.TEXT:
                log.debug("Received websocket text message: %s", msg.data)
                return msg.data.encode("utf-8")
            if msg.type == aiohttp.WSMsgType.BINARY:
                log.debug("Received websocket binary message: %s", msg.data)
                return msg.data
            if msg.type == aiohttp.WSMsgType.CLOSE:
                code = self._connection.close_code or 1000
                reason = ""
                log.debug("WebSocket connection closed with code %s: %s", code, reason)
                raise ConnectionClosed(code, reason)
            if msg.type == aiohttp.WSMsgType.ERROR:
                log.error("WebSocket connection error: %s", self._connection.exception())
                raise ConnectionClosed(1006, str(self._connection.exception()))
            if msg.type == aiohttp.WSMsgType.CLOSED:
                log.debug("WebSocket connection already closed")
                raise ConnectionClosed(1000, "Connection closed")
            
            log.warning("Unexpected WebSocket message type: %s", msg.type)
            return b""
        except aiohttp.ClientError as e:
            code = getattr(e, "code", 1006)
            reason = str(e)
            raise ConnectionClosed(code, reason) from e

    async def send(self, event: Union[Mapping[str, Any], ClientEvent]) -> None:
        """
        Send an event to the server over the active WebSocket connection (async).

        Accepts either:

        - A mapping-like object (e.g., dict, MappingProxyType). It will be copied
          to a plain dict and JSON-encoded. Any nested SDK models are handled
          by a fallback serializer.
        - A structured ClientEvent model. If the object (or its class) exposes a
          `serialize()` method, that is used to produce the wire format.

        :param event: The event to send.
        :type event: Union[Mapping[str, Any], ~azure.ai.voicelive.models.ClientEvent]
        :raises ConnectionError: If serialization or the WebSocket send fails.
        """
        try:
            # Build a JSON-ready object or string first
            payload: object
            if isinstance(event, ClientEvent):
                serialize_fn = getattr(type(event), "serialize", None)
                if callable(serialize_fn):
                    payload = serialize_fn(event)  # may be str or object (type checker: object | str)
                else:
                    payload = json.dumps(event, default=_json_default)
            elif isinstance(event, Mapping):
                payload = json.dumps(dict(event), default=_json_default)
            else:
                payload = json.dumps(event, default=_json_default)

            # Ensure we pass a str to send_str
            data: str = (
                payload if isinstance(payload, str) else json.dumps(payload, default=_json_default)
            )

            await self._connection.send_str(data)
        except (TypeError, ValueError, aiohttp.ClientError, RuntimeError) as e:
            log.error("Failed to send event: %s", e)
            raise ConnectionError(f"Failed to send event: {e}") from e

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket and underlying HTTP session.

        This will gracefully terminate the connection to the Voice Live service and
        release any network resources.

        :keyword int code: WebSocket close code to send to the server. Defaults to ``1000`` (Normal Closure).
        :keyword str reason: Optional reason string to include in the close frame.
        :rtype: None
        """
        try:
            await self._connection.close(code=code, message=reason.encode("utf-8"))
        except (aiohttp.ClientError, RuntimeError) as e:
            log.warning("Error closing connection: %s", e)
        try:
            await self._client_session.close()
        except (aiohttp.ClientError, RuntimeError) as e:
            log.warning("Error closing session: %s", e)


class WebsocketConnectionOptions(TypedDict, total=False):
    """
    Advanced WebSocket connection options for VoiceLive API connections.

    These options correspond to parameters accepted by :mod:`aiohttp`'s
    `ws_connect` method and control low-level WebSocket behavior.
    All keys are optional — if omitted, default values will be applied.

    :keyword compression: Enable per-message compression.
        - ``True`` enables compression.
        - ``False`` disables compression.
        If omitted, defaults to the aiohttp default.
    :type compression: bool

    :keyword max_msg_size: Maximum message size in bytes.
        Messages larger than this limit will cause the connection to close.
        If omitted, defaults to 10 MiB (10 * 1024 * 1024).
    :type max_msg_size: int

    :keyword timeout: Close timeout in seconds.
        Maximum time to wait for the connection to close gracefully.
        If omitted, defaults to aiohttp's internal default.
    :type timeout: float

    :keyword heartbeat: Interval in seconds for sending ping frames to keep
        the connection alive. If omitted, defaults to 30 seconds.
    :type heartbeat: float

    :keyword autoclose: Automatically close the connection when a close frame
        is received. Defaults to True if omitted.
    :type autoclose: bool

    :keyword autoping: Automatically respond to ping frames with pong frames.
        Defaults to True if omitted.
    :type autoping: bool
    """

    compression: NotRequired[bool]
    max_msg_size: NotRequired[int]
    timeout: NotRequired[float]
    heartbeat: NotRequired[float]
    autoclose: NotRequired[bool]
    autoping: NotRequired[bool]


class _VoiceLiveConnectionManager(AbstractAsyncContextManager["VoiceLiveConnection"]):
    """Async manager for VoiceLive WebSocket connections."""

    def __init__(
        self,
        *,
        credential: Union[AzureKeyCredential, TokenCredential],
        endpoint: str,
        model: str,
        api_version: str = "2025-05-01-preview",
        extra_query: Mapping[str, Any],
        extra_headers: Mapping[str, Any],
        connection_options: Optional[WebsocketConnectionOptions] = None,
        **kwargs: Any,
    ) -> None:
        self._credential = credential
        self._endpoint = endpoint
        self.__credential_scopes = kwargs.pop("credential_scopes", "https://cognitiveservices.azure.com/.default")
        self.__model = model
        self.__api_version = api_version
        self.__connection: Optional[VoiceLiveConnection] = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__connection_options = self._map_websocket_options(connection_options or {})
        self.__proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)

    def _map_websocket_options(self, options: WebsocketConnectionOptions) -> Dict[str, Any]:
        """
        Map user options to :mod:`aiohttp` ``ws_connect`` kwargs (accept both TypedDict keys and common aliases).

        :param options: The user-provided WebSocket options.
        :type options: ~azure.ai.voicelive.aio.WebsocketConnectionOptions
        :return: Mapped options suitable for ``aiohttp.ClientSession.ws_connect``.
        :rtype: Dict[str, Any]
        """
        # copy to a plain dict so we can safely check/pop alias keys without mypy complaints
        src: Dict[str, Any] = dict(options)
        mapped: Dict[str, Any] = {}
        # aliases commonly used by other libs
        if "max_size" in src:
            mapped["max_msg_size"] = src.pop("max_size")
        if "close_timeout" in src:
            mapped["timeout"] = src.pop("close_timeout")
        if "ping_interval" in src:
            mapped["heartbeat"] = src.pop("ping_interval")
        if "compression" in src:
            mapped["compress"] = src.pop("compression")
        # pass through supported aiohttp-style keys from our TypedDict
        for key in ("max_msg_size", "timeout", "heartbeat", "autoclose", "autoping"):
            if key in src:
                mapped[key] = src[key]
        return mapped

    async def __aenter__(self) -> VoiceLiveConnection:
        """
        Create and return an async WebSocket connection.

        :return: An established VoiceLiveConnection.
        :rtype: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        try:
            url = self._prepare_url()
            log.debug("Connecting to %s", url)

            self.__connection_options.setdefault("max_msg_size", 10 * 1024 * 1024)
            self.__connection_options.setdefault("heartbeat", 30)

            if self.__proxy_policy:
                self.__proxy_policy.proxies = {
                    "http": "http://localhost:8888",
                    "https": "http://localhost:8888",
                }

            auth_headers = self._get_auth_headers()
            headers = {**auth_headers, **dict(self.__extra_headers)}

            session = aiohttp.ClientSession()
            try:
                connection_obj = await session.ws_connect(
                    str(url), headers=headers, **self.__connection_options
                )
                self.__connection = VoiceLiveConnection(session, connection_obj)
                return self.__connection
            except aiohttp.ClientError as e:
                await session.close()
                raise ConnectionError(f"Failed to establish WebSocket connection: {e}") from e
        except (aiohttp.ClientError, ValueError) as e:
            raise ConnectionError(f"Failed to establish WebSocket connection: {e}") from e

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for WebSocket connection.

        :return: A dict of HTTP headers for authentication.
        :rtype: Dict[str, str]
        """
        if isinstance(self._credential, AzureKeyCredential):
            return {"api-key": self._credential.key}
        token = self._credential.get_token(self.__credential_scopes)
        return {"Authorization": f"Bearer {token.token}"}

    def _prepare_url(self) -> str:
        """
        Prepare the WebSocket URL.

        :return: The WebSocket URL as a string.
        :rtype: str
        """
        parsed = urlparse(self._endpoint)
        scheme = (
            "wss"
            if parsed.scheme.startswith("http") and parsed.scheme == "https"
            else ("ws" if parsed.scheme.startswith("http") else parsed.scheme)
        )

        params: Dict[str, Any] = {"model": self.__model, "api-version": self.__api_version}
        params.update(dict(self.__extra_query))

        existing_params = parse_qs(parsed.query)
        for key, value_list in existing_params.items():
            if key not in params:
                params[key] = value_list[0] if value_list else ""

        path = parsed.path.rstrip("/") + "/voice-agent/realtime"
        url = urlunparse((scheme, parsed.netloc, path, parsed.params, urlencode(params), parsed.fragment))
        return url

    async def __aexit__(self, exc_type, exc, exc_tb) -> None:
        """
        Clean up the connection when exiting context.

        :param exc_type: Exception type if an error occurred.
        :type exc_type: type | None
        :param exc: Exception instance if an error occurred.
        :type exc: BaseException | None
        :param exc_tb: Exception traceback if an error occurred.
        :type exc_tb: types.TracebackType | None
        :rtype: None
        """
        if self.__connection is not None:
            await self.__connection.close()


def connect(
    *,
    credential: Union[AzureKeyCredential, TokenCredential],
    endpoint: str,
    model: str,
    api_version: str = "2025-05-01-preview",
    query: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
    connection_options: Optional[WebsocketConnectionOptions] = None,
    **kwargs: Any,
) -> AbstractAsyncContextManager["VoiceLiveConnection"]:
    """
    Create and manage an asynchronous WebSocket connection to the Azure Voice Live API.

    This helper returns an async context manager that:
    - Authenticates with the service using an API key or Azure Active Directory token.
    - Prepares the correct WebSocket URL and query parameters.
    - Establishes the connection and yields a :class:`~azure.ai.voicelive.aio.VoiceLiveConnection`.
    - Automatically cleans up the connection when the context exits.

    :keyword ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential credential:
        The credential used to authenticate with the service.
    :keyword str endpoint: The service endpoint (e.g., ``https://<region>.api.cognitive.microsoft.com``).
    :keyword str model: The model identifier to use for the session.
    :keyword str api_version: The API version to use (default: ``"2025-05-01-preview"``).
    :keyword Mapping[str, Any] query: Optional query parameters to include in the WebSocket URL.
    :keyword Mapping[str, Any] headers: Optional HTTP headers to include in the WebSocket handshake.
    :keyword ~azure.ai.voicelive.aio.WebsocketConnectionOptions connection_options:
        Optional advanced WebSocket options compatible with :mod:`aiohttp`.
    :keyword Any kwargs: Additional keyword arguments for advanced configuration.

    :return: An async context manager yielding a connected :class:`~azure.ai.voicelive.aio.VoiceLiveConnection`.
    :rtype: collections.abc.AsyncContextManager[~azure.ai.voicelive.aio.VoiceLiveConnection]
    """
    return _VoiceLiveConnectionManager(
        credential=credential,
        endpoint=endpoint,
        model=model,
        api_version=api_version,
        extra_query=query or {},
        extra_headers=headers or {},
        connection_options=connection_options or {},
        **kwargs,
    )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
