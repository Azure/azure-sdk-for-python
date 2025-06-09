# Azure Service Bus Client Library Developer Guide

This guide is intended for developers contributing to the Azure Service Bus Python client library. It provides information on setting up your development environment, running tests, and contributing to the codebase.

## Setting Up Development Environment

### Prerequisites

- Python version supported by the client library
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

Live tests require an Azure Service Bus namespace. The test framework uses `ServiceBusPreparer` to create the necessary resources.

1. Login to Azure:
   ```bash
   az login
   ```

2. Set required environment variables (or create a `.env` file):
   ```
   SERVICEBUS_CONNECTION_STRING=<your-connection-string>
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

### Common Test Issues

- **Missing environment variables**: If you see a warning like:
  ```log
  sdk/servicebus/azure-servicebus/tests/livetest/asynctests/test_auth_async.py::test_client_token_credential_async[pyamqp]
    /.../tests/conftest.py:195: UserWarning: SERVICEBUS_RESOURCE_GROUP undefined - skipping test
      warnings.warn(UserWarning("SERVICEBUS_RESOURCE_GROUP undefined - skipping test"))
  ```
  Create an `.env` file with the named variable or set it in your environment.

- **Authentication errors**: If you see:
  ```log
  ERROR tests/unittest/test_partition_resolver.py::TestPartitionResolver::test_basic_round_robin[1] - azure.core.exceptions.ClientAuthenticationError: (InvalidAuthenticationToken) The access token is invalid.
  ```
  Run `az login` to refresh your authentication.

- **Resource Not Found**: If you see:
  ```log
  ERROR tests/unittest/test_partition_resolver.py::TestPartitionResolver::test_basic_round_robin[1] - azure.core.exceptions.ResourceNotFoundError: (ParentResourceNotFound) Failed to perform 'action' on resource(s) of type 'namespaces/authorizationrules', be...
  ```
  This probably means you included the suffix in SERVICEBUS_NAMESPACE. Only use the name, and strip out the ".servicebus.windows.net".

- **PytestUnknownMarkWarning**: You can ignore warnings like:
  ```log
    PytestUnknownMarkWarning: Unknown pytest.mark.livetest - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
      @pytest.mark.livetest
  ```
  These are not part of pytest, but are part of the azure-sdk-for-python test framework.

- **asyncio_default_fixture_loop_scope warnings**: These warnings from pytest-asyncio can be ignored. For example:
  ```log
  /.../.venv/lib/python3.10/site-packages/pytest_asyncio/plugin.py:217: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
  The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"
    warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
  ```

If you want to see pytest's output, even if the test succeeds, use `pytest -s <test>`

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

2. Review the README file for specific test setup:
   ```bash
   cat README.md
   ```

3. Run performance tests:
   ```bash
   # Run with default options
   python servicebus_perf.py

   # View available options
   python servicebus_perf.py --help
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