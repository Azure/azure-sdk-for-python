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

DURATION_SECONDS="${1:-86400}"
shift || true
if [[ "$#" -gt 0 ]]; then
  BACKENDS=("$@")
else
  BACKENDS=(rust core-python)
fi

OPERATIONS=(read create upsert replace delete patch)

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="logs/leak-${STAMP}"
mkdir -p "${LOG_DIR}"

echo "=== Phase B: memory-leak sweep ==="
echo "    soak = ${DURATION_SECONDS}s (~$(( DURATION_SECONDS / 3600 )) h) per backend batch"
echo "    backends = ${BACKENDS[*]} (each batch = 6 ops in PARALLEL)"
echo "    ops = ${OPERATIONS[*]} (closed-loop, one op per process)"
echo "    logs -> ${LOG_DIR}"
echo

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
      timeout --signal=INT --preserve-status "${DURATION_SECONDS}s" \
        python3 workload.py >"${log}" 2>&1
    ) &
    pids+=("$!")
    echo "    started op=${op} pid=$! -> ${wid}"
  done

  echo "    waiting for backend=${bk} batch to finish..."
  fail=0
  for pid in "${pids[@]}"; do
    if ! wait "${pid}"; then
      rc=$?
      # 124 = timeout fired the stop signal as intended; treat as success.
      if [[ "${rc}" != "124" ]]; then
        echo "    !! pid=${pid} exited rc=${rc}" >&2
        fail=1
      fi
    fi
  done
  echo "    backend=${bk} batch complete (fail=${fail})"
  echo
done

echo "=== Phase B complete. Read results from ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER},"
echo "    filtering workload_id LIKE 'leak-%-${STAMP}'. For each op, plot memory_bytes vs"
echo "    elapsed_seconds: a flat line after warmup = no leak; a steady upward slope = a leak."
