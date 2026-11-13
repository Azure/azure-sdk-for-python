# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline Python side of the isolated Rust-to-asyncio handoff experiment."""

import asyncio
import contextvars
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time
from native_experiment_metrics import python_source_json

TAG = "_offline_handoff_slot"


def distribution(values):
    ordered = sorted(values)
    return {
        "p50_ns": statistics.median(ordered),
        "p99_ns": ordered[math.ceil(0.99 * len(ordered)) - 1],
        "max_ns": ordered[-1],
    }


class DeliveryObserver:
    def __init__(self, native, loop):
        self.native = native
        self.loop = loop
        self.original = loop.call_soon_threadsafe
        self.records = [[0, 0, 0, 0] for _ in range(25000)]

    def install(self):
        def enqueue(hook, *args, **kwargs):
            slot = getattr(args[0], TAG, None) if args else None
            if slot is None:
                # Only this experiment submits Rust completions to its loop.
                # Unknown schedules remain functional and fail coverage if relevant.
                return self.original(hook, *args, **kwargs)
            record = self.records[slot]
            record[0] = self.native.clock()
            record[3] += 1

            def complete(*values):
                record[1] = self.native.clock()
                try:
                    return hook(*values)
                finally:
                    record[2] = self.native.clock()

            return self.original(complete, *args, **kwargs)

        self.loop.call_soon_threadsafe = enqueue

    def remove(self):
        self.loop.call_soon_threadsafe = self.original

    def tag(self, future, slot):
        setattr(future, TAG, slot)
        return future

    def timestamps(self, slot, resumed):
        native = self.native.row(slot)
        delivery = self.records[slot]
        assert delivery[3] == 1, (slot, "completion enqueue count", delivery)
        values = native + delivery[:3] + [resumed]
        assert all(value > 0 for value in values), (slot, "missing boundary", values)
        assert values == sorted(values), (slot, "unordered boundaries", values)
        return values


async def error_and_cancellation_fixture(native, observer):
    errors = []
    for mode in (False, True):
        slot = 24002 + int(mode)
        (error,) = await asyncio.gather(observer.tag(native.submit(slot, mode, True, 0), slot), return_exceptions=True)
        assert isinstance(error, Exception), "Native error became success"
        assert "offline handoff failure" in str(error), repr(error)
        errors.append((type(error), str(error)))
        cancelled = native.submit(24004 + int(mode), mode, False, 100)
        cancelled.cancel()
        try:
            await cancelled
        except asyncio.CancelledError:
            pass
        else:
            raise AssertionError("Cancellation became success")
    await asyncio.sleep(0.15)
    assert errors[0] == errors[1]
    assert native.row(24005)[0] == 0, "Cancelled native operation completed"


async def fixtures(native, observer):
    baseline = await native.submit(24000, False, False, 0)
    observed = await observer.tag(native.submit(24001, True, False, 0), 24001)
    assert baseline == observed
    observer.timestamps(24001, native.clock())
    assert json.loads(baseline[3])["id"] == "order-17"
    await error_and_cancellation_fixture(native, observer)

    marker = contextvars.ContextVar("handoff_test_context", default="wrong")
    context = contextvars.copy_context()
    context.run(marker.set, "preserved")
    completed = asyncio.get_running_loop().create_future()
    observer.tag(completed, 24006)

    def check_context(future):
        assert marker.get() == "preserved"
        future.set_result(True)

    handle = asyncio.get_running_loop().call_soon_threadsafe(check_context, completed, context=context)
    assert hasattr(handle, "cancel")
    assert await completed

    # Release the GIL but block the event-loop thread: enqueue can proceed.
    slot = 24007
    pending = observer.tag(native.submit(slot, True, False, 5), slot)
    time.sleep(0.06)
    await pending
    queue = observer.timestamps(slot, native.clock())
    assert queue[6] - queue[5] >= 10_000_000, queue

    # Let bridge setup run before holding the GIL across native completion.
    slot = 24008
    pending = observer.tag(native.submit(slot, True, False, 50), slot)
    await asyncio.sleep(0.01)
    previous = sys.getswitchinterval()
    try:
        sys.setswitchinterval(0.2)
        until = time.perf_counter() + 0.1
        while time.perf_counter() < until:
            pass
    finally:
        sys.setswitchinterval(previous)
    await pending
    gil = observer.timestamps(slot, native.clock())
    assert gil[3] - gil[2] >= 10_000_000, gil
    return {
        "tuple_parity": True,
        "error_and_cancellation_preserved": True,
        "explicit_context_preserved": True,
        "delayed_queue_ns": queue[6] - queue[5],
        "delayed_gil_ns": gil[3] - gil[2],
    }, baseline


