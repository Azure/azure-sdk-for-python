# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Thread-safe per-operation latency histogram and error tracking using HdrHistogram."""

import threading
import time
import math
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
    """Lock-protected, per-operation success histograms and error tracking.

    Durations are quantized in microseconds and clamped to the configured range.
    Each distinct operation allocates its own histograms; storage and percentile
    lookup costs are not established by this module's tests.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # min 1 microsecond, max 60 seconds (in microseconds), 3 significant digits
        self._histograms: dict[str, HdrHistogram] = {}
        # Header-derived durations are sampled separately from client durations.
        # Missing headers and multiple requests per call can make the populations
        # differ. Independent percentiles cannot be subtracted to isolate overhead.
        self._server_histograms: dict[str, HdrHistogram] = {}
        self._error_counts: dict[str, int] = {}
        self._throttled: dict[str, int] = {}
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
        # wide, not per operation, so it lives outside the per-op histograms.
        # A large sample records a scheduling delay, not its cause.
        self._loop_lag_max_ms: float = 0.0
        # Earliest per-op durations (ms) since process start, capped at _FIRST_N_CAP.
        # Unlike the histograms, this is NOT reset on drain, so a cold-start analyzer
        # can see the very first calls (startup penalty) even after warm windows have
        # flushed. The reporter repeats these snapshots on result rows.
        self._first_ms: dict[str, list] = {}
        self._timings: dict[tuple[str, str], dict] = {}
        self._latency_overflows: dict[str, int] = {}
        self._fixed_rate_schedules: list[dict] = []

    def record_schedule(self, schedule: dict):
        """Keep one completed scheduling interval per client, not per result row."""
        with self._lock:
            self._fixed_rate_schedules.append(dict(schedule))

    def schedule_snapshot(self) -> list[dict]:
        with self._lock:
            return [dict(schedule) for schedule in self._fixed_rate_schedules]

    @staticmethod
    def _validate_timing(delay_before_call_ms, sdk_call_ms):
        if delay_before_call_ms is None and sdk_call_ms is None:
            return
        if any(value is None or not math.isfinite(value) or value < 0
               for value in (delay_before_call_ms, sdk_call_ms)):
            raise ValueError("Both timing components must be finite and nonnegative")

    def _record_timing(self, operation, outcome, delay_before_call_ms, sdk_call_ms):
        # Called under the same lock as the corresponding success/error count.
        if delay_before_call_ms is None:
            return
        key = (operation, outcome)
        if key not in self._timings:
            self._timings[key] = {
                name: {"hist": HdrHistogram(_MIN_VALUE_US, _MAX_VALUE_US, 3),
                       "overflow_count": 0, "max_observed_ms": 0.0}
                for name in ("delay_before_call", "sdk_call", "total")
            }
        for name, value in (
            ("delay_before_call", delay_before_call_ms),
            ("sdk_call", sdk_call_ms),
            ("total", delay_before_call_ms + sdk_call_ms),
        ):
            series = self._timings[key][name]
            series["hist"].record_value(max(_MIN_VALUE_US, min(int(value * 1000), _MAX_VALUE_US)))
            series["overflow_count"] += int(value > _MAX_VALUE_US / 1000)
            series["max_observed_ms"] = max(series["max_observed_ms"], value)

    def first_ms_snapshot(self):
        """Return a copy of the earliest-N durations (ms) per op since process start.

        Used by the reporter to emit a cold-start sample (first call and warm-up
        curve) that survives the per-window histogram resets.
        """
        with self._lock:
            return {op: list(vals) for op, vals in self._first_ms.items()}

    def record(self, operation: str, duration_ms: float, *,
               delay_before_call_ms=None, sdk_call_ms=None):
        """Record a successful operation with its duration in milliseconds."""
        if not math.isfinite(duration_ms) or duration_ms < 0:
            raise ValueError("Duration must be finite and nonnegative")
        self._validate_timing(delay_before_call_ms, sdk_call_ms)
        if delay_before_call_ms is not None and not math.isclose(
                duration_ms, delay_before_call_ms + sdk_call_ms, rel_tol=1e-9, abs_tol=1e-6):
            raise ValueError("Total duration must equal delay before call plus SDK-call duration")
        with self._lock:
            if operation not in self._histograms:
                self._histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
                self._error_counts[operation] = 0
            # Clamp to histogram range to prevent crashes on very slow operations
            value_us = max(_MIN_VALUE_US, min(int(duration_ms * 1000), _MAX_VALUE_US))
            self._histograms[operation].record_value(value_us)
            self._latency_overflows[operation] = self._latency_overflows.get(operation, 0) + int(
                duration_ms > _MAX_VALUE_US / 1000)
            self._record_timing(operation, "success", delay_before_call_ms, sdk_call_ms)
            first = self._first_ms.get(operation)
            if first is None:
                first = self._first_ms[operation] = []
            if len(first) < _FIRST_N_CAP:
                first.append(duration_ms)

    def record_server_ms(self, operation: str, server_ms: float):
        """Record a supplied nonnegative request-duration header value.

        Header samples are kept separately from client durations and may cover a
        different population. Their percentiles cannot identify per-call overhead
        by subtraction or establish which layer caused a latency tail.
        """
        if not math.isfinite(server_ms) or server_ms < 0:
            raise ValueError("Header duration must be finite and nonnegative")
        with self._lock:
            if operation not in self._server_histograms:
                self._server_histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
            value_us = max(_MIN_VALUE_US, min(int(server_ms * 1000), _MAX_VALUE_US))
            self._server_histograms[operation].record_value(value_us)

    def record_ru(self, operation: str, request_charge: float):
        """Accumulate a supplied nonnegative RU value and its sample count.

        The caller determines which response/header is sampled. This method does
        not check one sample per operation or complete retry/request accounting.
        """
        if not math.isfinite(request_charge) or request_charge < 0:
            raise ValueError("Request charge must be finite and nonnegative")
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
        *,
        delay_before_call_ms=None,
        sdk_call_ms=None,
    ):
        """Record a failed operation with error details."""
        self._validate_timing(delay_before_call_ms, sdk_call_ms)
        with self._lock:
            if operation not in self._error_counts:
                self._error_counts[operation] = 0
                self._histograms[operation] = HdrHistogram(
                    _MIN_VALUE_US, _MAX_VALUE_US, 3
                )
            self._error_counts[operation] += 1
            self._record_timing(operation, "failure", delay_before_call_ms, sdk_call_ms)
            if status_code == 429:
                self._throttled[operation] = self._throttled.get(operation, 0) + 1
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
        """Detach one window atomically, then summarize it outside the recording lock.

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
            # Recorders must receive new containers, not clear the detached window.
            histograms, self._histograms = self._histograms, {}
            server_histograms, self._server_histograms = self._server_histograms, {}
            error_counts, self._error_counts = self._error_counts, {}
            throttled, self._throttled = self._throttled, {}
            ru_sums, self._ru_sums = self._ru_sums, {}
            ru_counts, self._ru_counts = self._ru_counts, {}
            timings, self._timings = self._timings, {}
            latency_overflows, self._latency_overflows = self._latency_overflows, {}
            error_details, self._errors = self._errors, deque(maxlen=2000)
            first_ms = {op: values[:50] for op, values in self._first_ms.items()}

        summaries: list[dict] = []
        all_ops = set(list(histograms.keys()) + list(error_counts.keys()) + list(ru_sums.keys()))
        for op in sorted(all_ops):
            hist = histograms.get(op)
            errors = error_counts.get(op, 0)
            count = hist.total_count if hist else 0
            # RU samples and successful calls can belong to different populations.
            ru_count = ru_counts.get(op, 0)
            ru_sum = ru_sums.get(op, 0.0)
            mean_ru = (ru_sum / ru_count) if ru_count else 0.0
            shist = server_histograms.get(op)
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
                        "p99_9_ms": hist.get_value_at_percentile(99.9) / 1000.0,
                        # Preserve full histograms for pooled cross-window percentiles.
                        "hist_b64": hist.encode().decode("ascii"),
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
                # All-error windows have no successful latency; zero is a placeholder.
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
        for summary in summaries:
            op = summary["operation"]
            summary["throttled_429"] = throttled.get(op, 0)
            summary["cold_first_n_ms"] = first_ms.get(op, [])
            summary["latency_overflow_count"] = latency_overflows.get(op, 0)
            summary["fixed_rate_timings"] = {}
            for outcome in ("success", "failure"):
                series = timings.get((op, outcome))
                if series is not None:
                    summary["fixed_rate_timings"][outcome] = {
                        name: {
                            "count": value["hist"].total_count,
                            "hist_b64": value["hist"].encode().decode("ascii"),
                            "overflow_count": value["overflow_count"],
                            "max_observed_ms": value["max_observed_ms"],
                        }
                        for name, value in series.items()
                    }
        return summaries, list(error_details)

    def drain_summaries(self) -> list[dict]:
        """Drain accumulated stats and return per-operation summaries."""
        summaries, _ = self.drain_all()
        return summaries

    def drain_errors(self) -> list[dict]:
        """Drain accumulated error details."""
        _, errors = self.drain_all()
        return errors
