# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Adversarial race and aggregate resource-limit tests for the voice host."""

import asyncio
import gc
import hashlib
import json
import sys
import threading
import weakref
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
        on_handoff_failed=None,
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

    def register_response_item(self, _response_id: str, _item_id: str) -> None:
        return None


class _RecordingWebSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []

    async def send_text(self, frame: str) -> None:
        self.sent.append(json.loads(frame))

    async def close(self, **_fields) -> None:
        return None


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


def test_session_retained_estimate_counts_mapping_proxy_storage_without_sender_graph() -> None:
    event = voice_host.parse_session_start(  # pylint: disable=protected-access
        {
            "protocol_version": "1.0",
            "reconnect": False,
            "response_timeouts": {
                "first_output_ms": 1,
                "idle_ms": 1,
                "max_duration_ms": 1,
            },
            "caller": {"custom_parameters": {f"key_{index}": index for index in range(32)}},
        }
    )
    sender = _Sender()
    session = voice_runtime.VoiceSession._create(sender, event)  # type: ignore[arg-type]  # pylint: disable=protected-access
    before = voice_host._estimate_session_retained_bytes(session, event)  # pylint: disable=protected-access
    sender.unrelated_large_state = ["x" * 1024 for _ in range(100)]

    assert voice_host._estimate_session_retained_bytes(session, event) == before  # pylint: disable=protected-access
    assert before > voice_host._estimate_retained_bytes(event)  # pylint: disable=protected-access
    assert event.caller is not None
    shallow_visible = sys.getsizeof(event.caller) + sum(
        sys.getsizeof(key) + sys.getsizeof(value) for key, value in event.caller.items()
    )
    assert voice_host._estimate_retained_bytes(event.caller) > shallow_visible  # pylint: disable=protected-access


def test_session_retention_budget_is_shared_across_connections(monkeypatch) -> None:
    monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 10)
    first = voice_host._reserve_session_retention(6)  # pylint: disable=protected-access
    assert first is not None
    try:
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 6  # pylint: disable=protected-access
        assert voice_host._reserve_session_retention(5) is None  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 6  # pylint: disable=protected-access
    finally:
        voice_host._release_session_retention(first)  # pylint: disable=protected-access
    assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access


def test_session_retention_outlives_connection_for_resistant_customer_task() -> None:
    async def scenario() -> None:
        connection = _connection()
        lease = voice_host._reserve_session_retention(17)  # pylint: disable=protected-access
        assert lease is not None
        connection._session_retention = lease  # pylint: disable=protected-access
        started = asyncio.Event()
        cancelled = asyncio.Event()
        release = asyncio.Event()

        async def resist_cancellation() -> None:
            started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                await release.wait()

        task = connection._create_customer_task(  # pylint: disable=protected-access
            resist_cancellation(),
            name="session_retention_resistant_customer",
        )
        await started.wait()
        task.cancel()
        await cancelled.wait()
        connection._release_connection_state()  # pylint: disable=protected-access

        assert lease.references == 1
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 17  # pylint: disable=protected-access
        release.set()
        await task
        await asyncio.sleep(0)
        assert lease.released
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access
        assert not voice_host._GLOBAL_SESSION_RETENTION_BY_TASK  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_session_retention_rolls_back_when_customer_task_creation_fails() -> None:
    async def scenario() -> None:
        connection = _connection()
        lease = voice_host._reserve_session_retention(11)  # pylint: disable=protected-access
        assert lease is not None
        connection._session_retention = lease  # pylint: disable=protected-access

        with mock.patch.object(asyncio, "create_task", side_effect=RuntimeError("task creation failed")):
            with pytest.raises(RuntimeError, match="task creation failed"):
                connection._create_customer_task(  # pylint: disable=protected-access
                    asyncio.Event().wait(),
                    name="session_retention_creation_failure",
                )

        assert lease.references == 1
        assert voice_host._GLOBAL_CUSTOMER_TASK_RESERVATIONS == 0  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 11  # pylint: disable=protected-access
        assert not voice_host._GLOBAL_SESSION_RETENTION_BY_TASK  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_eager_session_retention_task_release_is_idempotent() -> None:
    eager_task_factory = getattr(asyncio, "eager_task_factory", None)
    if eager_task_factory is None:
        pytest.skip("asyncio.eager_task_factory requires Python 3.12+")

    async def scenario() -> None:
        connection = _connection()
        lease = voice_host._reserve_session_retention(13)  # pylint: disable=protected-access
        assert lease is not None
        connection._session_retention = lease  # pylint: disable=protected-access
        loop = asyncio.get_running_loop()
        original_factory = loop.get_task_factory()
        loop.set_task_factory(eager_task_factory)

        async def complete_immediately() -> None:
            return None

        try:
            task = connection._create_customer_task(  # pylint: disable=protected-access
                complete_immediately(),
                name="eager_session_retention_customer",
            )
            assert task.done()
            assert lease.references == 1
            assert task not in voice_host._GLOBAL_SESSION_RETENTION_BY_TASK  # pylint: disable=protected-access
            voice_host._release_global_customer_task(task)  # pylint: disable=protected-access
            assert lease.references == 1
        finally:
            loop.set_task_factory(original_factory)
        connection._release_connection_state()  # pylint: disable=protected-access
        assert lease.released
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_session_retention_and_output_share_global_customer_budget(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 5)
        lease = voice_host._reserve_session_retention(3)  # pylint: disable=protected-access
        assert lease is not None
        connection = _connection(_RecordingWebSocket())
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_session_output_budget",
            in_reply_to=None,
            wire_opened=True,
        )
        try:
            with pytest.raises(RuntimeError, match="global customer task byte limit"):
                await response.send_text("123")
        finally:
            voice_host._release_session_retention(lease)  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


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


