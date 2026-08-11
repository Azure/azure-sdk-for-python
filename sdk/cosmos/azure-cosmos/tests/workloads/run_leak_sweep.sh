#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Phase B -- Memory-leak sweep (sdkdev-dikshi drill).
#
# WHAT IT DOES, AND WHY THIS SHAPE:
#   A memory leak shows up as a process's resident memory (RSS) creeping upward
#   over a long run and never coming back down after warmup. Because RSS is
#   measured PER PROCESS, and the Rust driver's allocator arenas are per process
#   too, several processes running at once do NOT corrupt each other's memory
#   reading. So -- unlike the latency phase -- we can legitimately run all six
#   operations IN PARALLEL, one operation per process, and learn which specific
#   operation (if any) leaks. That turns a 6x24h sequential slog into a single
#   ~24h wall-clock sweep per backend.
#
#   Everything runs CLOSED-LOOP here (WORKLOAD_ARRIVAL_RATE=0) so all six ops --
#   including create and delete, which open-loop does not support -- behave the
#   same way. We are watching the RSS slope, not the latency tail, so closed-loop
#   steady load is exactly right.
#
#   The verdict (SLA gate 4) needs HOURS -- a full day for confidence -- because
#   a slow leak only becomes visible against the noise over a long soak.
#
# USAGE:
#   source ./your-private-keys.sh      # exports COSMOS_KEY (+ RESULTS_COSMOS_KEY)
#   ./run_leak_sweep.sh [DURATION_SECONDS] [BACKENDS...]
#       DURATION_SECONDS  soak length (default 86400 = 24 h)
#       BACKENDS          which backends to sweep (default: rust core-python).
#                         Each backend's 6-op batch runs in parallel; batches run
#                         one after another.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"
source ./perf_env.sh

# Phase B canonical target for this drill:
# - VM: vm-python-dr-drill
# - Container: leak_cont
# Keep caller override support (`LEAK_COSMOS_DATABASE` / `LEAK_COSMOS_CONTAINER`),
# but if no explicit leak container is provided and we are still on the generic
# perf default (`scale_cont`), move to `leak_cont` to match the documented Phase B
# environment.
if [[ -n "${LEAK_COSMOS_DATABASE:-}" ]]; then
  export COSMOS_DATABASE="${LEAK_COSMOS_DATABASE}"
fi
if [[ -n "${LEAK_COSMOS_CONTAINER:-}" ]]; then
  export COSMOS_CONTAINER="${LEAK_COSMOS_CONTAINER}"
elif [[ "${COSMOS_CONTAINER}" == "scale_cont" ]]; then
  export COSMOS_CONTAINER="leak_cont"
fi

host_name="$(hostname 2>/dev/null || echo unknown)"
if [[ "${host_name}" != "vm-python-dr-drill" ]]; then
  echo "!! WARNING: Phase B is calibrated for vm-python-dr-drill; current host=${host_name}" >&2
fi

DURATION_SECONDS="${1:-86400}"
shift || true
if [[ "$#" -gt 0 ]]; then
  BACKENDS=("$@")
else
  BACKENDS=(rust core-python)
fi

# Which operations to soak. Defaults to all six (the full leak sweep). Override
# with LEAK_OPERATIONS (space-separated) to soak a SUBSET on the same rig --
# e.g. LEAK_OPERATIONS="create" for the targeted Create-only settle follow-up
# that confirms a single op's RSS levels off (Phase B WATCH closure) without
# paying for all six. Invalid names are left to the harness to reject.
if [[ -n "${LEAK_OPERATIONS:-}" ]]; then
  # shellcheck disable=SC2206  # word-splitting is the intended parse here
  OPERATIONS=(${LEAK_OPERATIONS})
else
  OPERATIONS=(read create upsert replace delete patch)
fi

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/leak-${STAMP}"
mkdir -p "${LOG_DIR}"
write_run_manifest "${LOG_DIR}" "${STAMP}" "B-leak-sweep"

echo "=== Phase B: memory-leak sweep ==="
echo "    soak = ${DURATION_SECONDS}s (~$(( DURATION_SECONDS / 3600 )) h) per backend batch"
echo "    host = ${host_name}"
echo "    target = ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
echo "    backends = ${BACKENDS[*]} (each batch = 6 ops in PARALLEL)"
echo "    ops = ${OPERATIONS[*]} (closed-loop, one op per process)"
echo "    logs -> ${LOG_DIR}"
echo

