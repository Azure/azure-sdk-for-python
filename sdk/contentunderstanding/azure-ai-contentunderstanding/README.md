# Azure AI Content Understanding client library for Python

Azure AI Content Understanding is a multimodal AI service that extracts semantic content from documents, video, audio, and image files. It transforms unstructured content into structured, machine-readable data optimized for retrieval-augmented generation (RAG) and automated workflows.

Use the client library for Azure AI Content Understanding to:

* **Extract document content** - Extract text, tables, figures, layout information, and structured markdown from documents (PDF, images with text or hand-written text, Office documents and more)
* **Transcribe and analyze audio** - Convert audio content into searchable transcripts with speaker diarization and timing information
* **Analyze video content** - Extract visual frames, transcribe audio tracks, and generate structured summaries from video files
* **Leverage prebuilt analyzers** - Use production-ready prebuilt analyzers across industries including finance and tax (invoices, receipts, tax forms), identity verification (passports, driver's licenses), mortgage and lending (loan applications, appraisals), procurement and contracts (purchase orders, agreements), and utilities (billing statements)
* **Create custom analyzers** - Build domain-specific analyzers for specialized content extraction needs across all four modalities (documents, video, audio, and images)
* **Classify documents and video** - Automatically categorize and extract information from documents and video by type

If you have encountered issues or want to suggest features, please [file an issue][file_issue].

[Source code][python_cu_src] | [Package (PyPI)][python_cu_pypi] | [Product documentation][python_cu_product_docs] | [Samples][python_cu_samples] | [Changelog][changelog]

## Table of Contents

- [Getting started](#getting-started)
  - [Install the package](#install-the-package)
  - [Prerequisites](#prerequisites)
  - [Configuring Microsoft Foundry resource](#configuring-microsoft-foundry-resource)
  - [Service API versions](#service-api-versions)
  - [Authenticate the client](#authenticate-the-client)
- [Key concepts](#key-concepts)
  - [Prebuilt analyzers](#prebuilt-analyzers)
  - [Custom analyzers](#custom-analyzers)
  - [Content types](#content-types)
  - [Analysis patterns (long-running operation and inline)](#analysis-patterns-long-running-operation-and-inline)
  - [Main classes](#main-classes)
  - [Thread safety](#thread-safety)
  - [Additional concepts](#additional-concepts)
- [Examples](#examples)
  - [Running the samples](#running-the-samples)
  - [Convert results to LLM-ready text](#convert-results-to-llm-ready-text)
- [Troubleshooting](#troubleshooting)
  - [Common issues](#common-issues)
  - [Enable logging](#enable-logging)
- [Next steps](#next-steps)
- [Contributing](#contributing)

## Getting started

### Install the package

Python 3.10 or later is required to use this package.

Install the client library for Python with [pip][pip].

**Stable (GA) package** — supports service API `2025-11-01` only:

```bash
python -m pip install azure-ai-contentunderstanding
```

**Preview / beta package** — required for `2026-06-01-preview` capabilities documented below (inline analysis, semantic chunking, analyzer workflows, and related APIs). Install a pre-release build:

```bash
python -m pip install --pre azure-ai-contentunderstanding
```

Without `--pre`, `pip` installs the latest stable release (currently `1.1.0`), which does not include preview service APIs.

**If running async APIs:** The async transport is designed to be opt-in. The [aiohttp][aiohttp] framework is one of the supported implementations of async transport. It's not installed by default. You need to install it separately as follows: `pip install aiohttp`

### Prerequisites

* An [Azure subscription][azure_sub].
* A **Microsoft Foundry resource** to use this package.

### Configuring Microsoft Foundry resource

Before using the Content Understanding SDK, you need to set up a Microsoft Foundry resource and deploy supported generative models. The service periodically adds support for more models, including the latest gpt-5.x models such as gpt-5.2, gpt-5.4-mini, gpt-5.5, and others. The examples in this README use **gpt-5.2** and **text-embedding-3-large**.

- Current supported and deprecated models: [Supported generative models][supported_generative_models]
- Models being retired: [Foundry model retirement schedule][model_retirement_schedule]
- Deployment guidance: [Content Understanding model deployments guidance][cu_models_deployments]

#### Step 1: Create Microsoft Foundry resource

> **Important:** You must create your Microsoft Foundry resource in a region that supports Content Understanding. For a list of available regions, see [Azure Content Understanding region and language support][cu_region_support].

1. Follow the steps in the [Azure Content Understanding quickstart][cu_quickstart] to create a Microsoft Foundry resource in the Azure portal
2. Get your Foundry resource's endpoint URL from Azure Portal:
   - Go to [Azure Portal][azure_portal]
   - Navigate to your Microsoft Foundry resource
   - Go to **Resource Management** > **Keys and Endpoint**
   - Copy the **Endpoint** URL (typically `https://<your-resource-name>.services.ai.azure.com/`)

**Important: Grant Required Permissions**

After creating your Microsoft Foundry resource, you must grant yourself the **Cognitive Services User** role to enable API calls for setting default model deployments:

1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Access Control (IAM)** in the left menu
4. Click **Add** > **Add role assignment**
5. Select the **Cognitive Services User** role
6. Assign it to yourself (or the user/service principal that will run the application)

> **Note:** This role assignment is required even if you are the owner of the resource. Without this role, you will not be able to call the Content Understanding API to configure model deployments for prebuilt analyzers and custom analyzers.

#### Step 2: Deploy supported models

**Important:** Prebuilt and custom analyzers require generative model deployments. Deploy models that Content Understanding currently supports; the supported set grows over time (for example, gpt-5.x models such as gpt-5.2, gpt-5.4-mini, and gpt-5.5). This README uses the following examples:
- **gpt-5.2**
- **text-embedding-3-large**

See [Supported generative models][supported_generative_models] for the current list, including models being deprecated.

For current setup guidance, see the [Azure Content Understanding quickstart][cu_quickstart]. To deploy a model, follow [Create model deployments in Microsoft Foundry portal][deploy_models_docs]. In the portal:

1. In Microsoft Foundry, go to **Deployments** > **Deploy model** > **Deploy base model**
2. Search for and select a [supported generative model][supported_generative_models] (this guide uses `gpt-5.2` and `text-embedding-3-large` as examples)
3. Complete the deployment with your preferred settings
4. Note the deployment name you chose (for example, `my-completion-deployment`). Deployment names are user-defined and do not need to match model names. You'll need the name in Step 3 when configuring model deployments.

Repeat this process for each model your analyzers need.

> **Note on model retirement:** Azure OpenAI / Foundry models are subject to a [model retirement schedule][model_retirement_schedule]. When a model is retired, redeploy to a still-supported model and update your Content Understanding defaults. Review the retirement schedule regularly so you can plan migrations before support ends.

#### Step 3: Configure model deployments (required for prebuilt analyzers)

> **IMPORTANT:**  This is a **one-time setup per Microsoft Foundry resource** that maps your deployed models to those required by the prebuilt analyzers and custom models. If you have multiple Microsoft Foundry resources, you need to configure each one separately.

You need to configure the default model mappings in your Microsoft Foundry resource. This can be done programmatically using the SDK. The configuration maps your deployed models (for example, gpt-5.2 and text-embedding-3-large) to the model names and aliases required by prebuilt analyzers.

Prebuilt analyzers reference model aliases in addition to concrete model names. Most prebuilt analyzers, including `prebuilt-invoice`, use `prebuilt-analyzer-completion`; `prebuilt-*Search` analyzers use `prebuilt-analyzer-completion-mini`; and analyzers requiring embeddings use `prebuilt-analyzer-embedding`. Configure all three aliases even when they map to the same deployments as your example models. See [Supported generative models][supported_generative_models] and [Content Understanding model deployments guidance][cu_models_deployments] for current requirements.

To configure model deployments using code, see [`sample_update_defaults.py`][sample_update_defaults] for a complete example. The sample shows how to:
- Map your deployed models to the models required by prebuilt analyzers
- Retrieve the current default model deployment configuration

For environment setup (virtual environment, `.env`, and deployment name variables) before running that sample, see the [samples README][sample_readme].

### Service API versions

Each SDK release of `azure-ai-contentunderstanding` targets a default Azure Content Understanding service API version:

| SDK version | Supported service API versions | Default service API version |
|-------------|--------------------------------|-----------------------------|
| `1.1.0` | `2025-11-01` | `2025-11-01` |
| `1.2.0b3` | `2025-11-01`, `2026-06-01-preview` | `2026-06-01-preview` |

**To use the latest GA service**, install the latest GA SDK version (`1.1.0`); to use the latest preview capabilities, install the latest preview SDK version (`1.2.0b3`) instead — see [Install the package](#install-the-package). Either way, create the client without specifying `api_version` to use your installed version's default:

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

client = ContentUnderstandingClient(endpoint=endpoint, credential=DefaultAzureCredential())
```

**To pin a specific service API version**, SDK versions that support more than one service API version (such as `1.2.0b3`) accept an explicit `api_version` keyword. For example, to keep using GA service behavior from the preview package:

```python
client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
    api_version="2025-11-01",
)
```

> **Note:** For capabilities introduced in `2026-06-01-preview`, see the [changelog][changelog].

### Authenticate the client

In order to interact with the Content Understanding service, you'll need to create an instance of the `ContentUnderstandingClient` class. To authenticate the client, you need your Microsoft Foundry resource endpoint and credentials. You can use either an API key or Microsoft Entra ID authentication.

#### Using DefaultAzureCredential

The simplest way to authenticate is using `DefaultAzureCredential`, which supports multiple authentication methods and works well in both local development and production environments. Install the identity package separately (`pip install azure-identity`); it is not a dependency of `azure-ai-contentunderstanding`.

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()
client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
# To pin a version explicitly, pass api_version="2026-06-01-preview"
# (or "2025-11-01" for GA). See "Service API versions" above.
```

For async operations:

```python
import os
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.identity.aio import DefaultAzureCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
credential = DefaultAzureCredential()
client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
# To pin a version explicitly, pass api_version="2026-06-01-preview"
# (or "2025-11-01" for GA). See "Service API versions" above.
```

#### Using API key

You can also authenticate using an API key from your Microsoft Foundry resource:

```python
import os
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
api_key = os.environ["CONTENTUNDERSTANDING_KEY"]
client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
```

> **⚠️ Security Warning**: API key authentication is less secure and is only recommended for testing purposes with test resources. For production, use `DefaultAzureCredential` or other secure authentication methods.

To get your API key:
1. Go to [Azure Portal][azure_portal]
2. Navigate to your Microsoft Foundry resource
3. Go to **Resource Management** > **Keys and Endpoint**
4. Copy one of the **Keys** (Key1 or Key2)

For more information on authentication, see [Azure Identity client library][azure_identity_readme].

## Key concepts

### Prebuilt analyzers

Content Understanding provides a rich set of prebuilt analyzers that are ready to use without any configuration. These analyzers are powered by knowledge bases of thousands of real-world document examples, enabling them to understand document structure and adapt to variations in format and content.

Prebuilt analyzers are organized into several categories:

* **RAG analyzers** - Optimized for retrieval-augmented generation scenarios with semantic analysis and markdown extraction. These analyzers return markdown and a one-paragraph `Summary` for each content item:
  * **`prebuilt-documentSearch`** - Extracts content from documents (PDF, images, Office documents) with layout preservation, table detection, figure analysis, and structured markdown output. Optimized for RAG scenarios.
  * **`prebuilt-imageSearch`** - Analyzes standalone images and returns a one-paragraph description of the image content. Optimized for image understanding and search scenarios. For images that contain text (including hand-written text), use `prebuilt-documentSearch`.
  * **`prebuilt-audioSearch`** - Transcribes audio content with speaker diarization, timing information, and conversation summaries. Supports multilingual transcription.
  * **`prebuilt-videoSearch`** - Analyzes video content with visual frame extraction, audio transcription, and structured summaries. Provides temporal alignment of visual and audio content and can return multiple segments per video.
* **Content extraction analyzers** - Focus on OCR and layout analysis (e.g., `prebuilt-read`, `prebuilt-layout`)
* **Base analyzers** - Fundamental content processing capabilities used as parent analyzers for custom analyzers (e.g., `prebuilt-document`, `prebuilt-image`, `prebuilt-audio`, `prebuilt-video`)
* **Domain-specific analyzers** - Preconfigured analyzers for common document categories including financial documents (invoices, receipts, bank statements), identity documents (passports, driver's licenses), tax forms, mortgage documents, and contracts
* **Utility analyzers** - Specialized tools for schema generation and field extraction (e.g., `prebuilt-documentFieldSchema`, `prebuilt-documentFields`)

For a complete list of available prebuilt analyzers and their capabilities, see the [Prebuilt analyzers documentation][cu_prebuilt_analyzers].

### Custom analyzers

You can create custom analyzers with specific field schemas for multi-modal content processing (documents, images, audio, video). Custom analyzers allow you to extract domain-specific information tailored to your use case across all four modalities (documents, video, audio, and images).

### Content types

The API returns different content types based on the input. Both `DocumentContent` and `AudioVisualContent` classes derive from `AnalysisContent` class, which provides basic information and markdown representation. Each derived class provides additional properties to access detailed information:

* **`DocumentContent`** - For document files (PDF, HTML, images, Office documents such as Word, Excel, PowerPoint, and more). Provides basic information such as page count and MIME type. Retrieve detailed information including pages, tables, figures, paragraphs, and many others.
* **`AudioVisualContent`** - For audio and video files. Provides basic information such as timing information (start/end times) and frame dimensions (for video). Retrieve detailed information including transcript phrases, timing information, and for video, key frame references and more.

### Analysis patterns (long-running operation and inline)

Content Understanding supports two analysis patterns:

**Long-running operations (LRO)** — `begin_analyze` / `begin_analyze_binary` (all supported service API versions):

1. **Begin analysis** — Start the operation (returns immediately with an operation location)
2. **Poll for results** — Poll until the analysis completes
3. **Process results** — Read the structured `AnalysisResult`

The SDK returns an `LROPoller` that handles polling when you call `.result()`. The poller also exposes `operation_id` for use with `get_result_file*` and `delete_result*`. Prefer LRO for larger inputs, broader analyzer coverage, and when you need results retained (up to 24 hours, or until you delete them).

**Inline analysis** — `analyze_inline` / `analyze_binary_inline` (`2026-06-01-preview` only):

- Returns a `ContentAnalyzerInlineResponse` in a single HTTP response (no polling); use `.result` for the `AnalysisResult`
- See the [inline samples][sample_analyze_inline] for limits, supported analyzers, failure behavior, and usage details

### Main classes

* **`ContentUnderstandingClient`** - The main client for analyzing content, as well as creating, managing, and configuring analyzers
* **`AnalysisResult`** - Contains the structured results of an analysis operation, including content elements, markdown, and metadata

### Thread safety

We guarantee that all client instance methods are thread-safe and independent of each other. This ensures that the recommendation of reusing client instances is always safe, even across threads.

### Additional concepts

[Client options][client_options] |
[Handling failures][handling_failures] |
[Diagnostics][diagnostics]

## Examples

You can familiarize yourself with different APIs using [Samples][python_cu_samples].

The samples demonstrate:

* **Configuration** - Configure model deployment defaults for prebuilt analyzers and custom analyzers
* **Document Content Extraction** - Extract structured markdown content from PDFs and images using `prebuilt-documentSearch`, optimized for RAG (Retrieval-Augmented Generation) applications
* **Multi-Modal Content Analysis** - Analyze content from URLs across all modalities: extract markdown and summaries from documents, images, audio, and video using `prebuilt-documentSearch`, `prebuilt-imageSearch`, `prebuilt-audioSearch`, and `prebuilt-videoSearch`
* **Domain-Specific Analysis** - Extract structured fields from invoices using `prebuilt-invoice`
* **LLM Integration** - Convert analysis results to LLM-ready text with `to_llm_input()`
* **Advanced Document Features** - Extract charts, hyperlinks, formulas, and annotations from documents
* **Custom Analyzers** - Create custom analyzers with field schemas for specialized extraction needs
* **Document Classification** - Create and use classifiers to categorize documents
* **Preview capabilities** - See the [changelog][changelog] for features introduced in `2026-06-01-preview`
* **Analyzer Management** - Get, list, update, copy, and delete analyzers
* **Labeled Training Data** - Create custom analyzers with labeled training data from Azure Blob Storage for improved extraction accuracy
* **Result Management** - Retrieve result files from video analysis and delete analysis results

See the [samples README][sample_readme] for introductions of samples and the [samples directory][python_cu_samples] for complete examples.

### Running the samples

Before running samples, complete the Microsoft Foundry resource and model deployment steps in this README, then follow the environment setup in the [samples README][sample_readme] (virtual environment, dependencies, and environment variables).

**Important:** Always run samples from the activated virtual environment!

#### Running sync samples

Sync samples are in the `samples/` directory. We recommend running them from the `samples/` directory to ensure relative paths (for local files and `.env` configuration) resolve correctly:

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

#### Running async samples

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

### Convert results to LLM-ready text

> **Note:** `to_llm_input()` is currently in preview and may change in future
> releases. We welcome feedback — please [file an issue][file_issue].

Use the `to_llm_input()` helper to convert any analysis result into a text format that LLMs
can consume directly — YAML front matter with extracted fields followed by the markdown body.
This works with all content types (documents, images, audio, video) and handles multi-segment
results and classification hierarchies automatically.

```python
from azure.ai.contentunderstanding import ContentUnderstandingClient, to_llm_input
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.identity import DefaultAzureCredential

client = ContentUnderstandingClient(endpoint, DefaultAzureCredential())

# Analyze a document with text, tables, and charts using prebuilt-documentSearch (CU's primary RAG analyzer)
# Run from the samples/ directory so this relative path resolves.
with open("sample_files/sample_document_features.pdf", "rb") as f:
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=f.read(),
    )
result = poller.result()

# One line to get LLM-ready text
text = to_llm_input(result)
print(text)
# Output:
#   ---
#   mimeType: application/pdf
#   pages: 1
#   fields:
#     Summary: The document provides an overview of Latin, includes a sample
#       table with names and corporate affiliations, presents a bar chart
#       figure illustrating monthly values, and describes the AI Document
#       Intelligence service...
#   ---
#   <!-- InputPageNumber: 1 -->
#   # ==This is title==
#   ## 1. Text
#   [Latin](https://en.wikipedia.org/wiki/Latin) refers to an ancient Italic language...
#   ## 2. Page Objects
#   ### 2.1 Table
#   <table><caption>Table 1: This is a dummy table</caption>...</table>
#   ### 2.2. Figure
#   ![Values...](figures/1.1 "Bar chart with six bars: Jan=200, Feb=300...")
#   ...
```

> **About `<!-- InputPageNumber: N -->`**
>
> The helper emits `<!-- InputPageNumber: N -->` markers at page boundaries in
> the markdown body. `N` is the **original 1-based page number from the source
> document** (i.e., the page index in the analyzed PDF), not a counter that
> restarts at 1 for each call. Downstream consumers (RAG indexers, page-citation
> prompts) can rely on the marker value to cite the correct source page even
> when only a subset of pages was analyzed.
>
> **Why this matters when a page range is specified**
>
> Use `content_range` on the analyze input to analyze only a subset of pages in
> a multi-page document. The markers in the rendered output preserve the
> original page identity:
>
> ```python
> # Analyze pages 2-3 and page 5 of a 10-page PDF.
> poller = client.begin_analyze(
>     analyzer_id="prebuilt-documentSearch",
>     inputs=[AnalysisInput(url=multi_page_url, content_range="2-3,5")],
> )
> result = poller.result()
> text = to_llm_input(result)
> # Output contains markers for the *original* page numbers, not 1, 2, 3:
> #   pages: 2-3, 5
> #   ...
> #   <!-- InputPageNumber: 2 -->
> #   ...page 2 content...
> #   <!-- InputPageNumber: 3 -->
> #   ...page 3 content...
> #   <!-- InputPageNumber: 5 -->
> #   ...page 5 content...
> ```
>
> An LLM or RAG indexer can therefore cite "see page 5" with the correct page
> number, even though page 5 is the *third* segment in the response.

See the [advanced sample][python_cu_sample_to_llm_input] for output options (fields-only,
markdown-only, custom metadata), metadata from the analysis result, multi-page content
ranges, and multi-segment video.

## Troubleshooting

### Common issues

**Error: "Access denied due to invalid subscription key or wrong API endpoint"**
- Verify your `endpoint URL` is correct
- Ensure your `API key` is valid or that your Microsoft Entra ID credentials have the correct permissions
- Make sure you have the **Cognitive Services User** role assigned to your account

**Error: "Model deployment not found" or "Default model deployment not configured"**
- Ensure you have deployed [supported generative models][supported_generative_models] (this guide uses gpt-5.2 and text-embedding-3-large as examples) in Microsoft Foundry
- Verify you have configured the default model deployments (see [Configure Model Deployments](#step-3-configure-model-deployments-required-for-prebuilt-analyzers))
- Check that your deployment names match what you configured in the defaults

**Error: "Operation failed" or timeout**
- LRO analysis may take time to complete; wait with `.result()` or poll manually.
- For inline analysis, confirm that the input is within the documented inline page and analyzer limits.

### Enable logging

To enable logging for debugging, configure logging in your application:

```python
import logging
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Create client with logging enabled
client = ContentUnderstandingClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(api_key),
    logging_enable=True
)
```

For more information about logging, see the [Azure SDK Python logging documentation][sdk_logging_docs].

## Next steps

* [`sample_update_defaults.py`][sample_update_defaults] - Required one-time setup to configure model deployments for prebuilt and custom analyzers
* [`sample_analyze_binary.py`][sample_analyze_binary] - Analyze PDF files from disk using `prebuilt-documentSearch`
* Explore the [samples directory][python_cu_samples] for complete code examples
* Read the [Azure AI Content Understanding documentation][python_cu_product_docs] for detailed service information

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][code_of_conduct_faq] or contact [opencode@microsoft.com][opencode_email] with any additional questions or comments.

To run the tests for this package, see the [tests README][tests_readme] and the [Azure SDK Python Testing Guide][azure_sdk_testing_guide].

<!-- LINKS -->

[python_cu_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/azure/ai/contentunderstanding
[python_cu_pypi]: https://pypi.org/project/azure-ai-contentunderstanding/
[python_cu_product_docs]: https://aka.ms/cu-doc
[python_cu_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples
[changelog]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/CHANGELOG.md
[python_cu_sample_to_llm_input]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_to_llm_input.py
[azure_sub]: https://azure.microsoft.com/free/
[cu_quickstart]: https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/use-rest-api?tabs=portal%2Cdocument&pivots=programming-language-rest
[cu_region_support]: https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support
[azure_portal]: https://portal.azure.com/
[deploy_models_docs]: https://learn.microsoft.com/azure/ai-studio/how-to/deploy-models-openai
[azure_identity_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity/README.md
[cu_prebuilt_analyzers]: https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers
[client_options]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#configurations
[handling_failures]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#azure-core-library-exceptions
[diagnostics]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md#logging
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[sample_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/README.md
[sample_update_defaults]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_update_defaults.py
[sample_analyze_binary]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_binary.py
[sample_analyze_inline]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_inline.py
[sample_analyze_binary_inline]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_binary_inline.py
[sample_analyze_chunking]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_chunking.py
[sample_create_analyzer_workflow]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_create_analyzer_workflow.py
[sample_analyze_configs]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_configs.py
[sample_detect_signatures]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_detect_signatures.py
[sample_classify_in_page_segments]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_classify_in_page_segments.py
[sample_extract_document_metadata]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_extract_document_metadata.py
[sample_analysis_diagnostics]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analysis_diagnostics.py
[tests_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/tests/README.md
[azure_sdk_testing_guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md
[pip]: https://pypi.org/project/pip/
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[file_issue]: https://github.com/Azure/azure-sdk-for-python/issues/new?labels=Cognitive%20-%20Content%20Understanding&title=[ContentUnderstanding]%20&body=%23%23%20Library%20Version%0A%0A%23%23%20Repro%20Steps%0A%0A%23%23%20Expected%20Result%0A%0A%23%23%20Actual%20Result
[code_of_conduct_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[opencode_email]: mailto:opencode@microsoft.com
[aiohttp]: https://pypi.org/project/aiohttp/
[cu_models_deployments]: https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/models-deployments
[supported_generative_models]: https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits#supported-generative-models
[model_retirement_schedule]: https://learn.microsoft.com/azure/foundry/openai/concepts/model-retirement-schedule
