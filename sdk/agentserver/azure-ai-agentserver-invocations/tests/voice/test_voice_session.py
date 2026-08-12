# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the thin Voice Session context."""

import asyncio
import json

import pytest
from starlette.websockets import WebSocketState

from azure.ai.agentserver.invocations.voice import EndCall, Session, SessionReady
from azure.ai.agentserver.invocations.voice import _session as session_module


class _BlockingWebSocket:
    def __init__(self):
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.frames = []
        self.closes = []
        self.close_error = None
        self.application_state = WebSocketState.CONNECTED
        self.active_sends = 0
        self.maximum_active_sends = 0

    async def send_text(self, frame):
        self.active_sends += 1
        self.maximum_active_sends = max(self.maximum_active_sends, self.active_sends)
        self.frames.append(json.loads(frame))
        self.entered.set()
        await self.release.wait()
        self.active_sends -= 1

    async def close(self, *, code, reason):
        self.active_sends += 1
        self.maximum_active_sends = max(self.maximum_active_sends, self.active_sends)
        self.closes.append((code, reason))
        self.active_sends -= 1
        if self.close_error is not None:
            raise self.close_error


def test_session_cannot_be_constructed_by_customer():
    with pytest.raises(TypeError, match="created by VoiceAgentServerHost"):
        Session()


@pytest.mark.asyncio
async def test_session_has_only_transport_and_send_lock_and_serializes_writes():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    assert not hasattr(session, "__dict__")
    assert set(Session.__slots__) == {"_websocket", "_send_lock", "_terminal"}

    first = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    second = asyncio.create_task(session.send(EndCall(reason="completed")))
    await asyncio.sleep(0)
    assert len(websocket.frames) == 1

    websocket.release.set()
    await asyncio.gather(first, second)
    assert websocket.maximum_active_sends == 1
    assert [frame["type"] for frame in websocket.frames] == ["session.ready", "end_call"]


@pytest.mark.asyncio
async def test_session_serializes_application_send_and_close():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
    await asyncio.sleep(0)

    assert websocket.closes == []
    websocket.release.set()
    await asyncio.gather(send_task, close_task)

    assert websocket.maximum_active_sends == 1
    assert websocket.closes == [(1002, "protocol error")]


@pytest.mark.asyncio
async def test_session_close_cancellation_does_not_wait_for_blocked_send():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
    await asyncio.sleep(0)

    with pytest.raises(RuntimeError, match="terminating"):
        await session.send(EndCall(reason="too late"))

    close_task.cancel("queued-close-cancel")
    with pytest.raises(asyncio.CancelledError) as raised:
        await asyncio.wait_for(close_task, timeout=1)

    assert raised.value.args == ("queued-close-cancel",)
    assert websocket.closes == []
    with pytest.raises(RuntimeError, match="terminating"):
        await session.send(EndCall(reason="too late"))

    websocket.release.set()
    await send_task
    assert not session._send_lock.locked()  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_session_queued_cancellation_skips_transport_close():
    websocket = _BlockingWebSocket()
    websocket.close_error = OSError("transport close failed")
    session = Session._create(websocket)  # pylint: disable=protected-access

    send_task = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    close_task = asyncio.create_task(session._close(1002, "protocol error"))  # pylint: disable=protected-access
    await asyncio.sleep(0)
    close_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(close_task, timeout=1)

    assert websocket.closes == []
    with pytest.raises(RuntimeError, match="terminating"):
        await session.send(EndCall(reason="too late"))

    websocket.release.set()
    await send_task
    assert not session._send_lock.locked()  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_session_close_preserves_inner_acquire_task_cancellation(monkeypatch):
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    real_create_task = asyncio.create_task

    def create_cancelled_task(coroutine, *, name=None):
        task = real_create_task(coroutine, name=name)
        task.cancel("inner-at-create")
        return task

    monkeypatch.setattr(session_module.asyncio, "create_task", create_cancelled_task)

    with pytest.raises(asyncio.CancelledError) as raised:
        await session._close(1002, "protocol error")  # pylint: disable=protected-access

    assert raised.value.args == ("inner-at-create",)
    assert not session._send_lock.locked()  # pylint: disable=protected-access
    with pytest.raises(RuntimeError, match="terminating"):
        await session.send(EndCall(reason="too late"))