# Overall script status. A real child failure or a failed driver-commit or integrity
# gate flips this to 1 so the sweep exits non-zero (an unattended/CI run cannot
# silently "pass"). Substantive verdict findings (a WATCH/STAIRCASE op) stay
# informational -- only hard failures fail the script.
overall_rc=0

for bk in "${BACKENDS[@]}"; do
  echo ">>> backend=${bk}: launching ${#OPERATIONS[@]} single-op processes in parallel for ${DURATION_SECONDS}s"
  pids=()
  for op in "${OPERATIONS[@]}"; do
    wid="leak-${op}-${bk}-${STAMP}"
    log="${LOG_DIR}/${wid}.log"
    # Each process gets its own exported environment in a subshell so the six
    # never share a setting. SIGINT (Ctrl-C equivalent) lets the reporter flush
    # a final RSS row when the soak ends.
    (
      export COSMOS_BACKEND="${bk}"
      export WORKLOAD_OPERATIONS="${op}"
      export WORKLOAD_ARRIVAL_RATE="0"
      export PERF_WORKLOAD_ID="${wid}"
      timeout --signal=INT --kill-after=120s --preserve-status "${DURATION_SECONDS}s" \
        python3 workload.py >"${log}" 2>&1
    ) &
    pids+=("$!")
    echo "    started op=${op} pid=$! -> ${wid}"
  done

  echo "    waiting for backend=${bk} batch to finish..."
  fail=0
  for pid in "${pids[@]}"; do
    # Capture the CHILD's real exit code. `wait "$pid" || rc=$?` puts wait on the
    # left of `||`, so $? is the child's status -- unlike `if ! wait ...; then
    # rc=$?`, where the `!` makes $? the negated condition (always 0 in the
    # branch), silently losing the real code. `rc=0` first so a clean exit reads 0.
    rc=0
    wait "${pid}" || rc=$?
    if [[ "${rc}" != "0" ]]; then
      # 130 = SIGINT fell back to KeyboardInterrupt (handler did not engage; data
      # OK), or a real failure (137 hung-and-killed, 124, other).
      # Treat 130 as a soft warning; everything else fails the batch.
      if [[ "${rc}" == "130" ]]; then
        echo "    !! pid=${pid} exited 130 (graceful handler did not engage; data OK)" >&2
      else
        echo "    !! pid=${pid} exited rc=${rc}" >&2
        fail=1
      fi
    fi
  done
  echo "    backend=${bk} batch complete (fail=${fail})"
  # A real child failure in this batch fails the whole sweep.
  if [[ "${fail}" != "0" ]]; then
    overall_rc=1
  fi
  echo
done

echo "=== Phase B sweep complete. Automated leak verdict (no eyeballing) below;"
echo "    raw rows are in ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER}, workload_id LIKE 'leak-%-${STAMP}'."

echo
echo "=== Running automated leak verdict (Phase B) ==="
# Replaces the old "plot memory_bytes vs elapsed_seconds and judge the slope by
# eye" instruction. leak_verdict.py fits the final-plateau slope with a 95% CI
# (so "flat" is statistical, not visual), cross-checks with a robust Theil-Sen
# slope, detects staircase steps, and enforces that rows name the expected backend. Informational
# at the sweep level (a WATCH/STAIRCASE op is a finding, not a harness failure),
# but it exits non-zero when a row names the wrong backend so a mislabeled run is loud.
if python3 leak_verdict.py --stamp "${STAMP}" --prefix "leak-"; then
  echo "=== leak verdict backend check PASSED ==="
else
  echo "!! leak verdict backend check FAILED -- explain the flagged rows before trusting the verdict." >&2
  overall_rc=1
fi

echo
echo "=== Running post-run integrity gate (Phase B) ==="
# Close the gap that only Phase A used to gate: prove no reporting window was
# dropped (a dropped BAD window could hide a leak step) and that every "rust" row
# actually ran on Rust (binding_calls check, --prefix leak-). A failure here
# fails the sweep so a mislabeled/incomplete run cannot pass unnoticed.
if python3 perf_validate.py --stamp "${STAMP}" --log-dir "${LOG_DIR}" --prefix "leak-"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect the rows/logs above before trusting the leak verdict." >&2
  overall_rc=1
fi

echo
if [[ "${overall_rc}" != "0" ]]; then
  echo "=== Phase B FAILED (a child process failed or a driver-commit or integrity check failed); exit ${overall_rc}. ===" >&2
else
  echo "=== Phase B OK (all batches clean, all gates passed). ==="
fi
exit "${overall_rc}"
