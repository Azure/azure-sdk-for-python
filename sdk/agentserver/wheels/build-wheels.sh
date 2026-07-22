#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Maintainer-only: rebuild the checked-in preview wheels.
#
# Output: refreshes *.whl files in this directory (sdk/agentserver/wheels/)
#         alongside this script and README.md. Devs do NOT need to run this —
#         the wheels are checked in. See README.md for consumption.
#
# Wheels included (azure-ai-agentserver-{core, invocations, responses}):
#   - core         — resilient-task primitives + storage_paths
#   - invocations  — invocations protocol HTTP host
#   - responses    — responses protocol HTTP host
#
# When to run:
#   - After making source changes to any of the three packages that
#     need to ship in the demo's docker image.
#   - Before committing those source changes, so the wheels stay in sync.
#
# Usage (from anywhere):
#   sdk/agentserver/wheels/build-wheels.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

WHEELS_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTSERVER_ROOT="$(cd "$WHEELS_DIR/.." && pwd)"

PACKAGES=(
    "azure-ai-agentserver-core"
    "azure-ai-agentserver-invocations"
    "azure-ai-agentserver-responses"
)

echo "==> Rebuilding preview wheels into: $WHEELS_DIR"
# Remove any stale wheel files but preserve README.md and the script itself.
rm -f "$WHEELS_DIR"/*.whl

for pkg in "${PACKAGES[@]}"; do
    pkg_dir="$AGENTSERVER_ROOT/$pkg"
    if [[ ! -d "$pkg_dir" ]]; then
        echo "  !! Skipping $pkg — directory not found at $pkg_dir" >&2
        continue
    fi
    echo "  - $pkg"
    pip wheel --no-deps --quiet --wheel-dir "$WHEELS_DIR" "$pkg_dir"
done

echo ""
echo "==> Refreshed wheels:"
ls -la "$WHEELS_DIR"/*.whl

echo ""
echo "Next: git add sdk/agentserver/wheels/*.whl && commit."
