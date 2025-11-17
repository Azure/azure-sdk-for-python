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
- Once you have your Azure subscription, create an [Azure AI Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) in the Azure portal. Be sure to create it in a [supported region](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support).
- For more information, see: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=document

### Install the package

```bash
python -m pip install azure-ai-contentunderstanding
```

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

### Azure AI Foundry Resource and Regional Support

Azure AI Content Understanding requires an [Azure AI Foundry resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesAIFoundry) and is only available in certain [supported regions](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support). Make sure to:

- Create an Azure AI Foundry resource in the Azure portal under **AI Foundry** > **AI Foundry**
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
   - `CONTENTUNDERSTANDING_ENDPOINT`: Your Azure AI Foundry resource endpoint
   - `AZURE_CONTENT_UNDERSTANDING_KEY`: Your API key (optional if using DefaultAzureCredential)
   - `AZURE_TEST_RUN_LIVE`: Set to `true` to run tests against real Azure resources
   - `AZURE_SKIP_LIVE_RECORDING`: Set to `true` to skip recording when running live tests

### Running tests

Install the development dependencies:
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
