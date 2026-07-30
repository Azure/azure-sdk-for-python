# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tests for the typed Voice Live bridge host."""

import asyncio
import threading
from unittest import mock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import (
    ResponseCancellationOutcome,
    ResponseTimeoutEvent,
    SessionStartEvent,
    UserMessageEvent,
    VoiceAgentServerHost,
    VoiceProactiveResponseDroppedError,
    VoiceResponse,
    VoiceSession,
)
from azure.ai.agentserver.invocations.voice import _host as voice_host

_TS = "2026-07-23T12:00:00.000Z"


def _start(**overrides):
    payload = {
        "type": "session.start",
        "id": "m_start",
        "ts": _TS,
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {
            "first_output_ms": 15_000,
            "idle_ms": 30_000,
            "max_duration_ms": 120_000,
        },
    }
    payload.update(overrides)
    return payload


def _user_message(*, message_id: str = "m_user", item_id: str = "in_1", text: str = "hello"):
    return {
        "type": "user.message",
        "id": message_id,
        "ts": _TS,
        "item_id": item_id,
        "content": [{"type": "input_text", "text": text}],
    }


def _app() -> VoiceAgentServerHost:
    return VoiceAgentServerHost(configure_observability=None)


def _activate(websocket, **overrides):
    websocket.send_json(_start(**overrides))
    ready = websocket.receive_json()
    assert ready["type"] == "session.ready"
    assert "protocol_version" not in ready
    return ready


def test_non_streaming_response_opens_sdk_owned_response() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session: VoiceSession, event: UserMessageEvent, response: VoiceResponse) -> None:
        assert event.item_id == "in_1"
        assert event.text == "hello"
        await response.send_text("Echo: hello")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        item_done = websocket.receive_json()
        response_done = websocket.receive_json()

    assert created["type"] == "response.created"
    assert created["response_id"].startswith("r_")
    assert created["in_reply_to"] == ["in_1"]
    assert item_done["type"] == "response.output_text.done"
    assert item_done["response_id"] == created["response_id"]
    assert item_done["item_id"].startswith("it_")
    assert item_done["text"] == "Echo: hello"
    assert "output_index" not in item_done
    assert response_done["type"] == "response.done"
    assert response_done["response_id"] == created["response_id"]


def test_streamed_multi_item_response_uses_wire_order() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session: VoiceSession, _event: UserMessageEvent, response: VoiceResponse) -> None:
        first = response.new_text_item()
        await first.send_text_delta("Hello ")
        await first.send_text_delta("world", voice={"rate": "+10%"})
        await first.send_text_done()
        second = response.new_text_item()
        await second.send_text("How can I help?")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        messages = [websocket.receive_json() for _ in range(6)]

    assert [message["type"] for message in messages] == [
        "response.created",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.output_text.done",
        "response.done",
    ]


def test_streamed_multi_item_response_frames() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        first = response.new_text_item()
        await first.send_text_delta("one")
        await first.send_text_done()
        second = response.new_text_item()
        await second.send_text("two")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        delta = websocket.receive_json()
        first_done = websocket.receive_json()
        second_done = websocket.receive_json()
        response_done = websocket.receive_json()

    assert delta["item_id"] == first_done["item_id"]
    assert first_done["text"] == "one"
    assert second_done["item_id"] != first_done["item_id"]
    assert second_done["text"] == "two"
    assert response_done["response_id"] == created["response_id"]
    assert all("output_index" not in message for message in (delta, first_done, second_done))


def test_oversized_output_is_rejected_before_response_open() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        with pytest.raises(ValueError, match="maximum encoded text size"):
            await response.send_text("x" * (901 * 1024))
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"


def test_explicit_decline_emits_response_none_without_response_id() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.decline(reason="no_reply_needed")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        declined = websocket.receive_json()

    assert declined["type"] == "response.none"
    assert declined["in_reply_to"] == ["in_1"]
    assert declined["reason"] == "no_reply_needed"
    assert "response_id" not in declined


def test_callback_without_output_emits_response_scoped_error() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        return

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        error = websocket.receive_json()

    assert created["type"] == "response.created"
    assert error["type"] == "error"
    assert error["code"] == "handler_error"
    assert error["response_id"] == created["response_id"]


def test_no_input_is_a_normal_bridge_generated_turn() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_user_no_input
    async def on_no_input(_session, event, response) -> None:
        assert event.count == 2
        await response.send_text("Are you still there?")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "user.no_input",
                "id": "m_no_input",
                "ts": _TS,
                "item_id": "in_silence",
                "count": 2,
            }
        )
        created = websocket.receive_json()
        output = websocket.receive_json()
        done = websocket.receive_json()

    assert created["in_reply_to"] == ["in_silence"]
    assert output["text"] == "Are you still there?"
    assert done["type"] == "response.done"


