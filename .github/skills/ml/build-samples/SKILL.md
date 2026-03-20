---
name: build-samples
description: Build, write, and run samples for the azure-ai-ml package following Azure SDK Python samples guidelines. Optionally accepts a GitHub issue URL for context and a virtual env path. Format: "build samples [for <issue-url>] [using venv <path>]"
---

# Build Samples Skill

This skill sets up the environment, installs dependencies, runs existing samples, and helps write new samples for the azure-ai-ml package following Azure SDK Python samples guidelines.

## Overview

Intelligently builds and runs samples by:
1. Getting the optional GitHub issue URL and virtual environment path from the user
2. Activating or creating a virtual environment
3. Installing required dependencies
4. Running existing samples via tox or directly
5. Analyzing failures and fixing or reporting them
6. Writing new samples if requested (following Azure SDK sample guidelines)
7. Verifying samples run successfully
8. Creating a pull request if new samples were written
9. Providing a summary of sample results

## Running Samples

**Command for all samples (tox):**
```powershell
cd sdk/ml/azure-ai-ml
tox -e samples --c ../../../eng/tox/tox.ini --root .
```

**Command for a specific sample file:**
```powershell
cd sdk/ml/azure-ai-ml
python samples/sample_name.py
```

**Command using the azpysdk CLI:**
```powershell
cd sdk/ml/azure-ai-ml
azpysdk samples .
```

**Command using the test_run_samples script directly:**
```powershell
cd sdk/ml/azure-ai-ml
python ../../../scripts/devops_tasks/test_run_samples.py -t .
```

## Reference Documentation

- [Azure SDK Python Tests Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Samples Runner Script](https://github.com/Azure/azure-sdk-for-python/blob/main/scripts/devops_tasks/test_run_samples.py)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Tox Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)

## Fixing Strategy

### Step 0: Gather Context

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message) — optional, for context
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is provided:**
Read the issue to understand which samples to run or write, and what functionality to demonstrate.

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

### Step 1: CRITICAL - Activate Virtual Environment FIRST

**IMMEDIATELY activate the virtual environment before ANY other command:**

```powershell
# Activate the provided virtual environment (e.g., envml, env, venv)
.\<venv-name>\Scripts\Activate.ps1

# If creating new virtual environment:
python -m venv env
.\env\Scripts\Activate.ps1
```

**⚠️ IMPORTANT: ALL subsequent commands MUST run within the activated virtual environment. Never run commands outside the venv.**

### Step 2: Install Dependencies (within activated venv)

```powershell
# Navigate to azure-ai-ml directory (within activated venv)
cd sdk/ml/azure-ai-ml

# Install dev dependencies from dev_requirements.txt (within activated venv)
pip install -r dev_requirements.txt

# Install the package in editable mode (within activated venv)
pip install -e .
```

### Step 3: Run Existing Samples (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

**Option A - Run all samples via tox:**
```powershell
cd sdk/ml/azure-ai-ml
tox -e samples --c ../../../eng/tox/tox.ini --root .
```

**Option B - Run a specific sample directly:**
```powershell
cd sdk/ml/azure-ai-ml
python samples/sample_name.py
```

**Option C - Run samples using the test runner script:**
```powershell
cd sdk/ml/azure-ai-ml
python ../../../scripts/devops_tasks/test_run_samples.py -t .
```

**Option D - Run samples mentioned in the issue:**
```powershell
cd sdk/ml/azure-ai-ml
python samples/<sample-from-issue>.py
```

### Step 4: Analyze Failures and Fix or Report

Parse the output to identify:
- Sample file name and path
- Failure type (ImportError, AuthenticationError, MissingEnvVar, etc.)
- Error message and traceback
- **Cross-reference with the GitHub issue** to understand expected behavior

**ALLOWED ACTIONS:**
 Fix sample failures caused by missing environment variables or configuration
 Update sample code to use current API when APIs have changed
 Add error handling for common transient failures
 Fix import errors by installing missing packages

