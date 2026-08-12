# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tests for typed Voice callback dispatch."""

import json
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import (
    InputTextPart,
    ResponseCreated,
    ResponseDone,
    ResponseOutputTextDelta,
    ResponseOutputTextDone,
    SessionReady,
    SessionDisconnected,
    SessionStart,
    UserMessage,
    VoiceAgentServerHost,
    new_item_id,
    new_response_id,
)
from azure.ai.agentserver.invocations.voice._codec import MAX_FRAME_BYTES


def _frame(message_type, **fields):
    return {
        "type": message_type,
        "id": "m_test",
        "ts": "2026-08-12T00:00:00Z",
        **fields,
    }


def test_decorators_reject_sync_duplicate_and_raw_handlers():
    app = VoiceAgentServerHost(configure_observability=None)

    with pytest.raises(TypeError, match="async function"):

        @app.on_user_message
        def sync_callback(session, event):
            del session, event

    @app.on_user_message
    async def first(session, event):
        del session, event

    with pytest.raises(RuntimeError, match="already registered"):
        app.on_user_message(first)

    with pytest.raises(RuntimeError, match="owns /invocations_ws"):
        app.ws_handler(lambda websocket: None)


def test_real_websocket_dispatches_explicit_streaming_response():
    app = VoiceAgentServerHost(configure_observability=None)
    observed_sessions = []

    @app.on_session_start
    async def on_start(session, event):
        observed_sessions.append(session)
        assert isinstance(event, SessionStart)
        await session.send(SessionReady())

    @app.on_user_message
    async def on_message(session, event):
        observed_sessions.append(session)
        assert isinstance(event, UserMessage)
        assert event.content == (InputTextPart(text="hello"),)
        response_id = new_response_id()
        item_id = new_item_id()
        await session.send(ResponseCreated(response_id=response_id, in_reply_to=(event.item_id,)))
        await session.send(ResponseOutputTextDelta(response_id=response_id, item_id=item_id, delta="hel"))
        await session.send(ResponseOutputTextDelta(response_id=response_id, item_id=item_id, delta="lo"))
        await session.send(ResponseOutputTextDone(response_id=response_id, item_id=item_id, text="hello"))
        await session.send(ResponseDone(response_id=response_id))

    with TestClient(app) as client:
        with client.websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_frame("future.message", ignored=True))
            websocket.send_json(
                _frame(
                    "session.start",
                    protocol_version="1.0",
                    reconnect=False,
                    response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
                )
            )
            assert websocket.receive_json()["type"] == "session.ready"
            websocket.send_json(
                _frame(
                    "user.message",
                    item_id="in_1",
                    content=[{"type": "input_text", "text": "hello"}],
                )
            )
            output = [websocket.receive_json() for _ in range(5)]

    assert len(observed_sessions) == 2
    assert observed_sessions[0] is observed_sessions[1]
    assert [message["type"] for message in output] == [
        "response.created",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.done",
    ]
    assert output[-2]["text"] == "hello"


def test_real_websocket_dispatches_transport_disconnect():
    app = VoiceAgentServerHost(configure_observability=None)
    observed = []

    @app.on_disconnect
    async def on_disconnect(session, event):
        observed.append((session, event))

    with TestClient(app) as client:
        with client.websocket_connect("/invocations_ws") as websocket:
            websocket.close(code=1001, reason="client restart")

    assert len(observed) == 1
    _, event = observed[0]
    assert isinstance(event, SessionDisconnected)
    assert event.code == 1001
    assert event.reason == "client restart"


@pytest.mark.parametrize(
    ("send", "expected_code"),
    [
        (lambda websocket: websocket.send_bytes(b"binary"), 1003),
        (lambda websocket: websocket.send_text("not-json"), 1002),
        (lambda websocket: websocket.send_json(_frame("handoff.failed")), 1003),
    ],
)
def test_invalid_or_excluded_frames_close_the_connection(send, expected_code):
    app = VoiceAgentServerHost(configure_observability=None)
    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as raised:
            with client.websocket_connect("/invocations_ws") as websocket:
                send(websocket)
                websocket.receive_text()
    assert raised.value.code == expected_code


def test_voice_host_sets_one_megabyte_websocket_admission_limit():
    app = VoiceAgentServerHost(configure_observability=None)
    config = app._build_hypercorn_config("127.0.0.1", 8088)  # pylint: disable=protected-access

    assert MAX_FRAME_BYTES == 1_048_576
    assert config.websocket_max_message_size == MAX_FRAME_BYTES


def test_voice_source_has_no_lifecycle_owners():
    source_root = Path(__file__).parents[2] / "azure" / "ai" / "agentserver" / "invocations" / "voice"
    source = "\n".join(path.read_text(encoding="utf-8") for path in source_root.glob("*.py"))
    for forbidden in (
        "asyncio.create_task",
        "Future[",
        "TimerHandle",
        "threading",
        "weakref",
        "_pending_responses",
        "_terminal_responses",
        "_response_tasks",
        "_reconnect",
    ):
        assert forbidden not in source
