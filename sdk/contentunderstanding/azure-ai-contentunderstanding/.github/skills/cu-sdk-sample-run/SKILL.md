---
name: cu-sdk-sample-run
description: Run a specific sample for the Azure AI Content Understanding SDK. Use when users want to run a particular sample like sample_analyze_url.py or sample_analyze_invoice.py.
---

# Run a Specific Sample

Run a specific sample from the Azure AI Content Understanding SDK.

> **[COPILOT INTERACTION MODEL]:** This skill is designed to be interactive. At each step marked with **[ASK USER]**, pause execution and prompt the user for input or confirmation before proceeding. Do NOT silently skip these prompts. Use the `ask_questions` tool when available.

## Prerequisites

- Python >= 3.9
- Virtual environment set up with SDK installed (see `cu-sdk-setup` skill)
- Environment variables configured in `.env`
- Model deployments configured via `sample_update_defaults.py` -- required for any sample that uses GPT-4.1 / text-embedding-3-large (prebuilt analyzers like `prebuilt-invoice`, custom analyzers with `extract` / `generate` / `classify` field methods, and `sample_create_analyzer_with_labels`)

> **[ASK USER] Prerequisites check (run BEFORE Step 1 of the Workflow below):**
> Before starting the numbered Workflow, verify the user's environment by asking these three questions in order. Do NOT skip Step 1 until each has a yes/handled answer:
> 1. "Have you already set up your Python environment and installed the SDK?" -- If no, direct them to the `cu-sdk-setup` skill first; pause this skill until that finishes.
> 2. "Have you configured your `.env` file with your endpoint and credentials?" -- If no, direct them to Step 4 of the `cu-sdk-setup` skill.
> 3. "Have you run `sample_update_defaults.py` to configure model defaults?" -- Defer judgement: ask once you know which sample they want (Step 3 below), then check it against the **"Samples that require `sample_update_defaults` first"** list in Step 4.

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

#### `sample_to_llm_input`
Advanced usage of the `to_llm_input` helper -- converts structured `AnalysisResult` into LLM-ready text (YAML front matter + markdown body).
- Key concepts: LLM integration, output options (fields-only, markdown-only, custom metadata), multi-segment video/audio rendering, page markers via `content_range`
- Python-only helper (not available in other language SDKs)

### Custom Analyzers

#### `sample_create_analyzer`
Creates custom analyzer with field schema for domain-specific extraction.
- Key concepts: Field types (string, number, date, object, array), extraction methods (extract, generate, classify)

#### `sample_create_classifier`
Creates classifier to categorize documents (Loan_Application, Invoice, Bank_Statement).
- Key concepts: Content categories, segmentation, document routing

#### `sample_create_analyzer_with_labels`
Builds analyzers with training labels (labeled data from Azure Blob Storage).
- Key concepts: Labeled data, knowledge sources, Blob Storage SAS URIs
- Requires additional env vars: `CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL` (Option A) **or** `CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT` + `CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER` (Option B)

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
> If the user reports it is not active or does not exist, direct them to the `cu-sdk-setup` skill.

### Step 3: Choose the Sample

Pick the sample (and sync/async variant) **before** configuring sample-specific settings -- subsequent `[ASK USER]` blocks in Step 4 are gated on the chosen sample.

> **[ASK USER] Which sample?:**
> If the user has already named a specific sample (e.g., "run sample_analyze_invoice"), confirm rather than re-prompt:
> "You want to run `<sample_name>`. Continuing with that -- correct? (Reply "no" to see the full list.)"
>
> If the user has not yet specified a sample, ask: "Which sample would you like to run?" with options:
> - `sample_analyze_url` -- Analyze content from a URL (recommended for first-time users)
> - `sample_analyze_binary` -- Analyze a local PDF/image file
> - `sample_analyze_invoice` -- Extract structured fields from an invoice
> - `sample_create_analyzer` -- Create a custom analyzer
> - `sample_create_analyzer_with_labels` -- Create a labeled-data analyzer (auto-uploads training data)
> - `sample_update_defaults` -- Configure model defaults (one-time setup)
> - Other -- Let me see the full list
>
> If the user picks "Other" (or replies "no" to the confirmation), show the full Available Samples list above or run the `--list` command (path note: from package root run `.github/skills/cu-sdk-sample-run/scripts/run_sample.sh --list`; from the workspace root prepend `sdk/contentunderstanding/azure-ai-contentunderstanding/`).

