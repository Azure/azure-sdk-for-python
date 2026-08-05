# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end tests for the typed Voice Live bridge host."""

import asyncio
import json
import threading
import time
from unittest import mock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations.voice import (
    HandoffFailedEvent,
    ResponseCancellationOutcome,
    ResponseTimeoutEvent,
    SessionStartEvent,
    UserMessageEvent,
    VoiceAgentServerHost,
    VoiceBridgeConnectionClosedError,
    VoiceProactiveResponseDroppedError,
    VoiceResponse,
    VoiceSession,
)
from azure.ai.agentserver.invocations.voice import _host as voice_host
from azure.ai.agentserver.invocations.voice import _runtime as voice_runtime

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


def _connection(websocket, **callbacks):
    callback_values = {
        "on_session_start": None,
        "on_user_message": None,
        "on_user_no_input": None,
        "on_user_speech_started": None,
        "on_dtmf_key": None,
        "on_dtmf_collected": None,
        "on_dtmf_collection_rejected": None,
        "on_dtmf_collection_cancelled": None,
        "on_handoff_failed": None,
        "on_conversation_item_create": None,
        "on_conversation_item_delete": None,
        "on_barge_in": None,
        "on_response_timeout": None,
        "on_session_end": None,
    }
    callback_values.update(callbacks)
    return voice_host._VoiceConnection(websocket=websocket, **callback_values)  # pylint: disable=protected-access


class _QueueWebSocket:
    def __init__(self) -> None:
        self.inbound: asyncio.Queue[dict] = asyncio.Queue()
        self.sent: list[dict] = []
        self.closes: list[dict] = []
        self.ready_started = asyncio.Event()

    async def receive(self) -> dict:
        return await self.inbound.get()

    async def send_text(self, data: str) -> None:
        payload = json.loads(data)
        self.sent.append(payload)
        if payload["type"] == "session.ready":
            self.ready_started.set()

    async def close(self, **fields) -> None:
        self.closes.append(fields)


def _receive_message(payload: dict) -> dict:
    return {"type": "websocket.receive", "text": json.dumps(payload)}


def test_voice_host_configures_one_mib_websocket_limit() -> None:
    config = _app()._build_hypercorn_config("127.0.0.1", 8088)  # pylint: disable=protected-access

    assert config.websocket_max_message_size == 1024 * 1024


def test_ready_gate_accepts_frame_sent_immediately_after_ready() -> None:
    async def scenario() -> None:
        websocket = _QueueWebSocket()
        await websocket.inbound.put(_receive_message(_start()))

        async def on_user_message(_session, _event, response) -> None:
            await response.decline()

        connection = _connection(websocket, on_user_message=on_user_message)

        async def compliant_peer() -> None:
            await websocket.ready_started.wait()
            await websocket.inbound.put(_receive_message(_user_message()))

        peer_task = asyncio.create_task(compliant_peer())
        assert await connection._activate()  # pylint: disable=protected-access
        await peer_task
        payload = await connection._receive_with_worker_supervision()  # pylint: disable=protected-access

        assert payload is not None
        assert payload["type"] == "user.message"
        assert [message["type"] for message in websocket.sent] == ["session.ready"]
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_ready_gate_rejects_unambiguously_early_frame() -> None:
    async def scenario() -> None:
        websocket = _QueueWebSocket()
        connection = _connection(websocket)
        await websocket.inbound.put(_receive_message(_user_message()))

        assert not await connection._send_ready_with_receive_gate()  # pylint: disable=protected-access
        assert [message["type"] for message in websocket.sent] == ["session.rejected"]
        assert websocket.closes[-1]["code"] == 1008
        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

    asyncio.run(scenario())


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


