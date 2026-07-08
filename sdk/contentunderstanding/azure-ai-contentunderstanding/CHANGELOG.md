# Release History

## 1.2.0b3 (Unreleased)

### Other Changes

- Added GitHub Copilot skills under `.github/skills/` to help users
  iteratively author custom analyzers in VS Code with Copilot:
  - **`cu-sdk-author-analyzer`** — author and refine a custom analyzer
    for a single document type (layout extraction → schema drafting →
    validation → batch test → agent review → refine cycle). Document
    modality only in this release; audio, video, and image are planned
    for a later release.
  - **`cu-sdk-author-analyzer-classify-route`** — author and refine a
    classify-and-route pipeline for mixed-document packets (e.g. invoice
    + bank statement + loan application in one PDF), with per-category
    review of both the outer classifier descriptions and each inner
    schema's field descriptions.

## 1.2.0b2 (2026-06-10)

### Bugs Fixed
- Filtered service-emitted `LLMStats:` telemetry entries from the rendered `rai_warnings` front matter.

### Other Changes
- Updated `to_llm_input` page markers from `<!-- page N -->` to `<!-- InputPageNumber: N -->` and avoided duplicate marker injection when the service markdown already includes `InputPageNumber` markers.

## 1.2.0b1 (2026-04-28)


### Features Added
- Added `to_llm_input` helper function that converts `AnalysisResult` objects into LLM-friendly text with YAML front matter and markdown content. Supports documents, audio/video, and classification hierarchies.

### Other Changes
- Aligned `sample_create_analyzer_with_labels` (sync + async) with the .NET and Java equivalents: added an analyze step (calls `begin_analyze` on the newly created analyzer to extract `MerchantName` / `TotalPrice` from a sample invoice when training data is configured), a `DEMO MODE` banner when no training data is configured, a field-schema verification banner, and `try` / `finally` cleanup so the analyzer is deleted even if creation fails.

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

