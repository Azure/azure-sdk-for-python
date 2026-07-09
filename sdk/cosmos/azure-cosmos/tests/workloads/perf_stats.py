# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Thread-safe per-operation latency histogram and error tracking using HdrHistogram."""

import threading
import time
from collections import deque

try:
    from hdrh.histogram import HdrHistogram
except ImportError:
    raise ImportError(
        "hdrhistogram is required for perf_stats. "
        "Install it with: pip install hdrhistogram (module name: hdrh)"
    )


_MIN_VALUE_US = 1
_MAX_VALUE_US = 60_000_000
# Number of earliest per-op durations kept for cold-start analysis. Small: only the
# first calls after process start matter for startup penalty.
_FIRST_N_CAP = 200


class Stats:
    """Thread-safe per-operation latency and error tracking using HdrHistogram.

    Uses HdrHistogram for O(1) record/query with fixed ~40KB memory per histogram,
    replacing the previous sorted-list approach that grew unbounded.
    Values are stored in microseconds internally for sub-ms precision.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # min 1 microsecond, max 60 seconds (in microseconds), 3 significant digits
        self._histograms: dict[str, HdrHistogram] = {}
        # Histogram of server-reported processing time (the
        # x-ms-request-duration-ms response header) for the same ops. The client
        # histogram above measures wall clock at the caller (network + transport +
        # binding + service); this one measures only the service's own time.
        # Client minus server shows where a tail is spent: a high client tail with
        # a normal server tail is client-side cost, not the service. Both backends
        # set the header, so the split is comparable across them.
        self._server_histograms: dict[str, HdrHistogram] = {}
        self._error_counts: dict[str, int] = {}
        # Running RU charge per operation: sum and sample count, so drain can
        # report mean RU per op. Fed by record_ru from the SDK response_hook
        # (x-ms-request-charge).
        self._ru_sums: dict[str, float] = {}
        self._ru_counts: dict[str, int] = {}
        # Bounded from the start so a burst of errors before the first drain
        # cannot grow this without limit. drain_all resets it to the same limit.
        self._errors: deque = deque(maxlen=2000)
        # Worst event-loop scheduling delay seen this interval, in milliseconds.
        # Fed by the async loop-lag monitor and drained per flush. It is process-
        # wide, not per operation, so it lives outside the per-op histograms. A
        # large value means the loop is the bottleneck, not the SDK.
        self._loop_lag_max_ms: float = 0.0
        # Earliest per-op durations (ms) since process start, capped at _FIRST_N_CAP.
        # Unlike the histograms, this is NOT reset on drain, so a cold-start analyzer
        # can see the very first calls (startup penalty) even after warm windows have
        # flushed. Reported once, on the final row, via first_ms_snapshot().
        self._first_ms: dict[str, list] = {}

    def first_ms_snapshot(self):
        """Return a copy of the earliest-N durations (ms) per op since process start.

        Used by the reporter to emit a cold-start sample (first call and warm-up
        curve) that survives the per-window histogram resets.
        """
        with self._lock:
            return {op: list(vals) for op, vals in self._first_ms.items()}

    def record(self, operation: str, duration_ms: float):
        """Record a successful operation with its duration in milliseconds."""
        with self._lock:
            if operation not in self._histograms:
                self._histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
                self._error_counts[operation] = 0
            # Clamp to histogram range to prevent crashes on very slow operations
            value_us = max(_MIN_VALUE_US, min(int(duration_ms * 1000), _MAX_VALUE_US))
            self._histograms[operation].record_value(value_us)
            first = self._first_ms.get(operation)
            if first is None:
                first = self._first_ms[operation] = []
            if len(first) < _FIRST_N_CAP:
                first.append(duration_ms)

    def record_server_ms(self, operation: str, server_ms: float):
        """Record the service-reported processing time of a successful operation.

        Fed from the SDK ``response_hook`` (the ``x-ms-request-duration-ms``
        header), which both backends set. Stored in a separate histogram from the
        client latency, so an analyzer can compare the server tail against the
        client tail: a high client tail with a normal server tail is client-side
        cost, not the service.
        """
        if server_ms < 0:
            return
        with self._lock:
            if operation not in self._server_histograms:
                self._server_histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
            value_us = max(_MIN_VALUE_US, min(int(server_ms * 1000), _MAX_VALUE_US))
            self._server_histograms[operation].record_value(value_us)

    def record_ru(self, operation: str, request_charge: float):
        """Record the RU charge of a successful operation.

        Kept as a running sum and count so drain_all can report the mean RU per
        operation. Fed from the SDK ``response_hook`` (the ``x-ms-request-charge``
        header), which fires once per successful op on both backends.
        """
        with self._lock:
            if operation not in self._ru_sums:
                self._ru_sums[operation] = 0.0
                self._ru_counts[operation] = 0
            self._ru_sums[operation] += request_charge
            self._ru_counts[operation] += 1

    def record_loop_lag(self, lag_ms: float):
        """Record one event-loop scheduling-delay sample (milliseconds).

        Keeps only the worst sample of the interval -- a single bad stall is what
        flags loop saturation, and an average would hide it. Drained and reset
        by ``drain_loop_lag`` each flush.
        """
        with self._lock:
            if lag_ms > self._loop_lag_max_ms:
                self._loop_lag_max_ms = lag_ms

    def drain_loop_lag(self) -> float:
        """Return the worst loop-lag (ms) since the last call, then reset to 0."""
        with self._lock:
            value = self._loop_lag_max_ms
            self._loop_lag_max_ms = 0.0
            return value

    def record_error(
        self,
        operation: str,
        error_msg: str,
        traceback_str: str,
        status_code: int = None,
        sub_status_code: int = None,
    ):
        """Record a failed operation with error details."""
        with self._lock:
            if operation not in self._error_counts:
                self._error_counts[operation] = 0
                self._histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
            self._error_counts[operation] += 1
            self._errors.append(
                {
                    "operation": operation,
                    "error_message": error_msg,
                    "source_message": traceback_str,
                    "error_status_code": status_code,
                    "error_sub_status_code": sub_status_code,
                    "timestamp": time.time(),
                }
            )

    def drain_all(self) -> tuple[list[dict], list[dict]]:
        """Atomically drain both summaries and error details under one lock.

        Returns (summaries, errors) where summaries is a list of dicts with:
        operation, count, errors, min_ms, max_ms, mean_ms, p50_ms, p90_ms, p99_ms,
        p99_9_ms, hist_b64, mean_ru, ru_sum, ru_count
        and errors is a list of dicts with: operation, error_message, source_message,
        error_status_code, error_sub_status_code, timestamp.

        ``hist_b64`` is the base64-encoded full HdrHistogram for the window (None when
        the op only had errors). It exists so an offline analyzer can MERGE every
        window of a point for a TRUE pooled tail, which per-window scalar percentiles
        cannot give.
        """
        with self._lock:
            summaries: list[dict] = []
            all_ops = set(
                list(self._histograms.keys())
                + list(self._error_counts.keys())
                + list(self._ru_sums.keys())
            )
            for op in sorted(all_ops):
                hist = self._histograms.get(op)
                errors = self._error_counts.get(op, 0)
                count = hist.total_count if hist else 0
                # Mean RU per successful op. 0.0 when no RU samples were recorded
                # this interval. ru_sum / ru_count are also emitted raw so a
                # cross-window average can be count-weighted.
                ru_count = self._ru_counts.get(op, 0)
                ru_sum = self._ru_sums.get(op, 0.0)
                mean_ru = (ru_sum / ru_count) if ru_count else 0.0
                # Server-reported processing time for this op this window. Emitted
                # as pooled-able base64 plus scalar tail so the offline analyzer
                # can compare the SERVER tail against the CLIENT tail per point.
                shist = self._server_histograms.get(op)
                if shist and shist.total_count > 0:
                    server_count = shist.total_count
                    server_p50_ms = shist.get_value_at_percentile(50.0) / 1000.0
                    server_p99_ms = shist.get_value_at_percentile(99.0) / 1000.0
                    server_p99_9_ms = shist.get_value_at_percentile(99.9) / 1000.0
                    server_hist_b64 = shist.encode().decode("ascii")
                else:
                    server_count = 0
                    server_p50_ms = server_p99_ms = server_p99_9_ms = 0.0
                    server_hist_b64 = None
                if count == 0 and errors == 0:
                    continue
                if count > 0:
                    summaries.append(
                        {
                            "operation": op,
                            "count": count,
                            "errors": errors,
                            "min_ms": hist.min_value / 1000.0,
                            "max_ms": hist.max_value / 1000.0,
                            "mean_ms": hist.get_mean_value() / 1000.0,
                            "p50_ms": hist.get_value_at_percentile(50.0) / 1000.0,
                            "p90_ms": hist.get_value_at_percentile(90.0) / 1000.0,
                            "p99_ms": hist.get_value_at_percentile(99.0) / 1000.0,
                            # p99.9 captures the slow tail, where the move to
                            # the Rust backend tends to show its cost first.
                            "p99_9_ms": hist.get_value_at_percentile(99.9) / 1000.0,
                            # Base64 of this window's full HdrHistogram, captured
                            # before the per-window reset below. Per-window scalar
                            # percentiles cannot be pooled across windows, so storing
                            # the histogram lets an offline analyzer merge windows
                            # into a true pooled p50/p99/p99.9 for the whole point.
                            "hist_b64": hist.encode().decode("ascii"),
                            # Mean RU per op; ru_sum / ru_count let the aggregate be
                            # count-weighted.
                            "mean_ru": mean_ru,
                            "ru_sum": ru_sum,
                            "ru_count": ru_count,
                            "server_count": server_count,
                            "server_p50_ms": server_p50_ms,
                            "server_p99_ms": server_p99_ms,
                            "server_p99_9_ms": server_p99_9_ms,
                            "server_hist_b64": server_hist_b64,
                        }
                    )
                else:
                    # count == 0 but errors > 0: every call failed, so there is no
                    # latency. The row is still emitted to surface the errors, with
                    # 0.0 placeholders for the latency fields. These are not fast
                    # results: a pass/fail check must require count > 0 before
                    # reading latency, or a fully failed op would read as p99 = 0.
                    summaries.append(
                        {
                            "operation": op,
                            "count": 0,
                            "errors": errors,
                            "min_ms": 0.0,
                            "max_ms": 0.0,
                            "mean_ms": 0.0,
                            "p50_ms": 0.0,
                            "p90_ms": 0.0,
                            "p99_ms": 0.0,
                            "p99_9_ms": 0.0,
                            # No latency samples (all calls failed), so no histogram.
                            "hist_b64": None,
                            "mean_ru": mean_ru,
                            "ru_sum": ru_sum,
                            "ru_count": ru_count,
                            "server_count": server_count,
                            "server_p50_ms": server_p50_ms,
                            "server_p99_ms": server_p99_ms,
                            "server_p99_9_ms": server_p99_9_ms,
                            "server_hist_b64": server_hist_b64,
                        }
                    )
            # Reset for next interval
            self._histograms.clear()
            self._server_histograms.clear()
            self._error_counts.clear()
            self._ru_sums.clear()
            self._ru_counts.clear()
            # Copy into a list so the caller gets a stable copy and the return
            # type matches the annotation, not the internal deque.
            error_details: list[dict] = list(self._errors)
            self._errors = deque(maxlen=2000)
            return summaries, error_details

    def drain_summaries(self) -> list[dict]:
        """Drain accumulated stats and return per-operation summaries."""
        summaries, _ = self.drain_all()
        return summaries

    def drain_errors(self) -> list[dict]:
        """Drain accumulated error details."""
        _, errors = self.drain_all()
        return errors
