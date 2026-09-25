#!/usr/bin/env bash
# Rate-limited point-read latency baseline. Rate comes from ~/profiling_config.env,
# no proxy. Check measured request charges against the test container's service
# capacity; 250 reads/s is not automatically below a 400-RU/s budget. Unpaced
# send-and-wait sends the next read immediately and can saturate the account.
#
# Purpose: validate the test environment before any A/B claim. A point-op baseline
# uses experiment-specific acceptance criteria, not a service SLA.
#
# Backend is selectable so the same workload runs both paths. Explicitly load
# the intended profiling session before starting:
#   bash ./profiling_run_read_baseline.sh 480
#   BASELINE_BACKENDS=rust bash ./profiling_run_read_baseline.sh 480
# Change workload settings in ~/profiling_config.env and create a fresh session.
# The baseline retains the validated profiling session's test target and item
# range. Prepare a new profiling session to change the database or container.
# Results use the active PROFILING_SESSION_ID and configured results container, tagged
# PERF_WORKLOAD_ID=baseline-<op>-<backend>-<profiling-session-id>.
set -uo pipefail
cd "$(dirname "$0")"
for removed in BASELINE_READ_RPS BASELINE_DATABASE BASELINE_CONTAINER BASELINE_OPERATIONS; do
  if [[ -v "$removed" ]]; then
    echo "ERROR: $removed is removed. Edit ~/profiling_config.env and unset $removed." >&2
    exit 2
  fi
done
source ./profiling_common.sh
if [[ -n "${ARTIFACTS:-}" ]]; then
  profiling_load_env || exit 2
  profiling_load_session "${ARTIFACTS}" || exit 2
else
  echo "ERROR: load the intended profiling session with profiling_activate.sh <directory-name> first." >&2
  exit 2
fi
: "${PROFILING_SESSION_ID:?no complete profiling session found; run profiling_start_session.sh first}"
: "${ARTIFACTS:?no complete profiling session found; run profiling_start_session.sh first}"

DURATION="${1:-480}"
[[ $# -le 1 ]] || { echo "ERROR: expected only an optional duration in seconds." >&2; exit 2; }
perf_require_positive "${DURATION}" || exit 2
profiling_require_read_workload || exit 2
OPERATIONS=(read)
read -r -a BACKENDS <<< "${BASELINE_BACKENDS-core-python rust}"
[[ ${#BACKENDS[@]} -gt 0 ]] || { echo "ERROR: BASELINE_BACKENDS is empty." >&2; exit 2; }
seen_backends=" "
for backend in "${BACKENDS[@]}"; do
  if [[ "$backend" != core-python && "$backend" != rust ]] || [[ "$seen_backends" == *" $backend "* ]]; then
    echo "ERROR: BASELINE_BACKENDS must select core-python and/or rust without duplicates." >&2
    exit 2
  fi
  seen_backends+="$backend "
done

LOG_DIR="${ARTIFACTS}/light-load-baseline-${PROFILING_SESSION_ID}"
perf_create_log_dir "$LOG_DIR" || exit 2
RUN_LOG="${LOG_DIR}/baseline-run.log"
REPORT_FILE="${LOG_DIR}/latency-report.txt"
exec > >(tee "${RUN_LOG}") 2>&1

# Persist the exact data target used by this child process. The parent shell
# does not inherit exports from this script, so the later transport check
# compares this record with its validated configuration.
BASELINE_TARGET_FILE="${LOG_DIR}/baseline-target.env"
{
  printf 'BASELINE_DATABASE=%q\n' "${COSMOS_DATABASE}"
  printf 'BASELINE_CONTAINER=%q\n' "${COSMOS_CONTAINER}"
  printf 'BASELINE_PARTITION_KEY=%q\n' "${COSMOS_PARTITION_KEY:-id}"
} >"${BASELINE_TARGET_FILE}"
write_run_manifest "${LOG_DIR}" "${PROFILING_SESSION_ID}" "light-load-baseline" || exit 2
for bk in "${BACKENDS[@]}"; do
  printf 'baseline-read-%s-%s\n' "${bk}" "${PROFILING_SESSION_ID}"
done >"${LOG_DIR}/expected-workloads.txt"

echo "=== Rate-limited point-read latency baseline ==="
echo "    profiling_session_id=${PROFILING_SESSION_ID} dur=${DURATION}s rate=${WORKLOAD_ARRIVAL_RATE} reads/s backends=${BACKENDS[*]}"
echo "    container=${COSMOS_DATABASE}/${COSMOS_CONTAINER}  results -> ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER} (workload_id LIKE baseline-%)"
echo
overall_rc=0

for op in "${OPERATIONS[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    wid="baseline-${op}-${bk}-${PROFILING_SESSION_ID}"
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
echo "=== Light-load baseline complete. profiling_session_id=${PROFILING_SESSION_ID} ==="
echo "=== Checking the light-load baseline results ==="
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
if perf_check_run "${LOG_DIR}" "${PROFILING_SESSION_ID}" "baseline-" "${BACKEND_CSV}"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect rows/logs before trusting the baseline." >&2
  overall_rc=1
fi
echo "=== Checking the point-read p99 gate ==="
if python3 latency_report.py --prefix "baseline-" --profiling-session-id "${PROFILING_SESSION_ID}" \
  --point-read-gate --expected-rps "${WORKLOAD_ARRIVAL_RATE}" --max-p99-ms 10 \
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
