# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.ai.finetuningsessions.aio import _completion_feed as module
from azure.ai.finetuningsessions.aio import _patch as patch
from azure.ai.finetuningsessions.models import AdamParams, LoRAConfig, SamplingParams


@pytest.mark.parametrize("value", ["true", "false", "True", "1", "", " true", None])
@pytest.mark.parametrize("text_only", [False, True], ids=["tokens", "text-only"])
def test_sync_handshake_exact_value_aliases_and_legacy_polling(monkeypatch, value, text_only):
    from azure.core.credentials import AzureKeyCredential

    from azure.ai.finetuningsessions import FineTuningSession, FineTuningSessionClient

    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda *args: None)
    headers = {} if value is None else {"x-LoOm-UsE-CoMpLeTiOn-FeEd": value}
    create = SimpleNamespace(
        status_code=200,
        headers=headers,
        json=lambda: {"session_id": "model_test1234", "request_id": "load"},
    )
    loaded = SimpleNamespace(status_code=200, json=lambda: {"status": "completed"})
    with FineTuningSessionClient("https://local.test", AzureKeyCredential("test-only")) as client:
        send = Mock(side_effect=[create, loaded])
        monkeypatch.setattr(client, "send_request", send)
        session = FineTuningSession.create(client, base_model="local", lora_config=LoRAConfig(rank=1))
        assert send.call_args_list[0].args[0].headers["X-Loom-Client-Capabilities"] == "use_completion_feed"
        assert "X-Loom-Client-Capabilities" not in send.call_args_list[1].args[0].headers
        assert client._completion_feed_enabled == {"session_test1234": value == "true"}
        assert client._session_resource_ids == {"session_test1234": "model_test1234"}
        assert client._completion_observer is None
        alias = FineTuningSession(client, "test1234")
        sample_kwargs = {
            "sampling_params": SamplingParams(max_tokens=2),
            "checkpoint_id": "local",
            "num_samples": 2,
        }
        if text_only:
            sample_kwargs["text_only_input"] = {"messages": [{"role": "user", "content": "Hi"}]}
        else:
            sample_kwargs["prompt_tokens"] = [1]
        if value == "true":
            observer = Mock()
            monkeypatch.setattr(client, "_get_completion_observer", lambda: observer)
            poll = Mock(side_effect=AssertionError("Enabled sampling must use the observer"))
            monkeypatch.setattr(alias, "_post_and_poll", poll)
            assert alias.sample(**sample_kwargs) is observer.sample.return_value
            assert observer.sample.call_args.args[0] == "model_test1234"
            assert observer.sample.call_args.kwargs.get("text_only_input") == sample_kwargs.get("text_only_input")
            assert observer.sample.call_args.kwargs["num_samples"] == 2
            poll.assert_not_called()
        else:
            poll = Mock(return_value="legacy")
            monkeypatch.setattr(session, "_post_and_poll", poll)
            assert session.sample(**sample_kwargs) == "legacy"
            poll.assert_called_once()
            assert client._completion_observer is None


def test_sync_close_cancels_waiting_samples_and_drains_loop(monkeypatch):
    import concurrent.futures
    import threading

    from azure.ai.finetuningsessions._completion_feed import _SyncCompletionObserver

    started = threading.Event()

    async def pending(*args, **kwargs):
        started.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(patch, "sample", pending)
    owner = _SyncCompletionObserver(
        SimpleNamespace(
            _config=SimpleNamespace(),
            _completion_feed_enabled={},
            _session_resource_ids={},
        )
    )
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            waiting = executor.submit(owner.sample, "session_local")
            assert started.wait(5)
            owner.close()
            with pytest.raises(RuntimeError, match="client is closed"):
                waiting.result(timeout=5)
        assert not owner.thread.is_alive()
        assert owner.loop.is_closed()
        owner.close()
        with pytest.raises(RuntimeError, match="client is closed"):
            owner.sample("session_local")
    finally:
        owner.close()


@pytest.mark.parametrize("close_fails", [False, True])
def test_sync_shutdown_closes_response_that_arrives_after_cancellation(monkeypatch, caplog, close_fails):
    import concurrent.futures
    import threading

    from azure.ai.finetuningsessions._completion_feed import _SyncCompletionObserver

    started, canceled, release = (threading.Event() for _ in range(3))
    response = SimpleNamespace(
        close=Mock(
            side_effect=RuntimeError("private transport details") if close_fails else None,
        )
    )

    def send(*args, **kwargs):
        started.set()
        assert release.wait(5)
        return response

    async def pending(adapter, *args, **kwargs):
        try:
            return await adapter.send_request(object(), stream=True)
        finally:
            canceled.set()

    monkeypatch.setattr(patch, "sample", pending)
    owner = _SyncCompletionObserver(
        SimpleNamespace(
            _config=SimpleNamespace(),
            _completion_feed_enabled={},
            _session_resource_ids={},
            send_request=send,
        )
    )
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            waiting = executor.submit(owner.sample, "session_local")
            assert started.wait(5)
            closing = executor.submit(owner.close)
            assert canceled.wait(5)
            release.set()
            closing.result(timeout=5)
            with pytest.raises(RuntimeError, match="client is closed"):
                waiting.result(timeout=5)
        response.close.assert_called_once()
        assert not owner.thread.is_alive()
        assert owner.loop.is_closed()
        assert "private transport details" not in caplog.text
    finally:
        release.set()
        owner.close()


