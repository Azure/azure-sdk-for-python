#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Phase C SCALE-OUT -- how far does the account scale PAST one process?
#
# WHAT IT DOES, AND WHY THIS SHAPE:
#   run_throughput_sweep.sh finds each engine's SINGLE-process ceiling and knee
#   concurrency C*. One Python process is GIL- and single-connection-pool-bound,
#   so its ceiling is NOT the account's ceiling. This script pins concurrency at
#   C* and fans OUT: for each process count N in a ladder it launches N copies of
#   the workload IN PARALLEL, each writing its own rows, and scaleout_report.py
#   SUMS their achieved req/s. The output is the aggregate throughput curve vs N
#   and the scaling efficiency (how close to linear the account stays).
#
#   Each N-point runs ALONE (points are sequential): the N processes of one point
#   are the only load on the box, so their summed req/s is a clean measurement and
#   two points never contend. Within a point the N processes run concurrently.
#
# REPEATABILITY (why the rep loop and ABBA order):
#   A single pass can be fooled by time drift (a quieter minute on Cosmos) or by
#   order (whichever engine ran first got the fresh box). With SCALEOUT_REPEATS>1
#   the whole ladder is repeated; scaleout_report.py pools the reps and prints
#   their spread so a headline number is shown to be stable, not lucky. When more
#   than one backend is swept, the backend ORDER is flipped every other rep (ABBA:
#   A B / B A / A B ...) so engine and running-order are decorrelated.
#
# RU BUDGET (accurate write scale-out):
#   Writes cost ~10x a read in RU. To scale writes out without the account's RU
#   ceiling (429s) masquerading as a scaling limit, raise scale_cont throughput
#   for the write block and drop it back afterward:
#     az cosmosdb sql container throughput update -g SDKDEV-DIKSHI-RG \
#       -a sdkdev-dikshi -d scale_db -n scale_cont --throughput 1000000
#   scaleout_report.py surfaces the 429 rate so an RU ceiling is visible, not silent.
#
# USAGE:
#   source ./your-private-keys.sh      # exports COSMOS_KEY (+ RESULTS_COSMOS_KEY)
#   ./run_scaleout_sweep.sh [DURATION_SECONDS] [ops...]
#       DURATION_SECONDS  per N-point (default 900 = 15 min; >warmup 600 leaves
#                         ~5 min of steady state after the report's warmup drop)
#       ops               operations to fan out (default: read)
#   Env overrides:
#       SCALEOUT_CONCURRENCY  knee concurrency C* to pin per process (default 256).
#                             Run reads and writes as SEPARATE invocations if their
#                             knees differ (e.g. read c256, upsert c512).
#       SCALEOUT_N_LEVELS     process-count ladder (default "1 2 4 8 12 16").
#       SCALEOUT_BACKENDS     backends to sweep (default "rust").
#       SCALEOUT_REPEATS      passes over the whole ladder (default 1; use 3 to
#                             prove the curve is not a time/order artifact).
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")"
source ./perf_env.sh

# Phase C scale-out uses the same canonical rig as the single-process Phase C run.
# Keep caller override support (`SCALE_COSMOS_DATABASE` / `SCALE_COSMOS_CONTAINER`)
# for controlled what-if runs, but warn if host/target differs from the documented
# baseline so comparisons are not mislabeled.
if [[ -n "${SCALE_COSMOS_DATABASE:-}" ]]; then
  export COSMOS_DATABASE="${SCALE_COSMOS_DATABASE}"
fi
if [[ -n "${SCALE_COSMOS_CONTAINER:-}" ]]; then
  export COSMOS_CONTAINER="${SCALE_COSMOS_CONTAINER}"
fi

host_name="$(hostname 2>/dev/null || echo unknown)"
if [[ "${host_name}" != "vm-python-phasec" ]]; then
  echo "!! WARNING: Phase C scale-out is calibrated for vm-python-phasec; current host=${host_name}" >&2
fi
if [[ "${COSMOS_DATABASE}" != "scale_db" || "${COSMOS_CONTAINER}" != "scale_cont" ]]; then
  echo "!! WARNING: Phase C canonical container is scale_db/scale_cont; current target=${COSMOS_DATABASE}/${COSMOS_CONTAINER}" >&2
fi

DURATION_SECONDS="${1:-900}"
shift || true
if [[ "$#" -gt 0 ]]; then
  OPERATIONS=("$@")