def test_first_output_item_is_owned_while_wire_send_is_in_flight() -> None:
    async def scenario() -> None:
        ownership_seen: list[bool] = []

        class Sender:
            ending = False
            response: VoiceResponse

            async def open_response(self, _response_id, _in_reply_to) -> bool:
                return True

            async def send(self, message_type, **fields) -> None:
                if message_type == "response.output_text.delta":
                    ownership_seen.append(
                        self.response._owns_item_id(fields["item_id"])  # pylint: disable=protected-access
                    )

        sender = Sender()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            sender,
            response_id="r_1",
            in_reply_to=("in_1",),
        )
        sender.response = response

        await response.send_text_delta("first")

        assert ownership_seen == [True]

    asyncio.run(scenario())


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


def test_json_escape_expansion_is_rejected_by_final_wire_budget(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_MAX_FRAME_BYTES", 300)
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        with pytest.raises(ValueError, match="frame exceeds"):
            await response.send_text("\x00" * 50)
        await response.fail(code="output_too_large", message="Output was too large")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "error"


def test_oversized_non_text_field_is_rejected_before_json_encoding(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_FRAME_BYTES", 100)
        connection = _connection(None)

        with pytest.raises(ValueError, match="fields exceed"):
            await connection.send("handoff", target="x" * 101)

        assert not connection.ending

    asyncio.run(scenario())


def test_oversized_inbound_frame_closes_1009(monkeypatch) -> None:
    app = _app()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.decline()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        monkeypatch.setattr(voice_host, "_MAX_FRAME_BYTES", 200)
        websocket.send_json(_user_message(text="x" * 256))
        with pytest.raises(WebSocketDisconnect) as exc_info:
            websocket.receive_json()

    assert exc_info.value.code == 1009


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


def test_readiness_send_failure_still_shuts_down(monkeypatch) -> None:
    app = _app()
    shutdown_calls: list[bool] = []

    original_send = voice_host._VoiceConnection.send
    original_shutdown = voice_host._VoiceConnection._shutdown_runtime

    async def fail_readiness(self, message_type, **fields) -> None:
        if message_type == "session.ready":
            raise RuntimeError("readiness send failed")
        await original_send(self, message_type, **fields)

    async def capture_shutdown(self, *, drain_callbacks) -> None:
        shutdown_calls.append(drain_callbacks)
        await original_shutdown(self, drain_callbacks=drain_callbacks)

    monkeypatch.setattr(voice_host._VoiceConnection, "send", fail_readiness)
    monkeypatch.setattr(voice_host._VoiceConnection, "_shutdown_runtime", capture_shutdown)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            websocket.send_json(_start())
            websocket.receive_json()

    assert exc_info.value.code == 1011
    assert shutdown_calls == [False]


def test_activation_cancellation_still_runs_shutdown(monkeypatch) -> None:
    shutdown_calls: list[bool] = []

    async def cancel_activation(_self) -> bool:
        raise asyncio.CancelledError()

    async def capture_shutdown(_self, *, drain_callbacks) -> None:
        shutdown_calls.append(drain_callbacks)

    monkeypatch.setattr(voice_host._VoiceConnection, "_activate", cancel_activation)
    monkeypatch.setattr(voice_host._VoiceConnection, "_shutdown_runtime", capture_shutdown)

    async def run_connection() -> None:
        connection = object.__new__(voice_host._VoiceConnection)  # pylint: disable=protected-access
        await connection.run()

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(run_connection())

    assert shutdown_calls == [False]


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


def test_batch_timeout_completes_every_cancel_waiter() -> None:
    async def scenario() -> None:
        connection = _connection(None)
        first = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_1",
            in_reply_to=("in_1",),
            wire_opened=True,
        )
        second = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_2",
            in_reply_to=("in_2",),
            wire_opened=True,
        )
        connection._resolved_input_prefixes[("in_1",)] = (first, True)  # pylint: disable=protected-access
        connection._resolved_input_prefixes[("in_2",)] = (second, True)  # pylint: disable=protected-access
        first_waiter = asyncio.get_running_loop().create_future()
        second_waiter = asyncio.get_running_loop().create_future()
        connection._cancel_waiters.update(  # pylint: disable=protected-access
            {"r_1": first_waiter, "r_2": second_waiter}
        )

        await connection._handle_response_timeout(  # pylint: disable=protected-access
            ResponseTimeoutEvent(stage="first_output", item_ids=("in_1", "in_2"))
        )

        assert first_waiter.done()
        assert second_waiter.done()
        assert isinstance(first_waiter.exception(), VoiceBridgeConnectionClosedError)
        assert isinstance(second_waiter.exception(), VoiceBridgeConnectionClosedError)
        assert not connection._cancel_waiters  # pylint: disable=protected-access

    asyncio.run(scenario())


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