async def spin_until(predicate):
    for _ in range(200):
        if predicate():
            return
        await asyncio.sleep(0)
    pytest.fail("Observer did not reach expected state")


class Bytes:
    def __init__(self, *chunks):
        self.chunks = chunks

    async def iter_bytes(self):
        for chunk in self.chunks:
            yield chunk


@pytest.mark.parametrize("split", range(1, 6))
async def test_incremental_frames_utf8_control_and_partial_tail(split):
    raw = (
        ": connected\r\n\r\nid: 9-1\r\nevent: completion\r\n"
        'data: {"request_id":"é","status":"failed"}\r\n\r\n'
        'event: end\n\nid: 9-2\nevent: completion\ndata: {"request_id":'
    ).encode()
    frames = [frame async for frame in module._frames(Bytes(*(raw[i : i + split] for i in range(0, len(raw), split))))]
    assert frames == [("9-1", "é", "failed"), ("", "", "end")]


@pytest.mark.parametrize(
    "frame",
    [
        b'id: -1-0\nevent: completion\ndata: {"request_id":"r","status":"completed"}\n\n',
        b"id: 18446744073709551616-0\nevent: completion\ndata: {}\n\n",
        b'id: 1-0\nevent: completion\ndata: {"request_id":"r","status":"pending"}\n\n',
        b"id: 1-0\nevent: completion\ndata: []\n\n",
        b'id: 1-0\nevent: completion\ndata: {"status":"failed"}\n\n',
        b"data: " + b"x" * 65537,
    ],
    ids=["negative", "overflow", "pending", "array", "missing-id", "oversized"],
)
async def test_invalid_frames_never_advance(frame):
    with pytest.raises(ValueError):
        [item async for item in module._frames(Bytes(frame))]


async def test_frames_multiline_data_last_fields_and_ignored_events():
    raw = (
        b"event: unknown\ndata: not-json\nid: invalid\n\n"
        b": keepalive\nunknown: ignored\nevent: ignored\nevent: completion\n"
        b'id: invalid\nid: 1-0\ndata: {"request_id":"r",\n'
        b'data: "status":"completed"}\n\n'
        b"event: unknown\ndata: not-json\n\n"
        b"event: end\n\n"
    )
    assert [frame async for frame in module._frames(Bytes(raw))] == [
        ("1-0", "r", "completed"),
        ("", "", "end"),
    ]


async def test_frame_fields_do_not_carry_over():
    raw = (
        b'id: 1-0\nevent: completion\ndata: {"request_id":"r","status":"completed"}\n\n'
        b'event: completion\ndata: {"request_id":"s","status":"completed"}\n\n'
    )
    frames = module._frames(Bytes(raw))
    assert await anext(frames) == ("1-0", "r", "completed")
    with pytest.raises(ValueError, match="Invalid completion cursor"):
        await anext(frames)


