---
page_type: sample
languages:
  - python
products:
  - azure
urlFragment: azure-ai-contentunderstanding-samples
---

# Azure AI Content Understanding client library for Python Samples

These code samples demonstrate common scenarios with the Azure AI Content Understanding client library.

**Note:** All samples in this folder use synchronous operations. For async samples, see the [`async_samples`](../async_samples) directory.

## Prerequisites

* Python 3.9 or later is required to use this package
* You need an [Azure subscription][azure_sub] and a [Microsoft Foundry resource][contentunderstanding_quickstart] to use this package.
* The Microsoft Foundry resource must be created in a [supported region][contentunderstanding_regions].
* **Required setup:** GPT-4.1, GPT-4.1-mini, and text-embedding-3-large models must be deployed in your Microsoft Foundry project and configured using `sample_configure_defaults.py` before using prebuilt analyzers.

## Setup

### Quick Start (Recommended)

```bash
# 1. Navigate to package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# 2. Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# .venv\Scripts\activate  # On Windows

# 3. Install SDK and all dependencies
pip install -e .
pip install -r dev_requirements.txt  # Includes aiohttp, pytest, python-dotenv, azure-identity

# 4. Set up environment variables
cd samples
cp ../env.sample .env
# Edit .env with your credentials

# 5. Configure model deployments (required for prebuilt analyzers)
python sample_configure_defaults.py

# 6. Run a sample
python sample_analyze_url.py
```

### Detailed Setup Instructions

#### 1. Activate the Virtual Environment

**This project uses a virtual environment. All samples MUST be run from the activated virtual environment.**

```bash
# From the package directory
cd sdk/contentunderstanding/azure-ai-contentunderstanding

# Activate virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows

# Verify activation
which python  # Should show: .../azure-ai-contentunderstanding/.venv/bin/python
```

#### 2. Install Dependencies

```bash
# Install the SDK in editable mode
pip install -e .

# Install development dependencies (includes aiohttp, pytest, python-dotenv, azure-identity)
pip install -r dev_requirements.txt
```

**Note:** All dependencies for running samples and tests are in `dev_requirements.txt`. This includes:
- `aiohttp` - Required for async operations
- `python-dotenv` - For loading `.env` files
- `azure-identity` - For `DefaultAzureCredential` authentication
- `pytest-xdist` - For parallel test execution

#### 3. Configure Environment Variables

```bash
# Navigate to samples directory
cd samples

# Copy the env.sample file
cp ../env.sample .env

# Edit .env file with your credentials
# Use your favorite editor (vim, nano, code, cursor, etc.)
```

Set the following in `.env`:
* `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` (required) - Your Microsoft Foundry resource endpoint
* `AZURE_CONTENT_UNDERSTANDING_KEY` (optional) - Your API key. If not set, `DefaultAzureCredential` will be used.
* `GPT_4_1_DEPLOYMENT` (required for sample_configure_defaults.py) - Your GPT-4.1 deployment name in Microsoft Foundry
* `GPT_4_1_MINI_DEPLOYMENT` (required for sample_configure_defaults.py) - Your GPT-4.1-mini deployment name in Microsoft Foundry
* `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` (required for sample_configure_defaults.py) - Your text-embedding-3-large deployment name in Microsoft Foundry

**Example `.env` file:**
```bash
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource.services.ai.azure.com/
AZURE_CONTENT_UNDERSTANDING_KEY=your-api-key-here  # Optional
GPT_4_1_DEPLOYMENT=your-gpt-4.1-deployment-name
GPT_4_1_MINI_DEPLOYMENT=your-gpt-4.1-mini-deployment-name
TEXT_EMBEDDING_3_LARGE_DEPLOYMENT=your-text-embedding-3-large-deployment-name
```

#### 4. Authenticate (if using DefaultAzureCredential)

If you're not using an API key, authenticate with Azure CLI:
```bash
az login
```

## Running the Samples

