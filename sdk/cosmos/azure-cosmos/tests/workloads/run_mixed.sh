#!/usr/bin/env bash
# Blended (mixed) workload run: one process issues a realistic MIX of operations
# instead of one operation type at a time, so we can gate on a single BLENDED p99
# — the latency a customer's SLA actually feels.
#
# Why: the per-op phases each measure the fastest case for that op in isolation.
# Real traffic is mostly reads with some writes; the blended p99 is what matters.
#
#   ./run_mixed.sh 900                          # core-python + rust (default)
#   MIXED_BACKENDS=rust ./run_mixed.sh 900       # rust
#   MIXED_BACKENDS="core-python rust" ./run_mixed.sh 900
# Mix defaults to a read-heavy app profile; override with WORKLOAD_MIX.
# Results land in perfdb/perfresults-v2 tagged mixed-blend-<backend>-<stamp>;
# read them back with mixed_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1
source ~/venvs/perfdrill/bin/activate

DURATION="${1:-900}"
BACKENDS=(${MIXED_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/mixed-${STAMP}"
mkdir -p "$LOG_DIR"

# Read-heavy realistic mix. Weights are relative (need not sum to 100).
export WORKLOAD_MIX="${WORKLOAD_MIX:-read=70,upsert=15,create=5,replace=5,patch=5}"
# Use the seeded probe container so reads/replace/patch have existing items.
export COSMOS_DATABASE="${MIXED_COSMOS_DATABASE:-lat_probe_db}"
export COSMOS_CONTAINER="${MIXED_COSMOS_CONTAINER:-lat_probe_cont}"
export COSMOS_CONCURRENT_REQUESTS="${COSMOS_CONCURRENT_REQUESTS:-100}"
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL="${PERF_REPORT_INTERVAL:-60}"

echo "=== Mixed/blended workload run ==="
echo "    stamp=${STAMP} dur=${DURATION}s backends=${BACKENDS[*]}"
echo "    mix=${WORKLOAD_MIX}  concurrency=${COSMOS_CONCURRENT_REQUESTS}"
echo "    container=${COSMOS_DATABASE}/${COSMOS_CONTAINER}  results -> perfdb/perfresults-v2 (mixed-%)"
echo
overall_rc=0

for bk in "${BACKENDS[@]}"; do
  wid="mixed-blend-${bk}-${STAMP}"
  log="${LOG_DIR}/${wid}.log"
  echo ">>> backend=${bk} -> ${wid}"
  # timeout sends SIGINT so the reporter flushes one final row; --kill-after
  # escalates if the process ever swallows the signal.
  if COSMOS_BACKEND="${bk}" PERF_WORKLOAD_ID="${wid}" \
    timeout --signal=INT --kill-after=120s --preserve-status "${DURATION}s" \
      python3 workload.py >"${log}" 2>&1; then
    rc=0
  else
    rc=$?
  fi
  echo "    rc=${rc}  log=${log}"
  if [[ "${rc}" -ne 0 ]]; then
    overall_rc=1
  fi
done
echo "=== Mixed run complete. stamp=${STAMP} ==="
echo
echo "=== Running mixed report + provenance gate ==="
# Lightweight post-run gate for this mini-phase: validate the single-build Rust
# provenance and print blended/per-op pooled latency from the just-finished stamp.
if python3 mixed_report.py --prefix "mixed-" --stamp "${STAMP}"; then
  echo "=== mixed report provenance gate PASSED ==="
else
  echo "!! mixed report provenance gate FAILED -- inspect rows before trusting mixed metrics." >&2
  overall_rc=1
fi
exit "${overall_rc}"
