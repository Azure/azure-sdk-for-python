#!/usr/bin/env bash
set -euo pipefail

# run_tests.sh - Run tests for azure-ai-contentunderstanding in playback, live, or record mode
# Usage:
#   run_tests.sh [--playback|--live|--record] [--parallel] [--dry-run] [-- PYTEST_ARGS...]
# Examples:
#   run_tests.sh                        # Run in playback mode (default)
#   run_tests.sh --live                 # Run in live mode
#   run_tests.sh --record               # Run in record mode
#   run_tests.sh --live -- -k test_foo  # Run live tests matching pattern

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REPO_ROOT="$(cd "$PACKAGE_ROOT/../../.." && pwd)"

# Default values
DRY_RUN=0
PARALLEL=0
MODE="playback"  # playback, live, or record
DATE_STR="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$SCRIPT_DIR/run_tests_${DATE_STR}.log"
PYTEST_ARGS=()

print_help() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS] [-- PYTEST_ARGS...]

Run tests for azure-ai-contentunderstanding in different modes.

Options:
  --playback    Run tests in playback mode (default)
                Uses recorded HTTP responses, no live service calls
  --live        Run tests in live mode
                Makes actual API calls to Azure services
  --record      Run tests in record mode
                Makes live API calls and records responses for playback
  --parallel    Run tests in parallel using pytest-xdist (pytest -n auto)
  --dry-run     Print what would be run without executing
  --log <file>  Save output to <file> (default: timestamped log file)
  --help, -h    Show this help message

Environment Variables Set by Mode:
  Playback: AZURE_TEST_RUN_LIVE=false
  Live:     AZURE_TEST_RUN_LIVE=true
  Record:   AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true

Examples:
  $(basename "$0")                           # Run in playback mode
  $(basename "$0") --live                    # Run in live mode
  $(basename "$0") --record                  # Run in record mode
  $(basename "$0") --live --parallel         # Run live tests in parallel
  $(basename "$0") -- -k test_analyzer       # Run tests matching pattern
  $(basename "$0") --live -- -v tests/test_foo.py  # Run specific test file verbose
  $(basename "$0") --dry-run                 # Show what would be executed

Prerequisites:
  - Python 3.9+ installed
  - For live/record modes: Valid Azure credentials
    (CONTENTUNDERSTANDING_KEY in .env or az login for DefaultAzureCredential)
  - For live/record modes: Model deployments configured (see main README)
EOF
}

log() {
  echo "[$(date '+%H:%M:%S')] $*"
}

error() {
  echo "[$(date '+%H:%M:%S')] ERROR: $*" >&2
}

warn() {
  echo "[$(date '+%H:%M:%S')] WARNING: $*" >&2
}

