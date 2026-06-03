#!/usr/bin/env bash
# Stage agentserver wheels into the docker build context for this demo.
# Run this BEFORE 'azd up' or 'docker build'.
#
# We don't bundle wheels in the sample. Instead, we (re)build them from
# the shared script at sdk/agentserver/scripts/build-wheels.sh and copy
# them into the local docker build context (src/durable-research-agent/wheels/).
# The local wheels/ dir is gitignored and is just a build-time staging
# location.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
CENTRAL_BUILD="$REPO_ROOT/sdk/agentserver/scripts/build-wheels.sh"
CENTRAL_WHEELS="$REPO_ROOT/sdk/agentserver/wheels"
STAGING_DIR="$SCRIPT_DIR/src/durable-research-agent/wheels"

echo "==> (Re)building agentserver wheels via $CENTRAL_BUILD"
"$CENTRAL_BUILD"

echo ""
echo "==> Staging wheels into docker build context: $STAGING_DIR"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp "$CENTRAL_WHEELS"/*.whl "$STAGING_DIR"/
ls -la "$STAGING_DIR"/*.whl

echo ""
echo "Done. Now run: azd up   (or docker build)"

