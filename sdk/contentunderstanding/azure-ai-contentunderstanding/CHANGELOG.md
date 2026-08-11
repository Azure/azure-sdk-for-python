# Release History

## 1.2.0b3 (2026-08-11)

### Features Added

- Added support for selecting `2025-11-01` or `2026-06-01-preview` through the `api_version` keyword argument on `ContentUnderstandingClient`; this beta package defaults to `2026-06-01-preview`. See the [README service API version examples](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md#service-api-versions).

- Added support for `2026-06-01-preview` service. Features included:
  - Analyze smaller inputs without long-running operation polling with `analyze_inline` and `analyze_binary_inline`. See [sample_analyze_inline.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_inline.py) and [sample_analyze_binary_inline.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_binary_inline.py).
  - Extract fields whose answers must be built from evidence across a document, such as multistep reasoning or calculations, with agentic analyzer workflows by setting `ContentAnalyzerConfig.workflow` to `ContentAnalyzerWorkflow.AGENTIC`. See [sample_create_analyzer_workflow.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_create_analyzer_workflow.py).
  - Classify mixed document packets with boundaries within a page by enabling `ContentAnalyzerConfig.allow_in_page_segments`. See [sample_classify_in_page_segments.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_classify_in_page_segments.py).
  - Prepare documents for retrieval and LLM workflows with semantic chunks by configuring `ContentAnalyzerConfig.chunking_strategy` with `SemanticChunkingStrategy` and reading `DocumentContent.chunks`. See [sample_analyze_chunking.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_chunking.py).
  - Identify signatures and their locations in documents with `DocumentSignature` and `DocumentContent.signatures`. See [sample_detect_signatures.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_detect_signatures.py) and [sample_analyze_configs.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_configs.py).
  - Preserve source document context in retrieval and LLM output with `AnalysisContent.metadata` and `to_llm_input`. See [sample_extract_document_metadata.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_extract_document_metadata.py) and [sample_to_llm_input.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_to_llm_input.py).
  - Troubleshoot analyses with diagnostic information from `AnalysisResult.infos`. See [sample_analysis_diagnostics.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analysis_diagnostics.py).
  - Track inline page usage and agentic workflow token consumption with expanded `UsageDetails`, available from `AnalyzeLROPoller.usage`, `AnalyzeAsyncLROPoller.usage`, and `ContentAnalyzerInlineResponse.usage`. See [sample_analyze_invoice.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_invoice.py), [sample_analyze_inline.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_inline.py), and [sample_analyze_binary_inline.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_analyze_binary_inline.py).

### Breaking Changes

### Bugs Fixed

### Other Changes

- Renamed the optional `to_llm_input` caller dictionary from `metadata` to `custom_metadata`; it is emitted under a nested `customMetadata:` front-matter block.
- Added advanced samples for [field grounding sources](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_content_source.py) and [long-running operation (LRO) continuation-token rehydration](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_rehydrate_operation.py), with async counterparts.
- Updated README, samples, env templates, and Copilot skills to recommend `gpt-5.2` and `text-embedding-3-large`, including prebuilt analyzer deployment aliases and a model retirement schedule note.
- Added experimental GitHub Copilot skills under `.github/skills/` for user feedback on iterative custom-analyzer authoring in VS Code:
  - **`cu-sdk-author-analyzer`** — author and refine a custom document analyzer for a single document type (layout extraction → schema drafting → validation → batch test → agent review → refine cycle).
  - **`cu-sdk-author-analyzer-classify-route`** — author and refine a classify-and-route pipeline for mixed-document packets (e.g. invoice + bank statement + loan application in one PDF), with per-category review of both the outer classifier descriptions and each inner schema's field descriptions.

## 1.2.0b2 (2026-06-10)

### Bugs Fixed
- Filtered service-emitted `LLMStats:` telemetry entries from the rendered `rai_warnings` front matter.

### Other Changes
- Updated `to_llm_input` page markers from `<!-- page N -->` to `<!-- InputPageNumber: N -->` and avoided duplicate marker injection when the service markdown already includes `InputPageNumber` markers.

## 1.2.0b1 (2026-04-28)


### Features Added
- Added `to_llm_input` helper function that converts `AnalysisResult` objects into LLM-friendly text with YAML front matter and markdown content. Supports documents, audio/video, and classification hierarchies.

### Other Changes
- Enhanced `sample_create_analyzer_with_labels` (sync + async): added an analyze step (calls `begin_analyze` on the newly created analyzer to extract `MerchantName` / `TotalPrice` from a sample invoice when training data is configured), a `DEMO MODE` banner when no training data is configured, a field-schema verification banner, and `try` / `finally` cleanup so the analyzer is deleted even if creation fails.

## 1.1.0 (2026-04-20)

### Features Added
- Added `usage` property on `AnalyzeLROPoller` and `AnalyzeAsyncLROPoller` to surface billing and token consumption details (`UsageDetails`) returned by the REST API.

## 1.0.1 (2026-03-06)

### Bugs Fixed
- Removed `_models.pyi` stub file that caused type checkers (pyright, mypy) to only resolve 10 of 51 model classes, hiding types like `AnalysisResult` and `AnalyzerDefinition`. The `.value` property type information is now provided via `TYPE_CHECKING` class redeclarations in `models/_patch.py`.

## 1.0.0 (2026-02-28)

### Features Added
- GA release of Azure AI Content Understanding client library for Python
- Each `ContentField` subclass (e.g., `StringField`, `NumberField`) now exposes a `value` property with a type appropriate to that subclass (e.g., `str` for `StringField`, `float` for `NumberField`)

### Other Changes

The following API changes were made from the preview SDK (`1.0.0b1`) to the GA SDK to align with [Azure SDK for Python design guidelines](https://azure.github.io/azure-sdk/python_design.html):

- **Type renames:** `AnalyzeInput` → `AnalysisInput`, `AnalyzeResult` → `AnalysisResult`, `MediaContent` → `AnalysisContent`, `MediaContentKind` → `AnalysisContentKind`
- **Property renames:** `AnalysisInput.input_range` → `content_range`
- **Method signatures:** `begin_analyze` `inputs` parameter is now a required keyword argument (previously optional); parameter order changed to `inputs`, `model_deployments`, `processing_location`
- **Method signatures:** `begin_analyze_binary` `input_range` keyword renamed to `content_range`; parameter order changed to `content_range`, `content_type`, `processing_location`
- Added new sample `sample_create_analyzer_with_labels` for label-based training (sync + async)

## 1.0.0b1 (2026-01-16)

### Features Added
- Initial release of Azure AI Content Understanding client library for Python
- Added `ContentUnderstandingClient` for analyzing documents, audio, and video content

