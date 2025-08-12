# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import logging
from contextlib import AbstractContextManager
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union, Mapping
from typing_extensions import TypedDict
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

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
from azure.core.exceptions import AzureError

from .models import ClientEvent, RequestSession, ServerEvent
try:  # Python 3.11+
    from typing import NotRequired, Required  # type: ignore[attr-defined]
except Exception:  # Python <=3.10
    from typing_extensions import NotRequired, Required

__all__: List[str] = [
    "connect",
    "WebsocketConnectionOptions",
    "ConnectionError",
    "ConnectionClosed",
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
        """Fallback JSON serializer for generated SDK models."""
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

class WebsocketConnectionOptions(TypedDict, total=False):
    """
    Advanced WebSocket connection options for the synchronous VoiceLive API.

    These options are passed directly to :func:`websockets.sync.client.connect`
    and control low-level WebSocket behavior.  
    All keys are optional — if omitted, the `websockets` library's defaults apply.  
    Unsupported or unknown keys are ignored.

    :keyword extensions: WebSocket extensions to negotiate with the server.
        Usually provided by the library; override with caution.
    :type extensions: Sequence[Any]

    :keyword subprotocols: A list of subprotocols to negotiate during the
        WebSocket handshake.
    :type subprotocols: Sequence[str]

    :keyword compression: Name of the compression method to use, or a
        compression configuration object.
        Set to ``None`` or an empty string to disable compression.
    :type compression: str

    :keyword max_size: Maximum size in bytes for incoming messages.
        Messages larger than this will close the connection with a
        `PayloadTooBig` exception.
    :type max_size: int

    :keyword max_queue: Maximum number of incoming messages to queue before
        processing. Can be:
        - An integer limit.
        - A tuple of ``(high_watermark, low_watermark)`` integers or None.
    :type max_queue: int or tuple[int | None, int | None]

    :keyword write_limit: TCP write buffer limit. Can be:
        - A single integer limit.
        - A tuple of ``(limit, interval)`` where ``interval`` is optional.
    :type write_limit: int or tuple[int, int | None]
    """

    extensions: NotRequired[Sequence[Any]]
    subprotocols: NotRequired[Sequence[str]]
    compression: NotRequired[str]
    max_size: NotRequired[int]
    max_queue: NotRequired[Union[int, Tuple[Optional[int], Optional[int]]]]
    write_limit: NotRequired[Union[int, Tuple[int, Optional[int]]]]


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
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def update(self, *, session: Mapping[str, Any] | RequestSession, event_id: Optional[str] = None) -> None:
        """Update the session configuration.

        :param session: Session configuration parameters.
        :type session: Mapping[str, Any] or ~azure.ai.voicelive.models.RequestSession
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        if isinstance(session, RequestSession):
            payload = session.as_dict()
        else:
            payload = dict(session)

        event = ClientEventSessionUpdate(session=payload)
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class ResponseResource:
    """Resource for response management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a response resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def create(self, *, response: Optional[Mapping[str, Any]] = None, event_id: Optional[str] = None) -> None:
        """Create a response from the model.

        Triggers model inference. In Server VAD mode, the server may create
        responses automatically.

        :param response: Optional response configuration.
        :type response: Mapping[str, Any] or None
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventResponseCreate()
        if response:
            event["response"] = dict(response)
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
        """Cancel an in-progress response.

        :param response_id: Optional ID of the response to cancel.
        :type response_id: str
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventResponseCancel()
        if response_id:
            event["response_id"] = response_id
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class InputAudioBufferResource:
    """Resource for input audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an input audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def append(self, *, audio: str, event_id: Optional[str] = None) -> None:
        """Append audio to the input buffer.

        :param audio: Base64-encoded audio data. Must match the session's ``input_audio_format``.
        :type audio: str
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventInputAudioBufferAppend(audio=audio)
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def commit(self, *, event_id: Optional[str] = None) -> None:
        """Commit the input audio buffer to create a user message item.

        In Server VAD mode, the server commits automatically.

        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventInputAudioBufferCommit()
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the input audio buffer.

        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventInputAudioBufferClear()
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class OutputAudioBufferResource:
    """Resource for output audio buffer management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize an output audio buffer resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Clear the output audio buffer and stop generation.

        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event: Dict[str, Any] = {"type": "output_audio_buffer.clear"}
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class ConversationItemResource:
    """Resource for conversation item management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation item resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def create(
        self, *, item: Mapping[str, Any], previous_item_id: Optional[str] = None, event_id: Optional[str] = None
    ) -> None:
        """Create a new conversation item.

        :param item: The item to create (message, function call, etc.).
        :type item: Mapping[str, Any]
        :param previous_item_id: Insert after this item, if provided.
        :type previous_item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventConversationItemCreate(item=dict(item))
        if previous_item_id:
            event["previous_item_id"] = previous_item_id
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete a conversation item.

        :param item_id: ID of the item to delete.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventConversationItemDelete(item_id=item_id)
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Retrieve a conversation item.

        :param item_id: ID of the item to retrieve.
        :type item_id: str
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventConversationItemRetrieve(item_id=item_id)
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)

    def truncate(self, *, item_id: str, audio_end_ms: int, content_index: int, event_id: Optional[str] = None) -> None:
        """Truncate a prior assistant item's audio (e.g., on user interruption).

        :param item_id: ID of the item to truncate.
        :type item_id: str
        :param audio_end_ms: Millisecond offset to cut at.
        :type audio_end_ms: int
        :param content_index: Content index within the item.
        :type content_index: int
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event = ClientEventConversationItemTruncate(
            item_id=item_id, audio_end_ms=audio_end_ms, content_index=content_index
        )
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class ConversationResource:
    """Resource for conversation management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a conversation resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection
        self.item = ConversationItemResource(connection)


