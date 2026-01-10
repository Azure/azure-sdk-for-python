# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a multimodal AI service that extracts semantic content from documents, video, audio, and image files. It transforms unstructured content into structured, machine-readable data optimized for retrieval-augmented generation (RAG) and automated workflows.

Use the client library for Azure AI Content Understanding to:

* **Extract document content** - Extract text, tables, figures, layout information, and structured markdown from documents (PDF, images with text or hand-written text, Office documents and more)
* **Transcribe and analyze audio** - Convert audio content into searchable transcripts with speaker diarization and timing information
* **Analyze video content** - Extract visual frames, transcribe audio tracks, and generate structured summaries from video files
* **Leverage prebuilt analyzers** - Use production-ready prebuilt analyzers across industries including finance and tax (invoices, receipts, tax forms), identity verification (passports, driver's licenses), mortgage and lending (loan applications, appraisals), procurement and contracts (purchase orders, agreements), and utilities (billing statements)
* **Create custom analyzers** - Build domain-specific analyzers for specialized content extraction needs across all four modalities (documents, video, audio, and images)
* **Classify documents and video** - Automatically categorize and extract information from documents and video by type

[Source code][python_cu_src] | [Package (PyPI)][python_cu_pypi] | [Product documentation][python_cu_product_docs] | [Samples][python_cu_samples]

## Getting started

### Install the package

Python 3.9 or later is required to use this package.

Install the client library for Python with [pip][pip]:

```bash
python -m pip install azure-ai-contentunderstanding
```

**If running async APIs:** The async transport is designed to be opt-in. The [aiohttp](https://pypi.org/project/aiohttp/) framework is one of the supported implementations of async transport. It's not installed by default. You need to install it separately as follows: `pip install aiohttp`

This table shows the relationship between SDK versions and supported API service versions:

| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0b1     | 2025-11-01                    |

### Prerequisites

* An [Azure subscription][azure_sub].
* A **Microsoft Foundry resource** to use this package.

### Configuring Microsoft Foundry resource

Before using the Content Understanding SDK, you need to set up a Microsoft Foundry resource and deploy the required large language models. Content Understanding currently uses OpenAI GPT models (such as gpt-4.1, gpt-4.1-mini, and text-embedding-3-large).

#### Step 1: Create Microsoft Foundry resource

> **Important:** You must create your Microsoft Foundry resource in a region that supports Content Understanding. For a list of available regions, see [Azure Content Understanding region and language support][cu_region_support].

1. Follow the steps in the [Azure Content Understanding quickstart][cu_quickstart] to create a Microsoft Foundry resource in the Azure portal
2. Get your Foundry resource's endpoint URL from Azure Portal:
   - Go to [Azure Portal][azure_portal]
   - Navigate to your Microsoft Foundry resource
   - Go to **Resource Management** > **Keys and Endpoint**
   - Copy the **Endpoint** URL (typically `https://<your-resource-name>.services.ai.azure.com/`)

**Important: Grant Required Permissions**

After creating your Microsoft Foundry resource, you must grant yourself the **Cognitive Services User** role to enable API calls for setting default model deployments:

1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Access Control (IAM)** in the left menu
4. Click **Add** > **Add role assignment**
5. Select the **Cognitive Services User** role
6. Assign it to yourself (or the user/service principal that will run the application)

> **Note:** This role assignment is required even if you are the owner of the resource. Without this role, you will not be able to call the Content Understanding API to configure model deployments for prebuilt analyzers and custom analyzers.

#### Step 2: Deploy required models

**Important:** The prebuilt and custom analyzers require large language model deployments. You must deploy at least the following models before using prebuilt analyzers and custom analyzers:
- `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch` require **gpt-4.1-mini** and **text-embedding-3-large**
- Other prebuilt analyzers like `prebuilt-invoice`, `prebuilt-receipt` require **gpt-4.1** and **text-embedding-3-large**

To deploy a model:

1. In Microsoft Foundry, go to **Deployments** > **Deploy model** > **Deploy base model**
2. Search for and select the model you want to deploy. Currently, prebuilt analyzers require models such as `gpt-4.1`, `gpt-4.1-mini`, and `text-embedding-3-large`
3. Complete the deployment with your preferred settings
4. Note the deployment name you chose (by convention, use the model name as the deployment name, e.g., `gpt-4.1` for the `gpt-4.1` model). You can use any deployment name you prefer, but you'll need to note it for use in Step 3 when configuring model deployments.

Repeat this process for each model required by your prebuilt analyzers.

For more information on deploying models, see [Create model deployments in Microsoft Foundry portal][deploy_models_docs].

#### Step 3: Configure model deployments (required for prebuilt analyzers)

> **IMPORTANT:**  This is a **one-time setup per Microsoft Foundry resource** that maps your deployed models to those required by the prebuilt analyzers and custom models. If you have multiple Microsoft Foundry resources, you need to configure each one separately.

You need to configure the default model mappings in your Microsoft Foundry resource. This can be done programmatically using the SDK. The configuration maps your deployed models (currently gpt-4.1, gpt-4.1-mini, and text-embedding-3-large) to the large language models required by prebuilt analyzers.

To configure model deployments using code, see [`sample_update_defaults.py`][sample_update_defaults] for a complete example. The sample shows how to:
- Map your deployed models to the models required by prebuilt analyzers
- Retrieve the current default model deployment configuration

Before running the sample, set up environment variables. For local development and tests this repository uses a root-level `.env` file. A template is provided in the package directory as `env.sample`.

Copy it to the repository root:

```bash
cp sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample .env
```

Then edit `.env` and set at minimum:

The environment variables define your Microsoft Foundry resource endpoint and the deployment names for the models you deployed in Step 2. **Important:** The deployment name values (e.g., `gpt-4.1`, `gpt-4.1-mini`, `text-embedding-3-large`) must exactly match the deployment names you chose when deploying models in Step 2.

```
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
# Optionally provide a key; if omitted, DefaultAzureCredential is used.
AZURE_CONTENT_UNDERSTANDING_KEY=<optional-api-key>
GPT_4_1_DEPLOYMENT=gpt-4.1
GPT_4_1_MINI_DEPLOYMENT=gpt-4.1-mini
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=text-embedding-3-large
```

Notes:
- If `AZURE_CONTENT_UNDERSTANDING_KEY` is not set the SDK will fall back to `DefaultAzureCredential`. Ensure you have authenticated (e.g. `az login`).
- Keep the `.env` file out of version control—do not commit secrets.
- The model deployment variables are required for configuring defaults and for samples that use prebuilt analyzers.

**This is a critical step:** After setting up the environment variables, you must run the sample to configure the default model deployments. This one-time configuration maps your deployed models to the standard model names that prebuilt analyzers require. Without running this configuration, prebuilt analyzers will not work because they won't know which of your deployed models to use.

Run the sample:

```bash
python samples/sample_update_defaults.py
```

After a successful run you can immediately use prebuilt analyzers such as `prebuilt-invoice` or `prebuilt-documentSearch`. If you encounter errors:

- Recheck deployment names (they must match exactly)
- Confirm the **Cognitive Services User** role assignment
- Verify the endpoint points to the correct resource

### Authenticate the client

In order to interact with the Content Understanding service, you'll need to create an instance of the `ContentUnderstandingClient` class. To authenticate the client, you need your Microsoft Foundry resource endpoint and credentials. You can use either an API key or Microsoft Entra ID authentication.

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

> **⚠️ Security Warning**: API key authentication is less secure and is only recommended for testing purposes with test resources. For production, use `DefaultAzureCredential` or other secure authentication methods.

To get your API key:
1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Resource Management** > **Keys and Endpoint**
4. Copy one of the **Keys** (Key1 or Key2)

For more information on authentication, see [Azure Identity client library][azure_identity_readme].

## Key concepts

### Prebuilt analyzers

Content Understanding provides a rich set of prebuilt analyzers that are ready to use without any configuration. These analyzers are powered by knowledge bases of thousands of real-world document examples, enabling them to understand document structure and adapt to variations in format and content.

Prebuilt analyzers are organized into several categories:

* **RAG analyzers** - Optimized for retrieval-augmented generation scenarios with semantic analysis and markdown extraction. These analyzers return markdown and a one-paragraph `Summary` for each content item:
  * **`prebuilt-documentSearch`** - Extracts content from documents (PDF, images, Office documents) with layout preservation, table detection, figure analysis, and structured markdown output. Optimized for RAG scenarios.
  * **`prebuilt-imageSearch`** - Analyzes standalone images and returns a one-paragraph description of the image content. Optimized for image understanding and search scenarios. For images that contain text (including hand-written text), use `prebuilt-documentSearch`.
  * **`prebuilt-audioSearch`** - Transcribes audio content with speaker diarization, timing information, and conversation summaries. Supports multilingual transcription.
  * **`prebuilt-videoSearch`** - Analyzes video content with visual frame extraction, audio transcription, and structured summaries. Provides temporal alignment of visual and audio content and can return multiple segments per video.
* **Content extraction analyzers** - Focus on OCR and layout analysis (e.g., `prebuilt-read`, `prebuilt-layout`)
* **Base analyzers** - Fundamental content processing capabilities used as parent analyzers for custom analyzers (e.g., `prebuilt-document`, `prebuilt-image`, `prebuilt-audio`, `prebuilt-video`)
* **Domain-specific analyzers** - Preconfigured analyzers for common document categories including financial documents (invoices, receipts, bank statements), identity documents (passports, driver's licenses), tax forms, mortgage documents, and contracts
* **Utility analyzers** - Specialized tools for schema generation and field extraction (e.g., `prebuilt-documentFieldSchema`, `prebuilt-documentFields`)

For a complete list of available prebuilt analyzers and their capabilities, see the [Prebuilt analyzers documentation][cu_prebuilt_analyzers].

>

### Custom analyzers

You can create custom analyzers with specific field schemas for multi-modal content processing (documents, images, audio, video). Custom analyzers allow you to extract domain-specific information tailored to your use case across all four modalities (documents, video, audio, and images).

### Content types

The API returns different content types based on the input. Both `DocumentContent` and `AudioVisualContent` classes derive from `MediaContent` class, which provides basic information and markdown representation. Each derived class provides additional properties to access detailed information:

* **`DocumentContent`** - For document files (PDF, HTML, images, Office documents such as Word, Excel, PowerPoint, and more). Provides basic information such as page count and MIME type. Retrieve detailed information including pages, tables, figures, paragraphs, and many others.
* **`AudioVisualContent`** - For audio and video files. Provides basic information such as timing information (start/end times) and frame dimensions (for video). Retrieve detailed information including transcript phrases, timing information, and for video, key frame references and more.

### Asynchronous operations

Content Understanding operations are asynchronous long-running operations. The workflow is:

1. **Begin Analysis** - Start the analysis operation (returns immediately with an operation location)
2. **Poll for Results** - Poll the operation location until the analysis completes
3. **Process Results** - Extract and display the structured results

The SDK provides `LROPoller` types that handle polling automatically when using `.result()`. For analysis operations, the SDK returns a poller that provides access to the operation ID via the `operation_id` property. This operation ID can be used with `get_result_file*` and `delete_result*` methods.

### Main classes

* **`ContentUnderstandingClient`** - The main client for analyzing content, as well as creating, managing, and configuring analyzers
* **`AnalyzeResult`** - Contains the structured results of an analysis operation, including content elements, markdown, and metadata

### Thread safety

We guarantee that all client instance methods are thread-safe and independent of each other. This ensures that the recommendation of reusing client instances is always safe, even across threads.

### Additional concepts

[Client options][client_options] |
[Accessing the response][accessing_response] |
[Long-running operations][long_running_operations] |
[Handling failures][handling_failures] |
[Diagnostics][diagnostics]

## Examples

You can familiarize yourself with different APIs using [Samples][python_cu_samples].

The samples demonstrate:

* **Configuration** - Configure model deployment defaults for prebuilt analyzers and custom analyzers
* **Document Content Extraction** - Extract structured markdown content from PDFs and images using `prebuilt-documentSearch`, optimized for RAG (Retrieval-Augmented Generation) applications
* **Multi-Modal Content Analysis** - Analyze content from URLs across all modalities: extract markdown and summaries from documents, images, audio, and video using `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, and `prebuilt-videoSearch`
* **Domain-Specific Analysis** - Extract structured fields from invoices using `prebuilt-invoice`
* **Advanced Document Features** - Extract charts, hyperlinks, formulas, and annotations from documents
* **Custom Analyzers** - Create custom analyzers with field schemas for specialized extraction needs
* **Document Classification** - Create and use classifiers to categorize documents
* **Analyzer Management** - Get, list, update, copy, and delete analyzers
* **Result Management** - Retrieve result files from video analysis and delete analysis results

See the [samples directory][python_cu_samples] for complete examples.

### Extract markdown content from documents

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
        print("Markdown Content:")
        print(content.markdown)
        
        # Access document-specific properties
        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore
            print(f"Pages: {document_content.start_page_number} - {document_content.end_page_number}")

    if isinstance(credential, DefaultAzureCredential):
        await credential.close()

# Run the analysis
asyncio.run(analyze_document())
```

### Extract structured fields from invoices

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
            print("\nInvoice Items:")
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

### Common issues

**Error: "Access denied due to invalid subscription key or wrong API endpoint"**
- Verify your `endpoint URL` is correct
- Ensure your `API key` is valid or that your Microsoft Entra ID credentials have the correct permissions
- Make sure you have the **Cognitive Services User** role assigned to your account

**Error: "Model deployment not found" or "Default model deployment not configured"**
- Ensure you have deployed the required models (gpt-4.1, gpt-4.1-mini, text-embedding-3-large) in Microsoft Foundry
- Verify you have configured the default model deployments (see [Configure Model Deployments](#step-3-configure-model-deployments-required-for-prebuilt-analyzers))
- Check that your deployment names match what you configured in the defaults

**Error: "Operation failed" or timeout**
- Content Understanding operations are asynchronous and may take time to complete
- Ensure you are properly polling for results using `.result()` or manual polling
- Check the operation status for more details about the failure

### Enable logging

To enable logging for debugging, configure logging in your application:

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

For more information about logging, see the [Azure SDK Python logging documentation][sdk_logging_docs].

## Next steps

* [`sample_update_defaults.py`][sample_update_defaults] - Required one-time setup to configure model deployments for prebuilt and custom analyzers
* [`sample_analyze_binary.py`][sample_analyze_binary] - Analyze PDF files from disk using `prebuilt-documentSearch`
* Explore the [samples directory][python_cu_samples] for complete code examples
* Read the [Azure AI Content Understanding documentation][python_cu_product_docs] for detailed service information

## Running the update defaults sample

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
```bat
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

## Running tests

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
[diagnostics]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#logging
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[sample_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples
[sample_update_defaults]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_update_defaults.py
[sample_analyze_binary]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_binary.py
[tests_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/tests/README.md
[azure_sdk_testing_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
[pip]: https://pypi.org/project/pip/
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[opencode_email]: mailto:opencode@microsoft.com
[aiohttp]: https://pypi.org/project/aiohttp/
