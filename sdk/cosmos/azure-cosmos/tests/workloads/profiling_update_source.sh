#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: get the source code that will be profiled.
#
# Updates the Python SDK/binding checkout to the requested ref. Cargo selects
# the driver's locked Git dependency when profiling_build_extension.sh builds.
#
# WHY IT REFUSES TO RUN ON A DIRTY CHECKOUT: uncommitted edits cannot be named
# by a commit hash alone. Skip this source-update step when deliberately profiling
# local changes; preserve those changes and their source fingerprint.
#
# This script does NOT build anything. Run profiling_build_extension.sh next.
#
# Usage:
#   ./profiling_update_source.sh
#   PROFILING_PYTHON_REF=your-feature-branch ./profiling_update_source.sh
#
# Override the branch only when profiling a feature branch on purpose.
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh

PYTHON_REF="${PROFILING_PYTHON_REF:-users/dibahl/python-sdk-with-rust-driver}"

# Update only this checkout. Cargo selects the driver's locked Git dependency.
PY_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [[ -z "${PY_DIR}" ]]; then
  echo "ERROR: $(pwd) is not a git checkout; cannot identify the Python SDK repo." >&2
  exit 2
fi

update_repo() {
  local label="$1" dir="$2" ref="$3"

  if ! git -C "${dir}" rev-parse --git-dir >/dev/null 2>&1; then
    echo "ERROR: ${label}: '${dir}' is not a git checkout." >&2
    echo "       Check the selected Python checkout path." >&2
    return 2
  fi

  echo ">>> ${label}: ${dir}"

  # Refuse before touching anything: a tree with ANY local modification cannot
  # be named by a commit. 'git diff' alone would miss staged and untracked
  # files, so a newly added source file would still be called clean.
  #
  # This refusal has no override, because the problem here is not the commit
  # record but the pull itself: fetching onto modified files either fails or
  # discards the operator's work. To profile local edits, skip this step and keep
  # the build, then allow the uncommitted tree at session time:
  #   PROFILING_SKIP_SOURCE_UPDATE=1 PROFILING_ALLOW_DIRTY=1 \
  #     ./prepare_profiling_environment.sh
  if profiling_repo_is_dirty "${dir}"; then
    echo "ERROR: ${label} has local changes. Commit or stash them first;" >&2
    echo "       a profile from an unnamed tree cannot be reproduced." >&2
    git -C "${dir}" status --short --untracked-files=normal >&2
    return 2
  fi

  git -C "${dir}" fetch origin || { echo "ERROR: ${label}: fetch failed." >&2; return 1; }
  git -C "${dir}" switch "${ref}" || { echo "ERROR: ${label}: no branch '${ref}'." >&2; return 1; }
  # --ff-only: never create a merge commit here. If the branch has diverged the
  # operator must resolve it deliberately, not inside a setup script.
  git -C "${dir}" pull --ff-only origin "${ref}" || {
    echo "ERROR: ${label}: '${ref}' could not fast-forward." >&2
    return 1
  }

  printf '    %s = %s (%s)\n' \
    "${label}" \
    "$(git -C "${dir}" rev-parse HEAD)" \
    "$(git -C "${dir}" rev-parse --abbrev-ref HEAD)"
}

echo "=== Updating profiling source ==="
rc=0
update_repo "azure-sdk-for-python" "${PY_DIR}"   "${PYTHON_REF}" || rc=$?
[[ ${rc} -eq 0 ]] || exit ${rc}
echo "The Rust driver is resolved from Cargo.toml/Cargo.lock during the build."
echo "The sibling Rust checkout is reference source and was not updated."

echo "=== Source updated. The extension is NOT rebuilt yet ==="
echo "    Next: ./profiling_build_extension.sh"
exit 0
