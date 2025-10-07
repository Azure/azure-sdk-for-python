# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import json
import logging
from contextlib import AbstractAsyncContextManager
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from typing import Any, Mapping, Optional, Union, AsyncIterator, cast

# === Third-party ===
from typing_extensions import TypedDict
import aiohttp
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
    ConversationRequestItem,
    ResponseCreateParams,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.exceptions import AzureError
from azure.core.pipeline import policies

# === Local ===
from ..models import ClientEvent, ServerEvent, RequestSession

if sys.version_info >= (3, 11):
    from typing import NotRequired  # noqa: F401
else:
    from typing_extensions import NotRequired  # noqa: F401

__all__: list[str] = [
    "connect",
    "WebsocketConnectionOptions",
    "VoiceLiveConnection",
    "SessionResource",
    "ResponseResource",
    "InputAudioBufferResource",
    "OutputAudioBufferResource",
    "ConnectionError",
    "ConnectionClosed",
    "ConversationResource",
    "ConversationItemResource",
    "TranscriptionSessionResource",
]

log = logging.getLogger(__name__)


def _json_default(o: Any) -> Any:
    """
    Fallback JSON serializer for SDK models and other non-JSON-native objects.

    :param o: The object to convert to a JSON-compatible form.
    :type o: Any
    :return: A JSON-serializable representation (e.g., ``dict``, ``list``, ``str``, etc.).
    :rtype: Any
    :raises TypeError: If *o* cannot be converted into a JSON-serializable form.
    """
    for attr in ("as_dict", "to_dict"):
        fn = getattr(o, attr, None)
        if callable(fn):
            try:
                return fn()
            except TypeError:
                # Some generators expose class/static serialize(obj)
                return getattr(o.__class__, attr)(o)
    if hasattr(o, "__dict__"):
        # Strip private attributes
        return {k: v for k, v in vars(o).items() if not k.startswith("_")}
    raise TypeError(f"{type(o).__name__} is not JSON serializable")


class ConnectionError(AzureError):
    """Base exception for Voice Live WebSocket connection errors."""


class ConnectionClosed(ConnectionError):
    """Raised when a WebSocket connection is closed."""

    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket connection closed with code {code}: {reason}")


