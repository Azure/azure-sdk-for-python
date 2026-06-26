#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Shared environment for the sdkdev-dikshi performance + memory-leak drill.
#
# This file holds every NON-SECRET setting both driver scripts share, so the
# baseline (core-python) and Rust runs differ by exactly one switch and nothing
# drifts between them. Source it; do not run it:
#
#     source ./perf_env.sh
#
# SECRETS ARE NOT STORED HERE. Export the two account keys yourself before
# sourcing (e.g. keep them in a private, git-ignored file you `source` first):
#
#     export COSMOS_KEY="...primary key of sdkdev-dikshi..."
#     export RESULTS_COSMOS_KEY="$COSMOS_KEY"   # same account for results, or a different one
#
# The block at the bottom hard-fails if either key is missing, so a run can
# never silently fall back to AAD (which would add token-refresh noise to the
# tail and make the two backends authenticate differently).
# ---------------------------------------------------------------------------

# ---- Account and data UNDER TEST ------------------------------------------
# The endpoint of the sdkdev-dikshi account (West US 2 write region == the VM's
# region, so we measure the SDK, not a cross-region hop).
export COSMOS_URI="${COSMOS_URI:-https://sdkdev-dikshi.documents.azure.com:443/}"
# A DEDICATED database/container created by initial-setup.py. We deliberately do
# NOT reuse openai-memdrill-db (the 1,000,000-RU memory-drill containers) or
# parity_db -- this drill stays fully isolated from that work.
export COSMOS_DATABASE="${COSMOS_DATABASE:-scale_db}"
export COSMOS_CONTAINER="${COSMOS_CONTAINER:-scale_cont}"
export COSMOS_PARTITION_KEY="${COSMOS_PARTITION_KEY:-id}"
export COSMOS_NUMBER_OF_LOGICAL_PARTITIONS="${COSMOS_NUMBER_OF_LOGICAL_PARTITIONS:-10000}"
# RU/s for scale_cont. Size so a short run shows NO steady 429s -- a 429 is the
# account being RU-limited, not the SDK being slow. 100k suits a single read-heavy
# sequential run; raise to 200k-400k if the parallel leak sweep (6 ops at once on
# one container) shows steady 429s on the write phases.
export COSMOS_THROUGHPUT="${COSMOS_THROUGHPUT:-100000}"
# The VM's region, listed first, so the client prefers the local replica.
export COSMOS_PREFERRED_LOCATIONS="${COSMOS_PREFERRED_LOCATIONS:-West US 2}"

# ---- Load shape (identical for both backends) -----------------------------
export WORKLOAD_NUM_CLIENTS="${WORKLOAD_NUM_CLIENTS:-1}"          # one client per process -> clean per-op attribution
export COSMOS_CONCURRENT_REQUESTS="${COSMOS_CONCURRENT_REQUESTS:-100}"  # point ops in flight per client
export WORKLOAD_USE_SYNC="${WORKLOAD_USE_SYNC:-false}"            # async path (sync is serial -> not for load)
# Per-op end-to-end timeout, in seconds. 0 = each backend keeps its own default,
# which makes the EXTREME tail incomparable (legacy ~65s/attempt vs Rust ~6s).
# Set the SAME non-zero value on BOTH runs to compare the tail fairly.
export COSMOS_REQUEST_TIMEOUT="${COSMOS_REQUEST_TIMEOUT:-0}"

# ---- Measurement quality switches -----------------------------------------
# Open-loop arrival rate (ops/sec PER CLIENT). 0 = closed-loop (default), which
# is uniform across all six ops. Set >0 to remove "coordinated omission" from the
# tail -- but it only applies to read/upsert/replace/patch; the matrix script
# automatically forces closed-loop for create/delete (the harness rejects them in
# open-loop). Pick a rate BELOW the ceiling you find with the concurrency sweep,
# or it just measures saturation.
export WORKLOAD_ARRIVAL_RATE="${WORKLOAD_ARRIVAL_RATE:-0}"
export WORKLOAD_MAX_INFLIGHT="${WORKLOAD_MAX_INFLIGHT:-10000}"   # open-loop safety cap so a stall can't OOM the rig
export WORKLOAD_GC_FREEZE="${WORKLOAD_GC_FREEZE:-false}"          # false = measure the SDK with GC as it really behaves
export WORKLOAD_LOOP_LAG_MONITOR="${WORKLOAD_LOOP_LAG_MONITOR:-true}"  # surface event-loop saturation as loop_lag_max_ms

# ---- Quiet the harness (logging is CPU + file-I/O that biases a perf run) --
export COSMOS_LOG_LEVEL="${COSMOS_LOG_LEVEL:-WARNING}"
export COSMOS_ENABLE_DIAGNOSTICS_LOGGING="${COSMOS_ENABLE_DIAGNOSTICS_LOGGING:-false}"

# ---- Results sink (separate database/container so it never competes) -------
# Per docs/RUST_PYTHON_SLA.md section 3: a separate account is safest, but a
# separate container WITH ITS OWN THROUGHPUT in the same account is acceptable
# (the reporter writes only a handful of docs per interval). We default to the
# same account, a separate perfdb/perfresults.
export PERF_ENABLED="${PERF_ENABLED:-true}"
export RESULTS_COSMOS_URI="${RESULTS_COSMOS_URI:-$COSMOS_URI}"
export RESULTS_COSMOS_DATABASE="${RESULTS_COSMOS_DATABASE:-perfdb}"
export RESULTS_COSMOS_CONTAINER="${RESULTS_COSMOS_CONTAINER:-perfresults}"
# One results row per interval. 300s (5 min) is the default; the long runs here
# span hours, so plenty of rows accumulate to drop warmup and read a settled tail.
export PERF_REPORT_INTERVAL="${PERF_REPORT_INTERVAL:-300}"

# ---- Guard: refuse to run without explicit key auth -----------------------
if [[ -z "${COSMOS_KEY:-}" ]]; then
  echo "ERROR: COSMOS_KEY is not set. Export the sdkdev-dikshi key before sourcing perf_env.sh." >&2
  echo "       (Key auth keeps both backends authenticating the same cheap way; AAD adds tail noise.)" >&2
  return 1 2>/dev/null || exit 1
fi
export COSMOS_KEY
export RESULTS_COSMOS_KEY="${RESULTS_COSMOS_KEY:-$COSMOS_KEY}"

echo "perf_env.sh sourced: account=${COSMOS_URI} db=${COSMOS_DATABASE} cont=${COSMOS_CONTAINER} region='${COSMOS_PREFERRED_LOCATIONS}'"
