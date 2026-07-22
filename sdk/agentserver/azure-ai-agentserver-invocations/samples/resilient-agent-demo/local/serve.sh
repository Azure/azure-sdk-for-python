#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Start the resilient research agent locally (file-backed state store, no hosted
# task API) so you can drive it yourself. See README.md "Manual exploration".
#
#   az login
#   export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
#   export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
#   ./serve.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${VENV:-$HERE/.venv}"
APP="$HERE/../src/resilient-research-agent/app.py"

if [[ ! -d "$VENV" ]]; then
    echo "venv not found at $VENV — run ./setup.sh first." >&2
    exit 1
fi
: "${FOUNDRY_PROJECT_ENDPOINT:?set FOUNDRY_PROJECT_ENDPOINT (your Foundry project endpoint) and run 'az login' first}"

# Local resilient backend — this is what removes the hosted /tasks API dependency.
export AGENTSERVER_TASKS_BACKEND=local
export AGENTSERVER_STATE_ROOT="${AGENTSERVER_STATE_ROOT:-$HERE/.agentserver}"
# Pin the session so a restart's recovery scan finds the in-progress task.
export FOUNDRY_AGENT_SESSION_ID="${FOUNDRY_AGENT_SESSION_ID:-local-demo-session}"
# Enables the "crash" message sentinel so you can trigger a crash on demand.
export DEMO_MODE=1
export AZURE_AI_MODEL_DEPLOYMENT_NAME="${AZURE_AI_MODEL_DEPLOYMENT_NAME:-gpt-4o}"
export NUM_PHASES="${NUM_PHASES:-3}"
export INTRA_PHASE_COOLDOWN_SEC="${INTRA_PHASE_COOLDOWN_SEC:-1}"
export INTER_PHASE_COOLDOWN_SEC="${INTER_PHASE_COOLDOWN_SEC:-1}"
export TARGET_OUTPUT_TOKENS="${TARGET_OUTPUT_TOKENS:-80}"
export PORT="${PORT:-8088}"

# Fail fast with a clear message if the port is already taken.
if "$VENV/bin/python" -c "import socket,sys; s=socket.socket(); r=s.connect_ex(('127.0.0.1', ${PORT})); s.close(); sys.exit(0 if r==0 else 1)"; then
    echo "Port ${PORT} is already in use (a server may still be running). Stop it, or pick another port: PORT=8090 ./serve.sh" >&2
    exit 1
fi

echo "Starting resilient research agent on http://localhost:${PORT}"
echo "  task store   : ${AGENTSERVER_STATE_ROOT}/tasks   (streams + checkpoints under ~/.agentserver-tasks)"
echo "  session id   : ${FOUNDRY_AGENT_SESSION_ID}  (must match across restarts to recover)"
echo "  crash input  : POST /invocations {\"message\":\"crash\"}   (DEMO_MODE=1)"
echo "  stop         : Ctrl-C"
exec "$VENV/bin/python" "$APP"
