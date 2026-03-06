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
The test framework uses the **test-proxy** for recording and playing back HTTP requests during tests. This allows tests to run consistently without requiring live Azure resources in most scenarios. The test proxy starts automatically when you run `pytest` — no configuration is needed.

## Troubleshooting

### Connection Refused Errors

If you see errors like:
```
ConnectionRefusedError: [Errno 111] Connection refused
MaxRetryError: HTTPConnectionPool(host='localhost', port=5000)
```

**Check:**
1. Is the test-proxy running?
   ```bash
   curl http://localhost:5000/Admin/IsAlive
   ```
2. Try re-running `pytest` — the proxy should start automatically

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

## Next steps

* Review the [main package README][main_readme] for package documentation and usage examples
* Explore the [samples directory][python_cu_samples] to see working code examples
* Read the [Azure SDK Python Testing Guide][azure_sdk_testing_guide] for comprehensive testing documentation
* Check the [Test-Proxy Documentation][test_proxy_docs] for detailed test-proxy information

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][code_of_conduct_faq] or contact [opencode@microsoft.com][opencode_email] with any additional questions or comments.

<!-- LINKS -->

[main_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md
[main_readme_setup]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md#step-3-configure-model-deployments-required-for-prebuilt-analyzers
[azure_sdk_testing_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
[test_proxy_docs]: https://github.com/Azure/azure-sdk-tools/tree/main/tools/test-proxy
[python_cu_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[opencode_email]: mailto:opencode@microsoft.com