def test_user_speech_started_dispatches_advisory_callback() -> None:
    app = _app()
    notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_user_speech_started
    async def on_speech(_session, _event) -> None:
        notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "user.speech_started",
                "id": "m_speech",
                "ts": _TS,
            }
        )
        assert notified.wait(timeout=1.0)


def test_raw_dtmf_key_dispatches_session_signal() -> None:
    app = _app()
    notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_dtmf_key
    async def on_dtmf(_session, event) -> None:
        assert event.digit == "1"
        notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "dtmf",
                "id": "m_dtmf",
                "ts": _TS,
                "digits": "1",
            }
        )
        assert notified.wait(timeout=1.0)


def test_self_cancelled_signal_callback_does_not_stop_dispatch() -> None:
    app = _app()
    signal_started = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("still running")

    @app.on_dtmf_key
    async def on_dtmf(_session, _event) -> None:
        signal_started.set()
        raise asyncio.CancelledError()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json({"type": "dtmf", "id": "m_dtmf", "ts": _TS, "digits": "1"})
        assert signal_started.wait(timeout=1.0)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["text"] == "still running"
        assert websocket.receive_json()["type"] == "response.done"


def test_missing_required_callback_rejects_activation() -> None:
    app = _app()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_start())
            rejected = websocket.receive_json()
            assert rejected["type"] == "session.rejected"
            assert rejected["code"] == "startup_failed"
            websocket.receive_json()

    assert exc_info.value.code == 1011


def test_application_frame_during_startup_callback_rejects_activation() -> None:
    app = _app()
    startup_started = threading.Event()
    startup_cancelled = threading.Event()

    @app.on_session_start
    async def on_start(_session, _event) -> None:
        startup_started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            startup_cancelled.set()
            raise

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_start())
            assert startup_started.wait(timeout=1.0)
            websocket.send_json(_user_message())
            rejection = websocket.receive_json()
            assert rejection["type"] == "session.rejected"
            assert rejection["code"] == "protocol_mismatch"
            assert rejection["retriable"] is False
            websocket.receive_json()

    assert exc_info.value.code == 1008
    assert startup_cancelled.wait(timeout=1.0)


def test_exact_duplicate_session_start_is_ignored_during_activation() -> None:
    app = _app()
    startup_started = threading.Event()
    finish_startup = threading.Event()

    @app.on_session_start
    async def on_start(_session, _event) -> None:
        startup_started.set()
        await asyncio.to_thread(finish_startup.wait)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        start = _start()
        websocket.send_json(start)
        assert startup_started.wait(timeout=1.0)
        websocket.send_json(start)
        finish_startup.set()
        assert websocket.receive_json()["type"] == "session.ready"


def test_startup_context_is_immutable_and_ready_has_no_version() -> None:
    app = _app()
    starts: list[SessionStartEvent] = []

    @app.on_session_start
    async def on_start(_session: VoiceSession, event: SessionStartEvent) -> None:
        starts.append(event)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(
            websocket,
            greeting="Welcome",
            no_input_timeout_ms=8_000,
            caller={"channel": "pstn", "nested": {"key": "value"}},
        )

    assert starts[0].greeting == "Welcome"
    assert starts[0].no_input_timeout_ms == 8_000
    with pytest.raises(TypeError):
        starts[0].caller["channel"] = "websocket"  # type: ignore[index]


def test_reconnect_greeting_is_rejected() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_start(reconnect=True, greeting="Welcome"))
            assert websocket.receive_json()["code"] == "invalid_session_start"
            websocket.receive_json()

    assert exc_info.value.code == 1002


def test_pre_response_timeout_cancels_generation_before_notification() -> None:
    app = _app()
    callback_started = threading.Event()
    callback_cancelled = threading.Event()
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        callback_started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            assert response.cancellation.is_cancelled
            callback_cancelled.set()
            raise

    @app.on_response_timeout
    async def on_timeout(_session: VoiceSession, event: ResponseTimeoutEvent) -> None:
        assert event.response_id is None
        assert event.item_ids == ("in_1",)
        assert callback_cancelled.is_set()
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert callback_started.wait(timeout=1.0)
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_timeout",
                "ts": _TS,
                "item_ids": ["in_1"],
                "stage": "first_output",
            }
        )
        assert timeout_notified.wait(timeout=2.0)


