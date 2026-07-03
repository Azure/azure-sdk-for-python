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

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/latency-${STAMP}"
mkdir -p "${LOG_DIR}"
write_run_manifest "${LOG_DIR}" "${STAMP}" "A-latency-matrix"

echo "=== Phase A: latency matrix ==="
echo "    per-run = ${DURATION_SECONDS}s, repeats = ${REPEATS}, ops = ${OPERATIONS[*]}"
echo "    backends = ${BACKENDS[*]} (baseline then rust, back-to-back per op)"
echo "    logs -> ${LOG_DIR}"
echo "    total sequential time ~= $(( DURATION_SECONDS * ${#OPERATIONS[@]} * ${#BACKENDS[@]} * REPEATS / 3600 )) h"
echo
overall_rc=0

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
      # Exit classification (no ambiguous pass).
      # workload.py installs an asyncio SIGINT/SIGTERM handler that sets a stop
      # event; the load loop polls it between waves and exits NORMALLY, so the
      # client closes cleanly and the process returns 0. With --preserve-status
      # that makes 0 the single clean outcome. The load loop never finishes on
      # its own, so a 0 can ONLY come from a handled stop -- it is unambiguous.
      #   0    graceful stop: handler fired, client closed cleanly (expected).
      #   130  SIGINT fell back to KeyboardInterrupt (handler NOT installed, e.g.
      #        an old workload.py or a non-main thread). The cell still stopped and
      #        its data is intact, but flag it so a handler regression is visible.
      #   137  SIGKILL after the 120s grace -> the cell HUNG on stop (real failure).
      #   124  cannot occur with --preserve-status; if seen, timeout behaved
      #        unexpectedly (e.g. flags changed) -> treat as failure, don't hide it.
      # The loop always CONTINUES; flagging just makes a bad cell visible.
      case "${rc}" in
        0)   ;;  # graceful clean stop, the expected outcome
        130) echo "    !! run exited 130 (SIGINT fell back to KeyboardInterrupt; graceful handler did not engage -- data OK, check workload.py is current); see ${log}" >&2 ;;
        137) echo "    !! run KILLED after 120s grace (cell hung on stop); see ${log}" >&2; overall_rc=1 ;;
        124) echo "    !! run exited 124 (unexpected with --preserve-status); see ${log}" >&2; overall_rc=1 ;;
        *)   echo "    !! run exited rc=${rc}; see ${log}" >&2; overall_rc=1 ;;
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
# Integrity gate: before anyone reads a percentile, prove every cell did real,
# low-error work on both backends, that no reporting window was dropped, and that
# the reporter logged no failed writes. It never aborts the matrix; it just prints
# PASS/FAIL so an unattended run cannot pass unnoticed.
echo "=== Running post-run integrity gate ==="
if python3 perf_validate.py --stamp "${STAMP}" --log-dir "${LOG_DIR}" --prefix "lat-"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect the rows/logs above before trusting results." >&2
  overall_rc=1
fi
if [[ "${overall_rc}" != "0" ]]; then
  echo "=== Phase A finished with failures/warnings requiring triage; exit ${overall_rc}. ===" >&2
else
  echo "=== Phase A OK (all points clean; integrity gate passed). ==="
fi
exit "${overall_rc}"