async def test_frame_limit_includes_ignored_lines():
    raw = b": keepalive\n" * (module._MAX_FRAME_BYTES // 11 + 1) + b"\n"
    with pytest.raises(ValueError, match="Completion frame too large"):
        [frame async for frame in module._frames(Bytes(raw))]


@pytest.mark.parametrize(
    "value,enabled",
    [
        ("true", True),
        ("false", False),
        ("True", False),
        ("1", False),
        ("", False),
        (" true", False),
        (None, False),
    ],
)
async def test_handshake_exact_value_and_aliases(monkeypatch, value, enabled):
    headers = {} if value is None else {"x-LoOm-UsE-CoMpLeTiOn-FeEd": value}
    create = SimpleNamespace(
        status_code=200,
        headers=headers,
        json=lambda: {"session_id": "model_test1234", "request_id": "load"},
    )
    loaded = SimpleNamespace(status_code=200, json=lambda: {"status": "completed"})
    client = SimpleNamespace(send_request=AsyncMock(side_effect=[create, loaded]))
    monkeypatch.setattr(patch, "_start_heartbeat", lambda *args: None)
    assert await patch.create_session(client, base_model="local", lora_config=LoRAConfig(rank=1)) == "session_test1234"
    sent = client.send_request.call_args_list[0].args[0]
    assert sent.headers["X-Loom-Client-Capabilities"] == "use_completion_feed"
    assert client._completion_feed_enabled == {"session_test1234": enabled}
    assert patch._client_resource_session_id(client, "test1234") == "model_test1234"
    assert patch._client_resource_session_id(client, "model_test1234") == "model_test1234"
    assert "X-Loom-Client-Capabilities" not in client.send_request.call_args_list[1].args[0].headers


@pytest.fixture
async def feed(monkeypatch):
    instance = module._CompletionFeed(SimpleNamespace(), "session_test1234", {}, {})

    async def watch(stopping):
        # Stand-in for a stream that reaches its end marker once observation is idle.
        while instance.active and not stopping.is_set():
            await asyncio.sleep(0)

    monkeypatch.setattr(instance, "_watch", watch)
    monkeypatch.setattr(instance, "_ack", AsyncMock())
    yield instance
    await asyncio.wait_for(instance.close(), 5)
    await asyncio.sleep(0)


async def test_completion_feed_cache_aliases_resource_route_and_closed_client():
    response = Bytes(b"event: end\n\n")
    response.status_code = 200
    response.headers = {"content-type": "text/event-stream"}
    response.raise_for_status = Mock()
    response.close = AsyncMock()
    client = SimpleNamespace(send_request=AsyncMock(return_value=response))
    patch._ensure_async_state(client)
    client._session_resource_ids["session_test1234"] = "model_test1234"

    feed = patch._get_or_create_completion_feed(client, "test1234")
    assert patch._get_or_create_completion_feed(client, "model_test1234") is feed
    assert patch._get_or_create_completion_feed(client, "session_other") is not feed
    assert len(client._completion_feeds) == 2
    await feed._round(30)
    sent = client.send_request.call_args.args[0]
    assert sent.url.split("?", 1)[0] == "{endpoint}/fine_tuning_sessions/model_test1234/retrieve_futures"
    response.close.assert_awaited_once()

    client._observer_closed = True
    with pytest.raises(RuntimeError, match="closed"):
        patch._get_or_create_completion_feed(client, "test1234")
    with pytest.raises(RuntimeError, match="closed"):
        patch._get_or_create_completion_feed(client, "session_new")


async def test_notification_fetches_allow_256_but_bound_additional_requests(feed):
    active = peak = 0
    saturated = asyncio.Event()
    release = asyncio.Event()

    async def retrieve():
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        if active == 256:
            saturated.set()
        try:
            await release.wait()
            return "result"
        finally:
            active -= 1

    waits = [asyncio.create_task(feed.wait(str(i), retrieve, feed.begin())) for i in range(257)]
    try:
        await asyncio.sleep(0)
        for i in range(257):
            await feed._accept(f"{i + 1}-0", str(i))
        await asyncio.wait_for(saturated.wait(), 5)
        await asyncio.sleep(0)
        assert active == peak == 256
        release.set()
        assert await asyncio.wait_for(asyncio.gather(*waits), 5) == ["result"] * 257
    finally:
        release.set()
        for task in waits:
            task.cancel()
        await asyncio.gather(*waits, return_exceptions=True)


@pytest.mark.parametrize("status", ["completed", "failed"])
async def test_notification_receipt_is_logged_before_accept_backpressure(feed, monkeypatch, caplog, status):
    caplog.set_level("INFO", logger=module.__name__)
    feed.path = "/fine_tuning_sessions/session_test1234/retrieve_futures"
    payload = (
        "id: 1-0\nevent: completion\n" f'data: {{"request_id":"r","status":"{status}","result":"private-payload"}}\n\n'
    ).encode()
    response = Bytes(payload, payload, b"event: end\ndata: {}\n\n")
    response.status_code = 200
    response.headers = {"content-type": "text/event-stream"}
    response.raise_for_status = Mock()
    response.close = AsyncMock()
    feed.client.send_request = AsyncMock(return_value=response)
    release = asyncio.Event()

    async def accept(cursor, request_id):
        assert cursor == "1-0" and request_id == "r"
        assert f"notification_received request_id=r status={status}" in caplog.text
        await release.wait()

    monkeypatch.setattr(feed, "_accept", accept)
    reading = asyncio.create_task(feed._round(30))
    try:
        await spin_until(lambda: "notification_received" in caplog.text)
        assert not reading.done()
    finally:
        release.set()
        await reading
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == module.__name__ and "notification_received" in record.getMessage()
    ]
    expected = f"[completion_feed] notification_received request_id=r status={status}"
    assert messages == [expected, expected]
    assert "private-payload" not in caplog.text
    response.close.assert_awaited_once()


