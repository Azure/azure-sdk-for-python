#!/usr/bin/env bash
# Capture Python-visible stacks while preserving the workload for the next
# all-thread profiling step. Source this file so WORKLOAD_PID, PROFILE_STAMP,
# cleanup_workload, and the cleanup traps remain available in the current shell.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this file so the next profiling step can reuse the workload:" >&2
  echo "    source ./profiling_capture_py_spy.sh" >&2
  exit 2
fi

_py_spy_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${_py_spy_here}" || return 1

# shellcheck disable=SC1091
source ./profiling_common.sh
if [[ -n "${RUN_ID:-}" && -n "${ARTIFACTS:-}" ]]; then
  profiling_load_env || return 2
  profiling_load_session "${ARTIFACTS}" || return 2
else
  # shellcheck disable=SC1091
  source ./profiling_activate.sh || return 2
fi

if [[ -n "${WORKLOAD_PID:-}" ]] && kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
  echo "ERROR: workload PID ${WORKLOAD_PID} is already running." >&2
  echo "       Stop it before starting another profiling workload." >&2
  return 2
fi

for _py_spy_command in python3 py-spy ps grep tee seq; do
  if ! command -v "${_py_spy_command}" >/dev/null 2>&1; then
    echo "ERROR: required command '${_py_spy_command}' is not installed." >&2
    return 2
  fi
done

export COSMOS_BACKEND=rust
export WORKLOAD_OPERATIONS=read
export COSMOS_CONCURRENT_REQUESTS=1
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=250
export WORKLOAD_USE_PROXY=false
export WORKLOAD_USE_SYNC=false
export WORKLOAD_LOOP_LAG_MONITOR=false
export PERF_REPORT_INTERVAL=3600
PROFILE_STAMP="$(date -u +%Y%m%d-%H%M%S)"
export PERF_WORKLOAD_ID="profile-read-rust-${PROFILE_STAMP}"

PY_SPY_DURATION="${PY_SPY_DURATION:-60}"
PY_SPY_RATE="${PY_SPY_RATE:-100}"
PY_SPY_WARMUP="${PY_SPY_WARMUP:-30}"
PY_SPY_SVG="${ARTIFACTS}/py-spy-wall.svg"
PY_SPY_DUMP="${ARTIFACTS}/py-spy-dump.txt"
PY_SPY_LOG="${ARTIFACTS}/py-spy-record.log"
PY_SPY_DUMP_LOG="${ARTIFACTS}/py-spy-dump.log"

python3 workload.py >"${ARTIFACTS}/profile-workload.log" 2>&1 &
WORKLOAD_PID=$!
printf 'profile_stamp=%s\nworkload_pid=%s\n' "${PROFILE_STAMP}" "${WORKLOAD_PID}" \
  | tee -a "${ARTIFACTS}/run.txt"

WORKLOAD_RC=unknown
cleanup_workload() {
  if [[ "${WORKLOAD_RC:-unknown}" != "unknown" ]]; then
    return 0
  fi
  if kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
    kill -INT "${WORKLOAD_PID}" 2>/dev/null
    for _ in $(seq 1 30); do
      kill -0 "${WORKLOAD_PID}" 2>/dev/null || break
      sleep 1
    done
    if kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
      kill -TERM "${WORKLOAD_PID}" 2>/dev/null
      sleep 5
    fi
    kill -0 "${WORKLOAD_PID}" 2>/dev/null && kill -KILL "${WORKLOAD_PID}" 2>/dev/null
  fi
  wait "${WORKLOAD_PID}" 2>/dev/null
  WORKLOAD_RC=$?
}
trap cleanup_workload EXIT
trap 'exit 130' INT TERM

echo "=== Warming the Rust point-read workload for ${PY_SPY_WARMUP}s ==="
sleep "${PY_SPY_WARMUP}"

_py_spy_failed=0
if ! kill -0 "${WORKLOAD_PID}" 2>/dev/null; then
  echo "ERROR: the workload stopped during warmup; see ${ARTIFACTS}/profile-workload.log." >&2
  _py_spy_failed=1
fi

if [[ "${_py_spy_failed}" -eq 0 ]]; then
  ps -p "${WORKLOAD_PID}" -o pid,ppid,etime,%cpu,rss,vsz,nlwp,cmd \
    | tee "${ARTIFACTS}/process-before.txt"
  _py_spy_ps_rc=${PIPESTATUS[0]}
  if [[ "${_py_spy_ps_rc}" -ne 0 ]]; then
    echo "ERROR: could not inspect workload PID ${WORKLOAD_PID}." >&2
    _py_spy_failed=1
  elif ! tr '\0' ' ' <"/proc/${WORKLOAD_PID}/cmdline" | grep -q 'workload.py'; then
    echo "ERROR: PID ${WORKLOAD_PID} is not the expected workload.py process." >&2
    _py_spy_failed=1
  fi
fi

if [[ "${_py_spy_failed}" -eq 0 ]]; then
  grep -E 'azure.*cosmos.*_rust|_rust.*\.so' "/proc/${WORKLOAD_PID}/maps" \
    | tee "${ARTIFACTS}/rust-mapping.txt"
  _py_spy_mapping_rc=${PIPESTATUS[0]}
  if [[ "${_py_spy_mapping_rc}" -ne 0 ]]; then
    echo "ERROR: the Cosmos Rust extension is not loaded in PID ${WORKLOAD_PID}." >&2
    _py_spy_failed=1
  elif ! cat "/proc/${WORKLOAD_PID}/smaps_rollup" >"${ARTIFACTS}/smaps-before.txt"; then
    echo "ERROR: could not capture initial process memory totals." >&2
    _py_spy_failed=1
  fi
fi

if [[ "${_py_spy_failed}" -eq 0 ]]; then
  echo "=== Recording Python-visible stacks for ${PY_SPY_DURATION}s at ${PY_SPY_RATE} Hz ==="
  py-spy record \
    --pid "${WORKLOAD_PID}" \
    --duration "${PY_SPY_DURATION}" \
    --rate "${PY_SPY_RATE}" \
    --native \
    --idle \
    --output "${PY_SPY_SVG}" \
    2>&1 | tee "${PY_SPY_LOG}"
  _py_spy_record_rc=${PIPESTATUS[0]}
  if [[ "${_py_spy_record_rc}" -ne 0 ]]; then
    echo "ERROR: py-spy record exited ${_py_spy_record_rc}." >&2
    _py_spy_failed=1
  elif grep -Eqi 'behind in sampling|failed to (sample|read)' "${PY_SPY_LOG}"; then
    echo "ERROR: py-spy reported that it could not sustain or read the requested samples." >&2
    _py_spy_failed=1
  elif [[ ! -s "${PY_SPY_SVG}" ]]; then
    echo "ERROR: py-spy produced no flame graph at ${PY_SPY_SVG}." >&2
    _py_spy_failed=1
  elif ! grep -Eqi 'workload|azure[._/: -]*cosmos|ContainerProxy|AsyncRustBackend' "${PY_SPY_SVG}"; then
    echo "ERROR: the flame graph contains no recognizable workload or Cosmos SDK frames." >&2
    _py_spy_failed=1
  fi
fi

if [[ "${_py_spy_failed}" -eq 0 ]]; then
  echo "=== Capturing one searchable text stack snapshot ==="
  if ! py-spy dump --pid "${WORKLOAD_PID}" --native \
    >"${PY_SPY_DUMP}" 2>"${PY_SPY_DUMP_LOG}"; then
    echo "ERROR: py-spy dump failed; see ${PY_SPY_DUMP_LOG}." >&2
    _py_spy_failed=1
  elif [[ ! -s "${PY_SPY_DUMP}" ]]; then
    echo "ERROR: py-spy dump produced no readable stack output." >&2
    _py_spy_failed=1
  fi
fi

if [[ "${_py_spy_failed}" -ne 0 ]]; then
  cleanup_workload
  trap - EXIT INT TERM
  unset _py_spy_here _py_spy_command _py_spy_failed _py_spy_mapping_rc \
    _py_spy_ps_rc _py_spy_record_rc
  return 1
fi

echo "=== py-spy capture PASSED ==="
echo "    flame graph : ${PY_SPY_SVG}"
echo "    text dump   : ${PY_SPY_DUMP}"
echo "    workload PID: ${WORKLOAD_PID} (left running for the next profiling step)"
echo "    Stop safely at any time with: cleanup_workload"

unset _py_spy_here _py_spy_command _py_spy_failed _py_spy_mapping_rc \
  _py_spy_ps_rc _py_spy_record_rc
return 0
