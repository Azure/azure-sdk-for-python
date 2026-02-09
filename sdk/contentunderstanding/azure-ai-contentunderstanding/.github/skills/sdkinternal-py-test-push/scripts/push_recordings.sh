#!/usr/bin/env bash
set -euo pipefail

# push_recordings.sh - Push test recordings to azure-sdk-assets repository
# Usage:
#   push_recordings.sh [--dry-run] [--log <file>]
# Examples:
#   push_recordings.sh              # push recordings
#   push_recordings.sh --dry-run    # show what would be done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REPO_ROOT="$(cd "$PACKAGE_ROOT/../../.." && pwd)"

DRY_RUN=0
DATE_STR="$(date '+%Y%m%d_%H%M%S')"
LOG_FILE="$SCRIPT_DIR/push_recordings_${DATE_STR}.log"

# Relative path from repo root to assets.json
ASSETS_JSON_PATH="sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json"

print_help() {
  cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Push test recordings for azure-ai-contentunderstanding to the
azure-sdk-assets repository.

Options:
  --dry-run     Print what would be run without executing
  --log <file>  Save output to <file> (default: $LOG_FILE)
  --help, -h    Show this help message

Prerequisites:
  - Write access to https://github.com/Azure/azure-sdk-assets
    (membership in azure-sdk-write GitHub group)
  - Dev dependencies installed: pip install -r dev_requirements.txt
  - Tests have been run in record mode (AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true)
  - Git is configured with user.name and user.email
  - Git version > 2.30.0

Workflow:
  1. Run tests in record mode: AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest
  2. Push recordings: $(basename "$0")
  3. Commit updated assets.json to your PR

What This Script Does:
  - Checks for assets.json
  - Verifies git is configured and version is compatible
  - Pushes recordings to azure-sdk-assets repo
  - Updates assets.json with the new tag
  - Displays the updated tag for verification

Examples:
  $(basename "$0")           # Push recordings
  $(basename "$0") --dry-run # Show what would be done
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
    *)
      error "Unknown option: $1"
      print_help
      exit 2
      ;;
  esac
done

check_git_version() {
  log "Checking git version..."
  
  local git_version
  git_version="$(git --version | sed 's/git version //')"
  
  # Extract major and minor version
  local major minor
  major="$(echo "$git_version" | cut -d. -f1)"
  minor="$(echo "$git_version" | cut -d. -f2)"
  
  # Require git version > 2.30.0
  if [[ "$major" -lt 2 ]] || { [[ "$major" -eq 2 ]] && [[ "$minor" -lt 30 ]]; }; then
    error "Git version $git_version is too old. Version > 2.30.0 is required."
    error "Please update Git: https://git-scm.com/downloads"
    exit 1
  fi
  
  log "Git version: $git_version (OK)"
}

check_git_config() {
  log "Checking git configuration..."
  
  local git_name git_email
  git_name="$(git config --get user.name || echo "${GIT_COMMIT_OWNER:-}")"
  git_email="$(git config --get user.email || echo "${GIT_COMMIT_EMAIL:-}")"
  
  if [[ -z "$git_name" ]]; then
    error "Git user.name is not configured"
    error "Run: git config --global user.name \"Your Name\""
    error "Or set environment variable: GIT_COMMIT_OWNER"
    exit 1
  fi
  
  if [[ -z "$git_email" ]]; then
    error "Git user.email is not configured"
    error "Run: git config --global user.email \"your.email@example.com\""
    error "Or set environment variable: GIT_COMMIT_EMAIL"
    exit 1
  fi
  
  log "Git configured as: $git_name <$git_email>"
}

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
  log "Checking for devtools_testutils module..."
  
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

