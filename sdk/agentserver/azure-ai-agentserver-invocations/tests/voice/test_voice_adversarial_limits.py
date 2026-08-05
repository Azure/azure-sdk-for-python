# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Adversarial race and aggregate resource-limit tests for the voice host."""

import asyncio
import threading
from unittest import mock

import pytest

from azure.ai.agentserver.invocations.voice import (
    HandoffFailedEvent,
    InputTextPart,
    ResponseTimeoutEvent,
    UserMessageEvent,
    VoiceBridgeProtocolError,
    VoiceResponse,
)
from azure.ai.agentserver.invocations.voice import _host as voice_host
from azure.ai.agentserver.invocations.voice import _runtime as voice_runtime


def _connection(websocket=None):
    return voice_host._VoiceConnection(  # pylint: disable=protected-access
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


class _Sender:
    ending = False

    def __init__(self) -> None:
        self.messages: list[tuple[str, dict]] = []

    async def send(self, message_type: str, **fields) -> None:
        self.messages.append((message_type, fields))


def test_barge_in_releases_active_turn_while_self_cancel_is_pending() -> None:
    async def scenario() -> None:
        connection = _connection()
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_cancel_pending",
            in_reply_to=("in_1",),
            wire_opened=True,
        )
        response._cancel_pending = True  # pylint: disable=protected-access
        release = asyncio.Event()
        connection._active_response = response  # pylint: disable=protected-access
        connection._active_release = release  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access

        await connection._handle_playback_terminal(  # pylint: disable=protected-access
            {
                "response_id": response.response_id,
                "heard_text": "stop",
            },
            kind="barge_in",
        )

        assert response.is_terminal
        assert release.is_set()

    asyncio.run(scenario())


def test_timeout_before_proactive_acceptance_is_protocol_error() -> None:
    async def scenario() -> None:
        connection = _connection()
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_pending_proactive",
            in_reply_to=None,
            wire_opened=True,
            accepted=False,
        )
        future = asyncio.get_running_loop().create_future()
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
        connection._pending_proactive[response.response_id] = (  # pylint: disable=protected-access
            response,
            future,
        )

        with pytest.raises(VoiceBridgeProtocolError) as exc_info:
            await connection._handle_response_timeout(  # pylint: disable=protected-access
                ResponseTimeoutEvent(stage="first_output", response_id=response.response_id)
            )

        assert exc_info.value.close_code == 1008
        assert not future.done()
        future.cancel()

    asyncio.run(scenario())


def test_retained_byte_estimate_counts_many_small_content_objects() -> None:
    event = UserMessageEvent(
        item_id="in_many_parts",
        content=tuple(InputTextPart(text="x") for _ in range(1024)),
    )

    retained = voice_host._estimate_retained_bytes(event)  # pylint: disable=protected-access
    encoded = voice_host._estimate_event_bytes(event)  # pylint: disable=protected-access

    assert retained > encoded * 4


