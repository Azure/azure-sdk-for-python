# pylint: disable=networking-import-outside-azure-core-transport
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Hand-written sync realtime (WebSocket) streaming client for voice agents.

This is the synchronous counterpart of :mod:`azure.ai.projects.aio._realtime`. See that
module's docstring for the full design rationale; the two modules are kept structurally
identical (sync method names drop the ``async``/``await`` keywords) so fixes/features land in
both at once.

``websockets`` is required for this feature and is *not* a hard dependency of the package; it
is imported lazily so importing the SDK never fails when it is absent.
"""

from __future__ import annotations

import base64
import json
from urllib.parse import urlencode, urlparse
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Type,
    TYPE_CHECKING,
    Union,
    cast,
)

from . import models as _models
from .models._enums import _AgentDefinitionOptInKeys
from .models._patch import _FOUNDRY_FEATURES_HEADER_NAME
from ._utils.model_base import Model as _Model, SdkJSONEncoder

# Scoped to just the voice-agent preview opt-in; callers connecting to other preview agent
# kinds through this same route can pass a broader value explicitly via ``foundry_features``.
_VOICE_AGENT_FEATURE_HEADER: str = _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection
    from azure.core.credentials import TokenCredential

    from ._client import AIProjectClient


__all__ = [
    "Realtime",
    "RealtimeConnection",
    "RealtimeConnectionManager",
    "ClientEvent",
    "ConversationItem",
    "ServerEvent",
]

# Union of the client event models sendable over the connection, plus a raw mapping escape
# hatch for forward compatibility with event types not yet represented in the generated models.
ClientEvent = Union[
    _models.RealtimeClientEventConversationItemCreate,
    _models.RealtimeClientEventConversationItemDelete,
    _models.RealtimeClientEventConversationItemRetrieve,
    _models.RealtimeClientEventConversationItemTruncate,
    _models.RealtimeClientEventInputAudioBufferAppend,
    _models.RealtimeClientEventInputAudioBufferClear,
    _models.RealtimeClientEventInputAudioBufferCommit,
    _models.RealtimeClientEventOutputAudioBufferClear,
    _models.RealtimeClientEventResponseCancel,
    _models.RealtimeClientEventResponseCreate,
    _models.VoiceAgentClientEventSessionAvatarConnect,
    _models.VoiceAgentClientEventSessionUpdate,
    str,
    Mapping[str, Any],
]

# The conversation item variants accepted by ``conversation.item.create``.
ConversationItem = Union[
    _models.RealtimeConversationItemMessageSystem,
    _models.RealtimeConversationItemMessageUser,
    _models.RealtimeConversationItemMessageAssistant,
    _models.RealtimeConversationItemFunctionCall,
    _models.RealtimeConversationItemFunctionCallOutput,
    _models.RealtimeMCPApprovalResponse,
    Mapping[str, Any],
]

# Every server event ``type`` string mapped to its generated model, used to deserialize
# inbound frames into strongly-typed objects. Event types not represented by a dedicated
# generated model in this package (for example ``conversation.created``) are intentionally
# left out here and fall back to a plain ``dict``, as do any newly-added service events.
_SERVER_EVENT_TYPES: Dict[str, Type[_Model]] = {
    "conversation.item.added": _models.RealtimeServerEventConversationItemAdded,
    "conversation.item.created": _models.RealtimeServerEventConversationItemCreated,
    "conversation.item.deleted": _models.RealtimeServerEventConversationItemDeleted,
    "conversation.item.done": _models.RealtimeServerEventConversationItemDone,
    "conversation.item.input_audio_transcription.completed": (
        _models.RealtimeServerEventConversationItemInputAudioTranscriptionCompleted
    ),
    "conversation.item.input_audio_transcription.delta": (
        _models.RealtimeServerEventConversationItemInputAudioTranscriptionDelta
    ),
    "conversation.item.input_audio_transcription.failed": (
        _models.RealtimeServerEventConversationItemInputAudioTranscriptionFailed
    ),
    "conversation.item.input_audio_transcription.segment": (
        _models.RealtimeServerEventConversationItemInputAudioTranscriptionSegment
    ),
    "conversation.item.retrieved": _models.RealtimeServerEventConversationItemRetrieved,
    "conversation.item.truncated": _models.RealtimeServerEventConversationItemTruncated,
    # Shared OpenAI-style Realtime error event (not voice-agent specific in this package).
    "error": _models.RealtimeServerEventError,
    "input_audio_buffer.cleared": _models.RealtimeServerEventInputAudioBufferCleared,
    "input_audio_buffer.committed": _models.RealtimeServerEventInputAudioBufferCommitted,
    "input_audio_buffer.speech_started": _models.RealtimeServerEventInputAudioBufferSpeechStarted,
    "input_audio_buffer.speech_stopped": _models.RealtimeServerEventInputAudioBufferSpeechStopped,
    "input_audio_buffer.timeout_triggered": (_models.RealtimeServerEventInputAudioBufferTimeoutTriggered),
    "mcp_list_tools.completed": _models.RealtimeServerEventMCPListToolsCompleted,
    "mcp_list_tools.failed": _models.RealtimeServerEventMCPListToolsFailed,
    "mcp_list_tools.in_progress": _models.RealtimeServerEventMCPListToolsInProgress,
    "output_audio_buffer.cleared": _models.RealtimeServerEventOutputAudioBufferCleared,
    "rate_limits.updated": _models.RealtimeServerEventRateLimitsUpdated,
    "response.animation_blendshapes.delta": (_models.VoiceAgentServerEventResponseAnimationBlendshapesDelta),
    "response.animation_blendshapes.done": (_models.VoiceAgentServerEventResponseAnimationBlendshapesDone),
    "response.animation_viseme.delta": _models.VoiceAgentServerEventResponseAnimationVisemeDelta,
    "response.animation_viseme.done": _models.VoiceAgentServerEventResponseAnimationVisemeDone,
    "response.audio_timestamp.delta": _models.VoiceAgentServerEventResponseAudioTimestampDelta,
    "response.audio_timestamp.done": _models.VoiceAgentServerEventResponseAudioTimestampDone,
    "response.content_part.added": _models.RealtimeServerEventResponseContentPartAdded,
    "response.content_part.done": _models.RealtimeServerEventResponseContentPartDone,
    "response.created": _models.RealtimeServerEventResponseCreated,
    "response.done": _models.RealtimeServerEventResponseDone,
    "response.function_call_arguments.delta": (_models.RealtimeServerEventResponseFunctionCallArgumentsDelta),
    "response.function_call_arguments.done": (_models.RealtimeServerEventResponseFunctionCallArgumentsDone),
    "response.mcp_call.completed": _models.RealtimeServerEventResponseMCPCallCompleted,
    "response.mcp_call.failed": _models.RealtimeServerEventResponseMCPCallFailed,
    "response.mcp_call.in_progress": _models.RealtimeServerEventResponseMCPCallInProgress,
    "response.mcp_call_arguments.delta": _models.RealtimeServerEventResponseMCPCallArgumentsDelta,
    "response.mcp_call_arguments.done": _models.RealtimeServerEventResponseMCPCallArgumentsDone,
    "response.output_audio.delta": _models.RealtimeServerEventResponseAudioDelta,
    "response.output_audio.done": _models.RealtimeServerEventResponseAudioDone,
    "response.output_audio_transcript.delta": (_models.RealtimeServerEventResponseAudioTranscriptDelta),
    "response.output_audio_transcript.done": (_models.RealtimeServerEventResponseAudioTranscriptDone),
    "response.output_item.added": _models.RealtimeServerEventResponseOutputItemAdded,
    "response.output_item.done": _models.RealtimeServerEventResponseOutputItemDone,
    "response.output_text.delta": _models.RealtimeServerEventResponseTextDelta,
    "response.output_text.done": _models.RealtimeServerEventResponseTextDone,
    "response.video.delta": _models.VoiceAgentServerEventResponseVideoDelta,
    "session.avatar.connecting": _models.VoiceAgentServerEventSessionAvatarConnecting,
    "session.avatar.switch_to_idle": _models.VoiceAgentServerEventSessionAvatarSwitchToIdle,
    "session.avatar.switch_to_speaking": _models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking,
    "session.created": _models.RealtimeServerEventSessionCreated,
    "session.updated": _models.RealtimeServerEventSessionUpdated,
    "warning": _models.VoiceAgentServerEventWarning,
}

# Every generated server event model, for consumers that want a precise return type.
ServerEvent = Union[
    _models.RealtimeServerEventError,
    _models.RealtimeServerEventResponseContentPartAdded,
    _models.RealtimeServerEventConversationItemAdded,
    _models.RealtimeServerEventConversationItemCreated,
    _models.RealtimeServerEventConversationItemDeleted,
    _models.RealtimeServerEventConversationItemDone,
    _models.RealtimeServerEventConversationItemInputAudioTranscriptionCompleted,
    _models.RealtimeServerEventConversationItemInputAudioTranscriptionDelta,
    _models.RealtimeServerEventConversationItemInputAudioTranscriptionFailed,
    _models.RealtimeServerEventConversationItemInputAudioTranscriptionSegment,
    _models.RealtimeServerEventConversationItemRetrieved,
    _models.RealtimeServerEventConversationItemTruncated,
    _models.RealtimeServerEventInputAudioBufferCleared,
    _models.RealtimeServerEventInputAudioBufferCommitted,
    _models.RealtimeServerEventInputAudioBufferSpeechStarted,
    _models.RealtimeServerEventInputAudioBufferSpeechStopped,
    _models.RealtimeServerEventInputAudioBufferTimeoutTriggered,
    _models.RealtimeServerEventMCPListToolsCompleted,
    _models.RealtimeServerEventMCPListToolsFailed,
    _models.RealtimeServerEventMCPListToolsInProgress,
    _models.RealtimeServerEventOutputAudioBufferCleared,
    _models.RealtimeServerEventRateLimitsUpdated,
    _models.VoiceAgentServerEventResponseAnimationBlendshapesDelta,
    _models.VoiceAgentServerEventResponseAnimationBlendshapesDone,
    _models.VoiceAgentServerEventResponseAnimationVisemeDelta,
    _models.VoiceAgentServerEventResponseAnimationVisemeDone,
    _models.RealtimeServerEventResponseAudioDelta,
    _models.RealtimeServerEventResponseAudioDone,
    _models.VoiceAgentServerEventResponseAudioTimestampDelta,
    _models.VoiceAgentServerEventResponseAudioTimestampDone,
    _models.RealtimeServerEventResponseAudioTranscriptDelta,
    _models.RealtimeServerEventResponseAudioTranscriptDone,
    _models.RealtimeServerEventResponseContentPartDone,
    _models.RealtimeServerEventResponseCreated,
    _models.RealtimeServerEventResponseDone,
    _models.RealtimeServerEventResponseFunctionCallArgumentsDelta,
    _models.RealtimeServerEventResponseFunctionCallArgumentsDone,
    _models.RealtimeServerEventResponseMCPCallArgumentsDelta,
    _models.RealtimeServerEventResponseMCPCallArgumentsDone,
    _models.RealtimeServerEventResponseMCPCallCompleted,
    _models.RealtimeServerEventResponseMCPCallFailed,
    _models.RealtimeServerEventResponseMCPCallInProgress,
    _models.RealtimeServerEventResponseOutputItemAdded,
    _models.RealtimeServerEventResponseOutputItemDone,
    _models.RealtimeServerEventResponseTextDelta,
    _models.RealtimeServerEventResponseTextDone,
    _models.VoiceAgentServerEventResponseVideoDelta,
    _models.VoiceAgentServerEventSessionAvatarConnecting,
    _models.VoiceAgentServerEventSessionAvatarSwitchToIdle,
    _models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking,
    _models.RealtimeServerEventSessionCreated,
    _models.RealtimeServerEventSessionUpdated,
    _models.VoiceAgentServerEventWarning,
    Mapping[str, Any],
]


def _to_ws_url(endpoint: str, agent_name: str) -> str:
    """Build the realtime WebSocket URL from the HTTP project endpoint.

    :param str endpoint: The Foundry project endpoint (``https://.../api/projects/...``).
    :param str agent_name: The name of the voice agent to connect to.
    :return: A ``wss://``/``ws://`` URL targeting the realtime route.
    :rtype: str
    """
    base = endpoint.rstrip("/")
    if base.startswith("https://"):
        base = "wss://" + base[len("https://") :]
    elif base.startswith("http://"):
        base = "ws://" + base[len("http://") :]
    return f"{base}/agents/{agent_name}/endpoint/protocols/voice"


def _assert_trusted_connection_url(connection_url: str, endpoint: str) -> None:
    """Guard against attaching the caller's Entra bearer token to an untrusted host.

    ``connection_url`` is an escape hatch that lets a caller override the computed
    scheme/host/path, but the Authorization header carrying the live credential's
    token must never be sent to a host other than the configured Foundry project
    endpoint: a caller-controlled or compromised URL could otherwise be used to
    exfiltrate the token to an arbitrary host.

    :param str connection_url: The caller-supplied override URL.
    :param str endpoint: The configured, trusted Foundry project endpoint.
    :raises ValueError: If the override URL's host does not match the endpoint's host.
    """
    override_host = (urlparse(connection_url).hostname or "").lower()
    trusted_host = (urlparse(endpoint).hostname or "").lower()
    if not override_host or override_host != trusted_host:
        raise ValueError(
            "The 'connection_url' override must target the same host as the configured Foundry "
            f"project endpoint ('{trusted_host}') to avoid sending the Authorization token to an "
            f"untrusted host; got host '{override_host or connection_url}'."
        )


class _BaseResource:  # pylint: disable=too-few-public-methods
    """Base helper that forwards typed helpers to the parent connection."""

    def __init__(self, connection: "RealtimeConnection") -> None:
        self._connection = connection

    def _send(self, event: ClientEvent) -> None:
        self._connection.send(event)


class SessionResource(_BaseResource):
    """Send ``session.*`` client events."""

    def update(
        self,
        *,
        session: Union["_models.VoiceAgentSessionUpdateConfig", Mapping[str, Any]],
        event_id: Optional[str] = None,
    ) -> None:
        """Update the realtime session configuration.

        :keyword session: The session configuration to apply.
        :paramtype session: ~azure.ai.projects.models.VoiceAgentSessionUpdateConfig or
         Mapping[str, Any]
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            cast(Any, _models.VoiceAgentClientEventSessionUpdate)(
                type=_models.RealtimeClientEventType.SESSION_UPDATE,
                session=session,
                event_id=event_id,
            )
        )

    def avatar_connect(self, *, client_sdp: str, event_id: Optional[str] = None) -> None:
        """Negotiate an avatar media session over WebRTC.

        :keyword str client_sdp: The client's SDP offer for avatar media negotiation.
        :keyword event_id: An optional client-generated event identifier.
        :paramtype event_id: str or None
        """
        self._send(
            _models.VoiceAgentClientEventSessionAvatarConnect(
                client_sdp=client_sdp,
                event_id=event_id,
            )
        )


