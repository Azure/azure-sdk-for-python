# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline tests for typed realtime transport selection in both Python clients."""

import inspect
from types import SimpleNamespace
from typing import Any, Optional, Union
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.credentials import AccessToken
from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects._realtime import BetaRealtime, BetaRealtimeConnectionManager
from azure.ai.projects.aio._realtime import AsyncBetaRealtime, AsyncBetaRealtimeConnectionManager
from azure.ai.projects.models import VoiceAgentTransport

_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
_PUBLIC_METHODS = [
    BetaRealtime.connect,
    AsyncBetaRealtime.connect,
    BetaRealtimeConnectionManager.__init__,
    AsyncBetaRealtimeConnectionManager.__init__,
]


def _make_realtime(is_async: bool) -> tuple[Union[BetaRealtime, AsyncBetaRealtime], MagicMock]:
    credential = MagicMock()
    token = AccessToken("fake-token", 9_999_999_999)
    credential.get_token = AsyncMock(return_value=token) if is_async else MagicMock(return_value=token)
    client = SimpleNamespace(
        _config=SimpleNamespace(
            endpoint=_ENDPOINT,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
            api_version="v1",
        )
    )
    return (AsyncBetaRealtime(client) if is_async else BetaRealtime(client)), credential


async def _capture_handshake(
    manager: Union[BetaRealtimeConnectionManager, AsyncBetaRealtimeConnectionManager],
) -> tuple[str, dict[str, Any]]:
    if isinstance(manager, AsyncBetaRealtimeConnectionManager):
        connection = MagicMock(close=AsyncMock())
        session = MagicMock(ws_connect=AsyncMock(return_value=connection), close=AsyncMock())
        with patch("aiohttp.ClientSession", return_value=session):
            async with manager:
                pass
        call = session.ws_connect.call_args
        session.close.assert_awaited_once()
        connection.close.assert_awaited_once()
    else:
        connection = MagicMock()
        with patch("websockets.sync.client.connect", return_value=connection) as connect:
            with manager:
                pass
        call = connect.call_args
        connection.close.assert_called_once()

    assert "transport" not in call.kwargs
    return call.args[0], call.kwargs


def _handshake_query(url: str, kwargs: dict[str, Any]) -> dict[str, list[str]]:
    query = parse_qs(urlsplit(url).query, keep_blank_values=True)
    for name, value in (kwargs.get("params") or {}).items():
        query.setdefault(name, []).append(value)
    return query


@pytest.mark.parametrize("method", _PUBLIC_METHODS)
def test_transport_is_optional_and_keyword_only(method: Any) -> None:
    parameter = inspect.signature(method).parameters["transport"]

    assert parameter.kind == inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is None
    assert "VoiceAgentTransport" in parameter.annotation


@pytest.mark.parametrize("method", _PUBLIC_METHODS)
def test_extra_query_retains_original_string_mapping_contract(method: Any) -> None:
    parameter = inspect.signature(method).parameters["extra_query"]

    assert parameter.annotation == "Optional[Mapping[str, str]]"
    assert parameter.default is None