class TranscriptionSessionResource:
    """Resource for transcription session management."""

    def __init__(self, connection: "VoiceLiveConnection") -> None:
        """Initialize a transcription session resource.

        :param connection: The VoiceLiveConnection to use.
        :type connection: ~azure.ai.voicelive.VoiceLiveConnection
        """
        self._connection = connection

    def update(self, *, session: Mapping[str, Any], event_id: Optional[str] = None) -> None:
        """Update the transcription session.

        :param session: Transcription session configuration.
        :type session: Mapping[str, Any]
        :param event_id: Optional ID for the event.
        :type event_id: str
        """
        event: Dict[str, Any] = {"type": "transcription_session.update", "session": dict(session)}
        if event_id:
            event["event_id"] = event_id
        self._connection.send(event)


class VoiceLiveConnection:
    """
    Represents a live WebSocket connection to the Azure Voice Live API.

    This class exposes resource helpers:

    - :attr:`session` – manage session configuration updates.
    - :attr:`response` – create or cancel model responses.
    - :attr:`input_audio_buffer` – append/commit/clear captured audio.
    - :attr:`output_audio_buffer` – clear generated audio output.
    - :attr:`conversation` – manage conversation items.
    - :attr:`transcription_session` – update transcription configuration.

    Instances are yielded by :func:`~azure.ai.voicelive.connect`.

    :ivar session: Resource for managing session configuration and updates.
    :vartype session: ~azure.ai.voicelive.SessionResource
    :ivar response: Resource for creating and cancelling model responses.
    :vartype response: ~azure.ai.voicelive.ResponseResource
    :ivar input_audio_buffer: Resource for appending, committing, and clearing input audio.
    :vartype input_audio_buffer: ~azure.ai.voicelive.InputAudioBufferResource
    :ivar output_audio_buffer: Resource for clearing generated audio output.
    :vartype output_audio_buffer: ~azure.ai.voicelive.OutputAudioBufferResource
    :ivar conversation: Resource for managing the conversation and its items.
    :vartype conversation: ~azure.ai.voicelive.ConversationResource
    :ivar transcription_session: Resource for updating transcription session parameters.
    :vartype transcription_session: ~azure.ai.voicelive.TranscriptionSessionResource
    """

    def __init__(self, connection) -> None:
        """Initialize a VoiceLiveConnection.

        :param connection: The underlying WebSocket connection.
        """
        self._connection = connection

        self.session = SessionResource(self)
        self.response = ResponseResource(self)
        self.input_audio_buffer = InputAudioBufferResource(self)
        self.conversation = ConversationResource(self)
        self.output_audio_buffer = OutputAudioBufferResource(self)
        self.transcription_session = TranscriptionSessionResource(self)

    def __iter__(self) -> Iterator[ServerEvent]:
        """Yield typed events until the connection is closed.

        :return: An iterator of :class:`~azure.ai.voicelive.models.ServerEvent`.
        :rtype: collections.abc.Iterator[~azure.ai.voicelive.models.ServerEvent]
        """
        try:
            while True:
                yield self.recv()
        except Exception as e:
            log.debug(f"Connection closed: {e}")
            return

    def recv(self) -> ServerEvent:
        """Receive and parse the next message as a typed event.

        :return: A parsed server event.
        :rtype: ~azure.ai.voicelive.models.ServerEvent
        :raises ConnectionError: If the connection is closed or the message cannot be parsed.
        """
        try:
            return ServerEvent.deserialize(self.recv_bytes())
        except Exception as e:
            log.error(f"Error parsing message: {e}")
            raise ConnectionError(f"Failed to parse message: {e}") from e

    def recv_bytes(self) -> bytes:
        """Receive raw bytes from the connection.

        :return: The raw message bytes.
        :rtype: bytes
        :raises ConnectionClosed: If the connection is closed.
        """
        try:
            message = self._connection.recv(decode=False)  # websockets.sync: return bytes if decode=False
            log.debug("Received websocket message: %s", message)
            return message
        except Exception as e:
            code = getattr(e, "code", 1006)  # 1006 = Abnormal Closure
            reason = str(e)
            raise ConnectionClosed(code, reason) from e

    def send(self, event: Union[Mapping[str, Any], ClientEvent]) -> None:
        """
        Send an event to the server over the active WebSocket connection.

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
            # Prefer model-provided serialization if available
            if callable(getattr(event, "serialize", None)):
                data = event.serialize()  # instance serializer
            elif callable(getattr(event.__class__, "serialize", None)):
                data = event.__class__.serialize(event)  # class/static serializer
            elif isinstance(event, Mapping):
                data = json.dumps(dict(event), default=_json_default)
            else:
                data = json.dumps(event, default=_json_default)
            self._connection.send(data)
        except Exception as e:
            log.error(f"Failed to send event: {e}")
            raise ConnectionError(f"Failed to send event: {e}") from e

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the WebSocket connection.

        Gracefully terminates the connection to the Voice Live service and
        releases the underlying socket resources.

        :param code: WebSocket close code to send to the server. Defaults to ``1000`` (Normal Closure).
        :type code: int
        :param reason: Optional reason string to include in the close frame.
        :type reason: str
        """
        try:
            # websockets.sync expects `close(code=..., reason=...)`
            self._connection.close(code=code, reason=reason)
        except Exception as e:
            log.warning(f"Error closing connection: {e}")