def test_proactive_acceptance_may_arrive_before_done_sender_resumes() -> None:
    class BlockingDoneWebSocket(_RecordingWebSocket):
        def __init__(self) -> None:
            super().__init__()
            self.done_started = asyncio.Event()
            self.release_done = asyncio.Event()

        async def send_text(self, frame: str) -> None:
            message = json.loads(frame)
            self.sent.append(message)
            if message["type"] == "response.done":
                self.done_started.set()
                await self.release_done.wait()

    async def scenario() -> None:
        websocket = BlockingDoneWebSocket()
        connection = _connection(websocket)
        connection._ready = True  # pylint: disable=protected-access
        previous = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_previous",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = previous  # pylint: disable=protected-access
        connection._seen_response_ids.add(previous.response_id)  # pylint: disable=protected-access
        await previous.send_text("finished")

        admission = asyncio.create_task(
            connection.start_proactive_response(admission_timeout_ms=1000, supersede_key=None)
        )
        while not connection._pending_proactive:  # pylint: disable=protected-access
            await asyncio.sleep(0)
        response_id = next(iter(connection._pending_proactive))  # pylint: disable=protected-access

        done_task = asyncio.create_task(previous.done())
        await websocket.done_started.wait()
        await connection._handle_response_accepted({"response_id": response_id})  # pylint: disable=protected-access
        accepted = await admission
        assert accepted.response_id == response_id

        websocket.release_done.set()
        await done_task
        await accepted.send_text("next")
        await accepted.done()
        assert not connection.ending

    asyncio.run(scenario())