> **[ASK USER] Sync or async?:**
> Ask: "Would you like to run the **sync** or **async** version of this sample?"
> - Sync (default) -- Runs in `samples/`
> - Async -- Runs in `samples/async_samples/` with `_async` suffix

### Step 4: Configure Sample-Specific Settings (if needed)

Now that the chosen sample is known, run only the subsections below that apply to it. Each subsection's `[ASK USER]` block is already gated on the relevant sample(s); skip a subsection if it doesn't match. For full environment setup (creating `.venv`, installing the SDK, writing `.env`), use the **`cu-sdk-setup`** skill. The subsections below cover settings that are sample-specific and may not have been configured during the initial setup.

#### Samples that require `sample_update_defaults` first

These samples invoke an analyzer that depends on GPT-4.1 / GPT-4.1-mini / text-embedding-3-large model deployments. They will fail with a *model deployment not found* error unless `sample_update_defaults.py` has been run for the resource:

| Sample | Why |
|--------|-----|
| `sample_analyze_invoice` | `prebuilt-invoice` uses GPT-4.1 for field extraction |
| `sample_analyze_configs` | Advanced features (charts, formulas, etc.) use GPT-4.1 |
| `sample_create_analyzer` | Custom field schema with `extract` / `generate` / `classify` methods |
| `sample_create_classifier` | Document classification uses GPT-4.1 |
| `sample_create_analyzer_with_labels` | Labeled-data analyzer uses GPT-4.1 + text-embedding-3-large |

Samples that do **not** require `sample_update_defaults` (safe to run first): `sample_analyze_url`, `sample_analyze_binary`, `sample_analyze_return_raw_json`, `sample_to_llm_input`, all analyzer-management samples (`sample_get_*`, `sample_list_*`, `sample_update_analyzer`, `sample_delete_*`, `sample_copy_analyzer`, `sample_grant_copy_auth`).

> **[ASK USER] Model defaults check (only if chosen sample is in the table above):**
> Ask: "This sample requires model deployments to be configured. Have you already run `sample_update_defaults.py` for this Microsoft Foundry resource?"
> - **Yes** -- proceed.
> - **No** -- run it first: `cd samples && python sample_update_defaults.py` (only needed once per resource).
> - **Not sure** -- it's safe to re-run; the call is idempotent.

#### Settings by sample

| Setting | Required By | Description |
|---------|-------------|-------------|
| `CONTENTUNDERSTANDING_ENDPOINT` | **All samples** | Your Microsoft Foundry resource endpoint URL |
| `CONTENTUNDERSTANDING_KEY` | All samples (optional) | API key for key-based auth. If empty, `DefaultAzureCredential` is used (recommended -- run `az login` first) |
| `GPT_4_1_DEPLOYMENT` | sample_update_defaults | Deployment name for gpt-4.1 model (default: `gpt-4.1`) |
| `GPT_4_1_MINI_DEPLOYMENT` | sample_update_defaults | Deployment name for gpt-4.1-mini model (default: `gpt-4.1-mini`) |
| `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` | sample_update_defaults | Deployment name for text-embedding-3-large model (default: `text-embedding-3-large`) |
| `CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID` | sample_grant_copy_auth | Source ARM resource ID for cross-resource copy |
| `CONTENTUNDERSTANDING_SOURCE_REGION` | sample_grant_copy_auth | Source region (e.g., `eastus`) for cross-resource copy |
| `CONTENTUNDERSTANDING_TARGET_ENDPOINT` | sample_grant_copy_auth | Target Foundry resource endpoint for cross-resource copy |
| `CONTENTUNDERSTANDING_TARGET_RESOURCE_ID` | sample_grant_copy_auth | Target ARM resource ID for cross-resource copy |
| `CONTENTUNDERSTANDING_TARGET_REGION` | sample_grant_copy_auth | Target region (e.g., `swedencentral`) for cross-resource copy |
| `CONTENTUNDERSTANDING_TARGET_KEY` | sample_grant_copy_auth (optional) | Target API key. If empty, `DefaultAzureCredential` is used for the target resource |
| `CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL` | sample_create_analyzer_with_labels (Option A) | SAS URL of the Blob container holding labeled training data (List + Read permissions) |
| `CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT` | sample_create_analyzer_with_labels (Option B) | Storage account name for auto-upload via `DefaultAzureCredential` |
| `CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER` | sample_create_analyzer_with_labels (Option B) | Container name for auto-upload |
| `CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX` | sample_create_analyzer_with_labels (optional) | Virtual directory (prefix) within the container, e.g., `training_samples/` |