def test_open_response_timeout_cancels_generation() -> None:
    app = _app()
    callback_cancelled = threading.Event()
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text_delta("hello")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            callback_cancelled.set()
            raise

    @app.on_response_timeout
    async def on_timeout(_session, event: ResponseTimeoutEvent) -> None:
        assert event.response_id is not None
        assert callback_cancelled.is_set()
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        assert websocket.receive_json()["type"] == "response.output_text.delta"
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_timeout",
                "ts": _TS,
                "response_id": created["response_id"],
                "stage": "idle",
            }
        )
        assert timeout_notified.wait(timeout=2.0)


def test_pre_response_timeout_after_local_response_created_is_reconciled() -> None:
    app = _app()
    callback_cancelled = threading.Event()
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, event, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.send_text_delta("first")
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                assert response.cancellation.is_cancelled
                callback_cancelled.set()
                raise
        else:
            await response.send_text("second")

    @app.on_response_timeout
    async def on_timeout(_session, event: ResponseTimeoutEvent) -> None:
        assert event.response_id is None
        assert event.item_ids == ("in_1",)
        assert callback_cancelled.is_set()
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.delta"
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_late_pre_response_timeout",
                "ts": _TS,
                "item_ids": ["in_1"],
                "stage": "first_output",
            }
        )
        assert timeout_notified.wait(timeout=2.0)
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"


def test_late_timeout_can_cover_resolved_prefix_and_inflight_input() -> None:
    app = _app()
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, event, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await asyncio.sleep(0.05)
            await response.send_text_delta("first")
            await asyncio.Event().wait()
        else:
            await response.send_text("third")

    @app.on_response_timeout
    async def on_timeout(_session, event: ResponseTimeoutEvent) -> None:
        assert event.item_ids == ("in_1", "in_2")
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.delta"
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_late_batch_timeout",
                "ts": _TS,
                "item_ids": ["in_1", "in_2"],
                "stage": "first_output",
            }
        )
        assert timeout_notified.wait(timeout=2.0)
        websocket.send_json(_user_message(message_id="m_user_3", item_id="in_3"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"


def test_pre_response_timeout_after_local_decline_is_reconciled() -> None:
    app = _app()
    declined_response: list[VoiceResponse] = []
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, event, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            declined_response.append(response)
            await response.decline()
        else:
            await response.send_text("second")

    @app.on_response_timeout
    async def on_timeout(_session, event: ResponseTimeoutEvent) -> None:
        assert event.item_ids == ("in_1",)
        assert declined_response[0].cancellation.is_cancelled
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_late_decline_timeout",
                "ts": _TS,
                "item_ids": ["in_1"],
                "stage": "first_output",
            }
        )
        assert timeout_notified.wait(timeout=2.0)
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"


def test_timeout_processed_while_decline_write_blocked_keeps_single_terminal() -> None:
    """Barrier race: a response.timeout must be processed by the receive pump
    while the decline's response.none write is suspended, and exactly one
    response.none reaches the wire.

    ``response.none`` carries no response_id, so ``send()`` cannot guard it via
    the response-scoped terminal check. The write is also performed outside
    ``_state_lock``; if it were held across the write, the receive pump could not
    acquire it to run ``_handle_response_timeout`` while the write stalled and
    ``timeout_seen`` would never fire (this test would hang).
    """
    app = _app()
    timeout_seen = threading.Event()
    write_blocked = threading.Event()
    release_write = threading.Event()
    original_send_text = WebSocket.send_text
    original_handle_timeout = voice_host._VoiceConnection._handle_response_timeout

    async def blocking_send_text(self: WebSocket, data: str) -> None:
        if '"response.none"' in data and not release_write.is_set():
            write_blocked.set()
            await asyncio.to_thread(release_write.wait)
        await original_send_text(self, data)

    async def handle_timeout(self, event):
        # Runs inside the receive pump (not the serialized callback worker), so it
        # is a liveness signal that the pump is not blocked behind the stalled write.
        timeout_seen.set()
        return await original_handle_timeout(self, event)

    @app.on_user_message
    async def on_message(_session, event: UserMessageEvent, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.decline()
        else:
            await response.send_text("second")

    with mock.patch.object(WebSocket, "send_text", blocking_send_text), mock.patch.object(
        voice_host._VoiceConnection, "_handle_response_timeout", handle_timeout
    ):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            # The decline's response.none write is now suspended mid-flight.
            assert write_blocked.wait(2.0)
            # A timeout for the same prefix must still be processed while the write
            # stalls — the receive pump must not be blocked behind it.
            websocket.send_json(
                {
                    "type": "response.timeout",
                    "id": "m_race_timeout",
                    "ts": _TS,
                    "item_ids": ["in_1"],
                    "stage": "first_output",
                }
            )
            assert timeout_seen.wait(2.0)
            # Release the write; exactly one response.none reaches the wire and the
            # connection stays healthy for the next turn (no second terminal, no crash).
            release_write.set()
            none_frame = websocket.receive_json()
            assert none_frame["type"] == "response.none"
            assert none_frame["in_reply_to"] == ["in_1"]
            websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
            assert websocket.receive_json()["type"] == "response.created"
            assert websocket.receive_json()["type"] == "response.output_text.done"
            assert websocket.receive_json()["type"] == "response.done"


def test_response_timeout_after_local_done_is_reconciled() -> None:
    app = _app()
    completed_response: list[VoiceResponse] = []
    timeout_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        completed_response.append(response)
        await response.send_text("hello")

    @app.on_response_timeout
    async def on_timeout(_session, event: ResponseTimeoutEvent) -> None:
        assert event.response_id == completed_response[0].response_id
        assert completed_response[0].cancellation.is_cancelled
        timeout_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_late_done_timeout",
                "ts": _TS,
                "response_id": created["response_id"],
                "stage": "max_duration",
            }
        )
        assert timeout_notified.wait(timeout=2.0)


