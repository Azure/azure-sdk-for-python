# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Background reporter that drains Stats and upserts PerfResult documents to Cosmos DB."""

import logging
import os
import socket
import threading
import uuid
from datetime import datetime, timezone

import psutil

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


def _get_memory_bytes(process) -> int:
    """Get current process RSS in bytes."""
    try:
        return process.memory_info().rss
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
        """Reporter loop: wait for interval, then flush."""
        try:
            self._ensure_container()
        except Exception as e:
            logger.warning("PerfReporter failed to initialize Cosmos client: %s", e)
            return

        # Prime psutil CPU counters (first call always returns 0)
        _get_cpu_percent(self._process)
        _get_system_cpu_percent()

        while not self._stop_event.wait(timeout=self._config["report_interval"]):
            try:
                with self._flush_lock:
                    self._flush()
            except Exception as e:
                logger.warning("PerfReporter flush failed: %s", e)

    def _ensure_container(self):
        """Lazily create the sync CosmosClient and get the container reference."""
        if self._container is not None:
            return

        from azure.cosmos import CosmosClient

        endpoint = self._config["results_endpoint"]
        if not endpoint:
            raise ValueError("RESULTS_COSMOS_URI is not set")

        key = os.environ.get("RESULTS_COSMOS_KEY", "")
        if key:
            credential = key
        else:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()

        self._client = CosmosClient(endpoint, credential)
        db = self._client.get_database_client(self._config["results_database"])
        self._container = db.get_container_client(self._config["results_container"])

    def _flush(self):
        """Drain stats and upsert PerfResult + ErrorResult documents."""
        if self._container is None:
            return

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        cpu = _get_cpu_percent(self._process)
        mem = _get_memory_bytes(self._process)
        sys_cpu = _get_system_cpu_percent()
        sys_total, sys_used = _get_system_memory()

        concurrency = _safe_int_env("COSMOS_CONCURRENT_REQUESTS", 100)
        preferred = os.environ.get("COSMOS_PREFERRED_LOCATIONS", "")
        excluded = os.environ.get("COSMOS_CLIENT_EXCLUDED_LOCATIONS", "")
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
                "min_ms": round(s["min_ms"], 3),
                "max_ms": round(s["max_ms"], 3),
                "mean_ms": round(s["mean_ms"], 3),
                "p50_ms": round(s["p50_ms"], 3),
                "p90_ms": round(s["p90_ms"], 3),
                "p99_ms": round(s["p99_ms"], 3),
                "cpu_percent": round(cpu, 1),
                "memory_bytes": mem,
                "system_cpu_percent": round(sys_cpu, 1),
                "system_total_memory_bytes": sys_total,
                "system_used_memory_bytes": sys_used,
                "sdk_language": "python",
                "sdk_version": self._sdk_version,
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
                "error_status_code": err.get("error_status_code"),
                "error_sub_status_code": err.get("error_sub_status_code"),
            }
            try:
                self._container.upsert_item(doc)
            except Exception as e:
                logger.warning("PerfReporter error upsert failed: %s", e)


def _safe_int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (ValueError, TypeError):
        return default
