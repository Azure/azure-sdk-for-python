# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# All configuration is driven by environment variables with sensible defaults.
import logging
import os

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


# Names exported by ``from workload_configs import *`` (keeps stdlib modules and
# DefaultAzureCredential from leaking into importers).
__all__ = [
    "PREFERRED_LOCATIONS",
    "CLIENT_EXCLUDED_LOCATIONS",
    "REQUEST_EXCLUDED_LOCATIONS",
    "COSMOS_PROXY_URI",
    "COSMOS_URI",
    "COSMOS_KEY",
    "COSMOS_CREDENTIAL",
    "COSMOS_CONTAINER",
    "COSMOS_DATABASE",
    "USER_AGENT_PREFIX",
    "LOG_LEVEL",
    "ENABLE_DIAGNOSTICS_LOGGING",
    "APP_INSIGHTS_CONNECTION_STRING",
    "CIRCUIT_BREAKER_ENABLED",
    "USE_MULTIPLE_WRITABLE_LOCATIONS",
    "CONCURRENT_REQUESTS",
    "CONCURRENT_QUERIES",
    "WORKLOAD_NUM_CLIENTS",
    "PARTITION_KEY",
    "NUMBER_OF_LOGICAL_PARTITIONS",
    "THROUGHPUT",
    "REQUEST_TIMEOUT",
    "WORKLOAD_OPERATIONS",
    "WORKLOAD_USE_PROXY",
    "WORKLOAD_USE_SYNC",
    "WORKLOAD_ARRIVAL_RATE",
    "WORKLOAD_MAX_INFLIGHT",
    "WORKLOAD_GC_FREEZE",
    "WORKLOAD_LOOP_LAG_MONITOR",
    "WORKLOAD_SKIP_CLOSE",
    "WORKLOAD_MIX",
    "WORKLOAD_DOC_PROFILE",
]


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
# Quiet by default. DEBUG makes the SDK and harness log heavily, adding CPU and
# file-I/O cost that skews a perf comparison. Use DEBUG only when debugging.
LOG_LEVEL = getattr(logging, os.environ.get("COSMOS_LOG_LEVEL", "WARNING"), logging.WARNING)
# Per-request diagnostics logging. Off by default: when on, the SDK writes a
# record for every request, adding CPU and file-I/O cost that skews a perf run.
# RU comes from the result row and 429s from the error count, so a perf run does
# not need this. Turn it on only for debugging.
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
# Highest item index the workload uses, despite the name. Item ids run "test-0"
# through "test-<this value>", so the seeding step creates one more item than this
# number and every operation picks an index in the inclusive range 0..this value.
# The name comes from each seeded item sitting in its own logical partition. Seeding
# and the timed run must use the same value, or reads ask for ids that were never
# created and return 404.
NUMBER_OF_LOGICAL_PARTITIONS = int(
    os.environ.get("COSMOS_NUMBER_OF_LOGICAL_PARTITIONS", "10000")
)
THROUGHPUT = _safe_int(os.environ.get("COSMOS_THROUGHPUT", "100000"), 100000)  # For DR drills, set COSMOS_THROUGHPUT=1000000

# Per-request end-to-end timeout in seconds, passed as the `timeout` kwarg on
# every timed operation. Unset or <= 0 means each backend keeps its own default
# (about 65 s per attempt on core-python, about 6 s end-to-end on Rust). Set the
# same value on both runs so a tail difference reflects the SDK, not the timeout.
# Sub-second values clamp to a 1 s floor on the Rust path.
REQUEST_TIMEOUT = _safe_float(os.environ.get("COSMOS_REQUEST_TIMEOUT", "0"), 0.0)

# WORKLOAD_OPERATIONS picks which operations the loop runs: any subset of the six
# point operations, plus "query". Comma-separated, case-insensitive. "write" is
# an alias for "upsert".
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