def test_timeout_processed_while_delta_write_blocked_does_not_block_pump() -> None:
    """Barrier race: a stalled ``response.output_text.delta`` write must not block
    the sole receive pump.

    Output writes are performed off the per-response state lock, so the pump can
    run ``_handle_response_timeout`` to completion — marking the response terminal
    and setting the cancellation token — while the delta write is suspended on
    outbound backpressure. The in-flight delta still drains to the wire (the turn
    coordinator, not the pump, awaits it) before the customer task is cancelled.

    At baseline (write held across the state lock) ``_mark_terminal`` would block on
    that lock until the write drained, so ``mark_terminal_done`` would not fire while
    the write is stalled and this assertion would fail.
    """
    app = _app()
    write_blocked = threading.Event()
    release_write = threading.Event()
    mark_terminal_done = threading.Event()
    original_send_text = WebSocket.send_text
    original_mark_terminal = VoiceResponse._mark_terminal

    async def blocking_send_text(self: WebSocket, data: str) -> None:
        if '"delta":"second"' in data and not release_write.is_set():
            write_blocked.set()
            await asyncio.to_thread(release_write.wait)
        await original_send_text(self, data)

    async def mark_terminal(self: VoiceResponse) -> None:
        await original_mark_terminal(self)
        mark_terminal_done.set()

    @app.on_user_message
    async def on_message(_session, event: UserMessageEvent, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.send_text_delta("first")
            await response.send_text_delta("second")
        else:
            await response.send_text("next")

    with mock.patch.object(WebSocket, "send_text", blocking_send_text), mock.patch.object(
        VoiceResponse, "_mark_terminal", mark_terminal
    ):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            created = websocket.receive_json()
            assert created["type"] == "response.created"
            assert websocket.receive_json()["type"] == "response.output_text.delta"
            # The second delta write is now suspended mid-flight.
            assert write_blocked.wait(2.0)
            websocket.send_json(
                {
                    "type": "response.timeout",
                    "id": "m_delta_race_timeout",
                    "ts": _TS,
                    "response_id": created["response_id"],
                    "stage": "max_duration",
                }
            )
            # The pump finishes terminal processing while the write is still stalled.
            assert mark_terminal_done.wait(2.0)
            assert not release_write.is_set()
            # Release: the in-flight delta still reaches the wire, then the turn is
            # cancelled and the connection stays healthy for the next turn.
            release_write.set()
            assert websocket.receive_json()["type"] == "response.output_text.delta"
            websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
            assert websocket.receive_json()["type"] == "response.created"
            assert websocket.receive_json()["type"] == "response.output_text.done"
            assert websocket.receive_json()["type"] == "response.done"


def test_barge_in_while_delta_write_blocked_does_not_block_pump() -> None:
    """Barrier race: barge_in must be processed by the receive pump while an
    in-flight write is stalled.

    Barge_in fires ``_active_release``, which routes through the same coordinator
    branch that drains the in-flight write before cancelling the customer task.
    Because writes happen off the per-response state lock, ``_mark_terminal`` (and
    the cancellation token) run to completion while the write is suspended, and the
    in-flight delta still drains to the wire. At baseline ``mark_terminal_done``
    would not fire until the write drained.
    """
    app = _app()
    write_blocked = threading.Event()
    release_write = threading.Event()
    mark_terminal_done = threading.Event()
    barge_notified = threading.Event()
    original_send_text = WebSocket.send_text
    original_mark_terminal = VoiceResponse._mark_terminal

    async def blocking_send_text(self: WebSocket, data: str) -> None:
        if '"delta":"second"' in data and not release_write.is_set():
            write_blocked.set()
            await asyncio.to_thread(release_write.wait)
        await original_send_text(self, data)

    async def mark_terminal(self: VoiceResponse) -> None:
        await original_mark_terminal(self)
        mark_terminal_done.set()

    @app.on_user_message
    async def on_message(_session, event: UserMessageEvent, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.send_text_delta("first")
            await response.send_text_delta("second")
        else:
            await response.send_text("next")

    @app.on_barge_in
    async def on_barge(_session, _event) -> None:
        barge_notified.set()

    with mock.patch.object(WebSocket, "send_text", blocking_send_text), mock.patch.object(
        VoiceResponse, "_mark_terminal", mark_terminal
    ):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            created = websocket.receive_json()
            assert created["type"] == "response.created"
            delta = websocket.receive_json()
            assert delta["type"] == "response.output_text.delta"
            # The second delta write is now suspended mid-flight.
            assert write_blocked.wait(2.0)
            websocket.send_json(
                {
                    "type": "barge_in",
                    "id": "m_barge_race",
                    "ts": _TS,
                    "response_id": created["response_id"],
                    "item_id": delta["item_id"],
                    "heard_text": "stop",
                }
            )
            # The pump finishes terminal processing while the write is still stalled.
            assert mark_terminal_done.wait(2.0)
            assert not release_write.is_set()
            # Release: the in-flight delta still reaches the wire, barge_in is
            # dispatched, and the connection stays healthy for the next turn.
            release_write.set()
            assert websocket.receive_json()["type"] == "response.output_text.delta"
            assert barge_notified.wait(2.0)
            websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
            assert websocket.receive_json()["type"] == "response.created"
            assert websocket.receive_json()["type"] == "response.output_text.done"
            assert websocket.receive_json()["type"] == "response.done"


def test_duplicate_frame_with_long_id_is_bounded_and_deduplicated() -> None:
    """The dedupe cache keys on a fixed-size digest of the (untrusted, unbounded)
    message id, so a long id cannot pin unbounded memory. Dedupe semantics are
    unchanged: an exact duplicate is ignored, and reusing an id with different
    content is a protocol violation.
    """
    app = _app()
    handled: list[str] = []

    @app.on_user_message
    async def on_message(_session, event: UserMessageEvent, response: VoiceResponse) -> None:
        handled.append(event.item_id)
        await response.send_text("ok")

    long_id = "m_" + "x" * 200_000
    duplicate = _user_message(message_id=long_id)
    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(duplicate)
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"
        # Exact duplicate (same id + content) is silently ignored.
        websocket.send_json(duplicate)
        # Same id, different content is rejected as a protocol violation.
        websocket.send_json(_user_message(message_id=long_id, text="different"))
        with pytest.raises(WebSocketDisconnect) as exc:
            websocket.receive_json()
        assert exc.value.code == 1008
    assert handled == ["in_1"]


def test_response_exceeding_cumulative_byte_budget_is_rejected() -> None:
    """A response is capped by a cumulative encoded-text budget across all items,
    not just per item, so one active response cannot accumulate unbounded text.
    """
    app = _app()
    errors: list[str] = []

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.send_text_delta("12345")  # 5 bytes, within budget
        try:
            await response.send_text_delta("6789")  # 5 + 4 > 8, over budget
        except ValueError as exc:
            errors.append(str(exc))
            raise

    with mock.patch.object(voice_runtime, "_MAX_RESPONSE_BYTES", 8):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            assert websocket.receive_json()["type"] == "response.created"
            assert websocket.receive_json()["type"] == "response.output_text.delta"
            assert websocket.receive_json()["type"] == "error"
    assert errors and "cumulative" in errors[0]


def test_full_text_item_exceeding_per_item_budget_is_rejected() -> None:
    """A non-streamed ``send_text`` item is bounded by the same per-item encoded
    size cap as the streaming delta path, not only by the transport frame limit.
    """
    app = _app()
    errors: list[str] = []

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        try:
            await response.send_text("123456")  # 6 bytes, over the patched 4-byte cap
        except ValueError as exc:
            errors.append(str(exc))
            raise

    with mock.patch.object(voice_runtime, "_MAX_OUTPUT_ITEM_BYTES", 4):
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(_user_message())
            # send_text is rejected before opening; the failed callback then opens
            # the response and emits the response-scoped error.
            assert websocket.receive_json()["type"] == "response.created"
            assert websocket.receive_json()["type"] == "error"
    assert errors and "maximum encoded text size" in errors[0]


def test_completed_response_output_buffers_are_released() -> None:
    """A response retained for late reconciliation keeps its item identity but
    frees the accumulated text buffers, so cached responses stay lightweight.
    """
    app = _app()
    captured: list[VoiceResponse] = []

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        captured.append(response)
        await response.send_text_delta("hello")
        await response.send_text_done()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.delta"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"

    response = captured[0]
    deadline = time.time() + 2.0
    while any(item._chunks for item in response._items) and time.time() < deadline:  # pylint: disable=protected-access
        time.sleep(0.02)
    # Item identity is retained for reconciliation, but the text buffers are freed.
    assert response._items  # pylint: disable=protected-access
    assert all(not item._chunks for item in response._items)  # pylint: disable=protected-access


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


def test_cancel_send_failure_restores_local_writability() -> None:
    async def scenario() -> None:
        class Sender:
            ending = False

            async def begin_cancel(self, _response_id, _reason):
                raise RuntimeError("failed before wire attempt")

        response = VoiceResponse._create(  # pylint: disable=protected-access
            Sender(),
            response_id="r_1",
            in_reply_to=("in_1",),
            wire_opened=True,
        )

        with pytest.raises(RuntimeError, match="before wire attempt"):
            await response.cancel()

        assert not response.is_cancel_pending

    asyncio.run(scenario())


def test_cancelled_ambiguous_proactive_send_terminates_connection() -> None:
    async def scenario() -> None:
        committed = asyncio.Event()

        class BlockingWebSocket:
            async def send_text(self, data: str) -> None:
                if json.loads(data)["type"] == "response.created":
                    committed.set()
                    await asyncio.Event().wait()

        connection = _connection(BlockingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        admission = asyncio.create_task(  # pylint: disable=protected-access
            connection.start_proactive_response(admission_timeout_ms=1000, supersede_key=None)
        )
        await committed.wait()
        admission.cancel()

        with pytest.raises(asyncio.CancelledError):
            await admission

        assert connection.ending
        assert len(connection._pending_proactive) == 1  # pylint: disable=protected-access
        _, future = next(iter(connection._pending_proactive.values()))  # pylint: disable=protected-access
        assert future.cancelled()
        connection._fail_helper_waiters("closed")  # pylint: disable=protected-access

    asyncio.run(scenario())


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


def test_turn_started_while_proactive_active_closes_1008() -> None:
    app = _app()
    colliding_callback_called = threading.Event()

    @app.on_user_message
    async def on_message(session: VoiceSession, event, response: VoiceResponse) -> None:
        if event.item_id != "in_1":
            # A colliding turn must be rejected before its callback runs; if the
            # guard regressed this would emit a second concurrent response.
            colliding_callback_called.set()
            await response.send_text("should not run")
            return
        await response.decline()
        proactive = await session.start_proactive_response(supersede_key="job-1")
        await proactive.send_text("Your job completed")
        # Intentionally do not call proactive.done(): keep it active after this
        # callback returns so the next turn collides with the live proactive
        # response and exercises the single-active-response guard.

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.none"
        proactive_created = websocket.receive_json()
        assert proactive_created["type"] == "response.created"
        websocket.send_json(
            {
                "type": "response.accepted",
                "id": "m_accepted",
                "ts": _TS,
                "response_id": proactive_created["response_id"],
            }
        )
        assert websocket.receive_json()["type"] == "response.output_text.done"

        with pytest.raises(WebSocketDisconnect) as exc_info:
            websocket.send_json(_user_message(message_id="m_user2", item_id="in_2"))
            while True:
                websocket.receive_json()

    assert exc_info.value.code == 1008
    assert not colliding_callback_called.is_set()


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


def test_invalid_history_predecessor_is_rejected_before_callback() -> None:
    app = _app()
    callback_called = threading.Event()

    @app.on_conversation_item_create
    async def on_create(_session, _event) -> None:
        callback_called.set()

    @app.on_user_message
    async def on_message(_session, _event, response: VoiceResponse) -> None:
        await response.decline()

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with TestClient(app).websocket_connect("/invocations_ws") as websocket:
            _activate(websocket)
            websocket.send_json(
                {
                    "type": "conversation.item.create",
                    "id": "m_history",
                    "ts": _TS,
                    "previous_item_id": "anything",
                    "item": {
                        "id": "hi_1",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "order 42"}],
                    },
                }
            )
            websocket.receive_json()

    assert exc_info.value.code == 1008
    assert not callback_called.is_set()


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


def test_terminal_tombstone_suppresses_auto_done_race() -> None:
    async def scenario() -> None:
        connection = _connection(None)
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_1",
            in_reply_to=("in_1",),
            wire_opened=True,
        )
        item = voice_runtime.VoiceTextItem._create(response, "it_1")  # pylint: disable=protected-access
        item._started = True  # pylint: disable=protected-access
        item._done = True  # pylint: disable=protected-access
        response._items.append(item)  # pylint: disable=protected-access
        connection._active_response = response  # pylint: disable=protected-access
        connection._terminal_response_ids.add("r_1")  # pylint: disable=protected-access
        release_task = asyncio.create_task(asyncio.Event().wait())
        try:
            await connection._finalize_turn_response(  # pylint: disable=protected-access
                response,
                release_task,
                failed=False,
            )
        finally:
            release_task.cancel()
            await asyncio.gather(release_task, return_exceptions=True)

    asyncio.run(scenario())


