#!/usr/bin/env bash
# Phase 0: light-load latency baseline probe. conc=1, arrival=0, 1 client, no proxy.
# At concurrency 1 there is no client-side queue, so measured latency = one round trip
# (service latency), NOT the saturated closed-loop residence time Phase A reported.
#
# Purpose: validate the test environment before any A/B claim. A point-op baseline
# should land near p99 10 ms in-region; if it does not, throughput/latency numbers
# from the loaded phases are not meaningful as an SLA reference.
#
# Backend is selectable so the same probe runs both engines:
#   ./run_phase0_probe.sh 480                         # core-python + rust (default)
#   PHASE0_BACKENDS=rust ./run_phase0_probe.sh 480    # rust
# Operations are selectable so a profiling run can isolate one call path:
#   PHASE0_OPERATIONS=read PHASE0_BACKENDS=rust ./run_phase0_probe.sh 480
# Results land in perfdb/perfresults tagged PERF_WORKLOAD_ID=lat0-<op>-<backend>-<stamp>;
# read them back with phase0_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1 || exit 1
source ~/venvs/perfdrill/bin/activate

DURATION="${1:-480}"
OPERATIONS=(${PHASE0_OPERATIONS:-read create upsert replace delete patch})
BACKENDS=(${PHASE0_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/phase0-${STAMP}"
mkdir -p "$LOG_DIR"

# The isolated probe container keeps this off the loaded phases' data. Seed it
# once with initial-setup.py (same COSMOS_DATABASE/COSMOS_CONTAINER overrides)
# so read/replace/delete/patch have existing items to touch.
export COSMOS_DATABASE=lat_probe_db
export COSMOS_CONTAINER=lat_probe_cont
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL=60
write_run_manifest "${LOG_DIR}" "${STAMP}" "phase0"

echo "=== Phase 0: light-load latency probe (conc=1) ==="
echo "    stamp=${STAMP} dur=${DURATION}s ops=${OPERATIONS[*]} backends=${BACKENDS[*]}"
echo "    container=lat_probe_db/lat_probe_cont  results -> perfdb/perfresults (workload_id LIKE lat0-%)"
echo
overall_rc=0

for op in "${OPERATIONS[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    wid="lat0-${op}-${bk}-${STAMP}"
    log="${LOG_DIR}/${wid}.log"
    echo ">>> op=${op} backend=${bk} -> ${wid}"
    # timeout sends SIGINT so the workload stops the same way a Ctrl-C would,
    # letting the reporter flush one final row; --kill-after escalates if a cell
    # ever swallows the signal so one wedged cell cannot stall the whole probe.
    if COSMOS_BACKEND="${bk}" WORKLOAD_OPERATIONS="${op}" PERF_WORKLOAD_ID="${wid}" \
      timeout --signal=INT --kill-after=120s --preserve-status "${DURATION}s" \
        python3 workload.py >"${log}" 2>&1; then
      rc=0
    else
      rc=$?
    fi
    echo "    rc=${rc}  log=${log}"
    case "${rc}" in
      0)   ;;
      130) echo "    !! run exited 130 (SIGINT fell back to KeyboardInterrupt; data likely OK but handler did not engage)" >&2 ;;
      137|124) overall_rc=1 ;;
      *)   overall_rc=1 ;;
    esac
  done
done
echo "=== Phase 0 complete. stamp=${STAMP} ==="
echo "=== Running post-run integrity gate (Phase 0) ==="
if python3 perf_validate.py --stamp "${STAMP}" --log-dir "${LOG_DIR}" --prefix "lat0-"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect rows/logs before trusting Phase 0." >&2
  overall_rc=1
fi
exit "${overall_rc}"
