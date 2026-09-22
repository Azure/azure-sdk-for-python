"""Bounded-wave behavior for async forward/backward chunk submission."""
from __future__ import annotations

import asyncio
import threading
import time

import pytest

from azure.ai.finetuningsessions.aio import _patch as _aio_mod
from azure.ai.finetuningsessions.models import (
    Datum,
    ForwardBackwardOperationResult,
    ModelInput,
    ModelInputChunk,
    TensorData,
)


def _result(total_loss, output_ids, metric):
    return ForwardBackwardOperationResult(
        {
            "total_loss": total_loss,
            "loss_fn_outputs": [{"id": output_id} for output_id in output_ids],
            "metrics": {"loss:mean": metric, "spread:slack": metric},
        }
    )


def _realistic_batch(datum_count=96, shifts_per_datum=10, tokens_per_shift=128):
    shift_tokens = list(range(tokens_per_shift))
    sequence_length = shifts_per_datum * tokens_per_shift
    target_tokens = [1.0] * sequence_length
    weights = [1.0] * sequence_length
    advantages = [0.5] * sequence_length
    logprobs = [-0.5] * sequence_length
    return [
        Datum(
            model_input=ModelInput(
                chunks=[
                    ModelInputChunk(tokens=shift_tokens)
                    for _ in range(shifts_per_datum)
                ]
            ),
            loss_fn_inputs={
                "target_tokens": TensorData(data=target_tokens),
                "weights": TensorData(data=weights),
                "advantages": TensorData(data=advantages),
                "logprobs": TensorData(data=logprobs),
            },
        )
        for _ in range(datum_count)
    ]


async def _wait_for_thread_event(event):
    while not event.is_set():
        await asyncio.sleep(0)


async def test_forward_backward_post_chunking_does_not_block_event_loop(monkeypatch):
    chunking_started = threading.Event()
    release_chunking = threading.Event()
    ticker_count = 0

    def _slow_chunk_data(batch):
        chunking_started.set()
        assert release_chunking.wait(timeout=1)
        return [batch]

    async def _post_chunks(client, session_id, chunks, *, loss_fn, loss_fn_config):
        del client, session_id, loss_fn, loss_fn_config
        return chunks

    async def _ticker():
        nonlocal ticker_count
        while not release_chunking.is_set():
            ticker_count += 1
            await asyncio.sleep(0)

    monkeypatch.setattr(_aio_mod, "_chunk_data", _slow_chunk_data)
    monkeypatch.setattr(_aio_mod, "_forward_backward_chunks_post", _post_chunks)

    post_task = asyncio.create_task(
        _aio_mod.forward_backward_post(object(), "session_deadbeef", ["datum"])
    )
    ticker_task = asyncio.create_task(_ticker())
    await _wait_for_thread_event(chunking_started)
    for _ in range(10):
        await asyncio.sleep(0)

    assert ticker_count > 1
    release_chunking.set()
    assert await post_task == [["datum"]]
    await ticker_task


async def test_offloaded_chunk_output_matches_synchronous_output():
    batch = _realistic_batch(datum_count=8)
    expected = _aio_mod._chunk_data(batch)

    actual = await _aio_mod._chunk_data_async(batch)

    assert actual == expected


async def test_large_realistic_batch_keeps_loop_drift_under_one_second(monkeypatch):
    batch = _realistic_batch()
    expected = _aio_mod._chunk_data(batch)
    original_chunk_data = _aio_mod._chunk_data
    stop_ticker = asyncio.Event()
    loop_drifts = []

    def _slow_real_chunk_data(data):
        time.sleep(1.05)
        return original_chunk_data(data)

    async def _ticker():
        loop = asyncio.get_running_loop()
        previous_tick = loop.time()
        while not stop_ticker.is_set():
            await asyncio.sleep(0.01)
            current_tick = loop.time()
            loop_drifts.append(max(0.0, current_tick - previous_tick - 0.01))
            previous_tick = current_tick

    monkeypatch.setattr(_aio_mod, "_chunk_data", _slow_real_chunk_data)
    ticker_task = asyncio.create_task(_ticker())
    actual = await _aio_mod._chunk_data_async(batch)
    stop_ticker.set()
    await ticker_task

    assert actual == expected
    assert loop_drifts
    assert max(loop_drifts) < 1.0