# Parse arguments
while [[ ${#@} -ge 1 ]]; do
  case "$1" in
    --help|-h)
      print_help
      exit 0
      ;;
    --playback)
      MODE="playback"
      shift
      ;;
    --live)
      MODE="live"
      shift
      ;;
    --record)
      MODE="record"
      shift
      ;;
    --parallel)
      PARALLEL=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --log)
      if [[ ${#@} -ge 2 ]]; then
        LOG_FILE="$2"
        shift 2
      else
        error "--log requires a file argument"
        exit 2
      fi
      ;;
    --)
      shift
      PYTEST_ARGS=("$@")
      break
      ;;
    *)
      error "Unknown option: $1"
      print_help
      exit 2
      ;;
  esac
done

check_and_setup_venv() {
  log "Checking virtual environment..."
  
  local venv_dir="$PACKAGE_ROOT/.venv"
  
  # Check if venv exists
  if [[ -d "$venv_dir" ]]; then
    log "Virtual environment found at $venv_dir"
  else
    log "Virtual environment not found at $venv_dir"
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "DRY RUN: Would create virtual environment at $venv_dir"
    else
      log "Creating virtual environment..."
      (cd "$PACKAGE_ROOT" && python3 -m venv .venv) || (cd "$PACKAGE_ROOT" && python -m venv .venv)
      log "Virtual environment created at $venv_dir"
    fi
  fi
  
  # Check if we're already in the venv
  if [[ "${VIRTUAL_ENV:-}" == "$venv_dir" ]]; then
    log "Virtual environment is already activated"
  else
    log "Activating virtual environment..."
    if [[ $DRY_RUN -eq 1 ]]; then
      echo "DRY RUN: Would activate virtual environment: source $venv_dir/bin/activate"
    else
      # shellcheck disable=SC1091
      source "$venv_dir/bin/activate"
      log "Virtual environment activated"
      log "Python: $(which python)"
    fi
  fi
}

check_and_install_dependencies() {
  log "Checking for test dependencies..."
  
  if python -c "import devtools_testutils" 2>/dev/null; then
    log "devtools_testutils module found (OK)"
    return 0
  fi
  
  log "Module 'devtools_testutils' is not installed."
  
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: Would install dependencies:"
    echo "  pip install -e $PACKAGE_ROOT"
    echo "  pip install -r $PACKAGE_ROOT/dev_requirements.txt"
    return 0
  fi
  
  log "Installing dependencies..."
  log "  Installing package in editable mode..."
  (cd "$PACKAGE_ROOT" && pip install -e . --quiet)
  log "  Installing dev requirements..."
  (cd "$PACKAGE_ROOT" && pip install -r dev_requirements.txt --quiet)
  log "Dependencies installed"
  
  # Verify installation
  if ! python -c "import devtools_testutils" 2>/dev/null; then
    error "Failed to install devtools_testutils. Please check the installation manually."
    exit 1
  fi
  
  log "devtools_testutils module found (OK)"
}

check_and_setup_env() {
  log "Checking environment configuration..."
  
  local env_file="$PACKAGE_ROOT/.env"
  local env_sample="$PACKAGE_ROOT/env.sample"
  
  if [[ -f "$env_file" ]]; then
    log ".env file found"
    
    # For live/record mode, check that endpoint is set
    if [[ "$MODE" != "playback" ]]; then
      if ! grep -q "CONTENTUNDERSTANDING_ENDPOINT=" "$env_file" 2>/dev/null || \
         grep -q "CONTENTUNDERSTANDING_ENDPOINT=$" "$env_file" 2>/dev/null || \
         grep -q "CONTENTUNDERSTANDING_ENDPOINT=<" "$env_file" 2>/dev/null; then
        warn "CONTENTUNDERSTANDING_ENDPOINT may not be configured in .env"
        warn "This is required for live/record mode"
      fi
    fi
  else
    if [[ -f "$env_sample" ]]; then
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: Would copy $env_sample to $env_file"
      else
        log "Creating .env from env.sample..."
        cp "$env_sample" "$env_file"
        log ".env created - please configure required variables:"
        log "  CONTENTUNDERSTANDING_ENDPOINT - Your Microsoft Foundry endpoint"
        log "  CONTENTUNDERSTANDING_KEY - API key (optional if using DefaultAzureCredential)"
        
        if [[ "$MODE" != "playback" ]]; then
          warn "Live/record mode requires environment variables to be configured!"
          warn "Please edit $env_file and set CONTENTUNDERSTANDING_ENDPOINT"
        fi
      fi
    else
      warn "No .env or env.sample found"
      if [[ "$MODE" != "playback" ]]; then
        error "Live/record mode requires environment configuration"
        error "Please create .env with CONTENTUNDERSTANDING_ENDPOINT set"
        exit 1
      fi
    fi
  fi
}

check_parallel_prerequisites() {
  if [[ $PARALLEL -eq 1 ]]; then
    log "Parallel mode requested..."
    
    # Check if pytest-xdist is installed
    if ! python -c "import xdist" 2>/dev/null; then
      if [[ $DRY_RUN -eq 1 ]]; then
        echo "DRY RUN: Would install pytest-xdist for parallel execution"
      else
        log "Installing pytest-xdist for parallel execution..."
        pip install pytest-xdist --quiet
      fi
    fi
  fi
}

build_pytest_command() {
  local cmd="pytest"
  
  # Add parallel flag if requested
  if [[ $PARALLEL -eq 1 ]]; then
    cmd="$cmd -n auto"
  fi
  
  # Add any additional pytest arguments
  if [[ ${#PYTEST_ARGS[@]} -gt 0 ]]; then
    cmd="$cmd ${PYTEST_ARGS[*]}"
  fi
  
  echo "$cmd"
}

build_env_vars() {
  local env_vars=""
  
  case "$MODE" in
    playback)
      env_vars="AZURE_TEST_RUN_LIVE=false"
      ;;
    live)
      env_vars="AZURE_TEST_RUN_LIVE=true"
      ;;
    record)
      env_vars="AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true"
      ;;
  esac
  
  echo "$env_vars"
}

run_tests() {
  local pytest_cmd
  local env_vars
  
  pytest_cmd=$(build_pytest_command)
  env_vars=$(build_env_vars)
  
  log "Running tests in $MODE mode..."
  log "  Environment: $env_vars"
  log "  Command: $pytest_cmd"
  log "  Working directory: $PACKAGE_ROOT"
  echo ""
  
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: Would execute:"
    echo "  cd $PACKAGE_ROOT"
    echo "  $env_vars $pytest_cmd"
    return 0
  fi
  
  # Run pytest with the appropriate environment variables
  (cd "$PACKAGE_ROOT" && eval "$env_vars $pytest_cmd")
}

show_post_run_info() {
  echo ""
  log "Tests completed!"
  
  case "$MODE" in
    playback)
      log "Playback tests finished."
      log ""
      log "If tests failed due to missing recordings:"
      log "  1. Run tests in record mode: $(basename "$0") --record"
      log "  2. Push recordings: .github/skills/sdkinternal-py-test-push/scripts/push_recordings.sh"
      ;;
    live)
      log "Live tests finished."
      log ""
      log "If you need to update recordings:"
      log "  1. Run tests in record mode: $(basename "$0") --record"
      log "  2. Push recordings: .github/skills/sdkinternal-py-test-push/scripts/push_recordings.sh"
      ;;
    record)
      log "Record mode tests finished."
      log ""
      log "Next steps:"
      log "  1. Push recordings to azure-sdk-assets:"
      log "       .github/skills/sdkinternal-py-test-push/scripts/push_recordings.sh"
      log "  2. Verify playback works:"
      log "       $(basename "$0") --playback"
      log "  3. Commit assets.json to your PR"
      ;;
  esac
}

main() {
  echo "========================================"
  echo "  Run Tests - azure-ai-contentunderstanding"
  echo "========================================"
  echo "Script directory: $SCRIPT_DIR"
  echo "Package root: $PACKAGE_ROOT"
  echo "Mode: $MODE"
  if [[ $PARALLEL -eq 1 ]]; then
    echo "Parallel: enabled"
  fi
  if [[ ${#PYTEST_ARGS[@]} -gt 0 ]]; then
    echo "Pytest args: ${PYTEST_ARGS[*]}"
  fi
  echo "Log file: $LOG_FILE"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "Dry run: enabled"
  fi
  echo ""

  {
    # Pre-flight checks and setup
    check_and_setup_venv
    check_and_install_dependencies
    check_and_setup_env
    check_parallel_prerequisites
    
    # Run tests
    run_tests
    
    # Show post-run information
    show_post_run_info
    
    log "Done!"
  } 2>&1 | tee "$LOG_FILE"
}

main