class SessionResource:
    """Resource for session management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a session resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.aio.VoiceLiveConnection
        """
        self._connection = connection

    async def update(
        self,
        *,
        session: Union[Mapping[str, Any], "RequestSession"],
        event_id: Optional[str] = None,
    ) -> None:
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

    async def create(
        self,
        *,
        response: Optional[Union[ResponseCreateParams, Mapping[str, Any]]] = None,
        event_id: Optional[str] = None,
        additional_instructions: Optional[str] = None,
    ) -> None:
        """Create a response from the model.

        This event instructs the server to create a Response (triggering model inference).
        When in Server VAD mode, the server may create responses automatically.

        :keyword response: Optional response configuration to send.
        :keyword type response: ~azure.ai.voicelive.models.ResponseCreateParams or Mapping[str, Any] or None
        :keyword event_id: Optional ID for the event.
        :keyword type event_id: str or None
        :keyword additional_instructions: Extra system prompt appended to the session's default, for this response only.
        :keyword type additional_instructions: str or None
        :rtype: None
        """
        if response is not None and not isinstance(response, ResponseCreateParams):
            response = ResponseCreateParams(**dict(response))

        event = ClientEventResponseCreate(
            event_id=event_id,
            response=response,
            additional_instructions=additional_instructions,
        )

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
        event: dict[str, Any] = {"type": "output_audio_buffer.clear"}
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
        self,
        *,
        item: Union[ConversationRequestItem, Mapping[str, Any]],
        previous_item_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> None:
        """Create a new conversation item.

        :keyword ConversationRequestItem | Mapping[str, Any] item: The item to create (message/functions/etc.).
        :keyword str previous_item_id: Optional ID of the item after which to insert this item.
        :keyword str event_id: Optional ID for the event.
        :rtype: None
        """
        if not isinstance(item, ConversationRequestItem):
            item = ConversationRequestItem(**dict(item))

        event = ClientEventConversationItemCreate(
            event_id=event_id,
            previous_item_id=previous_item_id,
            item=item,
        )
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
        event: dict[str, Any] = {"type": "transcription_session.update", "session": dict(session)}
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

    _client_session: aiohttp.ClientSession
    _connection: aiohttp.ClientWebSocketResponse

    session: "SessionResource"
    response: "ResponseResource"
    input_audio_buffer: "InputAudioBufferResource"
    conversation: "ConversationResource"
    output_audio_buffer: "OutputAudioBufferResource"
    transcription_session: "TranscriptionSessionResource"

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
            raw = await self.recv_bytes()  # bytes or str
            if not raw:
                # Treat empty payload as a closed/errored connection
                raise ConnectionClosed(1006, "Empty WebSocket frame")

            payload = json.loads(raw.decode("utf-8"))
            event = cast("ServerEvent", ServerEvent.deserialize(payload))
            return event
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
        Send an event to the server over the active WebSocket connection (asynchronously).

        Supported input types:

        * **Mapping-like object** (e.g., ``dict``, ``MappingProxyType``) — converted to
            a plain ``dict`` and then JSON-encoded. Any nested SDK models are serialized
            using the fallback serializer ``_json_default()``.
        * **ClientEvent model instance** — converted to a plain dictionary via
            ``as_dict()`` (preserving REST field names and discriminators), then JSON-encoded.
        * **Other objects** — directly passed to ``json.dumps()`` with ``_json_default()``
            handling non-JSON-native values.

        :param event: The event to send.
        :type event: Union[Mapping[str, Any], ~azure.ai.voicelive.models.ClientEvent]
        :raises ConnectionError: If serialization fails or the WebSocket send raises an error.
        """
        try:
            # Build a JSON-ready object or string first
            payload: object
            if isinstance(event, ClientEvent):
                payload = event.as_dict()
            elif isinstance(event, Mapping):
                payload = json.dumps(dict(event), default=_json_default)
            else:
                payload = json.dumps(event, default=_json_default)

            # Ensure we pass a str to send_str
            data: str = payload if isinstance(payload, str) else json.dumps(payload, default=_json_default)

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
    Transport-agnostic WebSocket connection options for VoiceLive.

    These control common WS behaviors (compression, message size limits,
    timeouts, ping/pong handling). Unless specified, defaults are determined
    by the underlying WebSocket library.

    :keyword compression: Enable per-message compression. Use ``True`` to enable,
        ``False`` to disable. Advanced users may pass an ``int`` to select a zlib
        window value if supported by the transport.
    :type compression: bool | int

    :keyword max_msg_size: Maximum message size in bytes before the client closes
        the connection.
    :type max_msg_size: int

    :keyword heartbeat: Interval in seconds between keep-alive pings.
    :type heartbeat: float

    :keyword autoclose: Automatically close when a close frame is received.
    :type autoclose: bool

    :keyword autoping: Automatically respond to ping frames with pong frames.
    :type autoping: bool

    :keyword receive_timeout: Max seconds to wait for a single incoming message
        on an established WebSocket.
    :type receive_timeout: float

    :keyword close_timeout: Max seconds to wait for a graceful close handshake.
    :type close_timeout: float

    :keyword handshake_timeout: Max seconds for connection establishment
        (DNS/TCP/TLS + WS upgrade). Note: with aiohttp this is applied on the
        ClientSession (not a ws_connect kwarg), so must be handled by the caller.
    :type handshake_timeout: float

    :keyword vendor_options: Optional implementation-specific options passed
        through as-is to the underlying library (not part of the stable API).
    :type vendor_options: Mapping[str, Any]
    """

    compression: NotRequired[Union[bool, int]]
    max_msg_size: NotRequired[int]
    heartbeat: NotRequired[float]
    autoclose: NotRequired[bool]
    autoping: NotRequired[bool]
    receive_timeout: NotRequired[float]
    close_timeout: NotRequired[float]
    handshake_timeout: NotRequired[float]
    vendor_options: NotRequired[Mapping[str, Any]]


