# Sample Validation in CI Pipelines

This document explains how code samples are validated in the Azure SDK for Python CI pipelines.

## Overview

The Azure SDK for Python repository includes extensive sample validation as part of its continuous integration (CI) pipeline. Sample validation ensures that the code examples provided to users actually work correctly and serve as reliable documentation.

## Sample Validation Architecture

### 1. Tox Environment Configuration

Sample validation is implemented through a dedicated tox environment called `samples`, defined in [`eng/tox/tox.ini`](eng/tox/tox.ini):

```ini
[testenv:samples]
description="Runs a package's samples"
skipsdist = false
skip_install = false
usedevelop = false
changedir = {envtmpdir}
setenv =
  {[testenv]setenv}
  PROXY_URL=http://localhost:5016
deps =
  {[base]deps}
  subprocess32; python_version < '3.5'
commands =
    {[tox]pip_command} freeze
    python {repository_root}/scripts/devops_tasks/test_run_samples.py -t {tox_root}
```

### 2. Sample Validation Script

The core sample validation logic is implemented in [`scripts/devops_tasks/test_run_samples.py`](scripts/devops_tasks/test_run_samples.py). This script:

- **Discovers samples**: Walks through the `samples/` directory of each package
- **Executes samples**: Runs each `.py` file as a standalone Python script
- **Handles timeouts**: Manages samples that may run indefinitely or need extended execution time
- **Manages dependencies**: Installs additional requirements from `sample_dev_requirements.txt` if present
- **Filters samples**: Skips samples that are configured to be ignored in CI

#### Key Features:

**Timeout Management**: Some samples may run indefinitely or require specific time limits:

```python
TIMEOUT_SAMPLES = {
    "azure-eventhub": {
        "receive_batch_with_checkpoint.py": (10),
        "recv.py": (10),
        # ... more samples with timeouts
    }
}
```

**Sample Filtering**: Samples that cannot or should not run in CI can be ignored:

```python
IGNORED_SAMPLES = {
    "azure-appconfiguration-provider": [
        "key_vault_reference_customized_clients_sample.py",
        "aad_sample.py",
        # ... more ignored samples
    ]
}
```

**Dependency Management**: Samples can have additional dependencies specified in `samples/sample_dev_requirements.txt`.

### 3. CI Pipeline Integration

Sample validation is integrated into the CI pipeline through the [`eng/pipelines/templates/steps/build-test.yml`](eng/pipelines/templates/steps/build-test.yml) template.

#### Conditional Execution

Samples are only executed when the `TestSamples` variable is set to `"true"`:

```yaml
- pwsh: |
    python scripts/devops_tasks/dispatch_tox.py "$(TargetingString)" `
      --service="${{ parameters.ServiceDirectory }}" `
      --toxenv="samples"
  displayName: 'Test Samples'
  condition: and(succeeded(), eq(variables['TestSamples'], 'true'))
```

#### Default Configuration

By default, `TestSamples` is set to `"false"` in the platform matrix configuration ([`eng/pipelines/templates/stages/platform-matrix.json`](eng/pipelines/templates/stages/platform-matrix.json)):

```json
{
  "matrix": {
    "Agent": {
      "ubuntu-24.04": { "OSVmImage": "env:LINUXVMIMAGE", "Pool": "env:LINUXPOOL" },
      "windows-2022": { "OSVmImage": "env:WINDOWSVMIMAGE", "Pool": "env:WINDOWSPOOL" }
    },
    "PythonVersion": [ "3.10", "3.12" ],
    "CoverageArg": "--disablecov",
    "TestSamples": "false"
  }
}
```

## Enabling Sample Validation for a Service

### Service-Level Configuration

Individual services can enable sample validation by creating a `tests.yml` file in their service directory that overrides the `TestSamples` variable:

```yaml
# Example: sdk/textanalytics/tests.yml
trigger: none

extends:
    template: /eng/pipelines/templates/stages/archetype-sdk-tests.yml
    parameters:
      BuildTargetingString: azure-ai-textanalytics
      ServiceDirectory: textanalytics
      CloudConfig:
        Public:
          Location: eastus
          SubscriptionConfigurations:
            - $(sub-config-text-analytics-azure-cloud-test-resources)
          MatrixReplace:
            - TestSamples=.*/true  # This enables sample testing
      EnvVars:
        TEST_MODE: 'RunLiveNoRecord'
        AZURE_SKIP_LIVE_RECORDING: 'True'
        AZURE_TEST_RUN_LIVE: 'true'
```

