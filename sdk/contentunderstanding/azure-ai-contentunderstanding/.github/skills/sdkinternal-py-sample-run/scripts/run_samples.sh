#!/bin/bash
# ===============================
# Run All Samples Script
# ===============================
# This script runs all sync and async samples for azure-ai-contentunderstanding
# and logs the output to a timestamped log file.
# Optionally, pass a sample name to run only that sample.
#
# Usage:
#   ./run_all_samples.sh                    # Run all samples
#   ./run_all_samples.sh sample_analyze.py  # Run a single sample

set -e

# ===============================
# Settings
# ===============================
SINGLE_SAMPLE="${1:-}"
VENV_PY="${VENV_PY:-python}"
CURRENT_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$(cd "$SCRIPT_DIR/../../../.." 2>/dev/null && pwd)" || PACKAGE_DIR=""
SAMPLES_PARENT="$(cd "$SCRIPT_DIR/../../../../samples" 2>/dev/null && pwd)" || SAMPLES_PARENT=""
SAMPLES_SUB="async_samples"
LOG_FILE="$CURRENT_DIR/run_samples_$(date +%Y%m%d_%H%M%S).log"
VENV_DIR="$PACKAGE_DIR/.venv"

# ===============================
# Virtual environment setup
# ===============================
if [[ -z "$VIRTUAL_ENV" ]]; then
    # Not in a virtual environment - check if .venv exists
    if [[ -d "$VENV_DIR" && -f "$VENV_DIR/bin/activate" ]]; then
        echo "Virtual environment already exists at $VENV_DIR"
        echo "Activating..."
        source "$VENV_DIR/bin/activate"
        VENV_PY="python"
    else
        echo "No virtual environment found at $VENV_DIR"
        echo "Creating virtual environment..."
        python -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        VENV_PY="python"
        
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -e "$PACKAGE_DIR"
        if [[ -f "$PACKAGE_DIR/dev_requirements.txt" ]]; then
            pip install -r "$PACKAGE_DIR/dev_requirements.txt"
        fi
        echo ""
    fi
else
    echo "Using active virtual environment: $VIRTUAL_ENV"
fi

# ===============================
# Check .env configuration
# ===============================
ENV_FILE="$PACKAGE_DIR/.env"
ENV_SAMPLE="$PACKAGE_DIR/env.sample"

if [[ ! -f "$ENV_FILE" ]]; then
    if [[ -f "$ENV_SAMPLE" ]]; then
        echo "No .env file found. Copying env.sample to .env..."
        cp "$ENV_SAMPLE" "$ENV_FILE"
        echo "Created .env - Please configure the required variables before running samples."
        echo "Required: CONTENTUNDERSTANDING_ENDPOINT"
        echo ""
    else
        echo "WARNING: No .env or env.sample found. Samples may fail without configuration."
        echo ""
    fi
else
    echo "Using existing .env configuration"
fi

echo "=== Azure SDK Samples Run - $(date '+%Y-%m-%d %H:%M:%S') ===" | tee "$LOG_FILE"
echo "Using Python: $VENV_PY ($(which $VENV_PY 2>/dev/null || echo 'not found'))" | tee -a "$LOG_FILE"

# ===============================
# Validate samples directory
# ===============================
if [[ -z "$SAMPLES_PARENT" || ! -d "$SAMPLES_PARENT" ]]; then
    echo "Sample directory not found: $SAMPLES_PARENT" | tee -a "$LOG_FILE"
    exit 1
fi

# ===============================
# Helper function to run a sample
# ===============================
run_sample() {
    local sample_path="$1"
    local sample_type="$2"
    local sample_name="$(basename "$sample_path")"
    
    echo "---------------------------------------------" | tee -a "$LOG_FILE"
    echo "Running sample ($sample_type): $sample_name" | tee -a "$LOG_FILE"
    echo "---------------------------------------------" | tee -a "$LOG_FILE"
    
    $VENV_PY "$sample_path" 2>&1 | tee -a "$LOG_FILE" || true
    
    echo "" | tee -a "$LOG_FILE"
}

# ===============================
# Run samples
# ===============================
cd "$SAMPLES_PARENT"

if [[ -n "$SINGLE_SAMPLE" ]]; then
    # Run a single sample
    SAMPLE_FOUND=false
    
    # Check in sync samples directory
    if [[ -f "./$SINGLE_SAMPLE" ]]; then
        run_sample "./$SINGLE_SAMPLE" "sync"
        SAMPLE_FOUND=true
    # Check in async samples directory
    elif [[ -f "./$SAMPLES_SUB/$SINGLE_SAMPLE" ]]; then
        run_sample "./$SAMPLES_SUB/$SINGLE_SAMPLE" "async"
        SAMPLE_FOUND=true
    fi
    
    if [[ "$SAMPLE_FOUND" == "false" ]]; then
        echo "ERROR: Sample '$SINGLE_SAMPLE' not found." | tee -a "$LOG_FILE"
        echo "Searched in:" | tee -a "$LOG_FILE"
        echo "  - $SAMPLES_PARENT/" | tee -a "$LOG_FILE"
        echo "  - $SAMPLES_PARENT/$SAMPLES_SUB/" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo "Available samples:" | tee -a "$LOG_FILE"
        echo "  Sync:" | tee -a "$LOG_FILE"
        for s in ./*.py; do [[ -f "$s" ]] && echo "    $(basename "$s")" | tee -a "$LOG_FILE"; done
        if [[ -d "$SAMPLES_SUB" ]]; then
            echo "  Async:" | tee -a "$LOG_FILE"
            for s in "$SAMPLES_SUB"/*.py; do [[ -f "$s" ]] && echo "    $(basename "$s")" | tee -a "$LOG_FILE"; done
        fi
        cd "$CURRENT_DIR"
        exit 1
    fi
else
    # Run all samples
    # Run sync samples located at the samples root (so `sample_files/...` resolves)
    for sample in ./*.py; do
        if [[ -f "$sample" ]]; then
            run_sample "$sample" "sync"
        fi
    done

    # Run async samples in the `async_samples` subfolder
    if [[ -d "$SAMPLES_SUB" ]]; then
        for sample in "$SAMPLES_SUB"/*.py; do
            if [[ -f "$sample" ]]; then
                run_sample "$sample" "async"
            fi
        done
    fi
fi

cd "$CURRENT_DIR"

echo "=============================================" | tee -a "$LOG_FILE"
if [[ -n "$SINGLE_SAMPLE" ]]; then
    echo "Sample finished. Log saved to $LOG_FILE." | tee -a "$LOG_FILE"
else
    echo "All samples finished. Log saved to $LOG_FILE." | tee -a "$LOG_FILE"
fi
