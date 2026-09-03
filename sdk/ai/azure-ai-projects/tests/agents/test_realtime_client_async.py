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
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.credentials import AccessToken

from azure.ai.projects.aio._realtime import AsyncRealtimeConnectionManager
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


def _make_manager(**overrides) -> AsyncRealtimeConnectionManager:
    kwargs = {
        "endpoint": _ENDPOINT,
        "credential": _AsyncFakeCredential(),
        "credential_scopes": ["https://ai.azure.com/.default"],
        "api_version": "v1",
        "agent_name": "my-agent",
        "foundry_features": "VoiceAgents=V1Preview",
    }
    kwargs.update(overrides)
    return AsyncRealtimeConnectionManager(**kwargs)


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


class TestAsyncRealtimeConnectionManagerEnter:
    """Unit tests for ``AsyncRealtimeConnectionManager.enter()``: URL/header construction and errors."""

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
    """Unit tests for ``AsyncRealtimeConnection.recv()``: event dispatch and non-text frames."""

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

        fake_ws = _make_fake_ws()
        fake_ws.receive = AsyncMock(
            return_value=_make_fake_msg(aiohttp.WSMsgType.TEXT, json.dumps({"type": "some.new.event", "foo": "bar"}))
        )
        patcher, _ = _patch_client_session(fake_ws)
        with patcher:
            manager = _make_manager()
            conn = await manager.enter()
            try:
                event = await conn.recv()
                assert isinstance(event, dict)
                assert event["foo"] == "bar"
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


class TestAsyncRealtimeConnectionSend:
    """Unit tests for ``AsyncRealtimeConnection.send()``: model/str/mapping serialization."""

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