class _VoiceLiveConnectionManager(AbstractAsyncContextManager["VoiceLiveConnection"]):
    """Async manager for VoiceLive WebSocket connections."""

    def __init__(
        self,
        *,
        credential: Union["AzureKeyCredential", "AsyncTokenCredential"],
        endpoint: str,
        api_version: str = "2025-10-01",
        model: Optional[str] = None,
        extra_query: Mapping[str, Any],
        extra_headers: Mapping[str, Any],
        connection_options: Optional[WebsocketConnectionOptions] = None,
        **kwargs: Any,
    ) -> None:
        self._credential = credential
        self._endpoint = endpoint
        raw_scopes = kwargs.pop("credential_scopes", ["https://ai.azure.com/.default"])
        self.__credential_scopes = [raw_scopes] if isinstance(raw_scopes, str) else list(raw_scopes)
        self.__api_version = api_version
        self.__model = model

        self.__connection: Optional["VoiceLiveConnection"] = None
        self.__extra_query = extra_query
        self.__extra_headers = extra_headers
        self.__connection_options = self._map_to_aiohttp_ws_options(connection_options or {})
        self.__proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)

    def _map_to_aiohttp_ws_options(self, options: WebsocketConnectionOptions) -> dict[str, Any]:
        """
        Map neutral WebSocket options to :mod:`aiohttp` ``ClientSession.ws_connect`` kwargs.

        NOTE:
        - ``receive_timeout`` and ``close_timeout`` are mapped into a single
          ``aiohttp.ClientWSTimeout`` instance passed as the ``timeout=`` kwarg.
        - ``handshake_timeout`` is NOT an ``ws_connect`` kwarg in aiohttp; it must be
          applied via ``aiohttp.ClientTimeout`` on the session by the caller.

        :param options: User-provided WebSocket options.
        :type options: ~azure.ai.voicelive.aio.WebsocketConnectionOptions
        :return: Options suitable for ``aiohttp.ClientSession.ws_connect``.
        :rtype: dict[str, Any]
        """
        src: dict[str, Any] = dict(options)
        mapped: dict[str, Any] = {}

        # --- Neutral -> aiohttp mapping ---

        # compression (neutral) -> compress (aiohttp expects int or None)
        comp = src.pop("compression", None)
        if comp is True:
            mapped["compress"] = -1  # enable compression with default window bits
        elif comp is False:
            mapped["compress"] = None  # disable compression
        elif isinstance(comp, int):
            mapped["compress"] = comp  # power user provided zlib window value

        # max message size
        if "max_msg_size" in src:
            mapped["max_msg_size"] = int(src.pop("max_msg_size"))

        # ping interval
        if "heartbeat" in src:
            mapped["heartbeat"] = float(src.pop("heartbeat"))

        # autoclose / autoping
        if "autoclose" in src:
            mapped["autoclose"] = bool(src.pop("autoclose"))
        if "autoping" in src:
            mapped["autoping"] = bool(src.pop("autoping"))

        # Build ClientWSTimeout for receive/close timeouts
        ws_timeout_kwargs: dict[str, float] = {}
        recv_to = src.pop("receive_timeout", None)
        if recv_to is not None:
            ws_timeout_kwargs["ws_receive"] = float(recv_to)
        close_to = src.pop("close_timeout", None)
        if close_to is not None:
            ws_timeout_kwargs["ws_close"] = float(close_to)
        if ws_timeout_kwargs:
            mapped["timeout"] = aiohttp.ClientWSTimeout(**ws_timeout_kwargs)

        # handshake_timeout is not a ws_connect kwarg; caller must apply it on session
        _ = src.pop("handshake_timeout", None)  # intentionally ignored here

        # --- Vendor-specific passthrough (escape hatch) ---
        vendor = src.pop("vendor_options", None)
        if isinstance(vendor, Mapping):
            for k, v in vendor.items():
                mapped.setdefault(k, v)

        # Any leftover keys in `src` are intentionally ignored to avoid leaking
        # transport-specific names into our public surface.
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

            self.__connection_options.setdefault("max_msg_size", 4 * 1024 * 1024)
            self.__connection_options.setdefault("heartbeat", 30)

            if self.__proxy_policy:
                self.__proxy_policy.proxies = {
                    "http": "http://localhost:8888",
                    "https": "http://localhost:8888",
                }

            auth_headers = await self._get_auth_headers()
            headers = {**auth_headers, **dict(self.__extra_headers)}

            session = aiohttp.ClientSession()
            try:
                connection_obj = await session.ws_connect(str(url), headers=headers, **self.__connection_options)
                self.__connection = VoiceLiveConnection(session, connection_obj)
                return self.__connection
            except aiohttp.ClientError as e:
                await session.close()
                raise ConnectionError(f"Failed to establish WebSocket connection: {e}") from e
        except (aiohttp.ClientError, ValueError) as e:
            raise ConnectionError(f"Failed to establish WebSocket connection: {e}") from e

    async def _get_auth_headers(self) -> dict[str, str]:
        """
        Get authentication headers for WebSocket connection.

        :return: A dict of HTTP headers for authentication.
        :rtype: dict[str, str]
        """
        if isinstance(self._credential, AzureKeyCredential):
            return {"api-key": self._credential.key}

        if isinstance(self._credential, AsyncTokenCredential):
            token = await self._credential.get_token(*self.__credential_scopes)
        else:  # sync TokenCredential
            token = self._credential.get_token(*self.__credential_scopes)

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

        params: dict[str, Any] = {"api-version": self.__api_version}
        if self.__model is not None:
            params["model"] = self.__model
        params.update(dict(self.__extra_query))

        existing_params = parse_qs(parsed.query)
        for key, value_list in existing_params.items():
            if key not in params:
                params[key] = value_list[0] if value_list else ""

        path = parsed.path.rstrip("/") + "/voice-live/realtime"
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
    credential: Union[AzureKeyCredential, AsyncTokenCredential],
    endpoint: str,
    api_version: str = "2025-10-01",
    model: Optional[str] = None,
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

    :keyword credential: The credential used to authenticate with the service.
    :paramtype type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AsyncTokenCredential
    :keyword endpoint: Service endpoint, e.g., ``https://<region>.api.cognitive.microsoft.com``.
    :paramtype type endpoint: str
    :keyword api_version: The API version to use. Defaults to ``"2025-10-01"``.
    :paramtype type api_version: str
    :keyword model: Model identifier to use for the session.
     In most scenarios, this parameter is required.
     It may be omitted only when connecting through an **Agent** scenario,
     in which case the service will use the model associated with the Agent.
    :paramtype model: str
    :keyword query: Optional query parameters to include in the WebSocket URL.
    :paramtype type query: Mapping[str, Any]
    :keyword headers: Optional HTTP headers to include in the WebSocket handshake.
    :paramtype type headers: Mapping[str, Any]
    :keyword connection_options: Optional advanced WebSocket options compatible with :mod:`aiohttp`.
    :paramtype type connection_options: ~azure.ai.voicelive.aio.WebsocketConnectionOptions
    :return: An async context manager yielding a connected :class:`~azure.ai.voicelive.aio.VoiceLiveConnection`.
    :rtype: collections.abc.AsyncContextManager[~azure.ai.voicelive.aio.VoiceLiveConnection]

    .. note::
        Additional keyword arguments can be passed and will be forwarded to the underlying connection.
    """
    return _VoiceLiveConnectionManager(
        credential=credential,
        endpoint=endpoint,
        api_version=api_version,
        model=model,
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
