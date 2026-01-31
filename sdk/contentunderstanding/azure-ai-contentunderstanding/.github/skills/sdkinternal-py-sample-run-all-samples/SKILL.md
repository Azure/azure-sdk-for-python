---
name: sdkinternal-py-sample-run-all-samples
description: "Run all samples (sync and async) for the azure-ai-contentunderstanding SDK. Use when you need to verify samples work correctly after SDK changes."
---

# Run All Samples

This skill runs all Python samples for the `azure-ai-contentunderstanding` SDK to verify they execute correctly.

## Prerequisites

- Python >= 3.9
- A Microsoft Foundry resource with required model deployments (gpt-4.1, gpt-4.1-mini, text-embedding-3-large)
- **Cognitive Services User** role assigned to your account
- Sample files available in `samples/sample_files/`

## Setup

### Step 1: Set Up Virtual Environment (Optional)

The script automatically handles virtual environment setup. It will:
- Use your active virtual environment if one is detected
- Activate `.venv` if it exists in the package directory
- Create `.venv` and install dependencies if neither exists

**To manually set up** (from the package directory `sdk/contentunderstanding/azure-ai-contentunderstanding`):

```bash
# Create virtual environment (only needed once)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate   # On Windows

# Install SDK (editable) and all dependencies
pip install -e .
pip install -r dev_requirements.txt  # Includes aiohttp, pytest, python-dotenv, azure-identity
```

### Step 2: Configure Environment Variables (Optional)

The script automatically copies `env.sample` to `.env` if no `.env` exists.

**To manually set up**, create a `.env` file in the package root directory:

```bash
cp env.sample .env
```

Edit `.env` with your values:

```bash
CONTENTUNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
# Optional: If omitted, DefaultAzureCredential is used
CONTENTUNDERSTANDING_KEY=<optional-api-key>

# Required for sample_update_defaults.py (one-time setup)
GPT_4_1_DEPLOYMENT=gpt-4.1
GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

**Note:** If `CONTENTUNDERSTANDING_KEY` is not set, the SDK uses `DefaultAzureCredential`. Ensure you have authenticated (e.g., `az login`).

### Step 3: Configure Model Deployments (One-Time)

Before running samples that use prebuilt analyzers, you must configure default model mappings:

```bash
cd samples
python sample_update_defaults.py
```

This maps your deployed models to those required by prebuilt analyzers.

## Quick Start

The script automatically sets up the environment if needed. It's **safe to rerun** - existing `.venv` and `.env` files are never overwritten.

From the `.github/skills/sdkinternal-py-sample-run-all-samples/scripts/` directory:

```bash
./run_all_samples.sh
```

Or from the package root:

```bash
.github/skills/sdkinternal-py-sample-run-all-samples/scripts/run_all_samples.sh
```

## What It Does

1. **Automatic virtual environment handling** (safe - never overwrites existing):
   - If already in an active venv → uses it
   - If `.venv` exists in the package directory → activates it (does NOT reinstall)
   - If no venv exists → creates `.venv`, installs SDK (`pip install -e .`) and dependencies
2. **Automatic .env configuration** (safe - never overwrites existing):
   - If `.env` exists → uses it
   - If `.env` doesn't exist but `env.sample` does → copies `env.sample` to `.env`
3. Runs all sync samples (`samples/*.py`)
4. Runs all async samples (`samples/async_samples/*.py`)
5. Logs all output to a timestamped log file in the current directory

## Script Location

The bash script is located at:
```
.github/skills/sdkinternal-py-sample-run-all-samples/scripts/run_all_samples.sh
```

## Configuration

The script uses the following defaults:
- **Python command**: `python` (can be changed via `VENV_PY` variable)
- **Log file**: `run_samples_YYYYMMDD_HHMMSS.log` in the current directory

To use a specific Python interpreter:

```bash
VENV_PY=python3.11 ./run_all_samples.sh
```

## Expected Output

The script creates a log file with:
- Timestamp of the run
- Output from each sample (grouped by sync/async)
- Summary of completion

Example log output:
```
=== Azure SDK Samples Run - 2026-01-30 10:30:00 ===
---------------------------------------------
Running sample (sync): sample_analyze_document.py
---------------------------------------------
[sample output here]

---------------------------------------------
Running sample (async): sample_analyze_document_async.py
---------------------------------------------
[sample output here]

=============================================
All samples finished. Log saved to run_samples_20260130_103000.log.
```

## Troubleshooting

### Sample fails to find sample_files

Make sure to run samples from the `samples/` directory (the script handles this automatically).

### Missing credentials / Access denied

Ensure Azure credentials are configured:
- Set `CONTENTUNDERSTANDING_ENDPOINT` environment variable
- For API key auth: set `CONTENTUNDERSTANDING_KEY`
- For DefaultAzureCredential: run `az login`
- Ensure you have the **Cognitive Services User** role assigned

### Model deployment not found

- Ensure you have deployed the required models (gpt-4.1, gpt-4.1-mini, text-embedding-3-large) in Microsoft Foundry
- Run `sample_update_defaults.py` to configure default model mappings
- Check that deployment names in `.env` match what you created in Foundry

### Import errors

Ensure the SDK and dependencies are installed:
```bash
pip install -e .
pip install -r dev_requirements.txt
```

### aiohttp not installed (async samples)

The async transport requires aiohttp:
```bash
pip install aiohttp
```
Or install all dev dependencies: `pip install -r dev_requirements.txt`

## Related Files

- `samples/*.py` - Sync samples
- `samples/async_samples/*.py` - Async samples
- `samples/sample_files/` - Sample input files (PDFs, images, etc.)
- `.env` - Environment configuration (created from `env.sample` if not exists)
- `env.sample` - Template for environment variables
- `dev_requirements.txt` - Development dependencies
