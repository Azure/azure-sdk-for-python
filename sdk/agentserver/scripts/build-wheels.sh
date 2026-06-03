#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Build distributable wheels for the agentserver pre-release packages.
#
# Output:
#   sdk/agentserver/wheels/azure_ai_agentserver_core-<version>-py3-none-any.whl
#   sdk/agentserver/wheels/azure_ai_agentserver_invocations-<version>-py3-none-any.whl
#
# Use these wheels until the agentserver packages are published to PyPI.
# See ../docs/USING_PRE_RELEASE_WHEELS.md for how to consume them.
#
# Usage (from anywhere):
#   sdk/agentserver/scripts/build-wheels.sh
# Or:
#   cd sdk/agentserver && scripts/build-wheels.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENTSERVER_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WHEELS_DIR="$AGENTSERVER_ROOT/wheels"

PACKAGES=(
    "azure-ai-agentserver-core"
    "azure-ai-agentserver-invocations"
)

echo "==> Building agentserver wheels into: $WHEELS_DIR"
rm -rf "$WHEELS_DIR"
mkdir -p "$WHEELS_DIR"

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
echo "==> Built wheels:"
ls -la "$WHEELS_DIR"/*.whl

echo ""
echo "Next: see sdk/agentserver/docs/USING_PRE_RELEASE_WHEELS.md for consumption."
