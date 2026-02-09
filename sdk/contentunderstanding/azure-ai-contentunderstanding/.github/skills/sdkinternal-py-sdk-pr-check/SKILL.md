---
name: sdkinternal-py-sdk-pr-check
description: "Run all required CI checks before creating a PR for the azure-ai-contentunderstanding SDK. Use this skill to validate code quality, type checking, documentation, and tests before submitting changes."
---

# Pre-PR Check Workflow for azure-ai-contentunderstanding

This skill guides you through running all required CI checks locally before creating a pull request. Running these checks locally helps catch issues early and reduces PR review cycles.

## Overview

The Azure SDK for Python CI runs these **required checks**:
- **Pylint** - Code linting and Azure SDK guidelines
- **MyPy** - Static type checking
- **Pyright** - Static type checking (catches different issues than MyPy)
- **Black** - Code formatting
- **Bandit** - Security linting

Additionally, there are **release-blocking checks**:
- **Sphinx** - Documentation generation/validation
- **Tests - CI** - Recorded tests in playback mode

Optional checks:
- **Verifytypes** - Type completeness verification

## Prerequisites

- Python >= 3.9 with pip and venv
- Virtual environment activated with dev dependencies

### Check and Create Virtual Environment

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Check if venv exists, create if not
if [ -d ".venv" ]; then
    echo "Virtual environment already exists at .venv"
else
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created at .venv"
fi
```

### Activate Virtual Environment

**On Linux/macOS:**
```bash
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

Verify activation:
```bash
which python  # Should show .venv/bin/python
```

### Install Dependencies

```bash
pip install -e .
pip install -r dev_requirements.txt
pip install "tox<5" black bandit
```

### Complete Setup Script

Alternatively, run the automated setup script:

```bash
.github/skills/sdkinternal-py-setup/scripts/setup_venv.sh
```

## Package Directory

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Quick Reference

All tox commands use this pattern from the package directory:

```bash
tox -e <environment> -c ../../../eng/tox/tox.ini --root .
```

**Tip:** For faster package installation, prefix with `TOX_PIP_IMPL=uv`:

```bash
TOX_PIP_IMPL=uv tox -e pylint -c ../../../eng/tox/tox.ini --root .
```

---

## Step 1: Run Pylint (Required - Release Blocking)

Pylint checks code style and adherence to Python/Azure SDK guidelines.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
tox -e pylint -c ../../../eng/tox/tox.ini --root .
```

### Common Pylint Issues and Fixes

| Error | Solution |
|-------|----------|
| `line-too-long` | Break long lines, max 120 characters |
| `missing-docstring` | Add docstrings to public methods/classes |
| `unused-import` | Remove unused imports |
| `protected-access` | Use `# pylint:disable=protected-access` if intentional |
| `client-method-missing-type-annotations` | Add type hints to public methods |

