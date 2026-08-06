# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Deterministic tests for outbound prepare/commit/transport phases."""

import asyncio
import json

import pytest

from azure.ai.agentserver.invocations.voice import VoiceBridgeConnectionClosedError, VoiceResponse
from azure.ai.agentserver.invocations.voice import _host as voice_host


class _RecordingWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.frames: list[str] = []

    async def send_text(self, frame: str) -> None:
        self.frames.append(frame)
        self.sent.append(json.loads(frame))

    async def close(self, **_fields) -> None:
        return None


def _connection(websocket) -> voice_host._VoiceConnection:  # pylint: disable=protected-access
    connection = voice_host._VoiceConnection(  # pylint: disable=protected-access
        websocket=websocket,
        on_session_start=None,
        on_user_message=None,
        on_user_no_input=None,
        on_user_speech_started=None,
        on_dtmf_key=None,
        on_dtmf_collected=None,
        on_dtmf_collection_rejected=None,
        on_dtmf_collection_cancelled=None,
        on_handoff_failed=None,
        on_conversation_item_create=None,
        on_conversation_item_delete=None,
        on_barge_in=None,
        on_response_timeout=None,
        on_session_end=None,
    )
    connection._ready = True  # pylint: disable=protected-access
    return connection


def _active_response(connection: voice_host._VoiceConnection) -> VoiceResponse:  # pylint: disable=protected-access
    response = VoiceResponse._create(  # pylint: disable=protected-access
        connection,
        response_id="r_test",
        in_reply_to=("in_test",),
    )
    connection._active_response = response  # pylint: disable=protected-access
    connection._pending_turns["in_test"] = response  # pylint: disable=protected-access
    connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
    return response


def test_local_terminal_frame_rejection_does_not_commit_session_state() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)

        with pytest.raises(ValueError, match="maximum encoded size"):
            await connection.end_call("x" * (1024 * 1024), "drain")

        assert not connection.ending
        assert not connection._terminal_response_ids  # pylint: disable=protected-access

        await connection.end_call("normal", "drain")
        assert [message["type"] for message in websocket.sent] == ["end_call"]

    asyncio.run(scenario())


def test_local_decline_frame_rejection_keeps_prefix_retryable() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        response = _active_response(connection)

        with pytest.raises(ValueError, match="maximum encoded size"):
            await response.decline(reason="x" * (1024 * 1024))

        assert tuple(connection._pending_turns) == ("in_test",)  # pylint: disable=protected-access
        assert not connection._resolved_input_prefixes  # pylint: disable=protected-access
        assert not connection._terminal_response_ids  # pylint: disable=protected-access

        await response.decline(reason="normal")
        assert [message["type"] for message in websocket.sent] == ["response.none"]

    asyncio.run(scenario())


def test_cancellation_after_open_commit_fails_connection_closed() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        response = _active_response(connection)
        await connection._send_lock.acquire()  # pylint: disable=protected-access
        send_task = asyncio.create_task(response.send_text("hello"))
        try:
            while connection._pending_turns:  # pylint: disable=protected-access
                await asyncio.sleep(0)
            assert ("in_test",) in connection._resolved_input_prefixes  # pylint: disable=protected-access

            send_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await send_task

            assert connection.ending
            assert connection._resource_limit_reached.done()  # pylint: disable=protected-access
        finally:
            connection._send_lock.release()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_cancellation_after_terminal_claim_fails_connection_closed() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        response = _active_response(connection)
        response._wire_opened = True  # pylint: disable=protected-access
        await response.send_text("hello")
        await connection._send_lock.acquire()  # pylint: disable=protected-access
        done_task = asyncio.create_task(response.done())
        try:
            while not response.is_terminal:
                await asyncio.sleep(0)

            done_task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await done_task

            assert connection.ending
            assert connection._resource_limit_reached.done()  # pylint: disable=protected-access
        finally:
            connection._send_lock.release()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_handoff_preflight_failure_keeps_response_retryable() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        response = _active_response(connection)

        with pytest.raises(ValueError, match="maximum encoded size"):
            await response.handoff(target="x" * (1024 * 1024 + 1))

        assert not response.is_terminal
        assert not response.is_wire_opened
        assert not response.cancellation.is_cancelled
        assert tuple(connection._pending_turns) == ("in_test",)  # pylint: disable=protected-access
        assert not connection._terminal_response_ids  # pylint: disable=protected-access
        assert not websocket.sent

        await response.send_text("recovered")
        await response.done()
        assert [message["type"] for message in websocket.sent] == [
            "response.created",
            "response.output_text.done",
            "response.done",
        ]

    asyncio.run(scenario())


