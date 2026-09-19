#!/usr/bin/env bash
# Blended (mixed) workload run: one process issues a realistic MIX of operations
# instead of one operation type at a time. Inspect both blended and per-op tails.
#
# The selected mix is an experiment input, not a claim about every application.
#
#   ./run_mixed.sh 900                          # core-python + rust (default)
#   MIXED_BACKENDS=rust ./run_mixed.sh 900       # rust
#   MIXED_BACKENDS="core-python rust" ./run_mixed.sh 900
# Mix defaults to a read-heavy app profile; override with WORKLOAD_MIX.
# Results land in perfdb/perfresults-v2 tagged mixed-blend-<backend>-<stamp>;
# read them back with mixed_report.py.
set -euo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1
source ~/venvs/perfdrill/bin/activate
export WORKLOAD_USE_SYNC=false WORKLOAD_SKIP_CLOSE=false PERF_ENABLED=true

DURATION="${1:-900}"
perf_require_positive "${DURATION}"
BACKENDS=(${MIXED_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/mixed-${STAMP}"
perf_create_log_dir "$LOG_DIR" || exit 2

# Read-heavy realistic mix. Weights are relative (need not sum to 100).
export WORKLOAD_MIX="${WORKLOAD_MIX:-read=70,upsert=15,create=5,replace=5,patch=5}"
# Use the seeded probe container so reads/replace/patch have existing items.
export COSMOS_DATABASE="${MIXED_COSMOS_DATABASE:-lat_probe_db}"
export COSMOS_CONTAINER="${MIXED_COSMOS_CONTAINER:-lat_probe_cont}"
export COSMOS_CONCURRENT_REQUESTS="${COSMOS_CONCURRENT_REQUESTS:-100}"
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL="${PERF_REPORT_INTERVAL:-60}"
export COSMOS_MAX_ITEM_INDEX="${MIXED_MAX_ITEM_INDEX:-1000}"
write_run_manifest "${LOG_DIR}" "${STAMP}" "mixed"
for bk in "${BACKENDS[@]}"; do printf 'mixed-blend-%s-%s\n' "$bk" "$STAMP"; done >"${LOG_DIR}/expected-workloads.txt"

echo "=== Mixed/blended workload run ==="
echo "    stamp=${STAMP} dur=${DURATION}s backends=${BACKENDS[*]}"
echo "    mix=${WORKLOAD_MIX}  concurrency=${COSMOS_CONCURRENT_REQUESTS}"
echo "    container=${COSMOS_DATABASE}/${COSMOS_CONTAINER}  results -> perfdb/perfresults-v2 (mixed-%)"
echo
overall_rc=0

for bk in "${BACKENDS[@]}"; do
  wid="mixed-blend-${bk}-${STAMP}"
  log="${LOG_DIR}/${wid}.log"
  echo ">>> backend=${bk} -> ${wid}"
  # timeout sends SIGINT so the reporter flushes one final row; --kill-after
  # escalates if the process ever swallows the signal.
  if COSMOS_BACKEND="${bk}" PERF_WORKLOAD_ID="${wid}" \
    timeout --signal=INT --kill-after=120s --preserve-status "${DURATION}s" \
      python3 workload.py >"${log}" 2>&1; then
    rc=0
  else
    rc=$?
  fi
  echo "    rc=${rc}  log=${log}"
  if [[ "${rc}" -ne 0 ]]; then
    overall_rc=1
  fi
done
echo "=== Mixed run complete. stamp=${STAMP} ==="
echo
echo "=== Running mixed report + driver commit check ==="
BACKEND_CSV="$(IFS=,; echo "${BACKENDS[*]}")"
perf_check_run "${LOG_DIR}" "${STAMP}" "mixed-" "${BACKEND_CSV}" || overall_rc=1
# Lightweight post-run check for this mini-phase: confirm every rust row names
# the same driver build, and print blended/per-op pooled latency for this stamp.
if python3 mixed_report.py --prefix "mixed-" --stamp "${STAMP}"; then
  echo "=== mixed report driver commit check PASSED ==="
else
  echo "!! mixed report driver commit check FAILED -- inspect rows before trusting mixed metrics." >&2
  overall_rc=1
fi
exit "${overall_rc}"
