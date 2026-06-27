# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# All configuration is driven by environment variables with sensible defaults.
import logging
import os
from perf_config import _safe_int

from azure.identity import DefaultAzureCredential


def _parse_region_list(env_var_name):
    value = os.environ.get(env_var_name, "")
    return (
        [region.strip() for region in value.split(",") if region.strip()]
        if value
        else []
    )


def _safe_float(value, default):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


PREFERRED_LOCATIONS = _parse_region_list("COSMOS_PREFERRED_LOCATIONS")
CLIENT_EXCLUDED_LOCATIONS = _parse_region_list("COSMOS_CLIENT_EXCLUDED_LOCATIONS")
REQUEST_EXCLUDED_LOCATIONS = _parse_region_list("COSMOS_REQUEST_EXCLUDED_LOCATIONS")
COSMOS_PROXY_URI = os.environ.get("COSMOS_PROXY_URI", "0.0.0.0")
COSMOS_URI = os.environ.get("COSMOS_URI", "")
COSMOS_KEY = os.environ.get("COSMOS_KEY", "")
COSMOS_CREDENTIAL = COSMOS_KEY if COSMOS_KEY else DefaultAzureCredential()
COSMOS_CONTAINER = os.environ.get("COSMOS_CONTAINER", "scale_cont")
COSMOS_DATABASE = os.environ.get("COSMOS_DATABASE", "scale_db")
USER_AGENT_PREFIX = os.environ.get("COSMOS_USER_AGENT_PREFIX", "")
# Quiet by default for measurement. DEBUG makes the SDK and this harness log
# heavily, which adds CPU and file-I/O overhead that confounds a perf comparison
# (see also ENABLE_DIAGNOSTICS_LOGGING). Set COSMOS_LOG_LEVEL=DEBUG only when
# debugging, never for an SLA/perf run.
LOG_LEVEL = getattr(logging, os.environ.get("COSMOS_LOG_LEVEL", "WARNING"), logging.WARNING)
# Per-request diagnostics logging. OFF by default: when on, the SDK emits a
# diagnostics record for *every* request, which the WorkloadLoggerFilter processes
# and writes to a rotating file — real CPU / latency / file-I/O overhead that
# confounds a perf comparison and can bias the two backends unequally (they log
# different volumes). RU is now read from the row (mean_ru) and 429s from the
# errors count, so a perf run does not need this. Turn it on
# (COSMOS_ENABLE_DIAGNOSTICS_LOGGING=true) only for debugging.
ENABLE_DIAGNOSTICS_LOGGING = (
    os.environ.get("COSMOS_ENABLE_DIAGNOSTICS_LOGGING", "false").lower() == "true"
)
APP_INSIGHTS_CONNECTION_STRING = os.environ.get("APP_INSIGHTS_CONNECTION_STRING", "")
CIRCUIT_BREAKER_ENABLED = (
    os.environ.get("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER", "false").lower() == "true"
)
USE_MULTIPLE_WRITABLE_LOCATIONS = (
    os.environ.get("COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS", "false").lower() == "true"
)
CONCURRENT_REQUESTS = _safe_int(os.environ.get("COSMOS_CONCURRENT_REQUESTS", "100"), 100)
CONCURRENT_QUERIES = _safe_int(os.environ.get("COSMOS_CONCURRENT_QUERIES", "2"), 2)
WORKLOAD_NUM_CLIENTS = _safe_int(os.environ.get("WORKLOAD_NUM_CLIENTS", "1"), 1)
PARTITION_KEY = os.environ.get("COSMOS_PARTITION_KEY", "id")
NUMBER_OF_LOGICAL_PARTITIONS = int(
    os.environ.get("COSMOS_NUMBER_OF_LOGICAL_PARTITIONS", "10000")
)
THROUGHPUT = _safe_int(os.environ.get("COSMOS_THROUGHPUT", "100000"), 100000)  # For DR drills, set COSMOS_THROUGHPUT=1000000