class InputAudioBufferResource(_BaseResource):
    """Send ``input_audio_buffer.*`` client events."""

    def append(self, *, audio: Union[str, bytes], event_id: Optional[str] = None) -> None:
        """Append audio bytes to the input buffer.

        :keyword audio: Raw audio bytes, or an already base64-encoded string.
        :paramtype audio: str or bytes
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        if isinstance(audio, (bytes, bytearray)):
            audio = base64.b64encode(bytes(audio)).decode("ascii")
        self._send(
            _models.RealtimeClientEventInputAudioBufferAppend(
                audio=audio,
                event_id=event_id,
            )
        )

    def commit(self, *, event_id: Optional[str] = None) -> None:
        """Commit the buffered input audio as a user turn.

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(_models.RealtimeClientEventInputAudioBufferCommit(event_id=event_id))

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Discard any buffered input audio.

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(_models.RealtimeClientEventInputAudioBufferClear(event_id=event_id))


class OutputAudioBufferResource(_BaseResource):  # pylint: disable=too-few-public-methods
    """Send ``output_audio_buffer.*`` client events."""

    def clear(self, *, event_id: Optional[str] = None) -> None:
        """Stop and clear any audio the service is currently playing back (barge-in).

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(_models.RealtimeClientEventOutputAudioBufferClear(event_id=event_id))


class ConversationItemResource(_BaseResource):
    """Send ``conversation.item.*`` client events."""

    def create(
        self,
        *,
        item: ConversationItem,
        previous_item_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> None:
        """Insert an item into the conversation.

        :keyword item: The conversation item to create.
        :paramtype item: ~azure.ai.projects.models.RealtimeConversationItemMessageSystem or
         ~azure.ai.projects.models.RealtimeConversationItemMessageUser or
         ~azure.ai.projects.models.RealtimeConversationItemMessageAssistant or
         ~azure.ai.projects.models.RealtimeConversationItemFunctionCall or
         ~azure.ai.projects.models.RealtimeConversationItemFunctionCallOutput or
         ~azure.ai.projects.models.RealtimeMCPApprovalResponse or Mapping[str, Any]
        :keyword previous_item_id: The ID of the preceding item after which the new item will be
         inserted. Default value is None.
        :paramtype previous_item_id: str or None
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            cast(Any, _models.RealtimeClientEventConversationItemCreate)(
                item=item,
                previous_item_id=previous_item_id,
                event_id=event_id,
            )
        )

    def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete an item from the conversation.

        :keyword str item_id: The ID of the item to delete.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            _models.RealtimeClientEventConversationItemDelete(
                item_id=item_id,
                event_id=event_id,
            )
        )

    def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Ask the server to emit a ``conversation.item.retrieved`` event for an item.

        :keyword str item_id: The ID of the item to retrieve.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            _models.RealtimeClientEventConversationItemRetrieve(
                item_id=item_id,
                event_id=event_id,
            )
        )

    def truncate(self, *, item_id: str, content_index: int, audio_end_ms: int, event_id: Optional[str] = None) -> None:
        """Truncate a previously produced assistant audio item (used for barge-in).

        :keyword str item_id: The ID of the assistant message item to truncate.
        :keyword int content_index: The index of the content part to truncate. Use ``0``.
        :keyword int audio_end_ms: The point, in milliseconds, to truncate the audio to.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            _models.RealtimeClientEventConversationItemTruncate(
                item_id=item_id,
                content_index=content_index,
                audio_end_ms=audio_end_ms,
                event_id=event_id,
            )
        )


class ConversationResource(_BaseResource):  # pylint: disable=too-few-public-methods
    """Send ``conversation.*`` client events."""

    def __init__(self, connection: "RealtimeConnection") -> None:
        super().__init__(connection)
        self.item: ConversationItemResource = ConversationItemResource(connection)


class ResponseResource(_BaseResource):
    """Send ``response.*`` client events."""

    def create(
        self,
        *,
        response: Optional[Union["_models.VoiceAgentResponseCreateParams", Mapping[str, Any]]] = None,
        event_id: Optional[str] = None,
    ) -> None:
        """Ask the model to generate a response.

        :keyword response: Optional per-response overrides. Default value is None.
        :paramtype response: ~azure.ai.projects.models.VoiceAgentResponseCreateParams or
         Mapping[str, Any] or None
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            cast(Any, _models.RealtimeClientEventResponseCreate)(
                response=response,
                event_id=event_id,
            )
        )

    def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
        """Cancel an in-progress response.

        :keyword response_id: The ID of the response to cancel, if targeting a specific one.
         Default value is None.
        :paramtype response_id: str or None
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        self._send(
            _models.RealtimeClientEventResponseCancel(
                response_id=response_id,
                event_id=event_id,
            )
        )


class RealtimeConnection:  # pylint: disable=too-many-instance-attributes
    """An open realtime WebSocket connection to a voice agent.

    Iterate over the connection to receive strongly-typed server events, and use the
    sub-namespaces to send strongly-typed client events::

        with client.realtime.connect(agent_name="my-agent") as conn:
            conn.input_audio_buffer.append(audio=chunk)
            conn.input_audio_buffer.commit()
            conn.response.create()
            for event in conn:
                if event.type == RealtimeServerEventType.RESPONSE_DONE:
                    break
    """

    def __init__(self, connection: "ClientConnection") -> None:
        self._connection = connection
        self._closed = False
        self.session: SessionResource = SessionResource(self)
        self.input_audio_buffer: InputAudioBufferResource = InputAudioBufferResource(self)
        self.output_audio_buffer: OutputAudioBufferResource = OutputAudioBufferResource(self)
        self.conversation: ConversationResource = ConversationResource(self)
        self.response: ResponseResource = ResponseResource(self)

    def __enter__(self) -> "RealtimeConnection":
        return self

    def __exit__(self, *exc_details: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "closed" if self.closed else "open"
        return f"<RealtimeConnection [{state}]>"

    @property
    def closed(self) -> bool:
        """Whether the underlying WebSocket connection has been closed.

        :rtype: bool
        """
        return self._closed

    def __iter__(self) -> Iterator[ServerEvent]:
        return self._iter()

    def _iter(self) -> Iterator[ServerEvent]:
        while True:
            try:
                yield self.recv()
            except ConnectionResetError:
                return

    def recv(self, *, timeout: Optional[float] = None) -> ServerEvent:
        """Receive and parse the next server event.

        Known event types are returned as their strongly-typed
        ``VoiceAgentServerEventXxx`` model. Event types not (yet) represented by a
        generated model are returned as a plain ``dict`` for forward compatibility.

        :keyword timeout: Maximum time in seconds to wait for the next event. If ``None``
         (the default), block until an event is received. If no event arrives within
         ``timeout`` seconds, raise :exc:`TimeoutError`.
        :paramtype timeout: float or None
        :return: The parsed server event.
        :rtype: ~azure.ai.projects.ServerEvent
        :raises ConnectionResetError: If the connection was closed by the server.
        :raises TimeoutError: If ``timeout`` elapses before an event is received.
        """
        from websockets.exceptions import ConnectionClosed  # pylint: disable=import-outside-toplevel

        try:
            raw = self._connection.recv(timeout=timeout)
        except ConnectionClosed as exc:
            self._closed = True
            raise ConnectionResetError("The realtime connection was closed.") from exc
        data = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
        payload: Dict[str, Any] = json.loads(data)
        event_type = payload.get("type")
        if not isinstance(event_type, str):
            return payload
        event_cls = _SERVER_EVENT_TYPES.get(event_type)
        if event_cls is None:
            return payload
        return event_cls(payload)

    def send(self, event: ClientEvent) -> None:
        """Send a client event over the connection.

        :param event: A strongly-typed client event, a ready-made mapping, or a raw JSON string.
        :type event: ~azure.ai.projects.ClientEvent or str
        :raises ValueError: If ``event`` is a ``str`` that is not valid JSON.
        """
        if isinstance(event, str):
            try:
                json.loads(event)
            except ValueError as exc:
                raise ValueError(f"'event' is not valid JSON: {exc}") from exc
            payload = event
        else:
            payload = json.dumps(event, cls=SdkJSONEncoder)
        self._connection.send(payload)

    def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the connection.

        :keyword int code: The WebSocket close code.
        :keyword str reason: The close reason.
        """
        if self._closed:
            return
        try:
            self._connection.close(code=code, reason=reason)
        finally:
            self._closed = True