async def test_chunking_cancellation_drains_worker(monkeypatch):
    chunking_started = threading.Event()
    release_chunking = threading.Event()
    chunking_finished = threading.Event()

    def _slow_chunk_data(batch):
        del batch
        chunking_started.set()
        assert release_chunking.wait(timeout=1)
        chunking_finished.set()
        return []

    monkeypatch.setattr(_aio_mod, "_chunk_data", _slow_chunk_data)
    chunking_task = asyncio.create_task(_aio_mod._chunk_data_async([]))
    await _wait_for_thread_event(chunking_started)
    chunking_task.cancel()
    for _ in range(10):
        await asyncio.sleep(0)

    assert not chunking_task.done()
    release_chunking.set()
    with pytest.raises(asyncio.CancelledError):
        await chunking_task
    assert chunking_finished.is_set()


async def test_forward_backward_chunks_post_sequentially_in_input_order(monkeypatch):
    posted_chunks = []

    async def _post(client, subpath, body):
        del client, subpath
        chunk = body.forward_backward_input.data
        posted_chunks.append(chunk)
        await asyncio.sleep(0)
        return f"request_{len(posted_chunks)}", "forward_backward"

    monkeypatch.setattr(_aio_mod, "_post", _post)
    chunks = [["a"], ["b", "c"], ["d"]]

    pending = await _aio_mod._forward_backward_chunks_post(
        object(),
        "session_deadbeef",
        chunks,
        loss_fn="cross_entropy",
        loss_fn_config=None,
    )

    assert posted_chunks == chunks
    assert [spec.request_id for spec in pending._posted] == [
        "request_1",
        "request_2",
        "request_3",
    ]


async def test_optim_step_is_not_posted_until_all_forward_backward_chunks_complete(
    monkeypatch,
):
    events = []
    polling_started = asyncio.Event()
    release_polling = asyncio.Event()

    class _ForwardBackwardPending:
        _posted = [object(), object()]

        async def poll_result(self, **kwargs):
            del kwargs
            events.append("forward_backward_poll_started")
            polling_started.set()
            await release_polling.wait()
            events.append("forward_backward_poll_completed")
            return _result(1.0, ["a", "b"], 2.0)

    class _OptimPending:
        async def poll_result(self):
            return "optim_completed"

    async def _post_chunks(client, session_id, chunks, *, loss_fn, loss_fn_config):
        del client, session_id, chunks, loss_fn, loss_fn_config
        events.append("forward_backward_posted")
        return _ForwardBackwardPending()

    async def _post_optim(client, session_id, adam_params):
        del client, session_id, adam_params
        events.append("optim_posted")
        return _OptimPending()

    monkeypatch.setattr(_aio_mod, "_chunk_data", lambda batch: [["a"], ["b"]])
    monkeypatch.setattr(_aio_mod, "_forward_backward_chunks_post", _post_chunks)
    monkeypatch.setattr(_aio_mod, "optim_step_post", _post_optim)

    forward_backward_submission = asyncio.create_task(
        _aio_mod.forward_backward_async(object(), "session_deadbeef", ["batch"])
    )
    await polling_started.wait()
    assert not forward_backward_submission.done()
    assert "optim_posted" not in events

    release_polling.set()
    forward_backward_result = await forward_backward_submission
    await forward_backward_result
    optim_result = await _aio_mod.optim_step_async(object(), "session_deadbeef", object())
    assert await optim_result == "optim_completed"
    assert events == [
        "forward_backward_posted",
        "forward_backward_poll_started",
        "forward_backward_poll_completed",
        "optim_posted",
    ]