else
  OPERATIONS=(read)
fi

CONC="${SCALEOUT_CONCURRENCY:-256}"
read -r -a N_LEVELS <<< "${SCALEOUT_N_LEVELS:-1 2 4 8 12 16}"
read -r -a BACKENDS <<< "${SCALEOUT_BACKENDS:-rust}"
REPEATS="${SCALEOUT_REPEATS:-1}"

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/scaleout-${STAMP}"
mkdir -p "${LOG_DIR}"
write_run_manifest "${LOG_DIR}" "${STAMP}" "C-scaleout-sweep"

# Rough peak process fan-out, for the reader's situational awareness.
max_n=0; for n in "${N_LEVELS[@]}"; do (( n > max_n )) && max_n="${n}"; done
echo "=== Phase C: scale-out sweep ==="
echo "    host = ${host_name}"
echo "    target = ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
echo "    ops = ${OPERATIONS[*]}, pinned concurrency C* = ${CONC}"
echo "    process ladder N = ${N_LEVELS[*]} (peak ${max_n} parallel processes)"
echo "    backends = ${BACKENDS[*]}, repeats = ${REPEATS} (ABBA order when >1 backend)"
echo "    per N-point = ${DURATION_SECONDS}s; container = ${COSMOS_DATABASE}/${COSMOS_CONTAINER} @ ${COSMOS_THROUGHPUT} RU"
echo "    logs -> ${LOG_DIR}"
echo

overall_rc=0

for (( rep=1; rep<=REPEATS; rep++ )); do
  # ABBA: flip backend order every other rep so engine != running-order.
  if (( rep % 2 == 1 )); then
    order=("${BACKENDS[@]}")
  else
    order=()
    for (( k=${#BACKENDS[@]}-1; k>=0; k-- )); do order+=("${BACKENDS[k]}"); done
  fi
  echo ">>> rep ${rep}/${REPEATS}: backend order = ${order[*]}"

  for op in "${OPERATIONS[@]}"; do
    for bk in "${order[@]}"; do
      for n in "${N_LEVELS[@]}"; do
        echo "    op=${op} backend=${bk} N=${n} c=${CONC} rep=${rep}: launching ${n} process(es)"
        pids=()
        for (( i=1; i<=n; i++ )); do
          wid="scaleout-${op}-${bk}-c${CONC}-N${n}-r${rep}-p${i}-${STAMP}"
          log="${LOG_DIR}/${wid}.log"
          (
            export COSMOS_BACKEND="${bk}"
            export WORKLOAD_OPERATIONS="${op}"
            export COSMOS_CONCURRENT_REQUESTS="${CONC}"
            export WORKLOAD_ARRIVAL_RATE="0"
            export PERF_WORKLOAD_ID="${wid}"
            timeout --signal=INT --kill-after=120s --preserve-status "${DURATION_SECONDS}s" \
              python3 workload.py >"${log}" 2>&1
          ) &
          pids+=("$!")
        done
        # Wait for every process of THIS point; capture real child exit codes.
        for pid in "${pids[@]}"; do
          rc=0
          wait "${pid}" || rc=$?
          case "${rc}" in
            0|130) ;;   # 0 clean; 130 = SIGINT->KeyboardInterrupt, data OK
            *) echo "    !! pid=${pid} (op=${op} bk=${bk} N=${n}) exited rc=${rc}" >&2
               overall_rc=1 ;;
          esac
        done
      done
    done
  done
done

echo
echo "=== Scale-out sweep complete. Raw rows in ${RESULTS_COSMOS_DATABASE}/${RESULTS_COSMOS_CONTAINER},"
echo "    workload_id LIKE 'scaleout-%-${STAMP}'."
echo
echo "=== Running scale-out report (Phase C) ==="
if python3 scaleout_report.py --stamp "${STAMP}" --prefix "scaleout-"; then
  echo "=== scale-out provenance gate PASSED ==="
else
  echo "!! scale-out provenance gate FAILED -- explain the flagged points before trusting the curve." >&2
  overall_rc=1
fi

echo
if [[ "${overall_rc}" != "0" ]]; then
  echo "=== Phase C scale-out FINISHED WITH WARNINGS (a child failed or the gate failed); exit ${overall_rc}. ===" >&2
else
  echo "=== Phase C scale-out OK (all processes clean, gate passed). ==="
fi
exit "${overall_rc}"
