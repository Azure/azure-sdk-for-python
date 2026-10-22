---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-content-understanding
urlFragment: contentunderstanding-samples
---

# Azure AI Content Understanding client library for Python Samples

These code samples demonstrate common scenarios with the Azure AI Content Understanding client library.

**Note:** All samples in this folder use synchronous operations. For async samples, see the [async_samples][async_samples] directory.

## Setup

Before running samples, complete the Microsoft Foundry resource and model deployment steps in the [main README][main_readme], then configure your local environment as shown below. Model deployment defaults are applied by [`sample_update_defaults.py`][sample_update_defaults].

Helpful docs while setting up:
- [Supported generative models](https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits#supported-generative-models)
- [Model retirement schedule](https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule)
- [Region and language support](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support)
- [Content Understanding quickstart prerequisites](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=portal%2Cdocument&pivots=programming-language-rest#prerequisites)
- [Deploy models in Microsoft Foundry](https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-openai)
- [Models and deployments guidance](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/models-deployments)

### 1. Virtual environment and dependencies

```bash
# 1. Navigate to package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# 2. Create virtual environment (only needed once)
python -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate  # On Windows

# 4. Install SDK and all dependencies
# Preview / beta package is required for 2026-06-01-preview samples (inline analysis,
# semantic chunking, analyzer workflows, and related APIs). Without --pre, pip installs
# the latest stable release, which does not include those preview APIs.
python -m pip install --pre azure-ai-contentunderstanding
pip install -r dev_requirements.txt  # Includes aiohttp, pytest, python-dotenv, azure-identity
```

**Note:** All dependencies for running samples and tests are in `dev_requirements.txt`. This includes:
- `aiohttp` - Required for async operations
- `python-dotenv` - For loading `.env` files
- `azure-identity` - For `DefaultAzureCredential` authentication
- `pytest-xdist` - For parallel test execution

### 2. Environment variables

The environment variables define your Microsoft Foundry resource endpoint and the deployment names for the models you deployed. **Important:** Deployment names are user-defined and must exactly match the names you chose when deploying models; they do not need to match the model names.

**Option A: Using .env file (Recommended for development)**

A template is provided in the package directory as `env.sample`.

1. Copy the template to the samples directory:
   ```bash
   # from sdk/contentunderstanding/azure-ai-contentunderstanding
   cp env.sample samples/.env
   ```

2. Edit the `.env` file and set the following variables at minimum:
    * `CONTENTUNDERSTANDING_ENDPOINT` (required) - Your Microsoft Foundry resource endpoint
    * `CONTENTUNDERSTANDING_KEY` (optional) - Your API key. Required if using API key authentication. If omitted, `DefaultAzureCredential` will be used.
    * `CU_COMPLETION_MODEL` (optional) - Completion model name (defaults to `gpt-5.2`)
    * `CU_COMPLETION_MODEL_MINI` (optional) - Mini completion model name (defaults to `CU_COMPLETION_MODEL`)
    * `CU_EMBEDDING_MODEL` (optional) - Embedding model name (defaults to `text-embedding-3-large`)
    * `CU_COMPLETION_MODEL_DEPLOYMENT` (required for sample_update_defaults.py) - Your gpt-5.2 deployment name in Microsoft Foundry
    * `CU_COMPLETION_MINI_DEPLOYMENT` (optional) - Deployment for prebuilt-analyzer-completion-mini (defaults to completion deployment)
    * `CU_EMBEDDING_DEPLOYMENT` (required for sample_update_defaults.py) - Your embedding model deployment name in Microsoft Foundry

    ```bash
    CONTENTUNDERSTANDING_ENDPOINT=https://<your-resource-name>.services.ai.azure.com/
    # Optionally provide a key; if omitted, DefaultAzureCredential is used.
    CONTENTUNDERSTANDING_KEY=<optional-api-key>
    CU_COMPLETION_MODEL=gpt-5.2
    CU_COMPLETION_MODEL_MINI=gpt-5.2
    CU_EMBEDDING_MODEL=text-embedding-3-large
    CU_COMPLETION_MODEL_DEPLOYMENT=my-completion-deployment
    CU_COMPLETION_MINI_DEPLOYMENT=my-completion-mini-deployment
    CU_EMBEDDING_DEPLOYMENT=my-embedding-deployment
    ```

**Option B: Using command line**

**On Linux/macOS (bash):**
```bash
export CONTENTUNDERSTANDING_ENDPOINT="https://<your-resource-name>.services.ai.azure.com/"
export CONTENTUNDERSTANDING_KEY="<your-api-key>"  # Optional if using DefaultAzureCredential
export CU_COMPLETION_MODEL="gpt-5.2"
export CU_COMPLETION_MODEL_MINI="gpt-5.2"
export CU_EMBEDDING_MODEL="text-embedding-3-large"
export CU_COMPLETION_MODEL_DEPLOYMENT="my-completion-deployment"
export CU_COMPLETION_MINI_DEPLOYMENT="my-completion-mini-deployment"
export CU_EMBEDDING_DEPLOYMENT="my-embedding-deployment"
```

**On Windows (PowerShell):**
```powershell
$env:CONTENTUNDERSTANDING_ENDPOINT="https://<your-resource-name>.services.ai.azure.com/"
$env:CONTENTUNDERSTANDING_KEY="<your-api-key>"  # Optional if using DefaultAzureCredential
$env:CU_COMPLETION_MODEL="gpt-5.2"
$env:CU_COMPLETION_MODEL_MINI="gpt-5.2"
$env:CU_EMBEDDING_MODEL="text-embedding-3-large"
$env:CU_COMPLETION_MODEL_DEPLOYMENT="my-completion-deployment"
$env:CU_COMPLETION_MINI_DEPLOYMENT="my-completion-mini-deployment"
$env:CU_EMBEDDING_DEPLOYMENT="my-embedding-deployment"
```

Notes:
- If `CONTENTUNDERSTANDING_KEY` is not set the SDK will fall back to `DefaultAzureCredential`. Ensure you have authenticated (e.g. `az login`).
- Keep the `.env` file out of version control—do not commit secrets.

### 3. Configure model deployment defaults

```bash
# from sdk/contentunderstanding/azure-ai-contentunderstanding
python samples/sample_update_defaults.py
```

(Or for async: `python samples/async_samples/sample_update_defaults_async.py`)

After the script runs successfully, you can use prebuilt analyzers like `prebuilt-invoice` or `prebuilt-documentSearch`.

If you encounter errors:
- **Deployment Not Found**: Check that deployment names in environment variables match exactly what you created in Foundry.
- **Access Denied**: Ensure you have the **Cognitive Services User** role assignment.

### 4. Running samples

**Important:** Always run samples from the activated virtual environment!

#### Sync samples

Sync samples are in the `samples/` directory. We recommend running them from the `samples/` directory so relative paths (for local files and `.env` configuration) resolve correctly:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# Navigate to samples directory
cd samples

# Run sync samples
python sample_analyze_url.py
python sample_analyze_binary.py
```

#### Async samples

Async samples live in `samples/async_samples/`. Run them from the `samples/` directory so relative paths such as `sample_files/...` and `.env` resolve the same way as sync samples:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Navigate to samples directory (not async_samples/)
cd samples

# Run async samples
python async_samples/sample_analyze_url_async.py
python async_samples/sample_analyze_binary_async.py
```

**Note:** When running samples that use local files (like `sample_analyze_binary.py` or `async_samples/sample_analyze_binary_async.py`), make sure you run them from the `samples/` directory (or use the full path) so that relative paths like `sample_files/sample_invoice.pdf` resolve correctly.

## Sample Files

### Sample 00: Configure Defaults

#### `sample_update_defaults.py` / `sample_update_defaults_async.py`
**Required setup!** Configures and retrieves default model deployment settings for your Microsoft Foundry resource. This is a required one-time setup per Microsoft Foundry resource before using prebuilt or custom analyzers. The service periodically adds support for newer gpt-5.x models; map both concrete model names and prebuilt aliases. See [supported generative models](https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits#supported-generative-models), [model retirement](https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule), [region support](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support), the [quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=portal%2Cdocument), [deploy models](https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-openai), and [models and deployments](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/models-deployments).

**Key concepts:**
- Setting up model deployment mappings (gpt-5.2, text-embedding-3-large, and prebuilt aliases)
- Required before using prebuilt analyzers
- Retrieving current default settings

### Sample 01: Analyze Binary

#### `sample_analyze_binary.py` / `sample_analyze_binary_async.py`
Analyzes a PDF document from local binary data using `prebuilt-documentSearch`. Demonstrates how to read local files, restrict pages with `content_range`, extract markdown content, and convert results to LLM-friendly text with `to_llm_input()`.

**Key concepts:**
- Using `begin_analyze_binary` with binary input
- Choosing long-running operation (LRO) vs inline analyze (`analyze_binary_inline`, preview-only)
- Restricting pages with `content_range` (e.g. `"3-"`, `"1-3,5,9-"`)
- Reading local PDF files
- Extracting markdown content
- Accessing document properties (pages, dimensions)
- Converting results to LLM-ready text with `to_llm_input()`

### Sample 02: Analyze URL

#### `sample_analyze_url.py` / `sample_analyze_url_async.py`
**Start here!** Analyzes content from remote URLs using prebuilt RAG analyzers across modalities (documents, images, audio, video), including `content_range` for pages and time windows.

**Key concepts:**
- Using `begin_analyze` with URL input
- Choosing LRO vs `analyze_inline` (preview-only)
- Restricting analysis with `content_range` (pages for documents; milliseconds for audio/video)
- Extracting markdown content
- Working with the analysis result object model
- Analyzing different content types (documents, images, audio, video)

### Sample 03: Analyze Invoice

#### `sample_analyze_invoice.py` / `sample_analyze_invoice_async.py`
Extracts structured fields from invoices using `prebuilt-invoice` analyzer. Shows how to work with structured field extraction from domain-specific prebuilt analyzers and convert field results to LLM-friendly text with `to_llm_input()`.

**Key concepts:**
- Using specialized prebuilt analyzers (prebuilt-invoice)
- Extracting structured fields (customer name, totals, dates, line items)
- Working with field confidence scores and source locations
- Accessing object fields and array fields
- Reading `DocumentContent.unit` for coordinate measurement units
- Accessing usage details (billing metrics, token consumption per model)
- Converting field extraction results to LLM-ready text with `to_llm_input()`
- Financial document processing (invoices, receipts, credit cards, bank statements, checks)

### Sample 04: Create Analyzer

#### `sample_create_analyzer.py` / `sample_create_analyzer_async.py`
Creates a custom analyzer with field schema to extract structured data from documents. Shows how to define custom fields and extraction methods for document, audio, video, and image content.

**Key concepts:**
- Defining custom field schemas (string, number, date, object, array)
- Using extraction methods: `extract`, `generate`, `classify`
- Configuring analysis options (OCR, layout, formulas)
- Enabling source and confidence tracking
- Fields can include grounding (source/confidence) whenever the corresponding option is enabled
- Creating analyzers for different modalities (document, audio, video, image)

### Sample 05: Create Classifier

#### `sample_create_classifier.py` / `sample_create_classifier_async.py`
Creates a classifier analyzer to categorize documents and demonstrates automatic segmentation. Shows how to create classification workflows with custom categories.

**Key concepts:**
- Creating classifiers with content categories
- Document categorization (Loan_Application, Invoice, Bank_Statement)
- Enabling segmentation for multi-document files
- Processing classification results
- Content organization and data routing
- Converting classification results to LLM-friendly text with `to_llm_input()`

### Sample 06: Get Analyzer

#### `sample_get_analyzer.py` / `sample_get_analyzer_async.py`
Retrieves information about analyzers, including prebuilt and custom analyzers. Shows how to inspect analyzer configuration and capabilities.

**Key concepts:**
- Getting prebuilt analyzer details
- Getting custom analyzer details
- Dumping analyzer configuration as JSON
- Verifying analyzer configuration
- Inspecting analyzer capabilities

### Sample 07: List Analyzers

#### `sample_list_analyzers.py` / `sample_list_analyzers_async.py`
Lists all available analyzers in your Microsoft Foundry resource. Shows how to discover and manage analyzers.

**Key concepts:**
- Listing prebuilt and custom analyzers
- Displaying analyzer summary and details
- Identifying analyzer types
- Analyzer discovery and management

### Sample 08: Update Analyzer

#### `sample_update_analyzer.py` / `sample_update_analyzer_async.py`
Updates an existing custom analyzer's description and tags. Shows how to modify analyzer properties.

**Key concepts:**
- Updating analyzer description
- Adding, updating, and removing tags
- Verifying analyzer updates
- Modifying analyzer properties

### Sample 09: Delete Analyzer

#### `sample_delete_analyzer.py` / `sample_delete_analyzer_async.py`
Deletes a custom analyzer from your resource. Shows how to remove custom analyzers (prebuilt analyzers cannot be deleted).

**Key concepts:**
- Creating a simple analyzer for deletion demo
- Deleting custom analyzers
- Understanding deletion limitations (prebuilt analyzers cannot be deleted)

### Sample 10: Analyze Configs

#### `sample_analyze_configs.py` / `sample_analyze_configs_async.py`
Extracts additional features from documents such as charts, hyperlinks, formulas, annotations, and signatures (`2026-06-01-preview`). Shows advanced document analysis capabilities.

**Key concepts:**
- Using prebuilt-documentSearch with enhanced features
- Extracting chart figures (Chart.js format)
- Extracting hyperlinks
- Extracting mathematical formulas (LaTeX)
- Extracting PDF annotations
- Signature regions via layout details (`2026-06-01-preview`; see `sample_detect_signatures.py`)
- Analysis configuration options (OCR, layout, formulas)

### Sample 11: Analyze Return Raw JSON

#### `sample_analyze_return_raw_json.py` / `sample_analyze_return_raw_json_async.py`
Accesses the raw JSON response from analysis operations for custom processing. Shows how to work with raw service responses.

**Key concepts:**
- Getting raw JSON response
- Saving analysis results to file
- Custom JSON processing
- Inspecting complete response structure
- Debugging and troubleshooting

### Sample 12: Get Result File

#### `sample_get_result_file.py` / `sample_get_result_file_async.py`
Retrieves result files (such as keyframe images) from video analysis operations. Shows how to access generated files from analysis.

**Key concepts:**
- Analyzing video content
- Extracting operation IDs
- Retrieving keyframe images
- Saving result files to disk
- Working with generated analysis artifacts

### Sample 13: Delete Result

#### `sample_delete_result.py` / `sample_delete_result_async.py`
Demonstrates analyzing a document and then deleting the analysis result. Shows how to manage result retention and data cleanup.

**Key concepts:**
- Extracting operation IDs from analysis operations
- Deleting analysis results to manage storage
- Verifying result deletion
- Understanding result retention policies (24-hour auto-deletion)
- Data retention and compliance

### Sample 14: Copy Analyzer

#### `sample_copy_analyzer.py` / `sample_copy_analyzer_async.py`
Copies an analyzer from source to target within the same resource. Shows how to duplicate analyzers for testing and deployment.

**Key concepts:**
- Creating source analyzers
- Copying analyzers within the same resource
- Updating copied analyzers with new tags
- Use cases: testing, staging, production deployment
- Same-resource analyzer management

### Sample 15: Grant Copy Auth

#### `sample_grant_copy_auth.py` / `sample_grant_copy_auth_async.py`
Grants copy authorization and copies an analyzer from a source resource to a target resource (cross-resource copying). Shows cross-resource analyzer migration.

**Key concepts:**
- Cross-resource copying between different Azure resources
- Granting copy authorization
- Resource migration and multi-region deployment
- Required environment variables for cross-resource operations
- Cross-subscription analyzer deployment

### Sample 16: Create Analyzer With Labels

#### `sample_create_analyzer_with_labels.py` / `sample_create_analyzer_with_labels_async.py`
Creates a custom analyzer with labeled training data from Azure Blob Storage. Labeled data improves extraction accuracy by providing annotated examples that teach the model how to identify and extract specific fields from your documents.

**Key concepts:**
- Creating analyzers with labeled training data (LabeledDataKnowledgeSource)
- Uploading training files to Azure Blob Storage
- Generating User Delegation SAS URLs via DefaultAzureCredential
- Defining field schemas with extract and generate methods
- Using labeled data for improved field extraction accuracy
- Content Understanding Studio alternative for labeling workflow

### Sample 17: Create Analyzer Workflow

#### `sample_create_analyzer_workflow.py` / `sample_create_analyzer_workflow_async.py`
Creates two analyzers with different workflow settings and compares extracted values on the same invoice. Omit `workflow` for standard extraction, or set `ContentAnalyzerWorkflow.AGENTIC` when an answer must be **built from evidence** (for example averaging unit prices). In `2026-06-01-preview`, analysis supports one input file per request regardless of workflow. Agentic mode uses the advanced contextualization rate and typically takes longer with higher token cost.

**Key concepts:**
- Omitting `workflow` (default) vs setting `ContentAnalyzerWorkflow.AGENTIC` (requires `2026-06-01-preview`)
- Comparing default vs agentic extraction behavior on direct vs derived fields
- One-file-per-request limit applies regardless of workflow; advanced contextualization billing for agentic

### Sample 18: Analyze Chunking

**Requires:** `2026-06-01-preview`

#### `sample_analyze_chunking.py` / `sample_analyze_chunking_async.py`
Creates a custom analyzer with `SemanticChunkingStrategy` and reconstructs chunk markdown from analysis result spans. Uses `sample_files/sample_invoice.pdf` (`max_tokens=300`); the service typically separates header/party details, line items, and totals into distinct chunks.

**Key concepts:**
- Configuring `chunking_strategy` with semantic chunking
- Inspecting `DocumentContent.chunks`
- Reading chunk source and span offsets/lengths
- Reconstructing chunk markdown from `DocumentContent.markdown`

### Sample 19: Analyze URL Inline

**Requires:** `2026-06-01-preview`

#### `sample_analyze_inline.py` / `sample_analyze_inline_async.py`
Analyzes a URL input with `analyze_inline` (available only in `2026-06-01-preview`). Returns `ContentAnalyzerInlineResponse` in a single HTTP call with no polling; results are not persisted. Prefer LRO (`begin_analyze`) for larger files, broader analyzer coverage, or 24-hour result retention.

**Key concepts:**
- Choosing LRO vs inline analysis
- Supported inline analyzers (`prebuilt-digitalParse`, `prebuilt-read`, `prebuilt-layout`, and custom document analyzers without fields; not analyzers with figure analysis)
- Accessing `ContentAnalyzerInlineResponse.result`
- Converting inline results with `to_llm_input()`

### Sample 20: Analyze Binary Inline

**Requires:** `2026-06-01-preview`

#### `sample_analyze_binary_inline.py` / `sample_analyze_binary_inline_async.py`
Analyzes local binary input with `analyze_binary_inline` (available only in `2026-06-01-preview`). Same trade-offs as URL inline; supports `content_range` with an inline limit of at most 5 pages.

**Key concepts:**
- Choosing LRO vs binary inline analysis
- Supported inline analyzers (`prebuilt-digitalParse`, `prebuilt-read`, `prebuilt-layout`, and custom document analyzers without fields; not analyzers with figure analysis)
- Restricting pages with `content_range` within the 5-page inline limit
- Accessing `ContentAnalyzerInlineResponse.result`

## Advanced Samples

### Convert Result to LLM Input

#### `sample_to_llm_input.py` / `sample_to_llm_input_async.py`
Advanced usage of the `to_llm_input` helper for multi-modal content and output customization. For basic `to_llm_input` usage, see Samples 01, 03, and 05. For classification results, see Sample 05.

**Key concepts:**
- Output options: fields-only, markdown-only, custom metadata
- `AnalysisContent.metadata` (requires `2026-06-01-preview`) rendered under `metadata:`; caller `custom_metadata` nested under `customMetadata:`
- Multi-page PDF with `content_range` — page markers use original page numbers
- Multi-segment video — each segment rendered with time range
- Audio with `content_range` — analyzing a specific time window

**Example output** (`2026-06-01-preview` metadata PDF front matter):
```text
---
mimeType: application/pdf
metadata:
  author: Contoso Metadata Team
  contentType: application/pdf
  language: en-US
  pageCount: '1'
  title: Contoso Metadata Extraction Sample
pages: 1
---
```

### Analysis Diagnostics

**Requires:** `2026-06-01-preview`

#### `sample_analysis_diagnostics.py` / `sample_analysis_diagnostics_async.py`
Read diagnostic information returned with an analysis result via `AnalysisResult.infos`. Diagnostics are human-readable troubleshooting messages (not structured telemetry). The service currently emits an `LLMStats` code for completion/embedding call counts and latency; handle unknown codes as the set may grow.

**Key concepts:**
- Inspecting `AnalysisResult.infos` diagnostics after a completed analysis
- Human-readable diagnostic codes and messages
- Treating messages as unstable troubleshooting text (prefer OpenTelemetry for structured telemetry)

**Example output**:
```text
LLMStats: completion calls: 2; embedding calls: 1; avg completion latency: 5.75s; total completion latency: 11.50s; avg embedding latency: 0.94s; total embedding latency: 0.94s
```

### Classify In-Page Segments

**Requires:** `2026-06-01-preview`

#### `sample_classify_in_page_segments.py` / `sample_classify_in_page_segments_async.py`
Create a classifier that splits a single page into multiple classified document segments. Enable `allow_in_page_segments` with `enable_segment` when multiple documents share one page — for example supplemental statements appended after a K-1 tax form. See the [classifier overview](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/classifier). Segment `span`/`source` values locate each document within the page.

**Key concepts:**
- `ContentAnalyzerConfig.allow_in_page_segments` to enable in-page segmentation
- Multiple `DocumentContentSegment` results per page
- Using segment `span`/`source` to locate documents within a page

### Detect Signatures

**Requires:** `2026-06-01-preview`

#### `sample_detect_signatures.py` / `sample_detect_signatures_async.py`
Detect signatures in an image using the `prebuilt-layout` analyzer. Signatures appear in markdown as `![alt](signatures/{id})` image references, with matching `DocumentSignature.id` and optional role/span.

**Key concepts:**
- Reading `DocumentContent.signatures` (`DocumentSignature`)
- Mapping signature markdown references to `DocumentSignature` spans

### Extract Document Metadata

**Requires:** `2026-06-01-preview`

#### `sample_extract_document_metadata.py` / `sample_extract_document_metadata_async.py`
Extract embedded document metadata from PDF and DOCX files using the `prebuilt-layout` analyzer. Metadata is a string-to-string dictionary; enumerate keys and tolerate additions as support evolves.

**Key concepts:**
- Reading `DocumentContent.metadata`
- Optional PDF keys such as `author`, `contentType`, `language`, `pageCount`, `title`
- Additional DOCX keys such as `characterCount`, `lastModifiedBy`, `wordCount`

**Example output** (sample PDF):
```text
author: Contoso Metadata Team
contentType: application/pdf
language: en-US
pageCount: 1
title: Contoso Metadata Extraction Sample
createdAt: (not returned)
```

### Field Grounding Sources

#### `sample_content_source.py` / `sample_content_source_async.py`
Read grounding source strings from extracted fields via `ContentField.source`. In Python, sources are plain strings; use the source string formats documented in the samples to interpret document, image, audio, and visual locations.

**Key concepts:**
- Iterating fields and reading `ContentField.source`
- Multi-region sources separated by `;`
- Document (`D(...)`) and audio/visual (`AV(...)`) wire formats

### Rehydrate Long-Running Operations

#### `sample_rehydrate_operation.py` / `sample_rehydrate_operation_async.py`
Persist an analysis LRO with `poller.continuation_token()` and resume later with `begin_analyze(..., continuation_token=...)`. Useful for cross-process handoff and crash resilience.

**Key concepts:**
- Capturing `continuation_token()` before waiting for completion
- Persisting the token (file, queue, or database)
- Reconstructing the poller and calling `result()`

## Common Patterns

### Authentication

All samples support two authentication methods:

**Option 1: API Key (simpler)**
```python
from azure.core.credentials import AzureKeyCredential
credential = AzureKeyCredential(api_key)
```

**Option 2: DefaultAzureCredential (recommended)**
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
# Requires: az login
```

### Working with the Client

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient

client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

# Analyze a document
poller = client.begin_analyze(analyzer_id="prebuilt-documentSearch", inputs=[...])
result = poller.result()
```

### Working with Results

**Access markdown content:**
```python
result: AnalysisResult = poller.result()
content = result.contents[0]
print(content.markdown)
```

**Access structured fields:**
```python
# For prebuilt-invoice
content = result.contents[0]
customer_name = content.fields["CustomerName"].value
invoice_total = content.fields["TotalAmount"].value
```

**Access document properties:**
```python
if content.kind == AnalysisContentKind.DOCUMENT:
    doc_content: DocumentContent = content  # type: ignore
    print(f"Pages: {doc_content.start_page_number} - {doc_content.end_page_number}")
    for table in doc_content.tables:
        print(f"Table: {table.row_count} x {table.column_count}")
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'azure.ai.contentunderstanding'"

**Solution:** Make sure the virtual environment is activated and the SDK is installed:
```bash
source .venv/bin/activate
pip install -e .
```

### "ImportError: aiohttp package is not installed"

**Solution:** Install the development dependencies:
```bash
source .venv/bin/activate
pip install -r dev_requirements.txt
```

### "KeyError: 'CONTENTUNDERSTANDING_ENDPOINT'"

**Solution:** Create a `.env` file with your credentials (see [Setup](#setup)).

### "Could not load credentials from the environment"

**Solution:** Either set `CONTENTUNDERSTANDING_KEY` in `.env` or run `az login`.

### Import errors or type checking issues

**Solution:** Reinstall the SDK in the virtual environment:
```bash
source .venv/bin/activate
pip install -e . --force-reinstall
```

### "Model deployments not configured" or "prebuilt analyzers not available"

**Solution:** Run the setup sample to configure model deployments:
```bash
source .venv/bin/activate
cd samples
  python sample_update_defaults.py
```

This configures the required model deployments (for example gpt-5.2 and text-embedding-3-large, plus prebuilt aliases) that prebuilt analyzers depend on.

### "Access denied" or "authorization errors" when creating analyzers or configuring deployments

**Solution:** Ensure your credential has the 'Cognitive Services User' role assigned to your Microsoft Foundry resource. This role is required for operations like:
- Configuring model deployments (`sample_update_defaults.py`)
- Creating custom analyzers
- Cross-resource copying operations

You can assign this role in the Azure portal under your Microsoft Foundry resource's Access Control (IAM) section.

### "FileNotFoundError" when running samples with local files

**Solution:** Make sure you run samples that use local files from the `samples/` directory:
```bash
source .venv/bin/activate
cd samples
python sample_analyze_binary.py  # This will find sample_files/sample_invoice.pdf
```

If running from the package directory, use the full path:
```bash
source .venv/bin/activate
python samples/sample_analyze_binary.py  # Make sure you're in the package directory
```

## Next Steps

* Review the [Azure AI Content Understanding documentation][contentunderstanding_docs]
* Check the API reference for detailed API information
* See the main [README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md) for more getting started information

<!-- LINKS -->
[async_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/async_samples
[contentunderstanding_docs]: https://learn.microsoft.com/azure/ai-services/content-understanding/
[main_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md
[sample_update_defaults]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_update_defaults.py
