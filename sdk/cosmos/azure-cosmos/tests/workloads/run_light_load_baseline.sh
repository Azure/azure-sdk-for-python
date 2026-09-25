#!/usr/bin/env bash
# Rate-limited point-read latency baseline. One client, 250 reads/s by default,
# no proxy. Check measured request charges against the test container's service
# capacity; 250 reads/s is not automatically below a 400-RU/s budget. Unpaced
# send-and-wait sends the next read immediately and can saturate the account.
#
# Purpose: validate the test environment before any A/B claim. A point-op baseline
# uses experiment-specific acceptance criteria, not a service SLA.
#
# Backend is selectable so the same probe runs both engines. The script loads
# the newest complete profiling session when the current shell has no active one:
#   ./run_light_load_baseline.sh 480                         # core-python + rust
#   BASELINE_BACKENDS=rust ./run_light_load_baseline.sh 480  # rust only
# Override the verified default only when intentionally testing a different rate:
#   BASELINE_READ_RPS=100 ./run_light_load_baseline.sh 480
# The baseline retains the validated profiling session's test target and item
# range. Prepare a new profiling session to change the database or container.
# Results use the active profiling session's RUN_ID and configured results container, tagged
# PERF_WORKLOAD_ID=baseline-<op>-<backend>-<run-id>; read them with latency_report.py.
set -uo pipefail
cd "$(dirname "$0")"
source ./profiling_common.sh
if [[ -n "${RUN_ID:-}" && -n "${ARTIFACTS:-}" ]]; then
  profiling_load_env || exit 2
  profiling_load_session "${ARTIFACTS}" || exit 2
else
  # Load the same environment and newest complete session that an operator would
  # get by sourcing profiling_activate.sh, but keep it local to this command.
  # shellcheck disable=SC1091
  source ./profiling_activate.sh || exit 2
fi
: "${RUN_ID:?no complete profiling session found; run profiling_start_session.sh first}"
: "${ARTIFACTS:?no complete profiling session found; run profiling_start_session.sh first}"

DURATION="${1:-480}"
perf_require_positive "${DURATION}" || exit 2
perf_single_operation_shape
OPERATIONS=(${BASELINE_OPERATIONS:-read})
BACKENDS=(${BASELINE_BACKENDS:-core-python rust})
BASELINE_READ_RPS="${BASELINE_READ_RPS:-${WORKLOAD_ARRIVAL_RATE}}"

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
perf_create_log_dir "$LOG_DIR" || exit 2
RUN_LOG="${LOG_DIR}/baseline-run.log"
REPORT_FILE="${LOG_DIR}/latency-report.txt"
exec > >(tee "${RUN_LOG}") 2>&1

BASELINE_DATABASE="${BASELINE_DATABASE:-${COSMOS_DATABASE}}"
BASELINE_CONTAINER="${BASELINE_CONTAINER:-${COSMOS_CONTAINER}}"
if [[ "${BASELINE_DATABASE}" != "${COSMOS_DATABASE:-}" ||
      "${BASELINE_CONTAINER}" != "${COSMOS_CONTAINER:-}" ]]; then
  echo "ERROR: baseline target differs from the validated profiling session." >&2
  echo "       Prepare and validate a new profiling session for the intended target." >&2
  exit 2
fi
export COSMOS_DATABASE="${BASELINE_DATABASE}"
export COSMOS_CONTAINER="${BASELINE_CONTAINER}"
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
# The pacing this baseline depends on lives only in the async fixed-rate path
# (workload.py). The sync client rejects a positive arrival rate. Pin async mode
# rather than inheriting a setting from a different experiment.
export WORKLOAD_USE_SYNC=false
export WORKLOAD_ARRIVAL_RATE="${BASELINE_READ_RPS}"
export WORKLOAD_USE_PROXY=false
# Keep the prepared item range, timeout and reporting interval.

# Persist the exact data target used by this child process. The parent shell
# does not inherit exports from `bash ./run_light_load_baseline.sh`, so the
# later transport proof reads this file to avoid proving a different container.
BASELINE_TARGET_FILE="${LOG_DIR}/baseline-target.env"
{
  printf 'BASELINE_DATABASE=%q\n' "${BASELINE_DATABASE}"
  printf 'BASELINE_CONTAINER=%q\n' "${BASELINE_CONTAINER}"
  printf 'BASELINE_PARTITION_KEY=%q\n' "${COSMOS_PARTITION_KEY:-id}"
} >"${BASELINE_TARGET_FILE}"
write_run_manifest "${LOG_DIR}" "${RUN_ID}" "light-load-baseline" || exit 2
for bk in "${BACKENDS[@]}"; do
  printf 'baseline-read-%s-%s\n' "${bk}" "${RUN_ID}"
done >"${LOG_DIR}/expected-workloads.txt"

echo "=== Rate-limited point-read latency baseline ==="
echo "    run_id=${RUN_ID} dur=${DURATION}s rate=${BASELINE_READ_RPS} reads/s backends=${BACKENDS[*]}"
echo "    container=${BASELINE_DATABASE}/${BASELINE_CONTAINER}  results -> ${RESULTS_COSMOS_DATABASE:-perfdb}/${RESULTS_COSMOS_CONTAINER:-perfresults-v2} (workload_id LIKE baseline-%)"
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
      130) echo "    !! interrupted; final data is not confirmed" >&2; overall_rc=1 ;;
      137|124) overall_rc=1 ;;
      *)   overall_rc=1 ;;
    esac
  done
done
echo "=== Light-load baseline complete. run_id=${RUN_ID} ==="
echo "=== Checking the light-load baseline results ==="
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
if perf_check_run "${LOG_DIR}" "${RUN_ID}" "baseline-" "${BACKEND_CSV}"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect rows/logs before trusting the baseline." >&2
  overall_rc=1
fi
echo "=== Checking the point-read p99 gate ==="
if python3 latency_report.py --prefix "baseline-" --run-id "${RUN_ID}" \
  --point-read-gate --expected-rps "${BASELINE_READ_RPS}" --max-p99-ms 10 \
  --gate-backends "${BACKEND_CSV}" \
  | tee "${REPORT_FILE}"; then
  echo "=== point-read p99 gate PASSED ==="
else
  echo "!! point-read p99 gate FAILED -- do not use this run as the low-load baseline." >&2
  overall_rc=1
fi
echo "=== Baseline log: ${RUN_LOG} ==="
echo "=== Baseline report: ${REPORT_FILE} ==="
exit "${overall_rc}"
