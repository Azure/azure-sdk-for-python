# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Synchronous GPT Live sessions at ``client.beta.voice_agents.live``."""

from __future__ import annotations

import base64
from typing import Any, Iterator, Mapping, Optional, TYPE_CHECKING, Union

from . import models
from ._realtime import _BaseWebSocketConnection, _BaseWebSocketConnectionManager, _ConfigProvider
from ._live_utils import LiveClientEvent, LiveServerEvent, _LOGGER, _SERVER_EVENT_TYPES, _event, _live_query, _live_url

if TYPE_CHECKING:
    from websockets.sync.client import ClientConnection

__all__ = ["BetaLive", "BetaLiveConnection", "BetaLiveConnectionManager", "LiveClientEvent", "LiveServerEvent"]


class _Resource:
    def __init__(self, connection: BetaLiveConnection) -> None:
        self._connection = connection


class TextResource(_Resource):
    """Send instructions, unspoken context, or spoken commentary."""

    def __init__(self, connection: BetaLiveConnection, event_model: type[models.LiveClientEvent]) -> None:
        super().__init__(connection)
        self._event_model = event_model

    def append(self, *, content: str, delegation_id: Optional[str], event_id: Optional[str] = None) -> None:
        """Send text, optionally tied to a request delegated to your app.

        :keyword str content: Text to append.
        :keyword delegation_id: The delegated request's ID, or None for standalone text.
        :paramtype delegation_id: str or None
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(self._event_model, event_id, content=content, delegation_id=delegation_id))


class InputAudioResource(_Resource):
    """Send audio using the session's configured format."""

    def append(self, *, audio: Union[str, bytes], event_id: Optional[str] = None) -> None:
        """Send raw audio bytes or base64 without a container header.

        :keyword audio: Raw audio or an already base64-encoded string.
        :paramtype audio: str or bytes
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        encoded = base64.b64encode(audio).decode("ascii") if isinstance(audio, bytes) else audio
        self._connection.send(_event(models.LiveClientEventLiveInputAudioAppendEvent, event_id, audio=encoded))

    def mute(self, *, event_id: Optional[str] = None) -> None:
        """Mute input audio processing.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveInputAudioMuteParam, event_id))

    def unmute(self, *, event_id: Optional[str] = None) -> None:
        """Resume input audio processing.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveInputAudioUnmuteParam, event_id))


class SessionResource(_Resource):
    """Control a Live session that Foundry starts when the connection opens."""

    def __init__(self, connection: BetaLiveConnection) -> None:
        super().__init__(connection)
        self.input_audio = InputAudioResource(connection)
        self.instructions = TextResource(connection, models.LiveClientEventLiveInstructionsAppendParam)
        self.thinking = TextResource(connection, models.LiveClientEventLiveThinkingAppendParam)
        self.commentary = TextResource(connection, models.LiveClientEventLiveCommentaryAppendParam)

    def update(
        self, *, session: Union[models.LiveSessionUpdateParams, Mapping[str, Any]], event_id: Optional[str] = None
    ) -> None:
        """Change delegation settings. The model and audio format cannot change mid-session.

        :keyword session: Only the delegation settings to change.
        :paramtype session: ~azure.ai.projects.models.LiveSessionUpdateParams or Mapping[str, Any]
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveSessionUpdateParam, event_id, session=session))

    def close(self, *, event_id: Optional[str] = None) -> None:
        """Request graceful session shutdown; receive session.closed before closing the socket.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveSessionCloseParam, event_id))


class ResponseItemResource(_Resource):
    """Send user messages or tool results to the Responses backend model."""

    def create(self, *, item: Mapping[str, Any], event_id: Optional[str] = None) -> None:
        """Send a message or tool result. Requires a Responses backend.

        :keyword item: Responses input item, including function_call_output.
        :paramtype item: Mapping[str, Any]
        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveResponseItemCreateParam, event_id, item=dict(item)))


class ResponseResource(_Resource):
    """Request replies from the Responses backend model."""

    def __init__(self, connection: BetaLiveConnection) -> None:
        super().__init__(connection)
        self.item = ResponseItemResource(connection)

    def create(self, *, event_id: Optional[str] = None) -> None:
        """Request or continue a backend response after submitting tool results.

        :keyword event_id: Optional client event identifier.
        :paramtype event_id: str or None
        """
        self._connection.send(_event(models.LiveClientEventLiveResponseCreateParam, event_id))


class BetaLiveConnection(_BaseWebSocketConnection[LiveServerEvent, LiveClientEvent]):
    """Send and receive events on a GPT Live connection.

    Service errors arrive as error events. Use the context manager to close
    the connection. Send ``session.close`` to end the session; Live has no
    ``response.cancel`` command.
    """

    _logger = _LOGGER
    _server_event_types = _SERVER_EVENT_TYPES
    _protocol_name = "Live"

    def __init__(self, connection: ClientConnection) -> None:
        super().__init__(connection)
        self.session = SessionResource(self)
        self.response = ResponseResource(self)

    def __enter__(self) -> BetaLiveConnection:
        return self

    def __iter__(self) -> Iterator[LiveServerEvent]:
        return self._iter()

    def recv(self, *, timeout: Optional[float] = None) -> LiveServerEvent:
        """Receive an SDK event model, or a dictionary for an unknown event type.

        :keyword timeout: Maximum receive wait in seconds; None waits indefinitely.
        :paramtype timeout: float or None
        :return: The server event.
        :rtype: ~azure.ai.projects.operations.LiveServerEvent
        :raises ConnectionResetError: On graceful or abnormal socket closure.
        :raises TimeoutError: When the receive deadline expires.
        """
        return super().recv(timeout=timeout)

    def send(self, event: LiveClientEvent) -> None:
        """Send an SDK event model, mapping, or JSON string.

        :param event: The client event.
        :type event: ~azure.ai.projects.operations.LiveClientEvent
        :raises ValueError: If the supplied JSON string is invalid.
        """
        super().send(dict(event) if isinstance(event, Mapping) else event)


class BetaLiveConnectionManager(_BaseWebSocketConnectionManager[BetaLiveConnection]):
    """Context manager for one Live session using the project's credential."""

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

    def __enter__(self) -> BetaLiveConnection:
        return self.enter()

    def enter(self) -> BetaLiveConnection:
        """Open the connection. Foundry starts the Live session automatically.

        :return: The Live connection.
        :rtype: ~azure.ai.projects.operations.BetaLiveConnection
        """
        return super().enter()

    def _get_url(self) -> str:
        return _live_url(self._endpoint, self._agent_name)

    def _get_query(self) -> dict[str, str]:
        return _live_query(
            self._api_version, self._agent_version, self._structured_inputs, self._store, self._extra_query
        )

    def _create_connection(self, connection: ClientConnection) -> BetaLiveConnection:
        return BetaLiveConnection(connection)


class BetaLive:
    """Connect to GPT Live through ``client.beta.voice_agents.live``.

    Foundry starts the session from the saved agent settings. Wait for
    ``session.started`` before sending commands; do not send ``session.start``.
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
    ) -> BetaLiveConnectionManager:
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
        :return: A Live connection context manager.
        :rtype: ~azure.ai.projects.operations.BetaLiveConnectionManager
        """
        return BetaLiveConnectionManager(
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
