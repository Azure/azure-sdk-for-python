# pylint: disable=networking-import-outside-azure-core-transport
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Hand-written async realtime (WebSocket) streaming client for voice agents.

Realtime uses a fundamentally different transport (a persistent WebSocket) than the
request/response HTTP surface generated from the service's TypeSpec definition, so it is
hand-written and exposed as the ``AIProjectClient.realtime`` namespace.

The connection ergonomics follow the OpenAI Python realtime client so that developers moving
between the libraries get a familiar surface:

* :meth:`AsyncRealtime.connect` returns an async context manager.
* Entering the context yields an :class:`AsyncRealtimeConnection`.
* The connection is async-iterable over inbound, strongly-typed server events and exposes
  sub-namespaces (``session``, ``input_audio_buffer``, ``output_audio_buffer``,
  ``conversation``, ``response``) for sending strongly-typed outbound client events.

Outbound and inbound events use the generated ``VoiceAgentClientEventXxx``/
``VoiceAgentServerEventXxx`` models directly where one exists. ``send`` and ``recv`` still
accept/return plain ``dict`` objects as a forward-compatible fallback for any event ``type``
the generated models don't yet know about (for example ``conversation.created``, which is a
valid event but does not (yet) have a dedicated generated model in this package).

``aiohttp`` is required for this feature and is *not* a hard dependency of the package; it is
imported lazily so importing the SDK never fails when it is absent.
"""

from __future__ import annotations

import base64
import json
from urllib.parse import urlparse
from typing import (
    Any,
    AsyncIterator,
    cast,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TYPE_CHECKING,
    Union,
)

from .. import models as _models
from ..models._enums import _AgentDefinitionOptInKeys
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _has_header_case_insensitive
from .._utils.model_base import Model as _Model, SdkJSONEncoder
from .._version import VERSION

from azure.core.pipeline.policies import UserAgentPolicy

# Scoped to just the voice-agent preview opt-in; callers connecting to other preview agent
# kinds through this same route can pass a broader value explicitly via ``foundry_features``.
_VOICE_AGENT_FEATURE_HEADER: str = _AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW.value

# Identifies the SDK to the service on the WebSocket handshake, which otherwise falls back to
# the underlying `aiohttp` library's generic default (the generated HTTP surface gets this for
# free from the pipeline's own UserAgentPolicy; this hand-written client builds its own request
# instead, so it needs to opt in explicitly the same way).
_USER_AGENT: str = UserAgentPolicy(sdk_moniker=f"ai-projects/{VERSION}").user_agent

if TYPE_CHECKING:
    from aiohttp import ClientSession, ClientWebSocketResponse
    from azure.core.credentials_async import AsyncTokenCredential

    from ._client import AIProjectClient


__all__ = [
    "AsyncRealtime",
    "AsyncRealtimeConnection",
    "AsyncRealtimeConnectionManager",
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
    _models.VoiceAgentClientEventRtcCallSdpCreate,
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
    "rtc.call.error": _models.VoiceAgentServerEventRtcCallError,
    "rtc.call.sdp.created": _models.VoiceAgentServerEventRtcCallSdpCreated,
    "session.avatar.connecting": _models.VoiceAgentServerEventSessionAvatarConnecting,
    "session.avatar.switch_to_idle": _models.VoiceAgentServerEventSessionAvatarSwitchToIdle,
    "session.avatar.switch_to_speaking": _models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking,
    "session.created": _models.RealtimeServerEventSessionCreated,
    "session.subagent.aborted": _models.VoiceAgentServerEventSessionSubagentAborted,
    "session.subagent.completed": _models.VoiceAgentServerEventSessionSubagentCompleted,
    "session.subagent.started": _models.VoiceAgentServerEventSessionSubagentStarted,
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
    _models.VoiceAgentServerEventRtcCallError,
    _models.VoiceAgentServerEventRtcCallSdpCreated,
    _models.VoiceAgentServerEventSessionAvatarConnecting,
    _models.VoiceAgentServerEventSessionAvatarSwitchToIdle,
    _models.VoiceAgentServerEventSessionAvatarSwitchToSpeaking,
    _models.RealtimeServerEventSessionCreated,
    _models.VoiceAgentServerEventSessionSubagentAborted,
    _models.VoiceAgentServerEventSessionSubagentCompleted,
    _models.VoiceAgentServerEventSessionSubagentStarted,
    _models.RealtimeServerEventSessionUpdated,
    _models.VoiceAgentServerEventWarning,
    Mapping[str, Any],
]


def _to_ws_url(endpoint: str, agent_name: str) -> str:
    """Build the realtime WebSocket URL from the HTTPS project endpoint.

    Only the ``https://`` scheme is translated (to ``wss://``); any other scheme is left
    unchanged so that :meth:`AsyncRealtimeConnectionManager.enter`'s ``wss://``-only check
    rejects it with a clear error instead of silently producing an unencrypted ``ws://`` URL
    that would also send the live Authorization token in plain text.

    :param str endpoint: The Foundry project endpoint (``https://.../api/projects/...``).
    :param str agent_name: The name of the voice agent to connect to.
    :return: A ``wss://`` URL targeting the realtime route.
    :rtype: str
    """
    base = endpoint.rstrip("/")
    if base.startswith("https://"):
        base = "wss://" + base[len("https://") :]
    return f"{base}/agents/{agent_name}/endpoint/protocols/voice"


_DEFAULT_PORT_BY_SCHEME = {"http": 80, "https": 443, "ws": 80, "wss": 443}


def _normalized_authority(url: str) -> Tuple[str, Optional[int]]:
    """Return a ``(hostname, port)`` tuple with the scheme's default port filled in.

    ``urlparse(...).port`` is ``None`` when a URL omits an explicit port, which would make
    ``https://host/...`` and ``https://host:8443/...`` compare as equal on hostname alone.
    Resolving the scheme's default port here lets callers compare authorities (not just
    hostnames) so a same-host override on a different, non-default port is correctly rejected.

    :param str url: The URL to parse.
    :return: A tuple of the lower-cased hostname (or empty string) and the resolved port
     (or ``None`` if the scheme has no known default and none was specified).
    :rtype: tuple[str, Optional[int]]
    """
    parsed = urlparse(url)
    port = parsed.port
    if port is None:
        port = _DEFAULT_PORT_BY_SCHEME.get((parsed.scheme or "").lower())
    return (parsed.hostname or "").lower(), port


def _assert_trusted_connection_url(connection_url: str, endpoint: str) -> None:
    """Guard against attaching the caller's Entra bearer token to an untrusted host.

    ``connection_url`` is an escape hatch that lets a caller override the computed
    scheme/host/path, but the Authorization header carrying the live credential's
    token must never be sent to a host other than the configured Foundry project
    endpoint: a caller-controlled or compromised URL could otherwise be used to
    exfiltrate the token to an arbitrary host or port.

    :param str connection_url: The caller-supplied override URL.
    :param str endpoint: The configured, trusted Foundry project endpoint.
    :raises ValueError: If the override URL's host or port does not match the endpoint's.
    """
    override_host, override_port = _normalized_authority(connection_url)
    trusted_host, trusted_port = _normalized_authority(endpoint)
    if not override_host or (override_host, override_port) != (trusted_host, trusted_port):
        got = override_host or connection_url
        if override_host and override_port:
            got = f"{override_host}:{override_port}"
        raise ValueError(
            "The 'connection_url' override must target the same host and port as the configured "
            f"Foundry project endpoint ('{trusted_host}:{trusted_port}') to avoid sending the "
            f"Authorization token to an untrusted host; got '{got}'."
        )


class _BaseResource:  # pylint: disable=too-few-public-methods
    """Base helper that forwards typed helpers to the parent connection."""

    def __init__(self, connection: "AsyncRealtimeConnection") -> None:
        self._connection = connection

    async def _send(self, event: ClientEvent) -> None:
        await self._connection.send(event)


class SessionResource(_BaseResource):
    """Send ``session.*`` client events."""

    async def update(
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
        await self._send(
            cast(Any, _models.VoiceAgentClientEventSessionUpdate)(
                type=_models.RealtimeClientEventType.SESSION_UPDATE,
                session=session,
                event_id=event_id,
            )
        )

    async def avatar_connect(self, *, client_sdp: str, event_id: Optional[str] = None) -> None:
        """Negotiate an avatar media session over WebRTC.

        :keyword str client_sdp: The client's SDP offer for avatar media negotiation.
        :keyword event_id: An optional client-generated event identifier.
        :paramtype event_id: str or None
        """
        await self._send(
            _models.VoiceAgentClientEventSessionAvatarConnect(
                client_sdp=client_sdp,
                event_id=event_id,
            )
        )


class InputAudioBufferResource(_BaseResource):
    """Send ``input_audio_buffer.*`` client events."""

    async def append(self, *, audio: Union[str, bytes], event_id: Optional[str] = None) -> None:
        """Append audio bytes to the input buffer.

        :keyword audio: Raw audio bytes, or an already base64-encoded string.
        :paramtype audio: str or bytes
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        if isinstance(audio, (bytes, bytearray)):
            audio = base64.b64encode(bytes(audio)).decode("ascii")
        await self._send(
            _models.RealtimeClientEventInputAudioBufferAppend(
                audio=audio,
                event_id=event_id,
            )
        )

    async def commit(self, *, event_id: Optional[str] = None) -> None:
        """Commit the buffered input audio as a user turn.

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(_models.RealtimeClientEventInputAudioBufferCommit(event_id=event_id))

    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Discard any buffered input audio.

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(_models.RealtimeClientEventInputAudioBufferClear(event_id=event_id))


class OutputAudioBufferResource(_BaseResource):  # pylint: disable=too-few-public-methods
    """Send ``output_audio_buffer.*`` client events."""

    async def clear(self, *, event_id: Optional[str] = None) -> None:
        """Stop and clear any audio the service is currently playing back (barge-in).

        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(_models.RealtimeClientEventOutputAudioBufferClear(event_id=event_id))


