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
# Inclusive highest item-id suffix. A value of 10000 uses test-0 through
# test-10000, so setup creates 10001 items.
export COSMOS_MAX_ITEM_INDEX="${COSMOS_MAX_ITEM_INDEX:-10000}"
# RU/s for scale_cont. Size so a short run shows NO steady 429s -- a 429 is the
# account being RU-limited, not the SDK being slow. 100k suits a single read-heavy
# sequential run; raise to 200k-400k if the parallel leak sweep (6 ops at once on
# one container) shows steady 429s on the write phases.
export COSMOS_THROUGHPUT="${COSMOS_THROUGHPUT:-100000}"
# The VM's region, listed first, so the client prefers the local replica.
export COSMOS_PREFERRED_LOCATIONS="${COSMOS_PREFERRED_LOCATIONS:-West US 2}"

# ---- Driver provenance (computed ONCE, inherited by every child) ----------
# The exact azure-sdk-for-rust DRIVER commit the binding was built against. We
# resolve the sibling clone and export it here so every process in a run -- incl.
# the N children of a scale-out point -- stamps the SAME driver commit on its rows
# without each one shelling out to git (and so a mid-run rebuild can't split one
# run's provenance). perf_config.py falls back to resolving it per process when
# this is unset. Best-effort: a missing clone/git must never fail a run.
if [[ -z "${PERF_DRIVER_COMMIT:-}" ]]; then
  _hdir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
  _driver_dir="${AZURE_SDK_FOR_RUST_DIR:-}"
  if [[ -z "${_driver_dir}" ]]; then
    # Prefer the git top-level of THIS (azure-sdk-for-python) clone, then its
    # sibling azure-sdk-for-rust -- robust to cwd and to the exact nesting depth.
    # Fall back to a fixed-depth relative path if this is not a git checkout.
    _pyroot="$(git -C "${_hdir}" rev-parse --show-toplevel 2>/dev/null || echo "")"
    if [[ -n "${_pyroot}" ]]; then
      _driver_dir="${_pyroot}/../azure-sdk-for-rust"
    else
      _driver_dir="${_hdir}/../../../../../../azure-sdk-for-rust"
    fi
  fi
  PERF_DRIVER_COMMIT="$(git -C "${_driver_dir}" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  export PERF_DRIVER_COMMIT
  unset _hdir _driver_dir _pyroot
fi

# ---- Load shape (identical for both backends) -----------------------------
export WORKLOAD_NUM_CLIENTS="${WORKLOAD_NUM_CLIENTS:-1}"          # one client per process -> clean per-op attribution
export COSMOS_CONCURRENT_REQUESTS="${COSMOS_CONCURRENT_REQUESTS:-100}"  # point ops in flight per client
export WORKLOAD_USE_SYNC="${WORKLOAD_USE_SYNC:-false}"            # async path (sync is serial -> not for load)
# Per-op end-to-end timeout, in seconds, PINNED THE SAME on both backends so the
# slowest calls compare fairly. Without a pin each backend keeps its own default
# (legacy ~65s/attempt vs Rust ~6s end-to-end), which are not comparable. 30s is a
# deliberate middle ground; override by exporting COSMOS_REQUEST_TIMEOUT before
# sourcing. (Rust clamps sub-second values up to a 1s floor.)
export COSMOS_REQUEST_TIMEOUT="${COSMOS_REQUEST_TIMEOUT:-30}"

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
# A separate account is safest, but a separate container with its own throughput
# in the same account is acceptable (the reporter writes only a handful of docs
# per interval). We default to the same account, a separate perfdb/perfresults-v2.
export PERF_ENABLED="${PERF_ENABLED:-true}"
export RESULTS_COSMOS_URI="${RESULTS_COSMOS_URI:-$COSMOS_URI}"
export RESULTS_COSMOS_DATABASE="${RESULTS_COSMOS_DATABASE:-perfdb}"
export RESULTS_COSMOS_CONTAINER="${RESULTS_COSMOS_CONTAINER:-perfresults-v2}"
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

