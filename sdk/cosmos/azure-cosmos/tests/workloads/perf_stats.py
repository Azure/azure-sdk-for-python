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
        self._error_counts: dict[str, int] = {}
        # Running RU (request-unit) charge per operation: sum and sample count,
        # so drain can report mean RU per op. Fed by record_ru from the SDK
        # response_hook (x-ms-request-charge). This is the data source for the
        # "same work" RU-parity check; the workload log cannot provide it (it
        # keeps only errors and slow calls).
        self._ru_sums: dict[str, float] = {}
        self._ru_counts: dict[str, int] = {}
        # Bounded from the start so a burst of errors before the first drain
        # cannot grow this without limit. drain_all resets it to the same limit.
        self._errors: deque = deque(maxlen=2000)
        # Worst event-loop scheduling delay seen this interval, in milliseconds.
        # Fed by the async loop-lag monitor (workload_utils._loop_lag_monitor) and
        # drained per flush. It is process-wide (not per operation), so it lives
        # outside the per-op histograms. A large value means the single asyncio
        # event-loop thread could not service timers on time -- the loop itself
        # (GIL-bound Python) is the bottleneck, not the SDK or the service. See
        # docs/RUST_PYTHON_SLA.md, "Is the event loop the bottleneck?".
        self._loop_lag_max_ms: float = 0.0

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

    def record_ru(self, operation: str, request_charge: float):
        """Record the RU (request-unit) charge of a successful operation.

        Kept as a running sum + count so drain_all can report the mean RU per
        operation (``mean_ru``) -- the data source for the doc's "same work"
        RU-parity check. Fed from the SDK ``response_hook`` (the
        ``x-ms-request-charge`` header), which fires once per successful op on
        both backends.
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
        flags loop saturation, and an average would wash it out. Drained and reset
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
        p99_9_ms, mean_ru, ru_sum, ru_count
        and errors is a list of dicts with: operation, error_message, source_message,
        error_status_code, error_sub_status_code, timestamp.
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
                # Mean RU per successful op (x-ms-request-charge). 0.0 when no
                # RU samples were recorded for this op in the interval. ru_sum /
                # ru_count are also emitted raw so a cross-window aggregate can be
                # COUNT-WEIGHTED — SUM(ru_sum)/SUM(ru_count) — rather than an
                # unweighted average of per-window means (matches the CPU check's
                # SUM(cpu_seconds)/SUM(count) shape).
                ru_count = self._ru_counts.get(op, 0)
                ru_sum = self._ru_sums.get(op, 0.0)
                mean_ru = (ru_sum / ru_count) if ru_count else 0.0
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
                            # Mean RU per op: the "same work" / RU-parity gate.
                            # ru_sum / ru_count let the aggregate be count-weighted.
                            "mean_ru": mean_ru,
                            "ru_sum": ru_sum,
                            "ru_count": ru_count,
                        }
                    )
                else:
                    # count == 0 but errors > 0: every call of this operation
                    # failed, so there is no latency to report. The row is still
                    # emitted to surface the errors, with 0.0 *placeholders* for
                    # every latency field. These 0.0s are NOT fast results: any
                    # pass/fail gate must guard latency with the precondition
                    # count > 0 (and count ≈ baseline, errors ≈ 0), or a fully
                    # failed op would read as p99 = 0 and falsely pass. See
                    # docs/RUST_PYTHON_SLA.md, "What counts as a pass" (check 0).
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
                            "mean_ru": mean_ru,
                            "ru_sum": ru_sum,
                            "ru_count": ru_count,
                        }
                    )
            # Reset for next interval
            self._histograms.clear()
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