@pytest.mark.parametrize(
    "ending,error",
    [
        ("normal", None),
        ("disconnect", ConnectionError),
        ("cancel", asyncio.CancelledError),
        ("close_failure", RuntimeError),
    ],
)
async def test_sampling_progress_ignores_replayed_notifications(feed, caplog, ending, error):
    caplog.set_level("INFO", logger=module.__name__)
    completed = b'id: 1-0\nevent: completion\ndata: {"request_id":"r","status":"completed"}\n\n'
    failed = b'id: 2-0\nevent: completion\ndata: {"request_id":"s","status":"failed"}\n\n'
    chunks = [completed, completed, failed]
    if ending in ("normal", "close_failure"):
        chunks.append(b"event: end\n\n")
    response = Bytes(*chunks)
    response.status_code = 200
    response.headers = {"content-type": "text/event-stream"}
    response.raise_for_status = Mock()
    response.close = AsyncMock()
    if ending == "close_failure":
        response.close.side_effect = RuntimeError("close failed")

    async def iter_bytes():
        for chunk in response.chunks:
            yield chunk
        if ending == "cancel":
            raise asyncio.CancelledError()

    response.iter_bytes = iter_bytes
    feed.client.send_request = AsyncMock(return_value=response)
    feed.completed_samples = 1
    feed.pending_samples = 2
    if error is None:
        assert await feed._round(30)
    else:
        with pytest.raises(error):
            await feed._round(30)
    summaries = [
        record.getMessage()
        for record in caplog.records
        if record.name == module.__name__ and "Sampling progress" in record.getMessage()
    ]
    assert summaries == ["[completion_feed] Sampling progress: 1 completed, 0 failed since last update; 2 pending"]
    response.close.assert_awaited_once()
    if error is None:
        assert await feed._round(30)
        assert caplog.messages[-1] == (
            "[completion_feed] Sampling progress: 0 completed, 0 failed since last update; 2 pending"
        )


async def test_sampling_progress_is_logged_when_transport_fails(feed, caplog):
    caplog.set_level("INFO", logger=module.__name__)
    feed.failed_samples = 1
    feed.client.send_request = AsyncMock(side_effect=ConnectionError("offline"))
    with pytest.raises(ConnectionError):
        await feed._round(30)
    assert ("[completion_feed] Sampling progress: 0 completed, 1 failed since last update; 0 pending") in caplog.text


async def test_ack_only_call_does_not_log_or_reset_sampling_progress(feed, caplog):
    caplog.set_level("INFO", logger=module.__name__)
    feed.completed_samples = 1
    response = SimpleNamespace(status_code=204, headers={}, raise_for_status=Mock(), close=AsyncMock())
    feed.client.send_request = AsyncMock(return_value=response)
    assert await feed._round(0)
    assert "Sampling progress" not in caplog.text
    assert feed.completed_samples == 1
    response.close.assert_awaited_once()


async def test_owned_backoff_keeps_runner_active_until_it_finishes(feed):
    registration = feed.begin()
    runner = feed.runner
    release = asyncio.Event()
    backoff = asyncio.create_task(feed.call(release.wait))
    try:
        await spin_until(lambda: feed.submissions)
        feed.end(registration)
        assert feed.active
        for _ in range(20):
            await asyncio.sleep(0)
        assert feed.runner is runner
        feed._ack.assert_not_awaited()
    finally:
        release.set()
        await backoff
    done, _ = await asyncio.wait([runner], timeout=1)
    assert runner in done
    assert not feed.active
    assert feed.runner is None
    feed._ack.assert_awaited_once()


@pytest.mark.parametrize("client_close", [False, True], ids=["idle", "client-close"])
async def test_scheduler_wakeup_racing_with_cancellation_joins_runner(feed, client_close):
    retrieve = AsyncMock(return_value="done")
    waiting = asyncio.create_task(feed.wait("q", retrieve, feed.begin()))
    runner = feed.runner
    for _ in range(20):
        await asyncio.sleep(0)
    if client_close:
        closing = asyncio.create_task(feed.close())
        with pytest.raises(RuntimeError, match="client is closed"):
            await waiting
        joining = closing
        retrieve.assert_not_awaited()
    else:
        await feed._accept("1-0", "q")
        assert await waiting == "done"
        joining = runner
        retrieve.assert_awaited_once()
    done, _ = await asyncio.wait([joining], timeout=1)
    assert joining in done
    await joining
    assert feed.runner is None
    assert not feed.requests


async def test_close_bounds_worker_join_before_final_ack(feed, monkeypatch, caplog):
    started, drained = asyncio.Event(), asyncio.Event()

    async def watch(*_):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            try:
                await asyncio.Event().wait()
            finally:
                drained.set()

    monkeypatch.setattr(feed, "_watch", watch)
    monkeypatch.setattr(module, "_STOP_TIMEOUT", 0.01, raising=False)
    registration = feed.begin()
    runner = feed.runner
    await started.wait()
    feed.end(registration)
    await asyncio.wait_for(feed.close(), 1)
    assert runner.done()
    assert drained.is_set()
    assert feed.runner is None
    feed._ack.assert_awaited_once()
    assert "worker shutdown exceeded deadline" in caplog.text