def test_proactive_acceptance_rechecks_active_owner_after_await() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        proactive = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_proactive",
            in_reply_to=None,
            wire_opened=True,
            accepted=False,
        )
        outcome = asyncio.get_running_loop().create_future()
        pending = (proactive, outcome)
        connection._pending_proactive[proactive.response_id] = pending  # pylint: disable=protected-access
        connection._seen_response_ids.add(proactive.response_id)  # pylint: disable=protected-access

        entered = asyncio.Event()
        release = asyncio.Event()
        original_mark_accepted = proactive._mark_accepted  # pylint: disable=protected-access

        async def blocked_mark_accepted() -> None:
            entered.set()
            await release.wait()
            await original_mark_accepted()

        proactive._mark_accepted = blocked_mark_accepted  # type: ignore[method-assign]  # pylint: disable=protected-access
        accepting = asyncio.create_task(
            connection._handle_response_accepted(  # pylint: disable=protected-access
                {"response_id": proactive.response_id}
            )
        )
        await entered.wait()

        turn = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_turn",
            in_reply_to=("in_1",),
        )
        connection._active_response = turn  # pylint: disable=protected-access
        release.set()

        with pytest.raises(VoiceBridgeProtocolError, match="another response is active"):
            await accepting
        assert connection._active_response is turn  # pylint: disable=protected-access
        assert connection._pending_proactive.get(proactive.response_id) is pending  # pylint: disable=protected-access
        outcome.cancel()

    asyncio.run(scenario())


