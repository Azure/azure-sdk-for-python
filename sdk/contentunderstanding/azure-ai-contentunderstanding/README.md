# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a multimodal AI service that extracts semantic content from documents, audio, and video files. It transforms unstructured content into structured, machine-readable data optimized for retrieval-augmented generation (RAG) and automated workflows.

Use the client library for Azure AI Content Understanding to:

* **Extract document content** - Extract text, tables, figures, layout information, and structured markdown from documents (PDF, images, Office documents)
* **Transcribe and analyze audio** - Convert audio content into searchable transcripts with speaker diarization and timing information
* **Analyze video content** - Extract visual frames, transcribe audio tracks, and generate structured summaries from video files
* **Create custom analyzers** - Build domain-specific analyzers for specialized content extraction needs
* **Classify documents** - Automatically categorize and organize documents by type or content

[Source code][python_cu_src] | [Package (PyPI)][python_cu_pypi] | [Product documentation][python_cu_product_docs] | [Samples][python_cu_samples]

## Getting started

### Install the package

Install the client library for Python with [pip][pip]:

```bash
python -m pip install azure-ai-contentunderstanding
```

This table shows the relationship between SDK versions and supported API service versions:

| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0b1     | 2025-11-01                    |

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- Once you have your Azure subscription, create a [Microsoft Foundry resource][cu_quickstart] in the Azure portal. Be sure to create it in a [supported region][cu_region_support].
- **If running async APIs:** The async transport is designed to be opt-in. The [aiohttp](https://pypi.org/project/aiohttp/) framework is one of the supported implementations of async transport. It's not installed by default. You need to install it separately as follows: `pip install aiohttp`

### Configure your Microsoft Foundry resource and required model deployments

Before running most samples (especially those that use prebuilt analyzers) you need to:

1. Create (or reuse) an Microsoft Foundry resource
2. Assign the correct role so you can configure default model deployments
3. Deploy the required foundation models (GPT and Embeddings) in that resource
4. Map those deployments to standard model names using the SDK's `update_defaults` API (one-time per resource)
5. Provide environment variables (via a `.env` file at the repository root for tests, or your shell/session for ad‑hoc runs)

#### Step 1: Create the Microsoft Foundry resource

> **Important:** You must create your Microsoft Foundry resource in a region that supports Content Understanding. For a list of available regions, see [Azure Content Understanding region and language support][cu_region_support].

1. Follow the steps in the [Azure Content Understanding quickstart][cu_quickstart] to create a Microsoft Foundry resource in the Azure portal
2. Get your Foundry resource's endpoint URL from Azure Portal:
   - Go to [Azure Portal][azure_portal]
   - Navigate to your Microsoft Foundry resource
   - Go to **Resource Management** > **Keys and Endpoint**
   - Copy the **Endpoint** URL (typically `https://<your-resource-name>.services.ai.azure.com/`)

The Content Understanding service is hosted within this resource. After creation, locate the endpoint under: Resource Management > Keys and Endpoint. It typically looks like:

```
https://<your-resource-name>.services.ai.azure.com/
```

Set this as `AZURE_CONTENT_UNDERSTANDING_ENDPOINT`.

**Important: Grant Required Permissions**

After creating your Microsoft Foundry resource, you must grant yourself the **Cognitive Services User** role to enable API calls for setting default GPT deployments:

1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Access Control (IAM)** in the left menu
4. Click **Add** > **Add role assignment**
5. Select the **Cognitive Services User** role
6. Assign it to yourself (or the user/service principal that will run the application)

> **Note:** This role assignment is required even if you are the owner of the resource. Without this role, you will not be able to call the Content Understanding API to configure model deployments for prebuilt analyzers.

#### Step 2: Deploy required models

**Important:** The prebuilt analyzers require model deployments. You must deploy these models before using prebuilt analyzers:
- `prebuilt-documentSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch` require **GPT-4.1-mini** and **text-embedding-3-large**
- Other prebuilt analyzers like `prebuilt-invoice`, `prebuilt-receipt` require **GPT-4.1** and **text-embedding-3-large**

1. **Deploy GPT-4.1:**
   - In Microsoft Foundry, go to **Deployments** > **Deploy model** > **Deploy base model**
   - Search for and select **gpt-4.1**
   - Complete the deployment with your preferred settings
   - Note the deployment name (by convention, use `gpt-4.1`)

2. **Deploy GPT-4.1-mini:**
   - In Microsoft Foundry, go to **Deployments** > **Deploy model** > **Deploy base model**
   - Search for and select **gpt-4.1-mini**
   - Complete the deployment with your preferred settings
   - Note the deployment name (by convention, use `gpt-4.1-mini`)

3. **Deploy text-embedding-3-large:**
   - In Microsoft Foundry, go to **Deployments** > **Deploy model** > **Deploy base model**
   - Search for and select **text-embedding-3-large**
   - Complete the deployment with your preferred settings
   - Note the deployment name (by convention, use `text-embedding-3-large`)

For more information on deploying models, see [Create model deployments in Microsoft Foundry portal][deploy_models_docs].

In Microsoft Foundry: Deployments > Deploy model > Deploy base model. Deploy each of:

- GPT-4.1 (suggested deployment name: `gpt-4.1`)
- GPT-4.1-mini (suggested deployment name: `gpt-4.1-mini`)
- text-embedding-3-large (suggested deployment name: `text-embedding-3-large`)

If you choose different deployment names, record them—you will use them in environment variables and when calling `update_defaults`.

#### Step 3: Configure model deployments (Required for Prebuilt Analyzers)

> **IMPORTANT:** Before using prebuilt analyzers, you must configure the model deployments. This is a **one-time setup per Microsoft Foundry resource** that maps your deployed models to the prebuilt analyzers.

You need to configure the default model mappings in your Microsoft Foundry resource. This can be done programmatically using the SDK or through the Azure Portal. The configuration maps your deployed models (GPT-4.1, GPT-4.1-mini, and text-embedding-3-large) to the prebuilt analyzers that require them.

> **Note:** The configuration is persisted in your Microsoft Foundry resource, so you only need to run this once per resource (or whenever you change your deployment names). If you have multiple Microsoft Foundry resources, you need to configure each one separately.

#### 4. Configure environment variables

For local development and tests this repository uses a root-level `.env` file. A template is provided in the package directory as `env.sample`.

Copy it to the repository root:

```bash
cp sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample .env
```

Then edit `.env` and set at minimum:

```
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
# Optionally provide a key; if omitted DefaultAzureCredential is used.
AZURE_CONTENT_UNDERSTANDING_KEY=<optional-api-key>
GPT_4_1_DEPLOYMENT=gpt-4.1
GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

Notes:
- If `AZURE_CONTENT_UNDERSTANDING_KEY` is not set the SDK will fall back to `DefaultAzureCredential`. Ensure you have authenticated (e.g. `az login`).
- Keep the `.env` file out of version control—do not commit secrets.
- The model deployment variables are required for configuring defaults and for samples that use prebuilt analyzers.

Content Understanding expects a mapping from standard model names to your deployment names. Run the sample `update_defaults.py` (located in the samples directory) after the environment variables are set and roles assigned.

**Example using async client:**

```python
import os, asyncio
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

async def configure():
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await client.update_defaults(
            model_deployments={
                "gpt-4.1": os.environ["GPT_4_1_DEPLOYMENT"],
                "gpt-4.1-mini": os.environ["GPT_4_1_MINI_DEPLOYMENT"],
                "text-embedding-3-large": os.environ["TEXT_EMBEDDING_3_LARGE_DEPLOYMENT"],
            }
        )
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()

asyncio.run(configure())
```

**Example using sync client:**

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

def configure():
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()
    
    with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        client.update_defaults(
            model_deployments={
                "gpt-4.1": os.environ["GPT_4_1_DEPLOYMENT"],
                "gpt-4.1-mini": os.environ["GPT_4_1_MINI_DEPLOYMENT"],
                "text-embedding-3-large": os.environ["TEXT_EMBEDDING_3_LARGE_DEPLOYMENT"],
            }
        )

configure()
```

After a successful run you can immediately use prebuilt analyzers such as `prebuilt-invoice` or `prebuilt-documentSearch`. If you encounter errors:

- Recheck deployment names (they must match exactly)
- Confirm the **Cognitive Services User** role assignment
- Verify the endpoint points to the correct resource

### Authenticate the client

To authenticate the client, you need your Microsoft Foundry resource endpoint and credentials. You can use either an API key or Azure Active Directory (Azure AD) authentication.

#### Using DefaultAzureCredential

The simplest way to authenticate is using `DefaultAzureCredential`, which supports multiple authentication methods and works well in both local development and production environments:

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()
client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
```

For async operations:

```python
import os
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()
client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
```

#### Using API Key

You can also authenticate using an API key from your Microsoft Foundry resource:

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
api_key = os.environ["AZURE_CONTENT_UNDERSTANDING_KEY"]
client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
```

To get your API key:
1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Resource Management** > **Keys and Endpoint**
4. Copy one of the **Keys** (Key1 or Key2)

For more information on authentication, see [Azure Identity client library][azure_identity_readme].

## Key concepts

### Prebuilt Analyzers

Content Understanding provides prebuilt analyzers that are ready to use without any configuration. These analyzers use the `*Search` naming pattern:

* **`prebuilt-documentSearch`** - Extracts content from documents (PDF, images, Office documents) with layout preservation, table detection, figure analysis, and structured markdown output. Optimized for RAG scenarios.
* **`prebuilt-audioSearch`** - Transcribes audio content with speaker diarization, timing information, and conversation summaries. Supports multilingual transcription.
* **`prebuilt-videoSearch`** - Analyzes video content with visual frame extraction, audio transcription, and structured summaries. Provides temporal alignment of visual and audio content.

> **Note:** The prebuilt analyzers use the `prebuilt-{type}Search` naming pattern (not `prebuilt-{type}Analyzer`). This is a recent change in the Content Understanding service.

For a full list of prebuilt analyzers, see [Azure AI Content Understanding prebuilt analyzers][cu_prebuilt_analyzers].

### Custom Analyzers

You can create custom analyzers with specific field schemas for multi-modal content processing (documents, images, audio, video). Custom analyzers allow you to extract domain-specific information tailored to your use case.

### Content Types

The API returns different content types based on the input:

* **`document`** - For document files (PDF, images, Office documents). Contains pages, tables, figures, paragraphs, and markdown representation.
* **`audioVisual`** - For audio and video files. Contains transcript phrases, timing information, and for video, visual frame references.

### Asynchronous Operations

Content Understanding operations are asynchronous long-running operations. The workflow is:

1. **Begin Analysis** - Start the analysis operation (returns immediately with an operation location)
2. **Poll for Results** - Poll the operation location until the analysis completes
3. **Process Results** - Extract and display the structured results

The SDK provides `LROPoller` types that handle polling automatically when using `.result()`. For analysis operations, the SDK returns a poller that provides access to the operation ID via the `operation_id` property. This operation ID can be used with `get_result_file*` and `delete_result*` methods.

### Main Classes

* **`ContentUnderstandingClient`** - The main client for analyzing content, as well as creating, managing, and configuring analyzers
* **`AnalyzeResult`** - Contains the structured results of an analysis operation, including content elements, markdown, and metadata
* **`LROPoller`** - A long-running operation wrapper for analysis results that provides access to the operation ID

### Thread safety

We guarantee that all client instance methods are thread-safe and independent of each other. This ensures that the recommendation of reusing client instances is always safe, even across threads.

### Additional concepts

[Client options][client_options] |
[Accessing the response][accessing_response] |
[Long-running operations][long_running_operations] |
[Handling failures][handling_failures] |
[Diagnostics][diagnostics] |
[Mocking][mocking] |
[Client lifetime][client_lifetime]

## Examples

You can familiarize yourself with different APIs using [Samples][python_cu_samples].

The samples demonstrate:

* **Document Analysis** - Extract content from PDFs and images using `prebuilt-documentSearch`
* **Audio Analysis** - Transcribe and analyze audio files using `prebuilt-audioSearch`
* **Video Analysis** - Analyze video content using `prebuilt-videoSearch`
* **Custom Analyzers** - Create domain-specific analyzers for specialized extraction needs
* **Document Classification** - Classify documents by type or content

See the [samples directory][python_cu_samples] for complete examples.

### Extract Markdown Content from Documents

Use the `prebuilt-documentSearch` to extract markdown content from documents:

```python
import asyncio
import os
from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeResult, MediaContent, DocumentContent, MediaContentKind
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

async def analyze_document():
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
        
        # Analyze document using prebuilt-documentSearch
        poller = await client.content_analyzers.begin_analyze(
            analyzer_id="prebuilt-documentSearch", 
            url=file_url
        )
        result: AnalyzeResult = await poller.result()
        
        # Extract markdown content
        content: MediaContent = result.contents[0]
        print("📄 Markdown Content:")
        print(content.markdown)
        
        # Access document-specific properties
        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore
            print(f"📚 Pages: {document_content.start_page_number} - {document_content.end_page_number}")

    if isinstance(credential, DefaultAzureCredential):
        await credential.close()

# Run the analysis
asyncio.run(analyze_document())
```

### Extract Structured Fields from Invoices

Use the `prebuilt-invoice` analyzer to extract structured invoice fields:

```python
import asyncio
import os
from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalyzeResult, MediaContent
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

def get_field_value(fields, field_name):
    """Helper function to safely extract field values."""
    field = fields.get(field_name)
    return field.value if field else None

async def analyze_invoice():
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
        
        # Analyze invoice using prebuilt-invoice analyzer
        poller = await client.content_analyzers.begin_analyze(
            analyzer_id="prebuilt-invoice", 
            url=file_url
        )
        result: AnalyzeResult = await poller.result()
        
        # Extract invoice fields
        content: MediaContent = result.contents[0]
        
        # Extract basic invoice information
        customer_name = get_field_value(content.fields, "CustomerName")
        invoice_total = get_field_value(content.fields, "InvoiceTotal")
        invoice_date = get_field_value(content.fields, "InvoiceDate")
        
        print(f"Customer Name: {customer_name or '(None)'}")
        print(f"Invoice Total: ${invoice_total or '(None)'}")
        print(f"Invoice Date: {invoice_date or '(None)'}")
        
        # Extract invoice items (array field)
        items = get_field_value(content.fields, "Items")
        if items:
            print("\n🛒 Invoice Items:")
            for i, item in enumerate(items):
                if hasattr(item, 'value_object') and item.value_object:
                    item_obj = item.value_object
                    description = get_field_value(item_obj, "Description")
                    quantity = get_field_value(item_obj, "Quantity")
                    unit_price = get_field_value(item_obj, "UnitPrice")
                    
                    print(f"  Item {i + 1}: {description} - Qty: {quantity} @ ${unit_price}")

    if isinstance(credential, DefaultAzureCredential):
        await credential.close()

# Run the analysis
asyncio.run(analyze_invoice())
```

## Troubleshooting

### Common Issues

**Error: "Access denied due to invalid subscription key or wrong API endpoint"**
- Verify your endpoint URL is correct and includes the trailing slash
- Ensure your API key is valid or that your Azure AD credentials have the correct permissions
- Make sure you have the **Cognitive Services User** role assigned to your account

**Error: "Model deployment not found" or "Default model deployment not configured"**
- Ensure you have deployed the required models (GPT-4.1, GPT-4.1-mini, text-embedding-3-large) in Microsoft Foundry
- Verify you have configured the default model deployments (see [Configure Model Deployments](#step-3-configure-model-deployments-required-for-prebuilt-analyzers))
- Check that your deployment names match what you configured in the defaults

**Error: "Operation failed" or timeout**
- Content Understanding operations are asynchronous and may take time to complete
- Ensure you are properly polling for results using `.result()` on the poller object
- Check the operation status for more details about the failure

### Microsoft Foundry Resource and Regional Support

Azure AI Content Understanding requires a [Microsoft Foundry resource][cu_quickstart] and is only available in certain [supported regions][cu_region_support]. Make sure to:

- Create a Microsoft Foundry resource in the Azure portal under **AI Foundry** > **AI Foundry**
- Select a supported region when creating the resource

For detailed setup instructions and current supported regions, see: **[Azure AI Content Understanding Quickstart Guide][cu_quickstart]**

### Enable Logging

This library uses the standard [logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted** headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

```python
import logging
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Create client with logging enabled
client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key),
    logging_enable=True
)
```

See full SDK logging documentation with examples [here][sdk_logging_docs].

## Next steps

### More sample code

See the [Sample README][sample_readme] for several code snippets illustrating common patterns used in the Content Understanding Python API.

### Additional documentation

For more extensive documentation on Azure AI Content Understanding, see the [Content Understanding documentation][python_cu_product_docs] on docs.microsoft.com.

* Explore the [samples directory][python_cu_samples] for complete code examples
* Read the [Azure AI Content Understanding documentation][python_cu_product_docs] for detailed service information

## Running the Update Defaults Sample

To run the `update_defaults` code example shown above, you need to set environment variables with your credentials and model deployment names.

### Setting environment variables

**On Linux/macOS (bash):**
```bash
export AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://<your-resource-name>.services.ai.azure.com/"
export AZURE_CONTENT_UNDERSTANDING_KEY="<your-api-key>"  # Optional if using DefaultAzureCredential
export GPT_4_1_DEPLOYMENT="gpt-4.1"
export GPT_4_1_MINI_DEPLOYMENT="gpt-4.1-mini"
export TEXT_EMBEDDING_3_LARGE_DEPLOYMENT="text-embedding-3-large"
```

**On Windows (PowerShell):**
```powershell
$env:AZURE_CONTENT_UNDERSTANDING_ENDPOINT="https://<your-resource-name>.services.ai.azure.com/"
$env:AZURE_CONTENT_UNDERSTANDING_KEY="<your-api-key>"  # Optional if using DefaultAzureCredential
$env:GPT_4_1_DEPLOYMENT="gpt-4.1"
$env:GPT_4_1_MINI_DEPLOYMENT="gpt-4.1-mini"
$env:TEXT_EMBEDDING_3_LARGE_DEPLOYMENT="text-embedding-3-large"
```

**On Windows (Command Prompt):**
```cmd
set AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
set AZURE_CONTENT_UNDERSTANDING_KEY=<your-api-key>  # Optional if using DefaultAzureCredential
set GPT_4_1_DEPLOYMENT=gpt-4.1
set GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
set TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

### Running the sample code

After setting the environment variables, you can run the code examples shown in the [Configure Model Deployments](#step-3-configure-model-deployments-required-for-prebuilt-analyzers) section above.

**Alternatively, use the prepared sample script:**

For a complete, ready-to-use example, see `sample_update_defaults.py` in the [samples directory][sample_readme]. This sample includes error handling and additional features:

```bash
# Navigate to samples directory
cd samples

# Run the prepared sample
python sample_update_defaults.py
```

For async version:
```bash
python async_samples/sample_update_defaults_async.py
```

For comprehensive documentation on all available samples, see the [samples README][sample_readme].

## Running Tests

To run the tests for this package, you need to set up a `.env` file at the repository root with your test credentials.

### Setting up the .env file for tests

1. The `env.sample` file is located in this package directory. This file contains a template with all the required environment variables.

2. **Important**: The `.env` file should be placed at the **root of the `azure-sdk-for-python` repository**, not in the package directory. This follows the Azure SDK testing guidelines.

3. Copy the `env.sample` file from this package to the repo root to create your `.env` file:
   ```bash
   # From the repo root directory
   cp sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample .env
   ```
   
   Or if you're in the package directory:
   ```bash
   # From the package directory
   cp env.sample ../../../../.env
   ```

4. Edit the `.env` file at the repo root and fill in your actual values:
   - `AZURE_CONTENT_UNDERSTANDING_ENDPOINT`: Your Microsoft Foundry resource endpoint
   - `AZURE_CONTENT_UNDERSTANDING_KEY`: Your API key (optional if using DefaultAzureCredential)
   - `AZURE_TEST_RUN_LIVE`: Set to `true` to run tests against real Azure resources
   - `AZURE_SKIP_LIVE_RECORDING`: Set to `true` to skip recording when running live tests

### Running tests

**Important:** Make sure you have activated the virtual environment before running tests.

Install the development dependencies (if not already installed):
```bash
pip install -r dev_requirements.txt
pip install -e .
```

Run tests with pytest:
```bash
pytest tests/
```

#### Running tests in parallel

The tests support parallel execution using `pytest-xdist` for faster test runs:

```bash
# Auto-detect number of CPUs and run tests in parallel
pytest tests/ -n auto

# Or specify the number of workers
pytest tests/ -n 4
```

**Note:** The test proxy server is session-scoped and automatically handles parallel execution, so no additional configuration is needed.

For more information about running tests, see the [tests README][tests_readme] and the [Azure SDK Python Testing Guide][azure_sdk_testing_guide].

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][code_of_conduct_faq] or contact [opencode@microsoft.com][opencode_email] with any additional questions or comments.

<!-- LINKS -->

[python_cu_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding
[python_cu_pypi]: https://pypi.org/project/azure-ai-contentunderstanding/
[python_cu_product_docs]: https://learn.microsoft.com/azure/ai-services/content-understanding/
[python_cu_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples
[azure_sub]: https://azure.microsoft.com/free/
[cu_quickstart]: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=portal%2Cdocument
[cu_region_support]: https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support
[azure_portal]: https://portal.azure.com/
[deploy_models_docs]: https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-openai
[azure_identity_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity/README.md
[cu_prebuilt_analyzers]: https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers
[client_options]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#configuring-service-clients-using-clientoptions
[accessing_response]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#accessing-http-response-details-using-responset
[long_running_operations]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#consuming-long-running-operations-using-operationt
[handling_failures]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#reporting-errors-requestfailedexception
[diagnostics]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/samples/Diagnostics.md
[mocking]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-mock-helpers
[client_lifetime]: https://devblogs.microsoft.com/azure-sdk/lifetime-management-and-thread-safety-guarantees-of-azure-sdk-python-clients/
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[sample_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples
[tests_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/tests/README.md
[azure_sdk_testing_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
[pip]: https://pypi.org/project/pip/
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[opencode_email]: mailto:opencode@microsoft.com