**FORBIDDEN ACTIONS:**
 Hardcode credentials or secrets in sample files
 Delete or skip failing samples without clear justification
 Suppress errors without investigation
 Use non-`DefaultAzureCredential` authentication unless clearly required

### Step 5: Write New Samples (if requested)

Follow the Azure SDK Python samples guidelines when writing new samples.

**Proper sample file structure:**
```python
# pylint: disable=missing-module-docstring
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to <describe what the sample does>.

USAGE:
    python sample_name.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_SUBSCRIPTION_ID - the Azure subscription ID
    2) AZURE_RESOURCE_GROUP - the name of the Azure resource group
    3) AZURE_ML_WORKSPACE_NAME - the name of the Azure ML workspace
"""
import os

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential


def main() -> None:
    # Create the MLClient using DefaultAzureCredential
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_group = os.environ["AZURE_RESOURCE_GROUP"]
    workspace_name = os.environ["AZURE_ML_WORKSPACE_NAME"]

    ml_client = MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name,
    )

    # Perform the operation
    result = ml_client.some_operation()
    print(f"Operation completed: {result}")


if __name__ == "__main__":
    main()
```

**Samples directory structure:**
```
sdk/ml/azure-ai-ml/samples/
    sample_create_job.py
    sample_list_models.py
    sample_deploy_endpoint.py
    ...
```

**Key requirements for samples:**
- Each sample must be a standalone, runnable Python script
- Use `DefaultAzureCredential` from `azure.identity` for authentication
- Load all configuration from environment variables (never hardcode values)
- Include a clear `DESCRIPTION` and `USAGE` docstring at the top
- Include a `main()` function and `if __name__ == "__main__": main()` guard
- Print meaningful output to confirm successful execution

### Step 6: Verify Samples Run Successfully (within activated venv)

```powershell
cd sdk/ml/azure-ai-ml

# Set required environment variables
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
$env:AZURE_RESOURCE_GROUP = "your-resource-group"
$env:AZURE_ML_WORKSPACE_NAME = "your-workspace-name"

# Run the sample to verify it works
python samples/sample_name.py

# Or run all samples via tox
tox -e samples --c ../../../eng/tox/tox.ini --root .
```

### Step 7: Summary

Provide a summary:
- GitHub issue being addressed (if provided)
- Number of samples run, passed, and failed
- New samples written (if any) and their location
- Environment variables required to run the samples
- Any samples requiring specific Azure resources

### Step 8: Create Pull Request (if new samples were written)

After writing and verifying new samples, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage sample files
git add samples/

# Create a descriptive commit message
git commit -m "samples(azure-ai-ml): add samples for <feature> (#<issue-number>)

