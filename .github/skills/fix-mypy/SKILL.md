---
name: fix-mypy
description: Automatically fix mypy type checking issues in any Azure SDK for Python package following Azure SDK Python patterns.
---

# Fix MyPy Issues Skill

This skill automatically fixes mypy type checking errors in any Azure SDK for Python package by analyzing existing code patterns and applying fixes with 100% confidence.

## Overview

Intelligently fixes mypy issues by:
1. Getting the package path or GitHub issue URL from the user
2. Reading and analyzing the issue details (if issue URL provided)
3. Setting up or using existing virtual environment
4. Installing required dependencies
5. Running mypy on the package
6. Analyzing the mypy output to identify type errors
7. Searching codebase for existing type annotation patterns
8. Applying fixes only with 100% confidence
9. Re-running mypy to verify fixes
10. Creating a pull request
11. Providing a summary of what was fixed

## Running MyPy

**Command:**
```powershell
cd <package-path>
azpysdk --isolate mypy .
```

> **Note:** `azpysdk mypy` runs with a pinned version of mypy at the package level only. To focus on specific files, run the full check and filter the output by file path.

**Using Latest MyPy:**
```powershell
azpysdk --isolate next-mypy .
```

> Use `azpysdk next-mypy` to run with the latest version of mypy. This is useful for catching issues that may be flagged by newer mypy versions.

## Reference Documentation

- [Azure SDK Python MyPy Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- [Official MyPy Documentation](https://mypy.readthedocs.io/en/stable/)
- [MyPy Common Issues](https://mypy.readthedocs.io/en/stable/common_issues.html)

## Fixing Strategy

### Step 0: Get Package and Issue Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path or name (e.g. `sdk/storage/azure-storage-blob` or `azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If both GitHub issue URL and package path are missing:**
Ask: "Please provide either the GitHub issue URL or the package path (e.g. sdk/storage/azure-storage-blob) for the mypy type checking problems you want to fix."

**If a GitHub issue URL is provided:**
Read the issue to understand which package and files/modules are affected, and the specific error codes to fix.

**If only a package path is provided:**
Run mypy checks directly on the package.

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

### Step 1: CRITICAL - Activate Virtual Environment FIRST

**IMMEDIATELY activate the virtual environment before ANY other command:**

```powershell
# Activate the provided virtual environment (e.g., env, venv)
.\<venv-name>\Scripts\Activate.ps1

# If creating new virtual environment
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

**Option A - Run mypy on the package and filter output:**
```powershell
# Ensure you're in the package directory (within activated venv)
cd <package-path>

# Run mypy on the full package, then filter output for files from the issue
azpysdk --isolate mypy .
# Review output for errors in the specific files/modules mentioned in the issue
```

**Option B - Check modified files (if no specific target):**
```powershell
git diff --name-only HEAD | Select-String "<package-path>"
git diff --cached --name-only | Select-String "<package-path>"
```

### Step 4: Run MyPy (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

```powershell
# Navigate to the package directory
cd <package-path>

# Run mypy on the package (within activated venv)
azpysdk --isolate mypy .
# Filter output for the specific files/modules from the issue
```

### Step 5: Analyze Type Errors

Parse the mypy output to identify:
- Error type and code (e.g., [arg-type], [return-value], [assignment])
- File path and line number
- Specific error description
- Expected vs actual types
- **Cross-reference with the GitHub issue** (if provided) to ensure you're fixing the right problems

### Step 6: Search for Existing Type Annotation Patterns

Before fixing, search the codebase for how similar types are annotated:
```powershell
# Example: Search for similar function signatures
grep -r "def similar_function" <package-path>/ -A 5

# Search for type imports
grep -r "from typing import" <package-path>/
```

Use the existing type annotation patterns to ensure consistency.

### Step 7: Apply Fixes (ONLY if 100% confident)

**ALLOWED ACTIONS:**
 Fix type errors with 100% confidence
 Use existing type annotation patterns as reference
 Follow Azure SDK Python type checking guidelines
 Add missing type hints
 Fix incorrect type annotations
 Make minimal, targeted changes

**FORBIDDEN ACTIONS:**
 Fix errors without complete confidence
 Create new files for solutions
 Import non-existent types or modules
 Add new dependencies or imports outside typing module
 Use `# type: ignore` without clear justification
 Change code logic to avoid type errors
 Delete code without clear justification

### Step 8: Verify Fixes

Re-run mypy to ensure:
- The type error is resolved
- No new errors were introduced
- The code still functions correctly

### Step 9: Summary

Provide a summary:
- GitHub issue being addressed
- Number of type errors fixed
- Number of errors remaining
- Types of fixes applied (e.g., added type hints, fixed return types)
- Any errors that need manual review

### Step 10: Create Pull Request

> **⚠️ REQUIRED when a GitHub issue URL was provided:** You MUST create a pull request after validating fixes. This is not optional.

Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all mypy checks pass. The PR title should follow the format: "fix(<package-name>): Resolve mypy type errors (#<issue-number>)".

## Notes

- Always read the existing code to understand type annotation patterns before making changes
- Prefer following existing patterns over adding new complex types
- Use Python 3.10+ compatible type hints (use `Optional[X]` instead of `X | None`)
- If unsure about a fix, mark it for manual review
- Some errors may require architectural changes - don't force fixes
- Test the code after fixing to ensure functionality is preserved
- Avoid using `# type: ignore` unless absolutely necessary and document why
