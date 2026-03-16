#!/usr/bin/env bash
# Sets up (or refreshes) the development virtual environment.
# Usage: ./scripts/setup-dev-env.sh [--python <path>] [--force]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_CMD=""
FORCE=false

usage() {
    echo "Usage: ./scripts/setup-dev-env.sh [--python <path>] [--force]"
    echo ""
    echo "Options:"
    echo "  --python <path>  Path to a specific Python interpreter (default: python3 or python)"
    echo "  --force          Recreate the virtual environment even if it already exists"
    echo "  --help           Show this help message"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --python) PYTHON_CMD="$2"; shift 2 ;;
        --force)  FORCE=true; shift ;;
        --help)   usage ;;
        *)        echo "Unknown option: $1"; usage ;;
    esac
done

# Resolve Python interpreter
if [[ -z "$PYTHON_CMD" ]]; then
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    else
        echo "[setup] ERROR: Could not find a Python interpreter. Install Python 3.10+ or pass --python."
        exit 1
    fi
fi

# Verify Python version
PY_VERSION=$("$PYTHON_CMD" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 10 ]]; }; then
    echo "[setup] ERROR: Python 3.10+ is required (found $PY_VERSION). Use --python to specify a compatible interpreter."
    exit 1
fi
echo "[setup] Using Python $PY_VERSION ($PYTHON_CMD)"

# Create or recreate virtual environment
if [[ -d "$VENV_DIR" ]] && $FORCE; then
    echo "[setup] Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "[setup] Creating virtual environment at .venv ..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
else
    echo "[setup] Virtual environment already exists at .venv (use --force to recreate)"
fi

# Upgrade pip and install
echo "[setup] Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet

echo "[setup] Installing package in editable mode with dev dependencies..."
"$VENV_DIR/bin/pip" install -e "$PROJECT_ROOT[dev]" --quiet

echo ""
echo "[setup] Development environment ready."
echo ""
echo "Activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Verify installation:"
echo "  python -m pytest --version"
echo "  ruff --version"
echo "  mypy --version"
