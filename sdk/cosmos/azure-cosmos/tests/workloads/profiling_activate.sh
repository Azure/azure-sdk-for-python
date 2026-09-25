#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: prepare one terminal to run profiling commands.
#
# SOURCE this file; do not execute it:
#
#     source ./profiling_activate.sh <session-directory-name>
#
# Executing it would set everything inside a child process that exits
# immediately, taking the settings with it. Sourcing runs it in the current
# shell, so the values stay.
#
# It activates ~/venvs/perfdrill, loads ~/profiling_config.env and
# ~/perf_secrets.env, supplies shared functions from perf_common.sh,
# and loads the explicitly selected session opened by profiling_start_session.sh, so
# PROFILING_SESSION_ID and ARTIFACTS identify saved evidence.
#
# Use it when opening a second terminal, or coming back to a session later.
# It does NOT update source, build, seed, or start a workload. To prepare the
# test items and their evidence, run profiling_prepare_experiment.sh with
# explicit --confirm-target arguments. Updating source/building are separate.
#
# Usage:
#   source ./profiling_activate.sh point-read-profile-20260810-180432717
# ---------------------------------------------------------------------------

# Guard against being executed rather than sourced: without this the failure is
# silent and confusing, because the script "succeeds" and nothing is set.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "ERROR: source this file, do not run it:" >&2
  echo "    source ./profiling_activate.sh <session-directory-name>" >&2
  exit 2
fi

_profiling_activate() {
  local here session_name session_dir
  if [[ $# -ne 1 || -z "$1" ]]; then
    echo "ERROR: specify one profiling session directory name; automatic newest-session selection is removed." >&2
    return 2
  fi
  session_name="$1"
  if [[ ! "${session_name}" =~ ^[A-Za-z0-9._-]+-[0-9]{8}-[0-9]{9}$ ]]; then
    echo "ERROR: invalid session directory name '${session_name}'." >&2
    return 1
  fi
  here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  cd "${here}" || return 1

  # Same loader every profiling step uses. A missing
  # piece is fatal there and here.
  # shellcheck disable=SC1091
  source ./profiling_common.sh || return 1
  profiling_load_env || return $?

  session_dir="${here}/artifacts/${session_name}"
  if [[ ! -d "${session_dir}" ]]; then
    echo "ERROR: no session directory ${session_dir}" >&2
    return 1
  fi
  profiling_load_session "${session_dir}" || return 1

  echo "profiling terminal ready"
  echo "    target   : ${COSMOS_DATABASE}/${COSMOS_CONTAINER}"
  echo "    python   : ${VIRTUAL_ENV}"
  echo "    profiling_session_id: ${PROFILING_SESSION_ID}"
  echo "    artifacts: ${ARTIFACTS}"
}

_profiling_activate "$@"
# Preserve the function's status: without this the sourced file's status would
# be that of 'unset -f', which always succeeds, so a failed activation would
# report success to the caller.
_profiling_activate_rc=$?
unset -f _profiling_activate
return "${_profiling_activate_rc}"
