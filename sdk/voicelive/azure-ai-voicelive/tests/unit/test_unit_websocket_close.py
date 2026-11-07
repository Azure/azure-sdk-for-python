# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# --------------------------------------------------------------------------
"""Unit tests for how VoiceLiveConnection maps WebSocket close frames to ConnectionClosed."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

aiohttp = pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)
from aiohttp import WSMessage, WSMsgType, web

from azure.ai.voicelive.aio import ConnectionClosed, VoiceLiveConnection
from azure.ai.voicelive.models import ServerEventSessionCreated


def _connection_returning(*messages, close_code=None):
    """Build a VoiceLiveConnection whose WebSocket returns the given messages in order."""
    ws = MagicMock()
    ws.receive = AsyncMock(side_effect=list(messages))
    ws.close_code = close_code
    ws.exception = MagicMock(return_value=None)
    return VoiceLiveConnection(MagicMock(), ws)


@pytest.mark.asyncio
class TestCloseFrameHandling:
    """CLOSE / CLOSING / CLOSED messages raise ConnectionClosed with the right code and reason."""

    async def test_close_frame_carries_server_code_and_reason(self):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSE, 4001, "Session expired"), close_code=4001)

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv()

        assert exc_info.value.code == 4001
        assert exc_info.value.reason == "Session expired"

    async def test_close_frame_uses_code_from_message(self):
        # close_code on the socket may not be populated yet; msg.data holds the code.
        conn = _connection_returning(WSMessage(WSMsgType.CLOSE, 1008, "Policy violation"), close_code=None)

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv_bytes()

        assert exc_info.value.code == 1008
        assert exc_info.value.reason == "Policy violation"

    async def test_close_frame_without_reason(self):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSE, 1000, ""), close_code=1000)

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv()

        assert exc_info.value.code == 1000
        assert exc_info.value.reason == ""

    async def test_closing_frame_raises_connection_closed(self):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSING, None, None), close_code=None)

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv()

        assert exc_info.value.code == 1000
        assert exc_info.value.reason != "Empty WebSocket frame"

    async def test_closing_frame_uses_known_close_code(self):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSING, None, None), close_code=4002)

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv_bytes()

        assert exc_info.value.code == 4002

    async def test_closing_frame_does_not_log_unexpected_type(self, caplog):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSING, None, None))

        with caplog.at_level("WARNING", logger="azure.ai.voicelive.aio._patch"):
            with pytest.raises(ConnectionClosed):
                await conn.recv()

        assert "Unexpected WebSocket message type" not in caplog.text

    async def test_closed_frame_unchanged(self):
        conn = _connection_returning(WSMessage(WSMsgType.CLOSED, None, None))

        with pytest.raises(ConnectionClosed) as exc_info:
            await conn.recv()

        assert exc_info.value.code == 1000
        assert exc_info.value.reason == "Connection closed"

    async def test_iteration_stops_cleanly_on_closing(self):
        event = {"type": "session.created", "event_id": "evt_1", "session": {"id": "sess_1"}}
        conn = _connection_returning(
            WSMessage(WSMsgType.TEXT, json.dumps(event), None),
            WSMessage(WSMsgType.CLOSING, None, None),
        )

        received = [e async for e in conn]

        assert len(received) == 1
        assert isinstance(received[0], ServerEventSessionCreated)


@pytest.mark.asyncio
class TestDataFramesUnaffected:
    """TEXT and BINARY messages are still returned as payload bytes."""

    async def test_text_frame(self):
        conn = _connection_returning(WSMessage(WSMsgType.TEXT, '{"type": "x"}', None))

        assert await conn.recv_bytes() == b'{"type": "x"}'

    async def test_binary_frame(self):
        conn = _connection_returning(WSMessage(WSMsgType.BINARY, b"\x00\x01", None))

        assert await conn.recv_bytes() == b"\x00\x01"

    async def test_text_frame_parsed_as_event(self):
        event = {"type": "session.created", "event_id": "evt_1", "session": {"id": "sess_1"}}
        conn = _connection_returning(WSMessage(WSMsgType.TEXT, json.dumps(event), None))

        result = await conn.recv()

        assert isinstance(result, ServerEventSessionCreated)
        assert result.event_id == "evt_1"


@pytest.mark.asyncio
class TestCloseOverRealSocket:
    """End-to-end check against a local aiohttp WebSocket server (no network access)."""

    async def _serve(self, handler):
        app = web.Application()
        app.router.add_get("/ws", handler)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]  # pylint: disable=protected-access
        return runner, f"http://127.0.0.1:{port}/ws"

    async def test_server_close_reason_is_preserved(self):
        async def handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            await ws.close(code=4001, message=b"Session expired: max duration reached")
            return ws

        runner, url = await self._serve(handler)
        try:
            async with aiohttp.ClientSession() as session:
                ws = await session.ws_connect(url)
                conn = VoiceLiveConnection(session, ws)
                with pytest.raises(ConnectionClosed) as exc_info:
                    await conn.recv()
        finally:
            await runner.cleanup()

        assert exc_info.value.code == 4001
        assert exc_info.value.reason == "Session expired: max duration reached"

    async def test_close_from_other_task_while_receiving(self):
        async def handler(request):
            ws = web.WebSocketResponse()
            await ws.prepare(request)
            async for _ in ws:
                pass
            return ws

        runner, url = await self._serve(handler)
        try:
            async with aiohttp.ClientSession() as session:
                ws = await session.ws_connect(url)
                conn = VoiceLiveConnection(session, ws)
                recv_task = asyncio.ensure_future(conn.recv())
                await asyncio.sleep(0.05)
                await ws.close()
                with pytest.raises(ConnectionClosed) as exc_info:
                    await asyncio.wait_for(recv_task, timeout=5)
        finally:
            await runner.cleanup()

        assert exc_info.value.code == 1000
        assert exc_info.value.reason != "Empty WebSocket frame"
