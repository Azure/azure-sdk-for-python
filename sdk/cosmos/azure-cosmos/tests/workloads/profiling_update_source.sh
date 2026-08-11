#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# RESPONSIBILITY: get the source code that will be profiled.
#
# Fetches the latest commits for BOTH repositories the profiled build is made
# from, and prints the commit each one landed on:
#
#   azure-sdk-for-python  - the Python SDK and the PyO3 binding
#   azure-sdk-for-rust    - the Cosmos driver the binding compiles against
#
# WHY BOTH: azure_cosmos_rust/Cargo.toml points Cargo at the SIBLING
# azure-sdk-for-rust checkout, so the compiled extension contains whatever
# driver commit is checked out there. Updating only the Python repo produces a
# build whose Rust half is silently stale, and no later step would notice.
#
# WHY IT REFUSES TO RUN ON A DIRTY CHECKOUT: uncommitted edits cannot be named
# by a commit hash. A profile taken from them cannot be reproduced or compared
# against another run, which is the whole point of recording which commits were
# built.
#
# This script does NOT build anything. Run profiling_build_extension.sh next.
#
# Usage:
#   ./profiling_update_source.sh
#   PROFILING_PYTHON_REF=users/dibahl/python-sdk-with-rust-driver \
#     PROFILING_RUST_REF=main ./profiling_update_source.sh
#
# Override the branch only when profiling a feature branch on purpose.
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")"

source ./profiling_common.sh

PYTHON_REF="${PROFILING_PYTHON_REF:-users/dibahl/python-sdk-with-rust-driver}"
RUST_REF="${PROFILING_RUST_REF:-main}"

# The Python repo is the one this script lives in. The Rust driver is its
# sibling, matching the path dependency in azure_cosmos_rust/Cargo.toml.
PY_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [[ -z "${PY_DIR}" ]]; then
  echo "ERROR: $(pwd) is not a git checkout; cannot identify the Python SDK repo." >&2
  exit 2
fi
RUST_DIR="${AZURE_SDK_FOR_RUST_DIR:-${PY_DIR}/../azure-sdk-for-rust}"

update_repo() {
  local label="$1" dir="$2" ref="$3"

  if [[ ! -d "${dir}/.git" ]]; then
    echo "ERROR: ${label}: '${dir}' is not a git checkout." >&2
    echo "       Clone it there, or set AZURE_SDK_FOR_RUST_DIR to its location." >&2
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
update_repo "azure-sdk-for-rust"   "${RUST_DIR}" "${RUST_REF}"   || rc=$?
[[ ${rc} -eq 0 ]] || exit ${rc}

echo "=== Source updated. The extension is NOT rebuilt yet ==="
echo "    Next: ./profiling_build_extension.sh"
exit 0
