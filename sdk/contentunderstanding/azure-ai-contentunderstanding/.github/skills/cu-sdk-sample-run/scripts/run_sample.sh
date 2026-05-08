#!/bin/bash
# Run a specific sample for Azure AI Content Understanding SDK
# Usage: ./run_sample.sh <sample_name>
# Example: ./run_sample.sh sample_analyze_url
#          ./run_sample.sh sample_analyze_url_async

set -e

# Determine script directory and package root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SAMPLES_DIR="$PACKAGE_ROOT/samples"
ASYNC_SAMPLES_DIR="$SAMPLES_DIR/async_samples"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() { echo -e "${BLUE}$1${NC}"; }
print_success() { echo -e "${GREEN}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }

# Function to list available samples
list_samples() {
    echo ""
    print_info "=== Available Sync Samples ==="
    for f in "$SAMPLES_DIR"/sample_*.py; do
        [ -f "$f" ] && echo "  $(basename "$f" .py)"
    done
    echo ""
    print_info "=== Available Async Samples ==="
    for f in "$ASYNC_SAMPLES_DIR"/sample_*_async.py; do
        [ -f "$f" ] && echo "  $(basename "$f" .py)"
    done
    echo ""
}

show_help() {
    cat <<EOF
Usage: $(basename "$0") <sample_name> [options]

Run a Python SDK sample for Azure AI Content Understanding.

Arguments:
  <sample_name>   Sample name (e.g. sample_analyze_url), with or without .py
                  extension. Append "_async" to run the async variant.

Options:
  --list, -l      List all available samples and exit.
  --help, -h      Show this help message.

Examples:
  $(basename "$0") sample_analyze_url
  $(basename "$0") sample_analyze_invoice.py
  $(basename "$0") sample_analyze_url_async
  $(basename "$0") --list
EOF
}

# Check for --help / --list flags
case "$1" in
    --help|-h) show_help; exit 0 ;;
    --list|-l) list_samples; exit 0 ;;
esac

# Check if sample name is provided
if [ -z "$1" ]; then
    print_error "Error: No sample name provided"
    echo ""
    echo "Usage: $0 <sample_name>"
    echo ""
    echo "Examples:"
    echo "  $0 sample_analyze_url"
    echo "  $0 sample_analyze_url_async"
    echo "  $0 sample_analyze_invoice.py"
    echo ""
    echo "Run '$0 --list' to see all available samples"
    exit 1
fi

# Normalize sample name (remove .py extension if present)
SAMPLE_NAME="${1%.py}"

# Determine if it's an async sample
if [[ "$SAMPLE_NAME" == *"_async" ]]; then
    IS_ASYNC=true
    SAMPLE_FILE="$ASYNC_SAMPLES_DIR/${SAMPLE_NAME}.py"
    RUN_DIR="$ASYNC_SAMPLES_DIR"
else
    IS_ASYNC=false
    SAMPLE_FILE="$SAMPLES_DIR/${SAMPLE_NAME}.py"
    RUN_DIR="$SAMPLES_DIR"
fi

# Check if sample file exists
if [ ! -f "$SAMPLE_FILE" ]; then
    print_error "Error: Sample not found: $SAMPLE_FILE"
    echo ""
    echo "Did you mean one of these?"
    if [ "$IS_ASYNC" = true ]; then
        ls "$ASYNC_SAMPLES_DIR"/sample_*_async.py 2>/dev/null | xargs -n1 basename | sed 's/\.py$//' | grep -i "${SAMPLE_NAME%_async}" | head -5 || true
    else
        ls "$SAMPLES_DIR"/sample_*.py 2>/dev/null | xargs -n1 basename | sed 's/\.py$//' | grep -i "$SAMPLE_NAME" | head -5 || true
    fi
    echo ""
    echo "Run '$0 --list' to see all available samples"
    exit 1
fi

# Navigate to package root
cd "$PACKAGE_ROOT"

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        print_info "Activating virtual environment..."
        source .venv/bin/activate
        print_success "✓ Activated .venv"
    else
        print_warning "⚠ No virtual environment found. Consider running cu-sdk-setup skill first."
    fi
else
    print_info "Using active virtual environment: $VIRTUAL_ENV"
fi

# Check for .env file
if [ ! -f ".env" ] && [ ! -f "$RUN_DIR/.env" ]; then
    print_warning "⚠ No .env file found. Some samples may fail without environment variables."
    echo "  Run: cp env.sample .env && edit .env"
fi

# Run the sample
echo ""
print_info "=== Running: $SAMPLE_NAME ==="
echo "File: $SAMPLE_FILE"
echo ""

cd "$RUN_DIR"
python "${SAMPLE_NAME}.py"

echo ""
print_success "✓ Sample completed: $SAMPLE_NAME"
