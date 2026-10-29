# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Asynchronous GPT Live sessions at ``client.beta.voice_agents.live``."""

from __future__ import annotations

import base64
from typing import Any, AsyncIterator, Mapping, Optional, TYPE_CHECKING, Union

from .. import models
from .._live_utils import LiveClientEvent, LiveServerEvent, _LOGGER, _SERVER_EVENT_TYPES, _event, _live_query, _live_url
from ._realtime import _BaseWebSocketConnection, _BaseWebSocketConnectionManager, _ConfigProvider

if TYPE_CHECKING:
    from aiohttp import (  # pylint: disable=networking-import-outside-azure-core-transport
        ClientSession,
        ClientWebSocketResponse,
    )

__all__ = [
    "AsyncBetaLive",
    "AsyncBetaLiveConnection",
    "AsyncBetaLiveConnectionManager",
    "LiveClientEvent",
    "LiveServerEvent",
]


class _Resource:
    def __init__(self, connection: AsyncBetaLiveConnection) -> None:
        self._connection = connection


class TextResource(_Resource):
    """Send instructions, unspoken context, or spoken commentary.

    :param connection: The parent Live connection.
    :type connection: ~azure.ai.projects.aio.operations.AsyncBetaLiveConnection
    :param event_model: The generated model for the text command.
    :type event_model: type[~azure.ai.projects.models.LiveClientEvent]
    """

    def __init__(self, connection: AsyncBetaLiveConnection, event_model: type[models.LiveClientEvent]) -> None:
        super().__init__(connection)
        self._event_model = event_model

    async def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] = None) -> None:
        """Send text, optionally tied to a request delegated to your app.

        :keyword str content: Text to append.
        :keyword delegation_id: The delegated request's ID, or None for standalone text.
        :paramtype delegation_id: str or None
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(self._event_model, event_id, content=content, delegation_id=delegation_id))


class InputAudioResource(_Resource):
    """Send audio using the session's configured format."""

    async def append(self, *, audio: Union[str, bytes], event_id: Optional[str] = None) -> None:
        """Send raw audio bytes or base64 without a container header.

        :keyword audio: Raw audio or an already base64-encoded string.
        :paramtype audio: str or bytes
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        encoded = base64.b64encode(audio).decode("ascii") if isinstance(audio, bytes) else audio
        await self._connection.send(_event(models.LiveClientEventLiveInputAudioAppendEvent, event_id, audio=encoded))

    async def mute(self, *, event_id: Optional[str] = None) -> None:
        """Mute input audio processing.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(models.LiveClientEventLiveInputAudioMuteParam, event_id))

    async def unmute(self, *, event_id: Optional[str] = None) -> None:
        """Resume input audio processing.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(models.LiveClientEventLiveInputAudioUnmuteParam, event_id))


class SessionResource(_Resource):
    """Control a Live session that Foundry starts when the connection opens.

    :param connection: The parent Live connection.
    :type connection: ~azure.ai.projects.aio.operations.AsyncBetaLiveConnection
    """

    def __init__(self, connection: AsyncBetaLiveConnection) -> None:
        super().__init__(connection)
        self.input_audio = InputAudioResource(connection)
        self.instructions = TextResource(connection, models.LiveClientEventLiveInstructionsAppendParam)
        self.thinking = TextResource(connection, models.LiveClientEventLiveThinkingAppendParam)
        self.commentary = TextResource(connection, models.LiveClientEventLiveCommentaryAppendParam)

    async def update(
        self, *, session: Union[models.LiveSessionUpdateParams, Mapping[str, Any]], event_id: Optional[str] = None
    ) -> None:
        """Change delegation settings. The model and audio format cannot change mid-session.

        :keyword session: Only the delegation settings to change.
        :paramtype session: ~azure.ai.projects.models.LiveSessionUpdateParams or Mapping[str, Any]
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(models.LiveClientEventLiveSessionUpdateParam, event_id, session=session))

    async def close(self, *, event_id: Optional[str] = None) -> None:
        """Request graceful session shutdown; receive session.closed before closing the socket.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(models.LiveClientEventLiveSessionCloseParam, event_id))


class ResponseItemResource(_Resource):
    """Send user messages or tool results to the Responses backend model."""

    async def create(self, *, item: Mapping[str, Any], event_id: Optional[str] = None) -> None:
        """Send a message or tool result. Requires a Responses backend.

        :keyword item: Responses input item, including function_call_output.
        :paramtype item: Mapping[str, Any]
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(
            _event(models.LiveClientEventLiveResponseItemCreateParam, event_id, item=dict(item))
        )


