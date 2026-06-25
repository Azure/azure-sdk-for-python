#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Automated end-to-end resilient crash-recovery demo:
#   start agent (local store) -> run -> crash -> restart -> recover -> verify.
#
#   az login
#   export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
#   export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
#   ./run.sh
#
# Tunables (env): NUM_PHASES (default 3), CRASH_AFTER (default 1), PORT (8088).
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HERE/.venv}"

if [[ ! -d "$VENV" ]]; then
    echo "venv not found at $VENV — run ./setup.sh first." >&2
    exit 1
fi
: "${FOUNDRY_PROJECT_ENDPOINT:?set FOUNDRY_PROJECT_ENDPOINT (your Foundry project endpoint) and run 'az login' first}"

exec "$VENV/bin/python" "$HERE/recovery_demo.py"
