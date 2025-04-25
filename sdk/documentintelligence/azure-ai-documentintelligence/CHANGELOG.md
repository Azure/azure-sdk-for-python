# Release History

## 1.0.3 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.2 (2025-03-26)

### Bugs Fixed

- Fix polling for `begin_copy_classifier_to()` to stop on success response from the "Operation-Location" endpoint and correctly parse the result.

## 1.0.1 (2025-03-13)

### Bugs Fixed

- Fix polling for `begin_copy_model_to()` to stop on success response from the "Operation-Location" endpoint and correctly parse the result.

## 1.0.0 (2024-12-17)

### Features Added

- Added support for the Analyze Batch Documents API:
  - Added operations `delete_analyze_batch_result()`, `get_analyze_batch_result()` and `list_analyze_batch_results()` to `DocumentIntelligenceClient`.
- Added support for the Analyze Documents API:
  - Added operations `delete_analyze_result()` to `DocumentIntelligenceClient`.

### Breaking Changes

- Renamed request body parameters on all methods to `body`.
- Renamed operation `get_resource_info()` to `get_resource_details()`.
- Renamed model `ContentFormat` to `DocumentContentFormat`.
- Renamed model `AnalyzeBatchResultOperation` to `AnalyzeBatchOperation`.
- Renamed model `CopyAuthorization` to `ModelCopyAuthorization`.
- Renamed model `Document` to `AnalyzedDocument`.
- Renamed model `Error` to `DocumentIntelligenceError`.
- Renamed model `ErrorResponse` to `DocumentIntelligenceErrorResponse`.
- Renamed model `InnerError` to `DocumentIntelligenceInnerError`.
- Renamed model `OperationDetails` to `DocumentIntelligenceOperationDetails`.
- Renamed model `OperationStatus` to `DocumentIntelligenceOperationStatus`.
- Renamed model `ResourceDetails` to `DocumentIntelligenceResourceDetails`.
- Renamed model `Warning` to `DocumentIntelligenceWarning`.
- Renamed property `items_property` in model `DocumentFieldSchema` to `items_schema`.
- Renamed enum `FontStyle` to `DocumentFontStyle`.
- Renamed enum `FontWeight` to `DocumentFontWeight`.
- Removed model `AnalyzeResultOperation`.
- Removed `GENERATIVE ` in enum `DocumentBuildMode`.

### Other Changes

- Changed the default service API version to `2024-11-30`.
- No need to pass `content-type` when analyze_request is a stream in `begin_analyze_document()` and `begin_classify_document()`.

## 1.0.0b4 (2024-09-05)

### Features Added

- Added support for the Analyze Batch Documents API:
  - Added LRO operation `begin_analyze_batch_documents()` to `DocumentIntelligenceClient`.
  - Added models `AnalyzeBatchDocumentsRequest`, `AnalyzeBatchResult` and `AnalyzeBatchOperationDetail`.
- Added support for different kinds of output in the Analyze Document API:
  - Added operations `get_analyze_result_figure()` and `get_analyze_result_pdf()` to `DocumentIntelligenceClient`.
  - Added optional kwarg `output` to LRO operation `begin_analyze_document()` overloads in `DocumentIntelligenceClient`.
  - Added enum `AnalyzeOutputOption` to specify output kind, either `pdf` or `figures`.
  - Added property `id` to model `DocumentFigure`.
- Added support for the Copy Classifier API:
  - Added operations `authorize_classifier_copy()` and `begin_copy_classifier_to()` to `DocumentIntelligenceAdministrationClient`.
  - Added models `AuthorizeClassifierCopyRequest` and `ClassifierCopyAuthorization`.