### Authentication and Environment

Sample validation supports both regular authentication and federated authentication for Azure services:

```yaml
# Federated authentication (preferred)
- task: AzurePowerShell@5
  displayName: Test Samples (AzurePowerShell@5)
  condition: and(succeeded(), eq(variables['TestSamples'], 'true'))
  env:
    # Enable samples tests that use DefaultAzureCredential
    AZURE_POD_IDENTITY_AUTHORITY_HOST: 'https://FakeAuthorityHost'
  inputs:
    azureSubscription: azure-sdk-tests-public
    azurePowerShellVersion: LatestVersion
```

## Sample Organization and Requirements

### Directory Structure

Samples should be organized in a `samples/` directory within each package:

```
sdk/textanalytics/azure-ai-textanalytics/
├── azure/
├── samples/                    # Samples directory
│   ├── sample_analyze_sentiment.py
│   ├── sample_extract_key_phrases.py
│   ├── sample_dev_requirements.txt  # Optional additional dependencies
│   └── async_samples/
│       ├── sample_analyze_sentiment_async.py
│       └── ...
├── tests/
└── setup.py
```

### Sample Development Guidelines

1. **Self-contained**: Each sample should be a standalone Python script that can be executed independently
2. **Robust error handling**: Samples should handle authentication failures gracefully
3. **Resource cleanup**: Samples should clean up any resources they create
4. **Timeout consideration**: Long-running samples should be added to the `TIMEOUT_SAMPLES` configuration
5. **Dependencies**: Additional dependencies should be specified in `samples/sample_dev_requirements.txt`

### Sample Types and Considerations

**Synchronous vs Asynchronous**: 
- Async samples (ending in `_async.py`) are skipped on Python < 3.5
- Both sync and async samples are validated when Python version supports them

**Authentication Requirements**:
- Samples requiring live Azure resources should work with `DefaultAzureCredential`
- Samples that cannot run without specific configurations should be added to `IGNORED_SAMPLES`

**Network and External Dependencies**:
- Samples requiring external services should handle connection failures gracefully
- Network-dependent samples may need timeout configurations

## Troubleshooting Sample Validation

### Common Issues

1. **Authentication Failures**: Ensure samples handle missing credentials gracefully
2. **Timeout Issues**: Add problematic samples to `TIMEOUT_SAMPLES` with appropriate timeouts
3. **Missing Dependencies**: Add required packages to `samples/sample_dev_requirements.txt`
4. **Environment-Specific Issues**: Add samples that can't run in CI to `IGNORED_SAMPLES`

### Debugging Sample Failures

1. Check the CI logs for specific sample failure messages
2. Run samples locally using the same tox environment: `tox -e samples`
3. Verify sample dependencies and authentication requirements
4. Test sample timeout behavior locally

### Sample Configuration Options

**Timeout Configuration**:
```python
TIMEOUT_SAMPLES = {
    "your-package-name": {
        "long_running_sample.py": (30),  # 30 second timeout
        "streaming_sample.py": (10, True),  # 10 seconds, pass if timeout
    }
}
```

**Ignore Configuration**:
```python
IGNORED_SAMPLES = {
    "your-package-name": [
        "sample_requiring_manual_setup.py",
        "sample_with_external_dependencies.py"
    ]
}
```

## Integration with Live Testing

Sample validation typically runs as part of live testing pipelines where:

- Real Azure resources are available for testing
- Authentication is configured through service connections
- Samples can interact with actual Azure services
- Results validate that samples work in real-world scenarios

This ensures that the samples provided to users are not only syntactically correct but also functionally accurate and up-to-date with the current state of Azure services.

## Best Practices

1. **Enable sample validation** for all packages that include samples
2. **Keep samples simple** and focused on demonstrating specific functionality
3. **Handle authentication gracefully** using DefaultAzureCredential patterns
4. **Add appropriate timeouts** for samples that may run longer than expected
5. **Test samples locally** before committing to ensure they work in CI
6. **Document any special requirements** for samples that need specific configurations
7. **Use async patterns appropriately** and provide both sync and async examples where relevant

This comprehensive sample validation ensures that Azure SDK users receive accurate, working code examples that serve as effective documentation and starting points for their own implementations.