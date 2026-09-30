---
name: fix-pylint
description: Automatically fix pylint issues in any Azure SDK for Python package following Azure SDK Python guidelines and existing code patterns.
---

# Fix Pylint Issues Skill

This skill automatically fixes pylint warnings in any Azure SDK for Python package by analyzing existing code patterns and applying fixes with 100% confidence.

## Overview

Intelligently fixes pylint issues by:
1. Getting the package path or GitHub issue URL from the user
2. Reading and analyzing the issue details (if issue URL provided)
3. Setting up or using existing virtual environment
4. Installing required dependencies
5. Running pylint on the package
6. Analyzing the pylint output to identify warnings
7. Searching codebase for existing patterns to follow
8. Applying fixes only with 100% confidence
9. Re-running pylint to verify fixes
10. Creating a pull request
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

### Step 0: Get Package and Issue Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path or name (e.g. `sdk/storage/azure-storage-blob` or `azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If both GitHub issue URL and package path are missing:**
Ask: "Please provide either the GitHub issue URL or the package path (e.g. sdk/storage/azure-storage-blob) for the pylint problems you want to fix."

**If a GitHub issue URL is provided:**
Read the issue to understand which package and files/modules are affected, and the specific warnings to fix.

**If only a package path is provided:**
Run pylint checks directly on the package.

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

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

**Important: Do not run black as part of the pylint fix workflow.** Running black will reformat the code and may mask or change the pylint warnings you are trying to fix. Only run pylint to identify and fix the specific warnings.

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
- **Cross-reference with the GitHub issue** (if provided) to ensure you're fixing the right problems

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

> **⚠️ REQUIRED when a GitHub issue URL was provided:** You MUST create a pull request after validating fixes. This is not optional.

Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all pylint checks pass. The PR title should follow the format: "fix(<package-name>): Resolve pylint errors (#<issue-number>)".

## Notes

- Always read the existing code to understand patterns before making changes
- Prefer following existing patterns over strict rule compliance
- If unsure about a fix, mark it for manual review
- Some warnings may require architectural changes - don't force fixes
- Test the code after fixing to ensure functionality is preserved