def test_response_output_counts_toward_global_customer_byte_limit(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_GLOBAL_CUSTOMER_TASK_BYTES", 5)
        first_connection = _connection(_RecordingWebSocket())
        second_connection = _connection(_RecordingWebSocket())
        first_connection._ready = True  # pylint: disable=protected-access
        second_connection._ready = True  # pylint: disable=protected-access
        first = VoiceResponse._create(  # pylint: disable=protected-access
            first_connection,
            response_id="r_first",
            in_reply_to=None,
            wire_opened=True,
        )
        second = VoiceResponse._create(  # pylint: disable=protected-access
            second_connection,
            response_id="r_second",
            in_reply_to=None,
            wire_opened=True,
        )

        await first.send_text("123")
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 3  # pylint: disable=protected-access
        with pytest.raises(RuntimeError, match="global customer task byte limit"):
            await second.send_text("456")

        await first._mark_terminal()  # pylint: disable=protected-access
        assert voice_host._GLOBAL_CUSTOMER_TASK_BYTES == 0  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_recent_response_cache_does_not_retain_response_object_graph() -> None:
    async def scenario() -> None:
        connection = _connection(_RecordingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_recent",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
        await response.send_text("hello")
        item_id = response._items[0].item_id  # pylint: disable=protected-access
        await response.done()
        reference = weakref.ref(response)
        del response
        gc.collect()

        recent = connection._recent_responses["r_recent"]  # pylint: disable=protected-access
        assert not hasattr(recent, "item_ids")
        assert connection._response_identities.owns_item("r_recent", item_id)  # pylint: disable=protected-access
        assert all(
            isinstance(value, bytes) and len(value) == hashlib.sha256().digest_size
            for value in connection._response_identities._item_owners  # pylint: disable=protected-access
        )
        assert reference() is None
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_dedupe_budget_fails_closed_without_evicting_history(monkeypatch) -> None:
    class QueueWebSocket(_RecordingWebSocket):
        def __init__(self, messages: list[dict]) -> None:
            super().__init__()
            self.messages = iter(messages)

        async def receive(self) -> dict:
            return next(self.messages)

    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_SEEN_MESSAGES", 2)
        messages = [
            {
                "type": "websocket.receive",
                "text": json.dumps({"type": "future", "id": f"m_{index}", "ts": "2026-08-05T00:00:00Z"}),
            }
            for index in range(3)
        ]
        connection = _connection(QueueWebSocket(messages))
        for _ in range(2):
            assert await connection._receive_payload() is not None  # pylint: disable=protected-access

        with pytest.raises(VoiceBridgeProtocolError, match="dedupe budget exceeded") as exc_info:
            await connection._receive_payload()  # pylint: disable=protected-access

        assert exc_info.value.close_code == 1008
        assert len(connection._seen_messages) == 2  # pylint: disable=protected-access
        first_key = hashlib.sha256(b"m_0").digest()
        assert first_key in connection._seen_messages._values  # pylint: disable=protected-access
        assert connection.ending
        assert connection._resource_limit_reached.done()  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_full_dedupe_ledger_ignores_old_replay_before_failing_new_message(monkeypatch) -> None:
    class QueueWebSocket(_RecordingWebSocket):
        def __init__(self, payloads: list[dict]) -> None:
            super().__init__()
            self.messages = iter({"type": "websocket.receive", "text": json.dumps(payload)} for payload in payloads)

        async def receive(self) -> dict:
            return next(self.messages)

    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_SEEN_MESSAGES", 2)
        replayed = {
            "type": "future.signal",
            "id": "m_replayed",
            "ts": "2026-08-05T00:00:00Z",
        }
        websocket = QueueWebSocket(
            [
                replayed,
                {"type": "future.signal", "id": "m_fill", "ts": "2026-08-05T00:00:00Z"},
                replayed,
                {"type": "future.signal", "id": "m_overflow", "ts": "2026-08-05T00:00:00Z"},
            ]
        )
        connection = _connection(websocket)
        assert await connection._receive_payload() == replayed  # pylint: disable=protected-access
        assert await connection._receive_payload() is not None  # pylint: disable=protected-access

        with pytest.raises(VoiceBridgeProtocolError, match="dedupe budget exceeded"):
            # _receive_payload skips the exact replay and fails on m_overflow;
            # the old message never consumes a second ledger record.
            await connection._receive_payload()  # pylint: disable=protected-access

        assert len(connection._seen_messages) == 2  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_connection_identity_byte_budget_is_unified_and_poisoned(monkeypatch) -> None:
    async def scenario() -> None:
        baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
        monkeypatch.setattr(
            voice_host,
            "_MAX_CONNECTION_IDENTITY_BYTES",
            voice_host._MESSAGE_IDENTITY_BYTES + voice_host._INPUT_IDENTITY_BYTES,  # pylint: disable=protected-access
        )
        connection = _connection()
        connection._seen_messages.add(b"m" * 32, b"p" * 32)  # pylint: disable=protected-access
        connection._seen_input_ids.add("in_1")  # pylint: disable=protected-access
        snapshot = (
            len(connection._seen_messages),  # pylint: disable=protected-access
            len(connection._seen_input_ids),  # pylint: disable=protected-access
            len(connection._seen_response_ids),  # pylint: disable=protected-access
            connection._identity_budget.used_bytes,  # pylint: disable=protected-access
        )

        with pytest.raises(VoiceBridgeProtocolError, match="connection identity byte budget"):
            connection._seen_response_ids.add("r_overflow")  # pylint: disable=protected-access
        with pytest.raises(VoiceBridgeProtocolError, match="connection identity byte budget"):
            connection._seen_messages.add(b"n" * 32, b"q" * 32)  # pylint: disable=protected-access

        assert snapshot == (
            len(connection._seen_messages),  # pylint: disable=protected-access
            len(connection._seen_input_ids),  # pylint: disable=protected-access
            len(connection._seen_response_ids),  # pylint: disable=protected-access
            connection._identity_budget.used_bytes,  # pylint: disable=protected-access
        )
        connection._release_connection_state()  # pylint: disable=protected-access
        assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_long_input_id_uses_fixed_digest_in_pending_and_resolved_state() -> None:
    async def scenario() -> None:
        item_id = f"in_{'x' * (256 * 1024)}"
        connection = _connection(_RecordingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        event = UserMessageEvent(
            item_id=item_id,
            content=(InputTextPart(text="hello"),),
        )

        await connection._enqueue_turn(  # pylint: disable=protected-access
            item_id,
            event,
            None,
            "user.message",
        )

        assert all(isinstance(key, bytes) and len(key) == 32 for key in connection._pending_turns)
        assert all(isinstance(key, bytes) and len(key) == 32 for key in connection._seen_input_ids._values)
        assert connection._identity_budget.used_bytes == (  # pylint: disable=protected-access
            voice_host._INPUT_IDENTITY_BYTES + voice_host._RESPONSE_IDENTITY_BYTES
        )
        await connection.decline_response((item_id,), None)
        assert all(
            all(isinstance(value, bytes) and len(value) == 32 for value in prefix)
            for prefix in connection._resolved_input_prefixes  # pylint: disable=protected-access
        )

        connection._discard_callback_queue()  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_fatal_identity_failure_blocks_signal_and_ledger_growth() -> None:
    async def scenario() -> None:
        connection = _connection()
        with pytest.raises(VoiceBridgeProtocolError, match="identity budget exhausted"):
            connection._identity_budget.fail(  # pylint: disable=protected-access
                "Voice identity budget exhausted",
                1008,
            )
        snapshot = (
            connection._callback_queue.qsize(),  # pylint: disable=protected-access
            connection._callback_queue_bytes,  # pylint: disable=protected-access
            len(connection._seen_messages),  # pylint: disable=protected-access
            len(connection._seen_input_ids),  # pylint: disable=protected-access
            len(connection._seen_response_ids),  # pylint: disable=protected-access
        )

        with pytest.raises(VoiceBridgeProtocolError, match="identity budget exhausted"):
            await connection._enqueue_signal(  # pylint: disable=protected-access
                object(),
                mock.AsyncMock(),
                "signal",
            )
        with pytest.raises(VoiceBridgeProtocolError, match="identity budget exhausted"):
            connection._seen_input_ids.add("in_late")  # pylint: disable=protected-access

        assert snapshot == (
            connection._callback_queue.qsize(),  # pylint: disable=protected-access
            connection._callback_queue_bytes,  # pylint: disable=protected-access
            len(connection._seen_messages),  # pylint: disable=protected-access
            len(connection._seen_input_ids),  # pylint: disable=protected-access
            len(connection._seen_response_ids),  # pylint: disable=protected-access
        )
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_old_playback_outcome_survives_recent_response_eviction_and_runs_once() -> None:
    async def scenario() -> None:
        calls: list[str] = []

        async def on_barge_in(_session, event) -> None:
            calls.append(event.response_id)

        connection = _connection()
        connection._ready = True  # pylint: disable=protected-access
        connection._session = object()  # type: ignore[assignment]  # pylint: disable=protected-access
        connection._on_barge_in = on_barge_in  # pylint: disable=protected-access
        connection._callback_worker = asyncio.create_task(  # pylint: disable=protected-access
            connection._callback_worker_loop()  # pylint: disable=protected-access
        )
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_old",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._seen_response_ids.add("r_old")  # pylint: disable=protected-access
        connection.register_response_item("r_old", "it_old")
        connection._terminal_response_ids.add("r_old")  # pylint: disable=protected-access
        await response._mark_terminal()  # pylint: disable=protected-access
        assert "r_old" not in connection._recent_responses  # pylint: disable=protected-access
        payload = {"response_id": "r_old", "item_id": "it_old", "heard_text": "hello"}

        await connection._handle_playback_terminal(payload, kind="barge_in")  # pylint: disable=protected-access
        await connection._callback_queue.join()  # pylint: disable=protected-access
        await connection._handle_playback_terminal(payload, kind="barge_in")  # pylint: disable=protected-access
        await connection._callback_queue.join()  # pylint: disable=protected-access

        assert calls == ["r_old"]
        connection._callback_worker.cancel()  # pylint: disable=protected-access
        await asyncio.gather(connection._callback_worker, return_exceptions=True)  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_connection_identity_ledgers_fail_closed_without_eviction() -> None:
    async def scenario() -> None:
        connection = _connection()
        response_views = (
            connection._seen_response_ids,  # pylint: disable=protected-access
            connection._terminal_response_ids,  # pylint: disable=protected-access
            connection._playback_outcomes,  # pylint: disable=protected-access
            connection._abandoned_proactive_cancels,  # pylint: disable=protected-access
        )
        seen = connection._seen_response_ids  # pylint: disable=protected-access
        for index in range(seen._max_size):  # pylint: disable=protected-access
            seen.add(f"id_{index}")
        for values in response_views:
            for index in range(values._max_size):  # pylint: disable=protected-access
                values.add(f"id_{index}")
            with pytest.raises(VoiceBridgeProtocolError, match="budget exceeded") as exc_info:
                values.add("id_overflow")
            assert exc_info.value.close_code == 1008
            assert len(values) == values._max_size  # pylint: disable=protected-access
            assert "id_0" in values
            assert "id_overflow" not in values
        seen.clear()
        connection._release_connection_state()  # pylint: disable=protected-access

        input_connection = _connection()
        input_ids = input_connection._seen_input_ids  # pylint: disable=protected-access
        for index in range(input_ids._max_size):  # pylint: disable=protected-access
            input_ids.add(f"input_{index}")
        with pytest.raises(VoiceBridgeProtocolError, match="budget exceeded"):
            input_ids.add("input_overflow")
        assert "input_0" in input_ids
        assert all(isinstance(value, bytes) and len(value) == 32 for value in input_ids._values)
        input_ids.clear()
        input_connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_identity_byte_budget_is_shared_across_connections(monkeypatch) -> None:
    baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
    monkeypatch.setattr(
        voice_host,
        "_MAX_GLOBAL_IDENTITY_BYTES",
        baseline + voice_host._INPUT_IDENTITY_BYTES,  # pylint: disable=protected-access
    )
    first_budget = voice_host._IdentityBudget(1024)  # pylint: disable=protected-access
    second_budget = voice_host._IdentityBudget(1024)  # pylint: disable=protected-access
    first = voice_host._ExactIdSet(2, name="input id", budget=first_budget)  # pylint: disable=protected-access
    second = voice_host._ExactIdSet(2, name="input id", budget=second_budget)  # pylint: disable=protected-access

    first.add("first")
    with pytest.raises(RuntimeError, match="global identity byte budget"):
        second.add("second")

    assert (
        voice_host._GLOBAL_IDENTITY_BYTES == baseline + voice_host._INPUT_IDENTITY_BYTES
    )  # pylint: disable=protected-access
    first.clear()
    assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access


def test_response_identity_flags_share_one_byte_reservation() -> None:
    baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
    budget = voice_host._IdentityBudget(4096)  # pylint: disable=protected-access
    ledger = voice_host._ResponseIdentityLedger(  # pylint: disable=protected-access
        4,
        max_abandoned=2,
        budget=budget,
    )
    seen = voice_host._ResponseIdentityView(ledger, "seen")  # pylint: disable=protected-access
    terminal = voice_host._ResponseIdentityView(ledger, "terminal")  # pylint: disable=protected-access
    playback = voice_host._ResponseIdentityView(ledger, "playback")  # pylint: disable=protected-access
    abandoned = voice_host._ResponseIdentityView(ledger, "abandoned")  # pylint: disable=protected-access

    seen.add("r_1")
    terminal.add("r_1")
    playback.add("r_1")
    abandoned.add("r_1")

    assert (
        voice_host._GLOBAL_IDENTITY_BYTES == baseline + voice_host._RESPONSE_IDENTITY_BYTES
    )  # pylint: disable=protected-access
    assert "r_1" in seen and "r_1" in terminal and "r_1" in playback and "r_1" in abandoned

    ledger.register_item("r_1", "it_1")
    assert ledger.owns_item("r_1", "it_1")
    assert voice_host._GLOBAL_IDENTITY_BYTES == (  # pylint: disable=protected-access
        baseline + voice_host._RESPONSE_IDENTITY_BYTES + voice_host._RESPONSE_ITEM_IDENTITY_BYTES
    )

    playback.remove("r_1")
    abandoned.discard("r_1")
    assert "r_1" in seen and "r_1" in terminal

    seen.clear()
    assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access


def test_callback_identity_overflow_wakes_connection_supervision(monkeypatch) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_ID_TOMBSTONES", 1)
        websocket = _RecordingWebSocket()
        connection = _connection(websocket)
        connection._ready = True  # pylint: disable=protected-access
        connection._seen_response_ids.add("r_existing")  # pylint: disable=protected-access

        with pytest.raises(VoiceBridgeProtocolError, match="response identity budget exceeded"):
            await connection.start_proactive_response(  # pylint: disable=protected-access
                admission_timeout_ms=1000,
                supersede_key=None,
            )

        assert connection.ending
        assert connection._resource_limit_reached.done()  # pylint: disable=protected-access
        assert connection._resource_limit_reached.result().close_code == 1008  # pylint: disable=protected-access
        assert not connection._pending_proactive  # pylint: disable=protected-access
        assert not websocket.sent
        connection._release_connection_state()  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_protocol_identity_failure_preserves_close_code_through_supervision() -> None:
    class BlockingWebSocket(_RecordingWebSocket):
        async def receive(self) -> dict:
            await asyncio.Event().wait()
            raise AssertionError("unreachable")

    async def scenario() -> None:
        connection = _connection(BlockingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        connection._callback_worker = asyncio.create_task(asyncio.Event().wait())  # pylint: disable=protected-access
        connection._signal_runtime_failure(  # pylint: disable=protected-access
            "Voice message dedupe limit exceeded",
            1008,
        )

        with pytest.raises(VoiceBridgeProtocolError, match="dedupe limit exceeded") as exc_info:
            await connection._receive_with_worker_supervision()  # pylint: disable=protected-access

        assert exc_info.value.close_code == 1008
        connection._callback_worker.cancel()  # pylint: disable=protected-access
        await asyncio.gather(connection._callback_worker, return_exceptions=True)  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_abandoned_proactive_identity_is_released_by_timeout() -> None:
    async def scenario() -> None:
        baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
        connection = _connection(_RecordingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_abandoned",
            in_reply_to=None,
            wire_opened=True,
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._seen_response_ids.add(response.response_id)  # pylint: disable=protected-access
        connection._abandoned_proactive_cancels.add(response.response_id)  # pylint: disable=protected-access

        await connection._handle_response_timeout(  # pylint: disable=protected-access
            ResponseTimeoutEvent(stage="idle", response_id=response.response_id)
        )

        assert response.response_id not in connection._abandoned_proactive_cancels  # pylint: disable=protected-access
        connection._release_connection_state()  # pylint: disable=protected-access
        assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access

    asyncio.run(scenario())


def test_release_connection_state_clears_abandoned_identity_records() -> None:
    async def scenario() -> None:
        baseline = voice_host._GLOBAL_IDENTITY_BYTES  # pylint: disable=protected-access
        connection = _connection()
        connection._abandoned_proactive_cancels.add("r_abandoned")  # pylint: disable=protected-access

        connection._release_connection_state()  # pylint: disable=protected-access

        assert not connection._abandoned_proactive_cancels  # pylint: disable=protected-access
        assert voice_host._GLOBAL_IDENTITY_BYTES == baseline  # pylint: disable=protected-access

    asyncio.run(scenario())


@pytest.mark.parametrize("terminal_kind", ["session_end", "shutdown"])
def test_teardown_does_not_allocate_terminal_tombstones(monkeypatch, terminal_kind: str) -> None:
    async def scenario() -> None:
        monkeypatch.setattr(voice_host, "_MAX_ID_TOMBSTONES", 1)
        connection = _connection(_RecordingWebSocket())
        connection._ready = True  # pylint: disable=protected-access
        response = VoiceResponse._create(  # pylint: disable=protected-access
            connection,
            response_id="r_active",
            in_reply_to=("in_active",),
        )
        connection._active_response = response  # pylint: disable=protected-access
        connection._pending_turns[voice_host._identity_digest("in_active")] = (
            response  # pylint: disable=protected-access
        )
        connection._terminal_response_ids.add("r_existing")  # pylint: disable=protected-access

        if terminal_kind == "session_end":
            await connection._handle_session_end({"reason": "caller_hangup"})  # pylint: disable=protected-access
            connection._release_connection_state()  # pylint: disable=protected-access
        else:
            await connection._shutdown_runtime(drain_callbacks=False)  # pylint: disable=protected-access

        assert response.is_terminal
        assert connection._closed or terminal_kind == "session_end"  # pylint: disable=protected-access

    asyncio.run(scenario())