def test_auto_finalization_that_ignores_cancel_is_bounded(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.01)
        connection = _connection(None)
        release = asyncio.Event()
        release.set()
        release_task = asyncio.create_task(release.wait())
        unblock = asyncio.Event()

        class ResistantResponse:
            response_id = "r_1"
            is_terminal = True

            async def _complete_callback(self) -> None:
                try:
                    await asyncio.Event().wait()
                except asyncio.CancelledError:
                    await unblock.wait()

        await connection._finalize_turn_response(  # type: ignore[arg-type]  # pylint: disable=protected-access
            ResistantResponse(),
            release_task,
            failed=False,
        )

        assert connection.ending
        assert connection._resource_limit_reached.done()  # pylint: disable=protected-access
        finalizers = [
            task
            for task in voice_host._GLOBAL_CUSTOMER_TASKS  # pylint: disable=protected-access
            if task.get_name() == "voice_response_callback_finalize"
        ]
        assert len(finalizers) == 1
        unblock.set()
        await asyncio.gather(*finalizers, return_exceptions=True)

    asyncio.run(scenario())


def test_callback_queue_byte_budget_covers_signal_events(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_CALLBACK_QUEUE_BYTES", 16)
        connection = _connection(None)
        work = voice_host._CallbackWork(  # pylint: disable=protected-access
            kind="handoff.failed",
            event=HandoffFailedEvent(
                item_id="in_recovery",
                target="billing",
                code="target_unavailable",
                message="x" * 32,
            ),
            callback=None,
        )

        with pytest.raises(voice_host.VoiceBridgeProtocolError, match="byte limit"):
            connection._put_work(work)  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_shutdown_releases_queued_callback_payloads() -> None:
    async def scenario() -> None:
        connection = _connection(None)
        work = voice_host._CallbackWork(  # pylint: disable=protected-access
            kind="handoff.failed",
            event=HandoffFailedEvent(
                item_id="in_recovery",
                target="billing",
                code="target_unavailable",
                message="x" * 1024,
            ),
            callback=None,
        )
        connection._put_work(work)  # pylint: disable=protected-access
        assert connection._callback_queue_bytes > 0  # pylint: disable=protected-access

        await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

        assert connection._callback_queue.empty()  # pylint: disable=protected-access
        assert connection._callback_queue_bytes == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_global_customer_task_admission_failure_cleans_activation_receive(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASKS", 0)

        class BlockingWebSocket:
            async def receive(self) -> dict:
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

        connection = _connection(BlockingWebSocket())
        with pytest.raises(RuntimeError, match="global customer task limit"):
            await connection._run_session_start_callback(None, None)  # type: ignore[arg-type]  # pylint: disable=protected-access

        assert not any(task.get_name() == "voice_activation_receive" for task in asyncio.all_tasks())

    asyncio.run(scenario())


def test_global_customer_task_limit_is_shared_across_connections(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASKS", 1)
        first_connection = _connection(None)
        second_connection = _connection(None)
        first_task = first_connection._create_customer_task(  # pylint: disable=protected-access
            asyncio.Event().wait(),
            name="first_connection_customer",
        )

        with pytest.raises(RuntimeError, match="global customer task limit"):
            second_connection._create_customer_task(  # pylint: disable=protected-access
                asyncio.Event().wait(),
                name="second_connection_customer",
            )

        assert second_connection.ending
        first_task.cancel()
        await asyncio.gather(first_task, return_exceptions=True)

    asyncio.run(scenario())


def test_eager_customer_task_completion_releases_global_slot(monkeypatch) -> None:
    eager_task_factory = getattr(asyncio, "eager_task_factory", None)
    if eager_task_factory is None:
        pytest.skip("asyncio.eager_task_factory requires Python 3.12+")

    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASKS", 1)
        loop = asyncio.get_running_loop()
        original_factory = loop.get_task_factory()
        loop.set_task_factory(eager_task_factory)
        connection = _connection(None)

        async def complete_immediately() -> None:
            return None

        try:
            first = connection._create_customer_task(  # pylint: disable=protected-access
                complete_immediately(),
                name="first_eager_customer",
            )
            second = connection._create_customer_task(  # pylint: disable=protected-access
                complete_immediately(),
                name="second_eager_customer",
            )
            assert first.done()
            assert second.done()
            assert not connection.ending
        finally:
            loop.set_task_factory(original_factory)

    asyncio.run(scenario())


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


def test_session_end_runs_despite_a_blocked_prior_callback(monkeypatch) -> None:
    """session.end teardown runs on its own dedicated path, not behind ordinary
    callback work. A signal callback that blocks the worker must not prevent
    ``on_session_end`` from firing (previously it was queued behind such work and
    was dropped when the worker was cancelled at shutdown).
    """
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.05)
    app = _app()
    dtmf_started = threading.Event()
    session_ended = threading.Event()

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_dtmf_key
    async def on_dtmf(_session, _event) -> None:
        dtmf_started.set()
        await asyncio.Event().wait()  # blocks the sole callback worker

    @app.on_session_end
    async def on_session_end(_session, event) -> None:
        assert event.reason == "caller_hangup"
        session_ended.set()

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json({"type": "dtmf", "id": "m_dtmf", "ts": _TS, "digits": "1"})
        assert dtmf_started.wait(1.0)  # worker is now blocked in the dtmf callback
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_session_end",
                "ts": _TS,
                "reason": "caller_hangup",
            }
        )
        # Dedicated path: on_session_end fires even though the worker is stuck.
        assert session_ended.wait(2.0)