def phase_distributions(observer, resumed_times):
    names = [
        "native_done_to_join_observed",
        "join_processing",
        "conversion_gil_wait",
        "response_conversion",
        "conversion_end_to_enqueue",
        "enqueue_entry_to_completion_hook",
        "completion_hook",
        "hook_end_to_application_resume",
    ]
    columns = [[] for _ in names]
    trace = []
    for index, resumed in enumerate(resumed_times):
        values = observer.timestamps(index, resumed)
        deltas = [end - begin for begin, end in zip(values, values[1:])]
        assert sum(deltas) == values[-1] - values[0]
        trace.append(values)
        for column, delta in zip(columns, deltas):
            column.append(delta)
    stages = {name: distribution(column) for name, column in zip(names, columns)}
    stages["native_done_to_application_resume"] = distribution([row[-1] - row[0] for row in trace])
    return stages, trace


async def measure(native, python_runtime):
    mode = os.environ["HANDOFF_MODE"]
    assert mode in ("control", "observed", "allocations", "conversion", "idle")
    count = int(os.environ["HANDOFF_ITERATIONS"])
    assert 1000 <= count <= 20000
    loop = asyncio.get_running_loop()
    observer = DeliveryObserver(native, loop)
    observer.install()
    qualification, expected = await fixtures(native, observer)
    observer.remove()
    observed = mode == "observed"
    if observed:
        observer.install()
    # Warm up both result paths outside the measured population.
    for index in range(512):
        if mode == "conversion":
            result = native.convert_one()
        else:
            result = await observer.tag(native.submit(24500, observed, False, 0), 24500)
        assert result == expected
    await asyncio.sleep(0.05)
    durations = [0] * count
    resumed_times = [0] * count
    allocations_start = native.allocation_counts(mode in ("allocations", "conversion", "idle"))
    assert allocations_start[0] == (mode in ("allocations", "conversion", "idle"))
    cpu_start = time.process_time_ns()
    wall_start = time.perf_counter_ns()
    if mode == "idle":
        await asyncio.sleep(float(os.environ.get("HANDOFF_IDLE_SECONDS", "1")))
    else:
        for index in range(count):
            begin = native.clock()
            if mode == "conversion":
                result = native.convert_one()
            else:
                future = native.submit(index, observed, False, 0)
                if observed:
                    observer.tag(future, index)
                result = await future
            resumed = native.clock()
            durations[index] = resumed - begin
            resumed_times[index] = resumed
            assert result == expected
    wall_ns = time.perf_counter_ns() - wall_start
    cpu_ns = time.process_time_ns() - cpu_start
    # Count delayed Rust task cleanup too; elapsed/CPU measurements end above.
    await asyncio.sleep(0.05)
    allocations_end = native.allocation_counts(False)
    assert allocations_start[0] == allocations_end[0]
    allocation_delta = [end - begin for begin, end in zip(allocations_start[1:], allocations_end[1:])]
    stages, trace = phase_distributions(observer, resumed_times) if observed else ({}, [])
    observer.remove()
    result = {
        "mode": mode,
        "iterations": 0 if mode == "idle" else count,
        "wall_ns": wall_ns,
        "process_cpu_ns": cpu_ns,
        "event_loop": type(loop).__name__,
        "python_runtime": python_runtime,
        "qualification": qualification,
        "cpu_ns_per_operation": None if mode == "idle" else cpu_ns / count,
        "submit_to_resume": None if mode == "idle" else distribution(durations),
        "stages": stages,
        "rust_allocation_delta": dict(
            zip(("allocations", "requested_bytes", "deallocations", "reallocations"), allocation_delta)
        ),
        "body_bytes": len(expected[3]),
        "header_count": len(expected[2]),
        "scope": (
            "Cached native response conversion only, no async bridge"
            if mode == "conversion"
            else (
                "Cached native read response through real binding runner/PyO3/asyncio; "
                "no service work or public Python API"
            )
        ),
        "clock": "All operation markers use one Rust Instant clock",
    }
    write_result(result, trace, durations)


def write_result(result, trace, durations):
    destination = Path(os.environ["HANDOFF_OUTPUT"])
    with destination.open("x", encoding="utf-8") as output:
        json.dump({"summary": result, "trace": trace, "submit_to_resume_ns": durations}, output)
    print("HANDOFF_RESULT=" + json.dumps(result), flush=True)


def run(native):
    asyncio.run(measure(native, json.loads(python_source_json())))
