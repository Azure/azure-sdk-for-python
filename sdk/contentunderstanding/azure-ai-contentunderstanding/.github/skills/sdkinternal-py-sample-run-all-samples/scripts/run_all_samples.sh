#!/bin/bash
# ===============================
# Run All Samples Script
# ===============================
# This script runs all sync and async samples for azure-ai-contentunderstanding
# and logs the output to a timestamped log file.

set -e

# ===============================
# Settings
# ===============================
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
# Run each sample
# ===============================
cd "$SAMPLES_PARENT"

# Run sync samples located at the samples root (so `sample_files/...` resolves)
for sample in ./*.py; do
    if [[ -f "$sample" ]]; then
        sample_name="$(basename "$sample")"
        echo "---------------------------------------------" | tee -a "$LOG_FILE"
        echo "Running sample (sync): $sample_name" | tee -a "$LOG_FILE"
        echo "---------------------------------------------" | tee -a "$LOG_FILE"
        
        $VENV_PY "./$sample_name" 2>&1 | tee -a "$LOG_FILE" || true
        
        echo "" | tee -a "$LOG_FILE"
    fi
done

# Run async samples in the `async_samples` subfolder
if [[ -d "$SAMPLES_SUB" ]]; then
    for sample in "$SAMPLES_SUB"/*.py; do
        if [[ -f "$sample" ]]; then
            sample_name="$(basename "$sample")"
            echo "---------------------------------------------" | tee -a "$LOG_FILE"
            echo "Running sample (async): $sample_name" | tee -a "$LOG_FILE"
            echo "---------------------------------------------" | tee -a "$LOG_FILE"
            
            # Run the script from the samples parent directory so relative sample_files paths resolve
            $VENV_PY "./$SAMPLES_SUB/$sample_name" 2>&1 | tee -a "$LOG_FILE" || true
            
            echo "" | tee -a "$LOG_FILE"
        fi
    done
fi

cd "$CURRENT_DIR"

echo "=============================================" | tee -a "$LOG_FILE"
echo "All samples finished. Log saved to $LOG_FILE." | tee -a "$LOG_FILE"