**Important:** Always run samples from the activated virtual environment!

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run a sample
python samples/sample_analyze_url.py
```

## Sample Files

### Sample 00: Configure Defaults

#### `sample_configure_defaults.py`
**Required setup!** Configures and retrieves default model deployment settings for your Content Understanding resource. This is a one-time setup before using prebuilt analyzers.

**Key concepts:**
- Setting up model deployment mappings (GPT-4.1, GPT-4.1-mini, text-embedding-3-large)
- Required before using prebuilt analyzers
- Retrieving current default settings

### Sample 01: Analyze Binary

#### `sample_analyze_binary.py`
Analyzes a PDF document from local binary data using `prebuilt-documentSearch`. Demonstrates how to read local files and extract markdown content.

**Key concepts:**
- Using `begin_analyze_binary` with binary input
- Reading local PDF files
- Extracting markdown content
- Accessing document properties (pages, dimensions)

### Sample 02: Analyze URL

#### `sample_analyze_url.py`
**Start here!** Analyzes a document from a remote URL using `prebuilt-documentSearch`. Shows basic document analysis and content extraction.

**Key concepts:**
- Using `begin_analyze` with URL input
- Extracting markdown content
- Working with the analysis result object model

### Sample 03: Analyze Invoice

#### `sample_analyze_invoice.py`
Extracts structured fields from invoices using `prebuilt-invoice` analyzer. Shows how to work with structured field extraction.

**Key concepts:**
- Using specialized prebuilt analyzers
- Extracting structured fields (customer name, totals, dates, line items)
- Working with field confidence scores and source locations
- Accessing object fields and array fields

### Sample 04: Create Analyzer

#### `sample_create_analyzer.py`
Creates a custom analyzer with field schema to extract structured data from documents.

**Key concepts:**
- Defining custom field schemas (string, number, date, object, array)
- Using extraction methods: `extract`, `generate`, `classify`
- Configuring analysis options (OCR, layout, formulas)
- Enabling source and confidence tracking

### Sample 05: Create Classifier

#### `sample_create_classifier.py`
Creates a classifier analyzer to categorize documents and demonstrates automatic segmentation.

**Key concepts:**
- Creating classifiers with content categories
- Document categorization (Loan_Application, Invoice, Bank_Statement)
- Enabling segmentation for multi-document files
- Processing classification results

### Sample 06: Get Analyzer

#### `sample_get_analyzer.py`
Retrieves information about analyzers, including prebuilt and custom analyzers.

**Key concepts:**
- Getting prebuilt analyzer details
- Getting custom analyzer details
- Dumping analyzer configuration as JSON

### Sample 07: List Analyzers

#### `sample_list_analyzers.py`
Lists all available analyzers in your Microsoft Foundry resource.

**Key concepts:**
- Listing prebuilt and custom analyzers
- Displaying analyzer summary and details
- Identifying analyzer types

### Sample 08: Update Analyzer

#### `sample_update_analyzer.py`
Updates an existing custom analyzer's description and tags.

**Key concepts:**
- Updating analyzer description
- Adding, updating, and removing tags
- Verifying analyzer updates

### Sample 09: Delete Analyzer

#### `sample_delete_analyzer.py`
Deletes a custom analyzer from your resource.

**Key concepts:**
- Creating a simple analyzer for deletion demo
- Deleting custom analyzers
- Understanding deletion limitations (prebuilt analyzers cannot be deleted)

### Sample 10: Analyze Configs

#### `sample_analyze_configs.py`
Extracts additional features from documents such as charts, hyperlinks, formulas, and annotations.

**Key concepts:**
- Using prebuilt-documentSearch with enhanced features
- Extracting chart figures
- Extracting hyperlinks
- Extracting mathematical formulas
- Extracting PDF annotations

### Sample 11: Analyze Return Raw JSON

#### `sample_analyze_return_raw_json.py`
Accesses the raw JSON response from analysis operations for custom processing.

**Key concepts:**
- Getting raw JSON response
- Saving analysis results to file
- Custom JSON processing

### Sample 12: Get Result File

#### `sample_get_result_file.py`
Retrieves result files (such as keyframe images) from video analysis operations.

**Key concepts:**
- Analyzing video content
- Extracting operation IDs
- Retrieving keyframe images
- Saving result files to disk

### Sample 13: Delete Result

#### `sample_delete_result.py`
Demonstrates analyzing a document and then deleting the analysis result.

**Key concepts:**
- Extracting operation IDs from analysis operations
- Deleting analysis results to manage storage
- Verifying result deletion
- Understanding result retention policies (24-hour auto-deletion)

### Sample 14: Copy Analyzer

#### `sample_copy_analyzer.py`
Copies an analyzer from source to target within the same resource.

**Key concepts:**
- Creating source analyzers
- Copying analyzers within the same resource
- Updating copied analyzers with new tags
- Use cases: testing, staging, production deployment

### Sample 15: Grant Copy Auth

#### `sample_grant_copy_auth.py`
Grants copy authorization and copies an analyzer from a source resource to a target resource (cross-resource copying).

**Key concepts:**
- Cross-resource copying between different Azure resources
- Granting copy authorization
- Resource migration and multi-region deployment
- Required environment variables for cross-resource operations

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
result: AnalyzeResult = poller.result()
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
if content.kind == MediaContentKind.DOCUMENT:
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

### "KeyError: 'AZURE_CONTENT_UNDERSTANDING_ENDPOINT'"

**Solution:** Create a `.env` file with your credentials (see Setup step 3).

### "Could not load credentials from the environment"

**Solution:** Either set `AZURE_CONTENT_UNDERSTANDING_KEY` in `.env` or run `az login`.

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
python sample_configure_defaults.py
```

This configures the required GPT-4.1, GPT-4.1-mini, and text-embedding-3-large model deployments that prebuilt analyzers depend on.

## Next Steps

* Review the [Azure AI Content Understanding documentation][contentunderstanding_docs]
* Check the [API reference][apiref] for detailed API information
* See the main [README](../README.md) for more getting started information

<!-- LINKS -->
[azure_sub]: https://azure.microsoft.com/free/
[contentunderstanding_docs]: https://learn.microsoft.com/azure/ai-services/content-understanding/
[contentunderstanding_quickstart]: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api
[contentunderstanding_regions]: https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support
[apiref]: https://learn.microsoft.com/python/api/azure-ai-contentunderstanding/

