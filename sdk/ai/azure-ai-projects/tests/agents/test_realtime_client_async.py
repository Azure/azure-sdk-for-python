# pylint: disable=too-many-lines,line-too-long,useless-suppression,protected-access
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
"""Transport-mocked unit tests for the hand-written async realtime (WebSocket) client.

Async counterpart of ``test_realtime_client.py``. The underlying ``aiohttp.ClientSession`` is
replaced with a fake so URL construction, header/auth handling, event serialization/
deserialization, connection cleanup, and dependency/error paths can all be verified without a
live service or a recorded transport.
"""

import json
import inspect
import logging
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any, Mapping, get_args, get_type_hints
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core.credentials import AccessToken

from azure.ai.projects import models
from azure.ai.projects.aio._realtime import AsyncBetaRealtime, AsyncBetaRealtimeConnectionManager, _USER_AGENT
from azure.ai.projects.aio.operations import AsyncBetaRealtimeConnection, ServerEvent
from azure.ai.projects._version import VERSION
from azure.ai.projects.models import (
    RealtimeClientEventResponseCreate,
    RealtimeServerEventSessionCreated,
)

_ENDPOINT = "https://my-account.services.ai.azure.com/api/projects/my-project"

pytestmark = pytest.mark.asyncio


class _AsyncFakeCredential:
    """Async stub credential that returns a never-expiring token."""

    def __init__(self, token: str = "fake-token") -> None:
        self._token = token

    async def get_token(self, *args, **kwargs) -> AccessToken:  # pylint: disable=unused-argument
        return AccessToken(self._token, 9_999_999_999)


async def test_async_realtime_constructor_hides_config_in_kwargs():
    config = MagicMock()
    client = MagicMock(_config=config)

    realtime = AsyncBetaRealtime(client)

    assert realtime._config is config
    assert tuple(inspect.signature(AsyncBetaRealtime.__init__).parameters) == ("self", "args", "kwargs")


def _make_manager(**overrides) -> AsyncBetaRealtimeConnectionManager:
    kwargs = {
        "endpoint": _ENDPOINT,
        "credential": _AsyncFakeCredential(),
        "credential_scopes": ["https://ai.azure.com/.default"],
        "api_version": "v1",
        "agent_name": "my-agent",
    }
    kwargs.update(overrides)
    return AsyncBetaRealtimeConnectionManager(**kwargs)


def _make_fake_msg(msg_type, data=None):
    msg = MagicMock()
    msg.type = msg_type
    msg.data = data
    return msg


def _make_fake_ws():
    """A fake aiohttp ClientWebSocketResponse with async close() (always awaited by __aexit__)."""
    fake_ws = MagicMock()
    fake_ws.close = AsyncMock()
    return fake_ws


def _patch_client_session(fake_ws_connection):
    """Patch aiohttp.ClientSession() to return a fake session whose ws_connect/close are async."""
    fake_session = MagicMock()
    fake_session.ws_connect = AsyncMock(return_value=fake_ws_connection)
    fake_session.close = AsyncMock()
    return patch("aiohttp.ClientSession", return_value=fake_session), fake_session


@asynccontextmanager
async def _helper_connection():
    sent = []
    transport = _make_fake_ws()
    transport.send_str = AsyncMock(side_effect=lambda payload: sent.append(json.loads(payload)))
    patcher, _ = _patch_client_session(transport)
    with patcher:
        async with _make_manager() as connection:
            yield connection, sent


async def test_public_server_event_union_covers_generated_events_and_shared_error():
    expected_models = set(models.RealtimeServerEvent.__mapping__.values()) | {models.RealtimeServerEventError}

    assert set(get_args(ServerEvent)) == expected_models | {Mapping[str, Any]}
    assert get_type_hints(AsyncBetaRealtimeConnection.recv)["return"] == ServerEvent
    assert get_args(get_type_hints(AsyncBetaRealtimeConnection.__aiter__)["return"]) == (ServerEvent,)


