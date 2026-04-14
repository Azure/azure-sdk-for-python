---
name: fix-black
description: Automatically fix black code formatting issues in any Azure SDK for Python package
---

# Fix Black Formatting Issues Skill

This skill automatically fixes black code formatting issues in any Azure SDK for Python package.

## Overview

1. Activate virtual environment FIRST
2. Install `eng/tools/azure-sdk-tools[build]`
3. Navigate to the package path
4. Run `azpysdk --isolate black .`

## Step 1: CRITICAL - Activate Virtual Environment FIRST

**IMMEDIATELY activate the virtual environment before ANY other command:**

```powershell
# Activate the provided virtual environment (e.g., env, venv)
.\<venv-name>\Scripts\Activate.ps1

# If creating new virtual environment:
python -m venv env
.\env\Scripts\Activate.ps1
```

**⚠️ IMPORTANT: ALL subsequent commands MUST run within the activated virtual environment. Never run commands outside the venv.**

## Step 2: Install Tool (within activated venv)

```powershell
cd <repo-root>
pip install -e eng/tools/azure-sdk-tools[build]
```

## Step 3: Run Black (within activated venv)

```powershell
cd <package-path>
azpysdk --isolate black .
```

> **Note:** `azpysdk black` runs at the package level only.

## Step 4: Review Changes

```powershell
git diff --name-only
git diff
```

## Step 5: Commit changes

Stage and commit the changes. 

## Notes

- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration
