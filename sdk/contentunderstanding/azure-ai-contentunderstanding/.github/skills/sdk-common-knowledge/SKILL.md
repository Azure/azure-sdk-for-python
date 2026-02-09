---
name: sdk-common-knowledge
description: Comprehensive domain knowledge for Azure AI Content Understanding - a multimodal AI service for extracting semantic content from documents, video, audio, and image files. Use this skill to answer questions about Content Understanding concepts, analyzers, field schemas, API operations, and Python SDK usage.
---

# Azure AI Content Understanding Domain Knowledge

This skill provides comprehensive domain knowledge for Azure AI Content Understanding, a multimodal AI service that extracts semantic content from documents, video, audio, and image files.

## Service Overview

**Azure AI Content Understanding** transforms unstructured content into structured, machine-readable data optimized for:
- **Retrieval-Augmented Generation (RAG)** applications
- **Automated workflows** and document processing pipelines
- **Multimodal content analysis** across documents, images, audio, and video

### Supported Modalities

| Modality | File Types | Use Cases |
|----------|-----------|-----------|
| **Document** | PDF, images (JPG, PNG, TIFF, BMP), Office docs (Word, Excel, PowerPoint), HTML | OCR, layout analysis, table extraction, markdown generation |
| **Image** | JPG, PNG, GIF, BMP, TIFF | Image description, visual content analysis |
| **Audio** | WAV, MP3, M4A, FLAC, OGG | Speech transcription, speaker diarization, conversation summaries |
| **Video** | MP4, MOV, AVI, MKV, WEBM | Frame extraction, audio transcription, temporal content alignment |

---

## Key Concepts

### Analyzers

Analyzers define how content is processed and what information is extracted. They determine:
- Processing configuration (OCR, layout, formulas, etc.)
- Field schema for structured extraction
- Output format (markdown, tables, annotations)

**Analyzer Types:**
1. **Prebuilt Analyzers** - Ready-to-use, production-ready analyzers
2. **Custom Analyzers** - User-defined analyzers with custom field schemas

### Analyzer ID Naming

- Pattern: `^[a-zA-Z0-9._-]{1,64}$`
- Max 64 characters
- Alphanumeric, dots, underscores, hyphens allowed
- Prebuilt analyzers use `prebuilt-` prefix

### Analyzer Status

| Status | Description |
|--------|-------------|
| `creating` | Analyzer is being created (async operation) |
| `ready` | Analyzer is ready for use |
| `deleting` | Analyzer is being deleted |
| `failed` | Analyzer creation failed |

---

## Prebuilt Analyzers

### RAG Analyzers (Optimized for Search/RAG)

| Analyzer ID | Modality | Description | Required Models |
|-------------|----------|-------------|-----------------|
| `prebuilt-documentSearch` | Document | Extracts markdown with layout preservation, tables, figures | gpt-4.1-mini, text-embedding-3-large |
| `prebuilt-imageSearch` | Image | Generates one-paragraph image descriptions | gpt-4.1-mini, text-embedding-3-large |
| `prebuilt-audioSearch` | Audio | Transcribes with speaker diarization and timing | gpt-4.1-mini, text-embedding-3-large |
| `prebuilt-videoSearch` | Video | Visual frame extraction + audio transcription with temporal alignment | gpt-4.1-mini, text-embedding-3-large |

### Base Analyzers (For Custom Analyzer Parents)

| Analyzer ID | Modality | Use Case |
|-------------|----------|----------|
| `prebuilt-document` | Document | Base for document custom analyzers |
| `prebuilt-image` | Image | Base for image custom analyzers |
| `prebuilt-audio` | Audio | Base for audio custom analyzers |
| `prebuilt-video` | Video | Base for video custom analyzers |

### Domain-Specific Analyzers

**Financial:**
- `prebuilt-invoice` - Invoice field extraction
- `prebuilt-receipt` - Receipt parsing
- `prebuilt-bankStatement` - Bank statement analysis

**Identity:**
- `prebuilt-idDocument` - ID documents (passports, licenses)
- `prebuilt-usDriverLicense` - US driver's licenses
- `prebuilt-usPassport` - US passports

**Tax Forms:**
- `prebuilt-tax.us.w2` - W-2 forms
- `prebuilt-tax.us.1040` - 1040 forms
- `prebuilt-tax.us.1099` - 1099 forms

**Mortgage/Lending:**
- `prebuilt-mortgage.closingDisclosure`
- `prebuilt-mortgage.loanApplication`