class TestAsyncRealtimeConnectionManagerEnter:
    """Unit tests for ``AsyncBetaRealtimeConnectionManager.enter()``: URL/header construction and errors."""

    async def test_enter_builds_bearer_auth_and_query(self):
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            await manager.enter()
            await manager.__aexit__()

        assert fake_session.ws_connect.call_count == 1
        _args, kwargs = fake_session.ws_connect.call_args
        assert _args[0].startswith("wss://my-account.services.ai.azure.com")
        assert kwargs["params"]["api-version"] == "v1"
        assert kwargs["headers"]["Authorization"] == "Bearer fake-token"
        assert kwargs["headers"]["Foundry-Features"] == "VoiceAgents=V1Preview"
        assert "Sec-WebSocket-Protocol" not in kwargs["headers"]
        assert kwargs["protocols"] == ("realtime",)

    async def test_enter_identifies_sdk_via_user_agent_and_query(self):
        # The generated HTTP surface gets SDK identification for free from the core pipeline's
        # UserAgentPolicy; this hand-written client builds its own request and must opt in
        # explicitly, both as a User-Agent header and (since some proxies/paths don't forward
        # WebSocket upgrade headers) as an x-ms-client-sdk query parameter.
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            await manager.enter()
            await manager.__aexit__()

        _args, kwargs = fake_session.ws_connect.call_args
        assert kwargs["headers"]["User-Agent"] == _USER_AGENT
        assert "azsdk-python-ai-projects" in _USER_AGENT
        assert VERSION in _USER_AGENT
        assert kwargs["params"]["x-ms-client-sdk"] == _USER_AGENT

    async def test_enter_caller_user_agent_overrides_default(self):
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager(extra_headers={"User-Agent": "custom-user-agent"})
            await manager.enter()
            await manager.__aexit__()

        _args, kwargs = fake_session.ws_connect.call_args
        assert kwargs["headers"]["User-Agent"] == "custom-user-agent"

    async def test_enter_sends_structured_inputs_as_query_parameter(self):
        # Regression test: structured_inputs used to be serialized into a custom
        # "x-ms-voice-structured-inputs" header, but the generated request builder
        # (build_beta_voice_agents_realtime_connect_voice_agent_request) defines this as the
        # "structured_inputs" query parameter -- the service never actually read the header.
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager(structured_inputs={"greeting_name": "Alex"})
            await manager.enter()
            await manager.__aexit__()

        _args, kwargs = fake_session.ws_connect.call_args
        assert json.loads(kwargs["params"]["structured_inputs"]) == {"greeting_name": "Alex"}
        assert "structured_input" not in kwargs["params"]
        assert "x-ms-voice-structured-inputs" not in kwargs["headers"]

    async def test_enter_caller_user_agent_overrides_default_case_insensitive(self):
        # Regression test: a plain dict merge of extra_headers would leave a differently-cased
        # caller override (e.g. "user-agent") as a *separate* key alongside our own "User-Agent"
        # default, since Python dict keys are case-sensitive but HTTP header names are not --
        # sending two User-Agent-like headers instead of cleanly honoring the caller's override.
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager(extra_headers={"user-agent": "custom-user-agent"})
            await manager.enter()
            await manager.__aexit__()

        _args, kwargs = fake_session.ws_connect.call_args
        headers = kwargs["headers"]
        assert "User-Agent" not in headers
        assert headers["user-agent"] == "custom-user-agent"

    async def test_enter_source_retains_client_identification_wiring(self):
        # SDK identification belongs to the authenticated transport shared by Live and Realtime.
        source = "\n".join(
            inspect.getsource(cls.__dict__[method])
            for cls in AsyncBetaRealtimeConnectionManager.__mro__
            for method in ("enter", "_get_query")
            if method in cls.__dict__
        )
        assert "_USER_AGENT" in source
        assert "_has_header_case_insensitive" in source
        assert "x-ms-client-sdk" in source

    async def test_enter_rejects_untrusted_connection_url_host(self):
        manager = _make_manager(connection_url="wss://evil.example.com/steal-token")
        with pytest.raises(ValueError):
            await manager.enter()

    async def test_enter_overrides_caller_supplied_protocols_kwarg(self):
        # Regression test: protocols=("realtime",) is now passed explicitly to ws_connect, so a
        # caller-supplied protocols override forwarded through **kwargs would otherwise collide
        # ("got multiple values for keyword argument 'protocols'"). The service requires the
        # "realtime" subprotocol, so the override is dropped rather than honored.
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager(protocols=("other",))
            await manager.enter()
            await manager.__aexit__()

        _args, kwargs = fake_session.ws_connect.call_args
        assert kwargs["protocols"] == ("realtime",)

    async def test_enter_rejects_non_wss_url(self):
        manager = _make_manager(endpoint="ftp://not-http-or-https")
        with pytest.raises(ValueError):
            await manager.enter()

    async def test_enter_raises_runtime_error_when_aiohttp_missing(self):
        manager = _make_manager()
        with patch.dict("sys.modules", {"aiohttp": None}):
            with pytest.raises(RuntimeError, match="aiohttp"):
                await manager.enter()

    async def test_enter_closes_session_on_connect_failure(self):
        fake_session = MagicMock()
        fake_session.ws_connect = AsyncMock(side_effect=OSError("connection refused"))
        fake_session.close = AsyncMock()
        with patch("aiohttp.ClientSession", return_value=fake_session):
            manager = _make_manager()
            with pytest.raises(ConnectionError):
                await manager.enter()
        fake_session.close.assert_awaited_once()

    async def test_context_manager_closes_connection_on_exit(self):
        fake_ws = _make_fake_ws()
        patcher, fake_session = _patch_client_session(fake_ws)
        with patcher:
            async with _make_manager():
                pass
        fake_ws.close.assert_awaited_once()
        fake_session.close.assert_awaited_once()