# Open-loop arrival rate (ops/sec). Default 0 uses the closed-loop wave driver.
# When > 0, the async driver fires operations at this fixed rate without waiting
# for each wave, and times each from its intended start, so the tail includes
# time a request waited to be issued. Async path only.
WORKLOAD_ARRIVAL_RATE = _safe_float(os.environ.get("WORKLOAD_ARRIVAL_RATE", "0"), 0.0)
# Cap on in-flight operations in open-loop mode, so a stalled service cannot grow
# the backlog without bound and run the generator out of memory. The backlog still
# shows up as rising latency; this only bounds memory.
WORKLOAD_MAX_INFLIGHT = _safe_int(os.environ.get("WORKLOAD_MAX_INFLIGHT", "10000"), 10000)

# Freeze the garbage collector after warmup (gc.freeze stops existing objects from
# being rescanned). Default off. Turn on to keep GC pauses out of the latency
# tail; leave off to measure the SDK as it really runs.
WORKLOAD_GC_FREEZE = os.environ.get("WORKLOAD_GC_FREEZE", "false").lower() == "true"

# Event-loop lag monitor (async only). Default on: a background task samples how
# late the loop services a timer and reports the worst value per window as
# loop_lag_max_ms, so a saturated loop is visible. Set false to disable.
WORKLOAD_LOOP_LAG_MONITOR = (
    os.environ.get("WORKLOAD_LOOP_LAG_MONITOR", "true").lower() == "true"
)

# When true, the client is created without a context manager (no automatic close),
# to model applications that do not close the Cosmos client.
WORKLOAD_SKIP_CLOSE = os.environ.get("WORKLOAD_SKIP_CLOSE", "false").lower() == "true"

# Blended traffic. WORKLOAD_MIX="read=70,create=10,upsert=10,replace=5,patch=5"
# makes one process issue a weighted BLEND of operations (a realistic app mix)
# instead of running each operation as its own phase, so a run can be gated on a
# single blended p99. Empty (default) keeps the per-operation phase behaviour.
# Weights are relative (need not sum to 100). "write" is an alias for "upsert";
# "query" is not part of a latency blend and is ignored if listed.
WORKLOAD_MIX = {}
_raw_mix = os.environ.get("WORKLOAD_MIX", "").strip()
if _raw_mix:
    for _pair in _raw_mix.split(","):
        _pair = _pair.strip()
        if not _pair:
            continue
        _k, _sep, _v = _pair.partition("=")
        _k = _OPERATION_ALIASES.get(_k.strip().lower(), _k.strip().lower())
        _w = _safe_float(_v, 0.0)
        if _k not in _VALID_OPERATIONS:
            raise ValueError(
                f"Unknown op in WORKLOAD_MIX: {_k!r}. Valid: {sorted(_VALID_OPERATIONS)} "
                f"(plus 'write' as an alias for 'upsert')."
            )
        if _w > 0:
            WORKLOAD_MIX[_k] = WORKLOAD_MIX.get(_k, 0.0) + _w
    # "query" carries no latency target and is not runnable in a blended wave, so a
    # mix of only query (or only zero-weight entries) has nothing to run. Reject it
    # up front: otherwise the closed-loop blended path would spin with no work and
    # record nothing.
    if _raw_mix and not any(_k != "query" for _k in WORKLOAD_MIX):
        raise ValueError(
            f"WORKLOAD_MIX={_raw_mix!r} has no runnable operation (only 'query' or "
            f"zero weights). Include at least one of read/create/upsert/replace/"
            f"delete/patch with a positive weight."
        )

# Document size/shape profile for GENERATED item bodies (create/upsert/replace/
# patch). "default" is the 732-byte flat document. "large" is a bigger, nested
# shape (4,670 bytes with nested objects and arrays, roughly 6.4x the default) so
# a run can check whether the latency/RU conclusions hold beyond one document
# shape. "nested" is an alias for "large" and generates the identical body. Both
# sizes are means over 200,000 generated documents. Reads return whatever already
# exists in the container, so a read-side size test needs the container seeded
# with that profile separately.
WORKLOAD_DOC_PROFILE = os.environ.get("WORKLOAD_DOC_PROFILE", "default").strip().lower()
_VALID_DOC_PROFILES = {"default", "large", "nested"}
if WORKLOAD_DOC_PROFILE not in _VALID_DOC_PROFILES:
    raise ValueError(
        "Unknown WORKLOAD_DOC_PROFILE: "
        f"{WORKLOAD_DOC_PROFILE!r}. Valid: {sorted(_VALID_DOC_PROFILES)}."
    )