def test_timeout_suppresses_late_barge_in_and_next_turn_continues() -> None:
    app = _app()
    timeout_notified = threading.Event()
    barge_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, event, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.send_text_delta("first")
            await asyncio.Event().wait()
        else:
            await response.send_text("second")

    @app.on_response_timeout
    async def on_timeout(_session, _event) -> None:
        timeout_notified.set()

    @app.on_barge_in
    async def on_barge(_session, _event) -> None:
        barge_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        first_created = websocket.receive_json()
        first_delta = websocket.receive_json()
        websocket.send_json(
            {
                "type": "response.timeout",
                "id": "m_timeout",
                "ts": _TS,
                "response_id": first_created["response_id"],
                "stage": "idle",
            }
        )
        assert timeout_notified.wait(timeout=2.0)
        websocket.send_json(
            {
                "type": "barge_in",
                "id": "m_late_barge",
                "ts": _TS,
                "response_id": first_created["response_id"],
                "item_id": first_delta["item_id"],
                "heard_text": "fir",
            }
        )
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"

    assert not barge_notified.is_set()


def test_barge_in_cancels_generation_before_callback() -> None:
    app = _app()
    callback_cancelled = threading.Event()
    barge_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text_delta("hello")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            assert response.cancellation.is_cancelled
            callback_cancelled.set()
            raise

    @app.on_barge_in
    async def on_barge(_session, event) -> None:
        assert event.heard_text == "hel"
        assert callback_cancelled.is_set()
        barge_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        delta = websocket.receive_json()
        websocket.send_json(
            {
                "type": "barge_in",
                "id": "m_barge",
                "ts": _TS,
                "response_id": created["response_id"],
                "item_id": delta["item_id"],
                "heard_text": "hel",
            }
        )
        assert barge_notified.wait(timeout=2.0)


def test_late_barge_in_after_response_done_is_dispatched() -> None:
    app = _app()
    barge_notified = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("complete")

    @app.on_barge_in
    async def on_barge(_session, event) -> None:
        assert event.heard_text == "comp"
        barge_notified.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        item_done = websocket.receive_json()
        assert websocket.receive_json()["type"] == "response.done"
        websocket.send_json(
            {
                "type": "barge_in",
                "id": "m_barge",
                "ts": _TS,
                "response_id": created["response_id"],
                "item_id": item_done["item_id"],
                "heard_text": "comp",
            }
        )
        assert barge_notified.wait(timeout=1.0)


def test_self_cancel_resolves_from_response_cancelled() -> None:
    app = _app()
    outcome_received = threading.Event()
    outcomes: list[ResponseCancellationOutcome] = []

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text_delta("incorrect")
        outcomes.append(await response.cancel(reason="self_correction"))
        outcome_received.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        delta = websocket.receive_json()
        cancel = websocket.receive_json()
        assert cancel["type"] == "response.cancel"
        websocket.send_json(
            {
                "type": "response.cancelled",
                "id": "m_cancelled",
                "ts": _TS,
                "response_id": created["response_id"],
                "item_id": delta["item_id"],
                "heard_text": "inc",
            }
        )
        assert outcome_received.wait(timeout=1.0)

    assert outcomes == [
        ResponseCancellationOutcome(
            response_id=created["response_id"],
            kind="cancelled",
            heard_text="inc",
            item_id=delta["item_id"],
        )
    ]


