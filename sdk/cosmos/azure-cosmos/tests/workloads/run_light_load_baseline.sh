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
#   source ./profiling_activate.sh                              # required first
#   ./run_light_load_baseline.sh 480                         # core-python + rust
#   BASELINE_BACKENDS=rust ./run_light_load_baseline.sh 480  # rust only
# Override the verified default only when intentionally testing a different rate:
#   BASELINE_READ_RPS=100 ./run_light_load_baseline.sh 480
# The baseline measures a dedicated low-load probe container, lat_probe_db/
# lat_probe_cont, not the session target; override with BASELINE_DATABASE and
# BASELINE_CONTAINER, and re-check BASELINE_READ_RPS against that container's
# throughput if you do.
# Results use the active profiling session's RUN_ID and land in
# perfdb/perfresults-v2 tagged
# PERF_WORKLOAD_ID=baseline-<op>-<backend>-<run-id>; read them with latency_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ./profiling_common.sh
profiling_load_env || exit 2
: "${RUN_ID:?source ./profiling_activate.sh before running the baseline}"
: "${ARTIFACTS:?source ./profiling_activate.sh before running the baseline}"
profiling_load_session "${ARTIFACTS}" || exit 2

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

LOG_DIR="${ARTIFACTS}/light-load-baseline-${RUN_ID}"
mkdir -p "$LOG_DIR"

# The isolated probe container keeps this off the loaded phases' data, and its
# 400-RU/s budget is what the default 250 reads/s is sized against. Seed it once
# with initial-setup.py (same BASELINE_DATABASE/BASELINE_CONTAINER overrides) so
# read/replace/delete/patch have existing items to touch.
#
# profiling_load_session has just verified the session manifest against the
# ACTIVE target, so silently pointing the run somewhere else would mean the
# validated target and the measured one are different containers. The probe
# target is therefore overridable, and any divergence from the session target is
# announced rather than assumed.
BASELINE_DATABASE="${BASELINE_DATABASE:-lat_probe_db}"
BASELINE_CONTAINER="${BASELINE_CONTAINER:-lat_probe_cont}"
if [[ "${BASELINE_DATABASE}" != "${COSMOS_DATABASE:-}" ||
      "${BASELINE_CONTAINER}" != "${COSMOS_CONTAINER:-}" ]]; then
  echo "NOTE: the baseline measures ${BASELINE_DATABASE}/${BASELINE_CONTAINER}," >&2
  echo "      not the session target ${COSMOS_DATABASE:-unset}/${COSMOS_CONTAINER:-unset}." >&2
  echo "      That is the dedicated low-load probe container; ${BASELINE_READ_RPS}" >&2
  echo "      reads/s is sized against its 400-RU/s budget. Set BASELINE_DATABASE" >&2
  echo "      and BASELINE_CONTAINER to measure the session target instead, and" >&2
  echo "      re-check the arrival rate against that container's throughput." >&2
fi
export COSMOS_DATABASE="${BASELINE_DATABASE}"
export COSMOS_CONTAINER="${BASELINE_CONTAINER}"
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
# The pacing this baseline depends on lives only in the async open-loop path
# (workload.py). The sync client ignores WORKLOAD_ARRIVAL_RATE and runs a closed
# loop, yet the reporter still stamps config_arrival_rate from the environment --
# so an inherited WORKLOAD_USE_SYNC=true would publish an unpaced run labelled as
# a scheduled one. Pin it rather than inherit it.
export WORKLOAD_USE_SYNC=false
export WORKLOAD_ARRIVAL_RATE="${BASELINE_READ_RPS}"
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL=60

# Persist the exact data target used by this child process. The parent shell
# does not inherit exports from `bash ./run_light_load_baseline.sh`, so the
# later transport proof reads this file to avoid proving a different container.
BASELINE_TARGET_FILE="${LOG_DIR}/baseline-target.env"
{
  printf 'BASELINE_DATABASE=%q\n' "${BASELINE_DATABASE}"
  printf 'BASELINE_CONTAINER=%q\n' "${BASELINE_CONTAINER}"
  printf 'BASELINE_PARTITION_KEY=%q\n' "${COSMOS_PARTITION_KEY:-id}"
} >"${BASELINE_TARGET_FILE}"
write_run_manifest "${LOG_DIR}" "${RUN_ID}" "light-load-baseline"

echo "=== Rate-limited point-read latency baseline ==="
echo "    run_id=${RUN_ID} dur=${DURATION}s rate=${BASELINE_READ_RPS} reads/s backends=${BACKENDS[*]}"
echo "    container=${BASELINE_DATABASE}/${BASELINE_CONTAINER}  results -> perfdb/perfresults-v2 (workload_id LIKE baseline-%)"
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
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
if python3 perf_validate.py --run-id "${RUN_ID}" --log-dir "${LOG_DIR}" \
  --prefix "baseline-" --required-backends "${BACKEND_CSV}"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect rows/logs before trusting the baseline." >&2
  overall_rc=1
fi
echo "=== Checking the point-read p99 gate ==="
if python3 latency_report.py --prefix "baseline-" --run-id "${RUN_ID}" \
  --point-read-gate --expected-rps "${BASELINE_READ_RPS}" --max-p99-ms 10 \
  --gate-backends "${BACKEND_CSV}" \
  | tee "${LOG_DIR}/latency-report.txt"; then
  echo "=== point-read p99 gate PASSED ==="
else
  echo "!! point-read p99 gate FAILED -- do not use this run as the low-load baseline." >&2
  overall_rc=1
fi
exit "${overall_rc}"
