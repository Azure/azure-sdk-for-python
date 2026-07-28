# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Hand-written async realtime (WebSocket) streaming client for voice agents.

Realtime uses a fundamentally different transport (a persistent WebSocket)
than the request/response HTTP surface. It is exposed as the
``VoiceAgentsClient.realtime`` namespace.
The connection ergonomics follow the OpenAI Python realtime client so that
developers moving between the two libraries get a familiar surface:

* :meth:`AsyncRealtime.connect` returns an async context manager.
* Entering the context yields an :class:`AsyncRealtimeConnection`.
* The connection is async-iterable over inbound server events and exposes
  sub-namespaces (``session``, ``input_audio_buffer``, ``output_audio_buffer``,
  ``conversation``, ``response``) for sending outbound client events.

The realtime wire schema is owned by Voice Live and is intentionally kept
open here: inbound events are surfaced as plain ``dict`` objects and outbound
events accept either a ready-made mapping or the typed helper methods below.
This keeps the SDK usable today without hard-coupling it to a frame schema
that is still being finalized service-side.

``aiohttp`` is required for this feature and is *not* a hard dependency of the
package; it is imported lazily so importing the SDK never fails when it is
absent.
"""

from __future__ import annotations

import base64
import json
from typing import Any, AsyncIterator, List, Mapping, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from aiohttp import ClientSession, ClientWebSocketResponse
    from azure.core.credentials_async import AsyncTokenCredential


__all__ = [
    "AsyncRealtime",
    "AsyncRealtimeConnection",
    "AsyncRealtimeConnectionManager",
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


class _BaseResource:
    """Base helper that forwards typed helpers to the parent connection."""

    def __init__(self, connection: "AsyncRealtimeConnection") -> None:
        self._connection = connection

    async def _send(self, event: Mapping[str, Any]) -> None:
        await self._connection.send(event)


class SessionResource(_BaseResource):
    """Send ``session.*`` client events."""

    async def update(self, *, session: Mapping[str, Any], **extra: Any) -> None:
        """Update the realtime session configuration.

        :keyword session: The session configuration to apply.
        :paramtype session: Mapping[str, Any]
        """
        await self._send({"type": "session.update", "session": dict(session), **extra})


class InputAudioBufferResource(_BaseResource):
    """Send ``input_audio_buffer.*`` client events."""

    async def append(self, *, audio: Union[str, bytes], **extra: Any) -> None:
        """Append audio bytes to the input buffer.

        :keyword audio: Raw audio bytes, or an already base64-encoded string.
        :paramtype audio: str or bytes
        """
        if isinstance(audio, (bytes, bytearray)):
            audio = base64.b64encode(bytes(audio)).decode("ascii")
        await self._send({"type": "input_audio_buffer.append", "audio": audio, **extra})

    async def commit(self, **extra: Any) -> None:
        """Commit the buffered input audio as a user turn."""
        await self._send({"type": "input_audio_buffer.commit", **extra})

    async def clear(self, **extra: Any) -> None:
        """Discard any buffered input audio."""
        await self._send({"type": "input_audio_buffer.clear", **extra})


class OutputAudioBufferResource(_BaseResource):
    """Send ``output_audio_buffer.*`` client events."""

    async def clear(self, **extra: Any) -> None:
        """Stop and clear any audio the service is currently playing back."""
        await self._send({"type": "output_audio_buffer.clear", **extra})


class ConversationItemResource(_BaseResource):
    """Send ``conversation.item.*`` client events."""

    async def create(self, *, item: Mapping[str, Any], **extra: Any) -> None:
        """Insert an item into the conversation.

        :keyword item: The conversation item to create.
        :paramtype item: Mapping[str, Any]
        """
        await self._send({"type": "conversation.item.create", "item": dict(item), **extra})

    async def delete(self, *, item_id: str, **extra: Any) -> None:
        """Delete an item from the conversation.

        :keyword str item_id: The id of the item to delete.
        """
        await self._send({"type": "conversation.item.delete", "item_id": item_id, **extra})

    async def truncate(self, *, item_id: str, content_index: int, audio_end_ms: int, **extra: Any) -> None:
        """Truncate a previously produced assistant audio item.

        :keyword str item_id: The id of the assistant item to truncate.
        :keyword int content_index: The index of the content part to truncate.
        :keyword int audio_end_ms: The point, in milliseconds, to truncate the audio to.
        """
        await self._send(
            {
                "type": "conversation.item.truncate",
                "item_id": item_id,
                "content_index": content_index,
                "audio_end_ms": audio_end_ms,
                **extra,
            }
        )


class ConversationResource(_BaseResource):
    """Send ``conversation.*`` client events."""

    def __init__(self, connection: "AsyncRealtimeConnection") -> None:
        super().__init__(connection)
        self.item: ConversationItemResource = ConversationItemResource(connection)


class ResponseResource(_BaseResource):
    """Send ``response.*`` client events."""

    async def create(self, *, response: Optional[Mapping[str, Any]] = None, **extra: Any) -> None:
        """Ask the model to generate a response.

        :keyword response: Optional per-response overrides.
        :paramtype response: Mapping[str, Any] or None
        """
        event: dict[str, Any] = {"type": "response.create", **extra}
        if response is not None:
            event["response"] = dict(response)
        await self._send(event)

    async def cancel(self, *, response_id: Optional[str] = None, **extra: Any) -> None:
        """Cancel an in-progress response.

        :keyword response_id: The id of the response to cancel, if targeting a specific one.
        :paramtype response_id: str or None
        """
        event: dict[str, Any] = {"type": "response.cancel", **extra}
        if response_id is not None:
            event["response_id"] = response_id
        await self._send(event)


class AsyncRealtimeConnection:
    """An open realtime WebSocket connection to a voice agent.

    Iterate over the connection to receive server events as ``dict`` objects,
    and use the sub-namespaces to send client events::

        async with client.realtime.connect(agent_name="my-agent") as conn:
            await conn.session.update(session={"modalities": ["audio", "text"]})
            await conn.input_audio_buffer.append(audio=chunk)
            await conn.input_audio_buffer.commit()
            await conn.response.create()
            async for event in conn:
                if event["type"] == "response.done":
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

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        return self._iter()

    async def _iter(self) -> AsyncIterator[dict[str, Any]]:
        while True:
            try:
                yield await self.recv()
            except ConnectionResetError:
                return

    async def recv(self) -> dict[str, Any]:
        """Receive and parse the next JSON server event.

        :return: The parsed server event.
        :rtype: dict[str, Any]
        :raises ConnectionResetError: If the connection was closed by the server.
        """
        import aiohttp

        msg = await self._connection.receive()
        if msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
            raise ConnectionResetError("The realtime connection was closed.")
        if msg.type == aiohttp.WSMsgType.ERROR:
            raise ConnectionResetError(
                "The realtime connection encountered an error."
            ) from self._connection.exception()
        if msg.type == aiohttp.WSMsgType.BINARY:
            return json.loads(msg.data.decode("utf-8"))
        return json.loads(msg.data)

    async def send(self, event: Union[Mapping[str, Any], str]) -> None:
        """Send a client event over the connection.

        :param event: A ready-made event mapping, or a raw JSON string.
        :type event: Mapping[str, Any] or str
        """
        if isinstance(event, str):
            await self._connection.send_str(event)
        else:
            await self._connection.send_str(json.dumps(dict(event)))

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        """Close the connection and release the underlying HTTP session.

        :keyword int code: The WebSocket close code.
        :keyword str reason: The close reason.
        """
        try:
            await self._connection.close(code=code, message=reason.encode("utf-8"))
        finally:
            await self._session.close()