def test_proactive_response_waits_for_acceptance() -> None:
    app = _app()
    proactive_done = threading.Event()

    @app.on_user_message
    async def on_message(session: VoiceSession, event, response: VoiceResponse) -> None:
        if event.item_id != "in_1":
            await response.send_text("next")
            return
        await response.decline()
        proactive = await session.start_proactive_response(supersede_key="job-1")
        await proactive.send_text("Your job completed")
        await proactive.done()
        proactive_done.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        proactive_created = websocket.receive_json()
        assert proactive_created["type"] == "response.created"
        assert "in_reply_to" not in proactive_created
        websocket.send_json(
            {
                "type": "response.accepted",
                "id": "m_accepted",
                "ts": _TS,
                "response_id": proactive_created["response_id"],
            }
        )
        output = websocket.receive_json()
        done = websocket.receive_json()
        assert proactive_done.wait(timeout=1.0)

    assert output["type"] == "response.output_text.done"
    assert done["type"] == "response.done"


def test_proactive_drop_raises_typed_error() -> None:
    app = _app()
    dropped = threading.Event()
    reasons: list[str] = []

    @app.on_user_message
    async def on_message(session: VoiceSession, _event, response: VoiceResponse) -> None:
        await response.decline()
        try:
            await session.start_proactive_response()
        except VoiceProactiveResponseDroppedError as exc:
            reasons.append(exc.reason)
            dropped.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        proactive_created = websocket.receive_json()
        websocket.send_json(
            {
                "type": "response.dropped",
                "id": "m_dropped",
                "ts": _TS,
                "response_id": proactive_created["response_id"],
                "reason": "no_barge_safe_window",
            }
        )
        assert dropped.wait(timeout=1.0)

    assert reasons == ["no_barge_safe_window"]


def test_proactive_request_can_supersede_pending_request() -> None:
    app = _app()
    completed = threading.Event()
    drop_reasons: list[str] = []

    @app.on_user_message
    async def on_message(session: VoiceSession, _event, response: VoiceResponse) -> None:
        await response.decline()
        first = asyncio.create_task(session.start_proactive_response(supersede_key="job-1"))
        await asyncio.sleep(0)
        second = asyncio.create_task(session.start_proactive_response(supersede_key="job-1"))
        try:
            await first
        except VoiceProactiveResponseDroppedError as exc:
            drop_reasons.append(exc.reason)
        accepted = await second
        await accepted.send_text("Latest status")
        await accepted.done()
        completed.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        first_created = websocket.receive_json()
        second_created = websocket.receive_json()
        assert first_created["supersede_key"] == "job-1"
        assert second_created["supersede_key"] == "job-1"
        websocket.send_json(
            {
                "type": "response.dropped",
                "id": "m_superseded",
                "ts": _TS,
                "response_id": first_created["response_id"],
                "reason": "superseded",
            }
        )
        websocket.send_json(
            {
                "type": "response.accepted",
                "id": "m_accepted",
                "ts": _TS,
                "response_id": second_created["response_id"],
            }
        )
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"
        assert completed.wait(timeout=1.0)

    assert drop_reasons == ["superseded"]


def test_cancelling_proactive_admission_sends_response_cancel() -> None:
    app = _app()
    cancel_admission = threading.Event()
    customer_cancelled = threading.Event()

    @app.on_user_message
    async def on_message(session: VoiceSession, event, response: VoiceResponse) -> None:
        if event.item_id != "in_1":
            await response.send_text("next")
            return
        await response.decline()
        admission = asyncio.create_task(session.start_proactive_response())
        await asyncio.to_thread(cancel_admission.wait)
        admission.cancel()
        with pytest.raises(asyncio.CancelledError):
            await admission
        customer_cancelled.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        proactive_created = websocket.receive_json()
        cancel_admission.set()
        cancel = websocket.receive_json()
        assert cancel["type"] == "response.cancel"
        assert cancel["response_id"] == proactive_created["response_id"]
        assert customer_cancelled.wait(timeout=1.0)
        websocket.send_json(
            {
                "type": "response.dropped",
                "id": "m_dropped",
                "ts": _TS,
                "response_id": proactive_created["response_id"],
                "reason": "cancelled_by_agent",
            }
        )
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"


