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

## Quick Start

### Authentication

The SDK supports multiple authentication methods. For development, we recommend using Azure CLI:

```bash
# Install Azure CLI and login
az login

# Set your endpoint
export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://your-resource-name.services.ai.azure.com/"
```

For production applications, use [DefaultAzureCredential][default_azure_credential] which supports managed identity, service principal, and other authentication methods.

### Document Analysis Example (Use prebuilt document analyzer)

The following async snippet shows how to extract content from a PDF using the out-of-the-box **prebuilt-documentAnalyzer**:

```python
import asyncio
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential
import os

async def main():
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT")
    credential = DefaultAzureCredential()
    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    async with client, credential:
        # Read your document
        with open("sample_invoice.pdf", "rb") as f:
            file_bytes = f.read()

        poller = await client.content_analyzers.begin_analyze_binary(
            analyzer_id="prebuilt-documentAnalyzer",
            input=file_bytes,
            content_type="application/pdf",
        )
        result = await poller.result()

        for content in result.contents:
            print("----- Content Preview -----")
            print(content.markdown[:300] if content.markdown else "(no markdown)")

asyncio.run(main())
```

### Using a Custom Analyzer (Field Extraction)

In many real-world scenarios you will create your own analyzer so you can define exactly which fields to extract.
The snippet below shows how to build a very small analyzer (it extracts only the `total_amount` from an invoice), upload it to your resource, run it, and read the structured result — all with the **object model**.

```python
import asyncio
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    FieldSchema,
    FieldDefinition,
    FieldType,
    GenerationMethod,
)
from azure.identity.aio import DefaultAzureCredential
import os

async def main():
    # 1) Create the client
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT")
    credential = DefaultAzureCredential()
    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    async with client, credential:
        # 2) Define a simple analyzer in-memory
        analyzer_id = "my-invoice-analyzer"  # must be unique within your resource
        my_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-documentAnalyzer",  # start from the general-purpose doc analyzer
            description="Extract total amount from invoices",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=FieldSchema(
                name="invoice_schema",
                description="Fields we care about in an invoice",
                fields={
                    "total_amount": FieldDefinition(
                        type=FieldType.NUMBER,
                        method=GenerationMethod.EXTRACT,
                        description="The grand total on the invoice",
                    )
                },
            ),
        )

        # 3) Upload (create or replace) the analyzer
        await client.content_analyzers.begin_create_or_replace(
            analyzer_id=analyzer_id,
            resource=my_analyzer,
        ).result()
        print(f"✓ Analyzer '{analyzer_id}' is ready")

        # 4) Run the analyzer on a PDF
        with open("sample_invoice.pdf", "rb") as f:
            pdf_bytes = f.read()

        poller = await client.content_analyzers.begin_analyze_binary(
            analyzer_id=analyzer_id,
            input=pdf_bytes,
            content_type="application/pdf",
        )
        analysis_result = await poller.result()
        print("✓ Analysis finished")

        # 5) Inspect the structured result
        content = analysis_result.contents[0]
        total_amount_field = content.fields.get("total_amount") if content.fields else None
        if total_amount_field:
            print(
                f"Total amount ➜ {total_amount_field.value_number} (confidence: {total_amount_field.confidence:.2f})"
            )
        else:
            print("total_amount field was not detected")

asyncio.run(main())
```

## SDK Development and Testing

> **Note**: This section is for SDK developers who want to contribute to or test the SDK itself. If you're using the SDK in your application, refer to the Quick Start section above.

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
