---
name: fix-black
description: Automatically fix black code formatting issues in any Azure SDK for Python package. Expects GitHub issue URL, package path, and optional virtual env path in the request. Format "fix black issue <issue-url> [in <package-path>] [using venv <path>]"
---

# Fix Black Formatting Issues Skill

This skill automatically fixes black code formatting issues in any Azure SDK for Python package.

## Overview

1. Get the GitHub issue URL and package path from the user
2. Install `eng/tools/azure-sdk-tools[build]`
3. Run `azpysdk --isolate black .`
4. Create a pull request with the changes

## Step 0: Get GitHub Issue and Package Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path (look for phrases like "in sdk/...", e.g. `sdk/storage/azure-storage-blob`)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the black formatting problems you want to fix."

**If package path is missing:**
Ask: "Please provide the package path (e.g. sdk/storage/azure-storage-blob)."

**Once you have the issue URL:**
Read the issue to understand which files/modules need reformatting.

## Step 1: Install Tool

```powershell
pip install -e eng/tools/azure-sdk-tools[build]
```

## Step 2: Run Black

```powershell
cd <package-path>
azpysdk --isolate black .
```

> **Note:** `azpysdk black` runs at the package level only. The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration.

## Step 3: Review Changes

```powershell
git diff --name-only
git diff
```

## Step 4: Create Pull Request

**Stage and commit the changes:**
```powershell
$branchName = "style/<package-name>-black-<issue-number>"
git checkout -b $branchName
git add .
git commit -m "style(<package-name>): apply black code formatting (#<issue-number>)

Closes #<issue-number>"
git push origin $branchName
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
gh pr create `
  --title "style(<package-name>): Apply black code formatting (#<issue-number>)" `
  --body "Fixes #<issue-number>" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

Option 2 - Manual PR creation (if GitHub CLI not available):
1. Push branch: `git push origin <branch-name>`
2. Navigate to: https://github.com/Azure/azure-sdk-for-python/compare/main...<branch-name>
3. Create the pull request manually.

Option 3 - Using GitHub MCP server (if available):
Use the GitHub MCP tools to create a pull request programmatically against the Azure/azure-sdk-for-python repository, main branch.

## Notes

- Black is an opinionated auto-formatter — it never changes code semantics
- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide configuration (line length 120, Python 3.8+)
- Always reference the GitHub issue in commits and PRs
