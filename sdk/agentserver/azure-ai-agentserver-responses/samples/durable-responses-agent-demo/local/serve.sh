#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Start the durable agent locally (file-backed durable store, no hosted task
# API) so you can drive it yourself — stream a response, crash it, reconnect.
# See README.md "Manual exploration" for the curl recipe.
#
#   az login
#   export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
#   export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
#   ./serve.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HERE/.venv}"
MAIN="$HERE/../src/durable-responses-agent-demo/main.py"

if [[ ! -d "$VENV" ]]; then
    echo "venv not found at $VENV — run ./setup.sh first." >&2
    exit 1
fi
: "${FOUNDRY_PROJECT_ENDPOINT:?set FOUNDRY_PROJECT_ENDPOINT (your Foundry project endpoint) and run 'az login' first}"

# Local durable backend — this is what removes the hosted /tasks API dependency.
export AGENTSERVER_TASKS_BACKEND=local
export AGENTSERVER_DURABLE_ROOT="${AGENTSERVER_DURABLE_ROOT:-$HERE/.durable}"
# Enables the "crash" input sentinel so you can trigger a crash on demand.
export DEMO_MODE=1
export AZURE_AI_MODEL_DEPLOYMENT_NAME="${AZURE_AI_MODEL_DEPLOYMENT_NAME:-gpt-4o}"
export NUM_PHASES="${NUM_PHASES:-3}"
export INTRA_PHASE_COOLDOWN_SEC="${INTRA_PHASE_COOLDOWN_SEC:-1}"
export INTER_PHASE_COOLDOWN_SEC="${INTER_PHASE_COOLDOWN_SEC:-1}"
export TARGET_OUTPUT_TOKENS="${TARGET_OUTPUT_TOKENS:-80}"
export PORT="${PORT:-8088}"

echo "Starting durable agent on http://localhost:${PORT}"
echo "  durable root : ${AGENTSERVER_DURABLE_ROOT}  (tasks + responses are file-backed here)"
echo "  crash input  : POST /responses with input \"crash\"  (DEMO_MODE=1)"
echo "  stop         : Ctrl-C"
exec "$VENV/bin/python" "$MAIN"
