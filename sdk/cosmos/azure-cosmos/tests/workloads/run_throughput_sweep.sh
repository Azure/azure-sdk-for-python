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
#   The most important output is not a single faster/slower verdict, but the
#   honest shape of how each backend scales.
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

# Phase C canonical target for this drill:
# - VM: vm-python-phasec
# - Container: scale_db/scale_cont
# Keep caller override support (`SCALE_COSMOS_DATABASE` / `SCALE_COSMOS_CONTAINER`)
# for controlled experiments, but warn when running on a different host/target so
# a mislabeled run is visible in logs.
if [[ -n "${SCALE_COSMOS_DATABASE:-}" ]]; then
  export COSMOS_DATABASE="${SCALE_COSMOS_DATABASE}"
fi
if [[ -n "${SCALE_COSMOS_CONTAINER:-}" ]]; then
  export COSMOS_CONTAINER="${SCALE_COSMOS_CONTAINER}"
fi

host_name="$(hostname 2>/dev/null || echo unknown)"
if [[ "${host_name}" != "vm-python-phasec" ]]; then
  echo "!! WARNING: Phase C throughput sweep is calibrated for vm-python-phasec; current host=${host_name}" >&2
fi
if [[ "${COSMOS_DATABASE}" != "scale_db" || "${COSMOS_CONTAINER}" != "scale_cont" ]]; then
  echo "!! WARNING: Phase C canonical container is scale_db/scale_cont; current target=${COSMOS_DATABASE}/${COSMOS_CONTAINER}" >&2
fi

DURATION_SECONDS="${1:-1800}"
shift || true
if [[ "$#" -gt 0 ]]; then
  OPERATIONS=("$@")
else
  OPERATIONS=(read upsert)
fi
read -r -a LEVELS <<< "${CONCURRENCY_LEVELS:-1 4 8 16 32 64 128 256 512 1024 2048}"
BACKENDS=(core-python rust)

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/sweep-${STAMP}"
mkdir -p "${LOG_DIR}"
write_run_manifest "${LOG_DIR}" "${STAMP}" "C-throughput-sweep"

n_points=$(( ${#OPERATIONS[@]} * ${#LEVELS[@]} * ${#BACKENDS[@]} ))
echo "=== Phase C: throughput / scaling sweep ==="
echo "    host = ${host_name}"
echo "    target = ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
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
        timeout --signal=INT --kill-after=120s --preserve-status "${DURATION_SECONDS}s" \
          python3 workload.py >"${log}" 2>&1 || rc=$?
      rc="${rc:-0}"
      # Graceful stop => exit 0 is the expected clean outcome (see
      # run_latency_matrix.sh). 130 = SIGINT fell back to KeyboardInterrupt
      # (handler did not engage; data OK but worth noticing); 137 = hung on stop;
      # 124 = unexpected with --preserve-status. Flag everything but 0.
      case "${rc}" in
        0)   ;;
        130) echo "    !! point exited 130 (graceful handler did not engage; data OK); see ${log}" >&2 ;;
        137) echo "    !! point KILLED after 120s grace (hung on stop); see ${log}" >&2 ;;
        124) echo "    !! point exited 124 (unexpected with --preserve-status); see ${log}" >&2 ;;
        *)   echo "    !! point exited rc=${rc}; see ${log}" >&2 ;;
      esac
      unset rc
    done
  done
done

echo
echo "=== Running post-run integrity gate (Phase C) ==="
# Same gate Phase A runs: prove every cell did real, low-error work on both
# backends, dropped no reporting window, and -- critically for the drill's
# biggest error source -- that each row actually ran on the engine it claims
# (binding_calls provenance, --prefix sweep-). A failure here fails the script
# (the sweep itself is already done) so an unattended run cannot pass unnoticed.
overall_rc=0
if python3 perf_validate.py --stamp "${STAMP}" --log-dir "${LOG_DIR}" --prefix "sweep-"; then
  echo "=== integrity gate PASSED ==="
else
  echo "!! integrity gate FAILED -- inspect the rows/logs above before trusting results." >&2
  overall_rc=1
fi

echo
echo "=== Running automated scaling verdict (Phase C) ==="
# Replaces the old "plot req/s vs concurrency and read the knee/crossover off the
# chart by eye" instruction. scale_verdict.py pools throughput per point, finds
# the saturation knee automatically (first level whose gain over the previous one
# drops below 5%), flags error/CPU saturation, and reports the rust-vs-core
# crossover -- all reproducibly. It exits non-zero on a provenance violation.
if python3 scale_verdict.py --stamp "${STAMP}" --prefix "sweep-"; then
  echo "=== scaling verdict provenance gate PASSED ==="
else
  echo "!! scaling verdict provenance gate FAILED -- explain the flagged points before trusting the knee/crossover." >&2
  overall_rc=1
fi

echo
echo "    SCALE-OUT (to push past one process toward the account's thousands/sec, esp. writes):"
echo "      take the plateau concurrency C* the verdict reports above, then run N copies in"
echo "      parallel and SUM their req/s, e.g.:"
echo "        for i in \$(seq 1 N); do ( export COSMOS_BACKEND=rust WORKLOAD_OPERATIONS=upsert \\"
echo "          COSMOS_CONCURRENT_REQUESTS=C* PERF_WORKLOAD_ID=scaleout-upsert-rust-p\$i-${STAMP}; \\"
echo "          timeout --signal=INT ${DURATION_SECONDS}s python3 workload.py ) & done; wait"

echo
if [[ "${overall_rc}" != "0" ]]; then
  echo "=== Phase C FAILED (a provenance/integrity gate failed); exit ${overall_rc}. ===" >&2
else
  echo "=== Phase C OK (all gates passed). ==="
fi
exit "${overall_rc}"