check_assets_json() {
  local assets_file="$REPO_ROOT/$ASSETS_JSON_PATH"
  
  if [[ -f "$assets_file" ]]; then
    log "Found existing assets.json"
    log "Current contents:"
    cat "$assets_file"
    echo ""
    
    # Check if Tag is empty
    local tag
    tag="$(grep -o '"Tag":[[:space:]]*"[^"]*"' "$assets_file" | sed 's/"Tag":[[:space:]]*"//' | sed 's/"$//')"
    if [[ -z "$tag" ]]; then
      warn "assets.json has an empty Tag. You may need to record tests first."
      warn "Run: AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest"
    fi
    return 0
  else
    error "assets.json not found at $assets_file"
    error "See the Recording Migration Guide for initial setup:"
    error "https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/recording_migration_guide.md"
    exit 1
  fi
}

check_recordings_exist() {
  local assets_dir="$REPO_ROOT/.assets"
  
  if [[ -d "$assets_dir" ]]; then
    log "Found .assets directory at $assets_dir"
    
    # Try to locate the package's recordings
    if [[ $DRY_RUN -eq 0 ]]; then
      log "Locating package recordings..."
      (cd "$REPO_ROOT" && python scripts/manage_recordings.py locate -p "$ASSETS_JSON_PATH") || true
    fi
  else
    warn ".assets directory not found. You may need to run tests first."
    warn "Run: AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest"
    warn "Or restore existing recordings: python scripts/manage_recordings.py restore -p $ASSETS_JSON_PATH"
  fi
}

preflight_checks() {
  log "Running pre-flight checks..."
  
  # Check if we're in the right directory structure
  if [[ ! -f "$PACKAGE_ROOT/setup.py" ]] && [[ ! -f "$PACKAGE_ROOT/pyproject.toml" ]]; then
    error "Cannot find setup.py or pyproject.toml at $PACKAGE_ROOT"
    exit 1
  fi
  
  # Check if manage_recordings.py exists
  if [[ ! -f "$REPO_ROOT/scripts/manage_recordings.py" ]]; then
    error "Cannot find manage_recordings.py at $REPO_ROOT/scripts/"
    exit 1
  fi

  # Check git version
  check_git_version

  # Check git configuration
  check_git_config
  
  # Check and setup virtual environment
  check_and_setup_venv
  
  # Check and install dependencies (including devtools_testutils)
  check_and_install_dependencies
  
  # Check assets.json exists
  check_assets_json
  
  # Check if recordings might exist
  check_recordings_exist

  log "Pre-flight checks passed"
}

push_recordings() {
  log "Pushing recordings to azure-sdk-assets..."
  
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "DRY RUN: (in $REPO_ROOT) python scripts/manage_recordings.py push -p $ASSETS_JSON_PATH"
  else
    (cd "$REPO_ROOT" && python scripts/manage_recordings.py push -p "$ASSETS_JSON_PATH")
  fi
}

show_result() {
  local assets_file="$REPO_ROOT/$ASSETS_JSON_PATH"
  
  log "Push completed!"
  log ""
  log "Updated assets.json:"
  if [[ $DRY_RUN -eq 0 ]]; then
    cat "$assets_file"
  else
    echo "DRY RUN: would show updated assets.json"
  fi
  echo ""
  
  log "Next steps:"
  log "  1. Verify the Tag was updated in assets.json"
  log "  2. Run playback tests to verify: AZURE_TEST_RUN_LIVE=false pytest"
  log "  3. Commit assets.json to your PR:"
  log "       git add $ASSETS_JSON_PATH"
  log "       git commit -m \"Update test recording tag\""
}

main() {
  echo "========================================"
  echo "  Push Recordings to Assets Repo"
  echo "========================================"
  echo "Script directory: $SCRIPT_DIR"
  echo "Package root: $PACKAGE_ROOT"
  echo "Repository root: $REPO_ROOT"
  echo "Assets JSON: $ASSETS_JSON_PATH"
  echo "Log file: $LOG_FILE"
  if [[ $DRY_RUN -eq 1 ]]; then
    echo "Mode: Dry run"
  else
    echo "Mode: Push"
  fi
  echo ""

  {
    preflight_checks
    push_recordings
    show_result
    log "Done!"
  } 2>&1 | tee "$LOG_FILE"
}

main
