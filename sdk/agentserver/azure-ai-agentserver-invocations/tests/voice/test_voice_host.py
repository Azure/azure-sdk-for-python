# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tests for typed Voice callback dispatch."""

import asyncio
import functools
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import _voice_host as voice_host_module
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

    with pytest.raises(TypeError, match="synchronous function"):

        @app.on_connection_terminating
        async def async_terminating_callback(session):
            del session

    class AsyncTerminatingCallback:
        async def __call__(self, session):
            del session

    with pytest.raises(TypeError, match="synchronous function"):
        app.on_connection_terminating(AsyncTerminatingCallback())

    async def wrapped_async_callback(session):
        del session

    @functools.wraps(wrapped_async_callback)
    def sync_wrapper(session):
        return wrapped_async_callback(session)

    with pytest.raises(TypeError, match="synchronous function"):
        app.on_connection_terminating(sync_wrapper)

    async def async_generator_callback(session):
        del session
        yield

    with pytest.raises(TypeError, match="synchronous function"):
        app.on_connection_terminating(async_generator_callback)

    with pytest.raises(TypeError, match="must accept Session"):

        @app.on_connection_terminating
        def missing_session_argument():
            pass

    @app.on_connection_terminating
    def terminating_callback(session):
        del session

    with pytest.raises(RuntimeError, match="already registered"):
        app.on_connection_terminating(terminating_callback)


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
    callback_order = []

    @app.on_disconnect
    async def on_disconnect(session, event):
        observed.append((session, event))
        callback_order.append("disconnect")

    @app.on_connection_terminating
    def on_connection_terminating(session):
        observed.append((session, None))
        callback_order.append("terminating")

    with TestClient(app) as client:
        with client.websocket_connect("/invocations_ws") as websocket:
            websocket.close(code=1001, reason="client restart")

    assert len(observed) == 2
    session, event = observed[0]
    assert isinstance(event, SessionDisconnected)
    assert event.code == 1001
    assert event.reason == "client restart"
    assert observed[1] == (session, None)
    assert callback_order == ["disconnect", "terminating"]


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
    terminating_sessions = []

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    with TestClient(app) as client:
        with pytest.raises(WebSocketDisconnect) as raised:
            with client.websocket_connect("/invocations_ws") as websocket:
                send(websocket)
                websocket.receive_text()
    assert raised.value.code == expected_code
    assert len(terminating_sessions) == 1


@pytest.mark.asyncio
async def test_connection_terminating_runs_when_handler_is_cancelled():
    app = VoiceAgentServerHost(configure_observability=None)
    receive_started = asyncio.Event()
    websocket = AsyncMock()
    terminating_sessions = []

    async def receive():
        receive_started.set()
        await asyncio.Future()

    websocket.receive.side_effect = receive

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    handler = asyncio.create_task(app._handle_voice_connection(websocket))  # pylint: disable=protected-access
    await receive_started.wait()
    handler.cancel()

    with pytest.raises(asyncio.CancelledError):
        await handler

    assert len(terminating_sessions) == 1


@pytest.mark.asyncio
async def test_connection_terminating_runs_once_under_repeated_cancellation():
    app = VoiceAgentServerHost(configure_observability=None)
    receive_started = asyncio.Event()
    websocket = AsyncMock()
    terminating_sessions = []

    async def receive():
        receive_started.set()
        await asyncio.Future()

    websocket.receive.side_effect = receive
    handler = None

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)
        assert handler is not None
        handler.cancel()

    handler = asyncio.create_task(app._handle_voice_connection(websocket))  # pylint: disable=protected-access
    await receive_started.wait()
    handler.cancel()

    with pytest.raises(asyncio.CancelledError):
        await handler

    assert len(terminating_sessions) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_point", ["receive", "close", "disconnect_callback"])
