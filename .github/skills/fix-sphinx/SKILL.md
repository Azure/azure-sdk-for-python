---
name: fix-sphinx
description: Automatically fix Sphinx documentation issues in any Azure SDK for Python package following Azure SDK Python documentation standards. Expects GitHub issue URL, package path, and optional virtual env path in the request. Format "fix sphinx issue <issue-url> [in <package-path>] [using venv <path>]"
---

# Fix Sphinx Documentation Issues Skill

This skill automatically fixes Sphinx documentation warnings and errors in any Azure SDK for Python package by analyzing existing documentation patterns and applying fixes with 100% confidence based on GitHub issues.

## Overview

Intelligently fixes Sphinx documentation issues by:
1. Getting the GitHub issue URL and package path from the user
2. Reading and analyzing the issue details
3. Setting up or using existing virtual environment
4. Installing required documentation dependencies
5. Running Sphinx build on the specific package mentioned in the issue
6. Analyzing the Sphinx output to identify warnings and errors
7. Searching codebase for existing documentation patterns to follow
8. Applying fixes only with 100% confidence
9. Re-running Sphinx build to verify fixes
10. Creating a pull request that references the GitHub issue
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

### Step 0: Get GitHub Issue and Package Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Package path (look for phrases like "in sdk/...", e.g. `sdk/storage/azure-storage-blob`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the Sphinx documentation problems you want to fix."

**If package path is missing:**
Ask: "Please provide the package path (e.g. sdk/storage/azure-storage-blob)."

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

**Once you have the issue URL:**
Read the issue to understand which documentation files/modules and specific warnings to fix.

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
- **Cross-reference with the GitHub issue** to ensure you're fixing the right problems

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

After successfully fixing Sphinx issues, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage all modified files
git add .

# Create a descriptive commit message referencing the issue
git commit -m "fix(<package-name>): resolve sphinx documentation warnings (#<issue-number>)

- Fixed <list specific types of documentation warnings>
- Updated <files/modules affected>
- All Sphinx documentation checks now pass

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "fix/<package-name>-sphinx-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "fix(<package-name>): Resolve Sphinx documentation warnings (#<issue-number>)" `
  --body "## Description
This PR fixes Sphinx documentation warnings in the <package-name> package as reported in #<issue-number>.

## Changes
- Fixed Sphinx documentation warnings following Azure SDK Python documentation guidelines
- Ensured consistency with existing documentation patterns
- Targeted fixes for: <specific files/modules from issue>
- All Sphinx documentation checks now pass for the affected areas

## Testing
- [x] Ran Sphinx build on affected package and verified all warnings are resolved
- [x] No new warnings introduced
- [x] Verified fixes follow existing documentation patterns
- [x] Documentation builds successfully and renders correctly

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

## Common Sphinx Issues and Fixes

### Missing Docstrings

**Warning:** `WARNING: missing docstring for function/class/module`

**Fix:** Add proper docstring following Azure SDK style:
```python
def function_name(param: str) -> None:
    """Brief description of function.
    
    :param param: Description of parameter
    :type param: str
    :return: None
    :rtype: None
    """
```

### Invalid Cross-References

**Warning:** `WARNING: unknown document` or `WARNING: undefined label`

**Fix:** Ensure referenced modules/functions exist and are properly documented:
```python
# Instead of invalid reference
"""See :func:`nonexistent_function` for details."""

# Use correct reference
"""See :func:`azure.storage.blob.BlobClient.upload_blob` for details."""
```

### Malformed Docstring Syntax

**Warning:** `WARNING: Unexpected indentation` or `WARNING: Block quote ends without a blank line`

**Fix:** Ensure proper reStructuredText formatting:
```python
def example_function():
    """Example function with proper formatting.
    
    This is a properly formatted docstring with:
    
    - Proper indentation
    - Blank lines where needed
    - Consistent formatting
    """
```

### Missing Parameter Documentation

**Warning:** `WARNING: Parameter 'param_name' not documented`

**Fix:** Document all parameters:
```python
def function_with_params(param1: str, param2: int = 0) -> str:
    """Function with documented parameters.
    
    :param param1: Description of first parameter
    :type param1: str
    :param param2: Description of second parameter, defaults to 0
    :type param2: int
    :return: Description of return value
    :rtype: str
    """
```

### Inconsistent Type Documentation

**Warning:** `WARNING: type annotation and docstring type mismatch`

**Fix:** Ensure type annotations match docstring types:
```python
def function_name(param: Optional[str] = None) -> List[str]:
    """Function with consistent typing.
    
    :param param: Optional parameter
    :type param: str or None
    :return: List of strings
    :rtype: List[str]
    """
```

## Example Workflow

```powershell
# 0. Get issue details
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/12345
# User provides package path: sdk/storage/azure-storage-blob
# Issue mentions: Sphinx warnings in azure/storage/blob/_blob_client.py

# 1. CRITICAL - Activate virtual environment FIRST
.\<venv-name>\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/storage/azure-storage-blob
pip install -r dev_requirements.txt
pip install -e .

# 2. Identify target from issue
$targetFile = "azure/storage/blob/_blob_client.py"

# 3. Run Sphinx on the package and check output for target file
azpysdk --isolate sphinx .
# Review output for warnings/errors in $targetFile

# 4. Analyze output and identify fixable issues
# Cross-reference with GitHub issue #12345

# 5. Search for existing documentation patterns
grep -r ":param" azure/storage/blob/ -A 2
grep -r ":return:" azure/storage/blob/ -A 2

# 6. Apply fixes to identified files

# 7. Re-run Sphinx to verify
azpysdk --isolate sphinx .

# 8. Report results

# 9. Create PR referencing the issue
$branchName = "fix/azure-storage-blob-sphinx-12345"
git checkout -b $branchName
git add .
git commit -m "fix(azure-storage-blob): resolve sphinx documentation warnings (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "fix(azure-storage-blob): Resolve Sphinx documentation warnings (#12345)" `
  --body "Fixes #12345" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Always read existing documentation patterns to understand the style before making changes
- Prefer following existing documentation patterns over strict rule compliance
- If unsure about a fix, mark it for manual review
- Some warnings may require architectural changes - don't force fixes
- Test the documentation build after fixing to ensure it renders correctly
- Always reference the GitHub issue in commits and PRs
- Focus on documentation clarity and completeness for end users