def test_cancellation_resistant_task_is_tracked_until_done(monkeypatch) -> None:
    """A callback that swallows CancelledError keeps running past the cleanup
    deadline; the underlying task must stay tracked (not dropped) so it is never
    left running untracked.
    """
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.05)
    app = _app()
    started = threading.Event()
    cancelled = threading.Event()
    captured: dict = {}

    original = voice_host._VoiceConnection._schedule_customer_cleanup

    def capture(self, task):
        captured["conn"] = self
        captured["task"] = task
        return original(self, task)

    monkeypatch.setattr(voice_host._VoiceConnection, "_schedule_customer_cleanup", capture)

    @app.on_user_message
    async def on_message(_session, _event, response) -> None:
        await response.decline()

    @app.on_dtmf_key
    async def on_dtmf(_session, _event) -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            await asyncio.Event().wait()  # resistant: keep running after cancellation

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json({"type": "dtmf", "id": "m_dtmf", "ts": _TS, "digits": "1"})
        assert started.wait(1.0)
        websocket.send_json(
            {
                "type": "session.end",
                "id": "m_session_end",
                "ts": _TS,
                "reason": "caller_hangup",
            }
        )
        assert cancelled.wait(1.0)
        # Assert while the connection is still live: the resistant underlying task
        # is retained in the tracking set (not dropped with its cleanup wrapper).
        conn = captured["conn"]
        task = captured["task"]
        assert task in conn._resistant_tasks  # pylint: disable=protected-access
        assert not task.done()