async def test_idle_stream_finishes_its_window_and_serves_new_work(feed, monkeypatch):
    window_end = asyncio.Event()
    rounds = []

    async def round_(wait):
        rounds.append(wait)
        await window_end.wait()
        return True

    monkeypatch.setattr(feed, "_round", round_)
    monkeypatch.setattr(feed, "_watch", module._CompletionFeed._watch.__get__(feed))
    registration = feed.begin()
    runner = feed.runner
    await spin_until(lambda: rounds)
    feed.end(registration)
    for _ in range(20):
        await asyncio.sleep(0)
    assert not feed.active
    assert feed.runner is runner and not runner.done()
    feed._ack.assert_not_awaited()

    waiting = asyncio.create_task(feed.wait("late", AsyncMock(return_value="done"), feed.begin()))
    await spin_until(lambda: "late" in feed.requests)
    await feed._accept("1-0", "late")
    assert await waiting == "done"

    window_end.set()
    done, _ = await asyncio.wait([runner], timeout=1)
    assert runner in done
    assert rounds == [module._STREAM_WAIT_SECONDS]
    feed._ack.assert_awaited_once()
    assert feed.runner is None


async def test_idle_stream_failure_does_not_reconnect(feed, monkeypatch, caplog):
    async def failed_round(wait):
        feed.registrations.discard(0)
        raise ConnectionError("closed stream")

    monkeypatch.setattr(feed, "_round", AsyncMock(side_effect=failed_round))
    feed.registrations.add(0)
    await asyncio.wait_for(module._CompletionFeed._watch(feed, asyncio.Event()), 0.1)
    feed._round.assert_awaited_once()
    assert "stream failed" not in caplog.text


async def test_becoming_idle_during_reconnect_backoff_opens_no_new_stream(feed, monkeypatch, caplog):
    monkeypatch.setattr(feed, "_round", AsyncMock(side_effect=ConnectionError("closed stream")))
    monkeypatch.setattr(feed, "_watch", module._CompletionFeed._watch.__get__(feed))
    monkeypatch.setattr(module, "_RECONNECT_INITIAL_DELAY", 0.05)
    registration = feed.begin()
    runner = feed.runner
    await spin_until(lambda: "stream failed" in caplog.text)
    feed.end(registration)
    done, _ = await asyncio.wait([runner], timeout=1)
    assert runner in done
    feed._round.assert_awaited_once()
    feed._ack.assert_awaited_once()


async def test_stopping_generation_does_not_back_off_after_stream_failure(feed, monkeypatch, caplog):
    stopping = asyncio.Event()

    async def failed_round(wait):
        stopping.set()
        raise ConnectionError("closed stream")

    monkeypatch.setattr(feed, "_round", failed_round)
    await asyncio.wait_for(module._CompletionFeed._watch(feed, stopping), 0.1)
    assert "stream failed" not in caplog.text


async def test_early_prefix_obligation_duplicates_and_history(feed):
    registration = feed.begin()
    await feed._accept("2-0", "early")
    await feed._accept("5-9", "history")
    assert feed.read_cursor == "5-9"
    assert feed.processed_cursor == "0-0"
    blocked = asyncio.Event()

    async def retrieve():
        await blocked.wait()
        return "hydrated"

    fetch = AsyncMock(side_effect=retrieve)
    waiter = asyncio.create_task(feed.wait("early", fetch, registration))
    await spin_until(lambda: "early" in feed.requests)
    assert feed.processed_cursor == "5-9"
    assert not waiter.done()
    await feed._accept("6-0", "early")
    await feed._accept("7-0", "history")
    blocked.set()
    assert await waiter == "hydrated"
    await feed._accept("10-0", "early")
    await feed._accept("9-0", "early")
    assert fetch.await_count == 1
    assert feed.processed_cursor == "10-0"


async def test_early_buffer_backpressure_released_by_registration(feed):
    registration = feed.begin()
    for i in range(1, 401):
        await feed._accept(f"{i}-0", "history")
    accepting = asyncio.create_task(feed._accept("401-0", "history"))
    await asyncio.sleep(0)
    assert not accepting.done()
    assert len(feed.positions) == 400
    wait = asyncio.create_task(feed.wait("owned", AsyncMock(return_value="done"), registration))
    await spin_until(lambda: feed.registering == 0)
    await accepting
    assert not feed.positions
    await feed._accept("402-0", "owned")
    assert await wait == "done"