class TestAsyncRealtimeConnectionRecv:
    """Unit tests for ``AsyncBetaRealtimeConnection.recv()``: event dispatch and non-text frames."""

    @pytest.mark.parametrize(
        "event_type,event_model",
        list(models.RealtimeServerEvent.__mapping__.items()),
        ids=list(models.RealtimeServerEvent.__mapping__),
    )
    async def test_every_generated_realtime_server_event_is_dispatched(self, event_type, event_model):
        import aiohttp

        payload = {
            "type": event_type,
            "event_id": "event-dispatch",
            "output_index": 0,
            "content_index": 0,
            "future_field": {"enabled": False, "count": 0},
        }
        expected = dict(payload)
        if event_type == "response.audio_timestamp.delta":
            expected["timestamp_type"] = "word"
        transport = _make_fake_ws()
        transport.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps(payload)))
        patcher, _ = _patch_client_session(transport)
        with patcher:
            async with _make_manager() as connection:
                event = await connection.recv()

        assert type(event) is event_model
        assert event.type == event_type
        assert event.as_dict() == expected

    async def test_recv_dispatches_shared_error_not_registered_on_generated_base(self):
        import aiohttp

        payload = {
            "type": "error",
            "event_id": "event-error",
            "error": {
                "type": "invalid_request_error",
                "code": "invalid_command",
                "message": "offline error",
                "event_id": "event-request",
                "future_field": False,
            },
            "future_field": {"enabled": False, "count": 0},
        }
        transport = _make_fake_ws()
        transport.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps(payload)))
        patcher, _ = _patch_client_session(transport)
        with patcher:
            async with _make_manager() as connection:
                event = await connection.recv()

        assert type(event) is models.RealtimeServerEventError
        assert event.error.message == "offline error"
        assert event.as_dict() == payload

    @pytest.mark.parametrize(
        "event_type", ["session.handoff.started", "session.handoff.completed", "session.handoff.aborted"]
    )
    async def test_recv_dispatches_handoff_events(self, event_type):
        import aiohttp

        from azure.ai.projects import models

        payload = {
            "type": event_type,
            "event_id": "event-test",
            "handoff_id": "handoff-test",
            "edge_id": "edge-test",
            "from_node_id": "$entrypoint",
            "to_node_id": "node-test",
            "from_model": "source-model-test",
            "to_model": "target-model-test",
            "tool_call_id": "call-test",
            "node_generation": 0,
        }
        if event_type == "session.handoff.aborted":
            payload["reason"] = "user_interruption"
        transport = _make_fake_ws()
        transport.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps(payload)))
        patcher, _ = _patch_client_session(transport)
        with patcher:
            manager = _make_manager()
            connection = await manager.enter()
            try:
                event = await connection.recv()
            finally:
                await manager.__aexit__()
        assert isinstance(event, models.RealtimeServerEvent.__mapping__[event_type])
        assert event.as_dict() == payload

    @pytest.mark.parametrize(
        "event_type,fields",
        [
            ("input_collection.status", {"channel": "dtmf", "status": "completed", "value": "0012"}),
            ("response.system_tool_arguments.delta", {"delta": '{"secret":'}),
            ("response.system_tool_arguments.done", {"name": "collect_dtmf", "arguments": '{"secret":false}'}),
        ],
    )
    async def test_recv_dispatches_system_tool_events(self, event_type, fields):
        import aiohttp

        from azure.ai.projects import models

        payload = {"type": event_type, "event_id": "event-test", "call_id": "call-test", **fields}
        if event_type.startswith("response."):
            payload.update(response_id="response-test", item_id="item-test", output_index=0)
        transport = _make_fake_ws()
        transport.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps(payload)))
        patcher, _ = _patch_client_session(transport)
        with patcher:
            manager = _make_manager()
            connection = await manager.enter()
            try:
                event = await connection.recv()
            finally:
                await manager.__aexit__()
        assert isinstance(event, models.RealtimeServerEvent.__mapping__[event_type])
        assert event.as_dict() == payload

    async def test_recv_dispatches_known_event_type(self):
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.receive = AsyncMock(
            return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps({"type": "session.created", "session": {}}))
        )
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                event = await conn.recv()
                assert isinstance(event, RealtimeServerEventSessionCreated)
            finally:
                await manager.__aexit__()

    async def test_recv_skips_ping_pong_frames(self):
        # Regression test locking in the existing PING/PONG handling.
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.receive = AsyncMock(
            side_effect=[
                _make_fake_msg(aiohttp.WSMsgType.PING, b""),
                _make_fake_msg(aiohttp.WSMsgType.PONG, b""),
                _make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps({"type": "session.created", "session": {}})),
            ]
        )
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                event = await conn.recv()
                assert isinstance(event, RealtimeServerEventSessionCreated)
                assert fake_ws.receive.await_count == 3
            finally:
                await manager.__aexit__()

    async def test_recv_unknown_event_type_returns_dict(self):
        import aiohttp

        payload = {"type": "some.new.event", "foo": "bar", "future_field": {"enabled": False, "count": 0}}
        fake_ws = _make_fake_ws()
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps(payload)))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                event = await conn.recv()
                assert isinstance(event, dict)
                assert event == payload
            finally:
                await manager.__aexit__()

    async def test_recv_close_frame_raises_connection_reset_error(self):
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.CLOSE))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                with pytest.raises(ConnectionResetError):
                    await conn.recv()
            finally:
                await manager.__aexit__()

    async def test_recv_error_frame_raises_connection_reset_error(self):
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.exception = MagicMock(return_value=RuntimeError("boom"))
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.ERROR))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                with pytest.raises(ConnectionResetError):
                    await conn.recv()
            finally:
                await manager.__aexit__()

    async def test_iteration_stops_cleanly_on_graceful_close(self):
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.close_code = 1000  # Normal Closure
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.CLOSE))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                assert [event async for event in conn] == []
            finally:
                await manager.__aexit__()

    async def test_iteration_propagates_abnormal_closure(self):
        # Regression test: recv() used to raise the same ConnectionResetError for every close
        # frame regardless of code, and the async iterator caught all of them, so a real
        # server-side failure (e.g. close code 1011) was indistinguishable from a normal end of
        # stream -- an `async for event in conn:` caller could silently accept a truncated
        # response. Only a graceful closure (code 1000/1001) should end iteration quietly.
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.close_code = 1011  # Internal Error
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.CLOSE))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                with pytest.raises(ConnectionResetError):
                    _ = [event async for event in conn]
            finally:
                await manager.__aexit__()

    async def test_iteration_propagates_transport_error(self):
        # Regression test: same as above, but for the WSMsgType.ERROR path (an actual transport
        # exception, not just an abnormal close code) -- this must never be swallowed either.
        import aiohttp

        fake_ws = _make_fake_ws()
        fake_ws.exception = MagicMock(return_value=RuntimeError("boom"))
        fake_ws.receive = AsyncMock(return_value=_make_fake_msg(aiohttp.WSMsgType.ERROR))
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                with pytest.raises(ConnectionResetError):
                    _ = [event async for event in conn]
            finally:
                await manager.__aexit__()