- Added standalone sample demonstrating <feature description>
- Sample uses DefaultAzureCredential for authentication
- Configuration loaded from environment variables

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "samples/azure-ai-ml-<feature>-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "samples(azure-ai-ml): Add samples for <feature> (#<issue-number>)" `
  --body "## Description
This PR adds samples for the azure-ai-ml package as described in #<issue-number>.

## Changes
- Added standalone sample(s) for <feature description>
- Samples use DefaultAzureCredential for authentication
- All configuration loaded from environment variables
- Samples cover: <list of scenarios demonstrated>

## Testing
- [x] Samples run successfully end-to-end
- [x] Samples use DefaultAzureCredential for authentication
- [x] No hardcoded credentials or secrets
- [x] Samples are standalone and runnable

## Required Environment Variables
- AZURE_SUBSCRIPTION_ID
- AZURE_RESOURCE_GROUP
- AZURE_ML_WORKSPACE_NAME

## Related Issues
Fixes #<issue-number>" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

Option 2 - Manual PR creation (if GitHub CLI not available):
1. Push branch: `git push origin <branch-name>`
2. Navigate to: https://github.com/Azure/azure-sdk-for-python/compare/main...<branch-name>
3. Create the pull request manually with the description above

Option 3 - Using GitHub MCP server (if available):
Use the GitHub MCP tools to create a pull request programmatically against the Azure/azure-sdk-for-python repository, main branch.

## Common Sample Failures and How to Fix Them

### Missing Environment Variables

**Error:** `KeyError: 'AZURE_SUBSCRIPTION_ID'` or `KeyError: 'AZURE_ML_WORKSPACE_NAME'`

**Fix:** Set the required environment variables before running:
```powershell
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
$env:AZURE_RESOURCE_GROUP = "your-resource-group"
$env:AZURE_ML_WORKSPACE_NAME = "your-workspace-name"
```

### Authentication Errors

**Error:** `azure.core.exceptions.ClientAuthenticationError`

**Fix:** Ensure Azure credentials are configured:
```powershell
az login
az account set --subscription "your-subscription-id"
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'azure.ai.ml'`

**Fix:** Ensure the package is installed in the venv:
```powershell
cd sdk/ml/azure-ai-ml
pip install -e .
pip install -r dev_requirements.txt
```

### Resource Not Found

**Error:** `azure.core.exceptions.ResourceNotFoundError`

**Fix:** Ensure the Azure ML workspace and referenced resources exist:
```powershell
# Verify the workspace exists
az ml workspace show --name $env:AZURE_ML_WORKSPACE_NAME `
  --resource-group $env:AZURE_RESOURCE_GROUP
```

### API Version or Deprecation Errors

**Error:** `AttributeError` or `TypeError` on method calls

**Fix:** Check the package version and update sample code to use current API:
```powershell
pip show azure-ai-ml
# Update the sample to use the current API as documented
```

### Permission Errors

**Error:** `azure.core.exceptions.HttpResponseError: (AuthorizationFailed)`

**Fix:** Ensure the service principal or user has the required RBAC roles on the workspace:
```powershell
# Assign Contributor or AzureML Data Scientist role to the service principal
az role assignment create --role "AzureML Data Scientist" `
  --assignee "your-service-principal-id" `
  --scope "/subscriptions/$env:AZURE_SUBSCRIPTION_ID/resourceGroups/$env:AZURE_RESOURCE_GROUP"
```

## Example Workflow

```powershell
# 0. Get context
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/12345
# Issue mentions: missing sample for model deployment feature

# 1. CRITICAL - Activate virtual environment FIRST
.\envml\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/ml/azure-ai-ml
pip install -r dev_requirements.txt
pip install -e .

# 2. Check what samples already exist
Get-ChildItem samples/ -Filter "*.py"

# 3. Run existing samples to verify they work
tox -e samples --c ../../../eng/tox/tox.ini --root .

# 4. Set environment variables for running samples
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
$env:AZURE_RESOURCE_GROUP = "your-resource-group"
$env:AZURE_ML_WORKSPACE_NAME = "your-workspace-name"

# 5. Write new sample for the missing scenario
# (Create samples/sample_deploy_model.py following Azure SDK guidelines)

# 6. Verify the new sample runs successfully
python samples/sample_deploy_model.py

# 7. Create PR
$branchName = "samples/azure-ai-ml-model-deployment-12345"
git checkout -b $branchName
git add samples/
git commit -m "samples(azure-ai-ml): add sample for model deployment (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "samples(azure-ai-ml): Add sample for model deployment (#12345)" `
  --body "Fixes #12345" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Always read existing sample files to understand patterns before writing new ones
- Samples must be standalone and runnable without requiring other sample files
- Use `DefaultAzureCredential` for authentication — never hardcode credentials
- Load all configuration values from environment variables using `os.environ`
- Include a clear description, usage instructions, and list of required env vars in every sample
- Prefer `os.environ["VAR_NAME"]` (raises KeyError on missing) over `os.environ.get("VAR_NAME")` for required vars
- Samples are validated by the `tox -e samples` environment using `test_run_samples.py`
- Each sample should demonstrate a single, focused scenario — keep samples concise and readable
- Always reference the GitHub issue in commits and PRs when applicable
