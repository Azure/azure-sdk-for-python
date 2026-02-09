---
name: sdkinternal-py-test-run
description: "Run tests for azure-ai-contentunderstanding package in playback, live, or record mode."
---

## Purpose

This skill runs tests for the Azure AI Content Understanding SDK (`azure-ai-contentunderstanding`) in different modes: playback, live, or record. It handles virtual environment setup, dependency installation, environment configuration, and test execution.

## When to Use

Use this skill when:

- You want to run tests in playback mode (using recorded responses)
- You need to run tests against live Azure services
- You want to record new test responses for later playback
- You need to verify tests pass before pushing changes

## Test Modes

| Mode | Description | Environment Variables |
|------|-------------|----------------------|
| **Playback** (default) | Tests run against recorded HTTP responses. No live service calls are made. | `AZURE_TEST_RUN_LIVE=false` |
| **Live** | Tests make actual API calls to Azure services. Requires valid credentials. | `AZURE_TEST_RUN_LIVE=true` |
| **Record** | Tests make live API calls and record the responses for future playback. | `AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true` |

## Prerequisites

Before running tests, ensure:

1. **Python 3.9+** is installed
2. **For live/record modes:** Valid Azure credentials configured
   - Either `CONTENTUNDERSTANDING_KEY` set in `.env`
   - Or authenticated via `az login` for `DefaultAzureCredential`
3. **For live/record modes:** Model deployments configured (see main README)

## Instructions

### Quick Start (Using the Script)

```bash
# From the script directory:
# sdk/contentunderstanding/azure-ai-contentunderstanding/.github/skills/sdkinternal-py-test-run/scripts/

# Run tests in playback mode (default)
./run_tests.sh

# Run tests in live mode
./run_tests.sh --live

# Run tests in record mode
./run_tests.sh --record

# Dry run to see what would be executed
./run_tests.sh --live --dry-run
```

### Manual Execution

```bash
# Navigate to package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Activate virtual environment
source .venv/bin/activate

# Run tests in playback mode (default)
AZURE_TEST_RUN_LIVE=false pytest

# Run tests in live mode
AZURE_TEST_RUN_LIVE=true pytest

# Run tests in record mode
AZURE_TEST_RUN_LIVE=true AZURE_TEST_RECORD_MODE=true pytest
```

## Using the Script

### Script Location

```bash
sdk/contentunderstanding/azure-ai-contentunderstanding/.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh
```

### Script Usage

```bash
./run_tests.sh [OPTIONS] [-- PYTEST_ARGS...]

Options:
  --playback    Run tests in playback mode (default)
  --live        Run tests in live mode against Azure services
  --record      Run tests in record mode (live + record HTTP responses)
  --parallel    Run tests in parallel (pytest -n auto)
  --dry-run     Show what would be executed without running
  --log <file>  Save output to a custom log file
  --help, -h    Show help message

Examples:
  ./run_tests.sh                        # Run in playback mode
  ./run_tests.sh --live                 # Run in live mode
  ./run_tests.sh --record               # Run in record mode
  ./run_tests.sh --live --parallel      # Run live tests in parallel
  ./run_tests.sh -- -k test_analyzer    # Run specific tests matching pattern
  ./run_tests.sh --live -- tests/test_content_understanding.py  # Run specific test file
```

### Script Features

- **Virtual environment setup**: Automatically creates and activates `.venv` if not present
- **Dependency installation**: Installs `dev_requirements.txt` if dependencies are missing
- **Environment configuration**: Copies `env.sample` to `.env` if not present
- **Mode selection**: Choose between playback, live, or record modes
- **Parallel execution**: Option to run tests in parallel with `pytest-xdist`
- **Logging**: Saves output to timestamped log files
- **Dry run**: See what would be executed without running
- **Pytest pass-through**: Pass additional arguments to pytest after `--`

## Test-Proxy Configuration

The test framework uses the **test-proxy** for recording and playing back HTTP requests during tests. The test proxy starts automatically when you run `pytest` — no configuration is needed.

## Example Workflows

### Workflow 1: Verify Tests Pass Before PR

```bash
# From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/

# Run playback tests to ensure they pass
.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh --playback

# If all tests pass, you're ready to submit your PR
```

### Workflow 2: Add New Tests and Record

```bash
# From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/

# 1. Write your new tests in tests/ directory

# 2. Run tests in record mode to capture HTTP responses
.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh --record

# 3. Push recordings (use sdkinternal-py-test-push skill)
.github/skills/sdkinternal-py-test-push/scripts/push_recordings.sh

# 4. Verify playback works
.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh --playback

# 5. Commit assets.json and your test changes
git add tests/ assets.json
git commit -m "Add new tests"
```

### Workflow 3: Debug Failing Live Tests

```bash
# From package directory: sdk/contentunderstanding/azure-ai-contentunderstanding/

# Run specific failing test in live mode with verbose output
.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh --live -- -v -k test_failing_test

# Or run a single test file
.github/skills/sdkinternal-py-test-run/scripts/run_tests.sh --live -- tests/test_specific.py::TestClass::test_method
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'devtools_testutils'"**

- The script automatically handles this by installing dependencies
- To fix manually:
  ```bash
  source .venv/bin/activate
  pip install -r dev_requirements.txt
  ```

**Connection Refused Errors (test-proxy)**

If you see errors like `ConnectionRefusedError: [Errno 111] Connection refused`:
- Try re-running `pytest` — the proxy should start automatically
- Check if the test-proxy is running: `curl http://localhost:5000/Admin/IsAlive`

**Tests fail in live mode with authentication errors**

- Check `CONTENTUNDERSTANDING_ENDPOINT` is correct in `.env`
- If using API key, verify `CONTENTUNDERSTANDING_KEY` is set
- If using `DefaultAzureCredential`, run `az login` first
- Ensure you have the **Cognitive Services User** role on your Foundry resource

**Tests pass locally but fail in CI**

- Ensure `assets.json` is committed with the latest recording tag
- Push recordings using `sdkinternal-py-test-push` skill
- Run playback tests locally to verify before pushing

**"Model deployment not found" errors**

- Ensure you have deployed the required models (gpt-4.1, gpt-4.1-mini, text-embedding-3-large)
- Verify model defaults are configured (see main README Step 3)

## Related Skills

- `sdkinternal-py-test-push` - Push test recordings to the azure-sdk-assets repository
- `sdkinternal-py-setup` - Set up virtual environment for development

## Documentation

- [Tests README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/tests/README.md) - Detailed testing guide
- [Main README - Configure Model Deployments](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md#step-3-configure-model-deployments-required-for-prebuilt-analyzers) - Environment setup
- [Azure SDK Python Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md) - Comprehensive testing documentation
- [Test-Proxy Documentation](https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy) - Official test-proxy documentation