def test_handoff_frame_is_fully_prepared_before_terminal_claim() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        response = _active_response(connection)
        terminal_states_during_prepare: list[bool] = []
        prepared_frames: list[str] = []
        original_prepare = connection.prepare_frame

        def recording_prepare(message_type: str, **fields):
            terminal_states_during_prepare.append(response.is_terminal)
            prepared = original_prepare(message_type, **fields)
            prepared_frames.append(prepared.frame)
            return prepared

        connection.prepare_frame = recording_prepare  # type: ignore[method-assign]
        await response.handoff(target="billing", message="Please hold")

        assert terminal_states_during_prepare == [False]
        assert response.is_terminal
        assert websocket.frames[-1] == prepared_frames[0]

    asyncio.run(scenario())


@pytest.mark.parametrize("terminal_kind", ["fail", "done", "auto_done", "callback_error"])
def test_every_terminal_frame_is_prepared_before_local_claim(terminal_kind: str) -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        response = _active_response(connection)
        response._wire_opened = True  # pylint: disable=protected-access
        if terminal_kind in ("done", "auto_done"):
            await response.send_text("hello")

        terminal_states_during_prepare: list[bool] = []
        original_prepare = connection.prepare_frame

        def recording_prepare(message_type: str, **fields):
            terminal_states_during_prepare.append(response.is_terminal)
            return original_prepare(message_type, **fields)

        connection.prepare_frame = recording_prepare  # type: ignore[method-assign]
        if terminal_kind == "fail":
            await response.fail(code="agent_error", message="failed")
        elif terminal_kind == "done":
            await response.done()
        elif terminal_kind == "auto_done":
            await response._complete_callback()  # pylint: disable=protected-access
        else:
            await response._fail_callback()  # pylint: disable=protected-access

        assert terminal_states_during_prepare == [False]
        assert response.is_terminal

    asyncio.run(scenario())


def test_cancellation_after_wire_terminal_waits_for_host_bookkeeping() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        response = _active_response(connection)
        response._wire_opened = True  # pylint: disable=protected-access
        await response.send_text("hello")

        bookkeeping_started = asyncio.Event()
        release_bookkeeping = asyncio.Event()
        original_completed = connection.response_completed

        async def blocked_completed(response_id: str, terminal_kind: str = "done") -> None:
            bookkeeping_started.set()
            await release_bookkeeping.wait()
            await original_completed(response_id, terminal_kind)

        connection.response_completed = blocked_completed  # type: ignore[method-assign]
        done_task = asyncio.create_task(response.done())
        await bookkeeping_started.wait()
        assert websocket.sent[-1]["type"] == "response.done"

        done_task.cancel()
        await asyncio.sleep(0)
        assert not done_task.done()
        assert connection._active_response is response  # pylint: disable=protected-access

        release_bookkeeping.set()
        with pytest.raises(asyncio.CancelledError):
            await done_task

        assert connection._active_response is None  # pylint: disable=protected-access
        assert response.response_id in connection._terminal_response_ids  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_host_bookkeeping_failure_takes_precedence_over_caller_cancellation() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        response = _active_response(connection)
        response._wire_opened = True  # pylint: disable=protected-access
        await response.send_text("hello")

        bookkeeping_started = asyncio.Event()
        release_bookkeeping = asyncio.Event()

        async def failing_completed(_response_id: str, _terminal_kind: str = "done") -> None:
            bookkeeping_started.set()
            await release_bookkeeping.wait()
            raise RuntimeError("bookkeeping failed")

        connection.response_completed = failing_completed  # type: ignore[method-assign]
        done_task = asyncio.create_task(response.done())
        await bookkeeping_started.wait()
        done_task.cancel()
        release_bookkeeping.set()

        with pytest.raises(RuntimeError, match="bookkeeping failed"):
            await done_task

    asyncio.run(scenario())


