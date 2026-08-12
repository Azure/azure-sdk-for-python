# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the thin Voice Session context."""

import asyncio
import json

import pytest

from azure.ai.agentserver.invocations.voice import EndCall, Session, SessionReady


class _BlockingWebSocket:
    def __init__(self):
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.frames = []
        self.active_sends = 0
        self.maximum_active_sends = 0

    async def send_text(self, frame):
        self.active_sends += 1
        self.maximum_active_sends = max(self.maximum_active_sends, self.active_sends)
        self.frames.append(json.loads(frame))
        self.entered.set()
        await self.release.wait()
        self.active_sends -= 1


def test_session_cannot_be_constructed_by_customer():
    with pytest.raises(TypeError, match="created by VoiceAgentServerHost"):
        Session()


@pytest.mark.asyncio
async def test_session_has_only_transport_and_send_lock_and_serializes_writes():
    websocket = _BlockingWebSocket()
    session = Session._create(websocket)  # pylint: disable=protected-access
    assert not hasattr(session, "__dict__")
    assert set(Session.__slots__) == {"_websocket", "_send_lock"}

    first = asyncio.create_task(session.send(SessionReady()))
    await websocket.entered.wait()
    second = asyncio.create_task(session.send(EndCall(reason="completed")))
    await asyncio.sleep(0)
    assert len(websocket.frames) == 1

    websocket.release.set()
    await asyncio.gather(first, second)
    assert websocket.maximum_active_sends == 1
    assert [frame["type"] for frame in websocket.frames] == ["session.ready", "end_call"]
