#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: prepare one terminal to run profiling commands.
#
# SOURCE this file; do not execute it:
#
#     source ./profiling_activate.sh
#
# Executing it would set everything inside a child process that exits
# immediately, taking the settings with it. Sourcing runs it in the current
# shell, so the values stay.
#
# It loads, in the order the fallbacks require:
#   ~/perf_secrets.env   account keys (not checked in)
#   ./profiling_target.env  which account/container/range/load to profile
#                           (checked in; ~/perf_target.env overrides it)
#   ./perf_env.sh        shared fallbacks, results sink, helper functions
#   ~/venvs/perfdrill    the Python environment holding the built extension
# and then the most recent session opened by profiling_start_session.sh, so
# RUN_ID and ARTIFACTS point at somewhere real.
#
# Use it when opening a second terminal, or coming back to a session later.
# It does NOT update source, build, seed, or start a workload. To prepare the
# environment from scratch, run ./prepare_profiling_environment.sh instead.
#
# Usage:
#   source ./profiling_activate.sh                       # latest session
#   source ./profiling_activate.sh point-read-profile-20260810-180432717
# ---------------------------------------------------------------------------

# Guard against being executed rather than sourced: without this the failure is
# silent and confusing, because the script "succeeds" and nothing is set.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this file, do not run it:" >&2
  echo "    source ./profiling_activate.sh" >&2
  exit 2
fi

_profiling_activate() {
  local here session_name session_dir candidate
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  cd "${here}" || return 1

  # Same loader every profiling step uses, so a terminal prepared here behaves
  # identically to one prepared by prepare_profiling_environment.sh. A missing
  # piece is fatal there and here.
  # shellcheck disable=SC1091
  source ./profiling_common.sh || return 1
  profiling_load_env || return $?

  session_name="${1:-}"
  if [[ -n "${session_name}" ]]; then
    if [[ ! "${session_name}" =~ ^[A-Za-z0-9._-]+-[0-9]{8}-[0-9]{9}$ ]]; then
      echo "ERROR: invalid session directory name '${session_name}'." >&2
      return 1
    fi
    session_dir="${here}/artifacts/${session_name}"
    if [[ ! -d "${session_dir}" ]]; then
      echo "ERROR: no session directory ${session_dir}" >&2
      return 1
    fi
    profiling_load_session "${session_dir}" || return 1
  else
    # Select the newest COMPLETE session, not merely the newest directory. A
    # failed preparation can leave a newer partial directory behind.
    session_dir=""
    while IFS= read -r candidate; do
      if profiling_load_session "${candidate}"; then
        session_dir="${candidate%/}"
        break
      fi
      unset RUN_ID ARTIFACTS PERF_PHASE
      echo "WARNING: skipping incomplete session ${candidate%/}" >&2
    done < <(ls -1dt "${here}"/artifacts/*/ 2>/dev/null || true)
  fi

  if [[ -n "${session_dir}" ]]; then
    echo "profiling terminal ready"
    echo "    target   : ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
    echo "    python   : ${VIRTUAL_ENV}"
    echo "    run_id   : ${RUN_ID}"
    echo "    artifacts: ${ARTIFACTS}"
  else
    echo "profiling terminal ready (no session loaded)"
    echo "    target   : ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
    echo "    python   : ${VIRTUAL_ENV}"
    echo "    Start one with ./profiling_start_session.sh"
  fi
}

_profiling_activate "$@"
# Preserve the function's status: without this the sourced file's status would
# be that of 'unset -f', which always succeeds, so a failed activation would
# report success to the caller.
_profiling_activate_rc=$?
unset -f _profiling_activate
return "${_profiling_activate_rc}"