async def test_forward_backward_async_posts_and_drains_bounded_waves(monkeypatch):
    chunks = [["a"], ["b", "c"], ["d"], ["e"], ["f"]]
    events = []

    class _Pending:
        def __init__(self, wave):
            self._wave = wave

        async def _poll_chunk_results(self, **kwargs):
            output_ids = [item for chunk in self._wave for item in chunk]
            events.append(("poll", output_ids, kwargs))
            chunk_indices = {"a": 1, "b": 2, "d": 3, "e": 4, "f": 5}
            return [
                _result(
                    float(chunk_indices[chunk[0]]),
                    chunk,
                    float(chunk_indices[chunk[0]] * 10),
                )
                for chunk in self._wave
            ]

    async def _post_wave(
        client,
        session_id,
        wave,
        *,
        loss_fn,
        loss_fn_config,
    ):
        del client, session_id, loss_fn, loss_fn_config
        output_ids = [item for chunk in wave for item in chunk]
        events.append(("post", output_ids))
        return _Pending(wave)

    monkeypatch.setattr(_aio_mod, "_chunk_data", lambda batch: chunks)
    monkeypatch.setattr(_aio_mod, "_forward_backward_chunks_post", _post_wave)

    result_future = await _aio_mod.forward_backward_async(
        object(),
        "session_deadbeef",
        [],
        poll_min_sec=0.25,
        poll_max_sec=0.5,
        max_chunks_per_wave=2,
    )
    result = await result_future

    assert events == [
        ("post", ["a", "b", "c"]),
        ("poll", ["a", "b", "c"], {"poll_min_sec": 0.25, "poll_max_sec": 0.5}),
        ("post", ["d", "e"]),
        ("poll", ["d", "e"], {"poll_min_sec": 0.25, "poll_max_sec": 0.5}),
        ("post", ["f"]),
        ("poll", ["f"], {"poll_min_sec": 0.25, "poll_max_sec": 0.5}),
    ]
    assert result.total_loss == 15.0
    assert [item["id"] for item in result["loss_fn_outputs"]] == [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
    ]
    weighted_mean = (10 + 20 * 2 + 30 + 40 + 50) / 6
    assert result.metrics["loss:mean"] == pytest.approx(weighted_mean)
    assert result.metrics["spread:slack"] == pytest.approx(50 - weighted_mean)


async def test_forward_backward_async_default_keeps_all_chunks_in_one_submission(
    monkeypatch,
):
    pending = type("Pending", (), {"_posted": [object(), object()]})()
    pending.poll_result = lambda: asyncio.sleep(0, result=_result(1.0, ["a"], 2.0))
    calls = []

    async def _post_all(client, session_id, chunks, *, loss_fn, loss_fn_config):
        del client, session_id, loss_fn, loss_fn_config
        calls.append(chunks)
        return pending

    monkeypatch.setattr(_aio_mod, "_chunk_data", lambda batch: [["a"], ["b"], ["c"]])
    monkeypatch.setattr(_aio_mod, "_forward_backward_chunks_post", _post_all)

    result_future = await _aio_mod.forward_backward_async(object(), "session_deadbeef", ["batch"])

    assert calls == [[['a'], ['b'], ['c']]]
    assert (await result_future).total_loss == 1.0


async def test_optim_step_async_default_does_not_pass_none_poll_kwargs(monkeypatch):
    class _Pending:
        async def poll_result(self):
            return "done"

    async def _post(client, session_id, adam_params):
        del client, session_id, adam_params
        return _Pending()

    monkeypatch.setattr(_aio_mod, "optim_step_post", _post)

    result_task = await _aio_mod.optim_step_async(object(), "session_deadbeef", object())

    assert await result_task == "done"


async def test_optim_step_async_propagates_poll_controls(monkeypatch):
    seen = {}

    class _Pending:
        async def poll_result(self, **kwargs):
            seen.update(kwargs)
            return "done"

    async def _post(client, session_id, adam_params):
        del client, session_id, adam_params
        return _Pending()

    monkeypatch.setattr(_aio_mod, "optim_step_post", _post)

    result_task = await _aio_mod.optim_step_async(
        object(),
        "session_deadbeef",
        object(),
        poll_min_sec=0.25,
        poll_max_sec=0.5,
    )

    assert await result_task == "done"
    assert seen == {"poll_min_sec": 0.25, "poll_max_sec": 0.5}


@pytest.mark.parametrize("wave_size", [0, -1])
async def test_forward_backward_async_rejects_non_positive_wave_size(wave_size):
    with pytest.raises(ValueError, match="max_chunks_per_wave must be positive"):
        await _aio_mod.forward_backward_async(
            object(),
            "session_deadbeef",
            [],
            max_chunks_per_wave=wave_size,
        )