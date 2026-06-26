#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Phase C -- Throughput / scaling sweep (sdkdev-dikshi drill).
#
# WHAT IT DOES, AND WHY THIS SHAPE:
#   The "thousands of requests per second" question is a SCALING question, and one
#   concurrency level cannot answer it. So we ramp concurrency (1 -> 2048) on both
#   backends and watch two things: where the two paths CROSS OVER, and where each
#   one's throughput PLATEAUS (more concurrency stops adding req/s, or 429s /
#   system_cpu_percent climb). That plateau is the single-process ceiling -- set
#   by the service, the driver's connection pool, the GIL, and this VM's CPU.
#
#   This is the doc's "most important output": not a single faster/slower verdict,
#   but the honest shape of how each backend scales.
#
#   It is CLOSED-LOOP on purpose -- concurrency is the independent variable here,
#   so we hold it fixed per point and read the achieved req/s (count/window_seconds)
#   from the result rows. One operation per process keeps each ceiling clean; we
#   sweep a light READ (highest ceiling) and a WRITE (upsert) by default, because
#   "thousands/sec" must be shown for reads AND writes, which scale differently.
#
#   Each point runs long enough to clear warmup -- 1800s leaves ~20 min of steady
#   state after the elapsed_seconds > 600 analysis filter.
#
#   The sweep is SEQUENTIAL: each point is its own clean throughput measurement, so
#   nothing else may run alongside it.
#
# IF ONE PROCESS PLATEAUS BELOW YOUR TARGET (common for writes): the account can do
#   far more than one Python process can drive (GIL + one connection pool). Scale
#   OUT -- run several copies of this workload at the plateau concurrency, on this
#   VM and/or more VMs, and SUM their achieved req/s. See the note printed at the end.
#
# USAGE:
#   source ./your-private-keys.sh      # exports COSMOS_KEY (+ RESULTS_COSMOS_KEY)
#   ./run_throughput_sweep.sh [DURATION_SECONDS] [ops...]
#       DURATION_SECONDS  per point (default 1800 = 30 min)
#       ops               operations to sweep (default: read upsert)
#   Override the ladder with CONCURRENCY_LEVELS="1 8 64 256 1024".
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"
source ./perf_env.sh

DURATION_SECONDS="${1:-1800}"
shift || true
if [[ "$#" -gt 0 ]]; then
  OPERATIONS=("$@")
else
  OPERATIONS=(read upsert)
fi
read -r -a LEVELS <<< "${CONCURRENCY_LEVELS:-1 4 8 16 32 64 128 256 512 1024 2048}"
BACKENDS=(core-python rust)

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="logs/sweep-${STAMP}"
mkdir -p "${LOG_DIR}"

n_points=$(( ${#OPERATIONS[@]} * ${#LEVELS[@]} * ${#BACKENDS[@]} ))
echo "=== Phase C: throughput / scaling sweep ==="
echo "    ops = ${OPERATIONS[*]}, concurrency ladder = ${LEVELS[*]}"
echo "    backends = ${BACKENDS[*]} (closed-loop; concurrency is the variable)"
echo "    per-point = ${DURATION_SECONDS}s, points = ${n_points}"
echo "    total sequential time ~= $(( DURATION_SECONDS * n_points / 3600 )) h"
echo "    logs -> ${LOG_DIR}"
echo

for op in "${OPERATIONS[@]}"; do
  for c in "${LEVELS[@]}"; do
    for bk in "${BACKENDS[@]}"; do
      wid="sweep-${op}-${bk}-c${c}-${STAMP}"
      log="${LOG_DIR}/${wid}.log"
      echo ">>> op=${op} concurrency=${c} backend=${bk} -> ${wid}"
      COSMOS_BACKEND="${bk}" \
      WORKLOAD_OPERATIONS="${op}" \
      COSMOS_CONCURRENT_REQUESTS="${c}" \
      WORKLOAD_ARRIVAL_RATE="0" \
      PERF_WORKLOAD_ID="${wid}" \
        timeout --signal=INT --preserve-status "${DURATION_SECONDS}s" \
          python3 workload.py >"${log}" 2>&1 || rc=$?
      rc="${rc:-0}"
      # 0/124/130 are all the expected timeout-stop (see run_latency_matrix.sh).
      if [[ "${rc}" != "0" && "${rc}" != "124" && "${rc}" != "130" ]]; then
        echo "    !! point exited rc=${rc}; see ${log}" >&2
      fi
      unset rc
    done
  done
done

echo
echo "=== Phase C complete. Read results from ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER},"
echo "    filtering workload_id LIKE 'sweep-%-${STAMP}', dropping warmup (elapsed_seconds > 600)."
echo "    For each op+backend, plot achieved req/s (SUM(count)/SUM(window_seconds)) and the"
echo "    tail against concurrency: the curve rises then FLATTENS at the single-process ceiling,"
echo "    and the two backends' lines reveal the crossover."
echo
echo "    SCALE-OUT (to push past one process toward the account's thousands/sec, esp. writes):"
echo "      pick the plateau concurrency C*, then run N copies in parallel and SUM their req/s, e.g.:"
echo "        for i in \$(seq 1 N); do ( export COSMOS_BACKEND=rust WORKLOAD_OPERATIONS=upsert \\"
echo "          COSMOS_CONCURRENT_REQUESTS=C* PERF_WORKLOAD_ID=scaleout-upsert-rust-p\$i-${STAMP}; \\"
echo "          timeout --signal=INT ${DURATION_SECONDS}s python3 workload.py ) & done; wait"
