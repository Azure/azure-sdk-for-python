#!/usr/bin/env bash
# Run a fresh Rust point-read workload under Memray. Source this file so
# MEMRAY_STAMP, MEMRAY_FILE, and MEMRAY_RC remain available for report checks.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this file so the next memory-report step can reuse its values:" >&2
  echo "    source ./profiling_capture_memray.sh" >&2
  exit 2
fi

_memray_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${_memray_here}" || return 1

# shellcheck disable=SC1091
source ./profiling_common.sh
if [[ -n "${ARTIFACTS:-}" ]]; then
  profiling_load_env || return 2
  profiling_load_session "${ARTIFACTS}" || return 2
else
  echo "ERROR: load the intended profiling session with profiling_activate.sh <directory-name> first." >&2
  return 2
fi

_memray_failed=0
for _memray_command in python3 timeout tee date grep; do
  if ! command -v "${_memray_command}" >/dev/null 2>&1; then
    echo "ERROR: required command '${_memray_command}' is not installed." >&2
    _memray_failed=1
  fi
done

if [[ -z "${ARTIFACTS:-}" || ! -d "${ARTIFACTS}" ]]; then
  echo "ERROR: ARTIFACTS does not name an existing profiling-session directory." >&2
  _memray_failed=1
fi

MEMRAY_DURATION="${MEMRAY_DURATION:-120}"
MEMRAY_KILL_AFTER="${MEMRAY_KILL_AFTER:-30}"
for _memray_value_name in MEMRAY_DURATION MEMRAY_KILL_AFTER; do
  _memray_value="${!_memray_value_name}"
  if [[ ! "${_memray_value}" =~ ^[1-9][0-9]*$ ]]; then
    echo "ERROR: ${_memray_value_name} must be a positive whole number." >&2
    _memray_failed=1
  fi
done

if [[ "${_memray_failed}" -eq 0 ]] && ! python3 -c "import memray" >/dev/null 2>&1; then
  echo "ERROR: Memray is not installed in ${VIRTUAL_ENV:-the active Python environment}." >&2
  _memray_failed=1
fi

if [[ "${_memray_failed}" -ne 0 ]]; then
  unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value
  return 1
fi

export COSMOS_BACKEND=rust
profiling_require_read_workload || return 2

MEMRAY_STAMP="$(date -u +%Y%m%d-%H%M%S%3N)"
export PERF_WORKLOAD_ID="memray-read-rust-${MEMRAY_STAMP}"
MEMRAY_FILE="${ARTIFACTS}/memray-read-r${WORKLOAD_ARRIVAL_RATE}.bin"
MEMRAY_LOG="${ARTIFACTS}/memray-workload.log"
MEMRAY_HEALTH="${ARTIFACTS}/memray-health.txt"
MEMRAY_INTEGRITY="${ARTIFACTS}/memray-integrity.txt"
export MEMRAY_STAMP MEMRAY_FILE MEMRAY_LOG MEMRAY_DURATION MEMRAY_KILL_AFTER \
  MEMRAY_HEALTH MEMRAY_INTEGRITY

if [[ -e "${MEMRAY_FILE}" || -e "${MEMRAY_LOG}" ]]; then
  echo "ERROR: Memray artifacts already exist in ${ARTIFACTS}." >&2
  echo "       Start a new profiling session or move the existing capture first." >&2
  unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value
  return 1
fi

printf 'memray_stamp=%s\nmemray_workload_id=%s\nmemray_arrival_rate=%s\nmemray_duration=%s\nmemray_file=%s\n' \
  "${MEMRAY_STAMP}" "${PERF_WORKLOAD_ID}" "${WORKLOAD_ARRIVAL_RATE}" \
  "${MEMRAY_DURATION}" "${MEMRAY_FILE}" | tee -a "${ARTIFACTS}/run.txt"

echo "=== Recording the Rust point-read workload with Memray for ${MEMRAY_DURATION}s ==="
write_run_manifest "${ARTIFACTS}" "${MEMRAY_STAMP}" "memory-capture" || return 2
MEMRAY_RC=0
timeout \
  --signal=INT \
  --kill-after="${MEMRAY_KILL_AFTER}s" \
  --preserve-status \
  "${MEMRAY_DURATION}s" \
  python3 -m memray run --native --output "${MEMRAY_FILE}" workload.py \
  >"${MEMRAY_LOG}" 2>&1 || MEMRAY_RC=$?
export MEMRAY_RC
printf 'memray_workload_rc=%s\n' "${MEMRAY_RC}" | tee -a "${ARTIFACTS}/run.txt"

if [[ "${MEMRAY_RC}" -ne 0 ]]; then
  echo "ERROR: Memray workload exited ${MEMRAY_RC}; see ${MEMRAY_LOG}." >&2
  unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value
  return 1
fi
if [[ ! -s "${MEMRAY_FILE}" ]]; then
  echo "ERROR: Memray produced no recording at ${MEMRAY_FILE}." >&2
  unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value
  return 1
fi

echo "=== Checking completed reads, errors, 429 responses, retries, and driver build ==="
PERF_ALLOW_MISSING_DRIVER_COMMIT=0 \
  python3 latency_report.py --prefix memray- --run-id "${MEMRAY_STAMP}" --workload-health \
  | tee "${MEMRAY_HEALTH}"
_memray_health_rc=("${PIPESTATUS[@]}")
if [[ "${_memray_health_rc[*]}" != "0 0" ]]; then
  echo "ERROR: latency_report.py rejected the Memray workload; see ${MEMRAY_HEALTH}." >&2
  _memray_failed=1
fi
if grep -Eq 'PerfReporter (upsert failed|error upsert failed)' "${MEMRAY_LOG}"; then
  echo "ERROR: the workload log reports a dropped final-results write; see ${MEMRAY_LOG}." >&2
  _memray_failed=1
fi

echo "=== Proving that the configured Rust path handled the reads ==="
PERF_ALLOW_MISSING_LOGS=0 PERF_ALLOW_UNKNOWN_BINDING=0 \
  python3 perf_validate.py \
    --prefix memray- \
    --run-id "${MEMRAY_STAMP}" \
    --required-backends rust \
    --log-dir "${ARTIFACTS}" \
  | tee "${MEMRAY_INTEGRITY}"
_memray_integrity_rc=("${PIPESTATUS[@]}")
if [[ "${_memray_integrity_rc[*]}" != "0 0" ]]; then
  echo "ERROR: workload integrity gate failed; see ${MEMRAY_INTEGRITY}." >&2
  _memray_failed=1
fi

if [[ "${_memray_failed}" -ne 0 ]]; then
  unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value \
    _memray_health_rc _memray_integrity_rc
  return 1
fi

echo "=== Memray capture and workload checks passed ==="
echo "    workload ID: ${PERF_WORKLOAD_ID}"
echo "    recording  : ${MEMRAY_FILE}"
echo "    workload log: ${MEMRAY_LOG}"
echo "    health report: ${MEMRAY_HEALTH}"
echo "    integrity report: ${MEMRAY_INTEGRITY}"

unset _memray_here _memray_command _memray_failed _memray_value_name _memray_value \
  _memray_health_rc _memray_integrity_rc
return 0
