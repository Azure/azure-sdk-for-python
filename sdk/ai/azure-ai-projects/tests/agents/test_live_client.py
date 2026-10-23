# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Deterministic public Live client tests, with only WebSocket transports replaced.

Both clients use the same wire assertions. No service, recording, real credential,
or audio device is involved; audio payloads are small synthetic byte sequences.
"""

import asyncio
import base64
import inspect
import json
import logging
import threading
from collections import UserDict
from collections.abc import AsyncIterator, Iterator, Mapping
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from types import MappingProxyType, SimpleNamespace
from typing import Optional, TypeVar, get_args, get_origin, get_type_hints
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from urllib.parse import parse_qs, urlsplit

import aiohttp
import pytest
import pytest_asyncio
from azure.core.credentials import AccessToken
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.frames import Close

from azure.ai.projects import AIProjectClient, __version__, models, operations
from azure.ai.projects._live_utils import _server_event_types
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.aio import operations as async_operations


_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
_HOST = "fake-account.services.ai.azure.com"
_AGENT = "agent-test"
_TOKEN = "unit-test-token"
_SCOPES = ("https://ai.azure.com/.default",)
_SESSION = {
    "id": "live-session-test",
    "model": "gpt-live-1",
    "expires_at": 9_999_999_999,
    "status": "active",
    "store": False,
    "delegation": {"type": "client"},
}
_STARTED = {"type": "session.started", "event_id": "evt-started", "session": _SESSION}
_CLOSED = {
    "type": "session.closed",
    "event_id": "evt-closed",
    "client_event_id": "evt-close",
    "reason": "close_requested",
    "session": _SESSION,
    "usage": {"seconds": 1.25},
}

pytestmark = pytest.mark.asyncio


class _FakeCredential:
    def __init__(self):
        self.calls = []
        self.failure = None

    def get_token(self, *scopes, **kwargs):
        self.calls.append((scopes, kwargs))
        if self.failure is not None:
            raise self.failure
        return AccessToken(_TOKEN, 9_999_999_999)


class _AsyncFakeCredential(_FakeCredential):
    async def get_token(self, *scopes, **kwargs):
        return super().get_token(*scopes, **kwargs)


def _message(kind, data=None):
    return SimpleNamespace(type=kind, data=data)


def _handshake_query(url, kwargs):
    query = parse_qs(urlsplit(url).query, keep_blank_values=True)
    for name, value in kwargs.get("params", {}).items():
        query.setdefault(name, []).append(value)
    return query


def _contains_type_variable(annotation):
    return isinstance(annotation, TypeVar) or any(
        _contains_type_variable(argument) for argument in get_args(annotation)
    )


class _Transport:
    def __init__(self, is_async):
        self.is_async = is_async
        self.socket = MagicMock(name="websocket")
        self.socket.closed = False
        self.socket.close_code = None
        self.socket.recv.return_value = json.dumps(_STARTED)
        self.socket.receive = AsyncMock(return_value=_message(aiohttp.WSMsgType.TEXT, json.dumps(_STARTED)))
        self.socket.send_str = AsyncMock()
        self.socket.exception.return_value = None
        close = AsyncMock if is_async else Mock
        self.socket.close = close(side_effect=self._close_socket)
        self.session = MagicMock(name="websocket_session")
        self.session.closed = False
        self.session.ws_connect = AsyncMock(return_value=self.socket)
        self.session.close = AsyncMock(side_effect=self._close_session)

    def _close_socket(self, **kwargs):
        self.socket.closed = True

    def _close_session(self):
        self.session.closed = True

    @property
    def writes(self):
        return self.socket.send_str if self.is_async else self.socket.send

    @property
    def sent(self):
        calls = self.writes.await_args_list if self.is_async else self.writes.call_args_list
        return [json.loads(call.args[0]) for call in calls]

    def queue(self, *payloads, binary=False):
        frames = [json.dumps(payload) for payload in payloads]
        if binary:
            frames = [frame.encode("utf-8") for frame in frames]
        self.socket.recv.side_effect = frames
        kind = aiohttp.WSMsgType.BINARY if binary else aiohttp.WSMsgType.TEXT
        self.socket.receive.side_effect = [_message(kind, frame) for frame in frames]

    def raw(self, frame):
        self.socket.recv.return_value = frame
        kind = aiohttp.WSMsgType.BINARY if isinstance(frame, (bytes, bytearray)) else aiohttp.WSMsgType.TEXT
        self.socket.receive.return_value = _message(kind, frame)

    def assert_closed_once(self):
        if self.is_async:
            self.socket.close.assert_awaited_once()
            self.session.close.assert_awaited_once()
            assert self.session.closed is True
        else:
            self.socket.close.assert_called_once()
        assert self.socket.closed is True


class _LiveHarness:
    def __init__(self, is_async):
        self.is_async = is_async
        self.credential = _AsyncFakeCredential() if is_async else _FakeCredential()
        self.transport = _Transport(is_async)
        self.connect = Mock(return_value=self.transport.socket)
        self.session_factory = Mock(return_value=self.transport.session)
        self.clients = []
        self.client = self.new_client(allow_preview=True)

    def new_client(self, **options):
        options.setdefault("endpoint", _ENDPOINT)
        options.setdefault("credential", self.credential)
        client_type = AsyncAIProjectClient if self.is_async else AIProjectClient
        client = client_type(**options)
        self.clients.append(client)
        return client

    @property
    def live(self):
        return self.client.beta.voice_agents.live

    @property
    def handshake(self):
        call = self.transport.session.ws_connect.await_args if self.is_async else self.connect.call_args
        assert call is not None
        return call.args[0], call.kwargs

    @property
    def headers(self):
        return self.handshake[1]["headers" if self.is_async else "additional_headers"]

    def manager(self, *, protocol="live", **options):
        options.setdefault("agent_name", _AGENT)
        return getattr(self.client.beta.voice_agents, protocol).connect(**options)

    async def call(self, method, *args, **kwargs):
        result = method(*args, **kwargs)
        return await result if self.is_async else result

    async def exit(self, manager):
        method = manager.__aexit__ if self.is_async else manager.__exit__
        await self.call(method, None, None, None)

    async def collect(self, connection):
        if self.is_async:
            return [event async for event in connection]
        return list(connection)

    @asynccontextmanager
    async def open(self, *, protocol="live", **options):
        manager = self.manager(protocol=protocol, **options)
        if self.is_async:
            async with manager as connection:
                yield connection
        else:
            with manager as connection:
                yield connection


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def is_async(request):
    return request.param


@pytest_asyncio.fixture
async def live(is_async, monkeypatch):
    harness = _LiveHarness(is_async)
    monkeypatch.setattr("websockets.sync.client.connect", harness.connect)
    monkeypatch.setattr("aiohttp.ClientSession", harness.session_factory)
    try:
        yield harness
    finally:
        for client in reversed(harness.clients):
            await harness.call(client.close)


async def test_live_is_public_and_connect_is_lazy(live):
    public_operations = async_operations if live.is_async else operations
    prefix = "Async" if live.is_async else ""
    assert isinstance(live.live, getattr(public_operations, f"{prefix}BetaLive"))
    assert live.live is live.client.beta.voice_agents.live
    assert live.live is not live.client.beta.voice_agents.realtime
    assert tuple(inspect.signature(type(live.live).__init__).parameters) == ("self", "args", "kwargs")

    manager = live.manager()
    assert isinstance(manager, getattr(public_operations, f"{prefix}BetaLiveConnectionManager"))
    assert live.credential.calls == []
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()

    connection = await live.call(manager.enter)
    try:
        assert isinstance(connection, getattr(public_operations, f"{prefix}BetaLiveConnection"))
        assert connection.closed is False
        assert "open" in repr(connection)
        live.transport.writes.assert_not_called()
    finally:
        await live.exit(manager)
    live.transport.assert_closed_once()
    assert "closed" in repr(connection)


async def test_connect_signature_has_only_live_options(live):
    parameters = inspect.signature(live.live.connect).parameters
    assert tuple(parameters) == (
        "agent_name",
        "agent_version",
        "structured_inputs",
        "store",
        "connection_url",
        "api_version",
        "credential_scopes",
        "extra_query",
        "extra_headers",
        "kwargs",
    )
    assert parameters["agent_name"].default is inspect.Parameter.empty
    for name, parameter in parameters.items():
        if name == "kwargs":
            assert parameter.kind is inspect.Parameter.VAR_KEYWORD
        else:
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
            if name != "agent_name":
                assert parameter.default is None
    assert "model" not in parameters
    assert "transport" not in parameters
    assert models.LiveServerEvent.__mapping__


@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("member", ["enter", "recv", "send", "iterator"])
async def test_public_websocket_signatures_have_concrete_type_hints(is_async, protocol, member):
    public_operations = async_operations if is_async else operations
    prefix = f"{'Async' if is_async else ''}Beta{protocol.capitalize()}"
    connection_type = getattr(public_operations, f"{prefix}Connection")
    manager_type = getattr(public_operations, f"{prefix}ConnectionManager")
    client_event = getattr(public_operations, "LiveClientEvent" if protocol == "live" else "ClientEvent")
    server_event = getattr(public_operations, "LiveServerEvent" if protocol == "live" else "ServerEvent")
    owner = manager_type if member == "enter" else connection_type
    method_name = ("__aiter__" if is_async else "__iter__") if member == "iterator" else member
    method = getattr(owner, method_name)
    parameters = inspect.signature(method).parameters
    hints = get_type_hints(method)

    assert hints, f"{owner.__name__}.{method_name} must retain public annotations"
    assert not any(
        _contains_type_variable(annotation) for annotation in hints.values()
    ), f"{owner.__name__}.{method_name} exposes unresolved generic type variables"
    assert "return" in hints

    if member == "enter":
        assert tuple(parameters) == ("self",)
        assert hints == {"return": connection_type}
    elif member == "recv":
        assert hints["return"] == server_event
        if is_async:
            assert tuple(parameters) == ("self",)
            assert set(hints) == {"return"}
        else:
            assert tuple(parameters) == ("self", "timeout")
            assert parameters["timeout"].kind is inspect.Parameter.KEYWORD_ONLY
            assert parameters["timeout"].default is None
            assert hints["timeout"] == Optional[float]
            assert set(hints) == {"timeout", "return"}
    elif member == "send":
        assert tuple(parameters) == ("self", "event")
        assert parameters["event"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameters["event"].default is inspect.Parameter.empty
        assert hints == {"event": client_event, "return": type(None)}
    else:
        assert tuple(parameters) == ("self",)
        assert set(hints) == {"return"}
        assert get_origin(hints["return"]) is (AsyncIterator if is_async else Iterator)
        assert get_args(hints["return"]) == (server_event,)


@pytest.mark.parametrize("preview", [None, False], ids=["default", "false"])
async def test_beta_namespace_implies_preview_opt_in_without_allow_preview(live, preview):
    options = {} if preview is None else {"allow_preview": preview}
    client = live.new_client(**options)
    manager = client.beta.voice_agents.live.connect(agent_name=_AGENT)
    assert live.credential.calls == []
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()

    connection = await live.call(manager.enter)
    try:
        assert connection.closed is False
        assert live.headers["Foundry-Features"] == "VoiceAgents=V1Preview"
        assert live.headers["Authorization"] == f"Bearer {_TOKEN}"
        assert live.credential.calls == [(_SCOPES, {})]
        live.transport.writes.assert_not_called()
        if live.is_async:
            live.transport.session.ws_connect.assert_awaited_once()
        else:
            live.connect.assert_called_once()
    finally:
        await live.exit(manager)
    live.transport.assert_closed_once()


@pytest.mark.parametrize("mapping_type", [dict, MappingProxyType, UserDict])
async def test_handshake_encodes_live_route_authentication_and_all_options(live, mapping_type):
    structured_inputs = mapping_type({"name": "Zoë / guest", "count": 0, "enabled": False, "optional": None})
    extra_query = MappingProxyType({"custom": "space + /?&=#"})
    extra_headers = MappingProxyType({"X-Custom": "example"})
    options = {"heartbeat": 3, "max_msg_size": 1024} if live.is_async else {"open_timeout": 3, "max_size": 1024}
    scopes = ["https://scope-one.example/.default", "https://scope-two.example/.default"]
    async with live.open(
        agent_name="name /?#% 雪",
        agent_version="7",
        structured_inputs=structured_inputs,
        store=False,
        api_version="live-test-version",
        credential_scopes=scopes,
        extra_query=extra_query,
        extra_headers=extra_headers,
        **options,
    ):
        url, kwargs = live.handshake
        assert urlsplit(url).path == (
            "/api/projects/fake-project/agents/name%20%2F%3F%23%25%20%E9%9B%AA"
            "/endpoint/protocols/voice/live/sessions"
        )
        assert urlsplit(url).scheme == "wss"
        assert urlsplit(url).netloc == _HOST
        query = _handshake_query(url, kwargs)
        user_agent = live.headers["User-Agent"]
        assert f"azsdk-python-ai-projects/{__version__}" in user_agent
        assert query == {
            "api-version": ["live-test-version"],
            "x-ms-client-sdk": [user_agent],
            "x-agent-version-override": ["7"],
            "structured_inputs": [query["structured_inputs"][0]],
            "store": ["false"],
            "custom": ["space + /?&=#"],
        }
        assert json.loads(query["structured_inputs"][0]) == structured_inputs
        assert live.headers == {
            "Authorization": f"Bearer {_TOKEN}",
            "Foundry-Features": "VoiceAgents=V1Preview",
            "User-Agent": user_agent,
            "X-Custom": "example",
        }
        assert live.credential.calls == [(tuple(scopes), {})]
        assert all(kwargs[name] == value for name, value in options.items())
        assert not kwargs.get("protocols" if live.is_async else "subprotocols")
        assert "Sec-WebSocket-Protocol" not in live.headers
        assert "model" not in query
        assert "transport" not in query
        assert "model" not in kwargs
        assert "transport" not in kwargs
        if not live.is_async:
            assert kwargs["user_agent_header"] is None
        live.transport.writes.assert_not_called()
    assert dict(extra_query) == {"custom": "space + /?&=#"}
    assert dict(extra_headers) == {"X-Custom": "example"}
    assert structured_inputs == {"name": "Zoë / guest", "count": 0, "enabled": False, "optional": None}
    live.transport.assert_closed_once()


async def test_defaults_do_not_add_model_transport_startup_or_optional_query(live):
    async with live.open():
        url, kwargs = live.handshake
        assert urlsplit(url).path.endswith(f"/agents/{_AGENT}/endpoint/protocols/voice/live/sessions")
        assert set(_handshake_query(url, kwargs)) == {"api-version", "x-ms-client-sdk"}
        assert live.credential.calls == [(_SCOPES, {})]
        assert not kwargs.get("protocols" if live.is_async else "subprotocols")
        live.transport.writes.assert_not_called()


@pytest.mark.parametrize("header_name", ["User-Agent", "user-agent", "uSeR-aGeNt"])
async def test_caller_user_agent_is_respected_case_insensitively(live, header_name):
    headers = {header_name: "custom-test-client"}
    async with live.open(extra_headers=headers):
        matching = [(name, value) for name, value in live.headers.items() if name.lower() == "user-agent"]
        assert matching == [(header_name, "custom-test-client")]
        query = _handshake_query(*live.handshake)
        assert f"azsdk-python-ai-projects/{__version__}" in query["x-ms-client-sdk"][0]
    assert headers == {header_name: "custom-test-client"}


@pytest.mark.parametrize("authority", [_HOST, f"{_HOST.upper()}:443"])
async def test_same_origin_override_preserves_opaque_query_and_caller_mappings(live, authority):
    override = (
        f"wss://{authority}/custom/live" "?sig=opaque%2fsignature%2Bvalue%3D&keep=one&keep=two&empty=&path=folder%2F"
    )
    query = {"custom": "space + /?&=#"}
    headers = {"X-Custom": "unchanged"}
    async with live.open(connection_url=override, extra_query=query, extra_headers=headers):
        url, kwargs = live.handshake
        assert url == override if live.is_async else url.startswith(override + "&")
        parsed = _handshake_query(url, kwargs)
        assert parsed["sig"] == ["opaque/signature+value="]
        assert parsed["keep"] == ["one", "two"]
        assert parsed["empty"] == [""]
        assert parsed["path"] == ["folder/"]
        assert parsed["custom"] == ["space + /?&=#"]
        assert url.count("?") == 1
        assert "sig=opaque%2fsignature%2Bvalue%3D" in url
        assert "path=folder%2F" in url
    assert query == {"custom": "space + /?&=#"}
    assert headers == {"X-Custom": "unchanged"}


@pytest.mark.parametrize(
    "override",
    [
        "wss://untrusted.example/custom",
        f"wss://{_HOST}:8443/custom",
        f"ws://{_HOST}/custom",
        f"ws://{_HOST}:443/custom",
        f"https://{_HOST}/custom",
        f"http://{_HOST}:443/custom",
        f"wss://{_HOST}:invalid/custom",
        "not-a-url",
        "",
    ],
)
async def test_invalid_override_fails_before_token_or_transport(live, override):
    manager = live.manager(connection_url=override)
    with pytest.raises(ValueError):
        await live.call(manager.enter)
    assert live.credential.calls == []
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()


@pytest.mark.parametrize("endpoint", [f"http://{_HOST}/project", f"ftp://{_HOST}/project"])
async def test_insecure_computed_endpoint_fails_before_token_or_transport(live, endpoint):
    client = live.new_client(endpoint=endpoint, allow_preview=True)
    manager = client.beta.voice_agents.live.connect(agent_name=_AGENT)
    with pytest.raises(ValueError, match="wss"):
        await live.call(manager.enter)
    assert live.credential.calls == []
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()


@pytest.mark.parametrize(
    "structured_inputs,extra_query",
    [
        ({"name": "guest"}, {"structured_input": "{}"}),
        (None, {"structured_inputs": "{}", "structured_input": "{}"}),
        ({}, {"structured_inputs": "{}", "structured_input": "{}"}),
    ],
)
async def test_structured_input_spellings_are_mutually_exclusive_before_auth(live, structured_inputs, extra_query):
    manager = live.manager(structured_inputs=structured_inputs, extra_query=extra_query)
    with pytest.raises(ValueError, match="structured_input.*structured_inputs"):
        await live.call(manager.enter)
    assert live.credential.calls == []
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()
    assert "structured_input" in extra_query


@pytest.mark.parametrize("name", ["structured_input", "structured_inputs"])
async def test_one_explicit_structured_input_query_spelling_is_preserved(live, name):
    query = {name: '{"name": "guest"}'}
    async with live.open(extra_query=query):
        values = _handshake_query(*live.handshake)
        assert values[name] == ['{"name": "guest"}']
        assert ("structured_inputs" if name == "structured_input" else "structured_input") not in values
    assert query == {name: '{"name": "guest"}'}


@pytest.mark.parametrize("store", [True, False])
async def test_typed_query_options_override_extra_query_without_mutating_it(live, store):
    extra_query = {
        "x-agent-version-override": "old-version",
        "structured_inputs": '{"old":true}',
        "store": "old-store",
    }
    async with live.open(agent_version="8", structured_inputs={}, store=store, extra_query=extra_query):
        query = _handshake_query(*live.handshake)
        assert query["x-agent-version-override"] == ["8"]
        assert query["structured_inputs"] == ["{}"]
        assert query["store"] == [str(store).lower()]
    assert extra_query == {
        "x-agent-version-override": "old-version",
        "structured_inputs": '{"old":true}',
        "store": "old-store",
    }


async def test_manager_snapshots_extra_query_and_headers(live):
    extra_query = {"custom": "original"}
    extra_headers = {"X-Custom": "original"}
    manager = live.manager(extra_query=extra_query, extra_headers=extra_headers)
    extra_query["custom"] = "changed"
    extra_headers["X-Custom"] = "changed"
    await live.call(manager.enter)
    try:
        assert _handshake_query(*live.handshake)["custom"] == ["original"]
        assert live.headers["X-Custom"] == "original"
    finally:
        await live.exit(manager)


async def test_optional_dependency_is_only_required_on_enter(live):
    modules = {"aiohttp": None} if live.is_async else {"websockets.sync.client": None, "websockets.typing": None}
    dependency = "aiohttp" if live.is_async else "websockets"
    with patch.dict("sys.modules", modules):
        client = live.new_client(allow_preview=True)
        manager = client.beta.voice_agents.live.connect(agent_name=_AGENT)
        assert live.credential.calls == []
        with pytest.raises(RuntimeError, match=f"pip install {dependency}") as caught:
            await live.call(manager.enter)
        assert "live" in str(caught.value).lower()
        assert "realtime" not in str(caught.value).lower()
    live.connect.assert_not_called()
    live.session_factory.assert_not_called()
    assert live.credential.calls == []


async def test_token_failure_propagates_without_opening_websocket_or_leaking_session(live):
    failure = RuntimeError("fake credential rejected the scope")
    live.credential.failure = failure
    with pytest.raises(RuntimeError) as caught:
        await live.call(live.manager().enter)
    assert caught.value is failure
    assert live.credential.calls == [(_SCOPES, {})]
    live.connect.assert_not_called()
    if live.is_async:
        live.transport.session.ws_connect.assert_not_awaited()
        assert live.session_factory.call_count <= 1
        assert live.transport.session.close.await_count == live.session_factory.call_count
    else:
        live.session_factory.assert_not_called()


@pytest.mark.parametrize(
    "failure,expected",
    [
        (OSError("upgrade refused"), ConnectionError),
        (ValueError("invalid websocket option"), ValueError),
        (RuntimeError("websocket already closing"), RuntimeError),
    ],
)
async def test_handshake_errors_preserve_causes_and_release_owned_resources(live, failure, expected):
    connector = live.transport.session.ws_connect if live.is_async else live.connect
    connector.side_effect = failure
    manager = live.manager()
    with pytest.raises(expected) as caught:
        await live.call(manager.enter)
    if expected is ConnectionError:
        assert caught.value.__cause__ is failure
        assert _AGENT in str(caught.value)
        assert "live" in str(caught.value).lower()
        assert "realtime" not in str(caught.value).lower()
    else:
        assert caught.value is failure
    if live.is_async:
        live.transport.session.close.assert_awaited_once()
        live.transport.socket.close.assert_not_awaited()
    await live.exit(manager)
    await live.exit(manager)
    if live.is_async:
        live.transport.session.close.assert_awaited_once()


async def test_live_does_not_negotiate_realtime_even_with_caller_protocol_override(live):
    option = "protocols" if live.is_async else "subprotocols"
    async with live.open(**{option: ["realtime"]}):
        assert not live.handshake[1].get(option)
        assert "Sec-WebSocket-Protocol" not in live.headers


@pytest.mark.parametrize("kind", ["model", "mapping", "mapping_proxy", "user_dict", "json"])
async def test_raw_send_supports_generated_model_mapping_and_exact_json(live, kind):
    expected = {"type": "response.create", "event_id": "evt-response"}
    raw = '{ "type": "response.create", "event_id": "evt-response" }'
    event = {
        "model": models.LiveClientEventLiveResponseCreateParam(event_id="evt-response"),
        "mapping": expected,
        "mapping_proxy": MappingProxyType(expected),
        "user_dict": UserDict(expected),
        "json": raw,
    }[kind]
    async with live.open() as connection:
        await live.call(connection.send, event)
        assert live.transport.sent == [expected]
        if kind == "json":
            live.transport.writes.assert_called_once_with(raw)
        assert expected == {"type": "response.create", "event_id": "evt-response"}


async def test_generated_session_start_is_available_only_when_explicitly_sent(live):
    event = models.LiveSessionStartEvent(
        session=models.LiveSessionCreateParams(model="gpt-live-1", store=False),
        event_id="evt-raw-start",
    )
    async with live.open() as connection:
        live.transport.writes.assert_not_called()
        await live.call(connection.send, event)
        assert live.transport.sent == [
            {
                "type": "session.start",
                "event_id": "evt-raw-start",
                "session": {"model": "gpt-live-1", "store": False},
            }
        ]


@pytest.mark.parametrize("raw", ["not-json", '{"type":', ""])
async def test_invalid_outgoing_json_never_reaches_socket(live, raw):
    async with live.open() as connection:
        with pytest.raises(ValueError, match="not valid JSON"):
            await live.call(connection.send, raw)
        live.transport.writes.assert_not_called()
        assert connection.closed is False


@pytest.mark.parametrize("raw", ["null", "[]", '"future-value"', "true", "42", '{"type":[]}'])
async def test_valid_json_values_match_realtime_pass_through_behavior(live, raw):
    async with live.open() as connection:
        await live.call(connection.send, raw)
        live.transport.writes.assert_called_once_with(raw)
        assert live.transport.sent == [json.loads(raw)]
        assert connection.closed is False


async def test_unserializable_mapping_is_rejected_before_socket_write(live):
    async with live.open() as connection:
        with pytest.raises(TypeError):
            await live.call(connection.send, {"type": "response.create", "future": object()})
        live.transport.writes.assert_not_called()
        assert connection.closed is False


@pytest.mark.parametrize("audio", [b"\x00\x01\xfe\xff", "AAH+/w==", b"", ""])
@pytest.mark.parametrize("event_id", [None, "evt-audio"])
async def test_input_audio_append_encodes_bytes_once_and_preserves_base64(live, audio, event_id):
    expected = {
        "type": "session.input_audio.append",
        "audio": base64.b64encode(audio).decode("ascii") if isinstance(audio, bytes) else audio,
    }
    if event_id is not None:
        expected["event_id"] = event_id
    async with live.open() as connection:
        await live.call(connection.session.input_audio.append, audio=audio, event_id=event_id)
        assert live.transport.sent == [expected]


async def test_input_audio_mute_and_unmute_emit_only_live_commands(live):
    async with live.open() as connection:
        await live.call(connection.session.input_audio.mute, event_id="evt-mute")
        await live.call(connection.session.input_audio.unmute)
        assert live.transport.sent == [
            {"type": "session.input_audio.mute", "event_id": "evt-mute"},
            {"type": "session.input_audio.unmute"},
        ]


@pytest.mark.parametrize("resource", ["instructions", "thinking", "commentary"])
@pytest.mark.parametrize("delegation_id", [None, "delegation-test"])
@pytest.mark.parametrize("event_id", [None, "evt-text"])
async def test_text_append_preserves_required_nullable_delegation_on_wire(live, resource, delegation_id, event_id):
    expected = {
        "type": f"session.{resource}.append",
        "content": "Context for the Live model.",
        "delegation_id": delegation_id,
    }
    if event_id is not None:
        expected["event_id"] = event_id
    async with live.open() as connection:
        await live.call(
            getattr(connection.session, resource).append,
            content="Context for the Live model.",
            delegation_id=delegation_id,
            event_id=event_id,
        )
        assert live.transport.sent == [expected]
        assert "delegation_id" in live.transport.sent[0]


@pytest.mark.parametrize("resource", ["instructions", "thinking", "commentary"])
async def test_text_append_cannot_omit_delegation_id(live, resource):
    async with live.open() as connection:
        append = getattr(connection.session, resource).append
        parameter = inspect.signature(append).parameters["delegation_id"]
        assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
        assert parameter.default is inspect.Parameter.empty
        with pytest.raises(TypeError, match="delegation_id"):
            await live.call(append, content="Context without a delegation argument")
        live.transport.writes.assert_not_called()


@pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
async def test_session_update_serializes_sparse_delegation_settings(live, typed):
    settings = {
        "delegation": {
            "type": "responses",
            "responses": {
                "instructions": "Answer concisely.",
                "parallel_tool_calls": False,
                "max_output_tokens": 32,
            },
        }
    }
    session = models.LiveSessionUpdateParams(settings) if typed else settings
    async with live.open() as connection:
        await live.call(connection.session.update, session=session, event_id="evt-update")
        assert live.transport.sent == [{"type": "session.update", "event_id": "evt-update", "session": settings}]
    assert "model" not in settings
    assert "audio" not in settings


@pytest.mark.parametrize(
    "item",
    [
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Check this itinerary."}],
        },
        {
            "type": "function_call_output",
            "call_id": "call-test",
            "output": '{"available":false,"count":0}',
        },
    ],
    ids=["message", "function-result"],
)
async def test_response_item_create_preserves_responses_item_mapping(live, item):
    expected = json.loads(json.dumps(item))
    async with live.open() as connection:
        await live.call(connection.response.item.create, item=MappingProxyType(item), event_id="evt-item")
        assert live.transport.sent == [{"type": "response.item.create", "event_id": "evt-item", "item": expected}]
    assert item == expected


@pytest.mark.parametrize("event_id", [None, "evt-create"])
async def test_response_create_has_only_event_id_and_no_cancel_helper(live, event_id):
    async with live.open() as connection:
        assert tuple(inspect.signature(connection.response.create).parameters) == ("event_id",)
        assert not hasattr(connection.response, "cancel")
        await live.call(connection.response.create, event_id=event_id)
        expected = {"type": "response.create"}
        if event_id is not None:
            expected["event_id"] = event_id
        assert live.transport.sent == [expected]


async def test_session_close_requests_shutdown_without_closing_transport(live):
    live.transport.queue(_STARTED, _CLOSED)
    async with live.open() as connection:
        started = await live.call(connection.recv)
        assert isinstance(started, models.LiveServerEventLiveSessionStarted)
        assert isinstance(started.session, models.VoiceAgentLiveSessionResource)
        assert started.session.id == "live-session-test"
        assert isinstance(started.session.delegation, Mapping)
        assert started.session.delegation["type"] == "client"
        assert started.as_dict() == _STARTED
        await live.call(connection.session.close, event_id="evt-close")
        assert live.transport.sent == [{"type": "session.close", "event_id": "evt-close"}]
        assert connection.closed is False
        live.transport.socket.close.assert_not_called()
        closed = await live.call(connection.recv)
        assert isinstance(closed, models.LiveServerEventLiveSessionClosed)
        assert closed.reason == "close_requested"
        assert closed.client_event_id == "evt-close"
        assert closed.session.status == "active"
        assert isinstance(closed.usage, models.LiveSessionUsage)
        assert closed.usage.seconds == 1.25
        assert closed.as_dict() == _CLOSED
        assert connection.closed is False
        live.transport.socket.close.assert_not_called()
    live.transport.assert_closed_once()


@pytest.mark.parametrize("invalid", [None, "not-a-model", 42, object, models.LiveServerEvent({"type": "future.event"})])
async def test_live_event_registry_accepts_only_model_classes(invalid):
    registry = {"session.started": models.LiveServerEventLiveSessionStarted, "invalid": invalid}

    assert _server_event_types(registry) == {"session.started": models.LiveServerEventLiveSessionStarted}


@pytest.mark.parametrize(
    "event_type,event_model",
    list(models.LiveServerEvent.__mapping__.items()),
    ids=list(models.LiveServerEvent.__mapping__),
)
async def test_every_generated_live_server_event_is_dispatched(live, event_type, event_model):
    payload = {"type": event_type, "event_id": "evt-dispatch", "future_field": {"enabled": False}}
    live.transport.queue(payload)
    async with live.open() as connection:
        event = await live.call(connection.recv)
        assert type(event) is event_model
        assert isinstance(event, models.LiveServerEvent)
        assert event.type == event_type
        assert event.as_dict() == payload


@pytest.mark.parametrize("frame_type", [bytes, bytearray], ids=["bytes", "bytearray"])
async def test_binary_json_audio_event_uses_generated_base64_string_field(live, frame_type):
    payload = {"type": "session.output_audio.delta", "delta": "AAH+/w==", "start_ms": 0, "end_ms": 20}
    live.transport.raw(frame_type(json.dumps(payload).encode("utf-8")))
    async with live.open() as connection:
        event = await live.call(connection.recv)
        assert isinstance(event, models.LiveOutputAudioDelta)
        assert isinstance(event.delta, str)
        assert base64.b64decode(event.delta) == b"\x00\x01\xfe\xff"
        assert (event.start_ms, event.end_ms) == (0, 20)
        assert event.as_dict() == payload


async def test_reflected_audio_and_transcript_fields_are_not_realtime_aliases(live):
    reflected = {"type": "session.input_audio.append", "audio": "AAH+/w=="}
    transcript = {
        "type": "session.output_transcript.delta",
        "event_id": "evt-transcript",
        "client_event_id": "evt-client",
        "delta": "A synthetic transcript.",
        "start_ms": 5,
        "end_ms": 15,
    }
    live.transport.queue(reflected, transcript)
    async with live.open() as connection:
        audio = await live.call(connection.recv)
        text = await live.call(connection.recv)
        assert isinstance(audio, models.LiveInputAudioAppend)
        assert audio.audio == "AAH+/w=="
        assert isinstance(text, models.LiveServerEventLiveOutputTranscriptDelta)
        assert text.delta == "A synthetic transcript."
        assert (text.start_ms, text.end_ms) == (5, 15)
        assert audio.as_dict() == reflected
        assert text.as_dict() == transcript


async def test_delegation_and_wrapped_responses_events_retain_full_wire_shape(live):
    delegation = {
        "type": "session.delegation.created",
        "event_id": "evt-delegation",
        "offset_ms": 20,
        "delegation": {
            "id": "delegation-test",
            "type": "delegation",
            "target": "responses",
            "response_id": "response-test",
        },
    }
    response = {
        "type": "response.event",
        "event_id": "evt-response-event",
        "client_event_id": "evt-response-create",
        "delegation_id": "delegation-test",
        "event": {
            "type": "response.function_call_arguments.done",
            "call_id": "call-test",
            "arguments": '{"city":"Seattle"}',
            "future": {"preserved": True},
        },
    }
    live.transport.queue(delegation, response)
    async with live.open() as connection:
        created = await live.call(connection.recv)
        wrapped = await live.call(connection.recv)
        assert isinstance(created, models.LiveServerEventLiveDelegationCreated)
        assert isinstance(created.delegation, models.VoiceAgentLiveDelegationItem)
        assert created.delegation.id == "delegation-test"
        assert created.delegation.response_id == "response-test"
        assert isinstance(wrapped, models.LiveServerEventLiveResponseEvent)
        assert wrapped.delegation_id == "delegation-test"
        assert wrapped.event == response["event"]
        assert created.as_dict() == delegation
        assert wrapped.as_dict() == response


async def test_foundry_managed_ownership_survives_public_live_event_parsing(live):
    owner = {
        "type": "foundry_managed_agent",
        "agent_name": "prompt-agent-test",
        "agent_version": "7",
    }
    session = dict(_SESSION, delegation=owner)
    payloads = [
        dict(_STARTED, session=session, conversation_id="conversation-test"),
        {"type": "session.updated", "event_id": "evt-updated", "session": session},
        {
            "type": "session.delegation.created",
            "event_id": "evt-delegation",
            "offset_ms": 20,
            "delegation": {
                "type": "delegation",
                "id": "delegation-test",
                "target": "foundry_managed_agent",
            },
        },
        dict(_CLOSED, session=session),
    ]
    event_models = [
        models.LiveServerEventLiveSessionStarted,
        models.LiveServerEventLiveSessionUpdated,
        models.LiveServerEventLiveDelegationCreated,
        models.LiveServerEventLiveSessionClosed,
    ]
    live.transport.queue(*payloads)

    async with live.open() as connection:
        for payload, event_model in zip(payloads, event_models):
            event = await live.call(connection.recv)
            assert isinstance(event, event_model)
            if isinstance(event, models.LiveServerEventLiveDelegationCreated):
                assert isinstance(event.delegation, models.VoiceAgentLiveDelegationItem)
                assert event.delegation.target == "foundry_managed_agent"
            else:
                assert isinstance(
                    event,
                    (
                        models.LiveServerEventLiveSessionStarted,
                        models.LiveServerEventLiveSessionUpdated,
                        models.LiveServerEventLiveSessionClosed,
                    ),
                )
                assert isinstance(event.session, models.VoiceAgentLiveSessionResource)
                assert isinstance(event.session.delegation, Mapping)
                assert dict(event.session.delegation) == owner
            assert event.as_dict() == payload
    live.transport.assert_closed_once()


@pytest.mark.parametrize("event_type", ["future.live.event", None, 1, False, [], {}])
async def test_unknown_or_non_string_event_type_returns_unchanged_mapping(live, event_type):
    payload = {"type": event_type, "future": {"text": "preserved", "optional": None}}
    live.transport.queue(payload, {"future": ["missing", "type"]})
    async with live.open() as connection:
        assert await live.call(connection.recv) == payload
        assert await live.call(connection.recv) == {"future": ["missing", "type"]}
        assert connection.closed is False


async def test_server_error_is_returned_as_typed_error_not_success_or_swallowed(live):
    payload = {
        "type": "error",
        "event_id": "evt-server-error",
        "client_event_id": "evt-request",
        "error": {
            "type": "invalid_request_error",
            "code": "invalid_delegation",
            "message": "The delegation does not exist.",
            "param": "delegation_id",
            "client_event_id": "evt-request",
        },
    }
    live.transport.queue(payload, _STARTED)
    async with live.open() as connection:
        event = await live.call(connection.recv)
        assert isinstance(event, models.LiveServerEventLiveErrorEvent)
        assert isinstance(event.error, models.LiveLiveError)
        assert event.error.code == "invalid_delegation"
        assert event.error.message == "The delegation does not exist."
        assert event.client_event_id == "evt-request"
        assert event.as_dict() == payload
        assert connection.closed is False
        assert isinstance(await live.call(connection.recv), models.LiveServerEventLiveSessionStarted)


@pytest.mark.parametrize("raw,exception", [("{invalid", ValueError), (b"\xff", UnicodeDecodeError)])
async def test_invalid_incoming_frame_is_not_replaced_with_success(live, raw, exception):
    live.transport.raw(raw)
    async with live.open() as connection:
        with pytest.raises(exception):
            await live.call(connection.recv)
        assert connection.closed is False
        live.transport.writes.assert_not_called()
    live.transport.assert_closed_once()


@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("payload", [None, [], [{"type": "session.started"}], "session.started", 0, True])
@pytest.mark.parametrize("binary", [False, True], ids=["text", "binary"])
async def test_incoming_non_object_json_raises_value_error_without_poisoning_connection(
    live, protocol, payload, binary
):
    next_payload = _STARTED if protocol == "live" else {"type": "session.created", "session": {}}
    live.transport.queue(payload, next_payload, binary=binary)
    async with live.open(protocol=protocol) as connection:
        with pytest.raises(ValueError):
            await live.call(connection.recv)
        assert connection.closed is False
        live.transport.socket.close.assert_not_called()
        event = await live.call(connection.recv)
        expected_type = (
            models.LiveServerEventLiveSessionStarted if protocol == "live" else models.RealtimeServerEventSessionCreated
        )
        assert isinstance(event, expected_type)
        assert event.as_dict() == next_payload
        live.transport.writes.assert_not_called()
    live.transport.assert_closed_once()


@pytest.mark.parametrize("fail_in_body", [False, True], ids=["normal", "exception"])
async def test_context_manager_releases_transport_and_preserves_body_exception(live, fail_in_body):
    failure = RuntimeError("application failed")
    try:
        async with live.open() as connection:
            if fail_in_body:
                raise failure
    except RuntimeError as caught:
        assert fail_in_body
        assert caught is failure
    else:
        assert not fail_in_body
    assert connection.closed is True
    live.transport.assert_closed_once()


async def test_explicit_close_is_idempotent_and_forwards_code_and_reason(live):
    manager = live.manager()
    connection = await live.call(manager.enter)
    try:
        await live.call(connection.close, code=1001, reason="finished ✓")
        assert connection.closed is True
        await live.call(connection.close)
    finally:
        await live.exit(manager)
        await live.exit(manager)
    live.transport.assert_closed_once()
    expected = {"code": 1001}
    expected["message" if live.is_async else "reason"] = "finished ✓".encode("utf-8") if live.is_async else "finished ✓"
    live.transport.socket.close.assert_called_once_with(**expected)
    live.transport.writes.assert_not_called()


async def test_connection_itself_is_a_context_manager(live):
    manager = live.manager()
    connection = await live.call(manager.enter)
    try:
        if live.is_async:
            async with connection as entered:
                assert entered is connection
        else:
            with connection as entered:
                assert entered is connection
        assert connection.closed is True
    finally:
        await live.exit(manager)
    live.transport.assert_closed_once()


@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_task_cancellation_inside_connection_context_releases_resources(live, protocol):
    entered = asyncio.Event()
    block = asyncio.Event()

    async def use_connection():
        async with live.open(protocol=protocol):
            entered.set()
            await block.wait()

    task = asyncio.create_task(use_connection())
    try:
        await asyncio.wait_for(entered.wait(), timeout=2)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    live.transport.assert_closed_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("blocked_resource", ["websocket", "http_session"])
@pytest.mark.parametrize("cancel_caller", [None, "first_close", "context_exit"])
async def test_async_close_callers_wait_for_shared_cancellation_safe_cleanup(
    live, protocol, blocked_resource, cancel_caller
):
    blocked = asyncio.Event()
    release = asyncio.Event()

    async def close_socket(**kwargs):
        if blocked_resource == "websocket":
            blocked.set()
            await release.wait()
        live.transport.socket.closed = True

    async def close_session():
        if blocked_resource == "http_session":
            blocked.set()
            await release.wait()
        live.transport.session.closed = True

    live.transport.socket.close.side_effect = close_socket
    live.transport.session.close.side_effect = close_session
    manager = live.manager(protocol=protocol)
    connection = await manager.enter()
    callers = {"first_close": asyncio.create_task(connection.close(code=1001, reason="first caller"))}
    try:
        await asyncio.wait_for(blocked.wait(), timeout=2)
        callers["second_close"] = asyncio.create_task(connection.close(code=1000, reason="second caller"))
        callers["context_exit"] = asyncio.create_task(live.exit(manager))
        callers["second_context_exit"] = asyncio.create_task(live.exit(manager))
        await asyncio.sleep(0)
        assert all(not caller.done() for caller in callers.values())
        assert live.transport.session.closed is False
        if cancel_caller is not None:
            for _ in range(2):
                callers[cancel_caller].cancel()
                await asyncio.sleep(0)
            assert all(not caller.done() for caller in callers.values())
        release.set()
        results = await asyncio.wait_for(asyncio.gather(*callers.values(), return_exceptions=True), timeout=2)
        for name, result in zip(callers, results):
            if name == cancel_caller:
                assert isinstance(result, asyncio.CancelledError)
            else:
                assert result is None
    finally:
        release.set()
        await asyncio.wait_for(asyncio.gather(*callers.values(), return_exceptions=True), timeout=2)
        await live.exit(manager)
    live.transport.assert_closed_once()
    live.transport.socket.close.assert_awaited_once_with(code=1001, message=b"first caller")
    assert manager._connection is None


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("failure_source", ["websocket", "http_session"])
async def test_async_close_failure_propagates_to_every_waiter_without_repeating_cleanup(live, protocol, failure_source):
    blocked = asyncio.Event()
    release = asyncio.Event()
    failure = OSError("offline cleanup failure")

    async def close_socket(**kwargs):
        blocked.set()
        await release.wait()
        if failure_source == "websocket":
            raise failure
        live.transport.socket.closed = True

    async def close_session():
        live.transport.session.closed = True
        if failure_source == "http_session":
            raise failure

    live.transport.socket.close.side_effect = close_socket
    live.transport.session.close.side_effect = close_session
    manager = live.manager(protocol=protocol)
    connection = await manager.enter()
    first = asyncio.create_task(connection.close())
    second = None
    context_exit = None
    try:
        await asyncio.wait_for(blocked.wait(), timeout=2)
        second = asyncio.create_task(connection.close())
        context_exit = asyncio.create_task(live.exit(manager))
        await asyncio.sleep(0)
        assert not second.done()
        assert not context_exit.done()
        release.set()
        results = await asyncio.wait_for(asyncio.gather(first, second, context_exit, return_exceptions=True), timeout=2)
        assert all(result is failure for result in results)
        await connection.close()
        await live.exit(manager)
    finally:
        release.set()
        await asyncio.wait_for(
            asyncio.gather(
                *(task for task in (first, second, context_exit) if task is not None), return_exceptions=True
            ),
            timeout=2,
        )
    live.transport.socket.close.assert_awaited_once()
    live.transport.session.close.assert_awaited_once()
    assert live.transport.session.closed is True


@pytest.mark.parametrize("is_async", [False], ids=["sync"])
async def test_sync_close_error_propagates_and_does_not_repeat_transport_cleanup(live):
    failure = OSError("fake socket close failed")
    live.transport.socket.close.side_effect = failure
    manager = live.manager()
    connection = manager.enter()
    with pytest.raises(OSError) as caught:
        connection.close()
    assert caught.value is failure
    assert connection.closed is True
    connection.close()
    await live.exit(manager)
    live.transport.socket.close.assert_called_once_with(code=1000, reason="")


@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("code", [1000, 1001])
async def test_graceful_websocket_closure_ends_iteration_for_both_protocols(live, protocol, code):
    if live.is_async:
        live.transport.socket.closed = True
        live.transport.socket.close_code = code
        live.transport.socket.receive.side_effect = [
            _message(aiohttp.WSMsgType.TEXT, json.dumps(_STARTED if protocol == "live" else {"type": "future.event"})),
            _message(aiohttp.WSMsgType.CLOSE),
        ]
    else:
        live.transport.socket.recv.side_effect = [
            json.dumps(_STARTED if protocol == "live" else {"type": "future.event"}),
            ConnectionClosedOK(Close(code, "finished"), None),
        ]
    async with live.open(protocol=protocol) as connection:
        events = await live.collect(connection)
        assert len(events) == 1
        assert events[0].type == "session.started" if protocol == "live" else events[0] == {"type": "future.event"}
        assert connection.closed is True
    if live.is_async:
        live.transport.session.close.assert_awaited_once()


@pytest.mark.parametrize("protocol", ["live", "realtime"])
@pytest.mark.parametrize("code", [1006, 1011])
async def test_abnormal_websocket_closure_is_not_silently_end_of_stream(live, protocol, code):
    if live.is_async:
        live.transport.socket.closed = True
        live.transport.socket.close_code = code
        live.transport.socket.receive.return_value = _message(aiohttp.WSMsgType.CLOSE)
    else:
        live.transport.socket.recv.side_effect = ConnectionClosedError(Close(code, "failed"), None)
    async with live.open(protocol=protocol) as connection:
        with pytest.raises(ConnectionResetError) as caught:
            await live.collect(connection)
        assert caught.value.__cause__ is not None
        assert protocol in str(caught.value).lower()
        if protocol == "live":
            assert "realtime" not in str(caught.value).lower()
        assert connection.closed is True
    if live.is_async:
        live.transport.session.close.assert_awaited_once()


@pytest.mark.parametrize("is_async", [False], ids=["sync"])
async def test_sync_receive_timeout_is_forwarded_and_does_not_close_connection(live):
    live.transport.socket.recv.side_effect = [TimeoutError("not ready"), json.dumps(_STARTED)]
    async with live.open() as connection:
        with pytest.raises(TimeoutError, match="not ready"):
            connection.recv(timeout=0.25)
        assert connection.closed is False
        assert isinstance(connection.recv(timeout=1), models.LiveServerEventLiveSessionStarted)
        assert [call.kwargs for call in live.transport.socket.recv.call_args_list] == [
            {"timeout": 0.25},
            {"timeout": 1},
        ]


async def test_write_error_propagates_and_context_still_releases_resources(live):
    failure = OSError("fake socket write failed")
    live.transport.writes.side_effect = failure
    with pytest.raises(OSError) as caught:
        async with live.open() as connection:
            await live.call(connection.response.create)
    assert caught.value is failure
    live.transport.assert_closed_once()


async def test_live_and_realtime_routes_events_and_resources_stay_independent(live):
    first = live.transport
    second = _Transport(live.is_async)
    live.connect.side_effect = [first.socket, second.socket]
    live.session_factory.side_effect = [first.session, second.session]
    first.queue(_STARTED)
    second.queue({"type": "session.created", "session": {}})
    first_manager = live.manager()
    second_manager = live.manager(protocol="realtime")
    first_connection = await live.call(first_manager.enter)
    try:
        second_connection = await live.call(second_manager.enter)
        try:
            assert isinstance(await live.call(first_connection.recv), models.LiveServerEventLiveSessionStarted)
            assert isinstance(await live.call(second_connection.recv), models.RealtimeServerEventSessionCreated)
            await live.call(first_connection.session.input_audio.mute)
            await live.call(second_connection.input_audio_buffer.commit)
            await live.call(second_connection.response.cancel, response_id="response-test")
            assert first.sent == [{"type": "session.input_audio.mute"}]
            assert second.sent == [
                {"type": "input_audio_buffer.commit"},
                {"type": "response.cancel", "response_id": "response-test"},
            ]
            await live.call(first_connection.close)
            assert first_connection.closed is True
            assert second_connection.closed is False
            assert not hasattr(first_connection, "input_audio_buffer")
            assert not hasattr(first_connection.response, "cancel")
        finally:
            await live.exit(second_manager)
    finally:
        await live.exit(first_manager)
    first.assert_closed_once()
    second.assert_closed_once()
    calls = (
        [first.session.ws_connect.await_args, second.session.ws_connect.await_args]
        if live.is_async
        else live.connect.call_args_list
    )
    assert urlsplit(calls[0].args[0]).path.endswith("/endpoint/protocols/voice/live/sessions")
    assert urlsplit(calls[1].args[0]).path.endswith("/endpoint/protocols/voice")
    option = "protocols" if live.is_async else "subprotocols"
    assert not calls[0].kwargs.get(option)
    assert list(calls[1].kwargs[option]) == ["realtime"]


async def test_sending_while_receiving_does_not_serialize_or_poison_the_other_direction(live):
    if live.is_async:
        receiving = asyncio.Event()
        release = asyncio.Event()

        async def receive():
            receiving.set()
            await release.wait()
            return _message(aiohttp.WSMsgType.TEXT, json.dumps(_STARTED))

        live.transport.socket.receive.side_effect = receive
        async with live.open() as connection:
            task = asyncio.create_task(connection.recv())
            try:
                await asyncio.wait_for(receiving.wait(), timeout=2)
                await asyncio.wait_for(connection.session.input_audio.append(audio=b"\x00\x01"), timeout=2)
                assert not task.done()
                assert live.transport.sent == [{"type": "session.input_audio.append", "audio": "AAE="}]
            finally:
                release.set()
                result = await asyncio.wait_for(task, timeout=2)
            assert isinstance(result, models.LiveServerEventLiveSessionStarted)
    else:
        receiving = threading.Event()
        release = threading.Event()

        def receive(**kwargs):
            receiving.set()
            assert release.wait(timeout=5), "The test did not release the fake receiver"
            return json.dumps(_STARTED)

        live.transport.socket.recv.side_effect = receive
        async with live.open() as connection:
            with ThreadPoolExecutor(max_workers=2) as executor:
                task = executor.submit(connection.recv)
                try:
                    assert receiving.wait(timeout=2)
                    sender = executor.submit(connection.session.input_audio.append, audio=b"\x00\x01")
                    sender.result(timeout=2)
                    assert not task.done()
                    assert live.transport.sent == [{"type": "session.input_audio.append", "audio": "AAE="}]
                finally:
                    release.set()
                assert isinstance(task.result(timeout=2), models.LiveServerEventLiveSessionStarted)
    live.transport.assert_closed_once()


async def test_logging_contains_metadata_but_never_tokens_queries_audio_or_text(live, caplog):
    synthetic_audio = base64.b64encode(b"synthetic-private-audio").decode("ascii")
    live.transport.queue({"type": "session.output_audio.delta", "delta": synthetic_audio})
    caplog.set_level(logging.DEBUG, logger="azure.ai.projects.live")
    async with live.open(
        connection_url=f"wss://{_HOST}/custom?sig=private-query",
        structured_inputs={"name": "private-structured-input"},
    ) as connection:
        await live.call(connection.session.input_audio.append, audio=synthetic_audio)
        await live.call(connection.session.thinking.append, content="private-outbound-context", delegation_id=None)
        await live.call(connection.recv)
    messages = "\n".join(record.getMessage() for record in caplog.records if record.name == "azure.ai.projects.live")
    assert f"WebSocket CONNECT target=wss://{_HOST}/custom" in messages
    assert f"WebSocket CONNECTED target=wss://{_HOST}/custom" in messages
    assert "WebSocket SEND type=session.input_audio.append bytes=" in messages
    assert "WebSocket RECEIVE type=session.output_audio.delta bytes=" in messages
    assert "WebSocket CLOSE code=1000" in messages
    for value in (_TOKEN, "private-query", "private-structured-input", "private-outbound-context", synthetic_audio):
        assert value not in messages


@pytest.mark.parametrize("is_async", [True], ids=["async"])
async def test_async_receive_ignores_ping_and_pong_frames(live):
    live.transport.socket.receive.side_effect = [
        _message(aiohttp.WSMsgType.PING, b""),
        _message(aiohttp.WSMsgType.PONG, b""),
        _message(aiohttp.WSMsgType.TEXT, json.dumps(_STARTED)),
    ]
    async with live.open() as connection:
        event = await connection.recv()
        assert isinstance(event, models.LiveServerEventLiveSessionStarted)
        assert live.transport.socket.receive.await_count == 3
    live.transport.assert_closed_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("frame_type", [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED])
async def test_async_remote_close_releases_session_even_when_socket_already_closed(live, frame_type):
    live.transport.socket.closed = True
    live.transport.socket.close_code = 1000
    live.transport.socket.receive.return_value = _message(frame_type)
    manager = live.manager()
    connection = await manager.enter()
    try:
        with pytest.raises(ConnectionResetError) as caught:
            await connection.recv()
        assert caught.value.__cause__ is None
        assert connection.closed is True
    finally:
        await live.exit(manager)
        await connection.close()
        await live.exit(manager)
    live.transport.session.close.assert_awaited_once()
    assert live.transport.session.closed is True


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_error_frame_preserves_transport_failure_and_releases_session(live, protocol):
    failure = OSError("fake websocket failed")
    live.transport.socket.exception.return_value = failure
    live.transport.socket.receive.return_value = _message(aiohttp.WSMsgType.ERROR)
    async with live.open(protocol=protocol) as connection:
        with pytest.raises(ConnectionResetError) as caught:
            await live.collect(connection)
        assert caught.value.__cause__ is failure
        assert protocol in str(caught.value).lower()
        if protocol == "live":
            assert "realtime" not in str(caught.value).lower()
    live.transport.assert_closed_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("failure", [OSError("close failed"), asyncio.CancelledError()], ids=["error", "cancellation"])
async def test_async_socket_close_failure_still_releases_session_once(live, failure):
    live.transport.socket.close.side_effect = failure
    manager = live.manager()
    connection = await manager.enter()
    with pytest.raises(type(failure)) as caught:
        await connection.close()
    assert caught.value is failure
    live.transport.session.close.assert_awaited_once()
    await connection.close()
    await live.exit(manager)
    live.transport.session.close.assert_awaited_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_concurrent_close_only_releases_each_owned_resource_once(live, protocol):
    closing = asyncio.Event()
    second_started = asyncio.Event()
    release = asyncio.Event()

    async def close_socket(**kwargs):
        closing.set()
        await release.wait()
        live.transport.socket.closed = True

    live.transport.socket.close.side_effect = close_socket
    manager = live.manager(protocol=protocol)
    connection = await manager.enter()

    async def close_again():
        second_started.set()
        await connection.close()

    first = asyncio.create_task(connection.close())
    second = None
    try:
        await asyncio.wait_for(closing.wait(), timeout=2)
        second = asyncio.create_task(close_again())
        await asyncio.wait_for(second_started.wait(), timeout=2)
    finally:
        release.set()
        tasks = [first] if second is None else [first, second]
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=2)
        await live.exit(manager)
    live.transport.assert_closed_once()
    assert connection.closed is True


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_cancellation_during_authentication_cannot_leak_session(live, protocol):
    authenticating = asyncio.Event()
    block = asyncio.Event()

    async def get_token(*scopes, **kwargs):
        live.credential.calls.append((scopes, kwargs))
        authenticating.set()
        await block.wait()
        return AccessToken(_TOKEN, 9_999_999_999)

    live.credential.get_token = get_token
    manager = live.manager(protocol=protocol)
    task = asyncio.create_task(manager.enter())
    try:
        await asyncio.wait_for(authenticating.wait(), timeout=2)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    assert live.credential.calls == [(_SCOPES, {})]
    live.transport.session.ws_connect.assert_not_awaited()
    live.transport.socket.close.assert_not_awaited()
    assert live.session_factory.call_count <= 1
    assert live.transport.session.close.await_count == live.session_factory.call_count
    await live.exit(manager)
    assert live.transport.session.close.await_count == live.session_factory.call_count


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_cancelled_handshake_releases_session_and_propagates_cancellation(live, protocol):
    entering = asyncio.Event()
    block = asyncio.Event()

    async def ws_connect(*args, **kwargs):
        entering.set()
        await block.wait()
        return live.transport.socket

    live.transport.session.ws_connect.side_effect = ws_connect
    manager = live.manager(protocol=protocol)
    task = asyncio.create_task(manager.enter())
    try:
        await asyncio.wait_for(entering.wait(), timeout=2)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    live.transport.session.close.assert_awaited_once()
    live.transport.socket.close.assert_not_awaited()
    await live.exit(manager)
    await live.exit(manager)
    live.transport.session.close.assert_awaited_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_competing_receive_failure_does_not_poison_active_receiver(live, protocol):
    receiving = asyncio.Event()
    release = asyncio.Event()
    active = False
    payload = _STARTED if protocol == "live" else {"type": "session.created", "session": {}}

    async def receive():
        nonlocal active
        if active:
            raise RuntimeError("Concurrent call to receive() is not allowed")
        active = True
        receiving.set()
        try:
            await release.wait()
        finally:
            active = False
        return _message(aiohttp.WSMsgType.TEXT, json.dumps(payload))

    live.transport.socket.receive.side_effect = receive
    async with live.open(protocol=protocol) as connection:
        task = asyncio.create_task(connection.recv())
        try:
            await asyncio.wait_for(receiving.wait(), timeout=2)
            with pytest.raises(RuntimeError, match="Concurrent call to receive"):
                await connection.recv()
            assert not task.done()
            assert connection.closed is False
            live.transport.socket.close.assert_not_awaited()
            live.transport.session.close.assert_not_awaited()
        finally:
            release.set()
            event = await asyncio.wait_for(task, timeout=2)
        assert event.type == payload["type"]
    live.transport.assert_closed_once()


@pytest.mark.parametrize("is_async", [True], ids=["async"])
@pytest.mark.parametrize("protocol", ["live", "realtime"])
async def test_async_recv_cancellation_does_not_close_socket_or_cancel_unrelated_work(live, protocol):
    receiving = asyncio.Event()
    block = asyncio.Event()
    calls = 0
    payload = _STARTED if protocol == "live" else {"type": "session.created", "session": {}}

    async def receive():
        nonlocal calls
        calls += 1
        if calls == 1:
            receiving.set()
            try:
                await block.wait()
            except asyncio.CancelledError:
                # aiohttp records 1006 on a cancelled receive without closing the socket.
                live.transport.socket.close_code = 1006
                raise
        return _message(aiohttp.WSMsgType.TEXT, json.dumps(payload))

    live.transport.socket.receive.side_effect = receive
    async with live.open(protocol=protocol) as connection:
        task = asyncio.create_task(connection.recv())
        try:
            await asyncio.wait_for(receiving.wait(), timeout=2)
            unrelated = asyncio.create_task(connection.send({"type": "future.client.command", "event_id": "evt-other"}))
        finally:
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        await asyncio.wait_for(unrelated, timeout=2)
        assert connection.closed is False
        live.transport.socket.close.assert_not_awaited()
        live.transport.session.close.assert_not_awaited()
        assert live.transport.sent == [{"type": "future.client.command", "event_id": "evt-other"}]
        event = await asyncio.wait_for(connection.recv(), timeout=2)
        expected_type = (
            models.LiveServerEventLiveSessionStarted if protocol == "live" else models.RealtimeServerEventSessionCreated
        )
        assert isinstance(event, expected_type)
        assert connection.closed is False
    live.transport.assert_closed_once()
