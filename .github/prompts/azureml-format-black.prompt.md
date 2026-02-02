---
name: 'azureml-format-black'
description: '[azure-ai-ml] Apply Black formatter to azure-ai-ml package'
agent: 'agent'
tools: ['runInTerminal', 'getTerminalOutput']
---

# Format Code with Black - Azure ML SDK

> ** Package Scope**: This prompt is for the **azure-ai-ml** package only (`sdk/ml/azure-ai-ml/`).

Format Python code using Black with the Azure SDK configuration.

##  Run Black Formatter

```bash
# Navigate to azure-ai-ml directory
cd sdk/ml/azure-ai-ml

# Create virtual environment if it doesn't exist
if (-not (Test-Path env)) {
    python -m venv env
}

# Activate virtual environment
env\Scripts\Activate.ps1

# Install black in virtual environment
pip install black

# Format all code (uses eng/black-pyproject.toml config)
python -m black --config ../../../eng/black-pyproject.toml .
```

##  Verify Formatting

```bash
# Check if code is properly formatted (without making changes)
cd sdk/ml/azure-ai-ml

# Activate virtual environment
env\Scripts\Activate.ps1

# Run Black check
python -m black --check --config ../../../eng/black-pyproject.toml .
```

##  Notes

- **Configuration**: Uses `eng/black-pyproject.toml` from repository root
- **Line Length**: 120 characters (per Azure SDK standards)
- **Auto-excluded**: `_vendor/*`, `_generated/*`, `_restclient/*` directories
- Black is deterministic - running multiple times produces same result

---
