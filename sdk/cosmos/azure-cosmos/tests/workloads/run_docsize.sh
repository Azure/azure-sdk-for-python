#!/usr/bin/env bash
# Document size/shape sensitivity run: does the latency/RU conclusion hold beyond
# one document shape? Runs a CREATE leg with the DEFAULT (732-byte flat) body and
# again with the LARGE (4,670-byte nested) body, for each backend.
#
# Why: every other phase uses one fixed item shape. Bigger, deeper documents cost
# more to serialize, transfer and index, so a conclusion drawn on one shape may not
# generalize. This is a modest two-point check (default vs large), not a full matrix.
#
# Why CREATE (not upsert): create writes fresh test-<uuid> items and deletes them
# again (untimed cleanup), so it NEVER overwrites the shared seeded test-<N> items
# the way an upsert leg would. That keeps the large-body writes from bloating the
# probe container and skewing later read-based phases -- no dedicated container or
# reseeding needed. This is a write-shape test; a read-side size test is deferred.
#
#   ./run_docsize.sh 600                          # core-python + rust (default)
#   DOCSIZE_BACKENDS=rust ./run_docsize.sh 600     # rust
#   DOCSIZE_BACKENDS="core-python rust" ./run_docsize.sh 600
# Results land in perfdb/perfresults tagged docsize-create-<backend>-<profile>-<stamp>;
# read them back with latency_report.py --prefix docsize- (backend column shows
# <backend>-<profile>, e.g. core-python-large).
set -uo pipefail
cd "$(dirname "$0")"
source ~/perf_secrets.env
source ./perf_env.sh >/dev/null 2>&1
source ~/venvs/perfdrill/bin/activate

DURATION="${1:-600}"
DOCSIZE_PROFILES_RAW="${DOCSIZE_PROFILES:-default,large}"
DOCSIZE_PROFILES_RAW="${DOCSIZE_PROFILES_RAW//,/ }"
read -r -a PROFILES <<< "${DOCSIZE_PROFILES_RAW}"
if [[ "${#PROFILES[@]}" -eq 0 ]]; then
  echo "ERROR: DOCSIZE_PROFILES is empty. Provide at least one profile." >&2
  exit 2
fi
BACKENDS=(${DOCSIZE_BACKENDS:-core-python rust})

_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
STAMP="$(date +%Y%m%d-%H%M%S)${_ns:0:3}"
LOG_DIR="logs/docsize-${STAMP}"
mkdir -p "$LOG_DIR"

# Use the shared probe container. The CREATE leg self-cleans (fresh uuids), so it
# does not mutate the seeded items -- no dedicated container needed.
# perf_env.sh exports scale_db/scale_cont, so we must set probe defaults explicitly.
export COSMOS_DATABASE="${DOCSIZE_COSMOS_DATABASE:-lat_probe_db}"
export COSMOS_CONTAINER="${DOCSIZE_COSMOS_CONTAINER:-lat_probe_cont}"
export COSMOS_CONCURRENT_REQUESTS="${COSMOS_CONCURRENT_REQUESTS:-100}"
export WORKLOAD_NUM_CLIENTS=1
export WORKLOAD_ARRIVAL_RATE=0
export WORKLOAD_USE_PROXY=false
export COSMOS_REQUEST_TIMEOUT=30
export PERF_REPORT_INTERVAL="${PERF_REPORT_INTERVAL:-60}"
export WORKLOAD_OPERATIONS=create

echo "=== Document size/shape sensitivity run ==="
echo "    stamp=${STAMP} dur=${DURATION}s profiles=${PROFILES[*]} backends=${BACKENDS[*]}"
echo "    op=create concurrency=${COSMOS_CONCURRENT_REQUESTS}"
echo "    container=${COSMOS_DATABASE}/${COSMOS_CONTAINER}  results -> perfdb/perfresults (docsize-%)"
echo
overall_rc=0

for prof in "${PROFILES[@]}"; do
  for bk in "${BACKENDS[@]}"; do
    # op field is the real op (create) so latency_report's _OP_ORDER matches; the
    # profile is folded into the backend segment, so _split_wid reads
    # backend="<bk>-<profile>" (e.g. core-python-large) and shows one row per
    # backend/profile. "rust" stays inside the backend string so the provenance
    # gate still fires on rust rows.
    wid="docsize-create-${bk}-${prof}-${STAMP}"
    log="${LOG_DIR}/${wid}.log"
    echo ">>> profile=${prof} backend=${bk} -> ${wid}"
    if COSMOS_BACKEND="${bk}" WORKLOAD_DOC_PROFILE="${prof}" PERF_WORKLOAD_ID="${wid}" \
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
done
echo "=== Doc-size run complete. stamp=${STAMP} ==="
echo
echo "=== Running doc-size report + provenance gate ==="
# Lightweight post-run gate for this mini-phase: validate Rust driver provenance
# and print pooled create latency per backend/profile for this stamp.
if python3 latency_report.py --prefix "docsize-" --run-id "${STAMP}"; then
  echo "=== doc-size report provenance gate PASSED ==="
else
  echo "!! doc-size report provenance gate FAILED -- inspect rows before trusting payload-size metrics." >&2
  overall_rc=1
fi
exit "${overall_rc}"
