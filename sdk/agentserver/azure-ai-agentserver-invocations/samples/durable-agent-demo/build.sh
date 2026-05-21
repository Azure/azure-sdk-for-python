#!/usr/bin/env bash
# Build local wheel packages for docker image.
# Run this BEFORE 'azd up' or 'docker build'.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
WHEELS_DIR="$SCRIPT_DIR/src/durable-research-agent/wheels"

echo "==> Building wheels from local agentserver packages..."
rm -rf "$WHEELS_DIR"
mkdir -p "$WHEELS_DIR"

# Build core
echo "  Building azure-ai-agentserver-core..."
pip wheel --no-deps --wheel-dir "$WHEELS_DIR" \
    "$REPO_ROOT/sdk/agentserver/azure-ai-agentserver-core"

# Build invocations
echo "  Building azure-ai-agentserver-invocations..."
pip wheel --no-deps --wheel-dir "$WHEELS_DIR" \
    "$REPO_ROOT/sdk/agentserver/azure-ai-agentserver-invocations"

echo "==> Wheels built in $WHEELS_DIR:"
ls -la "$WHEELS_DIR"/*.whl

echo ""
echo "Done! Now run: azd up (or docker build)"