class ResponseResource(_Resource):
    """Request replies from the Responses backend model.

    :param connection: The parent Live connection.
    :type connection: ~azure.ai.projects.aio.operations.AsyncBetaLiveConnection
    """

    def __init__(self, connection: AsyncBetaLiveConnection) -> None:
        super().__init__(connection)
        self.item = ResponseItemResource(connection)

    async def create(self, *, event_id: Optional[str] = None) -> None:
        """Request or continue a backend response after submitting tool results.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        await self._connection.send(_event(models.LiveClientEventLiveResponseCreateParam, event_id))


class AsyncBetaLiveConnection(_BaseWebSocketConnection[LiveServerEvent, LiveClientEvent]):
    """Send and receive events on a GPT Live connection.

    Service errors arrive as error events. Use the context manager to close
    the connection. Send ``session.close`` to end the session; Live has no
    ``response.cancel`` command.

    :param connection: The open WebSocket.
    :type connection: ~aiohttp.ClientWebSocketResponse
    :param session: The HTTP session that owns the WebSocket.
    :type session: ~aiohttp.ClientSession
    """

    _logger = _LOGGER
    _server_event_types = _SERVER_EVENT_TYPES
    _protocol_name = "Live"

    def __init__(self, connection: ClientWebSocketResponse, session: ClientSession) -> None:
        super().__init__(connection, session)
        self.session = SessionResource(self)
        self.response = ResponseResource(self)

    async def __aenter__(self) -> AsyncBetaLiveConnection:
        return self

    def __aiter__(self) -> AsyncIterator[LiveServerEvent]:
        return super().__aiter__()

    async def recv(self) -> LiveServerEvent:
        """Receive an SDK event model, or a dictionary for an unknown event type.

        :return: The server event.
        :rtype: ~azure.ai.projects.aio.operations.LiveServerEvent
        :raises ConnectionResetError: On graceful or abnormal socket closure.
        :raises ValueError: If the server event is not a JSON object.
        """
        return await super().recv()

    async def send(self, event: LiveClientEvent) -> None:
        """Send an SDK event model, mapping, or JSON string.

        :param event: The client event.
        :type event: ~azure.ai.projects.aio.operations.LiveClientEvent
        :raises ValueError: If the supplied JSON string is invalid.
        """
        await super().send(dict(event) if isinstance(event, Mapping) else event)


class AsyncBetaLiveConnectionManager(_BaseWebSocketConnectionManager[AsyncBetaLiveConnection]):
    """Context manager for one Live session using the project's credential.

    :keyword agent_version: A specific agent version, if needed.
    :paramtype agent_version: str or None
    :keyword store: Save conversation content and audio. None uses the agent's setting.
    :paramtype store: bool or None
    """

    _logger = _LOGGER
    _subprotocol = None
    _protocol_name = "Live"

    def __init__(
        self,
        *,
        agent_version: Optional[str] = None,
        store: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._agent_version = agent_version
        self._store = store

    async def __aenter__(self) -> AsyncBetaLiveConnection:
        return await self.enter()

    async def enter(self) -> AsyncBetaLiveConnection:
        """Open the connection. Foundry starts the Live session automatically.

        :return: The Live connection.
        :rtype: ~azure.ai.projects.aio.operations.AsyncBetaLiveConnection
        :raises RuntimeError: If ``aiohttp`` is not installed.
        :raises ValueError: If the computed or supplied WebSocket URL does not use ``wss://``.
        :raises ConnectionError: If the WebSocket upgrade handshake fails.
        """
        return await super().enter()

    def _get_url(self) -> str:
        return _live_url(self._endpoint, self._agent_name)

    def _get_query(self) -> dict[str, str]:
        return _live_query(
            self._api_version, self._agent_version, self._structured_inputs, self._store, self._extra_query
        )

    def _create_connection(
        self, connection: ClientWebSocketResponse, session: ClientSession
    ) -> AsyncBetaLiveConnection:
        return AsyncBetaLiveConnection(connection, session)


class AsyncBetaLive:
    """Connect to GPT Live through ``client.beta.voice_agents.live``.

    Foundry starts the session from the saved agent settings. Wait for
    ``session.started`` before sending commands; do not send ``session.start``.

    :param args: The voice-agent sub-client whose shared configuration is reused.
    :type args: ~azure.ai.projects.aio.operations.BetaVoiceAgentsOperations
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        input_args = list(args)
        client: _ConfigProvider = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config = client._config  # pylint: disable=protected-access

    def connect(
        self,
        *,
        agent_name: str,
        agent_version: Optional[str] = None,
        structured_inputs: Optional[Mapping[str, Any]] = None,
        store: Optional[bool] = None,
        connection_url: Optional[str] = None,
        api_version: Optional[str] = None,
        credential_scopes: Optional[list[str]] = None,
        extra_query: Optional[Mapping[str, str]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> AsyncBetaLiveConnectionManager:
        """Connect to a GPT Live agent when entering the context manager.

        :keyword str agent_name: The name of an existing GPT Live agent.
        :keyword agent_version: A specific agent version, if needed.
        :paramtype agent_version: str or None
        :keyword structured_inputs: Values for placeholders in the agent's instructions and greeting.
        :paramtype structured_inputs: Mapping[str, Any] or None
        :keyword store: Save conversation content and audio. None uses the agent's setting.
        :paramtype store: bool or None
        :keyword connection_url: A wss URL on the project endpoint's origin, instead of the default route.
        :paramtype connection_url: str or None
        :keyword api_version: API version override.
        :paramtype api_version: str or None
        :keyword credential_scopes: Token scope override.
        :paramtype credential_scopes: list[str] or None
        :keyword extra_query: Additional handshake query values.
        :paramtype extra_query: Mapping[str, str] or None
        :keyword extra_headers: Additional handshake headers.
        :paramtype extra_headers: Mapping[str, str] or None
        :return: An asynchronous Live connection context manager.
        :rtype: ~azure.ai.projects.aio.operations.AsyncBetaLiveConnectionManager
        """
        return AsyncBetaLiveConnectionManager(
            endpoint=self._config.endpoint,
            credential=self._config.credential,
            credential_scopes=credential_scopes or self._config.credential_scopes,
            api_version=api_version or self._config.api_version,
            agent_name=agent_name,
            agent_version=agent_version,
            structured_inputs=structured_inputs,
            store=store,
            connection_url=connection_url,
            extra_query=extra_query,
            extra_headers=extra_headers,
            **kwargs,
        )