def test_resistant_task_limit_closes_without_additional_work(monkeypatch) -> None:
    """Reaching the cancellation-resistant task cap must wake connection
    supervision and close immediately, without relying on another callback work
    item to make the worker notice the limit.
    """
    monkeypatch.setattr(voice_host, "_MAX_RESISTANT_TASKS", 1)
    monkeypatch.setattr(voice_host, "_CLEANUP_TIMEOUT_SECONDS", 0.02)
    app = _app()
    cancelled = threading.Event()
    closed = threading.Event()
    close_codes: list[int] = []

    original_close = voice_host._VoiceConnection._close

    async def capture_close(self, *, code, reason):
        close_codes.append(code)
        closed.set()
        await original_close(self, code=code, reason=reason)

    monkeypatch.setattr(voice_host._VoiceConnection, "_close", capture_close)

    @app.on_user_message
    async def on_message(_session, _event: UserMessageEvent, response: VoiceResponse) -> None:
        await response.send_text_delta("hi")
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            await asyncio.Event().wait()  # resistant: swallow cancellation

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
                "heard_text": "hi",
            }
        )
        assert cancelled.wait(timeout=2.0)
        # No second frame or callback work is sent. The one-shot resource-limit
        # signal itself must interrupt the pending receive and close the socket.
        assert closed.wait(timeout=1.0)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            websocket.receive_json()

    assert exc_info.value.code == 1011
    assert close_codes == [1011]


