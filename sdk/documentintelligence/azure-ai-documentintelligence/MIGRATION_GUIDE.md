# Guide for migrating azure-ai-documentintelligence from azure-ai-formrecognizer

This guide is intended to assist in the migration to `azure-ai-documentintelligence` from `azure-ai-formrecognizer`. 

> NOTE: Form Recognizer has been rebranded to Document Intelligence. Please check the [CHANGELOG][changelog] for new changes in future versions of this package.

Familiarity with `azure-ai-documentintelligence` package is assumed. For those new to the Azure AI Document Intelligence client library for Python please refer to the [README][readme] rather than this guide.

## Table of Contents
- [Migration benefits](#migration-benefits)
- [Features added](#features-added)
    - [Markdown Content Format](#markdown-content-format)
    - [Query Fields](#query-fields)
    - [Split Options](#split-options)
- [Breaking changes](#breaking-changes)
- [Additional samples](#additional-samples)

## Migration benefits

A natural question to ask when considering whether to adopt a new version of the library is what the benefits of doing so would be. As Azure Document Intelligence(formerly known as Form Recognizer) has matured and been embraced by a more diverse group of developers, we have been focused on learning the patterns and practices to best support developer productivity and add value to our customers. The API version since `2023-10-31-preview` will be used in `azure-ai-documentintelligence` library instead of `azure-ai-formrecognizer`.

There are many benefits to using the new design of the `azure-ai-documentintelligence` library. This new version of the library introduces two new clients `DocumentIntelligenceClient` and the `DocumentIntelligenceAdministrationClient` with unified methods for analyzing documents and provides support for the new features added by the service in API version `2023-10-31-preview` and later.

## Features Added

### Markdown Content Format

Supports output with Markdown content format along with the default plain _text_. For now, this is only supported for "prebuilt-layout". Markdown content format is deemed a more friendly format for LLM consumption in a chat or automation use scenario. Custom models should continue to use the default "text" content format for generating .ocr.json results.

Service follows the GFM spec ([GitHub Flavored Markdown](https://github.github.com/gfm/)) for the Markdown format. This SDK introduces a new enum _DocumentContentFormat_ with value "text" or "markdown" to indicate the result content format.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_forms/forms/Invoice_1.pdf"

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
poller = client.begin_analyze_document(
    "prebuilt-layout", AnalyzeDocumentRequest(url_source=url), output_content_format=DocumentContentFormat.MARKDOWN
)
result = poller.result()
```

### Query Fields

We reintroduce query fields as a premium add-on feature. When the keyword argument `features` is specified, the service will further extract the values of the fields specified via the keyword argument `query_fields` to supplement any existing fields defined by the model as fallback.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentAnalysisFeature

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_forms/forms/Invoice_1.pdf"

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
poller = client.begin_analyze_document(
    "prebuilt-layout",
    AnalyzeDocumentRequest(url_source=url),
    features=[DocumentAnalysisFeature.QUERY_FIELDS],
    query_fields=["NumberOfGuests", "StoreNumber"],
)
result = poller.result()
```

### Split Options

In the previous API versions supported by the older `azure-ai-formrecognizer` library, document splitting and classification operation (`"/documentClassifiers/{classifierId}:analyze"`) always tried to split the input file into multiple documents.

To enable a wider set of scenarios, this SDK introduces a keyword argument "split" to specify the document splitting mode with the new "2023-10-31-preview" service API version. The following values are supported:

- `split: "auto"`

Let service determine where to split.

- `split: "none"`

The entire file is treated as a single document. No splitting is performed.

- `split: "perPage"`

Each page is treated as a separate document. Each empty page is kept as its own document.

## Breaking Changes

### Clients names updates

|SDK version|Supported API service version|
|-|-|
|1.0.0b1|2023-10-31-preview|
|3.3.X(azure-ai-formrecognizer latest GA release)|2.0, 2.1, 2022-08-31, 2023-07-31 (default)|

|API version|Supported clients|
|-|-|
|2023-10-31-preview|DocumentIntelligenceClient and DocumentIntelligenceAdministrationClient|
|2023-07-31|DocumentAnalysisClient and DocumentModelAdministrationClient|
|2022-08-31 | DocumentAnalysisClient and DocumentModelAdministrationClient|
|2.1 | FormRecognizerClient and FormTrainingClient|
|2.0 | FormRecognizerClient and FormTrainingClient|

### Base endpoint updates
Updates all REST API operation paths from `{endpoint}/formrecognizer` to `{endpoint}/documentintelligence`. SDK would handle this change automatically, users would not have to do additional work to support this.

### Not backword compatible with azure-ai-formrecognizer
`azure-ai-documentintelligence` is a new package, it is not compatible with the previous `azure-ai-formrecognizer` package without necessary changes to your code.

### API shape changes
API shapes have been designed from scratch to support the new Client for the Document Intelligence service. Please refer to the [Readme][readme] and [Samples][samples] for more understanding.

### Field changes in prebuilt-receipt model
In `prebuilt-receipt` model, change to tract currency-related fields values from _number_ to _currency_.

```json
"Total": {
    "type": "currency",
    "valueCurrency": {
        "amount": 123.45,
        "currencySymbol": "$",
        "currencyCode": "USD"
    },
    ...
}
```
Now each currency-related field returning its own currency info to better support receipts with multi-currency, so the _Currency_ field in result has been removed.

```json
"fields": {
    "Total": {
        "type": "currency",
        "valueCurrency": {
            "amount": 123.45,
            "currencySymbol": "$",
            "currencyCode": "USD"
        },
    ...
    },
    "Tax": { "type": "currency", "valueCurrency": ... },
    ...
}
```

### Model Retirements/Deprecations

- `"prebuilt-businessCard"` model is retired.

- `"prebuilt-document"` model is retired, this model is essentially `"prebuilt-layout"` with `features="keyValuePairs"` specified. _(This is only supported as an optional feature for "prebuilt-layout" and "prebuilt-invoice".)_

All prebuilt models can be seen [here][di-models]. If you wish to still use these models, please rely on the older `azure-ai-formrecognizer` library through the older service API versions.

## Additional samples

For additional samples please take a look at the [Document Intelligence Samples][samples_readme] for more guidance.

[changelog]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/CHANGELOG.md
[readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md
[samples_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/README.md
[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples
[di-models]: https://aka.ms/azsdk/documentintelligence/models
