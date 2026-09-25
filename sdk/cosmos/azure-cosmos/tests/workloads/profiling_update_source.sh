#!/usr/bin/env bash
# Select an explicit published Python SDK commit. Does not build or contact Cosmos.
# Usage: bash profiling_update_source.sh <40-character-commit>
set -euo pipefail
cd "$(dirname "$0")"
source ./profiling_common.sh
if [[ $# -ne 1 || ! "$1" =~ ^[0-9a-f]{40}$ || -v PROFILING_PYTHON_REF ]]; then
  echo "ERROR: supply one exact 40-character commit; PROFILING_PYTHON_REF/branch defaults are removed." >&2
  exit 2
fi
repo="$(profiling_python_repo)"
if profiling_repo_is_dirty "$repo"; then
  echo "ERROR: checkout has local changes; source will not be replaced." >&2
  exit 2
else
  status=$?
  [[ "$status" -eq 1 ]] || exit "$status"
fi
git -C "$repo" fetch origin "$1"
git -C "$repo" checkout --detach "$1"
if [[ "$(git -C "$repo" rev-parse HEAD)" != "$1" ]]; then
  echo "ERROR: checkout HEAD does not match the requested commit." >&2
  exit 1
fi
echo "Selected Python SDK commit: $1"
echo "The Rust driver remains Cargo's locked dependency."
echo "Next, explicitly run: bash ./profiling_build_extension.sh"
