#!/usr/bin/env bash
# Rate-limited point-read latency baseline. Rate comes from ~/profiling_config.env,
# no proxy. Check measured request charges against the test container's service
# capacity; 250 reads/s is not automatically below a 400-RU/s budget. Unpaced
# send-and-wait sends the next read immediately and can saturate the account.
#
# Purpose: validate the test environment before any A/B claim. A point-op baseline
# uses experiment-specific acceptance criteria, not a service SLA.
# Primary latency is SDK-call duration, not the delay before entering the SDK.
# Scheduled-start total duration and scheduling health remain separate evidence.
#
# Backend is selectable so the same workload runs both paths. Explicitly load
# the intended profiling session before starting:
#   bash ./profiling_run_read_baseline.sh 480  # five comparisons by default
#   BASELINE_COMPARISONS=1 bash ./profiling_run_read_baseline.sh 480
#   BASELINE_COMPARISONS=5 BASELINE_BACKENDS=rust bash ./profiling_run_read_baseline.sh 480
# BASELINE_COMPARISONS controls the runner, not the workload configuration.
# Each comparison gets a separate session; the first uses the loaded session.
# A failed comparison stops the batch without discarding evidence or retrying.
# Change workload settings in ~/profiling_config.env and create a fresh session.
# The baseline retains the validated profiling session's test target and item
# range. Prepare a new profiling session to change the database or container.
# Results use the active PROFILING_SESSION_ID and configured results container, tagged
# PERF_WORKLOAD_ID=baseline-<op>-<backend>-<profiling-session-id>.
set -uo pipefail
cd "$(dirname "$0")"
BASELINE_COMPARISONS="${BASELINE_COMPARISONS-5}"
if [[ ! "${BASELINE_COMPARISONS}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: BASELINE_COMPARISONS must be a positive whole number." >&2
  exit 2
fi
if (( BASELINE_COMPARISONS <= 0 )) || [[ "$((BASELINE_COMPARISONS))" != "${BASELINE_COMPARISONS}" ]]; then
  echo "ERROR: BASELINE_COMPARISONS exceeds the supported integer range." >&2
  exit 2
fi
for removed in BASELINE_READ_RPS BASELINE_DATABASE BASELINE_CONTAINER BASELINE_OPERATIONS; do
  if [[ -v "$removed" ]]; then
    echo "ERROR: $removed is removed. Edit ~/profiling_config.env and unset $removed." >&2
    exit 2
  fi
done
source ./profiling_common.sh || exit 2
if [[ -n "${PROFILING_SESSION_DIR:-}" ]]; then
  profiling_load_env || exit 2
  profiling_load_session "${PROFILING_SESSION_DIR}" || exit 2
else
  echo "ERROR: load the intended profiling session with profiling_load_session.sh <directory-name> first." >&2
  exit 2
fi
: "${PROFILING_SESSION_ID:?no complete profiling session found; run profiling_create_session.sh first}"
: "${PROFILING_SESSION_DIR:?no complete profiling session found; run profiling_create_session.sh first}"

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

if (( BASELINE_COMPARISONS > 1 )); then
  SOURCE_SESSION_DIR="${PROFILING_SESSION_DIR}"
  SOURCE_SESSION_ID="${PROFILING_SESSION_ID}"
  BATCH_DIR="${SOURCE_SESSION_DIR}/baseline-batch-${SOURCE_SESSION_ID}"
  perf_create_log_dir "${BATCH_DIR}" || exit 2
  exec > >(tee "${BATCH_DIR}/batch-run.log") 2>&1
  COMPARISON_RESULTS="${BATCH_DIR}/comparisons.tsv"
  printf 'comparison\tprofiling_session_id\tsession_directory\tstatus\texit_status\n' \
    > "${COMPARISON_RESULTS}" || exit 1
  attempted=0
  completed=0
  passed=0
  comparison_open=false
  current_session_id=""
  current_session_dir=""

  write_batch_summary() {
    {
      printf 'source_session_id=%q\n' "${SOURCE_SESSION_ID}"
      printf 'requested_comparisons=%s\nattempted_comparisons=%s\ncompleted_comparisons=%s\npassed_comparisons=%s\n' \
        "${BASELINE_COMPARISONS}" "${attempted}" "${completed}" "${passed}"
      printf 'duration_seconds_per_backend=%q\nbackends=%q\nstatus=%q\nexit_status=%q\n' \
        "${DURATION}" "${BACKENDS[*]}" "$1" "$2"
    } > "${BATCH_DIR}/batch-summary.env.tmp" &&
      mv -- "${BATCH_DIR}/batch-summary.env.tmp" "${BATCH_DIR}/batch-summary.env"
  }

  record_comparison() {
    printf '%s\t%s\t%s\t%s\t%s\n' "${attempted}" \
      "${current_session_id:--}" "${current_session_dir:--}" "$1" "$2" >> "${COMPARISON_RESULTS}"
  }

  finish_batch() {
    local rc=$? status=failed
    trap - EXIT
    if [[ "${comparison_open}" == true ]]; then
      record_comparison interrupted "${rc}" || {
        echo "ERROR: cannot record interrupted comparison." >&2
        rc=1
      }
    fi
    if (( rc == 0 && passed == BASELINE_COMPARISONS )); then
      status=passed
    elif (( rc == 0 )); then
      rc=1
    fi
    write_batch_summary "${status}" "${rc}" || {
      echo "ERROR: cannot save baseline batch summary." >&2
      rc=1
      status=failed
    }
    echo "=== Baseline batch ${status}: ${passed}/${BASELINE_COMPARISONS} comparisons passed ==="
    echo "=== Batch summary: ${BATCH_DIR}/batch-summary.env ==="
    echo "=== Comparison sessions: ${COMPARISON_RESULTS} ==="
    exit "${rc}"
  }
  trap finish_batch EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  write_batch_summary running "" || { echo "ERROR: cannot initialize batch summary." >&2; exit 1; }

  for ((index=0; index<BASELINE_COMPARISONS; index++)); do
    attempted=$((index + 1))
    comparison_open=true
    current_session_id=""
    current_session_dir=""
    write_batch_summary running "" || { echo "ERROR: cannot update batch summary." >&2; exit 1; }
    # Revalidate against the original session, not only the newly created one:
    # otherwise a changed build/configuration could silently enter the batch.
    if ! profiling_load_env || ! profiling_load_session "${SOURCE_SESSION_DIR}"; then
      echo "ERROR: original session no longer matches the active setup; stopping batch." >&2
      record_comparison setup_failed 2 || exit 1
      comparison_open=false
      exit 2
    fi
    if (( index > 0 )); then
      control="${BATCH_DIR}/session-creation-${attempted}.log"
      if ! bash ./profiling_create_session.sh read-baseline 2>&1 | tee "${control}"; then
        echo "ERROR: comparison ${attempted} session creation failed; stopping batch." >&2
        record_comparison setup_failed 1 || exit 1
        comparison_open=false
        exit 1
      fi
      new_session_dir="$(sed -n 's/^artifacts=//p' "${control}")"
      if [[ -z "${new_session_dir}" || "${new_session_dir}" == *$'\n'* ]]; then
        echo "ERROR: session creation did not identify exactly one session; stopping batch." >&2
        record_comparison setup_failed 1 || exit 1
        comparison_open=false
        exit 1
      fi
      current_session_dir="${new_session_dir}"
      if ! profiling_load_session "${current_session_dir}"; then
        echo "ERROR: session creation did not identify one valid session; stopping batch." >&2
        record_comparison setup_failed 1 || exit 1
        comparison_open=false
        exit 1
      fi
    fi
    current_session_id="${PROFILING_SESSION_ID}"
    current_session_dir="${PROFILING_SESSION_DIR}"
    echo "=== Comparison ${attempted}/${BASELINE_COMPARISONS}: ${current_session_id} ==="
    if BASELINE_COMPARISONS=1 bash ./profiling_run_read_baseline.sh "${DURATION}"; then
      rc=0
      status=passed
      passed=$((passed + 1))
    else
      rc=$?
      status=failed
    fi
    completed=$((completed + 1))
    record_comparison "${status}" "${rc}" || { echo "ERROR: cannot save comparison outcome." >&2; exit 1; }
    comparison_open=false
    write_batch_summary running "" || { echo "ERROR: cannot update batch summary." >&2; exit 1; }
    if (( rc != 0 )); then
      echo "ERROR: comparison ${attempted} failed; no further comparisons will run." >&2
      exit "${rc}"
    fi
  done
  exit 0
fi

LOG_DIR="${PROFILING_SESSION_DIR}/light-load-baseline-${PROFILING_SESSION_ID}"
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
echo "=== Checking the SDK-call p99 and point-read workload-health gate ==="
if python3 latency_report.py --prefix "baseline-" --profiling-session-id "${PROFILING_SESSION_ID}" \
  --latency-metric sdk-call --point-read-gate --expected-rps "${WORKLOAD_ARRIVAL_RATE}" --max-p99-ms 10 \
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
