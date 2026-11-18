# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Opt-in, bounded diagnostic recording; not an uninstrumented latency baseline."""

import asyncio
from collections import Counter, deque
import contextvars
import datetime
import functools
import gc
import heapq
import json
from pathlib import Path
import threading
import time


class ReadTrace:
    HEADERS = (
        "x-ms-activity-id", "x-ms-request-charge", "x-ms-request-duration-ms",
        "x-ms-substatus", "x-ms-documentdb-partitionkeyrangeid",
        "x-ms-cosmos-sdk-diagnostics",
    )

    def __init__(self, backend, *, capacity=4096, top_count=20, slow_ms=10):
        if capacity < 1 or top_count < 1 or slow_ms <= 0:
            raise ValueError("Trace limits must be positive")
        self.backend = backend
        self.origin_ns = time.perf_counter_ns()
        self.origin_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.capacity = capacity
        self.top_count = top_count
        self.slow_ms = slow_ms
        self.calls = deque(maxlen=capacity)
        self.events = deque(maxlen=capacity)
        self.top = []
        self.active = {}
        self.counts = Counter()
        self.coverage = Counter()
        self.current = contextvars.ContextVar("profile_read", default=None)
        self._patches = []
        self._gc_starts = {}
        self._event_lock = threading.RLock()
        self._watcher = None
        self._started = False

    def begin(self, scheduled_ns, kwargs):
        self.counts["started"] += 1
        state = {
            "call": self.counts["started"], "scheduled_ns": scheduled_ns,
            "sdk_start_ns": None, "sdk_end_ns": None, "outcome": "cancelled",
            "headers": {}, "stages": {},
        }
        token = self.current.set(state)
        self.active[state["call"]] = state
        original = kwargs.get("response_hook")

        def hook(headers, body):
            begin = time.perf_counter_ns()
            try:
                if original is not None:
                    original(headers, body)
            finally:
                # Do not retain documents, credentials, or arbitrary headers.
                state["hook_count"] = state.get("hook_count", 0) + 1
                for name in self.HEADERS:
                    value = headers.get(name) if headers is not None else None
                    if value is not None:
                        text = str(value)
                        if len(text) > 8192:
                            state.setdefault("truncated_headers", []).append(name)
                        state["headers"][name] = text[:8192]
                state["stages"]["response_hook"] = [begin, time.perf_counter_ns()]

        kwargs["response_hook"] = hook
        return state, token

    def finish(self, state, token):
        try:
            self.counts["completed"] += 1
            self.counts[state["outcome"]] += 1
            for name in state["headers"]:
                self.coverage[name] += 1
            duration = (state["sdk_end_ns"] - state["sdk_start_ns"]) / 1_000_000
            state["sdk_call_ms"] = duration
            state["delay_before_call_ms"] = (state["sdk_start_ns"] - state["scheduled_ns"]) / 1_000_000
            candidate = (duration, state["call"], state)
            if len(self.top) < self.top_count:
                heapq.heappush(self.top, candidate)
            elif candidate[:2] > self.top[0][:2]:
                heapq.heapreplace(self.top, candidate)
            if duration >= self.slow_ms or state["delay_before_call_ms"] >= 8 or state["outcome"] != "success":
                self.counts["retention_candidates"] += 1
                if len(self.calls) == self.capacity:
                    self.counts["evicted_calls"] += 1
                self.calls.append(state)
        finally:
            self.active.pop(state["call"])
            self.current.reset(token)

    def event(self, label, begin, end, **fields):
        if end - begin < 1_000_000 and label != "slot_wait":
            return
        with self._event_lock:
            if len(self.events) == self.capacity:
                self.counts["evicted_events"] += 1
            self.events.append({"label": label, "start_ns": begin, "end_ns": end, **fields})

    def _patch(self, owner, name, replacement):
        self._patches.append((owner, name, getattr(owner, name)))
        setattr(owner, name, replacement)

    def _sync_span(self, owner, name):
        original = getattr(owner, name)

        @functools.wraps(original)
        def wrapped(*args, **kwargs):
            begin = time.perf_counter_ns()
            try:
                return original(*args, **kwargs)
            finally:
                end = time.perf_counter_ns()
                state = self.current.get()
                self.event(name, begin, end, call=state["call"] if state else None)
                if state is not None:
                    state["stages"][name] = [begin, end]

        self._patch(owner, name, wrapped)

    def install(self, stats, workload_utils, adapter_type=None, native=None):
        for name in ("record_ru", "record_server_ms", "drain_all"):
            self._sync_span(stats, name)
        original_wait = workload_utils._wait_for_launch_slot

        async def wait(slots, stop):
            begin = time.perf_counter_ns()
            occupied = list(self.active)
            try:
                return await original_wait(slots, stop)
            finally:
                self.event("slot_wait", begin, time.perf_counter_ns(), active_calls_at_start=occupied)

        self._patch(workload_utils, "_wait_for_launch_slot", wait)
        if adapter_type is not None:
            original_ensure = adapter_type._ensure_driver_handle

            async def ensure(adapter):
                begin = time.perf_counter_ns()
                try:
                    return await original_ensure(adapter)
                finally:
                    state = self.current.get()
                    if state is not None:
                        state["stages"]["ensure_driver"] = [begin, time.perf_counter_ns()]

            self._patch(adapter_type, "_ensure_driver_handle", ensure)
        if native is not None:
            original_binding = native.read_item_async

            def binding(*args, **kwargs):
                begin = time.perf_counter_ns()
                awaitable = original_binding(*args, **kwargs)
                submitted = time.perf_counter_ns()
                state = self.current.get()
                if state is not None:
                    state["stages"]["binding_submit"] = [begin, submitted]

                async def wait_binding():
                    try:
                        return await awaitable
                    finally:
                        if state is not None:
                            state["stages"]["binding_await"] = [submitted, time.perf_counter_ns()]

                return wait_binding()

            self._patch(native, "read_item_async", binding)

    def _gc_callback(self, phase, info):
        key = (threading.get_ident(), info["generation"])
        if phase == "start":
            self._gc_starts[key] = time.perf_counter_ns()
        elif phase == "stop":
            begin = self._gc_starts.pop(key, None)
            if begin is not None:
                self.event("gc", begin, time.perf_counter_ns(), generation=info["generation"])

    async def start(self):
        if self._started:
            raise RuntimeError("Trace already started")
        self._started = True
        gc.callbacks.append(self._gc_callback)

        async def watch():
            while True:
                planned = time.perf_counter_ns() + 10_000_000
                await asyncio.sleep(0.01)
                self.event("loop_lateness", planned, time.perf_counter_ns())

        self._watcher = asyncio.create_task(watch())

    async def stop(self):
        try:
            if self._watcher is not None:
                self._watcher.cancel()
                try:
                    await self._watcher
                except asyncio.CancelledError:
                    pass
        finally:
            if self._started:
                gc.callbacks.remove(self._gc_callback)
                self._started = False
            for owner, name, original in reversed(self._patches):
                setattr(owner, name, original)
            self._patches.clear()

    def save(self, path, *, measured_count, measured_errors):
        if self.active or self.counts["completed"] != measured_count + measured_errors:
            raise RuntimeError("Read trace does not cover the completed measurement population")
        if self.counts["error"] != measured_errors or self.counts["cancelled"]:
            raise RuntimeError("Read trace outcomes disagree with the measurement")
        payload = {
            "scope": "Instrumented diagnostic comparison, not an uninstrumented baseline",
            "backend": self.backend, "origin_ns": self.origin_ns, "origin_utc": self.origin_utc,
            "limits": {"calls": self.capacity, "events": self.capacity, "top": self.top_count,
                       "slow_ms": self.slow_ms, "header_chars": 8192, "loop_interval_ms": 10},
            "counts": dict(self.counts), "header_coverage": dict(self.coverage),
            "calls": list(self.calls), "top": [item[2] for item in sorted(self.top, reverse=True)],
            "events": list(self.events),
        }
        with Path(path).open("x", encoding="utf-8") as stream:
            json.dump(payload, stream)