# Per-request end-to-end timeout in seconds, passed as the `timeout` kwarg on
# every timed operation (the SDK scopes it to TimeoutScope.OPERATION). UNSET or
# <= 0 means "do not pass one" — each backend then keeps its own default (legacy
# ~65 s per-attempt on core-python; ~6 s end-to-end on Rust). To compare the
# extreme tail fairly, set the SAME COSMOS_REQUEST_TIMEOUT on both the baseline
# and the Rust run; otherwise a tail difference is the timeout *policy*, not the
# SDK (see docs/RUST_PYTHON_PERFORMANCE.md). Sub-second values clamp to a 1 s floor on
# the Rust path.
REQUEST_TIMEOUT = _safe_float(os.environ.get("COSMOS_REQUEST_TIMEOUT", "0"), 0.0)

# Workload behavior. WORKLOAD_OPERATIONS picks which operations the loop runs:
# any subset of the six point operations, plus "query" for context. Comma
# separated, case-insensitive. "write" is a backward-compatible alias for
# "upsert".
_VALID_OPERATIONS = {"read", "create", "upsert", "replace", "delete", "patch", "query"}
_OPERATION_ALIASES = {"write": "upsert"}
_raw_operations = [
    op.strip().lower()
    for op in os.environ.get(
        "WORKLOAD_OPERATIONS", "read,create,upsert,replace,delete,patch"
    ).split(",")
    if op.strip()
]
WORKLOAD_OPERATIONS = frozenset(
    _OPERATION_ALIASES.get(op, op) for op in _raw_operations
)
_unknown_ops = WORKLOAD_OPERATIONS - _VALID_OPERATIONS
if _unknown_ops:
    raise ValueError(
        f"Unknown WORKLOAD_OPERATIONS: {_unknown_ops}. Valid: {sorted(_VALID_OPERATIONS)} "
        f"(plus 'write' as an alias for 'upsert')."
    )
WORKLOAD_USE_PROXY = os.environ.get("WORKLOAD_USE_PROXY", "false").lower() == "true"
WORKLOAD_USE_SYNC = os.environ.get("WORKLOAD_USE_SYNC", "false").lower() == "true"

# Open-loop (constant-arrival) load. Default 0 = OFF -> the existing closed-loop
# batched-wave driver is used, unchanged. When > 0, the async driver instead fires
# operations at this fixed rate (ops/sec) WITHOUT waiting for each wave, and times
# every operation from its INTENDED arrival instant. That makes the measured tail
# include the time a request waited to be issued under load -- the "coordinated
# omission" a closed-loop generator hides. Only meaningful on the async path.
WORKLOAD_ARRIVAL_RATE = _safe_float(os.environ.get("WORKLOAD_ARRIVAL_RATE", "0"), 0.0)
# Safety cap on simultaneously in-flight operations in open-loop mode, so a stalled
# service cannot let the backlog grow without bound and OOM the generator. The
# backlog still shows up as rising latency (the intended-arrival clock keeps
# advancing); this only bounds memory.
WORKLOAD_MAX_INFLIGHT = _safe_int(os.environ.get("WORKLOAD_MAX_INFLIGHT", "10000"), 10000)

# Freeze the garbage collector after warmup (gc.freeze moves existing objects to a
# permanent generation so they are never rescanned). Default OFF. Turn ON for a
# measurement run where you want GC pauses out of the latency tail; leave OFF to
# measure the SDK as it really runs. Recorded GC counters (gc_collections etc.)
# show whether GC is firing either way.
WORKLOAD_GC_FREEZE = os.environ.get("WORKLOAD_GC_FREEZE", "false").lower() == "true"

# Event-loop lag monitor (async only). Default ON: a lightweight background task
# samples how late the loop services a timer and reports the worst value per window
# as loop_lag_max_ms, so loop saturation (the single GIL-bound loop thread becoming
# the bottleneck) is visible. Set false to disable.
WORKLOAD_LOOP_LAG_MONITOR = (
    os.environ.get("WORKLOAD_LOOP_LAG_MONITOR", "true").lower() == "true"
)

# When true, the client is created without a context manager (no automatic close).
# Simulates applications that don't properly close the Cosmos client.
WORKLOAD_SKIP_CLOSE = os.environ.get("WORKLOAD_SKIP_CLOSE", "false").lower() == "true"
