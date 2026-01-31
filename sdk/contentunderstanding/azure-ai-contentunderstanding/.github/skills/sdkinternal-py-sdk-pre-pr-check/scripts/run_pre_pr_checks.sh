#!/bin/bash
# Pre-PR Check Script for azure-ai-contentunderstanding
# Runs all required CI checks before creating a pull request
#
# Usage: ./run_pre_pr_checks.sh [--fast] [--all]
#   --fast: Use uv for faster package installation
#   --all:  Also run optional checks (verifytypes)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
TOX_INI="$PACKAGE_DIR/../../../eng/tox/tox.ini"

# Parse arguments
USE_UV=false
RUN_ALL=false

for arg in "$@"; do
    case $arg in
        --fast)
            USE_UV=true
            shift
            ;;
        --all)
            RUN_ALL=true
            shift
            ;;
        *)
            ;;
    esac
done

cd "$PACKAGE_DIR"
echo "Running pre-PR checks in: $PACKAGE_DIR"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "=========================================="
    echo "WARNING: No virtual environment detected!"
    echo "=========================================="
    echo ""
    echo "Please activate a virtual environment before running this script:"
    echo ""
    echo "  # Create venv if it doesn't exist"
    echo "  cd $PACKAGE_DIR"
    echo "  python -m venv .venv"
    echo ""
    echo "  # Activate venv"
    echo "  source .venv/bin/activate  # Linux/macOS"
    echo "  # .venv\\Scripts\\activate   # Windows"
    echo ""
    echo "  # Install dependencies"
    echo "  pip install -e ."
    echo "  pip install -r dev_requirements.txt"
    echo "  pip install \"tox<5\" black bandit"
    echo ""
    echo "Or run the setup script:"
    echo "  $PACKAGE_DIR/.github/skills/sdkinternal-py-env-setup-venv/scripts/setup_venv.sh"
    echo ""
    read -p "Continue without venv? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Please activate venv and try again."
        exit 1
    fi
    echo ""
fi

# Set tox pip implementation
if $USE_UV; then
    export TOX_PIP_IMPL=uv
    echo "Using uv for faster package installation"
    echo ""
fi

# Track results
PYLINT_RESULT=0
MYPY_RESULT=0
PYRIGHT_RESULT=0
BLACK_RESULT=0
BANDIT_RESULT=0
SPHINX_RESULT=0
TESTS_RESULT=0
VERIFYTYPES_RESULT=0

# Required checks
echo "=========================================="
echo "=== Step 1/7: Running Pylint (Required) ==="
echo "=========================================="
if tox -e pylint -c "$TOX_INI" --root .; then
    echo "✓ Pylint passed"
else
    PYLINT_RESULT=1
    echo "✗ Pylint failed"
fi
echo ""

echo "=========================================="
echo "=== Step 2/7: Running MyPy (Required) ==="
echo "=========================================="
if tox -e mypy -c "$TOX_INI" --root .; then
    echo "✓ MyPy passed"
else
    MYPY_RESULT=1
    echo "✗ MyPy failed"
fi
echo ""

echo "=========================================="
echo "=== Step 3/7: Running Pyright (Required) ==="
echo "=========================================="
if tox -e pyright -c "$TOX_INI" --root .; then
    echo "✓ Pyright passed"
else
    PYRIGHT_RESULT=1
    echo "✗ Pyright failed"
fi
echo ""

echo "=========================================="
echo "=== Step 4/7: Running Black (Required) ==="
echo "=========================================="
if python -m black --check azure/; then
    echo "✓ Black passed"
else
    BLACK_RESULT=1
    echo "✗ Black failed (run 'black azure/' to auto-format)"
fi
echo ""

echo "=========================================="
echo "=== Step 5/7: Running Bandit (Required) ==="
echo "=========================================="
if python -m bandit -r azure/ -x "azure/**/tests/**" -q; then
    echo "✓ Bandit passed"
else
    BANDIT_RESULT=1
    echo "✗ Bandit failed"
fi
echo ""

echo "=========================================="
echo "=== Step 6/7: Running Sphinx (Required) ==="
echo "=========================================="
if tox -e sphinx -c "$TOX_INI" --root .; then
    echo "✓ Sphinx passed"
else
    SPHINX_RESULT=1
    echo "✗ Sphinx failed"
fi
echo ""

echo "=============================================="
echo "=== Step 7/7: Running Tests (Playback Mode) ==="
echo "=============================================="
if AZURE_TEST_RUN_LIVE=false pytest; then
    echo "✓ Tests passed"
else
    TESTS_RESULT=1
    echo "✗ Tests failed"
fi
echo ""

# Optional checks (if --all specified)
if $RUN_ALL; then
    echo "=========================================="
    echo "=== Optional: Running Verifytypes ==="
    echo "=========================================="
    if tox -e verifytypes -c "$TOX_INI" --root .; then
        echo "✓ Verifytypes passed"
    else
        VERIFYTYPES_RESULT=1
        echo "✗ Verifytypes failed (optional)"
    fi
    echo ""
fi

# Summary
echo "=========================================="
echo "=== Summary ==="
echo "=========================================="
echo ""

REQUIRED_FAILED=0

if [ $PYLINT_RESULT -eq 0 ]; then
    echo "✓ Pylint:  PASSED"
else
    echo "✗ Pylint:  FAILED (CI blocking)"
    REQUIRED_FAILED=1
fi

if [ $MYPY_RESULT -eq 0 ]; then
    echo "✓ MyPy:    PASSED"
else
    echo "✗ MyPy:    FAILED (CI blocking)"
    REQUIRED_FAILED=1
fi

if [ $PYRIGHT_RESULT -eq 0 ]; then
    echo "✓ Pyright: PASSED"
else
    echo "✗ Pyright: FAILED (CI blocking)"
    REQUIRED_FAILED=1
fi

if [ $BLACK_RESULT -eq 0 ]; then
    echo "✓ Black:   PASSED"
else
    echo "✗ Black:   FAILED (CI blocking) - run 'black azure/' to fix"
    REQUIRED_FAILED=1
fi

if [ $BANDIT_RESULT -eq 0 ]; then
    echo "✓ Bandit:  PASSED"
else
    echo "✗ Bandit:  FAILED (CI blocking)"
    REQUIRED_FAILED=1
fi

if [ $SPHINX_RESULT -eq 0 ]; then
    echo "✓ Sphinx:  PASSED"
else
    echo "✗ Sphinx:  FAILED (release blocking)"
    REQUIRED_FAILED=1
fi

if [ $TESTS_RESULT -eq 0 ]; then
    echo "✓ Tests:   PASSED"
else
    echo "✗ Tests:   FAILED (release blocking)"
    REQUIRED_FAILED=1
fi

if $RUN_ALL; then
    if [ $VERIFYTYPES_RESULT -eq 0 ]; then
        echo "✓ Verifytypes: PASSED (optional)"
    else
        echo "✗ Verifytypes: FAILED (optional)"
    fi
fi

echo ""

if [ $REQUIRED_FAILED -eq 0 ]; then
    echo "=========================================="
    echo "=== All required checks passed! ==="
    echo "=== Ready to create PR ==="
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "=== Some required checks failed! ==="
    echo "=== Please fix issues before creating PR ==="
    echo "=========================================="
    exit 1
fi