def test_dtmf_collection_request_and_collected_turn() -> None:
    app = _app()
    collection_ids: list[str] = []

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text("Enter digits")
        collection_ids.append(
            await response.collect_dtmf(
                max_digits=4,
                terminator="#",
                initial_timeout_ms=10_000,
                inter_digit_timeout_ms=5_000,
            )
        )

    @app.on_dtmf_collected
    async def on_collected(_session, event, response: VoiceResponse) -> None:
        assert event.collection_id == collection_ids[0]
        assert event.digits == "1234"
        await response.send_text("Digits received")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        collect = websocket.receive_json()
        assert collect["type"] == "dtmf.collect"
        assert collect["collection_id"].startswith("dc_")
        assert collect["max_digits"] == 4
        assert collect["terminator"] == "#"
        assert websocket.receive_json()["type"] == "response.done"

        websocket.send_json(
            {
                "type": "dtmf",
                "id": "m_dtmf_collected",
                "ts": _TS,
                "collection_id": collect["collection_id"],
                "item_id": "in_dtmf",
                "digits": "1234",
                "completion_reason": "max_digits",
            }
        )
        created = websocket.receive_json()
        output = websocket.receive_json()
        done = websocket.receive_json()

    assert created["in_reply_to"] == ["in_dtmf"]
    assert output["text"] == "Digits received"
    assert done["type"] == "response.done"


def test_dtmf_collection_rejection_releases_slot() -> None:
    app = _app()
    rejected = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text("Enter digits")
        await response.collect_dtmf(
            max_digits=1,
            initial_timeout_ms=1_000,
            inter_digit_timeout_ms=1_000,
        )

    @app.on_dtmf_collection_rejected
    async def on_rejected(_session, event) -> None:
        assert event.reason == "invalid_configuration"
        rejected.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        websocket.receive_json()
        websocket.receive_json()
        collect = websocket.receive_json()
        websocket.receive_json()
        websocket.send_json(
            {
                "type": "dtmf.collect.rejected",
                "id": "m_rejected",
                "ts": _TS,
                "collection_id": collect["collection_id"],
                "reason": "invalid_configuration",
            }
        )
        assert rejected.wait(timeout=1.0)


def test_dtmf_collection_can_be_cancelled_explicitly() -> None:
    app = _app()
    cancel_requested = threading.Event()
    cancelled = threading.Event()
    cancellation_tasks: list[asyncio.Task[None]] = []

    @app.on_user_message
    async def on_message(session: VoiceSession, _event, response: VoiceResponse) -> None:
        await response.send_text("Enter digits")
        collection_id = await response.collect_dtmf(
            max_digits=4,
            initial_timeout_ms=5_000,
            inter_digit_timeout_ms=2_000,
            terminator="#",
        )

        async def cancel_when_requested() -> None:
            await asyncio.to_thread(cancel_requested.wait)
            await session.cancel_dtmf_collection(collection_id)

        cancellation_tasks.append(asyncio.create_task(cancel_when_requested()))

    @app.on_dtmf_collection_cancelled
    async def on_cancelled(_session, event) -> None:
        assert event.reason == "cancelled_by_agent"
        cancelled.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        collect = websocket.receive_json()
        assert collect["type"] == "dtmf.collect"
        assert websocket.receive_json()["type"] == "response.done"
        cancel_requested.set()
        cancel = websocket.receive_json()
        assert cancel == {
            "type": "dtmf.collect.cancel",
            "id": cancel["id"],
            "ts": cancel["ts"],
            "collection_id": collect["collection_id"],
        }
        websocket.send_json(
            {
                "type": "dtmf.collect.cancelled",
                "id": "m_cancelled",
                "ts": _TS,
                "collection_id": collect["collection_id"],
                "reason": "cancelled_by_agent",
            }
        )
        assert cancelled.wait(timeout=1.0)

    assert cancellation_tasks[0].done()
    assert cancellation_tasks[0].exception() is None


