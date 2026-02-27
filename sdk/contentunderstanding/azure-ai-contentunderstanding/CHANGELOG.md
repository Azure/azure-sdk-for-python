# Release History

## 1.0.0 (Unreleased)

### Features Added
- GA release of Azure AI Content Understanding client library for Python
- Each field subclass (e.g., `StringField`, `NumberField`) now exposes a strongly-typed `value` property
- Added `AnalysisContent` hierarchy (`DocumentContent`, `AudioVisualContent`) for strongly-typed parsing of content on `AnalysisResult`
- Added new sample `sample_create_analyzer_with_labels` for label-based training (sync + async)
- Updated to service API version `2025-11-01`

### Other Changes

The following API changes were made from the preview SDK (`1.0.0b1`) to the GA SDK to align with [Azure SDK for Python design guidelines](https://azure.github.io/azure-sdk/python_design.html):

- **Type renames:** `AnalyzeInput` → `AnalysisInput`, `AnalyzeResult` → `AnalysisResult`, `MediaContent` → `AnalysisContent`, `MediaContentKind` → `AnalysisContentKind`
- **Property renames:** `AnalysisInput.input_range` → `content_range`
- **Method signatures:** `begin_analyze` `inputs` parameter is now a required keyword argument (previously optional); parameter order changed to `inputs`, `model_deployments`, `processing_location`
- **Method signatures:** `begin_analyze_binary` `input_range` keyword renamed to `content_range`; parameter order changed to `content_range`, `content_type`, `processing_location`

## 1.0.0b1 (2026-01-16)

### Features Added
- Initial release of Azure AI Content Understanding client library for Python
- Added `ContentUnderstandingClient` for analyzing documents, audio, and video content

