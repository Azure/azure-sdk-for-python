# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Background reporter that drains Stats and upserts PerfResult documents to Cosmos DB."""

import logging
import os
import socket
import threading
import time
import uuid
import gc
from datetime import datetime, timezone

import psutil
from azure.cosmos import CosmosClient
from azure.cosmos._backend.constants import BACKEND_NAME_CORE_PYTHON
from azure.identity import DefaultAzureCredential

from perf_config import _safe_int_env
from perf_stats import Stats
import perf_backend_counters as backend_counters

try:
    from azure.cosmos import __version__ as _AZURE_COSMOS_VERSION
except Exception:
    _AZURE_COSMOS_VERSION = "unknown"

logger = logging.getLogger(__name__)


def _get_sdk_version() -> str:
    """Return the azure-cosmos SDK version string."""
    return _AZURE_COSMOS_VERSION


def _get_cpu_percent(process) -> float:
    """Get current process CPU percent."""
    return process.cpu_percent(interval=None)


def _get_cpu_times(process) -> tuple:
    """Read cumulative process user/system CPU times.

    Differences are measurements at the underlying counter's resolution, not
    exact attribution to a particular operation or backend.
    """
    t = process.cpu_times()
    return float(t.user), float(t.system)


def _get_gc_stats() -> tuple:
    """Read cumulative Python GC counters.

    Correlation with latency is a diagnostic clue, not proof of causation or
    that the SDK is uninvolved.
    """
    stats = gc.get_stats()
    return tuple(sum(g[name] for g in stats) for name in ("collections", "collected", "uncollectable"))


def _get_memory_bytes(process) -> int:
    """Get current process RSS in bytes."""
    return process.memory_info().rss


def _get_thread_count(process) -> int:
    """Read the process's OS thread count.

    This includes all process threads, not only driver-owned threads.
    """
    return process.num_threads()


def _get_system_cpu_percent() -> float:
    """Get system-wide CPU percent."""
    return psutil.cpu_percent(interval=None)


def _get_system_memory() -> tuple:
    """Get system total and used memory in bytes."""
    mem = psutil.virtual_memory()
    return mem.total, mem.used