class _VoiceLiveConnectionManager(AbstractContextManager["VoiceLiveConnection"]):
    """Context manager for Voice Live WebSocket connections (internal)."""

    def __init__(
        self,
        *,
        credential: Union[AzureKeyCredential, TokenCredential],
        endpoint: str,
        model: str,
        api_version: str,
        extra_query: Mapping[str, Any],
        extra_headers: Mapping[str, Any],
        connection_options: WebsocketConnectionOptions,
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
        self.__connection_options = connection_options

    def __enter__(self) -> VoiceLiveConnection:
        """Open and return a WebSocket connection."""
        try:
            from websockets.sync.client import connect as ws_connect
            from websockets.exceptions import WebSocketException
        except ImportError as exc:
            raise ImportError("Install `websockets` to use WebSocket functionality: pip install websockets") from exc

        try:
            url = self._prepare_url()
            log.debug("Connecting to %s", url)

            if self.__connection_options:
                log.debug("Connection options: %s", self.__connection_options)

            headers = {**self._get_auth_headers(), **dict(self.__extra_headers)}
            ws = ws_connect(url, additional_headers=headers, **self.__connection_options)
            self.__connection = VoiceLiveConnection(ws)
            return self.__connection
        except WebSocketException as e:
            raise ConnectionError(f"Failed to establish WebSocket connection: {e}") from e

    def __exit__(self, exc_type, exc, exc_tb) -> None:
        """Close the connection when exiting the context."""
        if self.__connection is not None:
            self.__connection.close()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for WebSocket connection."""
        if isinstance(self._credential, AzureKeyCredential):
            return {"api-key": self._credential.key}
        token = self._credential.get_token(self.__credential_scopes)
        return {"Authorization": f"Bearer {token.token}"}

    def _prepare_url(self) -> str:
        """Prepare the WebSocket URL."""
        parsed = urlparse(self._endpoint)
        scheme = "wss" if parsed.scheme == "https" else ("ws" if parsed.scheme == "http" else parsed.scheme)

        params: Dict[str, Any] = {"model": self.__model, "api-version": self.__api_version}
        params.update(dict(self.__extra_query))

        # Merge existing query params without overriding new ones
        existing_params = parse_qs(parsed.query)
        for key, value_list in existing_params.items():
            if key not in params:
                params[key] = value_list[0] if value_list else ""

        path = parsed.path.rstrip("/") + "/voice-agent/realtime"
        return urlunparse((scheme, parsed.netloc, path, parsed.params, urlencode(params), parsed.fragment))


def connect(
    *,
    endpoint: str,
    credential: Union[AzureKeyCredential, TokenCredential],
    model: str,
    api_version: str = "2025-05-01-preview",
    query: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, Any]] = None,
    connection_options: WebsocketConnectionOptions = {},
    **kwargs: Any,
) -> AbstractContextManager["VoiceLiveConnection"]:
    """
    Create and manage a synchronous WebSocket connection to the Azure Voice Live API.

    This helper returns a standard context manager that:

    - Authenticates with the service using an API key or Azure Active Directory token.
    - Builds the correct WebSocket URL and query parameters.
    - Establishes the connection and yields a :class:`~azure.ai.voicelive.VoiceLiveConnection`
      for sending and receiving events.
    - Automatically closes the connection on context exit.

    **Supported credentials**

    - :class:`~azure.core.credentials.AzureKeyCredential` (API key).
    - :class:`~azure.core.credentials.TokenCredential` (AAD), e.g., :class:`azure.identity.DefaultAzureCredential`.

    :param endpoint: Service endpoint, e.g., ``https://<region>.api.cognitive.microsoft.com``.
    :type endpoint: str
    :param credential: Credential used to authenticate the WebSocket connection.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :param model: Model identifier to use for the session.
    :type model: str
    :param api_version: API version to use. Defaults to ``"2025-05-01-preview"``.
    :type api_version: str
    :param query: Optional query parameters to include in the WebSocket URL.
    :type query: Mapping[str, Any] or None
    :param headers: Optional headers to include in the WebSocket handshake.
    :type headers: Mapping[str, Any] or None
    :param connection_options: Advanced WebSocket options passed to :func:`websockets.sync.client.connect`.
    :type connection_options: ~azure.ai.voicelive.WebsocketConnectionOptions
    :param kwargs: Additional keyword arguments reserved for future use.
    :type kwargs: Any
    :return: A context manager that yields a connected :class:`~azure.ai.voicelive.VoiceLiveConnection`.
    :rtype: contextlib.AbstractContextManager[~azure.ai.voicelive.VoiceLiveConnection]
    """
    return _VoiceLiveConnectionManager(
        credential=credential,
        endpoint=endpoint,
        model=model,
        api_version=api_version,
        extra_query=query or {},
        extra_headers=headers or {},
        connection_options=connection_options,
        **kwargs,
    )


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """