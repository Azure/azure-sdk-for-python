#!/usr/bin/env bash
# Shared workload helpers; no experiment defaults or credentials.

write_run_manifest() {
  local here
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 1
  python3 "${here}/perf_manifest.py" "$1" "$2" "${3:-unknown}"
}

perf_create_log_dir() {
  mkdir -p -- "$(dirname "$1")" || return 1
  if ! mkdir -- "$1"; then
    echo "ERROR: run directory must be new; existing evidence will not be overwritten: $1" >&2
    return 1
  fi
}

perf_single_operation_shape() {
  export WORKLOAD_MIX=""
  export WORKLOAD_USE_SYNC=false
  export WORKLOAD_NUM_CLIENTS=1
  export WORKLOAD_USE_PROXY=false
  export WORKLOAD_SKIP_CLOSE=false
  export PERF_ENABLED=true
}

perf_check_run() {
  local logs="$1" stamp="$2" prefix="$3" backends="$4"
  python3 "$(dirname "${BASH_SOURCE[0]}")/perf_validate.py" \
    --run-id "${stamp}" --prefix "${prefix}" --log-dir "${logs}" \
    --required-backends "${backends}" --expected-workloads "${logs}/expected-workloads.txt"
}

perf_require_positive() {
  local value
  for value in "$@"; do
    if [[ ! "${value}" =~ ^[1-9][0-9]*$ ]]; then
      echo "ERROR: duration, repeat, concurrency and process counts must be positive integers: ${value}" >&2
      return 2
    fi
  done
}
