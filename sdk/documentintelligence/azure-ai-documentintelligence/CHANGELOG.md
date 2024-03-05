# Release History

## 1.0.0b2 (Unreleased)

### Features Added

### Breaking Changes

- Changed property name from `items` to `items_property` in model `DocumentFieldSchema` and `DocumentList`.
- Changed property name from `base64_source` to `bytes_source` in model `AnalyzeDocumentRequest` and `ClassifyDocumentRequest`.

### Bugs Fixed

### Other Changes

- Changed the default polling interval from 30s to 5s.
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