#### Setting up sample_create_analyzer_with_labels training data

`sample_create_analyzer_with_labels` needs labeled training data in an Azure Blob container. Two configurations are supported -- the sample auto-detects which one to use based on which env vars are set.

> **[ASK USER] Training data option (sample_create_analyzer_with_labels only):**
> If the user chose `sample_create_analyzer_with_labels`, ask:
> "How would you like to provide labeled training data?"
>
> - **Option A -- Pre-generated SAS URL (recommended for production):** You already have labeled files in a Blob container and a SAS URL with **Read + List** permissions.
>   - Set `CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL` in `.env` to the full URL (`https://<account>.blob.core.windows.net/<container>?sv=...&se=...`).
>
> - **Option B -- Auto-upload from local files (recommended for first-time users):** The sample will upload the bundled `samples/sample_files/training_samples/` (receipts + label JSON) to your container and generate a User Delegation SAS automatically.
>   - Set `CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT` and `CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER` in `.env`.
>   - Optionally set `CONTENTUNDERSTANDING_TRAINING_DATA_PREFIX` (e.g., `training_samples/`) to scope uploads to a virtual folder.
>   - Requires `DefaultAzureCredential` to have **Storage Blob Data Contributor** on the storage account (run `az login` first).
>
> If the user is unsure, recommend **Option B**. The next subsection (**"Samples that need a local file"**) only applies if Option B is chosen.
>
> **Do not set both options.** If both are configured, Option A (the SAS URL) takes precedence.

#### Samples that need a local file

The `sample_analyze_binary` and `sample_analyze_configs` samples load a local file from `samples/sample_files/`. The default file paths are built into the samples (`sample_files/sample_invoice.pdf` and `sample_files/sample_document_features.pdf` respectively). To use your own file, update the `file_path` variable in the sample code.

`sample_create_analyzer_with_labels` (Option B only) auto-uploads bundled labeled receipts from `samples/sample_files/training_samples/` (`receipt1.jpg`, `receipt1.jpg.labels.json`, `receipt2.jpg`, `receipt2.jpg.labels.json`, etc.) to the configured Blob container. To use your own labeled data, replace the files under `samples/sample_files/training_samples/` (keeping the `<image>.labels.json` naming convention) before running.

> **[ASK USER] Local file (if applicable):**
> If the user chose a sample that requires a local file (`sample_analyze_binary`, `sample_analyze_configs`, or `sample_create_analyzer_with_labels` **and** chose Option B in the previous subsection), ask:
> "This sample uses local files from `samples/sample_files/`. Would you like to:"
> - **Use the default test files** -- The sample has built-in paths under `samples/sample_files/`.
> - **Provide your own files** -- For `sample_analyze_binary` / `sample_analyze_configs`, update the `file_path` variable in the sample code. For `sample_create_analyzer_with_labels` (Option B), replace the files under `samples/sample_files/training_samples/`.

#### Setting up sample_grant_copy_auth cross-resource environment

The `sample_grant_copy_auth` sample requires **two separate Microsoft Foundry resources** (source and target).

Add the following to your `.env`:

```bash
# Source is your CONTENTUNDERSTANDING_ENDPOINT (already configured above)
CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID="/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.CognitiveServices/accounts/{sourceAccountName}"
CONTENTUNDERSTANDING_SOURCE_REGION="eastus"
CONTENTUNDERSTANDING_TARGET_ENDPOINT="https://your-target-foundry.services.ai.azure.com/"
CONTENTUNDERSTANDING_TARGET_RESOURCE_ID="/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.CognitiveServices/accounts/{targetAccountName}"
CONTENTUNDERSTANDING_TARGET_REGION="swedencentral"
```

> **[ASK USER] Cross-resource setup (sample_grant_copy_auth only):**
> If the user chose `sample_grant_copy_auth`, ask:
> 1. "Do you have **two separate Microsoft Foundry resources** (source and target) set up?" -- If no, guide them to create a second resource.
> 2. "Your `CONTENTUNDERSTANDING_ENDPOINT` will be used as the **source endpoint**. Please provide the following for your **source** resource:" -- Source ARM Resource ID, Source region.
> 3. "Please provide the following for your **target** resource:" -- Target endpoint URL, Target ARM Resource ID, Target region.
> 4. Confirm: "Cross-resource copy works with both `DefaultAzureCredential` and API keys. Both resources must have the **Cognitive Services User** role assigned if using `DefaultAzureCredential`. Is this configured?"

### Step 5: Run the Sample

**Run manually (recommended):**

