#!/usr/bin/env bash
# Capture functions executing on every thread plus whole-process CPU, memory,
# disk, page-fault, and context-switch measurements. Then stop and validate the
# workload left running by profiling_capture_py_spy.sh.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this file in the terminal that ran profiling_capture_py_spy.sh:" >&2
  echo "    source ./profiling_capture_perf.sh" >&2
  exit 2
fi

_perf_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${_perf_here}" || return 1

_perf_failed=0

if [[ ! "${WORKLOAD_PID:-}" =~ ^[0-9]+$ ]]; then
  echo "ERROR: WORKLOAD_PID is missing or invalid." >&2
  echo "       First run: source ./profiling_capture_py_spy.sh" >&2
  _perf_failed=1
elif ! kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
  echo "ERROR: workload PID ${WORKLOAD_PID} is not running." >&2
  _perf_failed=1
fi

if [[ -z "${ARTIFACTS:-}" || ! -d "${ARTIFACTS}" ]]; then
  echo "ERROR: ARTIFACTS does not name an existing profiling-session directory." >&2
  _perf_failed=1
elif [[ ! -s "${ARTIFACTS}/smaps-before.txt" ]]; then
  echo "ERROR: ${ARTIFACTS}/smaps-before.txt is missing or empty." >&2
  echo "       The before/after memory comparison requires the py-spy capture first." >&2
  _perf_failed=1
fi

if [[ ! "${PROFILE_STAMP:-}" =~ ^[0-9]{8}-[0-9]{6}$ ]]; then
  echo "ERROR: PROFILE_STAMP is missing or invalid." >&2
  echo "       Source profiling_capture_py_spy.sh in this terminal first." >&2
  _perf_failed=1
fi

if ! declare -F cleanup_workload >/dev/null 2>&1; then
  echo "ERROR: cleanup_workload is unavailable." >&2
  echo "       Source profiling_capture_py_spy.sh in this terminal first." >&2
  _perf_failed=1
fi

for _perf_command in sudo perf pidstat c++filt ps tee grep cat python3; do
  if ! command -v "${_perf_command}" >/dev/null 2>&1; then
    echo "ERROR: required command '${_perf_command}' is not installed." >&2
    _perf_failed=1
  fi
done

PERF_CAPTURE_DURATION="${PERF_CAPTURE_DURATION:-60}"
PERF_SAMPLE_FREQUENCY="${PERF_SAMPLE_FREQUENCY:-199}"
SYSTEM_CAPTURE_DURATION="${SYSTEM_CAPTURE_DURATION:-60}"
PERF_CAPTURE_SCHED="${PERF_CAPTURE_SCHED:-false}"
PERF_SCHED_DURATION="${PERF_SCHED_DURATION:-30}"