def test_semantic_terminal_revalidation_does_not_fail_connection() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        response = _active_response(connection)
        await connection._send_lock.acquire()  # pylint: disable=protected-access
        send_task = asyncio.create_task(response.send_text("hello"))
        try:
            while connection._pending_turns:  # pylint: disable=protected-access
                await asyncio.sleep(0)
            async with connection._state_lock:  # pylint: disable=protected-access
                connection._terminal_response_ids.add(response.response_id)  # pylint: disable=protected-access
        finally:
            connection._send_lock.release()  # pylint: disable=protected-access

        with pytest.raises(VoiceBridgeConnectionClosedError, match="response is terminal"):
            await send_task

        assert not connection.ending
        assert not connection._resource_limit_reached.done()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_telemetry_failure_does_not_reclassify_successful_wire_send() -> None:
    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)

        def fail_telemetry(_message_type, _fields) -> None:
            raise RuntimeError("telemetry failed")

        connection._record_first_output = fail_telemetry  # type: ignore[method-assign]  # pylint: disable=protected-access
        await connection.send(
            "response.output_text.done",
            response_id="r_test",
            item_id="it_test",
            text="hello",
        )

        assert [message["type"] for message in websocket.sent] == ["response.output_text.done"]
        assert not connection.ending
        assert not connection._resource_limit_reached.done()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_output_item_pre_io_failure_does_not_create_ghost_ownership() -> None:
    """An item becomes playback-visible only after entering transport."""

    async def scenario() -> None:
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        response = _active_response(connection)

        async def lose_before_open() -> None:
            await response._mark_terminal()  # pylint: disable=protected-access
            raise VoiceBridgeConnectionClosedError("lost before response.created")

        response._ensure_open = lose_before_open  # type: ignore[method-assign]  # pylint: disable=protected-access
        with pytest.raises(VoiceBridgeConnectionClosedError, match="lost before response.created"):
            await response.send_text("never sent")

        item_id = response._items[0].item_id  # pylint: disable=protected-access
        assert not websocket.sent
        assert not connection._response_identities.owns_item(  # pylint: disable=protected-access
            response.response_id,
            item_id,
        )

    asyncio.run(scenario())


def test_connection_shutdown_finishes_before_rethrowing_cancellation() -> None:
    """A second cancellation cannot interrupt connection resource release."""

    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
        connection._seen_response_ids.add("r_shutdown")  # pylint: disable=protected-access
        shutdown_started = asyncio.Event()
        release_shutdown = asyncio.Event()
        original_shutdown = connection._shutdown_runtime  # pylint: disable=protected-access

        async def cancel_activation() -> bool:
            raise asyncio.CancelledError()

        async def blocked_shutdown(*, drain_callbacks: bool) -> None:
            shutdown_started.set()
            await release_shutdown.wait()
            await original_shutdown(drain_callbacks=drain_callbacks)

        connection._activate = cancel_activation  # type: ignore[method-assign]  # pylint: disable=protected-access
        connection._shutdown_runtime = blocked_shutdown  # type: ignore[method-assign]  # pylint: disable=protected-access
        run_task = asyncio.create_task(connection.run())
        await shutdown_started.wait()
        run_task.cancel()
        await asyncio.sleep(0)
        assert not run_task.done()

        release_shutdown.set()
        with pytest.raises(asyncio.CancelledError):
            await run_task

        assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access

    asyncio.run(scenario())
