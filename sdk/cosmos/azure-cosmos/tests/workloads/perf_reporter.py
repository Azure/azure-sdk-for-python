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

logger = logging.getLogger(__name__)


def _get_sdk_version() -> str:
    """Get the azure-cosmos SDK version string."""
    try:
        from azure.cosmos import __version__

        return __version__
    except Exception:
        return "unknown"


def _get_cpu_percent(process) -> float:
    """Get current process CPU percent."""
    try:
        return process.cpu_percent(interval=None)
    except Exception:
        return 0.0


def _get_cpu_times(process) -> tuple:
    """Return cumulative (user, system) CPU seconds for the process.

    Unlike ``cpu_percent`` (a sampled rate), ``cpu_times`` is a monotonically
    increasing counter, so the difference between two reads is the EXACT CPU time
    spent in that window -- the right input for the CPU-per-op gate (check 3),
    which is the migration's headline number. Returns (0.0, 0.0) on any error.
    """
    try:
        t = process.cpu_times()
        return float(t.user), float(t.system)
    except Exception:
        return 0.0, 0.0


def _get_gc_stats() -> tuple:
    """Return cumulative (collections, collected, uncollectable) across all GC
    generations.

    ``gc.get_stats`` returns per-generation cumulative counters; summing them and
    differencing across a window gives how many GC passes ran and how many objects
    they reclaimed in that window. A tail (P99.9) that moves with GC activity is a
    Python-garbage problem, and a real Rust-path tail win is partly *less* garbage
    crossing the boundary -- so recording GC makes that mechanism visible instead
    of hiding inside a "bad window". Returns (0, 0, 0) on any error.
    """
    try:
        stats = gc.get_stats()
        collections = sum(g.get("collections", 0) for g in stats)
        collected = sum(g.get("collected", 0) for g in stats)
        uncollectable = sum(g.get("uncollectable", 0) for g in stats)
        return collections, collected, uncollectable
    except Exception:
        return 0, 0, 0


def _get_memory_bytes(process) -> int:
    """Get current process RSS in bytes."""
    try:
        return process.memory_info().rss
    except Exception:
        return 0


def _get_thread_count(process) -> int:
    """Get the process's current OS thread count.

    On the **sync** path this is the shared Tokio runtime's threads; on the
    **async** path it is the driver's own runtime and connection threads. (The
    interim async thread-pool stopgap — a dedicated pool capped at 256 — was
    retired when the async path went true-async; see docs/RUST_PYTHON_SLA.md.
    A large, thread-shaped RSS step that tracks this count would therefore now
    be a *new* regression, not the old pool filling.) Recorded so RSS steps and
    any concurrency-sweep tail bend can be tied to threads actually in use, not
    inferred.
    """
    try:
        return process.num_threads()
    except Exception:
        return 0


def _get_system_cpu_percent() -> float:
    """Get system-wide CPU percent."""
    try:
        return psutil.cpu_percent(interval=None)
    except Exception:
        return 0.0


def _get_system_memory() -> tuple:
    """Get system total and used memory in bytes."""
    try:
        mem = psutil.virtual_memory()
        return mem.total, mem.used
    except Exception:
        return 0, 0


