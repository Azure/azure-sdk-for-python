---
name: fix-mypy
description: Automatically fix mypy type checking issues in azure-ai-ml package following Azure SDK Python patterns. Expects GitHub issue URL and optional virtual env path in the request. Format "fix mypy issue <issue-url> [using venv <path>]"
---

# Fix MyPy Issues Skill

This skill automatically fixes mypy type checking errors in the azure-ai-ml package by analyzing existing code patterns and applying fixes with 100% confidence based on GitHub issues.

## Overview

Intelligently fixes mypy issues by:
1. Getting the GitHub issue URL from the user
2. Reading and analyzing the issue details
3. Setting up or using existing virtual environment
4. Installing required dependencies
5. Running mypy on the specific files/areas mentioned in the issue
6. Analyzing the mypy output to identify type errors
7. Searching codebase for existing type annotation patterns
8. Applying fixes only with 100% confidence
9. Re-running mypy to verify fixes
10. Creating a pull request that references the GitHub issue
11. Providing a summary of what was fixed

## Running MyPy

**Command for entire package:**
```powershell
cd sdk/ml/azure-ai-ml
tox -e mypy --c ../../../eng/tox/tox.ini --root .
```

**Command for specific file/module:**
```powershell
cd sdk/ml/azure-ai-ml
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- path/to/file.py
```

## Reference Documentation