**Content Extraction:**
- `prebuilt-read` - OCR and text extraction
- `prebuilt-layout` - Layout analysis with structure

**Utility Analyzers:**
- `prebuilt-documentFieldSchema` - Schema generation
- `prebuilt-documentFields` - Field extraction

---

## Custom Analyzers

### Creating Custom Analyzers

Custom analyzers extend base analyzers with:
- Custom field schemas for domain-specific extraction
- Configuration overrides
- Knowledge sources for enhanced accuracy

### Request Body Structure

```json
{
  "description": "Description of the analyzer",
  "baseAnalyzerId": "prebuilt-document",
  "models": {
    "completion": "gpt-4.1",
    "embedding": "text-embedding-3-large"
  },
  "config": {
    "returnDetails": true,
    "enableFormula": false,
    "estimateFieldSourceAndConfidence": true
  },
  "fieldSchema": {
    "name": "MySchema",
    "description": "Schema description",
    "fields": {
      "FieldName": {
        "type": "string",
        "method": "extract",
        "description": "Field description"
      }
    }
  }
}
```

### Field Schema

#### Field Types (`ContentFieldType`)

| Type | Description | Python Representation |
|------|-------------|----------------------|
| `string` | Plain text | `str` |
| `date` | ISO 8601 date (YYYY-MM-DD) | `str` (date string) |
| `time` | ISO 8601 time (hh:mm:ss) | `str` (time string) |
| `number` | Double precision float | `float` |
| `integer` | 64-bit signed integer | `int` |
| `boolean` | Boolean value | `bool` |
| `array` | List of subfields | `list` |
| `object` | Named list of subfields | `dict` |
| `json` | JSON object | `dict` |

#### Generation Methods

| Method | Description |
|--------|-------------|
| `generate` | Values are generated based on content (AI interpretation) |
| `extract` | Values are extracted exactly as they appear |
| `classify` | Values are classified against predefined categories |

#### Field Definition Properties

```json
{
  "type": "string",
  "description": "Field description for AI guidance",
  "method": "extract",
  "enum": ["Option1", "Option2"],
  "enumDescriptions": {
    "Option1": "Description of option 1"
  },
  "examples": ["Example value 1", "Example value 2"],
  "estimateSourceAndConfidence": true,
  "items": { },  // For array type
  "properties": { }  // For object type
}
```

### Array and Object Fields

**Array Example:**
```json
{
  "Items": {
    "type": "array",
    "method": "extract",
    "items": {
      "type": "object",
      "properties": {
        "Description": { "type": "string" },
        "Amount": { "type": "number" }
      }
    }
  }
}
```

---

## Analyzer Configuration (`ContentAnalyzerConfig`)

### Document Processing Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enableOcr` | boolean | true | Enable optical character recognition |
| `enableLayout` | boolean | true | Enable layout analysis |
| `enableFormula` | boolean | false | Enable mathematical formula detection |
| `enableFigureAnalysis` | boolean | false | Enable chart/diagram analysis |
| `enableFigureDescription` | boolean | false | Generate figure descriptions |
| `returnDetails` | boolean | false | Return all content details |

### Output Format Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `tableFormat` | `html`, `markdown` | `html` | Table representation format |
| `chartFormat` | `chartJs`, `markdown` | `chartJs` | Chart representation format |
| `annotationFormat` | `none`, `markdown` | `markdown` | Annotation format |

### Classification/Segmentation Options

| Option | Type | Description |
|--------|------|-------------|
| `enableSegment` | boolean | Enable content segmentation by categories |
| `segmentPerPage` | boolean | Force segmentation by page |
| `contentCategories` | object | Map of categories for classification |
| `omitContent` | boolean | Omit original content, return only categorized results |

### Privacy/Processing Options

| Option | Type | Description |
|--------|------|-------------|
| `disableFaceBlurring` | boolean | Disable default face blurring |
| `processingLocation` | enum | Data processing location (`global`, `geography`, `dataZone`) |
| `locales` | string[] | Locale hints for speech transcription |

### Field Extraction Options

| Option | Type | Description |
|--------|------|-------------|
| `estimateFieldSourceAndConfidence` | boolean | Return field grounding and confidence scores |
| `dynamicFieldSchema` | boolean | Allow additional fields outside defined schema |

---

## API Operations

### Content Analyzers API

