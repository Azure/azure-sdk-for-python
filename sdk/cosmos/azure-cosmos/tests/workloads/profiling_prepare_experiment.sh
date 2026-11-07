#!/usr/bin/env bash
# Record the installed build, then validate and prepare test items.
# Source updates and builds are separate explicit commands.
# Usage: bash profiling_prepare_experiment.sh --confirm-target <endpoint> <database> <container>
set -euo pipefail
cd "$(dirname "$0")"
source ./profiling_common.sh || exit 2
for removed in PROFILING_SKIP_BUILD PROFILING_SKIP_SOURCE_UPDATE; do
  if [[ -v "$removed" ]]; then
    echo "ERROR: $removed is removed; preparation never updates or builds source." >&2
    exit 2
  fi
done
profiling_load_env
profiling_confirm_target "$@"
control="$(mktemp)" || exit 1
trap 'rm -f -- "$control"' EXIT
if ! bash ./profiling_create_session.sh read-preparation | tee "$control"; then
  echo "ERROR: profiling session creation failed; no test items were prepared." >&2
  exit 1
fi
PROFILING_SESSION_DIR="$(sed -n 's/^artifacts=//p' "$control")"
if [[ -z "$PROFILING_SESSION_DIR" || "$PROFILING_SESSION_DIR" == *$'\n'* ]]; then
  echo "ERROR: session creation did not identify one artifacts directory; no test items were prepared." >&2
  exit 1
fi
profiling_load_session "$PROFILING_SESSION_DIR"
cp "$control" "$PROFILING_SESSION_DIR/session-creation.log"
if ! bash ./profiling_prepare_test_items.sh "$@" 2>&1 | tee "$PROFILING_SESSION_DIR/test-item-preparation.log"; then
  echo "ERROR: preparation failed; inspect $PROFILING_SESSION_DIR/test-item-preparation.log." >&2
  exit 1
fi
profiling_load_session "$PROFILING_SESSION_DIR"
printf 'preparation_complete=true\n' > "$PROFILING_SESSION_DIR/preparation-completion.txt"
echo "=== Test items ready; no baseline has been executed ==="
echo "source ${PROFILING_SESSION_DIR}/session.env"
