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

To run the samples for this package, please follow the setup instructions in [Step 3: Configure model deployments][main_readme_setup] to configure with the necessary dependencies, environment variables, and model mappings required for the samples.

## Sample Files

### Sample 00: Configure Defaults

#### `sample_update_defaults.py` / `sample_update_defaults_async.py`
**Required setup!** Configures and retrieves default model deployment settings for your Microsoft Foundry resource. This is a required one-time setup per Microsoft Foundry resource before using prebuilt or custom analyzers.

**Key concepts:**
- Setting up model deployment mappings (GPT-4.1, GPT-4.1-mini, text-embedding-3-large)
- Required before using prebuilt analyzers
- Retrieving current default settings

### Sample 01: Analyze Binary

#### `sample_analyze_binary.py` / `sample_analyze_binary_async.py`
Analyzes a PDF document from local binary data using `prebuilt-documentSearch`. Demonstrates how to read local files and extract markdown content.

**Key concepts:**
- Using `begin_analyze_binary` with binary input
- Reading local PDF files
- Extracting markdown content
- Accessing document properties (pages, dimensions)

### Sample 02: Analyze URL

#### `sample_analyze_url.py` / `sample_analyze_url_async.py`
**Start here!** Analyzes a document from a remote URL using `prebuilt-documentSearch`. Shows basic document analysis and content extraction across modalities (documents, images, audio, video).

**Key concepts:**
- Using `begin_analyze` with URL input
- Extracting markdown content
- Working with the analysis result object model
- Analyzing different content types (documents, images, audio, video)

### Sample 03: Analyze Invoice

#### `sample_analyze_invoice.py` / `sample_analyze_invoice_async.py`
Extracts structured fields from invoices using `prebuilt-invoice` analyzer. Shows how to work with structured field extraction from domain-specific prebuilt analyzers.

**Key concepts:**
- Using specialized prebuilt analyzers (prebuilt-invoice)
- Extracting structured fields (customer name, totals, dates, line items)
- Working with field confidence scores and source locations
- Accessing object fields and array fields
- Financial document processing (invoices, receipts, credit cards, bank statements, checks)

### Sample 04: Create Analyzer

#### `sample_create_analyzer.py` / `sample_create_analyzer_async.py`
Creates a custom analyzer with field schema to extract structured data from documents. Shows how to define custom fields and extraction methods for document, audio, video, and image content.

**Key concepts:**
- Defining custom field schemas (string, number, date, object, array)
- Using extraction methods: `extract`, `generate`, `classify`
- Configuring analysis options (OCR, layout, formulas)
- Enabling source and confidence tracking
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
Extracts additional features from documents such as charts, hyperlinks, formulas, and annotations. Shows advanced document analysis capabilities.

**Key concepts:**
- Using prebuilt-documentSearch with enhanced features
- Extracting chart figures (Chart.js format)
- Extracting hyperlinks
- Extracting mathematical formulas (LaTeX)
- Extracting PDF annotations
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

### "KeyError: 'CONTENTUNDERSTANDING_ENDPOINT'"

**Solution:** Create a `.env` file with your credentials (see [Setup step 3][main_readme_setup]).

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

This configures the required GPT-4.1, GPT-4.1-mini, and text-embedding-3-large model deployments that prebuilt analyzers depend on.

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
[main_readme_setup]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md#step-3-configure-model-deployments-required-for-prebuilt-analyzers
