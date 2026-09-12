# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Regression tests for reviewed Voice protocol findings."""

import asyncio
import json
import logging
from unittest.mock import AsyncMock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import _voice_host as voice_host_module
from azure.ai.agentserver.invocations.voice import (
    ResponseCreated,
    SessionEnd,
    SessionReady,
    SessionTermination,
    UserSpeechStarted,
    VoiceAgentServerHost,
)
from azure.ai.agentserver.invocations.voice._codec import MAX_FRAME_BYTES, encode_outbound_message

from conftest import _records_with_ws_extras


def _voice_frame(message_type, message_id, **fields):
    return {
        "type": "websocket.receive",
        "text": json.dumps(
            {
                "type": message_type,
                "id": message_id,
                "ts": "2026-08-12T00:00:00Z",
                **fields,
            }
        ),
    }


@pytest.mark.parametrize(
    ("frame_kind", "frame", "expected_code"),
    [
        pytest.param("text", "not-json", 1002, id="invalid-json"),
        pytest.param("bytes", b"binary", 1003, id="binary-frame"),
        pytest.param("oversized-text", None, 1009, id="oversized-text"),
    ],
)
def test_voice_sdk_close_code_matches_structured_telemetry(caplog, frame_kind, frame, expected_code):
    app = VoiceAgentServerHost(configure_observability=None)

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        with pytest.raises(WebSocketDisconnect) as raised:
            with TestClient(app).websocket_connect("/invocations_ws") as websocket:
                if frame_kind == "text":
                    websocket.send_text(frame)
                elif frame_kind == "oversized-text":
                    websocket.send_text("x" * (MAX_FRAME_BYTES + 1))
                else:
                    websocket.send_bytes(frame)
                websocket.receive_text()

    assert raised.value.code == expected_code
    records = _records_with_ws_extras(caplog.records)
    assert records
    assert getattr(records[-1], "azure.ai.agentserver.invocations_ws.close_code") == expected_code
    assert getattr(records[-1], "azure.ai.agentserver.session_id") == getattr(
        records[-1],
        "azure.ai.agentserver.invocations_ws.session_id",
    )


def test_proactive_admission_timeout_enforces_protocol_maximum():
    frame = json.loads(
        encode_outbound_message(
            ResponseCreated(
                response_id="r_boundary",
                admission_timeout_ms=60_000,
            )
        )
    )
    assert frame["admission_timeout_ms"] == 60_000

    with pytest.raises(ValueError, match="at most 60000"):
        encode_outbound_message(
            ResponseCreated(
                response_id="r_too_late",
                admission_timeout_ms=60_001,
            )
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("register_session_end_callback", [False, True])
async def test_session_end_commits_terminal_and_stops_dispatch(register_session_end_callback):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.scope = {}
    websocket.receive.side_effect = [
        _voice_frame("session.end", "m_end", reason="completed"),
        _voice_frame("user.speech_started", "m_late"),
    ]
    session_end_events = []
    later_events = []
    disconnect_events = []
    terminating_sessions = []

    if register_session_end_callback:

        @app.on_session_end
        async def on_session_end(session, event):
            assert isinstance(event, SessionEnd)
            session_end_events.append((session, event))
            await session.send(SessionReady())

    @app.on_user_speech_started
    async def on_user_speech_started(_session, event):
        assert isinstance(event, UserSpeechStarted)
        later_events.append(event)
        raise AssertionError("event after session.end was dispatched")

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnect_events.append(event)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert websocket.receive.await_count == 1
    assert len(session_end_events) == int(register_session_end_callback)
    assert later_events == []
    assert disconnect_events == []
    assert len(terminating_sessions) == 1
    assert terminating_sessions[0].termination is SessionTermination.COMPLETED
    with pytest.raises(RuntimeError, match="Voice Session is terminating"):
        await terminating_sessions[0].send(SessionReady())
    assert websocket.send_text.await_count == int(register_session_end_callback)


@pytest.mark.asyncio
async def test_session_end_commits_terminal_before_post_callback_cancellation_probe(monkeypatch):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.scope = {}
    websocket.receive.side_effect = [_voice_frame("session.end", "m_end", reason="completed")]
    callback_sessions = []
    terminating_outcomes = []
    probe_entered = asyncio.Event()
    release_probe = asyncio.Event()
    probe_calls = 0
    raise_pending_cancellation = voice_host_module._raise_pending_cancellation  # pylint: disable=protected-access

    async def gate_post_callback_probe():
        nonlocal probe_calls
        probe_calls += 1
        if probe_calls == 2:
            probe_entered.set()
            await release_probe.wait()
            return
        await raise_pending_cancellation()

    monkeypatch.setattr(voice_host_module, "_raise_pending_cancellation", gate_post_callback_probe)

    @app.on_session_end
    async def on_session_end(session, event):
        assert isinstance(event, SessionEnd)
        callback_sessions.append(session)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_outcomes.append(session.termination)

    handler = asyncio.create_task(app._handle_voice_connection(websocket))  # pylint: disable=protected-access
    await asyncio.wait_for(probe_entered.wait(), timeout=1)
    assert len(callback_sessions) == 1

    handler.cancel()
    with pytest.raises(asyncio.CancelledError):
        await handler

    assert probe_calls == 2
    assert callback_sessions[0].termination is SessionTermination.COMPLETED
    assert terminating_outcomes == [SessionTermination.COMPLETED]
    assert websocket.send_text.await_count == 0


@pytest.mark.asyncio
async def test_session_end_callback_failure_still_commits_terminal():
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.scope = {}
    websocket.receive.side_effect = [
        _voice_frame("session.end", "m_end", reason="completed"),
        _voice_frame("user.speech_started", "m_late"),
    ]
    callback_sessions = []
    later_events = []
    terminating_sessions = []

    class SessionEndCallbackError(Exception):
        pass

    @app.on_session_end
    async def on_session_end(session, event):
        assert isinstance(event, SessionEnd)
        callback_sessions.append(session)
        raise SessionEndCallbackError("session.end callback failed")

    @app.on_user_speech_started
    async def on_user_speech_started(_session, event):
        later_events.append(event)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    with pytest.raises(SessionEndCallbackError, match="session.end callback failed"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert websocket.receive.await_count == 1
    assert len(callback_sessions) == 1
    assert later_events == []
    assert terminating_sessions == callback_sessions
    with pytest.raises(RuntimeError, match="Voice Session is terminating"):
        await callback_sessions[0].send(SessionReady())


@pytest.mark.asyncio
async def test_session_end_callback_cancellation_still_commits_terminal():
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.scope = {}
    websocket.receive.side_effect = [
        _voice_frame("session.end", "m_end", reason="completed"),
        _voice_frame("user.speech_started", "m_late"),
    ]
    callback_sessions = []
    later_events = []
    disconnect_events = []
    terminating_sessions = []

    @app.on_session_end
    async def on_session_end(session, event):
        assert isinstance(event, SessionEnd)
        callback_sessions.append(session)
        raise asyncio.CancelledError("session.end callback cancelled")

    @app.on_user_speech_started
    async def on_user_speech_started(_session, event):
        later_events.append(event)

    @app.on_disconnect
    async def on_disconnect(_session, event):
        disconnect_events.append(event)

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    with pytest.raises(asyncio.CancelledError) as raised:
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert raised.value.args == ("session.end callback cancelled",)
    assert websocket.receive.await_count == 1
    assert len(callback_sessions) == 1
    assert later_events == []
    assert disconnect_events == []
    assert terminating_sessions == callback_sessions
    with pytest.raises(RuntimeError, match="Voice Session is terminating"):
        await callback_sessions[0].send(SessionReady())
    assert websocket.send_text.await_count == 0


@pytest.mark.asyncio
async def test_non_terminal_event_continues_dispatch():
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.scope = {}
    websocket.receive.side_effect = [
        _voice_frame("user.speech_started", "m_first"),
        _voice_frame("user.speech_started", "m_second"),
    ]
    observed_events = []

    class SecondEventObserved(Exception):
        pass

    @app.on_user_speech_started
    async def on_user_speech_started(_session, event):
        assert isinstance(event, UserSpeechStarted)
        observed_events.append(event)
        if len(observed_events) == 2:
            raise SecondEventObserved("second non-terminal event observed")

    with pytest.raises(SecondEventObserved, match="second non-terminal event observed"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert websocket.receive.await_count == 2
    assert [event.id for event in observed_events] == ["m_first", "m_second"]