def test_global_callback_queue_byte_limit_is_shared_across_connections(monkeypatch) -> None:
    async def scenario() -> None:
        first_connection = _connection()
        second_connection = _connection()
        first_work = voice_host._CallbackWork(  # pylint: disable=protected-access
            kind="handoff.failed",
            event=HandoffFailedEvent(
                item_id="in_first",
                target="billing",
                code="target_unavailable",
                message="x" * 400,
            ),
            callback=None,
        )
        second_work = voice_host._CallbackWork(  # pylint: disable=protected-access
            kind="handoff.failed",
            event=HandoffFailedEvent(
                item_id="in_second",
                target="billing",
                code="target_unavailable",
                message="y" * 400,
            ),
            callback=None,
        )
        first_size = voice_host._estimate_retained_bytes(first_work)  # pylint: disable=protected-access
        second_size = voice_host._estimate_retained_bytes(second_work)  # pylint: disable=protected-access
        monkeypatch.setattr(
            voice_host,
            "_MAX_GLOBAL_CALLBACK_QUEUE_BYTES",
            first_size + second_size - 1,
        )

        assert voice_host._GLOBAL_CALLBACK_QUEUE_BYTES == 0  # pylint: disable=protected-access
        first_connection._put_work(first_work)  # pylint: disable=protected-access
        try:
            with pytest.raises(RuntimeError, match="global callback queue byte limit"):
                second_connection._put_work(second_work)  # pylint: disable=protected-access
        finally:
            first_connection._discard_callback_queue()  # pylint: disable=protected-access

        assert voice_host._GLOBAL_CALLBACK_QUEUE_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_global_customer_task_byte_limit_is_shared_across_connections(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 10)
        first_connection = _connection()
        second_connection = _connection()
        first_task = first_connection._create_customer_task(  # pylint: disable=protected-access
            asyncio.Event().wait(),
            name="first_connection_customer",
            retained_bytes=6,
        )

        with pytest.raises(RuntimeError, match="global customer task byte limit"):
            second_connection._create_customer_task(  # pylint: disable=protected-access
                asyncio.Event().wait(),
                name="second_connection_customer",
                retained_bytes=5,
            )

        first_task.cancel()
        await asyncio.gather(first_task, return_exceptions=True)
        await asyncio.sleep(0)
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_global_customer_task_bytes_are_shared_across_event_loops(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 10)
    reserved = threading.Event()
    release = threading.Event()
    thread_errors: list[BaseException] = []

    async def first_loop() -> None:
        connection = _connection()
        customer_task = connection._create_customer_task(  # pylint: disable=protected-access
            asyncio.Event().wait(),
            name="cross_loop_customer",
            retained_bytes=6,
        )
        reserved.set()
        await asyncio.to_thread(release.wait)
        customer_task.cancel()
        await asyncio.gather(customer_task, return_exceptions=True)

    def run_first_loop() -> None:
        try:
            asyncio.run(first_loop())
        except BaseException as exc:  # pylint: disable=broad-exception-caught
            thread_errors.append(exc)

    worker = threading.Thread(target=run_first_loop)
    worker.start()
    try:
        assert reserved.wait(timeout=2.0)

        async def second_loop() -> None:
            connection = _connection()
            with pytest.raises(RuntimeError, match="global customer task byte limit"):
                connection._create_customer_task(  # pylint: disable=protected-access
                    asyncio.Event().wait(),
                    name="second_loop_customer",
                    retained_bytes=5,
                )

        asyncio.run(second_loop())
    finally:
        release.set()
        worker.join(timeout=2.0)

    assert not worker.is_alive()
    assert not thread_errors
    assert voice_host._GLOBAL_CUSTOMER_TASK_RESERVATIONS == 0  # pylint: disable=protected-access
    assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access


def test_eager_customer_task_completion_releases_global_bytes(monkeypatch) -> None:
    eager_task_factory = getattr(asyncio, "eager_task_factory", None)
    if eager_task_factory is None:
        pytest.skip("asyncio.eager_task_factory requires Python 3.12+")

    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 1)
        loop = asyncio.get_running_loop()
        original_factory = loop.get_task_factory()
        loop.set_task_factory(eager_task_factory)
        connection = _connection()

        async def complete_immediately() -> None:
            return None

        try:
            first = connection._create_customer_task(  # pylint: disable=protected-access
                complete_immediately(),
                name="first_eager_customer_bytes",
                retained_bytes=1,
            )
            second = connection._create_customer_task(  # pylint: disable=protected-access
                complete_immediately(),
                name="second_eager_customer_bytes",
                retained_bytes=1,
            )
            assert first.done()
            assert second.done()
            assert voice_host._GLOBAL_CUSTOMER_TASK_RESERVATIONS == 0  # pylint: disable=protected-access
            assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access
        finally:
            loop.set_task_factory(original_factory)

    asyncio.run(scenario())


def test_response_cumulative_chunk_limit_spans_all_items() -> None:
    async def scenario() -> None:
        sender = _Sender()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            sender,  # type: ignore[arg-type]
            in_reply_to=("in_1",),
            wire_opened=True,
        )

        first = response.new_text_item()
        await first.send_text_delta("a")
        await first.send_text_done()
        second = response.new_text_item()
        await second.send_text_delta("b")
        with pytest.raises(ValueError, match="cumulative text chunk count"):
            await second.send_text_delta("c")

        assert [message_type for message_type, _ in sender.messages] == [
            "response.output_text.delta",
            "response.output_text.done",
            "response.output_text.delta",
        ]

    with mock.patch.object(voice_runtime, "_MAX_RESPONSE_CHUNKS", 2):
        asyncio.run(scenario())


def test_empty_output_fragments_do_not_bypass_response_budgets() -> None:
    async def scenario() -> None:
        sender = _Sender()
        response = VoiceResponse._create(  # pylint: disable=protected-access
            sender,  # type: ignore[arg-type]
            in_reply_to=("in_1",),
            wire_opened=True,
        )

        with pytest.raises(ValueError, match="text must be non-empty"):
            await response.send_text("")
        with pytest.raises(ValueError, match="delta must be non-empty"):
            await response.send_text_delta("")
        await response.send_text("ok")

        assert len(sender.messages) == 1
        assert sender.messages[0][0] == "response.output_text.done"
        assert sender.messages[0][1]["text"] == "ok"

    asyncio.run(scenario())
