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

    async def send_text(self, frame: str) -> None:
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