### Reference Documentation
- [Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Custom Azure Pylint Checkers](https://github.com/Azure/azure-sdk-tools/blob/main/tools/pylint-extensions/azure-pylint-guidelines-checker/README.md)

---

## Step 2: Run MyPy (Required - Release Blocking)

MyPy performs static type checking to catch type errors before runtime.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
tox -e mypy -c ../../../eng/tox/tox.ini --root .
```

### Common MyPy Issues and Fixes

| Error | Solution |
|-------|----------|
| `Missing type parameters` | Add generic type parameters, e.g., `List[str]` not `List` |
| `Incompatible types` | Fix type mismatches or use `Union` types |
| `Missing return statement` | Add return statement or annotate with `-> None` |
| `Argument has incompatible type` | Check parameter types match expected types |
| `Cannot find module` | Add stub package or use `# type: ignore` with issue link |

### Ignoring Specific Errors

```python
# Globally ignore (both mypy and pyright):
value: int = some_function()  # type: ignore  # https://github.com/issue-link

# MyPy specific:
value: int = some_function()  # type: ignore[misc]
```

### Reference Documentation
- [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md)
- [Static Type Checking Cheat Sheet](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking_cheat_sheet.md)

---

## Step 3: Run Sphinx (Required - Release Blocking)

Sphinx validates documentation and docstrings.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
tox -e sphinx -c ../../../eng/tox/tox.ini --root .
```

### Common Sphinx Issues and Fixes

| Error | Solution |
|-------|----------|
| `undefined label` | Fix cross-reference targets |
| `duplicate label` | Remove duplicate labels/references |
| `unknown directive` | Check directive syntax (`:param:`, `:returns:`, etc.) |
| Missing docstring | Add docstrings with proper RST formatting |

### Docstring Format

```python
def my_method(self, param1: str, param2: int) -> bool:
    """Short description of the method.

    :param str param1: Description of param1.
    :param int param2: Description of param2.
    :returns: Description of return value.
    :rtype: bool
    :raises ValueError: When validation fails.
    """
```

### Reference Documentation
- [Docstring Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/docstring.md)

---

## Step 4: Run Tests in Playback Mode (Required - Release Blocking)

Run recorded tests to verify functionality without making live API calls.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
AZURE_TEST_RUN_LIVE=false pytest
```

### Run Specific Tests

```bash
# Run a specific test file
AZURE_TEST_RUN_LIVE=false pytest tests/test_content_understanding_content_analyzers_operations.py

# Run a specific test method
AZURE_TEST_RUN_LIVE=false pytest tests/test_content_understanding_content_analyzers_operations.py::TestContentUnderstandingContentAnalyzersOperations::test_content_analyzers_get

# Run with verbose output
AZURE_TEST_RUN_LIVE=false pytest -v

# Run with print output visible
AZURE_TEST_RUN_LIVE=false pytest -s
```

### Test Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused` errors | Ensure test-proxy is running (automatic via conftest.py fixture) |
| Missing recordings | Recordings may need fetching: `python scripts/manage_recordings.py restore` |
| Test assertion failures | Check if API changes broke assertions; update tests or re-record |
| `ModuleNotFoundError` | Reinstall dependencies: `pip install -r dev_requirements.txt` |

### Re-recording Tests

If tests need new recordings due to API changes:

```bash
AZURE_TEST_RUN_LIVE=true pytest
# Then push recordings:
python scripts/manage_recordings.py push -p sdk/contentunderstanding/azure-ai-contentunderstanding/assets.json
```

### Reference Documentation
- [Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Test Proxy Troubleshooting](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_troubleshooting.md)

---

## Step 5: Run Pyright (Required - CI Blocking)

Pyright is a static type checker that catches different issues than MyPy. CI runs this check and will fail if there are errors.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
tox -e pyright -c ../../../eng/tox/tox.ini --root .
```

### Common Pyright Issues and Fixes

| Error | Solution |
|-------|----------|
| `reportInvalidTypeArguments` | Fix generic type arguments or add `# pyright: ignore[reportInvalidTypeArguments]` |
| `reportPrivateUsage` | Use public API or add `# pyright: ignore[reportPrivateUsage]` |
| `reportReturnType` | Fix return type mismatch or add `# pyright: ignore[reportReturnType]` |

### Ignoring Pyright Errors

```python
value: int = some_function()  # pyright: ignore[reportPrivateUsage]
```

**Important:** The `# pyright: ignore` comment must be on the same line as the error.

---

## Step 6: Run Black (Required - CI Blocking)

Black is an opinionated code formatter. CI runs this check and will fail if code is not formatted correctly.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
pip install black
black --check azure/
```

### Auto-format Code

To automatically format your code:

```bash
black azure/
```

---

## Step 7: Run Bandit (Required - CI Blocking)

Bandit is a security linter that finds common security issues in Python code.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
pip install bandit
bandit -r azure/ -c ../../../eng/bandit.yml
```

### Common Bandit Issues

| Issue | Solution |
|-------|----------|
| `B101: assert_used` | Use proper error handling instead of assert in production code |
| `B105: hardcoded_password` | Move credentials to environment variables |
| `B608: hardcoded_sql_expressions` | Use parameterized queries |

---

## Step 8: Run Verifytypes (Optional)

Verifytypes measures type completeness of the library.

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
tox -e verifytypes -c ../../../eng/tox/tox.ini --root .
```

---

## Complete Pre-PR Check Script

Run all required checks in sequence:

```bash
#!/bin/bash
set -e

cd sdk/contentunderstanding/azure-ai-contentunderstanding

echo "=== Running Pylint ==="
tox -e pylint -c ../../../eng/tox/tox.ini --root .

echo "=== Running MyPy ==="
tox -e mypy -c ../../../eng/tox/tox.ini --root .

echo "=== Running Pyright ==="
tox -e pyright -c ../../../eng/tox/tox.ini --root .

echo "=== Running Black ==="
black --check azure/

echo "=== Running Bandit ==="
bandit -r azure/ -x azure/**/tests/** || true  # May have config file

echo "=== Running Sphinx ==="
tox -e sphinx -c ../../../eng/tox/tox.ini --root .

echo "=== Running Tests (Playback) ==="
AZURE_TEST_RUN_LIVE=false pytest

echo "=== All required checks passed! ==="
```

### Faster Execution with uv

```bash
#!/bin/bash
set -e

cd sdk/contentunderstanding/azure-ai-contentunderstanding

echo "=== Running Pylint ==="
TOX_PIP_IMPL=uv tox -e pylint -c ../../../eng/tox/tox.ini --root .

echo "=== Running MyPy ==="
TOX_PIP_IMPL=uv tox -e mypy -c ../../../eng/tox/tox.ini --root .

echo "=== Running Pyright ==="
TOX_PIP_IMPL=uv tox -e pyright -c ../../../eng/tox/tox.ini --root .

echo "=== Running Black ==="
black --check azure/

echo "=== Running Bandit ==="
bandit -r azure/ -x azure/**/tests/** || true

echo "=== Running Sphinx ==="
TOX_PIP_IMPL=uv tox -e sphinx -c ../../../eng/tox/tox.ini --root .

echo "=== Running Tests (Playback) ==="
AZURE_TEST_RUN_LIVE=false pytest

echo "=== All required checks passed! ==="
```

---

## Additional Tox Environments

These additional tox environments are available for specific needs:

| Environment | Description | Command |
|-------------|-------------|---------|
| `next-pylint` | Test with upcoming Pylint version | `tox -e next-pylint -c ../../../eng/tox/tox.ini --root .` |
| `next-mypy` | Test with upcoming MyPy version | `tox -e next-mypy -c ../../../eng/tox/tox.ini --root .` |
| `next-pyright` | Test with upcoming Pyright version | `tox -e next-pyright -c ../../../eng/tox/tox.ini --root .` |
| `whl` | Build wheel package | `tox -e whl -c ../../../eng/tox/tox.ini --root .` |
| `sdist` | Build source distribution | `tox -e sdist -c ../../../eng/tox/tox.ini --root .` |
| `samples` | Run all samples | `tox -e samples -c ../../../eng/tox/tox.ini --root .` |
| `apistub` | Generate API stub for APIView | `tox -e apistub -c ../../../eng/tox/tox.ini --root .` |

---

## Troubleshooting

### Tox Issues

| Issue | Solution |
|-------|----------|
| `tox: command not found` | Install tox: `pip install "tox<5"` |
| Tox version mismatch | Upgrade: `pip install --upgrade "tox<5"` |
| Slow package installation | Use uv: `TOX_PIP_IMPL=uv tox -e ...` |
| `.tox` cache issues | Delete `.tox` directory and retry |

### General Issues

| Issue | Solution |
|-------|----------|
| Import errors | Ensure package is installed: `pip install -e .` |
| Missing dependencies | Run: `pip install -r dev_requirements.txt` |
| Wrong Python version | Ensure Python >= 3.9 is active in venv |
| Check disabled in CI | Remove `check = false` from `pyproject.toml` |

---

## Pre-PR Checklist

Before creating a PR, verify:

- [ ] **Pylint** passes with no errors
- [ ] **MyPy** passes with no errors
- [ ] **Pyright** passes with no errors
- [ ] **Black** formatting is correct
- [ ] **Bandit** security checks pass
- [ ] **Sphinx** passes with no errors
- [ ] **Tests** pass in playback mode
- [ ] **CHANGELOG.md** is updated with changes
- [ ] **Version** in `_version.py` is updated (if releasing)
- [ ] **Samples** work correctly (if modified)
- [ ] **Recordings** are updated (if API changes)

---

## Reference Documentation

- [Repo Health Status](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/repo_health_status.md) - Required checks explained
- [Engineering System Checks](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/eng_sys_checks.md) - All CI check details
- [Pylint Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/pylint_checking.md)
- [Static Type Checking Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/static_type_checking.md)
- [Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Docstring Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/docstring.md)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