```bash
# For sync samples
cd samples
python sample_analyze_url.py

# For async samples
cd samples/async_samples
python sample_analyze_url_async.py
```

**Or use the script:**

> **Path note:** All `run_sample.sh` invocations below assume the **package root** (`sdk/contentunderstanding/azure-ai-contentunderstanding`) as the current directory. From the workspace root, prepend `sdk/contentunderstanding/azure-ai-contentunderstanding/`. The script itself resolves paths relative to its own location, so the working directory only affects how you type the command.

```bash
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh <sample_name>
```

**Examples:**

```bash
# Run sync sample
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_url

# Run async sample
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_url_async

# With .py extension (also works)
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_invoice.py
```

### After the Sample Runs -- Review Results and Explain the Sample

After the sample completes, the skill **must** do the following for the user (do not skip):

1. **Show the terminal command to re-run this sample directly**, so the user can iterate without the skill. For example:

   ```bash
   cd samples && python sample_analyze_url.py
   # or for async samples:
   cd samples/async_samples && python sample_analyze_url_async.py
   ```

   Substitute `sample_analyze_url` with the sample the user just ran.

2. **Briefly explain the key code concepts** demonstrated in the sample. Tailor the explanation to the specific sample; common concepts include:
   - **Client creation** -- how the `ContentUnderstandingClient` (or `aio.ContentUnderstandingClient` for async) is constructed (endpoint + `DefaultAzureCredential` or `AzureKeyCredential`)
   - **Analyzer selection** -- which prebuilt (`prebuilt-documentSearch`, `prebuilt-invoice`, etc.) or custom analyzer is used and why
   - **Input type** -- URL vs. binary stream (`bytes`) vs. local file
   - **Result processing** -- how the returned `AnalyzeResult` is traversed (pages, fields, contents)
   - **Content type narrowing** -- e.g., narrowing `AnalyzedContent` to `AnalyzedDocumentContent` / `AnalyzedImageContent` / `AnalyzedAudioContent` / `AnalyzedVideoContent` (using `isinstance` or content `kind` discrimination)
   - **Long-running operations** -- if the sample uses `begin_analyze` and the returned `LROPoller` (or `AsyncLROPoller`)

   In addition to the generic concepts above, prefer the sample-specific highlights below when they apply:

   | Sample | Sample-specific concepts to call out |
   |--------|--------------------------------------|
   | `sample_analyze_url` | URL-based analysis, multi-modal content (document / image / audio / video), markdown output |
   | `sample_analyze_binary` | Reading local files as `bytes`, page properties, content type narrowing |
   | `sample_analyze_invoice` | `prebuilt-invoice` field schema, `Field` confidence scores, array fields (line items) |
   | `sample_analyze_configs` | `AnalysisConfig` options (charts, formulas, hyperlinks, annotations), Chart.js / LaTeX outputs |
   | `sample_analyze_return_raw_json` | Accessing the raw JSON via `cls=lambda pipeline_response, deserialized, _: pipeline_response.http_response.text()` -- bypassing the typed model |
   | `sample_to_llm_input` | `to_llm_input()` helper, output options (fields-only / markdown-only / metadata), `content_range` page markers |
   | `sample_update_defaults` | `update_defaults()` -- mapping model aliases to your deployment names; idempotent one-time setup |
   | `sample_create_analyzer` | `Analyzer` schema, field types, `extract` / `generate` / `classify` field methods |
   | `sample_create_classifier` | `ContentCategory` definitions, document segmentation, classification routing |
   | `sample_create_analyzer_with_labels` | `LabeledDataKnowledgeSource`, User Delegation SAS auto-generation (Option B), labeled receipts upload pattern, combining labeled data with `extract` / `generate` field methods |
   | `sample_get_analyzer` / `sample_list_analyzers` | Listing prebuilt + custom analyzers, paging |
   | `sample_update_analyzer` | Patching analyzer description / tags |
   | `sample_delete_analyzer` / `sample_delete_result` | Cleanup patterns; result auto-deletion after 24h |
   | `sample_copy_analyzer` | Same-resource copy via `begin_copy_analyzer` |
   | `sample_grant_copy_auth` | Cross-resource copy: `grant_copy_auth` on source + `begin_copy_analyzer` on target, `DefaultAzureCredential` with **Cognitive Services User** role |
   | `sample_get_result_file` | Operation IDs, retrieving generated keyframes from video analysis |

