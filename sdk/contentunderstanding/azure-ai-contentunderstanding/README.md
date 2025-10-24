# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a solution that analyzes and comprehends various media content—such as documents, images, audio, and video—transforming it into structured, organized, and searchable data.

This table shows the relationship between SDK versions and supported API service versions:

| SDK version | Supported API service version |
| ----------- | ----------------------------- |
| 1.0.0b1     | 2025-05-31                    |

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

Content Understanding provides three main capabilities:

### Content Analyzers
Analyze documents and extract structured information using prebuilt or custom analyzers:
- **Prebuilt analyzers**: Ready-to-use analyzers for multi-modal content processing including `prebuilt-documentAnalyzer`, `prebuilt-invoice`, `prebuilt-videoAnalyzer` (examples - see [full list of prebuilt analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers))
- **Custom analyzers**: Create analyzers with specific field schemas for multi-modal content processing (documents, images, audio, video)
- **Multiple input formats**: URLs, binary data, and various document types

### Content Classifiers
Detect and identify documents within your application using intelligent classification:
- **Document classification**: Categorize documents into up to 50 defined categories without training data
- **Multi-document processing**: Identify multiple document types or instances within a single file
- **Flexible splitting modes**: Choose how to process content (entire file, per-page, or auto-detection)
- **Analyzer integration**: Link classifier categories with analyzers for end-to-end document processing
- **Business use cases**: Perfect for invoices, tax documents, contracts, and complex document workflows

### Face Recognition & Person Management (Preview)
Cloud-based face detection, enrollment, and recognition capabilities:
- **Face detection**: Detect faces in images with bounding boxes
- **Person directories**: Organize faces and identity profiles in structured repositories
- **Face verification**: Compare faces for identity verification
- **Face identification**: Match faces to enrolled persons
- **Note**: This feature is in preview and will be removed in GA. See [Face solutions overview](https://learn.microsoft.com/azure/ai-services/content-understanding/face/overview) for details.

## Examples

### Extract Markdown Content from Documents

Use the `prebuilt-documentAnalyzer` to extract markdown content from documents:

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
        
        # Analyze document using prebuilt-documentAnalyzer
        poller = await client.content_analyzers.begin_analyze(
            analyzer_id="prebuilt-documentAnalyzer", 
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
    return field["value"] if field and "value" in field else None

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
                item_obj = item["valueObject"]
                if item_obj:
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