class ConversationItemResource(_BaseResource):
    """Send ``conversation.item.*`` client events."""

    async def create(
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
        await self._send(
            cast(Any, _models.RealtimeClientEventConversationItemCreate)(
                item=item,
                previous_item_id=previous_item_id,
                event_id=event_id,
            )
        )

    async def delete(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Delete an item from the conversation.

        :keyword str item_id: The ID of the item to delete.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(
            _models.RealtimeClientEventConversationItemDelete(
                item_id=item_id,
                event_id=event_id,
            )
        )

    async def retrieve(self, *, item_id: str, event_id: Optional[str] = None) -> None:
        """Ask the server to emit a ``conversation.item.retrieved`` event for an item.

        :keyword str item_id: The ID of the item to retrieve.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(
            _models.RealtimeClientEventConversationItemRetrieve(
                item_id=item_id,
                event_id=event_id,
            )
        )

    async def truncate(
        self, *, item_id: str, content_index: int, audio_end_ms: int, event_id: Optional[str] = None
    ) -> None:
        """Truncate a previously produced assistant audio item (used for barge-in).

        :keyword str item_id: The ID of the assistant message item to truncate.
        :keyword int content_index: The index of the content part to truncate. Use ``0``.
        :keyword int audio_end_ms: The point, in milliseconds, to truncate the audio to.
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(
            _models.RealtimeClientEventConversationItemTruncate(
                item_id=item_id,
                content_index=content_index,
                audio_end_ms=audio_end_ms,
                event_id=event_id,
            )
        )


class ConversationResource(_BaseResource):  # pylint: disable=too-few-public-methods
    """Send ``conversation.*`` client events."""

    def __init__(self, connection: "AsyncRealtimeConnection") -> None:
        super().__init__(connection)
        self.item: ConversationItemResource = ConversationItemResource(connection)


class ResponseResource(_BaseResource):
    """Send ``response.*`` client events."""

    async def create(
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
        await self._send(
            cast(Any, _models.RealtimeClientEventResponseCreate)(
                response=response,
                event_id=event_id,
            )
        )

    async def cancel(self, *, response_id: Optional[str] = None, event_id: Optional[str] = None) -> None:
        """Cancel an in-progress response.

        :keyword response_id: The ID of the response to cancel, if targeting a specific one.
         Default value is None.
        :paramtype response_id: str or None
        :keyword event_id: Optional client-generated ID used to identify this event.
        :paramtype event_id: str or None
        """
        await self._send(
            _models.RealtimeClientEventResponseCancel(
                response_id=response_id,
                event_id=event_id,
            )
        )


class AsyncRealtimeConnection:  # pylint: disable=too-many-instance-attributes
    """An open realtime WebSocket connection to a voice agent.

    Iterate over the connection to receive strongly-typed server events, and use the
    sub-namespaces to send strongly-typed client events::

        async with client.realtime.connect(agent_name="my-agent") as conn:
            await conn.input_audio_buffer.append(audio=chunk)
            await conn.input_audio_buffer.commit()
            await conn.response.create()
            async for event in conn:
                if event.type == RealtimeServerEventType.RESPONSE_DONE:
                    break
    """

    def __init__(self, connection: "ClientWebSocketResponse", session: "ClientSession") -> None:
        self._connection = connection
        self._session = session
        self.session: SessionResource = SessionResource(self)
        self.input_audio_buffer: InputAudioBufferResource = InputAudioBufferResource(self)
        self.output_audio_buffer: OutputAudioBufferResource = OutputAudioBufferResource(self)
        self.conversation: ConversationResource = ConversationResource(self)
        self.response: ResponseResource = ResponseResource(self)

    async def __aenter__(self) -> "AsyncRealtimeConnection":
        return self

    async def __aexit__(self, *exc_details: Any) -> None:
        await self.close()

    def __repr__(self) -> str:
        state = "closed" if self.closed else "open"
        return f"<AsyncRealtimeConnection [{state}]>"

    @property
    def closed(self) -> bool:
        """Whether the underlying WebSocket connection has been closed.

        :rtype: bool
        """
        return self._connection.closed

    def __aiter__(self) -> AsyncIterator[ServerEvent]:
        return self._iter()

    async def _iter(self) -> AsyncIterator[ServerEvent]:
        while True:
            try:
                yield await self.recv()
            except ConnectionResetError:
                return

    async def recv(self) -> ServerEvent:
        """Receive and parse the next server event.

        Known event types are returned as their strongly-typed
        ``VoiceAgentServerEventXxx`` model. Event types not (yet) represented by a
        generated model are returned as a plain ``dict`` for forward compatibility.

        :return: The parsed server event.
        :rtype: ~azure.ai.projects.aio.ServerEvent
        :raises ConnectionResetError: If the connection was closed by the server.
        """
        import aiohttp  # pylint: disable=import-outside-toplevel

        msg = await self._connection.receive()
        while msg.type in (aiohttp.WSMsgType.PING, aiohttp.WSMsgType.PONG):
            msg = await self._connection.receive()
        if msg.type in (
            aiohttp.WSMsgType.CLOSE,
            aiohttp.WSMsgType.CLOSING,
            aiohttp.WSMsgType.CLOSED,
        ):
            raise ConnectionResetError("The realtime connection was closed.")
        if msg.type == aiohttp.WSMsgType.ERROR:
            raise ConnectionResetError(
                "The realtime connection encountered an error."
            ) from self._connection.exception()
        raw = msg.data.decode("utf-8") if msg.type == aiohttp.WSMsgType.BINARY else msg.data
        payload: Dict[str, Any] = json.loads(raw)
        event_type = payload.get("type")
        if not isinstance(event_type, str):
            return payload
        event_cls = _SERVER_EVENT_TYPES.get(event_type)
        if event_cls is None:
            return payload
        return event_cls(payload)

    async def send(self, event: ClientEvent) -> None:
        """Send a client event over the connection.

        :param event: A strongly-typed client event, a ready-made mapping, or a raw JSON string.
        :type event: ~azure.ai.projects.aio.ClientEvent or str
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
        await self._connection.send_str(payload)

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the connection and release the underlying HTTP session.

        :keyword int code: The WebSocket close code.
        :keyword str reason: The close reason.
        """
        try:
            await self._connection.close(code=code, message=reason.encode("utf-8"))
        finally:
            await self._session.close()


class AsyncRealtimeConnectionManager:  # pylint: disable=too-many-instance-attributes
    """Async context manager that opens an :class:`AsyncRealtimeConnection`.

    Returned by :meth:`AsyncRealtime.connect`; you normally use it as
    ``async with client.realtime.connect(...) as conn:``.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        endpoint: str,
        credential: "AsyncTokenCredential",
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
        self._connection: Optional[AsyncRealtimeConnection] = None

    async def __aenter__(self) -> AsyncRealtimeConnection:
        return await self.enter()

    async def enter(self) -> AsyncRealtimeConnection:  # pylint: disable=too-many-locals
        """Open the connection.

        :return: The live realtime connection.
        :rtype: ~azure.ai.projects.aio.AsyncRealtimeConnection
        :raises RuntimeError: If ``aiohttp`` is not installed.
        :raises ValueError: If the computed or supplied WebSocket URL does not use ``wss://``.
        :raises ConnectionError: If the WebSocket upgrade handshake fails (for example, a
         network error, DNS failure, or a non-101 response from the service).
        """
        try:
            import aiohttp  # pylint: disable=import-outside-toplevel
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "The realtime client requires `aiohttp`. Install it with `pip install aiohttp`."
            ) from exc

        # ``connection_url`` fully overrides the computed route (scheme/host/path). This is the
        # escape hatch used to reach a specific data-plane host/path directly.
        if self._connection_url is not None:
            _assert_trusted_connection_url(self._connection_url, self._endpoint)
        url = self._connection_url or _to_ws_url(self._endpoint, self._agent_name)
        if not url.startswith("wss://"):
            raise ValueError("The realtime WebSocket URL must use wss:// to protect credentials in transit.")

        params: Dict[str, str] = {"api-version": self._api_version, "x-ms-client-sdk": _USER_AGENT}
        if self._agent_session_id is not None:
            params["agent_session_id"] = self._agent_session_id
        if self._agent_version_override is not None:
            params["x-agent-version-override"] = self._agent_version_override
        params.update(self._extra_query)

        token = await self._credential.get_token(*self._credential_scopes)
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {token.token}",
            _FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features,
        }
        if self._structured_inputs is not None:
            headers["x-ms-voice-structured-inputs"] = self._structured_inputs
        headers.update(self._extra_headers)
        if not _has_header_case_insensitive(headers, "User-Agent"):
            # Only set our default if the caller didn't supply their own (in any casing) --
            # a plain dict merge would otherwise leave both as separate keys (HTTP header names
            # are case-insensitive, but Python dict keys are not), sending two User-Agent-like
            # headers instead of cleanly honoring the caller's override.
            headers["User-Agent"] = _USER_AGENT

        session = aiohttp.ClientSession()
        try:
            # Force the "realtime" WebSocket subprotocol regardless of any caller-supplied
            # override in ``self._kwargs``: the service requires this exact subprotocol, so
            # silently accepting a different one here would just move the failure to a less
            # clear error inside aiohttp's handshake.
            ws_connect_kwargs = dict(self._kwargs)
            ws_connect_kwargs.pop("protocols", None)
            connection = await session.ws_connect(
                url, headers=headers, params=params, protocols=("realtime",), **ws_connect_kwargs
            )
        except BaseException as exc:
            await session.close()
            if not isinstance(exc, Exception) or isinstance(exc, (ValueError, RuntimeError)):
                raise
            raise ConnectionError(
                f"Failed to open the realtime WebSocket connection to voice agent "
                f"'{self._agent_name}' at '{url}': {exc}"
            ) from exc
        self._connection = AsyncRealtimeConnection(cast("ClientWebSocketResponse", connection), session)
        return self._connection

    async def __aexit__(self, *exc_details: Any) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


class AsyncRealtime:  # pylint: disable=too-few-public-methods
    """Realtime streaming entry point, exposed as ``client.realtime``.

    Follows the OpenAI Python realtime surface: obtain it from the HTTP client and open a
    connection with :meth:`connect`::

        from azure.ai.projects.aio import AIProjectClient
        from azure.identity.aio import DefaultAzureCredential

        client = AIProjectClient(endpoint, DefaultAzureCredential())
        async with client.realtime.connect(agent_name="my-agent") as conn:
            await conn.input_audio_buffer.append(audio=chunk)
            await conn.input_audio_buffer.commit()
            await conn.response.create()
            async for event in conn:
                if event.type == RealtimeServerEventType.RESPONSE_DONE:
                    break

    :param client: The HTTP client whose endpoint and credential are reused for the realtime
     handshake.
    :type client: ~azure.ai.projects.aio.AIProjectClient
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
    ) -> AsyncRealtimeConnectionManager:
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
        :keyword connection_url: Full ``wss://`` URL that overrides the route computed
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
        :return: An async context manager yielding an :class:`AsyncRealtimeConnection`.
        :rtype: ~azure.ai.projects.aio.AsyncRealtimeConnectionManager
        """
        return AsyncRealtimeConnectionManager(
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