class PerfReporter:
    """Drain shared stats and write result documents from a daemon thread.

    Reporting failures are logged where caught, but drained data is not
    guaranteed durable. Locks, sampling, encoding, and writes can affect the
    workload; isolation and zero measurement overhead are not guaranteed.
    """

    def __init__(self, stats: Stats, config: dict):
        self._stats = stats
        self._config = config
        self._stop_event = threading.Event()
        self._thread = None
        self._flush_lock = threading.Lock()
        self._client = None
        self._container = None
        self._failure = None
        self._process_id = str(uuid.uuid4())
        self._window_index = 0
        self._summary_count = 0
        self._total_count = 0
        self._total_errors = 0
        self._hostname = socket.gethostname()
        self._sdk_version = _get_sdk_version()
        self._process = psutil.Process()
        # Monotonic time of the last successful drain. Each row stores the actual
        # seconds it covers (window_seconds = now - this), so throughput is
        # count / window_seconds. If a flush is skipped the next drain covers a
        # longer window, which keeps req/s correct instead of too high.
        self._last_flush_monotonic = time.monotonic()
        # Reporter start (monotonic), for the elapsed_seconds each row carries so
        # warmup windows can be dropped later. Reset in _run after the CPU warmup
        # so elapsed starts at the first real window.
        self._start_monotonic = self._last_flush_monotonic
        # Baselines for the per-window CPU and GC deltas, primed in _run after
        # warmup and advanced on every flush. Initialised here so a flush that runs
        # before _run still has something to subtract.
        self._last_cpu_user, self._last_cpu_system = _get_cpu_times(self._process)
        self._last_gc_collections, self._last_gc_collected, self._last_gc_uncollectable = (
            _get_gc_stats()
        )
        # Backend-counter baselines, advanced like the CPU/GC baselines so each row
        # carries the per-window count of operations the Rust path handled
        # (rust_execute_calls) and that the Rust binding counted (binding_calls).
        # None for binding means the extension has no counter; we store -1 then.
        self._last_execute_calls = backend_counters.execute_count()
        self._last_binding_calls = backend_counters.binding_operation_count() or 0
        self._last_attempt_calls = backend_counters.binding_attempt_count() or 0
        self._last_retry_calls = backend_counters.binding_retry_count() or 0

    def start(self):
        """Start the background reporting thread (daemon)."""
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="perf-reporter"
        )
        self._thread.start()
        logger.info(
            "PerfReporter started (interval=%ds, workload_id=%s)",
            self._config["report_interval"],
            self._config["workload_id"],
        )

    def stop(self):
        """Stop the reporter and flush final results."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=30)
        # Final flush — only if background thread has stopped to avoid concurrent writes
        if self._thread and self._thread.is_alive():
            raise RuntimeError("PerfReporter thread still alive; final results are incomplete")
        else:
            try:
                with self._flush_lock:
                    self._ensure_container()
                    self._flush()
                    self._write_completion()
            except Exception as e:
                self._failure = e
                logger.warning("PerfReporter final flush failed: %s", e)
        if self._client:
            try:
                self._client.close()
            except Exception as exc:
                self._failure = exc
                logger.warning("PerfReporter client cleanup failed: %s", exc)
        if self._failure is not None:
            raise RuntimeError("PerfReporter failed; this run is incomplete") from self._failure
        logger.info("PerfReporter stopped")

    def _run(self):
        try:
            self._run_reporting()
        except Exception as exc:
            self._failure = exc
            logger.warning("PerfReporter thread failed: %s", exc)

    def _run_reporting(self):
        """Reporter loop: every interval, write the collected numbers out.

        The results client is built on the first loop pass, so a results
        account that is briefly unreachable at startup does not stop the
        reporter for the whole run -- it just retries next interval.
        """
        # Warm up the psutil CPU counters; the first call always returns 0.
        _get_cpu_percent(self._process)
        _get_system_cpu_percent()

        # Start the window clock now, after warmup, so the first row's
        # window_seconds reflects the first interval rather than any startup gap
        # between construction and the thread actually running.
        self._last_flush_monotonic = time.monotonic()
        self._start_monotonic = self._last_flush_monotonic
        # Re-prime the CPU/GC baselines at the same instant the window clock
        # starts, so the first window's deltas line up with its window_seconds.
        self._last_cpu_user, self._last_cpu_system = _get_cpu_times(self._process)
        self._last_gc_collections, self._last_gc_collected, self._last_gc_uncollectable = (
            _get_gc_stats()
        )
        # Reset the backend-counter baselines at the same instant, so the first
        # post-warmup window's execute/binding deltas line up with window_seconds.
        self._last_execute_calls = backend_counters.execute_count()
        self._last_binding_calls = backend_counters.binding_operation_count() or 0
        self._last_attempt_calls = backend_counters.binding_attempt_count() or 0
        self._last_retry_calls = backend_counters.binding_retry_count() or 0

        while not self._stop_event.wait(timeout=self._config["report_interval"]):
            try:
                with self._flush_lock:
                    self._ensure_container()
                    self._flush()
            except Exception as e:
                self._failure = e
                logger.warning("PerfReporter flush failed: %s", e)

    def _write_completion(self):
        if self._failure is not None:
            raise RuntimeError("Earlier reporting failure prevents completion") from self._failure
        self._container.upsert_item({
            "id": f"{self._process_id}-completion",
            "partition_key": self._process_id,
            "record_type": "completion",
            "workload_id": self._config["workload_id"],
            "process_id": self._process_id,
            "window_count": self._window_index,
            "summary_count": self._summary_count,
            "total_count": self._total_count,
            "total_errors": self._total_errors,
        })

    def _ensure_container(self):
        """Create the results client and container on the first call."""
        if self._container is not None:
            return

        endpoint = self._config["results_endpoint"]
        if not endpoint:
            raise ValueError("RESULTS_COSMOS_URI is not set")

        key = os.environ.get("RESULTS_COSMOS_KEY", "")
        if key:
            credential = key
        else:
            credential = DefaultAzureCredential()

        # Keep reporting on core-python, independent of the workload's backend
        # choice, and avoid adding result writes to the native binding counters.
        self._client = CosmosClient(endpoint, credential, _backend=BACKEND_NAME_CORE_PYTHON)
        db = self._client.get_database_client(self._config["results_database"])
        self._container = db.get_container_client(self._config["results_container"])

    def _flush(self):
        """Drain stats and upsert PerfResult + ErrorResult documents."""
        if self._container is None:
            return

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        cpu = _get_cpu_percent(self._process)
        mem = _get_memory_bytes(self._process)
        threads = _get_thread_count(self._process)
        sys_cpu = _get_system_cpu_percent()
        sys_total, sys_used = _get_system_memory()

        concurrency = _safe_int_env("COSMOS_CONCURRENT_REQUESTS", 100)
        target_database = os.environ.get("COSMOS_DATABASE", "")
        target_container = os.environ.get("COSMOS_CONTAINER", "")
        preferred = os.environ.get("COSMOS_PREFERRED_LOCATIONS", "")
        excluded = os.environ.get("COSMOS_CLIENT_EXCLUDED_LOCATIONS", "")
        # Record the per-op timeout and arrival mode on every row, so two rows can
        # be checked for the same policy later. arrival_rate == 0.0 means
        # closed-loop; > 0 means open-loop at that ops/sec per client.
        request_timeout = float(os.environ.get("COSMOS_REQUEST_TIMEOUT", "0"))
        try:
            arrival_rate = float(os.environ.get("WORKLOAD_ARRIVAL_RATE", "0") or "0")
        except (ValueError, TypeError):
            arrival_rate = 0.0
        max_inflight = _safe_int_env("WORKLOAD_MAX_INFLIGHT", 0)
        # How many client processes shared this workload, and whether the run
        # used the sync client. Both are recorded because arrival_rate alone
        # does not describe the arrival process: the sync client ignores
        # WORKLOAD_ARRIVAL_RATE and runs a closed loop, so a row with
        # use_sync == True was unpaced no matter what arrival_rate says.
        num_clients = _safe_int_env("WORKLOAD_NUM_CLIENTS", 1)
        use_sync = os.environ.get("WORKLOAD_USE_SYNC", "false").lower() == "true"
        # Which backend produced these numbers: "rust" or "core-python" (the
        # default). Tagged so the two can be told apart in the results store.
        backend = os.environ.get("COSMOS_BACKEND", "core-python")
        ppcb = (
            os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "false").lower()
            == "true"
        )
        multi_write = (
            os.environ.get("COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS", "false").lower()
            == "true"
        )
        proxy_enabled = (
            os.environ.get("WORKLOAD_USE_PROXY", "false").lower() == "true"
        )
        skip_close = (
            os.environ.get("WORKLOAD_SKIP_CLOSE", "false").lower() == "true"
        )
        workload_mix = os.environ.get("WORKLOAD_MIX", "").strip()
        doc_profile = os.environ.get("WORKLOAD_DOC_PROFILE", "default").strip().lower()

        summaries, errors = self._stats.drain_all()
        if not summaries and not errors:
            return
        self._window_index += 1
        window_id = f"{self._process_id}-{self._window_index}"
        self._summary_count += len(summaries)
        self._total_count += sum(s["count"] for s in summaries)
        self._total_errors += sum(s["errors"] for s in summaries)
        # The drain is when these counts stop accumulating, so measure the window
        # here. It is normally the configured interval, but longer when a previous
        # flush was skipped; storing it keeps count / window_seconds accurate.
        now_monotonic = time.monotonic()
        window_seconds = now_monotonic - self._last_flush_monotonic
        self._last_flush_monotonic = now_monotonic
        # Seconds since the (post-warmup) reporter start, so a query can drop
        # warmup windows instead of letting cold start decide the result.
        elapsed_seconds = now_monotonic - self._start_monotonic
        # Process CPU-time delta, including reporter and other concurrent work.
        # Per-operation attribution requires a suitable isolated workload.
        cur_cpu_user, cur_cpu_system = _get_cpu_times(self._process)
        cpu_user_seconds = round(max(0.0, cur_cpu_user - self._last_cpu_user), 4)
        cpu_system_seconds = round(max(0.0, cur_cpu_system - self._last_cpu_system), 4)
        cpu_seconds = round(cpu_user_seconds + cpu_system_seconds, 4)
        self._last_cpu_user, self._last_cpu_system = cur_cpu_user, cur_cpu_system
        # Process-wide GC activity. Correlation with a latency tail does not
        # establish causation or predict how the backends compare.
        cur_gc_collections, cur_gc_collected, cur_gc_uncollectable = _get_gc_stats()
        gc_collections = max(0, cur_gc_collections - self._last_gc_collections)
        gc_collected = max(0, cur_gc_collected - self._last_gc_collected)
        gc_uncollectable = max(0, cur_gc_uncollectable - self._last_gc_uncollectable)
        self._last_gc_collections = cur_gc_collections
        self._last_gc_collected = cur_gc_collected
        self._last_gc_uncollectable = cur_gc_uncollectable
        # Worst event-loop scheduling delay this window (ms); 0 on the sync path or
        # when the monitor is off. A large value does not identify the cause.
        loop_lag_max_ms = round(self._stats.drain_loop_lag(), 3)
        # Process-wide counter deltas: normal Python execute returns and
        # instrumented binding entries (-1 when unavailable). Window boundaries
        # and unrelated calls limit attribution to the measured operations.
        cur_execute_calls = backend_counters.execute_count()
        rust_execute_calls = max(0, cur_execute_calls - self._last_execute_calls)
        self._last_execute_calls = cur_execute_calls
        cur_binding_raw = backend_counters.binding_operation_count()
        if cur_binding_raw is None:
            binding_calls = -1
        else:
            binding_calls = max(0, cur_binding_raw - self._last_binding_calls)
            self._last_binding_calls = cur_binding_raw
        # Diagnostics-counter deltas (-1 when unavailable). Only recorded
        # contexts contribute; retry counting also depends on retained records.
        # They do not establish fixed per-operation round-trip counts.
        cur_attempt_raw = backend_counters.binding_attempt_count()
        if cur_attempt_raw is None:
            attempt_calls = -1
        else:
            attempt_calls = max(0, cur_attempt_raw - self._last_attempt_calls)
            self._last_attempt_calls = cur_attempt_raw
        cur_retry_raw = backend_counters.binding_retry_count()
        if cur_retry_raw is None:
            retry_calls = -1
        else:
            retry_calls = max(0, cur_retry_raw - self._last_retry_calls)
            self._last_retry_calls = cur_retry_raw
        runtime_backend = backend_counters.runtime_backend()
        # Earliest-N per-op durations since process start (not reset per window), so
        # a cold-start analyzer can pool the first calls across processes. Same for
        # every summary row of this flush; keyed per op below.
        for s in summaries:
            doc = {
                "id": str(uuid.uuid4()),
                "partition_key": str(uuid.uuid4()),
                "workload_id": self._config["workload_id"],
                "record_type": "measurement",
                "process_id": self._process_id,
                "window_id": window_id,
                "window_index": self._window_index,
                "commit_sha": self._config["commit_sha"],
                "driver_commit": self._config["driver_commit"],
                "hostname": self._hostname,
                "TIMESTAMP": now,  # ALL_CAPS for Rust SDK PerfResults schema compatibility
                "operation": s["operation"],
                "count": s["count"],
                "errors": s["errors"],
                "throttled_429": s["throttled_429"],
                # Actual seconds this row covers, so throughput is
                # count / window_seconds. Do not divide count by the configured
                # interval; that is wrong for merged windows and the final flush.
                "window_seconds": window_seconds,
                # Seconds since (post-warmup) start, so warmup windows can be
                # dropped from the result.
                "elapsed_seconds": elapsed_seconds,
                "min_ms": round(s["min_ms"], 3),
                "max_ms": round(s["max_ms"], 3),
                "mean_ms": round(s["mean_ms"], 3),
                "p50_ms": round(s["p50_ms"], 3),
                "p90_ms": round(s["p90_ms"], 3),
                "p99_ms": round(s["p99_ms"], 3),
                "p99_9_ms": round(s.get("p99_9_ms", 0.0), 3),
                # Base64 HdrHistogram for this window (None on an all-errors row).
                # Lets an offline analyzer merge every window of a point for a true
                # pooled p50/p99/p99.9, which the per-window scalars cannot give.
                "hist_b64": s.get("hist_b64"),
                # Cold-start sample: the very first call's latency (ms) for this op
                # since process start, and the earliest calls as a warm-up curve.
                # Not reset per window, so short one-flush processes each contribute
                # one first-call sample the analyzer can pool. Present on every row of
                # a process but identical across its rows; the curve is capped so this
                # does not bloat every result document (the analyzer only needs the
                # first several points to see where latency settles).
                "cold_first_ms": (
                    round(s["cold_first_n_ms"][0], 3)
                    if s["cold_first_n_ms"] else None
                ),
                "cold_first_n_ms": [
                    round(v, 3) for v in s["cold_first_n_ms"]
                ],
                # Mean of captured request-charge samples. Matching means alone
                # do not establish identical backend work or complete accounting.
                "mean_ru": round(s.get("mean_ru", 0.0), 3),
                # Raw RU total and sample count, so a cross-window average can be
                # count-weighted (SUM(ru_sum)/SUM(ru_count)) rather than an average
                # of per-window means.
                "ru_sum": round(s.get("ru_sum", 0.0), 4),
                "ru_count": s.get("ru_count", 0),
                # Header-derived duration samples, pooled separately from client
                # durations. Independent tails cannot isolate per-call overhead.
                # A sample-count mismatch requires checking header/callback coverage.
                "server_count": s.get("server_count", 0),
                "server_p50_ms": round(s.get("server_p50_ms", 0.0), 3),
                "server_p99_ms": round(s.get("server_p99_ms", 0.0), 3),
                "server_p99_9_ms": round(s.get("server_p99_9_ms", 0.0), 3),
                "server_hist_b64": s.get("server_hist_b64"),
                "cpu_percent": round(cpu, 1),
                # CPU-seconds in this window, from the cpu_times() delta. Compare as
                # CPU-seconds per 1k ops on single-op runs. cpu_user/system split it.
                "cpu_seconds": cpu_seconds,
                "cpu_user_seconds": cpu_user_seconds,
                "cpu_system_seconds": cpu_system_seconds,
                # Process-wide GC counts; correlation with latency is not causation.
                "gc_collections": gc_collections,
                "gc_collected": gc_collected,
                "gc_uncollectable": gc_uncollectable,
                # Worst event-loop scheduling delay this window (ms); 0 on the sync
                # path or when the monitor is off; this does not identify a cause.
                "loop_lag_max_ms": loop_lag_max_ms,
                "memory_bytes": mem,
                # All process OS threads, not a driver-owned-thread census.
                # Compare with RSS as a clue, not proof of a leak or its absence.
                "thread_count": threads,
                "system_cpu_percent": round(sys_cpu, 1),
                "system_total_memory_bytes": sys_total,
                "system_used_memory_bytes": sys_used,
                "sdk_language": "python",
                "sdk_version": self._sdk_version,
                "config_backend": backend,
                "runtime_backend": runtime_backend,
                "rust_execute_calls": rust_execute_calls,
                "binding_calls": binding_calls,
                # Recorded native diagnostics counts, with the coverage limits
                # described above. -1 means unavailable, not zero attempts/retries.
                "attempt_calls": attempt_calls,
                "retry_calls": retry_calls,
                "config_concurrency": concurrency,
                "config_database": target_database,
                "config_container": target_container,
                "config_application_region": preferred,
                "config_excluded_regions": excluded,
                "config_request_timeout": request_timeout,
                "config_arrival_rate": arrival_rate,
                "config_num_clients": num_clients,
                "config_use_sync": use_sync,
                "config_max_inflight": max_inflight,
                "config_workload_mix": workload_mix,
                "config_doc_profile": doc_profile,
                "config_ppcb_enabled": ppcb,
                "config_multi_write_enabled": multi_write,
                "config_proxy_enabled": proxy_enabled,
                "config_skip_close": skip_close,
            }
            try:
                self._container.upsert_item(doc)
            except Exception as e:
                self._failure = e
                logger.warning(
                    "PerfReporter upsert failed for %s: %s", s["operation"], e
                )

        for err in errors:
            doc = {
                "id": str(uuid.uuid4()),
                "partition_key": str(uuid.uuid4()),
                "workload_id": self._config["workload_id"],
                "record_type": "error",
                "process_id": self._process_id,
                "commit_sha": self._config["commit_sha"],
                "driver_commit": self._config["driver_commit"],
                "hostname": self._hostname,
                "TIMESTAMP": now,  # ALL_CAPS for Rust SDK PerfResults schema compatibility
                "operation": err["operation"],
                "error_message": err["error_message"][:2000],
                "source_message": err["source_message"][:4000],
                "sdk_language": "python",
                "config_backend": backend,
                "config_database": target_database,
                "config_container": target_container,
                "config_workload_mix": workload_mix,
                "config_doc_profile": doc_profile,
                "error_status_code": err.get("error_status_code"),
                "error_sub_status_code": err.get("error_sub_status_code"),
            }
            try:
                self._container.upsert_item(doc)
            except Exception as e:
                self._failure = e
                logger.warning("PerfReporter error upsert failed: %s", e)
