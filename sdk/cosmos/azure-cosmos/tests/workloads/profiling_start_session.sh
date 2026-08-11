#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: open one profiling session.
#
# It:
#   - mints RUN_ID, a UTC timestamp in the YYYYMMDD-HHMMSSmmm shape the
#     reporting tools expect (latency_report.py --run-id). Milliseconds keep
#     two sessions started in the same second apart.
#   - creates artifacts/<phase>-<RUN_ID>/ for captures, logs and reports.
#   - writes manifest-<RUN_ID>.json recording the build, host, account, load
#     and results sink. No secrets are written to it.
#   - writes session.env, which the operator sources to get RUN_ID and
#     ARTIFACTS into their terminal. A child process cannot export variables
#     back to the shell that started it, hence the printed 'source' line.
#
# RUN_ID is used both as the artifacts directory name and as the tail of every
# workload_id written to Cosmos DB, so rows and local files can be matched:
#
#   RUN_ID     20260810-180432717
#   directory  artifacts/point-read-profile-20260810-180432717/
#   row tag    workload_id = baseline-read-rust-20260810-180432717
#                            ^prefix  ^op ^backend ^RUN_ID
#
# The tag shape is required, not cosmetic: reports select rows with
# STARTSWITH(c.workload_id, @prefix) AND ENDSWITH(c.workload_id, @run_id).
# If PERF_WORKLOAD_ID is unset, perf_config.py falls back to a random UUID;
# rows are still written but no report can ever match them.
#
# Preparation fails here when the manifest is missing, unparseable, has no
# commit hashes, or either repository has uncommitted changes, because the
# recorded commits would not describe the code that ran. PROFILING_ALLOW_DIRTY=1
# allows a dirty tree; the manifest still records dirty=true.
#
# Usage:
#   ./profiling_start_session.sh                      # phase: point-read-profile
#   ./profiling_start_session.sh my-experiment        # custom phase label
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh

PHASE="${1:-point-read-profile}"
# The phase becomes a directory name and a JSON string value, so it is checked
# before either is built from it.
profiling_validate_phase "${PHASE}" || exit 2

profiling_load_env || exit 2
profiling_verify_extension_build || exit 1

# Milliseconds match the YYYYMMDD-HHMMSSmmm shape the reporting tools document,
# and keep two sessions started in the same second from colliding. date's %N is
# not portable, so fall back to zeros rather than mint a malformed id.
_ns="$(date +%N 2>/dev/null || echo 000000000)"
[[ "${_ns}" =~ ^[0-9]{9}$ ]] || _ns="000000000"
RUN_ID="$(date -u +%Y%m%d-%H%M%S)${_ns:0:3}"
ARTIFACTS="$PWD/artifacts/${PHASE}-${RUN_ID}"
mkdir -p "$ARTIFACTS" || { echo "ERROR: cannot create ${ARTIFACTS}" >&2; exit 1; }

# One JSON record of the build/host/account/load behind everything in this
# directory. Defined in perf_env.sh; best-effort, never writes secrets.
# RUN_ID is passed as its "stamp" argument, so the manifest's "stamp" field and
# RUN_ID are the same value under the two names the suite already uses.
write_run_manifest "$ARTIFACTS" "$RUN_ID" "$PHASE"

MANIFEST="${ARTIFACTS}/manifest-${RUN_ID}.json"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "ERROR: no manifest was written at ${MANIFEST}." >&2
  echo "       Without it the session cannot record which build produced its" >&2
  echo "       numbers, so preparation stops here." >&2
  exit 1
fi

python3 - "$MANIFEST" "${PROFILING_ALLOW_DIRTY:-0}" <<'PY'
import json
import sys

manifest_path, allow_dirty = sys.argv[1], sys.argv[2] == "1"

try:
    with open(manifest_path) as handle:
        manifest = json.load(handle)
except Exception as exc:
    print(f"    manifest is not readable JSON: {exc}")
    sys.exit(1)

build = manifest.get("build")
if not isinstance(build, dict):
    print("    manifest has no build section")
    sys.exit(1)

problems = []

# Uncommitted code cannot be named by a commit hash, so a profile taken from it
# cannot be reproduced or compared.
for field in ("git_dirty", "rust_driver_dirty"):
    if build.get(field) is True:
        problems.append(f"{field}=true (built from uncommitted code)")

# Without these the row cannot be traced back to source at all.
for field in (
    "git_commit",
    "rust_driver_commit",
    "rust_extension_path",
    "rust_extension_python_commit",
    "rust_extension_driver_commit",
):
    if build.get(field) in (None, "", "unknown", "none"):
        problems.append(f"{field} is unknown")

if build.get("rust_extension_python_commit") != build.get("git_commit"):
    problems.append("loaded extension Python commit differs from checkout commit")
if build.get("rust_extension_driver_commit") != build.get("rust_driver_commit"):
    problems.append("loaded extension Rust-driver commit differs from checkout commit")

# The path proof in the next document depends on this counter existing.
if build.get("rust_extension_has_operation_counter") != "True":
    problems.append("the loaded _rust extension has no operation_count()")

if not problems:
    print("    build record complete: commits recorded, both checkouts clean")
    sys.exit(0)

for problem in problems:
    print(f"    !! {problem}")

dirty_only = all("dirty" in problem for problem in problems)
if dirty_only and allow_dirty:
    print("    PROFILING_ALLOW_DIRTY=1: continuing, but the recorded commits do")
    print("    not describe the code that will run")
    sys.exit(0)
sys.exit(1)
PY
if [[ $? -ne 0 ]]; then
  echo "ERROR: the session's build record is incomplete (see above). Preparation" >&2
  echo "       stops here because these numbers could not be tied to a build." >&2
  echo "       Commit the changes, or rebuild, then re-run." >&2
  exit 1
fi

# The operator's shell needs these; a child process cannot export into it.
SESSION_ENV="${ARTIFACTS}/session.env"
cat > "${SESSION_ENV}" <<EOF
export RUN_ID="${RUN_ID}"
export ARTIFACTS="${ARTIFACTS}"
export PERF_PHASE="${PHASE}"
EOF
profiling_load_session "${ARTIFACTS}" || {
  echo "ERROR: generated session failed validation." >&2
  exit 1
}

printf 'artifacts=%s\ntarget=%s/%s\nrun_id=%s\n' \
  "$ARTIFACTS" "$COSMOS_DATABASE" "$COSMOS_CONTAINER" "$RUN_ID" \
  | tee "$ARTIFACTS/run.txt"

echo
echo "=== Session ${RUN_ID} open ==="
echo "    Tag every workload with a matching id, for example:"
echo "        PERF_WORKLOAD_ID=baseline-read-rust-${RUN_ID}"
echo "    and read its rows back with:"
echo "        python3 latency_report.py --prefix baseline- --run-id ${RUN_ID}"
echo
echo "    Load this session into the current terminal:"
echo "        source ${SESSION_ENV}"
exit 0
