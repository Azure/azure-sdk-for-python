---
name: sdk-py-sample-run
description: Run a specific sample for the Azure AI Content Understanding SDK. Use when users want to run a particular sample like sample_analyze_url.py or sample_analyze_invoice.py.
---

# Run a Specific Sample

Run a specific sample from the Azure AI Content Understanding SDK.

> **[COPILOT INTERACTION MODEL]:** This skill is designed to be interactive. At each step marked with **[ASK USER]**, pause execution and prompt the user for input or confirmation before proceeding. Do NOT silently skip these prompts. Use the `ask_questions` tool when available.

## Prerequisites

- Python >= 3.9
- Virtual environment set up with SDK installed (see `sdk-py-setup` skill)
- Environment variables configured in `.env`
- For prebuilt analyzers: model deployments configured (run `sample_update_defaults.py` first)

> **[ASK USER] Prerequisites check:**
> Before proceeding, verify the user's environment:
> 1. "Have you already set up your Python environment and installed the SDK?" -- If no, direct them to the `sdk-py-setup` skill first.
> 2. "Have you configured your `.env` file with your endpoint and credentials?" -- If no, direct them to Step 4 of the `sdk-py-setup` skill.
> 3. "Have you run `sample_update_defaults.py` to configure model defaults?" -- If no and they want to use prebuilt analyzers, guide them to run it first.

## Package Directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Available Samples

All sync samples have async versions with `_async` suffix in `samples/async_samples/`.

### Getting Started (Run These First)

#### `sample_update_defaults` -- Required First!
**One-time setup** - Configures model deployment mappings (GPT-4.1, GPT-4.1-mini, text-embedding-3-large) for your Microsoft Foundry resource. Must run before using prebuilt analyzers.

#### `sample_analyze_url` -- Start Here!
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

> **[ASK USER] Confirm venv active:**
> Ask: "Is your virtual environment active? Run `which python` (or `where python` on Windows) and confirm it points to a path inside `.venv`."
> If the user reports it is not active or does not exist, direct them to the `sdk-py-setup` skill.

### Step 3: Choose and Run the Sample

> **[ASK USER] Which sample?:**
> Ask the user: "Which sample would you like to run?" with options:
> - `sample_analyze_url` -- Analyze content from a URL (recommended for first-time users)
> - `sample_analyze_binary` -- Analyze a local PDF/image file
> - `sample_analyze_invoice` -- Extract structured fields from an invoice
> - `sample_create_analyzer` -- Create a custom analyzer
> - `sample_update_defaults` -- Configure model defaults (one-time setup)
> - Other -- Let me see the full list
>
> If the user picks "Other", show the full Available Samples list above or run `.github/skills/sdk-py-sample-run/scripts/run_sample.sh --list`.

> **[ASK USER] Sync or async?:**
> Ask: "Would you like to run the **sync** or **async** version of this sample?"
> - Sync (default) -- Runs in `samples/`
> - Async -- Runs in `samples/async_samples/` with `_async` suffix

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

> **[ASK USER] Sample result:**
> After running the sample, ask: "Did the sample run successfully?"
> - If yes: "Would you like to run another sample, or are you all set?"
> - If no: Help troubleshoot using the Troubleshooting section below. Common issues include missing `.env` configuration, inactive venv, or model defaults not configured.

> **[ASK USER] Run another?:**
> If the user wants to run another sample, loop back to the "Which sample?" prompt above.

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
