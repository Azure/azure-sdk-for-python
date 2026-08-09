#!/usr/bin/env bash
# Cold-start run: measure the latency an application pays on its FIRST calls after
# a process starts, which every warm phase hides. Starts MANY short processes, each
# doing only a few operations before exiting; each contributes one first-call
# sample plus a short warm-up curve.
#
# Why: a customer running short-lived workers pays the client/pool/TLS (and, for
# Rust, the Tokio runtime) setup on the critical path of the first call. If one
# engine has a heavier startup tail, that is an SLA risk warm numbers never show.
#
# How it works: each process runs a SHORT duration with PERF_REPORT_INTERVAL far
# larger than that duration, so there is exactly ONE final flush = ONE cold sample
# per process. All iterations of an (op,backend) share ONE workload_id so the
# reader can pool them; distinct rows come from each process's own row uuid.
#
#   ./run_coldstart.sh 25                          # 25 processes/cell, core-python + rust
#   COLD_BACKENDS=rust ./run_coldstart.sh 25        # rust
#   COLD_BACKENDS="core-python rust" ./run_coldstart.sh 25
# Results land in perfdb/perfresults-v2 tagged cold-<op>-<backend>-<stamp>;
# read them back with coldstart_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1
source ~/venvs/perfdrill/bin/activate

ITERATIONS="${1:-25}"
PROC_SECONDS="${COLD_PROC_SECONDS:-8}"
# delete is excluded: delete_item_concurrently does untimed setup creates before the
# timed delete, so its first timed call already runs on a warmed client and is not a
# clean cold sample. read/create/upsert/replace/patch hit the service cold on call 1.
OPERATIONS=(read create upsert replace patch)
BACKENDS=(${COLD_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/cold-${STAMP}"
mkdir -p "$LOG_DIR"

# Seeded probe container so read/replace/delete/patch have existing items to touch.
# Always target the probe container by default. perf_env.sh exports scale_db/scale_cont,
# so using ${COSMOS_DATABASE:-...} here would silently keep the wrong target.
export COSMOS_DATABASE="${COLD_COSMOS_DATABASE:-lat_probe_db}"
export COSMOS_CONTAINER="${COLD_COSMOS_CONTAINER:-lat_probe_cont}"
# Low concurrency so the first call is a clean single round trip, not queued.
# Use a dedicated override var so perf_env's default (100) does not silently
# leak into cold-start runs.
export COSMOS_CONCURRENT_REQUESTS="${COLD_CONCURRENT_REQUESTS:-1}"
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
# One flush per process: interval must exceed the per-process duration so the only
# report is the final one (= that process's single cold sample).
export PERF_REPORT_INTERVAL=300

echo "=== Cold-start run (first-call latency) ==="
echo "    stamp=${STAMP} iterations/cell=${ITERATIONS} proc_seconds=${PROC_SECONDS}s"
echo "    ops=${OPERATIONS[*]} backends=${BACKENDS[*]}"
echo "    container=${COSMOS_DATABASE}/${COSMOS_CONTAINER}  results -> perfdb/perfresults-v2 (cold-%)"
echo
overall_rc=0

for op in "${OPERATIONS[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    wid="cold-${op}-${bk}-${STAMP}"
    echo ">>> op=${op} backend=${bk} -> ${wid}  (${ITERATIONS} processes)"
    for i in $(seq 1 "${ITERATIONS}"); do
      log="${LOG_DIR}/${wid}-p$(printf '%03d' "${i}").log"
      if COSMOS_BACKEND="${bk}" WORKLOAD_OPERATIONS="${op}" PERF_WORKLOAD_ID="${wid}" \
        timeout --signal=INT --kill-after=30s --preserve-status "${PROC_SECONDS}s" \
          python3 workload.py >"${log}" 2>&1; then
        rc=0
      else
        rc=$?
      fi
      if [[ "${rc}" -ne 0 ]]; then
        overall_rc=1
      fi
    done
    echo "    done: ${ITERATIONS} processes"
  done
done
echo "=== Cold-start run complete. stamp=${STAMP} ==="
echo
echo "=== Running cold-start report + provenance gate ==="
# Lightweight post-run gate for this mini-phase: validate Rust driver provenance
# and print first-call pooled distributions for this stamp.
if python3 coldstart_report.py --prefix "cold-" --stamp "${STAMP}"; then
  echo "=== cold-start report provenance gate PASSED ==="
else
  echo "!! cold-start report provenance gate FAILED -- inspect rows before trusting cold metrics." >&2
  overall_rc=1
fi
exit "${overall_rc}"
