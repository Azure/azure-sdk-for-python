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

**Note:** All samples use async operations for better performance and modern Python best practices.

## Prerequisites

* Python 3.9 or later is required to use this package
* You need an [Azure subscription][azure_sub] and an [Azure AI Foundry resource][contentunderstanding_quickstart] to use this package.
* The Azure AI Foundry resource must be created in a [supported region][contentunderstanding_regions].

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

# 5. Run a sample
python analyze_url.py
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
* `AZURE_CONTENT_UNDERSTANDING_ENDPOINT` (required) - Your Azure AI Foundry resource endpoint
* `AZURE_CONTENT_UNDERSTANDING_KEY` (optional) - Your API key. If not set, `DefaultAzureCredential` will be used.

**Example `.env` file:**
```bash
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://your-resource.services.ai.azure.com/
AZURE_CONTENT_UNDERSTANDING_KEY=your-api-key-here  # Optional
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
python samples/analyze_url.py
```

## Sample Files

### Getting Started Samples

#### `analyze_url.py` ⭐
**Start here!** Analyzes a document from a remote URL using `prebuilt-documentSearch`. Shows basic document analysis, content extraction, and object model navigation.

**Key concepts:**
- Using `begin_analyze` with URL input
- Extracting markdown content
- Accessing document pages and tables
- Working with the analysis result object model

#### `analyze_binary.py`
Analyzes a PDF document from local binary data using `prebuilt-documentSearch`. Demonstrates how to read local files and analyze them.

**Key concepts:**
- Using `begin_analyze_binary` with binary input
- Reading local PDF files
- Same content extraction as `analyze_url.py`

#### `analyze_url_prebuilt_invoice.py`
Extracts structured fields from invoices using `prebuilt-invoice` analyzer. Shows how to work with structured field extraction.

**Key concepts:**
- Using specialized prebuilt analyzers
- Extracting structured fields (customer name, totals, dates, line items)
- Working with field types (StringField, NumberField, ArrayField)
- Using the convenience `.value` property

### Advanced Analysis Samples

#### `analyze_binary_raw_json.py`
Shows how to access the raw JSON response before deserialization for debugging or custom processing.

#### `analyze_binary_features.py`
Demonstrates advanced features like figure analysis, chart extraction, and custom output options.

#### `compare_prebuilt_analyzers.py`
Compares results from different prebuilt analyzers (`prebuilt-document` vs `prebuilt-documentSearch`) to show differences.

#### `analyze_category_enable_segments.py`
Creates a custom analyzer with content categories for document classification and automatic page segmentation.

**Use case:** Multi-page documents with mixed content types (e.g., PDF with invoices and bank statements)

### Custom Analyzer Management

#### `create_or_replace.py`
Creates or replaces a custom analyzer with field schemas and analysis configuration.

#### `get_analyzer.py`
Retrieves analyzer configuration and details.

#### `list_analyzers.py`
Lists all available analyzers (prebuilt and custom).

#### `update_analyzer.py`
Updates an existing analyzer configuration.

#### `delete_analyzer.py`
Deletes a custom analyzer.

### Advanced Features

#### `build_custom_model_with_training.py`
Builds a custom analyzer using training data from Azure Blob Storage. Requires additional configuration (see `env.sample`).

#### `copy_analyzer.py`
Copies an analyzer from one location/region to another.

#### `get_result_file.py`
Downloads result files from analysis operations (e.g., extracted video keyframes).

### Utility

#### `sample_helper.py`
Helper functions for saving results and working with sample files.

#### `run_all_samples.py`
Runs all samples sequentially for testing. Stops on first error.

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
from azure.identity.aio import DefaultAzureCredential
credential = DefaultAzureCredential()
# Requires: az login
```

### Async Context Managers

All samples use async context managers for proper resource cleanup:

```python
async with ContentUnderstandingClient(endpoint, credential) as client:
    # Client automatically closed when exiting context
    poller = await client.begin_analyze(...)
    result = await poller.result()

# Clean up credential if using DefaultAzureCredential
if isinstance(credential, DefaultAzureCredential):
    await credential.close()
```

### Working with Results

**Access markdown content:**
```python
result: AnalyzeResult = await poller.result()
content: MediaContent = result.contents[0]
print(content.markdown)
```

**Access structured fields:**
```python
# For prebuilt-invoice
content: MediaContent = result.contents[0]
customer_name = content.fields["CustomerName"].value  # Using .value property
invoice_total = content.fields["InvoiceTotal"].value
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

