---
name: sdk-py-sample-run
description: Run a specific sample for the Azure AI Content Understanding SDK. Use when users want to run a particular sample like sample_analyze_url.py or sample_analyze_invoice.py.
---

# Run a Specific Sample

Run a specific sample from the Azure AI Content Understanding SDK.

## Prerequisites

- Python >= 3.9
- Virtual environment set up with SDK installed (see `sdk-py-setup` skill)
- Environment variables configured in `.env`
- For prebuilt analyzers: model deployments configured (run `sample_update_defaults.py` first)

## Package Directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Available Samples

All sync samples have async versions with `_async` suffix in `samples/async_samples/`.

### Getting Started (Run These First)

#### `sample_update_defaults` ⭐ Required First!
**One-time setup** - Configures model deployment mappings (GPT-4.1, GPT-4.1-mini, text-embedding-3-large) for your Microsoft Foundry resource. Must run before using prebuilt analyzers.

#### `sample_analyze_url` ⭐ Start Here!
Analyzes content from a URL using `prebuilt-documentSearch`. Works with documents, images, audio, and video.
- Key concepts: URL input, markdown extraction, multi-modal content

#### `sample_analyze_binary`
Analyzes local PDF/image files using `prebuilt-documentSearch`.
- Key concepts: Binary input, local file reading, page properties

### Document Analysis

#### `sample_analyze_invoice`
Extracts structured fields from invoices using `prebuilt-invoice`.
- Key concepts: Field extraction (customer name, totals, dates, line items), confidence scores, array fields

#### `sample_analyze_configs`
Extracts advanced features: charts, hyperlinks, formulas, annotations.
- Key concepts: Chart.js output, LaTeX formulas, PDF annotations, enhanced analysis options

#### `sample_analyze_return_raw_json`
Gets raw JSON response for custom processing.
- Key concepts: Raw response access, saving to file, debugging

### Custom Analyzers

#### `sample_create_analyzer`
Creates custom analyzer with field schema for domain-specific extraction.
- Key concepts: Field types (string, number, date, object, array), extraction methods (extract, generate, classify)

#### `sample_create_classifier`
Creates classifier to categorize documents (Loan_Application, Invoice, Bank_Statement).
- Key concepts: Content categories, segmentation, document routing

### Analyzer Management

#### `sample_get_analyzer`
Retrieves analyzer details and configuration.

#### `sample_list_analyzers`
Lists all available analyzers (prebuilt and custom).

#### `sample_update_analyzer`
Updates analyzer description and tags.

#### `sample_delete_analyzer`
Deletes a custom analyzer.

#### `sample_copy_analyzer`
Copies analyzer within the same resource.

#### `sample_grant_copy_auth`
Cross-resource copying between different Azure resources/regions.
- Requires additional env vars: `CONTENTUNDERSTANDING_TARGET_ENDPOINT`, `CONTENTUNDERSTANDING_TARGET_RESOURCE_ID`

### Result Management

#### `sample_get_result_file`
Retrieves keyframe images from video analysis.
- Key concepts: Operation IDs, extracting generated files

#### `sample_delete_result`
Deletes analysis results for data cleanup.
- Key concepts: Result retention (24-hour auto-deletion), compliance

## Workflow

### Step 1: Navigate to Package Directory

```bash
cd sdk/contentunderstanding/azure-ai-contentunderstanding
```

### Step 2: Activate Virtual Environment

```bash
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### Step 3: Run the Sample

**Using the script (recommended):**

```bash
.github/skills/sdk-py-sample-run/scripts/run_sample.sh <sample_name>
```

**Examples:**

```bash
# Run sync sample
.github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_url

# Run async sample
.github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_url_async

# With .py extension (also works)
.github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_invoice.py
```

**Or run manually:**

```bash
# For sync samples
cd samples
python sample_analyze_url.py

# For async samples
cd samples/async_samples
python sample_analyze_url_async.py
```

## Quick Reference

### Most Common Samples for New Users

1. **First-time setup** (run once per Foundry resource):
   ```bash
   .github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_update_defaults
   ```

2. **Analyze a document from URL:**
   ```bash
   .github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_url
   ```

3. **Analyze a local PDF file:**
   ```bash
   .github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_binary
   ```

4. **Extract invoice fields:**
   ```bash
   .github/skills/sdk-py-sample-run/scripts/run_sample.sh sample_analyze_invoice
   ```

### List Available Samples

```bash
.github/skills/sdk-py-sample-run/scripts/run_sample.sh --list
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: azure.ai.contentunderstanding` | Activate venv: `source .venv/bin/activate` then `pip install azure-ai-contentunderstanding` |
| `ImportError: aiohttp package is not installed` | Install dev dependencies: `pip install -r dev_requirements.txt` |
| `KeyError: 'CONTENTUNDERSTANDING_ENDPOINT'` | Create `.env` file with credentials (see `sdk-py-setup` skill) |
| `FileNotFoundError: sample_files/...` | Run samples from the `samples/` directory |
| `Access denied` or authorization errors | Ensure **Cognitive Services User** role is assigned; check API key or run `az login` |
| `Model deployment not found` | Run `sample_update_defaults.py` first to configure model mappings |

## Related Skills

- `sdk-py-setup` - Set up environment for running samples
- `sdkinternal-py-sample-run` - Run all samples at once

## Additional Resources

- [Samples README](../../../samples/README.md) - Detailed sample descriptions with key concepts
- [SDK README](../../../README.md) - Full SDK documentation
- [Product Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
