#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Phase C SCALE-OUT -- how far does the account scale PAST one process?
#
# WHAT IT DOES, AND WHY THIS SHAPE:
#   Hold per-process wave size fixed while changing the number of processes.
#   Points are sequential; processes within a point run concurrently. Other host
#   traffic is not controlled by this script. The report sums per-process average
#   rates, which need aligned intervals before claiming exact account throughput.
#
# REPEATABILITY (why the rep loop and ABBA order):
#   A single pass can be fooled by time drift (a quieter minute on Cosmos) or by
#   order (whichever engine ran first got the fresh box). With SCALEOUT_REPEATS>1
#   the whole ladder is repeated; scaleout_report.py pools the reps and prints
#   their spread so a headline number is shown to be stable, not lucky. When more
#   than one backend is swept, the backend ORDER is flipped every other rep (ABBA:
#   A B / B A / A B ...) so engine and running-order are decorrelated.
#
# RU BUDGET:
#   Inspect actual returned charges and throttling before attributing low gains
#   to the SDK. Capacity changes are an operator decision, not an automatic step.
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
perf_single_operation_shape
export WORKLOAD_ARRIVAL_RATE=0

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
perf_require_positive "${DURATION_SECONDS}" "${REPEATS}" "${CONC}" "${N_LEVELS[@]}"

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/scaleout-${STAMP}"
perf_create_log_dir "${LOG_DIR}" || exit 2
write_run_manifest "${LOG_DIR}" "${STAMP}" "C-scaleout-sweep"
for (( rep=1; rep<=REPEATS; rep++ )); do
  for op in "${OPERATIONS[@]}"; do
    for bk in "${BACKENDS[@]}"; do
      for n in "${N_LEVELS[@]}"; do
        for (( i=1; i<=n; i++ )); do
          printf 'scaleout-%s-%s-c%s-N%s-r%s-p%s-%s\n' "$op" "$bk" "$CONC" "$n" "$rep" "$i" "$STAMP"
        done
      done
    done
  done
done >"${LOG_DIR}/expected-workloads.txt"

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
            0) ;;
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
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
perf_check_run "${LOG_DIR}" "${STAMP}" "scaleout-" "${BACKEND_CSV}" || overall_rc=1
if python3 scaleout_report.py --stamp "${STAMP}" --prefix "scaleout-"; then
  echo "=== scale-out backend check PASSED ==="
else
  echo "!! scale-out backend check FAILED -- explain the flagged points before trusting the curve." >&2
  overall_rc=1
fi

echo
if [[ "${overall_rc}" != "0" ]]; then
  echo "=== Phase C scale-out FINISHED WITH WARNINGS (a child failed or the gate failed); exit ${overall_rc}. ===" >&2
else
  echo "=== Phase C scale-out OK (all processes clean, gate passed). ==="
fi
exit "${overall_rc}"