- Added optional kwarg `pages` to LRO operation `begin_classify_document()` overloads in `DocumentIntelligenceClient`.
- Added new kind `GENERATIVE` to enum `DocumentBuildMode`.
- Added property `warnings` to model `AnalyzeResult`.
- Added properties `classifier_id`, `split`, and `training_hours` to model `DocumentModelDetails`.
- Added properties `model_id`, `confidence_threshold`, `features`, `query_fields` and `max_documents_to_analyze` to model `DocumentTypeDetails`.
- Added property `allow_overwrite` to model `BuildDocumentClassifierRequest`.
- Added properties `allow_overwrite` and `max_training_hours` to model `BuildDocumentModelRequest`.
- Added properties `classifier_id`, `split` and `doc_types` to model `ComposeDocumentModelRequest`.
- Added support for getting `operation_id` via `details` property in the new return types `AnalyzeDocumentLROPoller` and `AsyncAnalyzeDocumentLROPoller` in operation `begin_analyze_document()`.

### Breaking Changes

- Removed support for extracting lists from analyzed documents:
  - Removed models `DocumentList` and `DocumentListItem`.
  - Removed property `lists` from model `AnalyzeResult`.
- Changes to the Compose Document API:
  - Removed model `ComponentDocumentModelDetails`.
  - Removed property `component_models` from model `ComposeDocumentModelRequest`.
  - `ComposeDocumentModelRequest` now requires a dictionary of `DocumentTypeDetails` instances and a classifier ID to be constructed.
- Removed model `QuotaDetails`.
- Removed property `custom_neural_document_model_builds` from model `ResourceDetails`.
- Changed the _required_ property `field_schema` from `DocumentTypeDetails` to be _optional_.

### Other Changes

- Changed the default service API version to `2024-07-31-preview`.
- Improved performance by about `1.5X` faster when deserializing `JSON` to an `AnalyzeResult` object compared to last version `1.0.0b3`.

## 1.0.0b3 (2024-04-09)

### Other Changes

- Changed the default polling interval from 5s to 1s.

## 1.0.0b2 (2024-03-07)

### Features Added

- Added models `AnalyzeResultOperation` and `Warning`.
- Added property `base_classifier_id` to model `BuildDocumentClassifierRequest`.
- Added properties `base_classifier_id` and `warnings` to model `DocumentClassifierDetails`.
- Added property `warnings` to model `DocumentModelDetails`.
- Added property `value_selection_group` to model `DocumentField`.
- Added value `selectionGroup` to enum `DocumentFieldType`.
- Added value `completed` to enum `OperationStatus`.

### Breaking Changes

- Changed property name from `items` to `items_property` in model `DocumentFieldSchema` and `DocumentList`.
- Changed property name from `base64_source` to `bytes_source` in model `AnalyzeDocumentRequest` and `ClassifyDocumentRequest`.

### Other Changes

- Changed the default polling interval from 30s to 5s.
- Changed the default service API version to `2024-02-29-preview`.
- Bumped minimum dependency on `azure-core` to `>=1.30.0`.
- Bumped minimum dependency on `typing-extensions` to `>=4.6.0`.
- Python 3.7 is no longer supported. Please use Python version 3.8 or later.

## 1.0.0b1 (2023-11-17)

This is the first preview of the `azure-ai-documentintelligence` package, targeting API version `2023-10-31-preview` of the Document Intelligence service(formerly known as Form Recognizer).

> Note: Form Recognizer has been rebranded to Document Intelligence.

### Breaking Changes

- Changed clients names from DocumentAnalysisClient and DocumentModelAdministrationClient in API version 2023-07-31 in `azure-ai-formrecognizer` to DocumentIntelligenceClient and DocumentIntelligenceAdministrationClient in API version 2023-10-31-preview in `azure-ai-documentintelligence`.
- Changed all REST API operation paths from `{endpoint}/formrecognizer` to `{endpoint}/documentintelligence`.
- Changed some currency-related fields in `prebuilt-receipt` model.
- Retired model `prebuilt-businessCard` and `prebuilt-document`. `prebuilt-document` model is essentially `prebuilt-layout` with `features="keyValuePairs"` specified. _(This is only supported as an optional feature for "prebuilt-layout" and "prebuilt-invoice".)_

If you were using the old `azure-ai-formrecognizer` package, please refer [MIGRATION_GUIDE.MD](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/MIGRATION_GUIDE.md) for more details.