class PerfReporter:
    """Background reporter that upserts PerfResult documents to Cosmos DB.

    Uses a daemon thread with a sync CosmosClient. The reporter drains
    Stats at the configured interval and upserts one PerfResult document
    per operation. All errors are caught and logged — the workload is
    never affected.
    """

    def __init__(self, stats: Stats, config: dict):
        self._stats = stats
        self._config = config
        self._stop_event = threading.Event()
        self._thread = None
        self._flush_lock = threading.Lock()
        self._client = None
        self._container = None
        self._hostname = socket.gethostname()
        self._sdk_version = _get_sdk_version()
        self._process = psutil.Process()
        # Monotonic time of the last successful drain. Each row stores the
        # ACTUAL seconds it covers (window_seconds = now - this), so throughput
        # is count / window_seconds rather than count / the configured interval.
        # When a flush is skipped (e.g. _ensure_container raises because the
        # results account is briefly unreachable), the stats keep accumulating
        # and the next successful drain covers a longer window; storing the real
        # window keeps req/s correct instead of ~2x too high on the merged row.
        self._last_flush_monotonic = time.monotonic()
        # Reporter start (monotonic), for the elapsed_seconds each row carries so
        # warmup windows can be excluded from the verdict — the first windows
        # include cold start and the Rust driver warming its connection pools
        # (RSS steps up once), which would otherwise skew the tail and the
        # memory-slope check. (The old async thread-pool fill that used to
        # dominate this step is retired — see _get_thread_count.) Reset in
        # _run after the CPU warmup so elapsed starts at the first real window.
        self._start_monotonic = self._last_flush_monotonic
        # Baselines for the EXACT per-window CPU and GC deltas, primed in _run
        # after warmup (so the first window starts clean) and advanced on every
        # successful flush in lockstep with window_seconds. Initialised here so a
        # flush that somehow runs before _run still has something to subtract.
        self._last_cpu_user, self._last_cpu_system = _get_cpu_times(self._process)
        self._last_gc_collections, self._last_gc_collected, self._last_gc_uncollectable = (
            _get_gc_stats()
        )

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
            logger.warning("PerfReporter thread still alive after join timeout, skipping final flush")
        else:
            try:
                with self._flush_lock:
                    self._ensure_container()
                    self._flush()
            except Exception as e:
                logger.warning("PerfReporter final flush failed: %s", e)
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
        logger.info("PerfReporter stopped")

    def _run(self):
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

        while not self._stop_event.wait(timeout=self._config["report_interval"]):
            try:
                with self._flush_lock:
                    self._ensure_container()
                    self._flush()
            except Exception as e:
                logger.warning("PerfReporter flush failed: %s", e)

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

        # Force the results client to use core-python so it keeps working when
        # the workload runs with COSMOS_BACKEND=rust. Otherwise the reporter
        # would follow that variable and write its results over the rust path,
        # which cannot read the account yet.
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
        preferred = os.environ.get("COSMOS_PREFERRED_LOCATIONS", "")
        excluded = os.environ.get("COSMOS_CLIENT_EXCLUDED_LOCATIONS", "")
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

        summaries, errors = self._stats.drain_all()
        # The drain is the instant these counts stop accumulating, so measure the
        # window here (monotonic, immune to wall-clock changes). It is normally
        # the configured interval, but ~2x (or more) when a previous flush was
        # skipped; storing it keeps throughput = count / window_seconds honest.
        now_monotonic = time.monotonic()
        window_seconds = round(now_monotonic - self._last_flush_monotonic, 3)
        self._last_flush_monotonic = now_monotonic
        # Seconds since the (post-warmup) reporter start, so a query can drop
        # warmup windows — e.g. WHERE c.elapsed_seconds > 1800 — instead of letting
        # cold start or connection-pool warmup decide the verdict. See the SLA doc.
        elapsed_seconds = round(now_monotonic - self._start_monotonic, 3)
        # CPU-seconds the process spent in this window, measured EXACTLY from the
        # cpu_times() counter delta (user + system), not from a sampled cpu_percent.
        # This is the input for the CPU-per-op gate (check 3) -- the migration's
        # headline number -- so it is worth measuring precisely. The user/system
        # split is also kept: the Rust driver's native networking work tends to land
        # in *system* time, so a shift in the split is itself informative. Normalize
        # in the SLA doc as CPU-seconds per 1k ops = SUM(cpu_seconds)/SUM(count)*1000,
        # meaningful on a SINGLE-op run (an all-six run shares CPU across ops).
        cur_cpu_user, cur_cpu_system = _get_cpu_times(self._process)
        cpu_user_seconds = round(max(0.0, cur_cpu_user - self._last_cpu_user), 4)
        cpu_system_seconds = round(max(0.0, cur_cpu_system - self._last_cpu_system), 4)
        cpu_seconds = round(cpu_user_seconds + cpu_system_seconds, 4)
        self._last_cpu_user, self._last_cpu_system = cur_cpu_user, cur_cpu_system
        # GC activity in this window (delta of cumulative counters): how many GC
        # passes ran and how many objects they reclaimed. Correlate with p99_9_ms to
        # see whether a tail spike is GC-driven (a Python-garbage effect), and watch
        # it drop on the Rust path, which allocates fewer Python objects per op.
        cur_gc_collections, cur_gc_collected, cur_gc_uncollectable = _get_gc_stats()
        gc_collections = max(0, cur_gc_collections - self._last_gc_collections)
        gc_collected = max(0, cur_gc_collected - self._last_gc_collected)
        gc_uncollectable = max(0, cur_gc_uncollectable - self._last_gc_uncollectable)
        self._last_gc_collections = cur_gc_collections
        self._last_gc_collected = cur_gc_collected
        self._last_gc_uncollectable = cur_gc_uncollectable
        # Worst event-loop scheduling delay this window (ms); 0 on the sync path or
        # when the monitor is not running. A large value means the single asyncio
        # loop thread is the bottleneck, not the SDK -- see the SLA doc.
        loop_lag_max_ms = round(self._stats.drain_loop_lag(), 3)
        for s in summaries:
            doc = {
                "id": str(uuid.uuid4()),
                "partition_key": str(uuid.uuid4()),
                "workload_id": self._config["workload_id"],
                "commit_sha": self._config["commit_sha"],
                "hostname": self._hostname,
                "TIMESTAMP": now,  # ALL_CAPS for Rust SDK PerfResults schema compatibility
                "operation": s["operation"],
                "count": s["count"],
                "errors": s["errors"],
                # Actual seconds this row covers, so throughput is
                # count / window_seconds — correct even when a skipped flush made
                # this row merge more than one interval. Do NOT divide count by
                # the configured PERF_REPORT_INTERVAL; that is wrong for merged
                # windows and for the (usually shorter) final flush.
                "window_seconds": window_seconds,
                # Seconds since (post-warmup) start, so warmup windows can be
                # excluded from the verdict (checks 1 & 4 in the SLA doc).
                "elapsed_seconds": elapsed_seconds,
                "min_ms": round(s["min_ms"], 3),
                "max_ms": round(s["max_ms"], 3),
                "mean_ms": round(s["mean_ms"], 3),
                "p50_ms": round(s["p50_ms"], 3),
                "p90_ms": round(s["p90_ms"], 3),
                "p99_ms": round(s["p99_ms"], 3),
                "p99_9_ms": round(s.get("p99_9_ms", 0.0), 3),
                # Mean RU (request-unit) charge per successful op, from the
                # x-ms-request-charge response header. The data source for the
                # "same work" RU-parity check (the workload log keeps only
                # errors and slow calls, so it cannot provide this).
                "mean_ru": round(s.get("mean_ru", 0.0), 3),
                # Raw RU total + sample count, so a cross-window aggregate can be
                # count-weighted (SUM(ru_sum)/SUM(ru_count)) instead of an unweighted
                # average of per-window means. RU/op is near-constant so the two
                # barely differ, but this keeps check 5 strict like the CPU check.
                "ru_sum": round(s.get("ru_sum", 0.0), 4),
                "ru_count": s.get("ru_count", 0),
                "cpu_percent": round(cpu, 1),
                # CPU-seconds in this window, EXACT from the cpu_times() delta;
                # normalize by work in the SLA doc as CPU-seconds per 1k ops
                # (single-op runs — see comment above). cpu_user/system split it.
                "cpu_seconds": cpu_seconds,
                "cpu_user_seconds": cpu_user_seconds,
                "cpu_system_seconds": cpu_system_seconds,
                # GC activity this window (deltas): passes run, objects reclaimed,
                # objects it could not reclaim. A p99_9_ms that tracks gc_collections
                # is a Python-garbage tail, not the SDK; expect these lower on Rust.
                "gc_collections": gc_collections,
                "gc_collected": gc_collected,
                "gc_uncollectable": gc_uncollectable,
                # Worst event-loop scheduling delay this window (ms); 0 on the sync
                # path or when the async loop-lag monitor is not running. Large =>
                # the single asyncio loop thread is the bottleneck, not the SDK.
                "loop_lag_max_ms": loop_lag_max_ms,
                "memory_bytes": mem,
                # OS thread count at this sample. On the **async** path this is
                # the Rust driver's own runtime and connection threads; on the
                # **sync** path, the shared Tokio runtime's threads. (The interim
                # async thread-pool stopgap — a dedicated pool capped at 256 — is
                # retired, so thread_count no longer tracks a worker pool on the
                # async path; a large thread-shaped RSS step that tracks this
                # count would now be a *new* regression, not the old pool filling.
                # See _get_thread_count and docs/RUST_PYTHON_SLA.md.) Correlate
                # with memory_bytes to tell a one-time warmup RSS step from a leak.
                "thread_count": threads,
                "system_cpu_percent": round(sys_cpu, 1),
                "system_total_memory_bytes": sys_total,
                "system_used_memory_bytes": sys_used,
                "sdk_language": "python",
                "sdk_version": self._sdk_version,
                "config_backend": backend,
                "config_concurrency": concurrency,
                "config_application_region": preferred,
                "config_excluded_regions": excluded,
                "config_ppcb_enabled": ppcb,
                "config_multi_write_enabled": multi_write,
                "config_proxy_enabled": proxy_enabled,
                "config_skip_close": skip_close,
            }
            try:
                self._container.upsert_item(doc)
            except Exception as e:
                logger.warning(
                    "PerfReporter upsert failed for %s: %s", s["operation"], e
                )

        for err in errors:
            doc = {
                "id": str(uuid.uuid4()),
                "partition_key": str(uuid.uuid4()),
                "workload_id": self._config["workload_id"],
                "commit_sha": self._config["commit_sha"],
                "hostname": self._hostname,
                "TIMESTAMP": now,  # ALL_CAPS for Rust SDK PerfResults schema compatibility
                "operation": err["operation"],
                "error_message": err["error_message"][:2000],
                "source_message": err["source_message"][:4000],
                "sdk_language": "python",
                "config_backend": backend,
                "error_status_code": err.get("error_status_code"),
                "error_sub_status_code": err.get("error_sub_status_code"),
            }
            try:
                self._container.upsert_item(doc)
            except Exception as e:
                logger.warning("PerfReporter error upsert failed: %s", e)