def test_dtmf_source_cancellation_can_race_agent_cancel() -> None:
    app = _app()
    cancel_requested = threading.Event()
    cancelled = threading.Event()
    cancel_rejected = threading.Event()
    cancellation_tasks: list[asyncio.Task[None]] = []

    @app.on_user_message
    async def on_message(session: VoiceSession, _event, response: VoiceResponse) -> None:
        await response.send_text("Enter digits")
        collection_id = await response.collect_dtmf(
            max_digits=4,
            initial_timeout_ms=5_000,
            inter_digit_timeout_ms=2_000,
        )

        async def cancel_when_requested() -> None:
            await asyncio.to_thread(cancel_requested.wait)
            await session.cancel_dtmf_collection(collection_id)

        cancellation_tasks.append(asyncio.create_task(cancel_when_requested()))

    @app.on_dtmf_collection_cancelled
    async def on_cancelled(_session, event) -> None:
        assert event.reason == "speech_input"
        cancelled.set()

    @app.on_dtmf_collection_rejected
    async def on_rejected(_session, event) -> None:
        assert event.reason == "collection_not_found"
        cancel_rejected.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        websocket.receive_json()
        websocket.receive_json()
        collect = websocket.receive_json()
        websocket.receive_json()
        cancel_requested.set()
        assert websocket.receive_json()["type"] == "dtmf.collect.cancel"
        websocket.send_json(
            {
                "type": "dtmf.collect.cancelled",
                "id": "m_cancelled",
                "ts": _TS,
                "collection_id": collect["collection_id"],
                "reason": "speech_input",
            }
        )
        websocket.send_json(
            {
                "type": "dtmf.collect.rejected",
                "id": "m_rejected",
                "ts": _TS,
                "collection_id": collect["collection_id"],
                "reason": "collection_not_found",
            }
        )
        assert cancelled.wait(timeout=1.0)
        assert cancel_rejected.wait(timeout=1.0)

    assert cancellation_tasks[0].done()
    assert cancellation_tasks[0].exception() is None


def test_handoff_is_terminal_and_failed_handoff_opens_recovery_turn() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text("Connecting you")
        await response.handoff(target="billing", message="Please hold")

    @app.on_handoff_failed
    async def on_handoff_failed(_session, event, response: VoiceResponse) -> None:
        assert event.target == "billing"
        assert event.code == "target_unavailable"
        await response.send_text("I will keep helping")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        created = websocket.receive_json()
        assert websocket.receive_json()["type"] == "response.output_text.done"
        handoff = websocket.receive_json()
        assert handoff["type"] == "handoff"
        assert handoff["response_id"] == created["response_id"]
        assert handoff["target"] == "billing"
        assert handoff["message"] == "Please hold"

        websocket.send_json(
            {
                "type": "handoff.failed",
                "id": "m_handoff_failed",
                "ts": _TS,
                "item_id": "in_recovery",
                "target": "billing",
                "code": "target_unavailable",
            }
        )
        recovery_created = websocket.receive_json()
        recovery_output = websocket.receive_json()
        recovery_done = websocket.receive_json()

    assert recovery_created["in_reply_to"] == ["in_recovery"]
    assert recovery_output["text"] == "I will keep helping"
    assert recovery_done["type"] == "response.done"


def test_history_mutation_result_precedes_dependent_turn() -> None:
    app = _app()
    history: list[str] = []

    @app.on_conversation_item_create
    async def on_create(_session, event) -> None:
        history.append(event.item.item_id)

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        assert history == ["hi_1"]
        await response.send_text("history applied")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "conversation.item.create",
                "id": "m_history",
                "ts": _TS,
                "item": {
                    "id": "hi_1",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "order 42"}],
                },
            }
        )
        websocket.send_json(_user_message())
        mutation_result = websocket.receive_json()
        assert mutation_result == {
            "type": "conversation.item.created",
            "id": mutation_result["id"],
            "ts": mutation_result["ts"],
            "request_id": "m_history",
        }
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["text"] == "history applied"
        assert websocket.receive_json()["type"] == "response.done"


def test_history_callback_failure_emits_correlated_failure() -> None:
    app = _app()

    @app.on_conversation_item_delete
    async def on_delete(_session, _event) -> None:
        raise RuntimeError("private storage detail")

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "conversation.item.delete",
                "id": "m_delete",
                "ts": _TS,
                "item_id": "hi_1",
            }
        )
        failure = websocket.receive_json()

    assert failure["type"] == "conversation.item.failed"
    assert failure["request_id"] == "m_delete"
    assert failure["code"] == "mutation_failed"
    assert "private storage detail" not in failure["message"]


def test_history_without_registered_callback_emits_mutation_failure() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "conversation.item.delete",
                "id": "m_delete",
                "ts": _TS,
                "item_id": "hi_1",
            }
        )
        failure = websocket.receive_json()

    assert failure["type"] == "conversation.item.failed"
    assert failure["request_id"] == "m_delete"
    assert failure["code"] == "mutation_failed"


def test_exact_duplicate_is_ignored_but_next_turn_runs() -> None:
    app = _app()
    seen: list[str] = []

    @app.on_user_message
    async def on_message(_session, event, response) -> None:
        seen.append(event.item_id)
        await response.send_text(event.text)

    first = _user_message()
    second = _user_message(message_id="m_user_2", item_id="in_2", text="world")
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(first)
        for _ in range(3):
            websocket.receive_json()
        websocket.send_json(first)
        websocket.send_json(second)
        for _ in range(3):
            websocket.receive_json()

    assert seen == ["in_1", "in_2"]