# ---- Run manifest (post-hoc reproducibility / apples-to-apples audit) ------
# WHY: a row's numbers are only trustworthy if we can later PROVE which code,
# host, container and load policy produced them. The reporter now stamps the
# load-shape config on every row, but the BUILD and HOST provenance (commit, the
# Rust extension actually loaded, rustc/python versions, the VM and its core
# count, the RU budget) live nowhere in the rows. write_run_manifest captures all
# of that ONCE per run into the log dir, next to the per-cell logs, so a future
# auditor can confirm two runs were truly comparable. Secrets are never written.
# Usage:  write_run_manifest "<log_dir>" "<stamp>" "<phase>"
write_run_manifest() {
  local log_dir="$1" stamp="$2" phase="${3:-unknown}"
  local out="${log_dir}/manifest-${stamp}.json"
  mkdir -p "${log_dir}" 2>/dev/null || true
  # All probes are best-effort: a missing tool must never abort a 22h run.
  local git_sha git_branch git_dirty rustc_ver py_ver cosmos_ver ext_ver ext_path
  local ext_mtime kernel host nproc_n mem_kb vm_sku vm_zone now_utc
  local driver_dir driver_sha driver_branch driver_dirty _drv_root
  git_sha="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse HEAD 2>/dev/null || echo unknown)"
  git_branch="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  if git -C "$(dirname "${BASH_SOURCE[0]}")" diff --quiet 2>/dev/null; then git_dirty=false; else git_dirty=true; fi
  # The azure-sdk-for-rust DRIVER commit. git_sha above is THIS repo (harness +
  # binding); the driver we build from is a sibling clone (see
  # azure_cosmos_rust/Cargo.toml path dep). Resolve it via this clone's git
  # top-level then its sibling (robust to cwd/depth), falling back to a
  # fixed-depth relative path. AZURE_SDK_FOR_RUST_DIR overrides. Record its HEAD
  # so the manifest proves which driver the run actually built against.
  driver_dir="${AZURE_SDK_FOR_RUST_DIR:-}"
  if [[ -z "${driver_dir}" ]]; then
    _drv_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel 2>/dev/null || echo "")"
    if [[ -n "${_drv_root}" ]]; then
      driver_dir="${_drv_root}/../azure-sdk-for-rust"
    else
      driver_dir="$(dirname "${BASH_SOURCE[0]}")/../../../../../../azure-sdk-for-rust"
    fi
  fi
  driver_sha="$(git -C "${driver_dir}" rev-parse HEAD 2>/dev/null || echo unknown)"
  driver_branch="$(git -C "${driver_dir}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  if git -C "${driver_dir}" diff --quiet 2>/dev/null; then driver_dirty=false; else driver_dirty=true; fi
  rustc_ver="$(rustc --version 2>/dev/null || echo unknown)"
  py_ver="$(python3 -c 'import platform;print(platform.python_version())' 2>/dev/null || echo unknown)"
  cosmos_ver="$(python3 -c 'import azure.cosmos as c;print(getattr(c,"__version__","unknown"))' 2>/dev/null || echo unknown)"
  # The Rust extension actually importable (proves WHICH binding build is live)
  # and whether it carries the provenance counter (operation_count).
  ext_ver="$(python3 -c 'from azure.cosmos import _rust;print(getattr(_rust,"__version__","unknown"))' 2>/dev/null || echo none)"
  local ext_has_counter
  ext_has_counter="$(python3 -c 'from azure.cosmos import _rust;print(hasattr(_rust,"operation_count"))' 2>/dev/null || echo unknown)"
  ext_path="$(python3 -c 'from azure.cosmos import _rust;print(_rust.__file__)' 2>/dev/null || echo none)"
  ext_mtime="$( [ -f "${ext_path}" ] && date -u -r "${ext_path}" +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo none)"
  kernel="$(uname -srm 2>/dev/null || echo unknown)"
  host="$(hostname 2>/dev/null || echo unknown)"
  nproc_n="$(nproc 2>/dev/null || echo unknown)"
  mem_kb="$(awk '/MemTotal/{print $2}' /proc/meminfo 2>/dev/null || echo unknown)"
  # Azure IMDS (no secret): VM size + zone, so the host SKU is on the record.
  vm_sku="$(curl -s -H Metadata:true --max-time 2 'http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2021-02-01&format=text' 2>/dev/null || echo unknown)"
  vm_zone="$(curl -s -H Metadata:true --max-time 2 'http://169.254.169.254/metadata/instance/compute/zone?api-version=2021-02-01&format=text' 2>/dev/null || echo unknown)"
  now_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo unknown)"
  cat > "${out}" <<EOF
{
  "phase": "${phase}",
  "stamp": "${stamp}",
  "created_utc": "${now_utc}",
  "build": {
    "git_commit": "${git_sha}",
    "git_branch": "${git_branch}",
    "git_dirty": ${git_dirty},
    "rust_driver_commit": "${driver_sha}",
    "rust_driver_branch": "${driver_branch}",
    "rust_driver_dirty": ${driver_dirty},
    "rustc": "${rustc_ver}",
    "python": "${py_ver}",
    "azure_cosmos": "${cosmos_ver}",
    "rust_extension_version": "${ext_ver}",
    "rust_extension_has_provenance_counter": "${ext_has_counter}",
    "rust_extension_path": "${ext_path}",
    "rust_extension_mtime_utc": "${ext_mtime}"
  },
  "host": {
    "hostname": "${host}",
    "kernel": "${kernel}",
    "nproc": "${nproc_n}",
    "mem_total_kb": "${mem_kb}",
    "vm_size": "${vm_sku}",
    "vm_zone": "${vm_zone}"
  },
  "account": {
    "uri": "${COSMOS_URI}",
    "database": "${COSMOS_DATABASE}",
    "container": "${COSMOS_CONTAINER}",
    "throughput_ru": "${COSMOS_THROUGHPUT}",
    "preferred_locations": "${COSMOS_PREFERRED_LOCATIONS}",
    "client_excluded_locations": "${COSMOS_CLIENT_EXCLUDED_LOCATIONS:-}",
    "request_excluded_locations": "${COSMOS_REQUEST_EXCLUDED_LOCATIONS:-}"
  },
  "load": {
    "num_clients": "${WORKLOAD_NUM_CLIENTS}",
    "concurrent_requests": "${COSMOS_CONCURRENT_REQUESTS}",
    "request_timeout_s": "${COSMOS_REQUEST_TIMEOUT}",
    "arrival_rate": "${WORKLOAD_ARRIVAL_RATE}",
    "max_inflight": "${WORKLOAD_MAX_INFLIGHT}",
    "use_sync": "${WORKLOAD_USE_SYNC}",
    "gc_freeze": "${WORKLOAD_GC_FREEZE}",
    "multi_write": "${COSMOS_USE_MULTIPLE_WRITABLE_LOCATIONS:-false}",
    "report_interval_s": "${PERF_REPORT_INTERVAL}"
  },
  "results_sink": {
    "database": "${RESULTS_COSMOS_DATABASE}",
    "container": "${RESULTS_COSMOS_CONTAINER}"
  }
}
EOF
  echo "run manifest written: ${out}"
  if [[ "${ext_has_counter}" != "True" && "${COSMOS_BACKEND:-}" == "rust" ]]; then
    echo "    !! WARNING: rust backend selected but the loaded _rust extension has" >&2
    echo "       no operation_count() -- binding provenance will be UNKNOWN. Rebuild" >&2
    echo "       the extension before trusting 'rust' rows." >&2
  fi
}
