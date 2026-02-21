#!/usr/bin/env bash
set -euo pipefail

# Simple local runner for the bilingual weekend planner container sample.
# Examples:
#   API_HOST=github GITHUB_TOKEN=... ./run.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.venv/bin/activate"
fi

PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -u "$SCRIPT_DIR/main.py"