class AsyncRealtimeConnectionManager:
    """Async context manager that opens an :class:`AsyncRealtimeConnection`.

    Returned by :meth:`AsyncRealtime.connect`; you normally use it as
    ``async with client.realtime.connect(...) as conn:``.
    """

    def __init__(
        self,
        *,
        endpoint: str,
        credential: "AsyncTokenCredential",
        credential_scopes: List[str],
        api_version: str,
        agent_name: str,
        foundry_features: Optional[str] = None,
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
        self._connection_url = connection_url
        self._extra_query = dict(extra_query or {})
        self._extra_headers = dict(extra_headers or {})
        self._kwargs = kwargs
        self._connection: Optional[AsyncRealtimeConnection] = None

    async def __aenter__(self) -> AsyncRealtimeConnection:
        return await self.enter()

    async def enter(self) -> AsyncRealtimeConnection:
        """Open the connection.

        :return: The live realtime connection.
        :rtype: AsyncRealtimeConnection
        """
        try:
            import aiohttp
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError(
                "The realtime client requires `aiohttp`. Install it with `pip install aiohttp`."
            ) from exc

        # ``connection_url`` fully overrides the computed route (scheme/host/path). This is the
        # escape hatch used to reach the deployed data-plane route directly while the public
        # endpoint's routing to agent orchestration is still rolling out.
        url = self._connection_url or _to_ws_url(self._endpoint, self._agent_name)

        params: dict[str, str] = {"api-version": self._api_version}
        params.update(self._extra_query)

        token = await self._credential.get_token(*self._credential_scopes)
        headers: dict[str, str] = {"Authorization": f"Bearer {token.token}"}
        if self._foundry_features is not None:
            # Coerce enum members (e.g. ``AgentDefinitionOptInKeys``) to their string value so the
            # header carries ``VoiceAgents=V1Preview`` rather than the enum's ``repr``/``str`` form,
            # which the gateway rejects with a 403 during the WebSocket handshake.
            foundry_features = getattr(self._foundry_features, "value", self._foundry_features)
            headers["Foundry-Features"] = str(foundry_features)
        headers.update(self._extra_headers)

        session = aiohttp.ClientSession()
        try:
            connection = await session.ws_connect(url, headers=headers, params=params, **self._kwargs)
        except BaseException:
            await session.close()
            raise
        self._connection = AsyncRealtimeConnection(connection, session)  # type: ignore[arg-type]
        return self._connection

    async def __aexit__(self, *exc_details: Any) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


class AsyncRealtime:
    """Realtime streaming entry point, exposed as ``client.realtime``.

    Follows the OpenAI Python realtime surface: obtain it from the HTTP client
    and open a connection with :meth:`connect`::

        from azure.ai.voiceagents.aio import VoiceAgentsClient
        from azure.identity.aio import DefaultAzureCredential

        client = VoiceAgentsClient(endpoint, DefaultAzureCredential())
        async with client.realtime.connect(agent_name="my-agent") as conn:
            await conn.session.update(session={"modalities": ["audio", "text"]})
            await conn.input_audio_buffer.append(audio=chunk)
            await conn.input_audio_buffer.commit()
            await conn.response.create()
            async for event in conn:
                if event["type"] == "response.done":
                    break

    :param client: The HTTP client whose endpoint and credential are reused for
     the realtime handshake.
    :type client: ~azure.ai.voiceagents.aio.VoiceAgentsClient
    """

    def __init__(self, client: Any) -> None:
        self._config = client._config  # pylint: disable=protected-access

    def connect(
        self,
        *,
        agent_name: str,
        foundry_features: Optional[str] = None,
        connection_url: Optional[str] = None,
        api_version: Optional[str] = None,
        credential_scopes: Optional[List[str]] = None,
        extra_query: Optional[Mapping[str, str]] = None,
        extra_headers: Optional[Mapping[str, str]] = None,
        **kwargs: Any,
    ) -> AsyncRealtimeConnectionManager:
        """Open a realtime WebSocket connection to a voice agent.

        :keyword str agent_name: The name of the voice agent to connect to.
        :keyword foundry_features: Preview opt-in value for the ``Foundry-Features`` header,
         e.g. ``AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW`` or
         ``"VoiceAgents=V1Preview"``. Default value is None.
        :paramtype foundry_features: str or None
        :keyword connection_url: Full ``wss://``/``ws://`` URL that overrides the route computed
         from the client endpoint. Use this to target a specific data-plane host/path directly;
         query parameters are still appended. Default value is None.
        :paramtype connection_url: str or None
        :keyword api_version: Overrides the client's API version for the handshake. Default value is None.
        :paramtype api_version: str or None
        :keyword credential_scopes: Overrides the client's token scopes for the handshake.
         Default value is None.
        :paramtype credential_scopes: list[str] or None
        :keyword extra_query: Additional query-string parameters for the handshake.
        :paramtype extra_query: Mapping[str, str] or None
        :keyword extra_headers: Additional headers for the handshake.
        :paramtype extra_headers: Mapping[str, str] or None
        :return: An async context manager yielding an :class:`AsyncRealtimeConnection`.
        :rtype: AsyncRealtimeConnectionManager
        """
        return AsyncRealtimeConnectionManager(
            endpoint=self._config.endpoint,
            credential=self._config.credential,
            credential_scopes=credential_scopes or self._config.credential_scopes,
            api_version=api_version or self._config.api_version,
            agent_name=agent_name,
            foundry_features=foundry_features,
            connection_url=connection_url,
            extra_query=extra_query,
            extra_headers=extra_headers,
            **kwargs,
        )
