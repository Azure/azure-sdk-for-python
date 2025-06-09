# Azure Event Hubs Client Library Developer Guide

This guide is intended for developers contributing to the Azure Event Hubs Python client library. It provides information on setting up your development environment, running tests, and contributing to the codebase.

## Setting Up Development Environment

### Prerequisites

- Python version [supported by the client library](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)
- Git
- pip and setuptools
- Azure subscription to create Event Hubs resources

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Azure/azure-sdk-for-python.git
   cd azure-sdk-for-python/sdk/eventhub/azure-eventhub
   ```

2. Create a virtual environment:
   ```bash
   # Linux/macOS
   python -m venv .venv && source .venv/bin/activate && pip install -r dev_requirements.txt

   # Windows PowerShell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r dev_requirements.txt
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

   If you encounter import errors when running tests, use the standard installation:
   ```bash
   pip install .
   ```
   Note: You'll need to rerun this command after making changes to the package.

## Running Tests

### Unit Tests

Unit tests don't require any Azure resources:

```bash
# Run all unit tests
pytest tests/unittest

# Run specific unit test
pytest tests/unittest/test_specific_file.py::test_specific_test
```

### Live Tests

Live tests require an Azure Event Hubs namespace. Resources are created dynamically for live tests using fixtures in the `conftest.py` file.

1. Login to Azure:
   ```bash
   az login
   ```

2. Set required environment variables (or create a `.env` file):
   
   The following need to be set to run live tests locally and authenticate with AzureCliCredential:
   ```
   AZURE_SUBSCRIPTION_ID=<your-subscription-id>
   EVENTHUB_RESOURCE_GROUP=<your-resource-group>
   EVENTHUB_NAMESPACE=<your-namespace>  # Only the name, not the full URL
   AZURE_TEST_RUN_LIVE=true
   ```
   
   If using CLI:
   ```
   AZURE_TEST_USE_CLI_AUTH=true
   ```
   
   OR
   
   If using pwsh:
   ```
   AZURE_TEST_USE_PWSH_AUTH=true
   ```

3. Run tests:
   ```bash
   # Run a specific test to check if your environment is set up correctly
   pytest tests/livetest/synctests/test_consumer_client.py::test_receive_partition
   
   # Run all live tests
   pytest tests/livetest
   
   # Run with output visible even if tests pass
   pytest -s tests/livetest/synctests/test_specific_file.py::test_specific_function
   ```

### Common Test Issues

- **Authentication errors**: If you see "The access token is invalid" errors, run `az login` to refresh your authentication.
- **Resource Not Found**: Ensure your environment variables are correctly set. For `EVENTHUB_NAMESPACE`, only use the name part (without the `.servicebus.windows.net` suffix).
- **ImportError**: If you see errors like "cannot import name 'EventHubProducerClient' from 'azure.eventhub'", use `pip install .` instead of `pip install -e .`.
- **PytestUnknownMarkWarning**: You can ignore warnings about "Unknown pytest.mark.livetest" as they're related to the Azure SDK test framework.
- **asyncio_default_fixture_loop_scope warnings**: These warnings from pytest-asyncio can be ignored.

## Stress Testing

Stress tests help verify reliability and performance under load. They are designed to test the library under extreme conditions and for extended periods.

### Structure of Stress Test Files

Stress test files are typically organized in the `stress` directory with the following structure:

```
stress/
├── scenarios/           # Contains stress test scenario definitions
├── scripts/             # Support scripts for stress test deployment
│   └── dev_requirement.txt  # Dependencies for the stress test
└── templates/           # Kubernetes templates for test deployment
    └── testjob.yaml     # Test job configuration
```

### Prerequisites

- Docker Desktop
- Kubernetes CLI (kubectl)
- PowerShell
- Helm

### Running Stress Tests

1. Ensure Docker Desktop is running with Kubernetes enabled.

2. Deploy stress tests from the library folder:
   ```powershell
   ..\..\..\eng\common\scripts\stress-testing\deploy-stress-tests.ps1 -Namespace <your-namespace>
   ```

3. Common kubectl commands:
   ```bash
   # Check on pods
   kubectl get pods -n <your-namespace>
   
   # Delete namespace
   kubectl delete namespace <your-namespace>
   
   # List all active namespaces
   helm list --all-namespaces
   
   # Show logs in console
   kubectl logs -n <your-namespace> <pod-name>
   
   # For init failure
   kubectl logs -n <your-namespace> <pod-name> -c init-azure-deployer
   ```

4. Testing branch changes:
   - To run stress tests against changes in a specific branch, update the `stress/scripts/dev_requirement.txt` file to replace the library with:
   ```
   git+<gh-repo-url>@<branch>#subdirectory=<path/to/sdk>&egg=<package-name>
   ```

5. Monitoring performance:
   - Check the CPU/Memory/errors in the Production Dashboard specified in the Reliability Testing wiki
   - Add `--debug_level Debug` in `stress/templates/testjob.yaml` to output debug logs to the File Share (link available in Reliability Testing wiki)

For complete stress testing requirements and setup, refer to the [Reliability Testing documentation](https://dev.azure.com/azure-sdk/internal/_wiki/wikis/internal.wiki/463/Reliability-Testing).

## Performance Testing

The Performance framework helps measure performance metrics for the client library.

### Running Performance Tests Locally

1. Navigate to the performance test directory:
   ```bash
   cd tests/perfstress
   ```

2. Review the README file for specific test setup and instructions on running tests:
   ```bash
   cat README.md
   ```

### Running Performance Tests in Pipelines

- Performance test resources are deployed dynamically and specified in the service level directory's `perf-resources.bicep` file
- Default parameters are in the service level directory in `perf.yml`, and baseline and source package versions are specified in `perf-tests.yml`

To run performance tests in a pipeline for a PR:
1. Add a comment to the PR: `/azp run python - eventhub - perf`
2. To run manually with custom parameters:
   - Find the perf pipelines in azure-sdk internal DevOps pipelines
   - Click Run and set the commit to: `refs/pull/<PR #>/merge`

## Additional Resources

- [Event Hubs Architecture](https://docs.microsoft.com/azure/event-hubs/event-hubs-about)
- [Azure SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Event Hubs Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventhub/azure-eventhub/samples)