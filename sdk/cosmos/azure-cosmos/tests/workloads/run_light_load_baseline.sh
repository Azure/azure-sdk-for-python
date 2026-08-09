#!/usr/bin/env bash
# Rate-limited point-read latency baseline. One client, 250 reads/s by default,
# no proxy. The fixed arrival rate keeps this 1-RU read workload below the
# dedicated probe container's 400-RU/s budget. An unpaced closed loop is not a
# low-load test: it sends the next read immediately and can saturate the account.
#
# Purpose: validate the test environment before any A/B claim. A point-op baseline
# should land near p99 10 ms in-region; if it does not, throughput/latency numbers
# from the loaded phases are not meaningful as an SLA reference.
#
# Backend is selectable so the same probe runs both engines:
#   ./run_light_load_baseline.sh 480                         # core-python + rust
#   BASELINE_BACKENDS=rust ./run_light_load_baseline.sh 480  # rust only
# Override the verified default only when intentionally testing a different rate:
#   BASELINE_READ_RPS=100 ./run_light_load_baseline.sh 480
# Results land in perfdb/perfresults-v2 tagged
# PERF_WORKLOAD_ID=baseline-<op>-<backend>-<run-id>; read them with latency_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1 || exit 1
source ~/venvs/perfdrill/bin/activate

DURATION="${1:-480}"
OPERATIONS=(${BASELINE_OPERATIONS:-read})
BACKENDS=(${BASELINE_BACKENDS:-core-python rust})
BASELINE_READ_RPS="${BASELINE_READ_RPS:-250}"

if [[ "${OPERATIONS[*]}" != "read" ]]; then
  echo "ERROR: the low-load p99 gate supports BASELINE_OPERATIONS=read only." >&2
  exit 2
fi
if ! [[ "${BASELINE_READ_RPS}" =~ ^[0-9]+([.][0-9]+)?$ ]] ||
   ! awk -v rate="${BASELINE_READ_RPS}" 'BEGIN { exit !(rate > 0) }'; then
  echo "ERROR: BASELINE_READ_RPS must be a positive number; got '${BASELINE_READ_RPS}'." >&2
  exit 2
fi

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
RUN_ID="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/light-load-baseline-${RUN_ID}"
mkdir -p "$LOG_DIR"

# The isolated probe container keeps this off the loaded phases' data. Seed it
# once with initial-setup.py (same COSMOS_DATABASE/COSMOS_CONTAINER overrides)
# so read/replace/delete/patch have existing items to touch.
export COSMOS_DATABASE=lat_probe_db
export COSMOS_CONTAINER=lat_probe_cont
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE="${BASELINE_READ_RPS}"
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL=60
write_run_manifest "${LOG_DIR}" "${RUN_ID}" "light-load-baseline"

echo "=== Rate-limited point-read latency baseline ==="
echo "    run_id=${RUN_ID} dur=${DURATION}s rate=${BASELINE_READ_RPS} reads/s backends=${BACKENDS[*]}"
echo "    container=lat_probe_db/lat_probe_cont  results -> perfdb/perfresults-v2 (workload_id LIKE baseline-%)"
echo
overall_rc=0

for op in "${OPERATIONS[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    wid="baseline-${op}-${bk}-${RUN_ID}"
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
echo "=== Light-load baseline complete. run_id=${RUN_ID} ==="
echo "=== Checking the light-load baseline results ==="
if python3 perf_validate.py --run-id "${RUN_ID}" --log-dir "${LOG_DIR}" --prefix "baseline-"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect rows/logs before trusting the baseline." >&2
  overall_rc=1
fi
echo "=== Checking the point-read p99 gate ==="
if python3 latency_report.py --prefix "baseline-" --run-id "${RUN_ID}" \
  --point-read-gate --expected-rps "${BASELINE_READ_RPS}" --max-p99-ms 10 \
  | tee "${LOG_DIR}/latency-report.txt"; then
  echo "=== point-read p99 gate PASSED ==="
else
  echo "!! point-read p99 gate FAILED -- do not use this run as the low-load baseline." >&2
  overall_rc=1
fi
exit "${overall_rc}"