async def test_connection_terminating_runs_once_on_handler_failure(failure_point):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    terminating_sessions = []

    if failure_point == "receive":
        websocket.receive.side_effect = RuntimeError("receive")
    elif failure_point == "close":
        websocket.receive.return_value = {"type": "invalid"}
        websocket.close.side_effect = RuntimeError("close")
    else:
        websocket.receive.return_value = {"type": "websocket.disconnect", "code": 1006}

        @app.on_disconnect
        async def on_disconnect(_session, _event):
            raise RuntimeError("disconnect_callback")

    @app.on_connection_terminating
    def on_connection_terminating(session):
        terminating_sessions.append(session)

    with pytest.raises(RuntimeError, match=failure_point):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert len(terminating_sessions) == 1


@pytest.mark.asyncio
async def test_connection_terminating_failure_preserves_handler_failure(caplog):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()

    class HandlerFailure(Exception):
        pass

    websocket.receive.return_value = {
        "type": "websocket.receive",
        "text": json.dumps(
            _frame(
                "user.message",
                item_id="in_1",
                content=[{"type": "input_text", "text": "hello"}],
            )
        ),
    }

    @app.on_user_message
    async def on_user_message(_session, _event):
        raise HandlerFailure("primary")

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        raise RuntimeError("termination callback")

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        with pytest.raises(HandlerFailure, match="primary"):
            await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert "Voice connection termination callback failed" in caplog.text


@pytest.mark.asyncio
async def test_connection_terminating_cancellation_preserves_handler_failure(caplog):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.receive.side_effect = RuntimeError("primary")

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        raise asyncio.CancelledError("termination callback")

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        with pytest.raises(RuntimeError, match="primary"):
            await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert "Voice connection termination callback failed" in caplog.text


@pytest.mark.asyncio
async def test_connection_terminating_logging_failure_preserves_handler_failure(monkeypatch):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.receive.side_effect = RuntimeError("primary")

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        raise asyncio.CancelledError("termination callback")

    def fail_logging(*_args, **_kwargs):
        raise RuntimeError("logging")

    monkeypatch.setattr(voice_host_module.logger, "exception", fail_logging)

    with pytest.raises(RuntimeError, match="primary"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access


@pytest.mark.asyncio
async def test_connection_terminating_rejects_awaitable_result_without_leaking(caplog):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.receive.return_value = {"type": "invalid"}

    async def async_cleanup():
        raise AssertionError("must not run")

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        return async_cleanup()

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert "Connection terminating callback must return None" in caplog.text


@pytest.mark.asyncio
async def test_connection_terminating_cancels_returned_task(caplog):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.receive.return_value = {"type": "invalid"}
    cleanup_started = False
    returned_tasks = []

    async def async_cleanup():
        nonlocal cleanup_started
        cleanup_started = True

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        task = asyncio.create_task(async_cleanup())
        returned_tasks.append(task)
        return task

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access
    await asyncio.sleep(0)

    assert len(returned_tasks) == 1
    assert returned_tasks[0].cancelled()
    assert cleanup_started is False
    assert "Connection terminating callback must return None" in caplog.text


@pytest.mark.asyncio
async def test_connection_terminating_closes_custom_awaitable(caplog):
    app = VoiceAgentServerHost(configure_observability=None)
    websocket = AsyncMock()
    websocket.receive.return_value = {"type": "invalid"}
    returned_awaitables = []

    async def async_cleanup():
        raise AssertionError("must not run")

    class CustomAwaitable:
        def __init__(self):
            self.coroutine = async_cleanup()

        def __await__(self):
            return self.coroutine.__await__()

    @app.on_connection_terminating
    def on_connection_terminating(_session):
        awaitable = CustomAwaitable()
        returned_awaitables.append(awaitable)
        return awaitable

    with caplog.at_level(logging.ERROR, logger="azure.ai.agentserver"):
        await app._handle_voice_connection(websocket)  # pylint: disable=protected-access

    assert len(returned_awaitables) == 1
    assert returned_awaitables[0].coroutine.cr_frame is None
    assert "Connection terminating callback must return None" in caplog.text


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
