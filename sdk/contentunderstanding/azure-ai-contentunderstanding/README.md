# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a solution that analyzes and comprehends various media content—such as documents, images, audio, and video—transforming it into structured, organized, and searchable data.

This Python SDK provides easy access to the Azure AI Content Understanding service, enabling developers to integrate powerful content analysis capabilities into their applications.

## Additional Resources

- **Service Documentation**: [Azure AI Content Understanding documentation](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/)
- **Python Samples**: [Azure AI Content Understanding Python Samples](https://github.com/Azure-Samples/azure-ai-content-understanding-python)
- **C# Samples**: [Azure AI Content Understanding .NET Samples](https://github.com/Azure-Samples/azure-ai-content-understanding-dotnet/tree/changjian-wang/init-content-understanding-dotnet)

> **⚠️ Note**: The sample repositories above are not yet updated to use this SDK. They demonstrate concepts and API usage patterns but use direct REST API calls. These samples will be updated to use the SDK very soon.

## Getting started

### Install the package

```bash
python -m pip install azure-ai-contentunderstanding
```

#### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Content Understanding instance.

## Development and Testing

### Setting up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Azure/azure-sdk-for-python.git
   cd azure-sdk-for-python/sdk/contentunderstanding/azure-ai-contentunderstanding
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

4. **Install testing dependencies**:
   ```bash
   pip install pytest pytest-asyncio pytest-xdist azure-devtools
   ```

### Running Tests

#### Environment Setup

Before running tests, you need to set up your Azure AI Content Understanding service endpoint and authentication.

**Option 1: Using Azure CLI (Recommended for development)**

1. **Install Azure CLI**: Follow instructions at https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Login to Azure**:
   ```bash
   az login
   ```
3. **Set the endpoint environment variable**:
   ```bash
   export CONTENTUNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
   ```

**Option 2: Using .env file (Recommended)**

1. **Create .env file in the repo root**:
   ```bash
   # Create .env file in the repository root
   cd <repository-root>
   touch .env
   ```

2. **Edit the .env file** with your Azure Content Understanding configuration:
   ```bash
   # Required for Content Understanding SDK and testing
   CONTENTUNDERSTANDING_ENDPOINT=https://your-resource-name.services.ai.azure.com/
   
   # Test Recording Mode - Set to "true" for live testing (record mode)
   AZURE_TEST_RUN_LIVE=true
   AZURE_SKIP_LIVE_RECORDING=true
   
   # Optional: For key-based authentication (alternative to DefaultAzureCredential)
   # Set this to use AzureKeyCredential instead of DefaultAzureCredential
   AZURE_CONTENT_UNDERSTANDING_KEY=your-api-key
   
   # Only required for CI/CD scenarios (for test recording sanitization)
   # Not needed for local development with 'az login'
   # CONTENTUNDERSTANDING_SUBSCRIPTION_ID=your-subscription-id
   # CONTENTUNDERSTANDING_TENANT_ID=your-tenant-id
   # CONTENTUNDERSTANDING_CLIENT_ID=your-client-id
   # CONTENTUNDERSTANDING_CLIENT_SECRET=your-client-secret
   ```

3. **Ensure you're authenticated** via `az login` or other DefaultAzureCredential methods

**Option 3: Using environment variables (For CI/CD)**

For CI/CD scenarios where `az login` is not available:
```bash
export CONTENTUNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret" 
export AZURE_TENANT_ID="your-tenant-id"

# Test recording mode for live testing
export AZURE_TEST_RUN_LIVE="true"
export AZURE_SKIP_LIVE_RECORDING="true"

# Additional variables for test recording sanitization in CI/CD
export CONTENTUNDERSTANDING_SUBSCRIPTION_ID="your-subscription-id"
export CONTENTUNDERSTANDING_TENANT_ID="your-tenant-id"
export CONTENTUNDERSTANDING_CLIENT_ID="your-client-id"
export CONTENTUNDERSTANDING_CLIENT_SECRET="your-client-secret"
```

**Option 4: Using API Key (For testing only - less secure)**

```bash
export CONTENTUNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
export AZURE_CONTENT_UNDERSTANDING_KEY="your-api-key"
```

> **Note**: Key-based authentication is less secure and should only be used for testing and development. For production, use DefaultAzureCredential with `az login` or managed identity.

#### Basic Test Execution

**Run all tests**:
```bash
python -m pytest generated_tests/
```

**Run specific test module**:
```bash
python -m pytest generated_tests/test_content_understanding_person_directories_operations_async.py
```

**Run specific test**:
```bash
python -m pytest generated_tests/test_content_understanding_person_directories_operations_async.py::TestContentUnderstandingPersonDirectoriesOperationsAsync::test_person_directories_get_person
```

#### Parallel Test Execution

For faster test execution, use pytest-xdist to run tests in parallel:

**Auto-detect CPU cores and run in parallel**:
```bash
python -m pytest generated_tests/ -n auto
```

**Specify number of parallel workers**:
```bash
python -m pytest generated_tests/ -n 4
```

**Run with verbose output and parallel execution**:
```bash
python -m pytest generated_tests/ -n auto -v
```

#### Test Options and Filtering

**Run with detailed output**:
```bash
python -m pytest generated_tests/ -v -s
```

**Run only failed tests from last run**:
```bash
python -m pytest generated_tests/ --lf
```

**Run tests matching a pattern**:
```bash
python -m pytest generated_tests/ -k "person_directories"
```

**Skip tests with specific markers**:
```bash
python -m pytest generated_tests/ -m "not skip"
```

**Generate coverage report**:
```bash
python -m pytest generated_tests/ --cov=azure.ai.contentunderstanding --cov-report=html
```

#### Performance and Debugging

**Run with short traceback**:
```bash
python -m pytest generated_tests/ --tb=short
```

**Stop on first failure**:
```bash
python -m pytest generated_tests/ -x
```

**Run with timing information**:
```bash
python -m pytest generated_tests/ --durations=10
```

#### Required Modules for Testing

Make sure you have the following modules installed for comprehensive testing:

```bash
pip install pytest>=7.0.0
pip install pytest-asyncio>=0.21.0
pip install pytest-xdist>=3.0.0      # For parallel execution
pip install pytest-cov>=4.0.0        # For coverage reports
pip install azure-devtools>=1.2.0    # For Azure SDK test utilities
pip install azure-identity>=1.12.0   # For authentication
pip install python-dotenv>=1.0.0     # For .env file support
```



### Test Categories

The test suite includes:

- **Unit Tests**: Test individual operations and models
- **Integration Tests**: Test end-to-end workflows with live Azure services
- **Async Tests**: Test asynchronous client operations
- **Error Handling Tests**: Test error scenarios and edge cases

### Test Results

The test suite includes comprehensive coverage of all Azure AI Content Understanding operations:

- **Person Directory Operations**: Create, list, get, update, delete person directories
- **Person Management**: Add, update, list, get, verify persons within directories  
- **Face Operations**: Add, update, list, get faces associated with persons
- **Content Analysis**: Document, image, audio, and video content analysis
- **Content Classification**: Custom and prebuilt content classifiers

All core functionality is fully tested and operational.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[authenticate_with_token]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-an-authentication-token
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/