class TestAsyncRealtimeConnectionSend:
    """Unit tests for ``AsyncBetaRealtimeConnection.send()``: model/str/mapping serialization."""

    async def test_send_serializes_typed_model(self):
        fake_ws = _make_fake_ws()
        fake_ws.send_str = AsyncMock()
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                await conn.send(RealtimeClientEventResponseCreate())
                sent_raw = fake_ws.send_str.call_args[0][0]
                payload = json.loads(sent_raw)
                assert payload["type"] == "response.create"
            finally:
                await manager.__aexit__()

    async def test_send_rejects_invalid_json_string(self):
        fake_ws = _make_fake_ws()
        fake_ws.send_str = AsyncMock()
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                with pytest.raises(ValueError):
                    await conn.send("not valid json")
            finally:
                await manager.__aexit__()

    async def test_send_serializes_mapping(self):
        fake_ws = _make_fake_ws()
        fake_ws.send_str = AsyncMock()
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                await conn.send({"type": "response.cancel"})
                sent_raw = fake_ws.send_str.call_args[0][0]
                assert json.loads(sent_raw) == {"type": "response.cancel"}
            finally:
                await manager.__aexit__()


@pytest.mark.parametrize("event_id", [None, "event-helper"], ids=["default-event-id", "explicit-event-id"])
class TestAsyncRealtimeHelperSerialization:
    """Exercise the actual resource helper, SDK encoder, and socket send together."""

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    async def test_session_update_preserves_sparse_settings(self, typed, event_id):
        settings = {
            "instructions": "",
            "temperature": 0.0,
            "parallel_tool_calls": False,
            "tools": [],
            "output_modalities": ["text"],
        }
        if typed:
            session = models.VoiceAgentSessionUpdateConfig(**settings)
            expected_settings = {"type": "realtime", **settings}
        else:
            settings["future_settings"] = {"enabled": False, "count": 0}
            session = settings
            expected_settings = deepcopy(settings)
        original = deepcopy(session)
        kwargs = {"event_id": event_id} if event_id is not None else {}
        expected = {"type": "session.update", "session": expected_settings, **kwargs}

        async with _helper_connection() as (connection, sent):
            assert await connection.session.update(session=session, **kwargs) is None

        assert sent == [expected]
        assert session == original

    @pytest.mark.parametrize(
        "helper,arguments,expected",
        [
            pytest.param(
                "session.avatar_connect",
                {"client_sdp": "v=0\r\ns=offline\r\n"},
                {"type": "session.avatar.connect", "client_sdp": "v=0\r\ns=offline\r\n"},
                id="avatar-connect",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": b"\x00\x01\xfe\xff"},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-bytes",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": bytearray(b"\x00\x01\xfe\xff")},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-bytearray",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": "AAH+/w=="},
                {"type": "input_audio_buffer.append", "audio": "AAH+/w=="},
                id="append-base64",
            ),
            pytest.param(
                "input_audio_buffer.append",
                {"audio": b""},
                {"type": "input_audio_buffer.append", "audio": ""},
                id="append-empty-bytes",
            ),
            pytest.param("input_audio_buffer.commit", {}, {"type": "input_audio_buffer.commit"}, id="commit-input"),
            pytest.param("input_audio_buffer.clear", {}, {"type": "input_audio_buffer.clear"}, id="clear-input"),
            pytest.param("output_audio_buffer.clear", {}, {"type": "output_audio_buffer.clear"}, id="clear-output"),
            pytest.param(
                "conversation.item.delete",
                {"item_id": "item-test"},
                {"type": "conversation.item.delete", "item_id": "item-test"},
                id="delete-item",
            ),
            pytest.param(
                "conversation.item.retrieve",
                {"item_id": "item-test"},
                {"type": "conversation.item.retrieve", "item_id": "item-test"},
                id="retrieve-item",
            ),
            pytest.param(
                "conversation.item.truncate",
                {"item_id": "item-test", "content_index": 0, "audio_end_ms": 0},
                {"type": "conversation.item.truncate", "item_id": "item-test", "content_index": 0, "audio_end_ms": 0},
                id="truncate-at-zero",
            ),
            pytest.param(
                "conversation.item.truncate",
                {"item_id": "item-test", "content_index": 1, "audio_end_ms": 240},
                {"type": "conversation.item.truncate", "item_id": "item-test", "content_index": 1, "audio_end_ms": 240},
                id="truncate-at-offset",
            ),
            pytest.param("response.create", {}, {"type": "response.create"}, id="create-default-response"),
            pytest.param("response.create", {"response": None}, {"type": "response.create"}, id="create-none-response"),
            pytest.param(
                "response.create",
                {"response": {}},
                {"type": "response.create", "response": {}},
                id="create-empty-response",
            ),
            pytest.param("response.cancel", {}, {"type": "response.cancel"}, id="cancel-current-response"),
            pytest.param(
                "response.cancel",
                {"response_id": "response-test"},
                {"type": "response.cancel", "response_id": "response-test"},
                id="cancel-specific-response",
            ),
        ],
    )
    async def test_resource_helpers_send_exact_wire_payload(self, helper, arguments, expected, event_id):
        original = deepcopy(arguments)
        kwargs = {"event_id": event_id} if event_id is not None else {}

        async with _helper_connection() as (connection, sent):
            resource = connection
            for name in helper.split("."):
                resource = getattr(resource, name)
            assert await resource(**arguments, **kwargs) is None

        assert sent == [{**expected, **kwargs}]
        assert arguments == original

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    @pytest.mark.parametrize("previous_item_id", [None, "", "previous-test"])
    async def test_conversation_item_create_preserves_tool_output(self, typed, previous_item_id, event_id):
        item_payload = {
            "type": "function_call_output",
            "call_id": "canonical-call-test",
            "output": '{"available":false,"count":0}',
        }
        if typed:
            item = models.RealtimeConversationItemFunctionCallOutput(
                call_id="canonical-call-test", output='{"available":false,"count":0}'
            )
        else:
            item_payload["future_field"] = {"enabled": False, "count": 0}
            item = deepcopy(item_payload)
        original = deepcopy(item)
        kwargs = {"event_id": event_id} if event_id is not None else {}
        if previous_item_id is not None:
            kwargs["previous_item_id"] = previous_item_id

        async with _helper_connection() as (connection, sent):
            assert await connection.conversation.item.create(item=item, **kwargs) is None

        assert sent == [{"type": "conversation.item.create", "item": item_payload, **kwargs}]
        assert item == original

    @pytest.mark.parametrize("typed", [False, True], ids=["mapping", "generated-model"])
    async def test_response_create_preserves_per_response_overrides(self, typed, event_id):
        response_payload = {
            "instructions": "",
            "parallel_tool_calls": False,
            "input": [],
            "output_modalities": ["text"],
        }
        if typed:
            response = models.VoiceAgentResponseCreateParams(**response_payload)
        else:
            response_payload["future_settings"] = {"enabled": False, "count": 0}
            response = deepcopy(response_payload)
        original = deepcopy(response)
        kwargs = {"event_id": event_id} if event_id is not None else {}

        async with _helper_connection() as (connection, sent):
            assert await connection.response.create(response=response, **kwargs) is None

        assert sent == [{"type": "response.create", "response": response_payload, **kwargs}]
        assert response == original


