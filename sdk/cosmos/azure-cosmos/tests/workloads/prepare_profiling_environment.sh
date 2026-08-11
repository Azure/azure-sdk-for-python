#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: the one command an operator runs to prepare a profiling VM.
#
# It runs the five setup steps in the order their dependencies require, and
# stops at the first failure, so a later step cannot hide an earlier one:
#
#   1  profiling_update_source.sh      fetch both repos, refuse a dirty tree
#   2  profiling_build_extension.sh    build _rust, prove which file is imported
#   3  profiling_check_target.sh       confirm account, item range, load, tools
#   4  profiling_seed_probe_data.sh    create the probe items if any are missing
#   5  profiling_start_session.sh      mint RUN_ID, artifacts dir, manifest
#
# WHY THIS ORDER: each step would invalidate the ones before it if moved later.
# Pulling new commits after building would leave the built extension stale.
# Seeding before checking the account could write 1,001 items into the wrong
# container. Opening the session last means the manifest records the build that
# was actually just produced, rather than the one that happened to be there.
#
# Steps 1 and 2 are skippable for the common case of profiling the same build
# again, which is the slowest part and often unchanged. They must be skipped
# TOGETHER: pulling new commits while reusing an old extension would produce a
# manifest whose recorded commits do not describe the code that actually ran,
# which is exactly what the manifest's commit fields exist to record.
#
#   ./prepare_profiling_environment.sh                 # full preparation
#   PROFILING_SKIP_BUILD=1 PROFILING_SKIP_SOURCE_UPDATE=1 \
#     ./prepare_profiling_environment.sh               # reuse current build
#
# Environment files this expects on the VM:
#   ~/perf_secrets.env      COSMOS_KEY and friends. The ONLY file not checked
#                           in, because it holds credentials. Permission 600.
#   ./profiling_target.env  which account, container, item range and load this
#                           session profiles. Checked in; holds no secrets.
#                           An operator copy at ~/perf_target.env overrides it.
#
# Usage:
#   ./prepare_profiling_environment.sh
#   ./prepare_profiling_environment.sh my-experiment   # session phase label
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

PHASE="${1:-point-read-profile}"

SKIP_SOURCE="${PROFILING_SKIP_SOURCE_UPDATE:-0}"
SKIP_BUILD="${PROFILING_SKIP_BUILD:-0}"

# Updating source without rebuilding leaves the loaded extension describing
# older commits than the manifest records. Refuse the combination rather than
# produce a session that cannot be cited.
if [[ "${SKIP_BUILD}" == "1" && "${SKIP_SOURCE}" != "1" ]]; then
  echo "ERROR: PROFILING_SKIP_BUILD=1 without PROFILING_SKIP_SOURCE_UPDATE=1." >&2
  echo "       That would pull new commits and then profile the OLD compiled" >&2
  echo "       extension, so the manifest would record commits that never ran." >&2
  echo "       To profile the build already on this VM:" >&2
  echo "           PROFILING_SKIP_BUILD=1 PROFILING_SKIP_SOURCE_UPDATE=1 \\" >&2
  echo "             ./prepare_profiling_environment.sh" >&2
  exit 2
fi

run_step() {
  local number="$1" script="$2"
  shift 2
  echo
  echo "############################################################"
  echo "# Step ${number}: ${script}"
  echo "############################################################"
  if [[ ! -x "./${script}" ]]; then
    # Checked-out scripts can lose the executable bit; bash runs them anyway.
    bash "./${script}" "$@"
  else
    "./${script}" "$@"
  fi
  local rc=$?
  if [[ ${rc} -ne 0 ]]; then
    echo >&2
    echo "!! Step ${number} (${script}) failed with rc=${rc}. Stopping." >&2
    echo "   Later steps would build on an environment that is already wrong." >&2
    exit ${rc}
  fi
}

echo "=== Preparing the profiling environment ==="
echo "    phase: ${PHASE}"

# Validate the phase before any step runs, so a bad label fails in a second
# rather than after a rebuild.
source ./profiling_common.sh
profiling_validate_phase "${PHASE}" || exit 2

if [[ "${SKIP_SOURCE}" == "1" ]]; then
  echo
  echo "# Step 1 skipped (PROFILING_SKIP_SOURCE_UPDATE=1): profiling the commits"
  echo "# already checked out on this VM."
else
  run_step 1 profiling_update_source.sh
fi

if [[ "${SKIP_BUILD}" == "1" ]]; then
  echo
  echo "# Step 2 skipped (PROFILING_SKIP_BUILD=1): reusing the extension already"
  echo "# installed in the perfdrill environment. Source was not updated either,"
  echo "# so the manifest still describes the code that is loaded."
else
  run_step 2 profiling_build_extension.sh
fi

run_step 3 profiling_check_target.sh
run_step 4 profiling_seed_probe_data.sh
run_step 5 profiling_start_session.sh "${PHASE}"

echo
echo "=== Environment ready ==="
echo "    The session directory and manifest are listed above. Load the session"
echo "    into this terminal with the 'source' line printed by step 5, then"
echo "    continue with 03-path-proof-and-baseline.md to prove a read really"
echo "    entered Rust before capturing any profile."
exit 0
