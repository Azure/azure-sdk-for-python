#!/usr/bin/env bash
# Stage agentserver @task preview wheels into the docker build context.
# Run this BEFORE 'azd up' or 'docker build'.
#
# Wheels are checked into the repo at sdk/agentserver/wheels/ — this
# script just copies them into a per-sample docker-build staging dir
# (src/resilient-research-agent/wheels/, gitignored) so the Dockerfile's
# `COPY wheels/ /tmp/wheels/` finds them at build time.
#
# To refresh the source wheels (maintainer-only — devs shouldn't need
# to do this), see ../../../../wheels/README.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
CENTRAL_WHEELS="$REPO_ROOT/sdk/agentserver/wheels"
STAGING_DIR="$SCRIPT_DIR/src/resilient-research-agent/wheels"

if [[ ! -d "$CENTRAL_WHEELS" ]] || ! ls "$CENTRAL_WHEELS"/*.whl >/dev/null 2>&1; then
    echo "ERROR: no checked-in wheels found at $CENTRAL_WHEELS" >&2
    echo "       Did you pull the latest from the agentserver demo branch?" >&2
    exit 1
fi

echo "==> Staging checked-in @task preview wheels into docker build context"
echo "    src:  $CENTRAL_WHEELS"
echo "    dst:  $STAGING_DIR"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp "$CENTRAL_WHEELS"/*.whl "$STAGING_DIR"/
ls -la "$STAGING_DIR"/*.whl

echo ""
echo "Done. Now run: azd up   (or docker build)"


