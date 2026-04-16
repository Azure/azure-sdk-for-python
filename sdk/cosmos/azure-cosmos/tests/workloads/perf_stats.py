from collections import deque
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Thread-safe per-operation latency histogram and error tracking using HdrHistogram."""

import threading
import time

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
        self._errors: list[dict] = []

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
        operation, count, errors, min_ms, max_ms, mean_ms, p50_ms, p90_ms, p99_ms
        and errors is a list of dicts with: operation, error_message, source_message,
        error_status_code, error_sub_status_code, timestamp.
        """
        with self._lock:
            summaries = []
            all_ops = set(
                list(self._histograms.keys()) + list(self._error_counts.keys())
            )
            for op in sorted(all_ops):
                hist = self._histograms.get(op)
                errors = self._error_counts.get(op, 0)
                count = hist.total_count if hist else 0
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
                        }
                    )
                else:
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
                        }
                    )
            # Reset for next interval
            self._histograms.clear()
            self._error_counts.clear()
            error_details = self._errors
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