| Operation | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| Create Or Replace | PUT | `/contentunderstanding/analyzers/{analyzerId}` | Create new analyzer |
| Get | GET | `/contentunderstanding/analyzers/{analyzerId}` | Get analyzer properties |
| List | GET | `/contentunderstanding/analyzers` | List all analyzers |
| Update | PATCH | `/contentunderstanding/analyzers/{analyzerId}` | Update analyzer |
| Delete | DELETE | `/contentunderstanding/analyzers/{analyzerId}` | Delete analyzer |
| Copy | POST | `/contentunderstanding/analyzers/{analyzerId}:copy` | Copy analyzer |
| Grant Copy Authorization | POST | `/contentunderstanding/analyzers/{analyzerId}:grantCopyAuthorization` | Get copy auth |

### Analysis Operations

| Operation | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| Analyze | POST | `/contentunderstanding/analyzers/{analyzerId}:analyze` | Analyze from URL |
| Analyze Binary | POST | `/contentunderstanding/analyzers/{analyzerId}:analyzeBinary` | Analyze binary content |
| Get Result | GET | `/contentunderstanding/analyzerResults/{resultId}` | Get analysis result |
| Get Result File | GET | `/contentunderstanding/analyzerResults/{resultId}/files/{fileId}` | Get result file |
| Delete Result | DELETE | `/contentunderstanding/analyzerResults/{resultId}` | Delete result |

### Configuration Operations

| Operation | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| Get Defaults | GET | `/contentunderstanding/defaults` | Get resource defaults |
| Update Defaults | PATCH | `/contentunderstanding/defaults` | Update default model deployments |

---

## Python SDK Usage

### Client Initialization

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

# Using DefaultAzureCredential (recommended)
client = ContentUnderstandingClient(
    endpoint="https://<resource>.services.ai.azure.com/",
    credential=DefaultAzureCredential()
)

# Using API key
from azure.core.credentials import AzureKeyCredential
client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key)
)
```

### Async Client

```python
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

async with ContentUnderstandingClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential()
) as client:
    # Use client
    pass
```

### Analysis Operations

```python
from azure.ai.contentunderstanding.models import AnalyzeInput, AnalyzeResult

# Analyze from URL
poller = client.begin_analyze(
    analyzer_id="prebuilt-documentSearch",
    inputs=[AnalyzeInput(url="https://example.com/document.pdf")]
)
result: AnalyzeResult = poller.result()

# Access markdown content
content = result.contents[0]
print(content.markdown)
```

### Content Types

```python
from azure.ai.contentunderstanding.models import (
    MediaContent,
    DocumentContent,
    AudioVisualContent,
    MediaContentKind
)

# Check content type
if content.kind == MediaContentKind.DOCUMENT:
    doc_content: DocumentContent = content
    print(f"Pages: {doc_content.start_page_number} - {doc_content.end_page_number}")
elif content.kind == MediaContentKind.AUDIO_VISUAL:
    av_content: AudioVisualContent = content
    print(f"Duration: {av_content.start_time} - {av_content.end_time}")
```

### Field Extraction

```python
# Access extracted fields
fields = content.fields
if "VendorName" in fields:
    vendor = fields["VendorName"]
    print(f"Vendor: {vendor.value}")
    print(f"Confidence: {vendor.confidence}")
    print(f"Source: {vendor.source}")

# Access array fields
items = fields.get("Items")
if items and items.value:
    for item in items.value:
        item_obj = item.value_object
        description = item_obj.get("Description")
        amount = item_obj.get("Amount")
```

### Custom Analyzer Management

```python
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition
)

# Create custom analyzer
analyzer = ContentAnalyzer(
    description="My custom invoice analyzer",
    base_analyzer_id="prebuilt-document",
    config=ContentAnalyzerConfig(
        return_details=True,
        enable_formula=False,
        estimate_field_source_and_confidence=True
    ),
    field_schema=ContentFieldSchema(
        name="InvoiceFields",
        fields={
            "VendorName": ContentFieldDefinition(
                type="string",
                method="extract",
                description="Name of the vendor"
            ),
            "TotalAmount": ContentFieldDefinition(
                type="number",
                method="extract",
                description="Total invoice amount"
            )
        }
    )
)

poller = client.begin_create_or_replace_analyzer(
    analyzer_id="my-invoice-analyzer",
    analyzer=analyzer
)
created_analyzer = poller.result()
```

### Update Default Model Deployments

```python
from azure.ai.contentunderstanding.models import DefaultsSettings, ModelDeploymentInfo

# Configure model deployments (one-time setup per resource)
defaults = DefaultsSettings(
    model_deployments={
        "gpt-4.1": ModelDeploymentInfo(deployment_id="gpt-4.1"),
        "gpt-4.1-mini": ModelDeploymentInfo(deployment_id="gpt-4.1-mini"),
        "text-embedding-3-large": ModelDeploymentInfo(deployment_id="text-embedding-3-large")
    }
)