def test_no_second_terminal_when_callback_returns_with_cancel_pending() -> None:
    """If a callback starts a self-cancel, its await is cancelled (e.g. the callback
    times out waiting for arbitration) and the callback then returns, auto-completion
    must not emit a second terminal (response.done / SDK error) while response.cancel
    is still being arbitrated by the bridge.
    """
    app = _app()

    @app.on_user_message
    async def on_message(_session, event: UserMessageEvent, response: VoiceResponse) -> None:
        if event.item_id == "in_1":
            await response.send_text_delta("hi")
            try:
                # The bridge never resolves the cancellation here, so the customer's
                # bounded wait is cancelled while _cancel_pending stays set.
                await asyncio.wait_for(response.cancel(), timeout=0.05)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
        else:
            await response.send_text("second")

    with TestClient(app).websocket_connect("/invocations_ws") as websocket:
        _activate(websocket)
        websocket.send_json(_user_message())
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.delta"
        assert websocket.receive_json()["type"] == "response.cancel"
        # No response.done / error must follow for the first response. The second
        # turn proves the connection is healthy and that the next frame is its own
        # response.created, not a stray terminal for the cancel-pending response.
        websocket.send_json(_user_message(message_id="m_user_2", item_id="in_2"))
        assert websocket.receive_json()["type"] == "response.created"
        assert websocket.receive_json()["type"] == "response.output_text.done"
        assert websocket.receive_json()["type"] == "response.done"


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
