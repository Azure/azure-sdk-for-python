# Azure Service Bus Client Library Developer Guide

This guide is intended for developers contributing to the Azure Service Bus Python client library. It provides information on setting up your development environment, running tests, and contributing to the codebase.

## Setting Up Development Environment

### Prerequisites

- Python version [supported by the client library](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)
- Git
- pip and setuptools
- Azure subscription to create Service Bus resources

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Azure/azure-sdk-for-python.git
   cd azure-sdk-for-python/sdk/servicebus/azure-servicebus
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

## Running Tests

### Live Tests

Live tests require an Azure Service Bus namespace. The test framework uses `ServiceBusPreparer` to create the necessary resources for AMQP tests.

The tests/mgmt_tests run tests for `azure.servicebus.management` and are HTTP-based. These use the [test proxy](https://github.com/Azure/azure-sdk-for-python/blob/2e7b619b1540319aeaef2c08f3898dcc2e4ddf5c/doc/dev/tests.md#start-the-test-proxy-server).

1. Login to Azure:
   ```bash
   az login
   ```

2. Set required environment variables (or create a `.env` file):
   
   The following need to be set to run live tests locally and authenticate with AzureCliCredential:
   ```
   AZURE_SUBSCRIPTION_ID=<your-subscription-id>
   SERVICEBUS_RESOURCE_GROUP=<your-resource-group>
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
   
   Note: To run mgmt tests in playback mode instead of live mode, set:
   ```
   AZURE_TEST_RUN_LIVE=false
   ```

3. Run tests:
   ```bash
   # Run all live tests
   pytest tests/livetest

   # Run specific live test
   pytest tests/livetest/synctests/test_queue_client.py::test_specific_function
   
   # Show output during test run
   pytest -s tests/livetest/synctests/test_queue_client.py::test_specific_function
   ```

4. Run mgmt tests only:
   ```bash
   # Review the README file for specific test setup and instructions on running tests
   pytest tests/mgmt_tests
   ```

   To pull mgmt test recordings:
   ```bash
   python azure-sdk-for-python/scripts/manage_recordings.py restore -p sdk/servicebus/azure-servicebus/assets.json
   ```
   
   To push after recording mgmt tests in live mode:
   ```bash
   python scripts/manage_recordings.py push -p sdk/servicebus/azure-servicebus/assets.json
   ```

### Common Test Issues

- **Authentication errors**: If you see "The access token is invalid" errors, run `az login` to refresh your authentication.
- **Resource Not Found**: Ensure your environment variables are correctly set and don't include unnecessary parts (e.g., don't include the `.servicebus.windows.net` suffix in namespace names).
- **ImportError**: If you see errors importing library components, try reinstalling with `pip install .` instead of development mode.

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
1. Add a comment to the PR: `/azp run python - servicebus - perf`
2. To run manually with custom parameters:
   - Find the perf pipelines in azure-sdk internal DevOps pipelines
   - Click Run and set the commit to: `refs/pull/<PR #>/merge`

## Additional Resources

- [Service Bus Architecture](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-architecture)
- [Azure SDK Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
- [Service Bus Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/servicebus/azure-servicebus/samples)