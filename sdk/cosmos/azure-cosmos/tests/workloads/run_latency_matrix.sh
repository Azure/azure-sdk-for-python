#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Phase A -- Latency / throughput matrix (sdkdev-dikshi drill).
#
# WHAT IT DOES, AND WHY THIS SHAPE:
#   Runs every point operation, on both backends, ONE AT A TIME. Latency is the
#   one measurement that CPU contention can quietly distort, so nothing else may
#   be running on the box while a run is timed -- hence strictly sequential, no
#   parallelism here. Each operation gets its OWN process (one operation per
#   process) so the throughput and CPU-per-op numbers are trustworthy (with all
#   six sharing a process they throttle and bleed into each other).
#
#   For each operation we run the BASELINE (core-python) and then the RUST run
#   BACK-TO-BACK, so neither lands in a quieter period on Cosmos and the only
#   thing that changed between them is the one COSMOS_BACKEND switch.
#
#   The whole matrix repeats (default twice) so the result is reproducible, not
#   a single lucky sample.
#
# USAGE:
#   source ./your-private-keys.sh      # exports COSMOS_KEY (+ RESULTS_COSMOS_KEY)
#   ./run_latency_matrix.sh [DURATION_SECONDS] [REPEATS]
#       DURATION_SECONDS  per-run length (default 7200 = 2 h; P99.9 needs hours)
#       REPEATS           how many times to run the whole matrix (default 2)
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"
source ./perf_env.sh

DURATION_SECONDS="${1:-7200}"
REPEATS="${2:-2}"

OPERATIONS=(read create upsert replace delete patch)
BACKENDS=(core-python rust)
# Operations the harness accepts in open-loop mode. create/delete are NOT
# supported there (each does an extra untimed step), so they always run
# closed-loop regardless of WORKLOAD_ARRIVAL_RATE.
OPENLOOP_OK=" read upsert replace patch "

STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="logs/latency-${STAMP}"
mkdir -p "${LOG_DIR}"

echo "=== Phase A: latency matrix ==="
echo "    per-run = ${DURATION_SECONDS}s, repeats = ${REPEATS}, ops = ${OPERATIONS[*]}"
echo "    backends = ${BACKENDS[*]} (baseline then rust, back-to-back per op)"
echo "    logs -> ${LOG_DIR}"
echo "    total sequential time ~= $(( DURATION_SECONDS * ${#OPERATIONS[@]} * ${#BACKENDS[@]} * REPEATS / 3600 )) h"
echo

for (( r=1; r<=REPEATS; r++ )); do
  for op in "${OPERATIONS[@]}"; do
    for bk in "${BACKENDS[@]}"; do
      # Decide the arrival mode for THIS op. Open-loop only if the user asked for
      # it (rate > 0) AND the op supports it; otherwise closed-loop.
      run_arrival="${WORKLOAD_ARRIVAL_RATE}"
      if [[ "${OPENLOOP_OK}" != *" ${op} "* ]]; then
        run_arrival="0"
      fi

      wid="lat-${op}-${bk}-r${r}-${STAMP}"
      log="${LOG_DIR}/${wid}.log"
      echo ">>> [repeat ${r}/${REPEATS}] op=${op} backend=${bk} arrival_rate=${run_arrival} -> ${wid}"

      # timeout sends SIGINT (--signal=INT) so the workload stops the same way a
      # Ctrl-C would, letting the reporter flush one final row on the way out.
      # --kill-after=120s is the safety net: if a cell ever SWALLOWS the SIGINT
      # (e.g. a teardown that blocks while joining an executor thread), timeout
      # escalates to SIGKILL after a 120s grace window so one wedged cell can
      # never stall the whole unattended matrix again. A SIGKILLed cell exits
      # 137 -> flagged below as a failure (visible) but the loop still continues.
      COSMOS_BACKEND="${bk}" \
      WORKLOAD_OPERATIONS="${op}" \
      WORKLOAD_ARRIVAL_RATE="${run_arrival}" \
      PERF_WORKLOAD_ID="${wid}" \
        timeout --signal=INT --kill-after=120s --preserve-status "${DURATION_SECONDS}s" \
          python3 workload.py >"${log}" 2>&1 || rc=$?
      rc="${rc:-0}"
      # Tightened exit classification (methodology flag #3 -- no ambiguous pass).
      # workload.py installs NO SIGINT handler and does NOT catch KeyboardInterrupt
      # at the top level, and the load loop never finishes on its own, so with
      # --preserve-status + --signal=INT there is exactly ONE clean outcome:
      #   130  KeyboardInterrupt propagated out of asyncio.run -> clean stop (expected).
      # Everything else is called out distinctly instead of being waved through:
      #   137  SIGKILL after the 120s grace -> the cell HUNG on stop (real failure).
      #   124  cannot occur with --preserve-status; if seen, timeout behaved
      #        unexpectedly (e.g. flags changed) -> treat as failure, don't hide it.
      #   0    the infinite load loop should never exit on its own; a 0 means it
      #        stopped early or swallowed the stop -> suspicious, flag it.
      # The loop always CONTINUES; flagging just makes a bad cell visible.
      case "${rc}" in
        130) ;;  # clean stop, the only expected outcome
        137) echo "    !! run KILLED after 120s grace (cell hung on stop); see ${log}" >&2 ;;
        124) echo "    !! run exited 124 (unexpected with --preserve-status); see ${log}" >&2 ;;
        0)   echo "    !! run exited 0 (load loop ended early / stop swallowed); see ${log}" >&2 ;;
        *)   echo "    !! run exited rc=${rc}; see ${log}" >&2 ;;
      esac
      unset rc
      echo "    done op=${op} backend=${bk}"
    done
  done
done

echo
echo "=== Phase A complete. Read results from ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER},"
echo "    filtering workload_id LIKE 'lat-%-${STAMP}' and dropping warmup rows (elapsed_seconds > 600)."
echo
# Integrity gate (methodology flags #2 and #4): refuse a silent "looks good".
# Before anyone reads a percentile, prove every cell did real, low-error work on
# both backends (check 0), that no reporting window was dropped (check 1), and
# that the reporter logged no failed writes (check 2). Non-zero exit => a hole
# the analyst must see. It never aborts the matrix (we are already done here);
# it just prints PASS/FAIL so an unattended run cannot pass unnoticed.
echo "=== Running post-run integrity gate ==="
if python3 perf_validate.py --stamp "${STAMP}" --log-dir "${LOG_DIR}"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect the rows/logs above before trusting results." >&2
fi
