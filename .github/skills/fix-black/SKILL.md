---
name: fix-black
description: Automatically fix black code formatting issues in any Azure SDK for Python package"
---

# Fix Black Formatting Issues Skill

This skill automatically fixes black code formatting issues in any Azure SDK for Python package.

## Overview

1. Install `eng/tools/azure-sdk-tools[build]`
2. Navigate to the package path
3. Run `azpysdk --isolate black .`

## Step 1: Install Tool

```powershell
cd <repo-root>
pip install -e eng/tools/azure-sdk-tools[build]
```

## Step 2: Run Black

```powershell
cd <package-path>
azpysdk --isolate black .
```

> **Note:** `azpysdk black` runs at the package level only.

## Step 3: Review Changes

```powershell
git diff --name-only
git diff
```

## Step 4: Commit changes

Stage and commit the changes. 

## Notes

- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration (line length 120, Python 3.8+)
