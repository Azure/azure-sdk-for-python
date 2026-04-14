---
name: fix-pylint
description: Automatically fix pylint issues in any Azure SDK for Python package following Azure SDK Python guidelines and existing code patterns. Expects GitHub issue URL, package path, and optional virtual env path in the request. Format "fix pylint issue <issue-url> [in <package-path>] [using venv <path>]"
---

# Fix Pylint Issues Skill

This skill automatically fixes pylint warnings in any Azure SDK for Python package by analyzing existing code patterns and applying fixes with 100% confidence based on GitHub issues.

## Overview

Intelligently fixes pylint issues by:
1. Getting the GitHub issue URL and package path from the user
2. Reading and analyzing the issue details
3. Setting up or using existing virtual environment
4. Installing required dependencies
5. Running pylint on the specific files/areas mentioned in the issue
6. Analyzing the pylint output to identify warnings
7. Searching codebase for existing patterns to follow
8. Applying fixes only with 100% confidence
9. Re-running pylint to verify fixes
10. Creating a pull request that references the GitHub issue
11. Providing a summary of what was fixed

## Running Pylint

**Command:**
```powershell
cd <package-path>
azpysdk --isolate pylint .
```

> **Note:** `azpysdk pylint` runs with a pinned version of pylint at the package level only. To focus on specific files, run the full check and filter the output by file path.

**Using Latest Pylint:**
```powershell
azpysdk --isolate next-pylint .
```

> Use `azpysdk next-pylint` to run with the latest version of pylint. This is useful for catching issues that may be flagged by newer pylint versions.

## Reference Documentation

- [Azure SDK Python Pylint Guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Official Pylint Documentation](https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html)
- [Azure SDK Python Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)

## Fixing Strategy

### Step 0: Get GitHub Issue and Package Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path (look for phrases like "in sdk/...", e.g. `sdk/storage/azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the pylint problems you want to fix."

**If package path is missing:**
Ask: "Please provide the package path (e.g. sdk/storage/azure-storage-blob)."

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

**Once you have the issue URL:**
Read the issue to understand which files/modules and specific warnings to fix.

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

### Step 3: Identify Target Files (within activated venv)

Based on the GitHub issue details, determine which files to check:

**Option A - Run pylint on the package and filter output:**
```powershell
# Ensure you're in the package directory (within activated venv)
cd <package-path>

# Run pylint on the full package, then filter output for files from the issue
azpysdk --isolate pylint .
# Review output for warnings in the specific files/modules mentioned in the issue
```

**Option B - Check modified files (if no specific target):**
```powershell
git diff --name-only HEAD | Select-String "<package-path>"
git diff --cached --name-only | Select-String "<package-path>"
```

### Step 4: Run Pylint (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

```powershell
# Navigate to the package directory
cd <package-path>

# Run pylint on the package (within activated venv)
azpysdk --isolate pylint .
# Filter output for the specific files/modules from the issue
```

### Step 5: Analyze Warnings

Parse the pylint output to identify:
- Warning type and code (e.g., C0103, W0212, R0913)
- File path and line number
- Specific issue description
- **Cross-reference with the GitHub issue** to ensure you're fixing the right problems

### Step 6: Search for Existing Patterns

Before fixing, search the codebase for how similar issues are handled:
```powershell
# Example: Search for similar function patterns
grep -r "pattern" <package-path>/
```

Use the existing code patterns to ensure consistency.

### Step 7: Apply Fixes (ONLY if 100% confident)

**ALLOWED ACTIONS:**
 Fix warnings with 100% confidence
 Use existing file patterns as reference
 Follow Azure SDK Python guidelines
 Make minimal, targeted changes

**FORBIDDEN ACTIONS:**
 Fix warnings without complete confidence
 Create new files for solutions
 Import non-existent modules
 Add new dependencies or imports
 Make unnecessary large changes
 Change code style without clear reason
 Delete code without clear justification

### Step 8: Verify Fixes

Re-run pylint to ensure:
- The warning is resolved
- No new warnings were introduced
- The code still functions correctly

### Step 9: Summary

Provide a summary:
- GitHub issue being addressed
- Number of warnings fixed
- Number of warnings remaining
- Types of fixes applied
- Any warnings that need manual review

### Step 10: Create Pull Request

After successfully fixing pylint issues, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage all modified files
git add .

# Create a descriptive commit message referencing the issue
git commit -m "fix(<package-name>): resolve pylint warnings (#<issue-number>)

- Fixed <list specific types of warnings>
- Updated <files/modules affected>
- All pylint checks now pass

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "fix/<package-name>-pylint-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "fix(<package-name>): Resolve pylint warnings (#<issue-number>)" `
  --body "## Description
This PR fixes pylint warnings in the <package-name> package as reported in #<issue-number>.

## Changes
- Fixed pylint warnings following Azure SDK Python guidelines
- Ensured consistency with existing code patterns
- Targeted fixes for: <specific files/modules from issue>
- All pylint checks now pass for the affected areas

## Testing
- [x] Ran pylint on affected files and verified all warnings are resolved
- [x] No new warnings introduced
- [x] Verified fixes follow existing code patterns

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

## Common Pylint Issues and Fixes

### Missing Docstrings

**Warning:** `C0111: Missing module/function/class docstring`

**Fix:** Add proper docstring following Azure SDK style:
```python
def function_name(param: str) -> None:
    """Brief description of function.
    
    :param param: Description of parameter
    :type param: str
    :return: None
    """
```

### Too Many Arguments

**Warning:** `R0913: Too many arguments`

**Fix:** Consider grouping related parameters into a configuration object or using keyword-only arguments.

### Line Too Long

**Warning:** `C0301: Line too long`

**Fix:** Break line at logical points following PEP 8 style.

### Unused Import

**Warning:** `W0611: Unused import`

**Fix:** Remove the unused import statement.

### Invalid Name

**Warning:** `C0103: Invalid name`

**Fix:** Rename to follow snake_case for functions/variables, PascalCase for classes.

## Example Workflow

```powershell
# 0. Get issue details
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/12345
# User provides package path: sdk/storage/azure-storage-blob
# Issue mentions: pylint warnings in azure/storage/blob/_blob_client.py

# 1. CRITICAL - Activate virtual environment FIRST
.\<venv-name>\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/storage/azure-storage-blob
pip install -r dev_requirements.txt
pip install -e .

# 2. Identify target from issue
$targetFile = "azure/storage/blob/_blob_client.py"

# 3. Run pylint on the package and check output for target file
azpysdk --isolate pylint .
# Filter output for warnings in $targetFile

# 4. Analyze output and identify fixable issues
# Cross-reference with GitHub issue #12345

# 5. Search for existing patterns in codebase
grep -r "similar_pattern" azure/storage/blob/

# 6. Apply fixes to identified files

# 7. Re-run pylint to verify
azpysdk --isolate pylint .

# 8. Report results

# 9. Create PR referencing the issue
$branchName = "fix/azure-storage-blob-pylint-12345"
git checkout -b $branchName
git add .
git commit -m "fix(azure-storage-blob): resolve pylint warnings (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "fix(azure-storage-blob): Resolve pylint warnings (#12345)" `
  --body "Fixes #12345" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Always read the existing code to understand patterns before making changes
- Prefer following existing patterns over strict rule compliance
- If unsure about a fix, mark it for manual review
- Some warnings may require architectural changes - don't force fixes
- Test the code after fixing to ensure functionality is preserved
- Always reference the GitHub issue in commits and PRs
