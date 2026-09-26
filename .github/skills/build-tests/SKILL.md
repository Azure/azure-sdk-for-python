---
name: build-tests
description: Build, write, and run tests for any Azure SDK for Python package following Azure SDK Python testing guidelines. Optionally accepts a GitHub issue URL for context, a package path, and a virtual env path. Format: "build tests [for <issue-url>] [in <package-path>] [using venv <path>]"
---

# Build Tests Skill

This skill sets up the environment, installs dependencies, runs existing tests, and helps write new tests for any Azure SDK for Python package following Azure SDK Python testing guidelines.

## Overview

Intelligently builds and runs tests by:
1. Getting the optional GitHub issue URL and virtual environment path from the user
2. Activating or creating a virtual environment
3. Installing required dependencies
4. Configuring test mode (playback vs. live)
5. Running tests via pytest or tox
6. Analyzing failures and fixing or reporting them
7. Writing new tests if requested (following `AzureRecordedTestCase` pattern)
8. Verifying tests pass in both playback and live modes
9. Creating a pull request if new tests were written
10. Providing a summary of test results

## Running Tests

**Command for entire package (tox):**
```powershell
cd sdk/<service>/<package>
tox -e whl --c ../../../eng/tox/tox.ini --root .
```

**Command for specific test file (pytest):**
```powershell
cd sdk/<service>/<package>
pytest tests/test_specific_file.py -v
```

**Command for specific test class or method:**
```powershell
cd sdk/<service>/<package>
pytest tests/test_specific_file.py::TestClassName::test_method_name -v
```

**Run all tests in playback mode (default):**
```powershell
cd sdk/<service>/<package>
pytest tests/ -v
```

**Run tests in live mode:**
```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
cd sdk/<service>/<package>
pytest tests/ -v
```

## Reference Documentation

