---
name: fix-black
description: Automatically fix black code formatting issues in any Azure SDK for Python package. Expects GitHub issue URL, package path, and optional virtual env path in the request. Format "fix black issue <issue-url> [in <package-path>] [using venv <path>]"
---

# Fix Black Formatting Issues Skill

This skill automatically fixes black code formatting issues in any Azure SDK for Python package by running the black formatter and creating a pull request with the changes.

## Overview

Intelligently fixes black formatting issues by:
1. Getting the GitHub issue URL and package path from the user
2. Reading and analyzing the issue details
3. Setting up or using existing virtual environment
4. Installing required dependencies
5. Running black on the package to auto-format code
6. Verifying the formatting changes
7. Creating a pull request that references the GitHub issue
8. Providing a summary of what was formatted

## Running Black

**Command for entire package:**
```powershell
python -m azpysdk black --pkg-path <package-path>
```

**Command for specific file/module:**
```powershell
python -m azpysdk black --pkg-path <package-path> -- path/to/file.py
```

## Reference Documentation

- [Black Documentation](https://black.readthedocs.io/en/stable/)
- [Azure SDK Python Black Configuration](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/black-pyproject.toml)

## Fixing Strategy

### Step 0: Get GitHub Issue and Package Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path (look for phrases like "in sdk/...", e.g. `sdk/storage/azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the black formatting problems you want to fix."

**If package path is missing:**
Ask: "Please provide the package path (e.g. sdk/storage/azure-storage-blob)."

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

**Once you have the issue URL:**
Read the issue to understand which files/modules need reformatting.

### Step 1: CRITICAL - Activate Virtual Environment FIRST

**IMMEDIATELY activate the virtual environment before ANY other command:**

```powershell
# Activate the provided virtual environment (e.g., env, venv)
.\<venv-name>\Scripts\Activate.ps1

# If creating new virtual environment:
python -m venv env
.\env\Scripts\Activate.ps1
```

**⚠️ IMPORTANT: ALL subsequent commands MUST run within the activated virtual environment. Never run commands outside the venv.**

### Step 2: Install Dependencies (within activated venv)

```powershell
# Navigate to the package directory (within activated venv)
cd <package-path>

# Install dev dependencies from dev_requirements.txt (within activated venv)
pip install -r dev_requirements.txt

# Install the package in editable mode (within activated venv)
pip install -e .
```

### Step 3: Run Black to Auto-Format (within activated venv)

Black is an auto-formatter — it rewrites files to comply with the style. Simply run the command and it applies all changes automatically.

**Format entire package:**
```powershell
# Run black on the entire package (within activated venv)
python -m azpysdk black --pkg-path <package-path>
```

**Format specific files (if issue mentions specific files):**
```powershell
# Run black on specific files (within activated venv)
python -m azpysdk black --pkg-path <package-path> -- path/to/specific_file.py
```

### Step 4: Review Changes

After running black, review the changes that were made:

```powershell
# See which files were modified
git diff --name-only

# Review the actual changes
git diff
```

### Step 5: Verify No Remaining Formatting Issues

Re-run black in check mode to confirm all files are now properly formatted:

```powershell
# Verify formatting (within activated venv)
python -m azpysdk black --pkg-path <package-path>
```

If black reports no files were changed, all formatting issues are resolved.

### Step 6: Summary

Provide a summary:
- GitHub issue being addressed
- Number of files reformatted
- Types of formatting changes applied (line length, string quotes, trailing commas, etc.)

### Step 7: Create Pull Request

After successfully fixing black formatting issues, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage all modified files
git add .

# Create a descriptive commit message referencing the issue
git commit -m "style(<package-name>): apply black code formatting (#<issue-number>)

- Reformatted files to comply with black code style
- Applied Azure SDK Python black configuration

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "style/<package-name>-black-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "style(<package-name>): Apply black code formatting (#<issue-number>)" `
  --body "## Description
This PR applies black code formatting to the <package-name> package as reported in #<issue-number>.

## Changes
- Applied black code formatting following Azure SDK Python configuration
- All files now comply with the repo-wide black style settings

## Testing
- [x] Ran black on affected files and verified all formatting is correct
- [x] No functional code changes, formatting only

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

## Black Configuration

The Azure SDK for Python uses a repo-wide black configuration located at `eng/black-pyproject.toml`. Key settings include:
- Line length: 120 characters
- Target Python versions: 3.8+

The `python -m azpysdk black` command automatically uses this configuration, so no manual configuration is needed.

## Common Black Formatting Changes

### Line Too Long
Black will automatically break long lines at 120 characters using Python's implicit line continuation inside brackets.

### String Quotes
Black normalizes string quotes to double quotes throughout the file.

### Trailing Commas
Black adds trailing commas to multi-line data structures and function signatures where appropriate.

### Blank Lines
Black ensures consistent blank lines between top-level definitions (2 blank lines) and methods (1 blank line).

## Example Workflow

```powershell
# 0. Get issue details
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/99999
# User provides package path: sdk/storage/azure-storage-blob
# Issue mentions: black formatting failures in CI

# 1. CRITICAL - Activate virtual environment FIRST
.\<venv-name>\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/storage/azure-storage-blob
pip install -r dev_requirements.txt
pip install -e .

# 2. Run black to auto-format the package
python -m azpysdk black --pkg-path sdk/storage/azure-storage-blob

# 3. Review what changed
git diff --name-only
git diff

# 4. Verify no remaining issues
python -m azpysdk black --pkg-path sdk/storage/azure-storage-blob

# 5. Create PR referencing the issue
$branchName = "style/azure-storage-blob-black-99999"
git checkout -b $branchName
git add .
git commit -m "style(azure-storage-blob): apply black code formatting (#99999)

Closes #99999"
git push origin $branchName
gh pr create `
  --title "style(azure-storage-blob): Apply black code formatting (#99999)" `
  --body "Fixes #99999" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Black is an opinionated formatter with no configuration options beyond line length and target version
- Changes are purely cosmetic — black never changes the semantics of your code
- Always review the diff after running black to understand what changed
- The Azure SDK uses `eng/black-pyproject.toml` for repo-wide black configuration
- If a file has `# fmt: off` / `# fmt: on` comments, black will skip those sections intentionally
- Always reference the GitHub issue in commits and PRs