async def test_realtime_logging_emits_metadata_without_sensitive_content(caplog):
    import aiohttp

    fake_ws = _make_fake_ws()
    fake_ws.send_str = AsyncMock()
    fake_ws.receive = AsyncMock(
        return_value=_make_fake_msg(
            aiohttp.WSMsgType.TEXT,
            json.dumps({"type": "some.new.event", "text": "secret-inbound-content"}),
        )
    )
    connection_url = "wss://my-account.services.ai.azure.com/custom?sig=secret-query"

    caplog.set_level(logging.DEBUG, logger="azure.ai.projects.realtime")
    patcher, _ = _patch_client_session(fake_ws)
    with patcher:
        manager = _make_manager(
            connection_url=connection_url,
            structured_inputs={"value": "secret-structured-input"},
        )
        conn = await manager.enter()
        await conn.send({"type": "response.create", "text": "secret-outbound-content"})
        await conn.recv()
        await manager.__aexit__()

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "WebSocket CONNECT target=wss://my-account.services.ai.azure.com/custom" in messages
    assert "WebSocket CONNECTED target=wss://my-account.services.ai.azure.com/custom" in messages
    assert "WebSocket SEND type=response.create bytes=" in messages
    assert "WebSocket RECEIVE type=some.new.event bytes=" in messages
    assert "WebSocket CLOSE code=1000" in messages
    for sensitive_value in (
        "fake-token",
        "secret-query",
        "secret-structured-input",
        "secret-inbound-content",
        "secret-outbound-content",
    ):
        assert sensitive_value not in messages
