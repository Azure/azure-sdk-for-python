#!/usr/bin/env bash
# Measure first timed SDK calls after client construction/entry, not total startup.
# Each fresh process gets its own workload ID. Repeated cold snapshots are
# deduplicated by process identity; concurrency is one to preserve call order.
#
#   ./run_coldstart.sh 25                          # 25 processes/cell, core-python + rust
#   COLD_BACKENDS=rust ./run_coldstart.sh 25        # rust
#   COLD_BACKENDS="core-python rust" ./run_coldstart.sh 25
# Results land in perfdb/perfresults-v2 tagged cold-<op>-<backend>-<stamp>;
# read them back with coldstart_report.py.
set -euo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1
source ~/venvs/perfdrill/bin/activate
perf_single_operation_shape

ITERATIONS="${1:-25}"
PROC_SECONDS="${COLD_PROC_SECONDS:-8}"
perf_require_positive "${ITERATIONS}" "${PROC_SECONDS}"
# delete is excluded: delete_item_concurrently does untimed setup creates before the
# timed delete, so its first timed call already runs on a warmed client and is not a
# comparable first timed call. Other operations may still have lazy setup.
OPERATIONS=(read create upsert replace patch)
BACKENDS=(${COLD_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/cold-${STAMP}"
perf_create_log_dir "$LOG_DIR" || exit 2

# Seeded probe container so read/replace/delete/patch have existing items to touch.
# Always target the probe container by default. perf_env.sh exports scale_db/scale_cont,
# so using ${COSMOS_DATABASE:-...} here would silently keep the wrong target.
export COSMOS_DATABASE="${COLD_COSMOS_DATABASE:-lat_probe_db}"
export COSMOS_CONTAINER="${COLD_COSMOS_CONTAINER:-lat_probe_cont}"
# Low concurrency so the first call is a clean single round trip, not queued.
# Use a dedicated override var so perf_env's default (100) does not silently
# leak into cold-start runs.
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
# One flush per process: interval must exceed the per-process duration so the only
# report is the final one (= that process's single cold sample).
export COSMOS_MAX_ITEM_INDEX="${COLD_MAX_ITEM_INDEX:-1000}"
export PERF_REPORT_INTERVAL="$(( PROC_SECONDS + 60 ))"
write_run_manifest "${LOG_DIR}" "${STAMP}" "cold-first-call"
for op in "${OPERATIONS[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    for (( i=1; i<=ITERATIONS; i++ )); do printf 'cold-%s-%s-r%s-%s\n' "$op" "$bk" "$i" "$STAMP"; done
  done
done >"${LOG_DIR}/expected-workloads.txt"

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
      wid="cold-${op}-${bk}-r${i}-${STAMP}"
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
echo "=== Running cold-start report + driver commit check ==="
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
perf_check_run "${LOG_DIR}" "${STAMP}" "cold-" "${BACKEND_CSV}" || overall_rc=1
# Lightweight post-run gate for this mini-phase: validate the Rust driver commit
# and print first-call pooled distributions for this stamp.
if python3 coldstart_report.py --prefix "cold-" --stamp "${STAMP}"; then
  echo "=== cold-start report driver commit check PASSED ==="
else
  echo "!! cold-start report driver commit check FAILED -- inspect rows before trusting cold metrics." >&2
  overall_rc=1
fi
exit "${overall_rc}"
