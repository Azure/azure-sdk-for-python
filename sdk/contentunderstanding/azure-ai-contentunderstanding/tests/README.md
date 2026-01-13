# Azure AI Content Understanding client library for Python - Testing Guide

This guide provides instructions for running tests for the Azure AI Content Understanding SDK.

## Getting started

To run the tests for this package, please follow the setup instructions in the main package README:

[Step 3: Configure model deployments][main_readme_setup]

This step ensures your environment is correctly configured with the necessary dependencies, environment variables, and model mappings required for the tests.

## Running Tests

### Basic Test Execution

Run all tests:
```bash
# Navigate to package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding
pytest
```

Run specific test file:
```bash
pytest tests/test_content_understanding_content_analyzers_operations.py
```

Run specific test:
```bash
pytest tests/test_content_understanding_content_analyzers_operations.py::TestContentUnderstandingContentAnalyzersOperations::test_content_analyzers_get
```

### Parallel Test Execution

To run tests in parallel using `pytest-xdist`:
```bash
pytest -n auto
```

**Important:** Parallel execution requires manual test-proxy management. See [Test-Proxy Configuration](#test-proxy-configuration) below.

## Test-Proxy Configuration

The test framework uses the **test-proxy** for recording and playing back HTTP requests during tests.

### Automatic Startup (Default)

By default, the test-proxy starts automatically when you run `pytest`. **No configuration is needed.**

**⚠️ IMPORTANT:** Do NOT set `PROXY_MANUAL_START=false` in your `.env` file. 

**Why?** Environment variables are read as strings. Setting `PROXY_MANUAL_START=false` makes it the string `"false"`, which is truthy in Python. This causes the framework to think the proxy is manually started, preventing automatic startup.

**Correct approach:**
- **Remove** `PROXY_MANUAL_START` from `.env` entirely (or don't set it)
- The framework will use the default `False` (boolean), enabling automatic startup

**Incorrect approach:**
```bash
# ❌ DON'T DO THIS - This will break automatic startup!
PROXY_MANUAL_START=false
```

**Correct approach:**
```bash
# ✅ DO THIS - Remove the line entirely or don't set it
# (No PROXY_MANUAL_START line in .env)
```

### Manual Startup (For Parallel Execution)

If you need to run tests in parallel (`pytest -n auto`), you must manually start the test-proxy:

1. **Start the test-proxy manually:**
   ```bash
   ./start_test_proxy_for_parallel.sh
   ```

2. **Set environment variable:**
   ```bash
   export PROXY_MANUAL_START=true
   ```
   
   Or add to `.env` file:
   ```bash
   PROXY_MANUAL_START=true
   ```

3. **Run tests in parallel:**
   ```bash
   pytest -n auto
   ```

4. **Stop the test-proxy when done:**
   ```bash
   ./stop_test_proxy.sh
   ```

**Note:** The string `"true"` is truthy in Python, so setting `PROXY_MANUAL_START=true` correctly tells the framework that the proxy is manually managed.

## Key concepts

### Test Modes

#### Playback Mode (Default)
Tests run against recorded HTTP responses. No live service calls are made.

#### Live Mode
Tests make actual API calls to Azure services. Requires valid credentials.

Set environment variable:
```bash
export AZURE_TEST_RUN_LIVE=true
```

#### Record Mode
Tests make live API calls and record the responses for future playback.

Set environment variable:
```bash
export AZURE_TEST_RUN_LIVE=true
export AZURE_TEST_RECORD_MODE=true
```

### Test Proxy
The test framework uses the **test-proxy** for recording and playing back HTTP requests during tests. This allows tests to run consistently without requiring live Azure resources in most scenarios.

## Troubleshooting

### Connection Refused Errors

If you see errors like:
```
ConnectionRefusedError: [Errno 111] Connection refused
MaxRetryError: HTTPConnectionPool(host='localhost', port=5000)
```

**Check:**
1. Is `PROXY_MANUAL_START` set incorrectly in `.env`?
   - Remove it entirely for automatic startup
   - Or set it to `true` if manually managing the proxy
2. Is the test-proxy running?
   ```bash
   curl http://localhost:5000/Admin/IsAlive
   ```
3. For automatic startup, ensure `PROXY_MANUAL_START` is not in `.env` (or is unset)

### Test-Proxy Not Starting Automatically

**Symptoms:** Tests fail with connection errors, proxy doesn't start.

**Solution:**
1. Check `.env` file at repository root
2. Remove any `PROXY_MANUAL_START=false` line
3. The framework will use the default `False` (boolean) for automatic startup

## Examples

### Running a Single Test
```bash
pytest tests/test_content_understanding_content_analyzers_operations.py::TestContentUnderstandingContentAnalyzersOperations::test_content_analyzers_get
```

### Running Tests in Live Mode
```bash
export AZURE_TEST_RUN_LIVE=true
pytest tests/
```

## Additional Resources

- [main README][main_readme] - Package documentation
- [Azure SDK Python Testing Guide][azure_sdk_testing_guide] - Comprehensive testing documentation
- [Test-Proxy Documentation][test_proxy_docs] - Official test-proxy documentation

<!-- LINKS -->

[main_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md
[main_readme_setup]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md#step-3-configure-model-deployments-required-for-prebuilt-analyzers
[azure_sdk_testing_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
[test_proxy_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy
