# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Read tracing must preserve results and record the same SDK timing boundary."""

import asyncio
import importlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import pytest


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[1] / "workloads"))
    return tuple(importlib.import_module(name) for name in ("perf_read_trace", "workload_utils", "perf_stats"))


def test_bounded_retention_keeps_global_slowest_and_reports_evictions(modules, tmp_path):
    trace = modules[0].ReadTrace("rust", capacity=2, top_count=2, slow_ms=1)
    for duration in (100, 80, 5, 4, 3):
        state, token = trace.begin(0, {})
        state.update(sdk_start_ns=0, sdk_end_ns=duration * 1_000_000, outcome="success")
        trace.finish(state, token)
    assert [v["sdk_call_ms"] for v in trace.calls] == [4, 3]
    assert trace.counts["evicted_calls"] == 3
    assert sorted(v[0] for v in trace.top) == [80, 100]
    for i in range(3):
        trace.event("slot_wait", i, i + 1)
    assert trace.counts["evicted_events"] == 1
    path = tmp_path / "trace.json"
    trace.save(path, measured_count=5, measured_errors=0)
    assert [row["sdk_call_ms"] for row in json.loads(path.read_text())["top"]] == [100, 80]
    with pytest.raises(FileExistsError):
        trace.save(path, measured_count=5, measured_errors=0)
    with pytest.raises(RuntimeError, match="population"):
        trace.save(tmp_path / "bad.json", measured_count=4, measured_errors=0)


def test_read_result_hook_headers_and_exact_stats_timing(modules, monkeypatch):
    trace_module, utils, stats_module = modules
    stats = stats_module.Stats()
    trace = stats.read_trace = trace_module.ReadTrace("rust", slow_ms=0.000001)
    hook_calls = []
    recorded = []
    original = stats.record

    def record(*args, **kwargs):
        recorded.append(kwargs)
        return original(*args, **kwargs)

    monkeypatch.setattr(stats, "record", record)

    async def read(*args, response_hook, **kwargs):
        response_hook({
            "x-ms-activity-id": "activity-1",
            "x-ms-cosmos-sdk-diagnostics": "d" * 9000,
            "authorization": "must-not-be-retained",
        }, {"secret-document": "must-not-be-retained"})
        return {"id": "order-42"}

    result = asyncio.run(utils._fixed_rate_call_async(
        "ReadItem", stats, time.perf_counter_ns(), read,
        response_hook=lambda headers, body: hook_calls.append(1)))
    assert result == {"id": "order-42"} and hook_calls == [1]
    row = trace.calls[0]
    assert row["sdk_call_ms"] == recorded[0]["sdk_call_ms"]
    assert row["delay_before_call_ms"] == recorded[0]["delay_before_call_ms"]
    assert row["headers"]["x-ms-activity-id"] == "activity-1"
    assert len(row["headers"]["x-ms-cosmos-sdk-diagnostics"]) == 8192
    assert row["truncated_headers"] == ["x-ms-cosmos-sdk-diagnostics"]
    assert "must-not-be-retained" not in json.dumps(row)
    assert trace.current.get() is None and not trace.active


def test_errors_cancellation_and_missing_headers_are_explicit(modules, tmp_path):
    trace_module, utils, stats_module = modules
    stats = stats_module.Stats()
    trace = stats.read_trace = trace_module.ReadTrace("core-python")

    async def fail(**kwargs):
        raise ValueError("example failure")

    assert asyncio.run(utils._fixed_rate_call_async("ReadItem", stats, time.perf_counter_ns(), fail)) is None
    assert trace.calls[0]["exception_type"] == "ValueError"
    assert trace.calls[0]["headers"] == {}
    trace.save(tmp_path / "error.json", measured_count=0, measured_errors=1)

    async def cancel(**kwargs):
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(utils._fixed_rate_call_async("ReadItem", stats, time.perf_counter_ns(), cancel))
    assert trace.counts["cancelled"] == 1 and not trace.active
    with pytest.raises(RuntimeError, match="outcomes"):
        trace.save(tmp_path / "cancelled.json", measured_count=1, measured_errors=1)


def test_concurrent_calls_keep_their_own_binding_spans_and_restore_patches(modules):
    trace_module, utils, stats_module = modules
    trace = trace_module.ReadTrace("rust", slow_ms=0.000001)
    stats = stats_module.Stats()
    stats.read_trace = trace

    class Adapter:
        async def _ensure_driver_handle(self):
            await asyncio.sleep(0)
            return 1

    async def binding(item):
        await asyncio.sleep(0.001)
        return item

    native = SimpleNamespace(read_item_async=binding)
    original_ensure = Adapter._ensure_driver_handle
    original_wait = utils._wait_for_launch_slot

    async def run():
        trace.install(stats, utils, Adapter, native)
        await trace.start()
        try:
            async def read(item, response_hook, **kwargs):
                await Adapter()._ensure_driver_handle()
                result = await native.read_item_async(item)
                response_hook({"x-ms-activity-id": str(item)}, None)
                return result
            return await asyncio.gather(*(
                utils._fixed_rate_call_async("ReadItem", stats, time.perf_counter_ns(), read, item)
                for item in range(4)))
        finally:
            await trace.stop()

    assert asyncio.run(run()) == [0, 1, 2, 3]
    assert len(trace.calls) == 4
    for row in trace.calls:
        assert row["headers"]["x-ms-activity-id"] == str(row["call"] - 1)
        for name in ("ensure_driver", "binding_submit", "binding_await", "response_hook"):
            start, end = row["stages"][name]
            assert row["sdk_start_ns"] <= start <= end <= row["sdk_end_ns"]
    assert Adapter._ensure_driver_handle is original_ensure
    assert native.read_item_async is binding
    assert utils._wait_for_launch_slot is original_wait
    assert trace._gc_callback not in trace_module.gc.callbacks