if [[ ! "${PERF_CAPTURE_DURATION}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: PERF_CAPTURE_DURATION must be a positive whole number." >&2
  _perf_failed=1
fi
if [[ ! "${PERF_SAMPLE_FREQUENCY}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: PERF_SAMPLE_FREQUENCY must be a positive whole number." >&2
  _perf_failed=1
fi
if [[ ! "${SYSTEM_CAPTURE_DURATION}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: SYSTEM_CAPTURE_DURATION must be a positive whole number." >&2
  _perf_failed=1
fi
if [[ "${PERF_CAPTURE_SCHED}" != "true" && "${PERF_CAPTURE_SCHED}" != "false" ]]; then
  echo "ERROR: PERF_CAPTURE_SCHED must be true or false." >&2
  _perf_failed=1
fi
if [[ ! "${PERF_SCHED_DURATION}" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: PERF_SCHED_DURATION must be a positive whole number." >&2
  _perf_failed=1
fi

if [[ "${_perf_failed}" -eq 0 ]] && ! sudo -v; then
  echo "ERROR: sudo permission is required for Linux perf." >&2
  _perf_failed=1
fi

if [[ "${_perf_failed}" -eq 0 ]]; then
  echo "=== Recording all workload threads for ${PERF_CAPTURE_DURATION}s ==="
  sudo perf record \
    --pid "${WORKLOAD_PID}" \
    --freq "${PERF_SAMPLE_FREQUENCY}" \
    --call-graph dwarf \
    --output "${ARTIFACTS}/perf.data" \
    -- sleep "${PERF_CAPTURE_DURATION}" \
    2>&1 | tee "${ARTIFACTS}/perf-record.log"
  _perf_record_rc=${PIPESTATUS[0]}
  if [[ "${_perf_record_rc}" -ne 0 ]]; then
    echo "ERROR: perf record exited ${_perf_record_rc}." >&2
    _perf_failed=1
  elif [[ ! -s "${ARTIFACTS}/perf.data" ]]; then
    echo "ERROR: perf record produced no data." >&2
    _perf_failed=1
  elif ! kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
    echo "ERROR: the workload stopped during perf record." >&2
    _perf_failed=1
  fi
fi

if [[ "${_perf_failed}" -eq 0 ]]; then
  echo "=== Writing a readable all-thread report ==="
  sudo perf report \
    --stdio \
    --input "${ARTIFACTS}/perf.data" \
    --sort comm,dso,symbol \
    2>"${ARTIFACTS}/perf-report.log" \
    | c++filt >"${ARTIFACTS}/perf-report.txt"
  _perf_report_status=("${PIPESTATUS[@]}")
  _perf_report_rc=${_perf_report_status[0]}
  _perf_demangle_rc=${_perf_report_status[1]}
  if [[ "${_perf_report_rc}" -ne 0 || "${_perf_demangle_rc}" -ne 0 ]]; then
    echo "ERROR: perf report or c++filt failed; see perf-report.log." >&2
    _perf_failed=1
  elif [[ ! -s "${ARTIFACTS}/perf-report.txt" ]]; then
    echo "ERROR: perf report produced no readable text." >&2
    _perf_failed=1
  elif ! grep -Eqi 'tokio|azure_cosmos_driver|_rust\.abi3|python3' \
    "${ARTIFACTS}/perf-report.txt"; then
    echo "ERROR: perf report contains no recognizable workload symbols." >&2
    _perf_failed=1
  fi
fi

if [[ "${_perf_failed}" -eq 0 && "${PERF_CAPTURE_SCHED}" == "true" ]]; then
  echo "=== Recording scheduler states for ${PERF_SCHED_DURATION}s ==="
  sudo perf sched record \
    --all-cpus \
    --output "${ARTIFACTS}/perf-sched.data" \
    -- sleep "${PERF_SCHED_DURATION}" \
    2>&1 | tee "${ARTIFACTS}/perf-sched-record.log"
  _perf_sched_record_rc=${PIPESTATUS[0]}
  if [[ "${_perf_sched_record_rc}" -ne 0 ]]; then
    echo "ERROR: perf sched record exited ${_perf_sched_record_rc}." >&2
    _perf_failed=1
  elif ! sudo perf sched timehist \
    --input "${ARTIFACTS}/perf-sched.data" \
    --pid "${WORKLOAD_PID}" \
    >"${ARTIFACTS}/perf-sched-timehist.txt" \
    2>"${ARTIFACTS}/perf-sched-timehist.log"; then
    echo "ERROR: perf sched timehist failed; see perf-sched-timehist.log." >&2
    _perf_failed=1
  elif [[ ! -s "${ARTIFACTS}/perf-sched-timehist.txt" ]]; then
    echo "ERROR: perf sched produced no workload scheduling timeline." >&2
    _perf_failed=1
  elif ! kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
    echo "ERROR: the workload stopped during perf sched." >&2
    _perf_failed=1
  fi
fi

if [[ "${_perf_failed}" -eq 0 ]]; then
  echo "=== Recording whole-process CPU, memory, disk, fault, and switch measurements for ${SYSTEM_CAPTURE_DURATION}s ==="
  pidstat -rudw -p "${WORKLOAD_PID}" 1 "${SYSTEM_CAPTURE_DURATION}" \
    | tee "${ARTIFACTS}/pidstat.txt"
  _perf_pidstat_rc=${PIPESTATUS[0]}
  if [[ "${_perf_pidstat_rc}" -ne 0 ]]; then
    echo "ERROR: pidstat exited ${_perf_pidstat_rc}." >&2
    _perf_failed=1
  elif [[ ! -s "${ARTIFACTS}/pidstat.txt" ]]; then
    echo "ERROR: pidstat produced no whole-process measurements." >&2
    _perf_failed=1
  elif ! kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
    echo "ERROR: the workload stopped during pidstat." >&2
    _perf_failed=1
  elif ! cat "/proc/${WORKLOAD_PID}/smaps_rollup" >"${ARTIFACTS}/smaps-after.txt"; then
    echo "ERROR: could not capture final process memory totals." >&2
    _perf_failed=1
  elif ! ps -L -p "${WORKLOAD_PID}" -o pid,tid,psr,pcpu,rss,comm \
    >"${ARTIFACTS}/threads-after.txt"; then
    echo "ERROR: could not capture the final thread list." >&2
    _perf_failed=1
  fi
fi

# Stop immediately even when a profiler fails. The health report covers the
# workload's entire lifetime, so leaving it running would change the result.
if declare -F cleanup_workload >/dev/null 2>&1; then
  cleanup_workload
fi
trap - EXIT INT TERM

if [[ -n "${ARTIFACTS:-}" && -d "${ARTIFACTS}" ]]; then
  printf 'profile_workload_rc=%s\n' "${WORKLOAD_RC:-unknown}" \
    | tee -a "${ARTIFACTS}/run.txt"
fi

if [[ "${_perf_failed}" -eq 0 ]]; then
  echo "=== Checking completed reads, errors, 429 responses, and Rust retries ==="
  python3 latency_report.py --prefix profile- --run-id "${PROFILE_STAMP}" \
    | tee "${ARTIFACTS}/profile-health.txt"
  _perf_health_rc=${PIPESTATUS[0]}
  if [[ "${_perf_health_rc}" -ne 0 ]]; then
    echo "ERROR: latency_report.py exited ${_perf_health_rc}." >&2
    _perf_failed=1
  elif ! grep -Eq 'count= *[1-9][0-9]*.*err= *0.*429= *0.*retries= *0' \
    "${ARTIFACTS}/profile-health.txt"; then
    echo "ERROR: workload health gate failed; see profile-health.txt." >&2
    _perf_failed=1
  fi
fi

if [[ "${_perf_failed}" -ne 0 ]]; then
  unset _perf_here _perf_command _perf_failed _perf_record_rc _perf_report_rc \
    _perf_demangle_rc _perf_report_status _perf_sched_record_rc \
    _perf_pidstat_rc _perf_health_rc
  return 1
fi

echo "=== perf, process measurements, and workload health PASSED ==="
echo "    CPU data       : ${ARTIFACTS}/perf.data"
echo "    readable report: ${ARTIFACTS}/perf-report.txt"
echo "    process metrics: ${ARTIFACTS}/pidstat.txt"
echo "    memory after   : ${ARTIFACTS}/smaps-after.txt"
echo "    workload health: ${ARTIFACTS}/profile-health.txt"
if [[ "${PERF_CAPTURE_SCHED}" == "true" ]]; then
  echo "    scheduler trace: ${ARTIFACTS}/perf-sched-timehist.txt"
fi

unset _perf_here _perf_command _perf_failed _perf_record_rc _perf_report_rc \
  _perf_demangle_rc _perf_report_status _perf_sched_record_rc \
  _perf_pidstat_rc _perf_health_rc
return 0