class RealtimeConnectionManager:  # pylint: disable=too-many-instance-attributes
    """Context manager that opens a :class:`RealtimeConnection`.

    Returned by :meth:`Realtime.connect`; you normally use it as
    ``with client.realtime.connect(...) as conn:``.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        endpoint: str,
        credential: "TokenCredential",
        credential_scopes: List[str],
        api_version: str,
        agent_name: str,
        foundry_features: str,
        agent_session_id: Optional[str] = None,
        agent_version_override: Optional[str] = None,
        structured_inputs: Optional[str] = None,
        connection_url: Optional[str] = None,
        extra_query: Optional[Mapping[str, str]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        self._endpoint = endpoint
        self._credential = credential
        self._credential_scopes = credential_scopes
        self._api_version = api_version
        self._agent_name = agent_name
        self._foundry_features = foundry_features
        self._agent_session_id = agent_session_id
        self._agent_version_override = agent_version_override
        self._structured_inputs = structured_inputs
        self._connection_url = connection_url
        self._extra_query = dict(extra_query or {})
        self._extra_headers = dict(extra_headers or {})
        self._kwargs = kwargs
        self._connection: Optional[RealtimeConnection] = None

    def __enter__(self) -> RealtimeConnection:
        return self.enter()

    def enter(self) -> RealtimeConnection:  # pylint: disable=too-many-locals
        """Open the connection.

        :return: The live realtime connection.
        :rtype: ~azure.ai.projects.RealtimeConnection
        :raises RuntimeError: If ``websockets`` is not installed.
        :raises ValueError: If the computed or supplied WebSocket URL does not use ``wss://``.
        :raises ConnectionError: If the WebSocket upgrade handshake fails (for example, a
         network error, DNS failure, or a non-101 response from the service).
        """
        try:
            from websockets.sync.client import connect as _ws_connect  # pylint: disable=import-outside-toplevel
            from websockets.typing import Subprotocol  # pylint: disable=import-outside-toplevel
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "The realtime client requires `websockets`. Install it with `pip install websockets`."
            ) from exc

        # ``connection_url`` fully overrides the computed route (scheme/host/path). This is the
        # escape hatch used to reach a specific data-plane host/path directly.
        if self._connection_url is not None:
            _assert_trusted_connection_url(self._connection_url, self._endpoint)
        url = self._connection_url or _to_ws_url(self._endpoint, self._agent_name)
        if not url.startswith("wss://"):
            raise ValueError("The realtime WebSocket URL must use wss:// to protect credentials in transit.")

        params: Dict[str, str] = {"api-version": self._api_version}
        if self._agent_session_id is not None:
            params["agent_session_id"] = self._agent_session_id
        if self._agent_version_override is not None:
            params["x-agent-version-override"] = self._agent_version_override
        params.update(self._extra_query)

        if params:
            # Preserve an existing query string on a `connection_url` override (for example a
            # SAS-style `?sig=...`) instead of unconditionally appending a second `?`.
            delimiter = "&" if urlparse(url).query else "?"
            full_url = f"{url}{delimiter}{urlencode(params)}"
        else:
            full_url = url

        token = self._credential.get_token(*self._credential_scopes)
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {token.token}",
            _FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features,
        }
        if self._structured_inputs is not None:
            headers["x-ms-voice-structured-inputs"] = self._structured_inputs
        headers.update(self._extra_headers)

        try:
            connection = _ws_connect(
                full_url,
                additional_headers=headers,
                subprotocols=[Subprotocol("realtime")],
                **self._kwargs,
            )
        except BaseException as exc:
            if not isinstance(exc, Exception) or isinstance(exc, (ValueError, RuntimeError)):
                raise
            raise ConnectionError(
                f"Failed to open the realtime WebSocket connection to voice agent "
                f"'{self._agent_name}' at '{url}': {exc}"
            ) from exc
        self._connection = RealtimeConnection(connection)
        return self._connection

    def __exit__(self, *exc_details: Any) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None


class Realtime:  # pylint: disable=too-few-public-methods
    """Realtime streaming entry point, exposed as ``client.realtime``.

    Follows the OpenAI Python realtime surface: obtain it from the HTTP client and open a
    connection with :meth:`connect`::

        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential

        client = AIProjectClient(endpoint, DefaultAzureCredential())
        with client.realtime.connect(agent_name="my-agent") as conn:
            conn.input_audio_buffer.append(audio=chunk)
            conn.input_audio_buffer.commit()
            conn.response.create()
            for event in conn:
                if event.type == RealtimeServerEventType.RESPONSE_DONE:
                    break

    :param client: The HTTP client whose endpoint and credential are reused for the realtime
     handshake.
    :type client: ~azure.ai.projects.AIProjectClient
    """

    def __init__(self, client: "AIProjectClient") -> None:
        self._config = client._config  # pylint: disable=protected-access

    def connect(  # pylint: disable=too-many-arguments
        self,
        *,
        agent_name: str,
        foundry_features: str = _VOICE_AGENT_FEATURE_HEADER,
        agent_session_id: Optional[str] = None,
        agent_version_override: Optional[str] = None,
        structured_inputs: Optional[str] = None,
        connection_url: Optional[str] = None,
        api_version: Optional[str] = None,
        credential_scopes: Optional[List[str]] = None,
        extra_query: Optional[Mapping[str, str]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> RealtimeConnectionManager:
        """Open a realtime WebSocket connection to a voice agent.

        :keyword str agent_name: The name of the voice agent to connect to.
        :keyword foundry_features: Preview opt-in value(s) for the ``Foundry-Features`` header.
         Defaults to ``VoiceAgents=V1Preview``. Pass a comma-separated value to opt in to
         additional preview features on the same request.
        :paramtype foundry_features: str
        :keyword agent_session_id: An optional identifier used to correlate the voice session.
         Default value is None.
        :paramtype agent_session_id: str or None
        :keyword agent_version_override: Selects a specific version of the voice agent for this
         session. Default value is None.
        :paramtype agent_version_override: str or None
        :keyword structured_inputs: A JSON object that maps structured-input names to their
         values for this session. Default value is None.
        :paramtype structured_inputs: str or None
        :keyword connection_url: Full ``wss://``/``ws://`` URL that overrides the route computed
         from the client endpoint. Query parameters are still appended. Default value is None.
        :paramtype connection_url: str or None
        :keyword api_version: Overrides the client's API version for the handshake. Default
         value is None.
        :paramtype api_version: str or None
        :keyword credential_scopes: Overrides the client's token scopes for the handshake.
         Default value is None.
        :paramtype credential_scopes: list[str] or None
        :keyword extra_query: Additional query-string parameters for the handshake.
        :paramtype extra_query: Mapping[str, str] or None
        :keyword extra_headers: Additional headers for the handshake.
        :paramtype extra_headers: Mapping[str, str] or None
        :return: A context manager yielding a :class:`RealtimeConnection`.
        :rtype: ~azure.ai.projects.RealtimeConnectionManager
        """
        return RealtimeConnectionManager(
            endpoint=self._config.endpoint,
            credential=self._config.credential,
            credential_scopes=credential_scopes or self._config.credential_scopes,
            api_version=api_version or self._config.api_version,
            agent_name=agent_name,
            foundry_features=foundry_features,
            agent_session_id=agent_session_id,
            agent_version_override=agent_version_override,
            structured_inputs=structured_inputs,
            connection_url=connection_url,
            extra_query=extra_query,
            extra_headers=extra_headers,
            **kwargs,
        )