- [Azure SDK Python Tests Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md)
- [Advanced Tests Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests-advanced.md)
- [devtools_testutils README](https://github.com/Azure/azure-sdk-for-python/tree/main/tools/azure-sdk-tools/devtools_testutils)
- [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Tox Tool Usage Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/tool_usage_guide.md)

## Fixing Strategy

### Step 0: Gather Context

**Check if user provided in their request:**
- GitHub issue URL (look for `https://github.com/Azure/azure-sdk-for-python/issues/...` in user's message) — optional, for context
- Package path (look for phrases like "in sdk/...", "for package", or a path like `sdk/<service>/<package>`)
- Virtual environment path (look for phrases like "using venv", "use env", "virtual environment at", or just the venv name)

**If package path is missing:**
Ask: "Which package do you want to run tests for? Please provide the path (e.g., `sdk/<service>/<package>`)."

**If GitHub issue URL is provided:**
Read the issue to understand which tests to run or write, and what functionality to validate.

**If virtual environment is missing:**
Ask: "Do you have an existing virtual environment path, or should I create 'env'?"

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
# Navigate to the package directory (within activated venv)
cd sdk/<service>/<package>

# Install dev dependencies from dev_requirements.txt (within activated venv)
pip install -r dev_requirements.txt

# Install the package in editable mode (within activated venv)
pip install -e .
```

### Step 3: Configure Test Mode (within activated venv)

**Playback mode (default — no live credentials needed):**
```powershell
# Leave AZURE_TEST_RUN_LIVE unset (default is playback)
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
```

**Live mode (requires Azure credentials):**
```powershell
# Set environment variable to run against live Azure services
$env:AZURE_TEST_RUN_LIVE = "true"

# Ensure credentials are configured (e.g., via Azure CLI)
az login
```

### Step 4: Run Tests (within activated venv)

**⚠️ Ensure virtual environment is still activated before running:**

**Option A - Run all tests via tox:**
```powershell
cd sdk/<service>/<package>
tox -e whl --c ../../../eng/tox/tox.ini --root .
```

**Option B - Run specific tests via pytest:**
```powershell
cd sdk/<service>/<package>
pytest tests/ -v

# Or a specific test file
pytest tests/test_specific_file.py -v

# Or a specific test class
pytest tests/test_specific_file.py::TestClassName -v
```

**Option C - Run tests mentioned in the issue:**
```powershell
cd sdk/<service>/<package>
pytest tests/<path-from-issue> -v -k "<test-name-pattern>"
```

### Step 5: Analyze Failures and Fix or Report

Parse the pytest/tox output to identify:
- Test name and file path
- Failure type (AssertionError, ImportError, etc.)
- Error message and stack trace
- **Cross-reference with the GitHub issue** to understand expected behavior

**ALLOWED ACTIONS:**
 Fix test failures caused by bugs in test setup or configuration
 Update recordings if tests are outdated (playback mode)
 Add missing environment variables or fixtures
 Fix import errors by installing missing packages

**FORBIDDEN ACTIONS:**
 Modify production code to make tests pass artificially
 Delete or skip failing tests without clear justification
 Change test assertions to always pass
 Ignore failures without investigation

### Step 6: Write New Tests (if requested)

Follow the Azure SDK Python testing patterns when writing new tests.

**`conftest.py` with test proxy fixture:**
```python
import pytest
from devtools_testutils import test_proxy


# Fixture that enables test recording and playback via the Azure SDK test proxy
@pytest.fixture(scope="session")
def start_proxy(test_proxy):
    return
```

**Test class inheriting from `AzureRecordedTestCase`:**
```python
import pytest
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.identity import DefaultAzureCredential

# Import the client for the package under test
from azure.<service>.<package> import <ServiceClient>


class TestMyFeature(AzureRecordedTestCase):

    @recorded_by_proxy
    def test_my_feature(self, **kwargs):
        """Test description following Azure SDK style."""
        # Arrange
        client = self.create_mgmt_client(<ServiceClient>)

        # Act
        result = client.some_operation()

        # Assert
        assert result is not None
```

**Using `EnvironmentVariableLoader` for credentials:**
```python
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader, recorded_by_proxy

ServicePreparer = EnvironmentVariableLoader(
    "<service>",
    azure_subscription_id="00000000-0000-0000-0000-000000000000",
    azure_resource_group="test-rg",
    # Add any other service-specific environment variables here
)


class TestMyFeature(AzureRecordedTestCase):

    @ServicePreparer()
    @recorded_by_proxy
    def test_my_feature(self, **kwargs):
        subscription_id = kwargs.pop("azure_subscription_id")
        # Use the injected variables in the test
        assert subscription_id is not None
```

**Recording new tests:**
```powershell
# Run once in live mode to record interactions
$env:AZURE_TEST_RUN_LIVE = "true"
pytest tests/test_my_feature.py -v

# Recordings are saved to tests/recordings/
# Subsequent runs in playback mode use these recordings
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
pytest tests/test_my_feature.py -v
```

### Step 7: Verify Tests Pass (within activated venv)

Run tests in both playback and live modes (if credentials available):

```powershell
cd sdk/<service>/<package>

# Verify in playback mode
pytest tests/ -v

# Verify in live mode (if Azure credentials are available)
$env:AZURE_TEST_RUN_LIVE = "true"
pytest tests/ -v
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
```

### Step 8: Summary

Provide a summary:
- GitHub issue being addressed (if provided)
- Number of tests run, passed, failed, and skipped
- New tests written (if any) and their location
- Any tests requiring manual review or live credentials
- Recordings created or updated

### Step 9: Create Pull Request (if new tests were written)

After writing and verifying new tests, create a pull request:

**Stage and commit the changes:**
```powershell
# Stage test files and recordings
git add tests/
git add sdk/<service>/<package>/tests/

# Create a descriptive commit message
git commit -m "test(<package-name>): add tests for <feature> (#<issue-number>)

- Added tests for <feature description>
- Tests use AzureRecordedTestCase with playback recordings
- All tests pass in playback mode

Closes #<issue-number>"
```

**Create pull request using GitHub CLI or MCP server:**

Option 1 - Using GitHub CLI (if available):
```powershell
# Create a new branch
$branchName = "test/<package-name>-<feature>-<issue-number>"
git checkout -b $branchName

# Push the branch
git push origin $branchName

# Create PR using gh CLI
gh pr create `
  --title "test(<package-name>): Add tests for <feature> (#<issue-number>)" `
  --body "## Description
This PR adds tests for the <package-name> package as described in #<issue-number>.

## Changes
- Added tests for <feature description> following AzureRecordedTestCase pattern
- Included playback recordings for offline test runs
- Tests cover: <list of scenarios tested>
- All tests pass in playback mode

## Testing
- [x] Tests pass in playback mode
- [x] Tests follow AzureRecordedTestCase pattern with @recorded_by_proxy
- [x] Recordings generated for all new tests
- [ ] Tests verified in live mode (requires Azure credentials)

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

## Common Test Failures and How to Fix Them

### Missing Recordings

**Error:** `RecordingFileNotFoundError` or `No recording found`

**Fix:** Run tests in live mode first to generate recordings:
```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
pytest tests/test_failing.py -v
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'azure.<service>.<package>'`

**Fix:** Ensure the package is installed in the venv:
```powershell
cd sdk/<service>/<package>
pip install -e .
pip install -r dev_requirements.txt
```

### Environment Variable Missing

**Error:** `KeyError: 'AZURE_SUBSCRIPTION_ID'` or similar

**Fix:** Set required environment variables or use `EnvironmentVariableLoader` with defaults:
```powershell
$env:AZURE_SUBSCRIPTION_ID = "your-subscription-id"
$env:AZURE_RESOURCE_GROUP = "your-resource-group"
```

### Authentication Errors (Live Mode)

**Error:** `azure.core.exceptions.ClientAuthenticationError`

**Fix:** Ensure Azure credentials are configured:
```powershell
az login
az account set --subscription "your-subscription-id"
```

### Test Proxy Connection Errors

**Error:** `ConnectionError` when using test proxy

**Fix:** Start the test proxy before running tests or use the `start_proxy` conftest fixture:
```powershell
# The conftest.py test_proxy fixture handles this automatically
# Ensure devtools_testutils is installed
pip install azure-devtools
```

### Outdated Recordings

**Error:** `PlaybackResponseError` or unexpected assertion failures in playback

**Fix:** Re-record by running in live mode:
```powershell
$env:AZURE_TEST_RUN_LIVE = "true"
pytest tests/test_outdated.py -v
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
```

## Example Workflow

```powershell
# 0. Get context
# User provides: https://github.com/Azure/azure-sdk-for-python/issues/12345
# Issue mentions: missing tests for a feature in sdk/storage/azure-storage-blob

# 1. CRITICAL - Activate virtual environment FIRST
.\env\Scripts\Activate.ps1  # Use the venv name provided by user
cd sdk/storage/azure-storage-blob
pip install -r dev_requirements.txt
pip install -e .

# 2. Run existing tests to check baseline
pytest tests/ -v --tb=short 2>&1 | Tee-Object test_results.txt

# 3. Check what tests already exist for the feature
Get-ChildItem tests/ -Filter "*blob*"

# 4. Run tests in playback mode (default)
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue
pytest tests/test_blob_client.py -v

# 5. Write new test for the missing scenario
# (Edit tests/test_blob_client.py following AzureRecordedTestCase pattern)

# 6. Record the new test in live mode
$env:AZURE_TEST_RUN_LIVE = "true"
pytest tests/test_blob_client.py::TestBlobClient::test_upload_blob -v
Remove-Item Env:AZURE_TEST_RUN_LIVE -ErrorAction SilentlyContinue

# 7. Verify new test passes in playback mode
pytest tests/test_blob_client.py -v

# 8. Create PR
$branchName = "test/azure-storage-blob-upload-12345"
git checkout -b $branchName
git add tests/
git commit -m "test(azure-storage-blob): add tests for blob upload (#12345)

Closes #12345"
git push origin $branchName
gh pr create `
  --title "test(azure-storage-blob): Add tests for blob upload (#12345)" `
  --body "Fixes #12345" `
  --base main `
  --repo Azure/azure-sdk-for-python
```

## Notes

- Always read existing test files to understand patterns before writing new tests
- Tests use `AzureRecordedTestCase` for integration tests with recorded HTTP interactions
- Playback mode (default) replays recorded HTTP interactions without live Azure services
- Live mode (`AZURE_TEST_RUN_LIVE=true`) makes real calls to Azure services
- Recording files are stored in `tests/recordings/` as JSON files
- Use `@recorded_by_proxy` decorator on every test method that makes HTTP calls
- Use `EnvironmentVariableLoader` to inject credentials from environment into tests
- Prefer playback mode for CI; live mode is used for initial recording and validation
- Some tests may require specific Azure resources — document these requirements clearly