def test_unknown_future_message_is_ignored_after_readiness() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("still ready")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json({"type": "future.signal", "id": "m_future", "ts": _TS})
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["text"] == "still ready"
        assert websocket.receive_json()["type"] == "response.done"


def test_known_wrong_direction_message_closes_connection() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(
                {
                    "type": "response.created",
                    "id": "m_wrong_direction",
                    "ts": _TS,
                    "response_id": "r_peer",
                    "in_reply_to": ["in_1"],
                }
            )
            websocket.receive_json()

    assert exc_info.value.code == 1008


def test_unknown_playback_response_id_closes_connection() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(
                {
                    "type": "barge_in",
                    "id": "m_unknown_barge",
                    "ts": _TS,
                    "response_id": "r_unknown",
                    "item_id": "it_unknown",
                    "heard_text": "",
                }
            )
            websocket.receive_json()

    assert exc_info.value.code == 1008


def test_changed_payload_under_same_message_id_closes_1008() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            assert websocket.receive_json()["type"] == "response.none"
            websocket.send_json(_user_message(text="changed"))
            websocket.receive_json()

    assert exc_info.value.code == 1008


def test_consumed_input_item_id_cannot_be_reused() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            assert websocket.receive_json()["type"] == "response.none"
            websocket.send_json(_user_message(message_id="m_user_2", item_id="in_1"))
            websocket.receive_json()

    assert exc_info.value.code == 1008


def test_session_end_is_delivered_before_graceful_teardown() -> None:
    app = _app()
    ended = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_session_end
    async def on_session_end(_session, event) -> None:
        assert event.reason == "caller_hangup"
        ended.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_session_end",
                "ts": _TS,
                "reason": "caller_hangup",
            }
        )
        assert ended.wait(timeout=1.0)


def test_cancellation_resistant_signal_does_not_block_teardown(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)
    app = _app()
    started = threading.Event()
    cancellation_seen = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_dtmf_key
    async def on_dtmf(_session, _event) -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancellation_seen.set()
            await asyncio.Event().wait()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json({"type": "dtmf", "id": "m_dtmf", "ts": _TS, "digits": "1"})
        assert started.wait(timeout=1.0)
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_session_end",
                "ts": _TS,
                "reason": "caller_hangup",
            }
        )
        assert cancellation_seen.wait(timeout=1.0)


def test_end_call_supports_immediate_mode() -> None:
    app = _app()

    @app.on_user_message
    async def on_message(session: VoiceSession, _event, response: VoiceResponse) -> None:
        await response.send_text("Goodbye")
        await session.end_call(reason="abuse", mode="immediate")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        end_call = websocket.receive_json()

    assert end_call["type"] == "end_call"
    assert end_call["reason"] == "abuse"
    assert end_call["mode"] == "immediate"


def test_typed_host_rejects_raw_ws_handler_replacement() -> None:
    app = _app()

    with pytest.raises(RuntimeError, match="owns /invocations_ws"):

        @app.ws_handler
        async def raw_handler(_websocket) -> None:
            return


def test_voice_protocol_metrics_are_emitted(monkeypatch) -> None:
    class FakeInstrument:
        def __init__(self) -> None:
            self.calls: list[tuple[float, dict]] = []

        def add(self, value, attributes=None) -> None:
            self.calls.append((value, attributes or {}))

        def record(self, value, attributes=None) -> None:
            self.calls.append((value, attributes or {}))

    activations = FakeInstrument()
    first_output = FakeInstrument()
    terminals = FakeInstrument()
    active_connections = FakeInstrument()
    close_codes = FakeInstrument()
    monkeypatch.setattr(voice_host, "_ACTIVATION_COUNTER", activations)
    monkeypatch.setattr(voice_host, "_FIRST_OUTPUT_DURATION", first_output)
    monkeypatch.setattr(voice_host, "_TERMINAL_COUNTER", terminals)
    monkeypatch.setattr(voice_host, "_ACTIVE_CONNECTIONS", active_connections)
    monkeypatch.setattr(voice_host, "_CLOSE_CODE_COUNTER", close_codes)

    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.send_text("metrics")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        websocket.receive_json()
        websocket.receive_json()
        websocket.receive_json()

    assert (1, {"result": "ready"}) in activations.calls
    assert len(first_output.calls) == 1
    assert (1, {"kind": "done"}) in terminals.calls
    assert active_connections.calls[0][0] == 1
    assert active_connections.calls[-1][0] == -1
    assert close_codes.calls
