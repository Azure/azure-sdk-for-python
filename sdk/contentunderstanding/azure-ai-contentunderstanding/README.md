# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a solution that analyzes and comprehends various media content—such as documents, images, audio, and video—transforming it into structured, organized, and searchable data.

This table shows the relationship between SDK versions and supported API service versions:

| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0       | 2025-11-01                    |

## Getting started

### Prerequisites

- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- Once you have your Azure subscription, create an [Microsoft Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) in the Azure portal. Be sure to create it in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support).
- For more information, see: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=document

### Install the package

```bash
python -m pip install azure-ai-contentunderstanding
```

### Configure your Microsoft Foundry resource and required model deployments

Before running most samples (especially those that use prebuilt analyzers) you need to:

1. Create (or reuse) an Microsoft Foundry resource
2. Assign the correct role so you can configure default model deployments
3. Deploy the required foundation models (GPT and Embeddings) in that resource
4. Map those deployments to standard model names using the SDK's `update_defaults` API (one-time per resource)
5. Provide environment variables (via a `.env` file at the repository root for tests, or your shell/session for ad‑hoc runs)

#### 1. Create the Microsoft Foundry resource

Follow the steps in the Azure portal (Create a resource > AI Foundry). The Content Understanding service is hosted within this resource. After creation, locate the endpoint under: Resource Management > Keys and Endpoint. It typically looks like:

```
https://<your-resource-name>.services.ai.azure.com/
```

Set this as `AZURE_CONTENT_UNDERSTANDING_ENDPOINT`.

#### 2. Grant required permissions

To configure default model deployments you (or the service principal / managed identity you use) must have the **Cognitive Services User** role on the Microsoft Foundry resource, even if you are already an Owner. In the Azure portal:

1. Go to your resource
2. Access Control (IAM) > Add > Add role assignment
3. Choose Cognitive Services User
4. Assign it to your identity

Without this role, calls to `update_defaults` will fail.

#### 3. Deploy required models

Prebuilt analyzers rely on specific model families:

| Prebuilt analyzers | Required deployments |
| ------------------ | -------------------- |
| `prebuilt-documentSearch`, `prebuilt-audioSearch`, `prebuilt-videoSearch` | `gpt-4.1-mini`, `text-embedding-3-large` |
| `prebuilt-invoice`, `prebuilt-receipt` and similar structured document analyzers | `gpt-4.1`, `text-embedding-3-large` |

In Microsoft Foundry: Deployments > Deploy model > Deploy base model. Deploy each of:

- GPT-4.1 (suggested deployment name: `gpt-4.1`)
- GPT-4.1-mini (suggested deployment name: `gpt-4.1-mini`)
- text-embedding-3-large (suggested deployment name: `text-embedding-3-large`)

If you choose different deployment names, record them—you will use them in environment variables and when calling `update_defaults`.

#### 4. Configure environment variables

For local development and tests this repository uses a root-level `.env` file. A template is provided at:

`sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample`

Copy it to the repository root:

```bash
cp sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample .env
```

Then edit `.env` and set at minimum:

```env
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

#### 5. Set default model deployments (one-time)

Content Understanding expects a mapping from standard model names to your deployment names. Run the sample `update_defaults.py` (located in `samples/`) after the environment variables are set and roles assigned.

Short example (async):

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

After a successful run you can immediately use prebuilt analyzers such as `prebuilt-invoice` or `prebuilt-documentSearch`. If you encounter errors:

- Recheck deployment names (they must match exactly)
- Confirm the **Cognitive Services User** role assignment
- Verify the endpoint points to the correct resource

You only need to perform this configuration again if you change deployment names or create a new Microsoft Foundry resource.

#### Troubleshooting quick tips
- Missing model variables: ensure all three deployment environment variables are present; samples will warn politely if any are absent.
- Permission errors calling `update_defaults`: add (or re-add) the Cognitive Services User role.
- Authentication failures with DefaultAzureCredential: run `az login` (CLI) or configure another supported credential method.

For more detailed setup guidance, see the official service quickstart (linked below) and the inline comments in `env.sample`.

## Key concepts

Content Understanding provides the following main capability:

### Content Analyzers
Analyze documents and extract structured information using prebuilt or custom analyzers:
- **Prebuilt analyzers**: Ready-to-use analyzers for multi-modal content processing including `prebuilt-documentSearch`, `prebuilt-invoice`, `prebuilt-videoSearch` (examples - see [full list of prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers))
- **Custom analyzers**: Create analyzers with specific field schemas for multi-modal content processing (documents, images, audio, video)
- **Multiple input formats**: URLs, binary data, and various document types

## Examples

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

### Microsoft Foundry Resource and Regional Support

Azure AI Content Understanding requires an [Microsoft Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) and is only available in certain [supported regions](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support). Make sure to:

- Create an Microsoft Foundry resource in the Azure portal under **AI Foundry** > **AI Foundry**
- Select a supported region when creating the resource

For detailed setup instructions and current supported regions, see: **[Azure AI Content Understanding Quickstart Guide](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)**

## Next steps

For more information about Azure AI Content Understanding, see the following additional resources:
- **[Azure AI Content Understanding Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)**
- **[REST API Reference](https://learn.microsoft.com/rest/api/content-understanding/)**
- **[Quickstart Guide](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api)**

## Running Tests

To run the tests for this package, you need to set up a `.env` file with your test credentials.

### Setting up the .env file

1. The `env.sample` file is located in this package directory (`sdk/contentunderstanding/azure-ai-contentunderstanding/env.sample`). This file contains a template with all the required environment variables.

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
   - `CONTENTUNDERSTANDING_ENDPOINT`: Your Microsoft Foundry resource endpoint
   - `AZURE_CONTENT_UNDERSTANDING_KEY`: Your API key (optional if using DefaultAzureCredential)
   - `AZURE_TEST_RUN_LIVE`: Set to `true` to run tests against real Azure resources
   - `AZURE_SKIP_LIVE_RECORDING`: Set to `true` to skip recording when running live tests

### Running tests

**Important:** Make sure you have activated the virtual environment before running tests (see [Virtual Environment Setup](#virtual-environment-setup) above).

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

For more information about running tests, see the [Azure SDK Python Testing Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md).


[azure_sub]: https://azure.microsoft.com/free/