- [Azure SDK Python MyPy Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)
- [Tox Guidance](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#tox)
- [Official MyPy Documentation](https://mypy.readthedocs.io/en/stable/)
- [MyPy Common Issues](https://mypy.readthedocs.io/en/stable/common_issues.html)

## Fixing Strategy

### Step 0: Get GitHub Issue Details

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If GitHub issue URL is missing:**
Ask: "Please provide the GitHub issue URL for the mypy type checking problems you want to fix."

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

**Once you have the issue URL:**
Read the issue to understand which files/modules and specific error codes to fix.

### Step 1: CRITICAL - Activate Virtual Environment FIRST

**IMMEDIATELY activate the virtual environment before ANY other command:**

```powershell
# Activate the provided virtual environment (e.g., envml, env, venv)
.\<venv-name>\Scripts\Activate.ps1

# If creating new virtual environment (Python 3.9+):
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

**Important:** Use Python 3.9 compatible environment for mypy checks.

### Step 3: Identify Target Files (within activated venv)

Based on the GitHub issue details, determine which files to check:

**Option A - Issue specifies files:**
```powershell
# Ensure you're in azure-ai-ml directory (within activated venv)
cd sdk/ml/azure-ai-ml

# Run mypy on specific files mentioned in the issue (within activated venv)
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- path/to/specific_file.py
```

**Option B - Issue mentions module/directory:**
```powershell
# Run mypy on specific module (within activated venv)
cd sdk/ml/azure-ai-ml
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- azure/ai/ml/specific_module/
```

**Option C - Check modified files (if no specific target):**
```powershell
git diff --name-only HEAD | Select-String "sdk/ml/azure-ai-ml"
git diff --cached --name-only | Select-String "sdk/ml/azure-ai-ml"
```

### Step 4: Run MyPy (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

```powershell
# Navigate to azure-ai-ml directory
cd sdk/ml/azure-ai-ml

# Run mypy targeting the specific area from the issue (within activated venv)
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- <target-from-issue>
```

### Step 5: Analyze Type Errors

Parse the mypy output to identify:
- Error type and code (e.g., [arg-type], [return-value], [assignment])
- File path and line number
- Specific error description
- Expected vs actual types
- **Cross-reference with the GitHub issue** to ensure you're fixing the right problems

### Step 6: Search for Existing Type Annotation Patterns

Before fixing, search the codebase for how similar types are annotated:
```powershell
# Example: Search for similar function signatures
grep -r "def similar_function" sdk/ml/azure-ai-ml/ -A 5

# Search for type imports
grep -r "from typing import" sdk/ml/azure-ai-ml/
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

### Step 7: Verify Fixes

Re-run mypy to ensure:
- The type error is resolved
- No new errors were introduced
- The code still functions correctly

### Step 8: Summary

Provide a summary:
- GitHub issue being addressed
- Number of type errors fixed
- Number of errors remaining
- Types of fixes applied (e.g., added type hints, fixed return types)
- Any errors that need manual review

### Step 9: Create Pull Request

After successfully fixing mypy issues, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage all modified files
git add .

# Create a descriptive commit message referencing the issue
git commit -m "fix(azure-ai-ml): resolve mypy type checking errors (#<issue-number>)

- Fixed <list specific types of errors>
- Added type hints to <files/modules affected>
- All mypy checks now pass

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "fix/azure-ai-ml-mypy-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "fix(azure-ai-ml): Resolve mypy type checking errors (#<issue-number>)" `
  --body "## Description
This PR fixes mypy type checking errors in the azure-ai-ml package as reported in #<issue-number>.

## Changes
- Fixed mypy type checking errors following Azure SDK Python guidelines
- Ensured consistency with existing type annotation patterns
- Targeted fixes for: <specific files/modules from issue>
- All mypy checks now pass for the affected areas

## Testing
- [x] Ran mypy on affected files and verified all errors are resolved
- [x] No new errors introduced
- [x] Verified fixes follow existing patterns
- [x] Used Python 3.9 compatible type hints

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

## Common MyPy Issues and Fixes

### Missing Type Hints

**Error:** `Function is missing a type annotation`

**Fix:** Add proper type hints:
```python
from typing import Optional

def function_name(param: str, optional_param: Optional[int] = None) -> None:
    """Brief description."""
    pass
```

### Argument Type Mismatch

**Error:** `Argument 1 to "function" has incompatible type "X"; expected "Y"`

**Fix:** Ensure the argument matches the expected type or add proper type conversion:
```python
# If expecting str but passing int
value: str = str(int_value)

# Or fix the function signature if the type is incorrect
def function(param: Union[str, int]) -> None:
    pass
```

### Return Type Mismatch

**Error:** `Incompatible return value type (got "X", expected "Y")`

**Fix:** Ensure the return type matches the annotation:
```python
from typing import Optional

def get_value() -> Optional[str]:
    if condition:
        return "value"
    return None  # Not empty string if Optional
```

### Type Annotation with Optional

**Error:** `Item "None" of "Optional[X]" has no attribute "Y"`

**Fix:** Add None check before accessing attributes:
```python
from typing import Optional

def process(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.upper()
```

### Union Types

**Error:** `Argument has incompatible type`

**Fix:** Use Union for multiple acceptable types:
```python
from typing import Union

def function(param: Union[str, int, None]) -> str:
    if param is None:
        return ""
    return str(param)
```

### List/Dict Type Annotations

**Error:** `Need type annotation for variable`

**Fix:** Add specific type annotations for collections:
```python
from typing import List, Dict, Any

items: List[str] = []
config: Dict[str, Any] = {}
```

## Example Workflow

```powershell
# 0. Get issue details
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/67890
# Issue mentions: mypy errors in azure/ai/ml/entities/job.py

# 1. CRITICAL - Activate virtual environment FIRST
.\<venv-name>\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/ml/azure-ai-ml
pip install -r dev_requirements.txt
pip install -e .

# 2. Identify target from issue
$targetFile = "azure/ai/ml/operations/job_operations.py"

# 3. Run mypy on specific file
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- $targetFile

# 4. Analyze output and identify fixable issues
# Cross-reference with GitHub issue #12345

# 5. Search for existing type annotation patterns
grep -r "from typing import" azure/ai/ml/ | findstr "operations"

# 6. Apply fixes to identified files

# 7. Re-run mypy to verify
tox -e mypy --c ../../../eng/tox/tox.ini --root . -- $targetFile

# 8. Report results

# 9. Create PR referencing the issue
$branchName = "fix/azure-ai-ml-mypy-12345"
git checkout -b $branchName
git add .
git commit -m "fix(azure-ai-ml): resolve mypy type checking errors (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "fix(azure-ai-ml): Resolve mypy type checking errors (#12345)" `
  --body "Fixes #12345" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Always read the existing code to understand type annotation patterns before making changes
- Prefer following existing patterns over adding new complex types
- Use Python 3.9+ compatible type hints (use `Optional[X]` instead of `X | None`)
- If unsure about a fix, mark it for manual review
- Some errors may require architectural changes - don't force fixes
- Test the code after fixing to ensure functionality is preserved
- Always reference the GitHub issue in commits and PRs
- Avoid using `# type: ignore` unless absolutely necessary and document why
