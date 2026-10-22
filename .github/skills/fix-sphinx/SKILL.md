---
name: fix-sphinx
description: Automatically fix Sphinx documentation issues in any Azure SDK for Python package following Azure SDK Python documentation standards.
---

# Fix Sphinx Documentation Issues Skill

This skill automatically fixes Sphinx documentation warnings and errors in any Azure SDK for Python package by analyzing existing documentation patterns and applying fixes with 100% confidence.

## Overview

Intelligently fixes Sphinx documentation issues by:
1. Getting the package path or GitHub issue URL from the user
2. Reading and analyzing the issue details (if issue URL provided)
3. Setting up or using existing virtual environment
4. Installing required documentation dependencies
5. Running Sphinx build on the package
6. Analyzing the Sphinx output to identify warnings and errors
7. Searching codebase for existing documentation patterns to follow
8. Applying fixes only with 100% confidence
9. Re-running Sphinx build to verify fixes
10. Creating a pull request
11. Providing a summary of what was fixed

## Running Sphinx

**Command:**
```powershell
cd <package-path>
azpysdk --isolate sphinx .
```

> **Note:** `azpysdk sphinx` runs Sphinx documentation build for the package. This checks for documentation warnings and errors.

**Using Latest Sphinx:**
```powershell
azpysdk --isolate next-sphinx .
```

> Use `azpysdk next-sphinx` to run with the latest version of Sphinx. This is useful for catching issues that may be flagged by newer Sphinx versions.

## Reference Documentation

- [Azure SDK Python Documentation Guide](https://azure.github.io/azure-sdk/python_documentation.html)
- [Sphinx Documentation](https://www.sphinx-doc.org/en/master/)
- [Azure SDK Python Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)

## Fixing Strategy

### Step 0: Get Package and Issue Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path or name (e.g. `sdk/storage/azure-storage-blob` or `azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If both GitHub issue URL and package path are missing:**
Ask: "Please provide either the GitHub issue URL or the package path (e.g. sdk/storage/azure-storage-blob) for the Sphinx documentation problems you want to fix."

**If a GitHub issue URL is provided:**
Read the issue to understand which package and documentation files/modules are affected, and the specific warnings to fix.

**If only a package path is provided:**
Run Sphinx checks directly on the package.

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

Based on the GitHub issue details, determine which documentation files to check:

**Option A - Run Sphinx on the package and review output:**
```powershell
# Ensure you're in the package directory (within activated venv)
cd <package-path>

# Run Sphinx build on the package
azpysdk --isolate sphinx .
# Review output for warnings/errors in the specific files/modules mentioned in the issue
```

**Option B - Check modified documentation files (if no specific target):**
```powershell
git diff --name-only HEAD | Select-String "\.py$|\.rst$|\.md$" | Select-String "<package-path>"
git diff --cached --name-only | Select-String "\.py$|\.rst$|\.md$" | Select-String "<package-path>"
```

### Step 4: Run Sphinx (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

```powershell
# Navigate to the package directory
cd <package-path>

# Run Sphinx build on the package (within activated venv)
azpysdk --isolate sphinx .
# Review output for the specific files/modules from the issue
```

### Step 5: Analyze Warnings and Errors

Parse the Sphinx output to identify:
- Warning/error type (e.g., missing docstring, invalid reference, malformed docstring)
- File path and line number
- Specific issue description
- **Cross-reference with the GitHub issue** (if provided) to ensure you're fixing the right problems

### Step 6: Search for Existing Patterns

Before fixing, search the codebase for how similar documentation is handled:
```powershell
# Example: Search for similar docstring patterns
grep -r "docstring_pattern" <package-path>/
grep -r ":param" <package-path>/
grep -r ":return:" <package-path>/
```

Use the existing documentation patterns to ensure consistency.

### Step 7: Apply Fixes (ONLY if 100% confident)

**ALLOWED ACTIONS:**
✅ Fix documentation warnings/errors with 100% confidence
✅ Use existing documentation patterns as reference
✅ Follow Azure SDK Python documentation guidelines
✅ Make minimal, targeted changes to docstrings
✅ Add missing docstrings following existing patterns
✅ Fix malformed docstring syntax
✅ Correct parameter and return type documentation

**FORBIDDEN ACTIONS:**
❌ Fix warnings without complete confidence
❌ Create new documentation files for solutions
❌ Import non-existent modules in documentation
❌ Add new dependencies or imports
❌ Make unnecessary large changes
❌ Change code logic without clear reason
❌ Delete documentation without clear justification

### Step 8: Verify Fixes

Re-run Sphinx to ensure:
- The warning/error is resolved
- No new warnings were introduced
- The documentation builds successfully
- The generated documentation looks correct

### Step 9: Summary

Provide a summary:
- GitHub issue being addressed
- Number of warnings/errors fixed
- Number of warnings/errors remaining
- Types of fixes applied
- Any documentation issues that need manual review

### Step 10: Create Pull Request

> **⚠️ REQUIRED when a GitHub issue URL was provided:** You MUST create a pull request after validating fixes. This is not optional.

Create a pull request with a descriptive title and body referencing the issue. Include what was fixed and confirm all Sphinx documentation checks pass. The PR title should follow the format: "fix(<package-name>): Resolve sphinx errors (#<issue-number>)".

## Notes

- Always read existing documentation patterns to understand the style before making changes
- Prefer following existing documentation patterns over strict rule compliance
- If unsure about a fix, mark it for manual review
- Some warnings may require architectural changes - don't force fixes
- Test the documentation build after fixing to ensure it renders correctly
- Focus on documentation clarity and completeness for end users