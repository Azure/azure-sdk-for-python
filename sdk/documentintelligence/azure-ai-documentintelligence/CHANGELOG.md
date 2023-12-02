# Release History

## 1.0.0b1 (2023-11-17)

This is the first preview of the `azure-ai-documentintelligence` package, targeting API version `2023-10-31-preview` of the Document Intelligence service(formerly known as Form Recognizer).

> Note: Form Recognizer has been rebranded to Document Intelligence.

### Breaking Changes

- Changed clients names from DocumentAnalysisClient and DocumentModelAdministrationClient in API version 2023-07-31 in `azure-ai-formrecognizer` to DocumentModelAdministrationClient and DocumentIntelligenceAdministrationClient in API version 2023-10-31-preview in `azure-ai-documentintelligence`.
- Changed all REST API operation paths from `{endpoint}/formrecognizer` to `{endpoint}/documentintelligence`.
- Changed some currency-related fields in `prebuilt-receipt` model.
- Retired model `prebuilt-businessCard` and `prebuilt-document`. `prebuilt-document` model is essentially `prebuilt-layout` with `features="keyValuePairs"` specified. _(This is only supported as an optional feature for "prebuilt-layout" and "prebuilt-invoice".)_

If you wish to still use these models, please rely on the older `azure-ai-formrecognizer` library through the older service API versions.

Please refer [MIGRATION.MD](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/MIGRATION_GUIDE.md) for more details.