> **[ASK USER] Sample result:**
> Ask: "Did the sample run successfully?"
> - If yes: present the re-run command and the key-code explanation (above), then ask: "Would you like to run another sample, or are you all set?"
> - If no: help troubleshoot using the Troubleshooting section below. Common issues include missing `.env` configuration, inactive venv, or model defaults not configured.

> **[ASK USER] Run another?:**
> If the user wants to run another sample, loop back to the "Which sample?" prompt above.

## Quick Reference

### Most Common Samples for New Users

1. **First-time setup** (run once per Foundry resource):
   ```bash
   .github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_update_defaults
   ```

2. **Analyze a document from URL:**
   ```bash
   .github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_url
   ```

3. **Analyze a local PDF file:**
   ```bash
   .github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_binary
   ```

4. **Extract invoice fields:**
   ```bash
   .github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_invoice
   ```

### List Available Samples

```bash
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh --list
```

## Scripts

This skill includes a single helper script in the `scripts/` directory.

### `run_sample.sh` — Run a sample (activates `.venv` and loads `.env` automatically)

A convenience wrapper that activates the virtual environment, sources `.env`, and runs the sample. Detects sync and async variants automatically.

```bash
# Run a sync sample by name (with or without .py extension)
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_url
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_invoice.py

# Run an async sample
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh sample_analyze_url_async

# List all available samples (sync and async)
.github/skills/cu-sdk-sample-run/scripts/run_sample.sh --list
```

For environment setup (creating `.venv`, installing the SDK, writing `.env`), use the `cu-sdk-setup` skill's `setup_user_env.sh` / `setup_user_env.ps1` script.

## Troubleshooting

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: azure.ai.contentunderstanding` | Activate venv: `source .venv/bin/activate` then `pip install azure-ai-contentunderstanding` |
| `ImportError: aiohttp package is not installed` | Install dev dependencies: `pip install -r dev_requirements.txt` |
| `KeyError: 'CONTENTUNDERSTANDING_ENDPOINT'` | Create `.env` file with credentials (see `cu-sdk-setup` skill) |
| `KeyError` for any `CONTENTUNDERSTANDING_TRAINING_DATA_*` var (running `sample_create_analyzer_with_labels`) | Set **either** `CONTENTUNDERSTANDING_TRAINING_DATA_SAS_URL` (Option A) **or both** `CONTENTUNDERSTANDING_TRAINING_DATA_STORAGE_ACCOUNT` + `CONTENTUNDERSTANDING_TRAINING_DATA_CONTAINER` (Option B). See **"Setting up sample_create_analyzer_with_labels training data"** in Step 4. |
| `KeyError` for any `CONTENTUNDERSTANDING_TARGET_*` or `CONTENTUNDERSTANDING_SOURCE_*` var (running `sample_grant_copy_auth`) | Configure all six cross-resource env vars. See **"Setting up sample_grant_copy_auth cross-resource environment"** in Step 4. |
| `FileNotFoundError: sample_files/...` | Run samples from the `samples/` directory (or use `run_sample.sh`, which sets the working directory automatically). |
| `Access denied` or authorization errors (Foundry resource) | Ensure **Cognitive Services User** role is assigned; check API key or run `az login`. |
| `Access denied` on Blob (running `sample_create_analyzer_with_labels` Option B) | Assign **Storage Blob Data Contributor** to the `DefaultAzureCredential` principal on the storage account, then re-run `az login`. |
| `SAS signature invalid` / `AuthenticationFailed` (running `sample_create_analyzer_with_labels` Option A) | The SAS URL has expired or is missing **Read + List** permissions. Regenerate the SAS URL with both permissions. |
| `Model deployment not found` | The sample requires `sample_update_defaults.py` to be run first. See the **"Samples that require `sample_update_defaults` first"** table in Step 4. Then run: `cd samples && python sample_update_defaults.py`. |
| `Model deployment '<name>' not found` even after running `sample_update_defaults` | Your `GPT_4_1_DEPLOYMENT` / `GPT_4_1_MINI_DEPLOYMENT` / `TEXT_EMBEDDING_3_LARGE_DEPLOYMENT` env vars don't match the actual deployment names in your Foundry resource. Check the resource's deployments page and update `.env`. |

## Related Skills

- `cu-sdk-setup` - Set up environment for running samples
- `cu-sdk-common-knowledge` - Domain knowledge for Content Understanding concepts

## Additional Resources

- [Samples README](../../../samples/README.md) - Detailed sample descriptions with key concepts
- [SDK README](../../../README.md) - Full SDK documentation
- [Product Documentation](https://learn.microsoft.com/azure/ai-services/content-understanding/)