async def test_later_submissions_do_not_hold_historical_ack_positions(feed):
    first = feed.begin()
    await feed._accept("1-0", "history")
    second = feed.begin()
    await feed._accept("2-0", "second")
    feed.end(first)
    assert feed.processed_cursor == "1-0"
    third = feed.begin()
    wait = asyncio.create_task(feed.wait("second", AsyncMock(return_value="done"), second))
    assert await wait == "done"
    assert feed.registering == 1
    assert feed.processed_cursor == "2-0"
    feed.end(third)


async def test_registration_responses_can_finish_out_of_order(feed):
    first = feed.begin()
    await feed._accept("1-0", "first")
    second = feed.begin()
    feed.end(second)
    assert feed.processed_cursor == "0-0"
    retrieve = AsyncMock(return_value="hydrated")
    assert await feed.wait("first", retrieve, first) == "hydrated"
    assert retrieve.await_count == 1
    assert feed.processed_cursor == "1-0"


async def test_sparse_600_300_age_and_notification_coalescing(feed, monkeypatch):
    clock = SimpleNamespace(now=10.0)
    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: clock.now))
    retrieve = AsyncMock(side_effect=[None, "done"])
    registration = feed.begin()
    waiting = asyncio.create_task(feed.wait("slow", retrieve, registration))
    await spin_until(lambda: "slow" in feed.requests)
    assert feed.requests["slow"].due == 610
    clock.now = 609.9
    feed.changed.set()
    await asyncio.sleep(0)
    assert retrieve.await_count == 0
    clock.now = 610
    feed.changed.set()
    await spin_until(lambda: retrieve.await_count == 1 and feed.requests["slow"].task is None)
    assert feed.requests["slow"].due == 910
    clock.now = 909.9
    feed.changed.set()
    await asyncio.sleep(0)
    assert retrieve.await_count == 1
    clock.now = 910
    feed.changed.set()
    await feed._accept("1-0", "slow")
    await feed._accept("2-0", "slow")
    assert await waiting == "done"
    assert retrieve.await_count == 2


async def test_pending_notified_result_keeps_obligation_without_duplicate_fetch(feed, monkeypatch):
    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: clock.now))
    retrieve = AsyncMock(side_effect=[None, "hydrated"])
    registration = feed.begin()
    waiting = asyncio.create_task(feed.wait("r", retrieve, registration))
    await spin_until(lambda: "r" in feed.requests)
    await feed._accept("1-0", "r")
    await spin_until(lambda: retrieve.await_count == 1 and feed.requests["r"].task is None)
    await feed._accept("2-0", "r")
    assert retrieve.await_count == 1
    assert feed.processed_cursor == "2-0"
    clock.now = 300
    feed.changed.set()
    assert await waiting == "hydrated"


async def test_cancel_one_close_other_idle_reuse_and_registration_race(feed):
    fetch = AsyncMock(return_value="done")
    first = feed.begin()
    a = asyncio.create_task(feed.wait("a", fetch, first))
    second = feed.begin()
    b = asyncio.create_task(feed.wait("b", fetch, second))
    await spin_until(lambda: len(feed.requests) == 2)
    a.cancel()
    with pytest.raises(asyncio.CancelledError):
        await a
    await feed._accept("1-0", "a")
    await feed._accept("2-0", "b")
    assert await b == "done"
    assert fetch.await_count == 1
    await spin_until(lambda: feed.runner is None)
    assert feed.processed_cursor == "2-0"
    registration = feed.begin()
    pending = asyncio.create_task(feed.wait("c", fetch, registration))
    await spin_until(lambda: "c" in feed.requests)
    await feed.close()
    with pytest.raises(RuntimeError, match="closed"):
        await pending
    assert feed.runner is None
    assert not feed.requests
    with pytest.raises(RuntimeError, match="closed"):
        feed.begin()


async def test_single_pending_retrieval_preserves_existing_terminal_normalization(
    monkeypatch,
):
    class Response:
        status_code = 200
        headers = None

        def json(self):
            return {"status": "pending"}

    client = SimpleNamespace(send_request=AsyncMock(return_value=Response()))
    assert await patch._poll(client, "session_test1234", "r", "sample", _pending_once=True) is None
    assert client.send_request.await_count == 1


async def test_full_sample_permit_lifetime_and_alias_observer(monkeypatch, feed):
    client = SimpleNamespace()
    patch._ensure_async_state(client)
    client._sample_semaphore = asyncio.Semaphore(1)
    client._completion_feed_enabled["session_test1234"] = True
    client._completion_feeds["session_test1234"] = feed
    post = AsyncMock(side_effect=[("a", "sample"), ("b", "sample")])
    monkeypatch.setattr(patch, "_post_sample", post)
    monkeypatch.setattr(patch, "_poll", AsyncMock(return_value="done"))
    kwargs = {
        "prompt_tokens": [1],
        "sampling_params": SamplingParams(max_tokens=1),
        "checkpoint_id": "local",
    }
    a = asyncio.create_task(patch.sample(client, "model_test1234", **kwargs))
    await spin_until(lambda: "a" in feed.requests)
    monkeypatch.setattr(patch, "_post", AsyncMock(return_value=("optim", "optim_step")))
    assert await patch.optim_step(client, "model_test1234", AdamParams(learning_rate=1e-4)) == "done"
    assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (0, 0, 1)
    b = asyncio.create_task(patch.sample(client, "test1234", **kwargs))
    await asyncio.sleep(0)
    assert post.await_count == 1
    assert feed.pending_samples == 1
    await feed._accept("1-0", "a")
    assert await a == "done"
    await spin_until(lambda: "b" in feed.requests)
    assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (1, 0, 1)
    await feed._accept("2-0", "b")
    assert await b == "done"
    assert post.await_count == 2
    assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (2, 0, 0)