def test_generated_transport_enum_is_public_with_expected_wire_values() -> None:
    assert VoiceAgentTransport.WEBSOCKET.value == "websocket"
    assert VoiceAgentTransport.WEBRTC.value == "webrtc"


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "transport",
    [VoiceAgentTransport.WEBSOCKET, VoiceAgentTransport.WEBRTC, "websocket", "webrtc", "future-transport"],
)
async def test_transport_is_encoded_internally_without_socket_keyword(
    is_async: bool, transport: Union[str, VoiceAgentTransport]
) -> None:
    realtime, _ = _make_realtime(is_async)
    manager = realtime.connect(agent_name="agent-test", transport=transport)
    url, kwargs = await _capture_handshake(manager)
    query = _handshake_query(url, kwargs)
    expected = transport.value if isinstance(transport, VoiceAgentTransport) else transport

    assert query["transport"] == [expected]


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("explicit_none", [False, True], ids=["omitted", "none"])
async def test_default_transport_does_not_add_a_query_parameter(is_async: bool, explicit_none: bool) -> None:
    realtime, _ = _make_realtime(is_async)
    options = {"transport": None} if explicit_none else {}
    manager = realtime.connect(agent_name="agent-test", **options)
    url, kwargs = await _capture_handshake(manager)

    assert "transport" not in _handshake_query(url, kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("transport", [None, VoiceAgentTransport.WEBRTC], ids=["legacy-query", "typed-option"])
async def test_transport_selection_preserves_other_query_values_and_override_precedence(
    is_async: bool, transport: Optional[VoiceAgentTransport]
) -> None:
    realtime, _ = _make_realtime(is_async)
    extra_query = {"transport": "websocket", "custom": "space + /?&=#"}
    connection_url = (
        "wss://fake-account.services.ai.azure.com/custom"
        "?transport=old&%74ransport=duplicate&keep=one&keep=two&empty=&path=folder%2F"
    )
    manager = realtime.connect(
        agent_name="agent-test",
        connection_url=connection_url,
        transport=transport,
        extra_query=extra_query,
    )
    url, kwargs = await _capture_handshake(manager)
    query = _handshake_query(url, kwargs)

    assert query["keep"] == ["one", "two"]
    assert query["empty"] == [""]
    assert query["path"] == ["folder/"]
    assert query["custom"] == ["space + /?&=#"]
    assert "path=folder%2F" in url
    if transport is not None:
        assert query["transport"] == ["webrtc"]
    else:
        assert query["transport"] == ["old", "duplicate", "websocket"]
    assert extra_query == {"transport": "websocket", "custom": "space + /?&=#"}


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("transport", [False, 1, {}, object()])
def test_invalid_transport_type_fails_before_authentication_or_socket_creation(is_async: bool, transport: Any) -> None:
    realtime, credential = _make_realtime(is_async)
    with patch("aiohttp.ClientSession") as session, patch("websockets.sync.client.connect") as connect:
        with pytest.raises(TypeError, match="transport must be a string or VoiceAgentTransport"):
            realtime.connect(agent_name="agent-test", transport=transport)

    credential.get_token.assert_not_called()
    session.assert_not_called()
    connect.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
async def test_transport_selection_is_connection_scoped(is_async: bool) -> None:
    realtime, _ = _make_realtime(is_async)
    first = realtime.connect(agent_name="agent-test", transport=VoiceAgentTransport.WEBRTC)
    second = realtime.connect(agent_name="agent-test")
    first_url, first_kwargs = await _capture_handshake(first)
    second_url, second_kwargs = await _capture_handshake(second)

    assert _handshake_query(first_url, first_kwargs)["transport"] == ["webrtc"]
    assert "transport" not in _handshake_query(second_url, second_kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
async def test_public_project_client_exposes_typed_transport_selection(is_async: bool) -> None:
    _, credential = _make_realtime(is_async)
    manager: Union[BetaRealtimeConnectionManager, AsyncBetaRealtimeConnectionManager]
    if is_async:
        async with AsyncAIProjectClient(endpoint=_ENDPOINT, credential=credential, allow_preview=True) as async_client:
            manager = async_client.beta.voice_agents.realtime.connect(
                agent_name="agent-test", transport=VoiceAgentTransport.WEBRTC
            )
            url, kwargs = await _capture_handshake(manager)
    else:
        with AIProjectClient(endpoint=_ENDPOINT, credential=credential, allow_preview=True) as client:
            manager = client.beta.voice_agents.realtime.connect(
                agent_name="agent-test", transport=VoiceAgentTransport.WEBRTC
            )
            url, kwargs = await _capture_handshake(manager)

    assert _handshake_query(url, kwargs)["transport"] == ["webrtc"]