client.update_defaults(defaults=defaults)
```

---

## Content Categories and Document Classification

### Defining Content Categories

```json
{
  "baseAnalyzerId": "prebuilt-document",
  "config": {
    "enableSegment": false,
    "contentCategories": {
      "receipt": {
        "description": "Any images or documents of receipts",
        "analyzerId": "my-receipt-analyzer"
      },
      "invoice": {
        "description": "Any images or documents of invoice",
        "analyzerId": "prebuilt-invoice"
      },
      "other": {
        "description": "Other document types"
      }
    },
    "omitContent": true
  }
}
```

### Classification Workflow

1. Input content is processed by base analyzer
2. Content is classified into defined categories
3. If `analyzerId` is specified, content is routed to that analyzer
4. If `omitContent: true`, only categorized results are returned

---

## Knowledge Sources

### Labeled Data Knowledge Source

Enhance analyzer accuracy with labeled training data:

```json
{
  "knowledgeSources": [
    {
      "kind": "labeledData",
      "containerUrl": "https://storage.blob.core.windows.net/container",
      "prefix": "trainingData/",
      "fileListPath": "trainingData/fileList.jsonl"
    }
  ]
}
```

---

## Required Model Deployments

### Model Requirements by Analyzer Type

| Analyzer Category | Required Models |
|-------------------|-----------------|
| RAG analyzers (`*Search`) | gpt-4.1-mini, text-embedding-3-large |
| Domain-specific (invoice, receipt, etc.) | gpt-4.1, text-embedding-3-large |
| Custom analyzers | Depends on `models` configuration |

### Setting Up Model Deployments

1. Deploy models in Microsoft Foundry portal
2. Configure default model mappings via `update_defaults` API
3. This is a one-time setup per Microsoft Foundry resource

---

## Response Structure

### AnalyzeResult

```python
class AnalyzeResult:
    analyzer_id: str
    api_version: str
    created_at: datetime
    contents: List[MediaContent]  # DocumentContent or AudioVisualContent
    warnings: List[Error]
```

### DocumentContent

```python
class DocumentContent(MediaContent):
    kind: Literal["document"]
    markdown: str
    fields: Dict[str, FieldValue]
    start_page_number: int
    end_page_number: int
    pages: List[PageInfo]
    tables: List[Table]
    figures: List[Figure]
    paragraphs: List[Paragraph]
    # ... additional properties
```

### AudioVisualContent

```python
class AudioVisualContent(MediaContent):
    kind: Literal["audioVisual"]
    markdown: str
    fields: Dict[str, FieldValue]
    start_time: float
    end_time: float
    transcript_phrases: List[TranscriptPhrase]
    # ... additional properties
```

---

## Common Troubleshooting

### Error: "Model deployment not found"
- Ensure models are deployed in Microsoft Foundry
- Verify `update_defaults` has been called to configure model mappings
- Check deployment names match exactly

### Error: "Access denied"
- Ensure **Cognitive Services User** role is assigned
- Verify API key or credentials are correct
- Check endpoint URL format

### Error: Operation timeout
- Content Understanding uses async long-running operations
- Use `.result()` to wait for completion
- Check operation status via operation location URL

### Best Practices

1. **Always configure defaults first** - Run `sample_update_defaults.py` before using prebuilt analyzers
2. **Use appropriate analyzers** - Match analyzer to content type for best results
3. **Enable `returnDetails`** - For detailed content information
4. **Set `estimateFieldSourceAndConfidence`** - To get grounding and confidence scores
5. **Handle async operations** - Use poller's `.result()` method

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONTENTUNDERSTANDING_ENDPOINT` | Yes | Microsoft Foundry resource endpoint |
| `CONTENTUNDERSTANDING_KEY` | No | API key (optional if using DefaultAzureCredential) |
| `GPT_4_1_DEPLOYMENT` | For setup | GPT-4.1 deployment name |
| `GPT_4_1_MINI_DEPLOYMENT` | For setup | GPT-4.1-mini deployment name |
| `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` | For setup | Text embedding deployment name |

---

## Related Resources

- [Python SDK README](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md)
- [Python SDK Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples)
- [Product Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
- [REST API Reference](https://learn.microsoft.com/rest/api/contentunderstanding/)
- [Prebuilt Analyzers](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers)
- [Create Custom Analyzer Tutorial](https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/create-custom-analyzer)
- [Region Support](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)