@pytest.mark.parametrize("fails", [False, True])
async def test_sampling_progress_counts_one_final_outcome_across_retry(monkeypatch, feed, fails):
    from azure.ai.finetuningsessions import RequestRetryableError

    client = SimpleNamespace()
    patch._ensure_async_state(client)
    client._completion_feed_enabled["session_test1234"] = True
    client._completion_feeds["session_test1234"] = feed
    retry_started = asyncio.Event()
    release_retry = asyncio.Event()
    attempts = 0

    async def post(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            retry_started.set()
            await release_retry.wait()
        return str(attempts), "sample"

    monkeypatch.setattr(patch, "_post_sample", post)
    monkeypatch.setattr(patch, "_retryable_resubmit_wait", lambda delay: 0)
    monkeypatch.setattr(
        patch,
        "_poll",
        AsyncMock(
            side_effect=[
                RequestRetryableError("retry"),
                RuntimeError("terminal failure") if fails else "done",
            ]
        ),
    )
    waiting = asyncio.create_task(
        patch.sample(
            client,
            "model_test1234",
            [1],
            SamplingParams(max_tokens=1),
            checkpoint_id="local",
        )
    )
    try:
        await spin_until(lambda: "1" in feed.requests)
        await feed._accept("1-0", "1")
        await asyncio.wait_for(retry_started.wait(), 5)
        assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (0, 0, 1)
        release_retry.set()
        await spin_until(lambda: "2" in feed.requests)
        await feed._accept("2-0", "2")
        if fails:
            with pytest.raises(RuntimeError, match="terminal failure"):
                await waiting
        else:
            assert await waiting == "done"
        assert attempts == 2
        assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (
            int(not fails),
            int(fails),
            0,
        )
    finally:
        release_retry.set()
        waiting.cancel()
        await asyncio.gather(waiting, return_exceptions=True)


@pytest.mark.parametrize("cancel", [False, True])
async def test_sampling_progress_owns_submissions_and_excludes_cancellation(monkeypatch, feed, cancel):
    client = SimpleNamespace()
    patch._ensure_async_state(client)
    client._completion_feed_enabled["session_test1234"] = True
    client._completion_feeds["session_test1234"] = feed
    submitting = asyncio.Event()

    async def post(*args, **kwargs):
        assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (0, 0, 1)
        submitting.set()
        if cancel:
            await asyncio.Event().wait()
        raise RuntimeError("submit failed")

    monkeypatch.setattr(patch, "_post_sample", post)
    waiting = asyncio.create_task(
        patch.sample(
            client,
            "model_test1234",
            [1],
            SamplingParams(max_tokens=1),
            checkpoint_id="local",
        )
    )
    try:
        await asyncio.wait_for(submitting.wait(), 5)
        if cancel:
            waiting.cancel()
            with pytest.raises(asyncio.CancelledError):
                await waiting
        else:
            with pytest.raises(RuntimeError, match="submit failed"):
                await waiting
        assert (feed.completed_samples, feed.failed_samples, feed.pending_samples) == (
            0,
            int(not cancel),
            0,
        )
    finally:
        waiting.cancel()
        await asyncio.gather(waiting, return_exceptions=True)


async def test_only_retrieved_retry_authorizes_resubmit_with_new_age(monkeypatch, feed):
    from azure.ai.finetuningsessions import RequestRetryableError

    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr(module, "time", SimpleNamespace(monotonic=lambda: clock.now))
    monkeypatch.setattr(patch, "_retryable_resubmit_wait", lambda delay: 0)
    poll = AsyncMock(
        side_effect=[
            RequestRetryableError("retry", error_code="request_orphaned"),
            "done",
        ]
    )
    monkeypatch.setattr(patch, "_poll", poll)
    post = AsyncMock(return_value=("fresh", "sample"))
    registration = feed.begin()
    waiting = asyncio.create_task(
        patch._poll_with_resubmit(
            SimpleNamespace(),
            "session_test1234",
            "old",
            "sample",
            "/sample",
            {},
            post_fn=post,
            _feed=feed,
            _registration=registration,
        )
    )
    await spin_until(lambda: "old" in feed.requests)
    clock.now = 100
    await feed._accept("1-0", "old")
    await spin_until(lambda: "fresh" in feed.requests)
    assert feed.requests["fresh"].due == 700
    assert post.await_count == 1
    await feed._accept("2-0", "fresh")
    assert await waiting == "done"


async def test_normal_end_reconnects_immediately_errors_back_off(monkeypatch, feed, caplog):
    rounds = AsyncMock(
        side_effect=[
            True,
            ConnectionError(),
            ConnectionError(),
            asyncio.CancelledError(),
        ]
    )
    monkeypatch.setattr(feed, "_round", rounds)
    sleep = AsyncMock()
    monkeypatch.setattr(module.asyncio, "sleep", sleep)
    monkeypatch.setattr(module.random, "uniform", lambda low, high: 1)
    feed.registrations.add(0)
    with pytest.raises(asyncio.CancelledError):
        await module._CompletionFeed._watch(feed, asyncio.Event())
    assert [call.args[0] for call in sleep.call_args_list] == [1, 2]
    assert caplog.text.count("stream failed") == 2


@pytest.mark.parametrize(
    "retry_after, expected_delay",
    [("5", 5), ("0", 1), ("malformed", 1), ("nan", 1), ("600", 60)],
)
async def test_feed_reconnect_honors_bounded_retry_after_without_losing_progress(
    monkeypatch, feed, caplog, retry_after, expected_delay
):
    from azure.core.exceptions import HttpResponseError

    failure = HttpResponseError(message="private transport details")
    failure.response = SimpleNamespace(headers={"Retry-After": retry_after})
    monkeypatch.setattr(
        feed,
        "_round",
        AsyncMock(side_effect=[failure, asyncio.CancelledError()]),
    )
    sleep = AsyncMock()
    monkeypatch.setattr(module.asyncio, "sleep", sleep)
    monkeypatch.setattr(module.random, "uniform", lambda low, high: 1)
    feed.read_cursor, feed.processed_cursor = "10-0", "9-0"
    feed.registrations.add(0)

    with pytest.raises(asyncio.CancelledError):
        await module._CompletionFeed._watch(feed, asyncio.Event())

    sleep.assert_awaited_once_with(expected_delay)
    assert (feed.read_cursor, feed.processed_cursor) == ("10-0", "9-0")
    assert "private transport details" not in caplog.text


async def test_close_during_registration_and_idle_final_ack_failure(feed, monkeypatch, caplog):
    monkeypatch.setattr(feed, "_round", AsyncMock(side_effect=ConnectionError("ACK failure")))
    monkeypatch.setattr(feed, "_ack", module._CompletionFeed._ack.__get__(feed))
    registration = feed.begin()
    feed.end(registration)
    await spin_until(lambda: feed.runner is None)
    assert "final ACK failed" in caplog.text
    registration = feed.begin()
    await feed.close()
    with pytest.raises(RuntimeError, match="closed"):
        await feed.wait("late", AsyncMock(), registration)
    assert feed.registering == 0
    assert feed.runner is None


async def test_new_registration_during_idle_ack_is_not_stranded(feed, monkeypatch):
    acknowledging = asyncio.Event()
    release_ack = asyncio.Event()

    async def ack():
        acknowledging.set()
        await release_ack.wait()

    monkeypatch.setattr(feed, "_ack", ack)
    registration = feed.begin()
    feed.end(registration)
    await acknowledging.wait()
    registration = feed.begin()
    waiting = asyncio.create_task(feed.wait("new", AsyncMock(return_value="done"), registration))
    await spin_until(lambda: "new" in feed.requests)
    release_ack.set()
    await feed._accept("1-0", "new")
    assert await waiting == "done"
    await spin_until(lambda: feed.runner is None)


async def test_close_interrupts_owned_submit_without_canceling_backend(feed, monkeypatch):
    submitted = asyncio.Event()
    drained = asyncio.Event()

    async def post(*args, **kwargs):
        submitted.set()
        try:
            await asyncio.Event().wait()
        finally:
            drained.set()

    monkeypatch.setattr(patch, "_post_sample", post)
    client = SimpleNamespace()
    patch._ensure_async_state(client)
    client._completion_feed_enabled["session_test1234"] = True
    client._completion_feeds["session_test1234"] = feed
    waiting = asyncio.create_task(
        patch.sample(
            client,
            "session_test1234",
            [1],
            SamplingParams(max_tokens=1),
            checkpoint_id="local",
        )
    )
    await submitted.wait()
    await asyncio.gather(feed.close(), feed.close())
    with pytest.raises(RuntimeError, match="closed"):
        await waiting
    assert drained.is_set()
    assert feed.registering == 0
    assert not feed.submissions
    assert feed.runner is None
