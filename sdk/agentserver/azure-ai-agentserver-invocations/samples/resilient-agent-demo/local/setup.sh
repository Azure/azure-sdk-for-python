#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# One-time setup: create a local venv and install the preview wheels + the
# demo's runtime dependencies. Re-run any time to refresh.
#
#   ./setup.sh
#
# Override the interpreter or venv location:
#   PYTHON=python3.12 VENV=/tmp/resilient-inv-venv ./setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WHEELS="$(cd "$HERE/../../../../wheels" && pwd)"
VENV="${VENV:-$HERE/.venv}"
PYTHON="${PYTHON:-python3}"

echo "==> Creating venv: $VENV"
"$PYTHON" -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip

echo "==> Installing preview wheels from: $WHEELS"
"$VENV/bin/pip" install --quiet "$WHEELS"/*.whl

echo "==> Installing demo runtime deps (azure-ai-projects, azure-identity, httpx)"
"$VENV/bin/pip" install --quiet azure-ai-projects==2.0.1 azure-identity==1.25.3 httpx

echo ""
echo "Done. Next:"
echo "  az login"
echo "  export FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>"
echo "  export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o   # a model deployment in that project"
echo "  ./run.sh        # automated crash -> recover demo"
echo "  ./serve.sh      # or run the agent yourself for manual exploration"
