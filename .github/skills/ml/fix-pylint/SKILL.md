---
name: fix-pylint
description: Automatically fix pylint issues in azure-ai-ml package following Azure SDK Python guidelines and existing code patterns. Expects GitHub issue URL and optional virtual env path in the request. Format "fix pylint issue <issue-url> [using venv <path>]"
---

# Fix Pylint Issues Skill

This skill automatically fixes pylint warnings in the azure-ai-ml package by analyzing existing code patterns and applying fixes with 100% confidence based on GitHub issues.

## Overview

Intelligently fixes pylint issues by:
1. Getting the GitHub issue URL from the user
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

**Command for entire package:**
```powershell
cd sdk/ml/azure-ai-ml
tox -e pylint --c ../../../eng/tox/tox.ini --root .
```

**Command for specific file/module:**
```powershell
cd sdk/ml/azure-ai-ml
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- path/to/file.py
```

## Reference Documentation

- [Azure SDK Python Pylint Guidelines](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)
- [Official Pylint Documentation](https://pylint.readthedocs.io/en/stable/user_guide/checkers/features.html)
- [Azure SDK Python Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Tox Formatting Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)

## Fixing Strategy

### Step 0: Get GitHub Issue Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the pylint problems you want to fix."

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

**Once you have the issue URL:**
Read the issue to understand which files/modules and specific warnings to fix.

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

### Step 3: Identify Target Files (within activated venv)

Based on the GitHub issue details, determine which files to check:

**Option A - Issue specifies files:**
```powershell
# Ensure you're in azure-ai-ml directory (within activated venv)
cd sdk/ml/azure-ai-ml

# Run pylint on specific files mentioned in the issue (within activated venv)
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- path/to/specific_file.py
```

**Option B - Issue mentions module/directory:**
```powershell
# Run pylint on specific module (within activated venv)
cd sdk/ml/azure-ai-ml
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- azure/ai/ml/specific_module/
```

**Option C - Check modified files (if no specific target):**
```powershell
git diff --name-only HEAD | Select-String "sdk/ml/azure-ai-ml"
git diff --cached --name-only | Select-String "sdk/ml/azure-ai-ml"
```

### Step 4: Run Pylint (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

```powershell
# Navigate to azure-ai-ml directory
cd sdk/ml/azure-ai-ml

# Run pylint targeting the specific area from the issue (within activated venv)
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- <target-from-issue>
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
grep -r "pattern" sdk/ml/azure-ai-ml/
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

### Step 7: Verify Fixes

Re-run pylint to ensure:
- The warning is resolved
- No new warnings were introduced
- The code still functions correctly

### Step 8: Summary

Provide a summary:
- GitHub issue being addressed
- Number of warnings fixed
- Number of warnings remaining
- Types of fixes applied
- Any warnings that need manual review

### Step 9: Create Pull Request

After successfully fixing pylint issues, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage all modified files
git add .

# Create a descriptive commit message referencing the issue
git commit -m "fix(azure-ai-ml): resolve pylint warnings (#<issue-number>)

- Fixed <list specific types of warnings>
- Updated <files/modules affected>
- All pylint checks now pass

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "fix/azure-ai-ml-pylint-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "fix(azure-ai-ml): Resolve pylint warnings (#<issue-number>)" `
  --body "## Description
This PR fixes pylint warnings in the azure-ai-ml package as reported in #<issue-number>.

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
# Issue mentions: pylint warnings in azure/ai/ml/operations/job_operations.py

# 1. CRITICAL - Activate virtual environment FIRST
.\<venv-name>\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/ml/azure-ai-ml
pip install -r dev_requirements.txt
pip install -e .

# 2. Identify target from issue
$targetFile = "azure/ai/ml/operations/job_operations.py"

# 3. Run pylint on specific file
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- $targetFile

# 4. Analyze output and identify fixable issues
# Cross-reference with GitHub issue #12345

# 5. Search for existing patterns in codebase
grep -r "similar_pattern" azure/ai/ml/

# 6. Apply fixes to identified files

# 7. Re-run pylint to verify
tox -e pylint --c ../../../eng/tox/tox.ini --root . -- $targetFile

# 8. Report results

# 9. Create PR referencing the issue
$branchName = "fix/azure-ai-ml-pylint-12345"
git checkout -b $branchName
git add .
git commit -m "fix(azure-ai-ml): resolve pylint warnings (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "fix(azure-ai-ml): Resolve pylint warnings (#12345)" `
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
