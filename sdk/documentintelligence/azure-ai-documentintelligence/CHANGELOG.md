# Release History

## 1.0.0b1 (2023-11-17)

This is the first preview of the `azure-ai-documentintelligence` package, targeting API version `2023-10-31-preview` of the Document Intelligence service(formerly known as Form Recognizer).

_**Note: Form Recognizer has been rebranded to Document Intelligence.**_

The new `2023-10-31-preview` service version comes with some new features and a few breaking changes when compared to the API versions supported by the `azure-ai-formrecognizer` library.

### Features Added

- **Markdown content format**

Supports output with Markdown content format along with the default plain _text_. For now, this is only supported for "prebuilt-layout". Markdown content format is deemed a more friendly format for LLM consumption in a chat or automation use scenario. Custom models should continue to use the default "text" content format for generating .ocr.json results.

Service follows the GFM spec ([GitHub Flavored Markdown](https://github.github.com/gfm/)) for the Markdown format. This SDK introduces a new enum _ContentFormat_ with value "text" or "markdown" to indicate the result content format.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_forms/forms/Invoice_1.pdf"

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
poller = client.begin_analyze_document(
    "prebuilt-layout", AnalyzeDocumentRequest(url_source=url), output_content_format=ContentFormat.MARKDOWN
)
result = poller.result()
```

Tables, paragraphs formulas and styles are represented accordingly and may have breaking changes with regards to the content that you may have received using the older `azure-ai-formrecognizer` library, that relies on older service API versions.

- **Query Fields**

We reintroduce query fields as a premium add-on feature. When the keyword argument `features` is specified, the service will further extract the values of the fields specified via the keyword argument `query_fields` to supplement any existing fields defined by the model as fallback.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentAnalysisFeature

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_forms/forms/Invoice_1.pdf"

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
poller = client.begin_analyze_document(
    "prebuilt-layout",
    AnalyzeDocumentRequest(url_source=url),
    features=[DocumentAnalysisFeature.QUERY_FIELDS],
    query_fields=["NumberOfGuests", "StoreNumber"],
)
result = poller.result()
```

- **Split Options**

In the previous API versions supported by the older `azure-ai-formrecognizer` library, document splitting and classification operation (`"/documentClassifiers/{classifierId}:analyze"`) always tried to split the input file into multiple documents.

To enable a wider set of scenarios, this SDK introduces a keyword argument "split" to specify the document splitting mode with the new "2023-10-31-preview" service version. The following values are supported:

- `split: "auto"`

Let service determine where to split.

- `split: "none"`

The entire file is treated as a single document. No splitting is performed.

- `split: "perPage"`

Each page is treated as a separate document. Each empty page is kept as its own document.

### Breaking Changes

- Updates clients names.

|**2023-07-31**|**2023-10-31-preview**|
|----------------|-------------|
|DocumentAnalysisClient|DocumentIntelligenceClient|
|DocumentModelAdministrationClient|DocumentIntelligenceAdministrationClient|

- Updates all REST API operation paths from `{endpoint}/formrecognizer` to `{endpoint}/documentintelligence`. SDK would handle this change automatically, users would not have to do additional work to support this.

- `azure-ai-documentintelligence` is a new package, it is not compatible with the previous `azure-ai-formrecognizer` package without necessary changes to your code.

- API shapes have been designed from scratch to support the new Client for the Document Intelligence service. Please refer to the [Readme](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md) and [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples) for more understanding.

- In `prebuilt-receipt` model, change to tract currency-related fields values from _number_ to _currency_.

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

- Model Retirements/Deprecations.

`"prebuilt-businessCard"` model is retired.

`"prebuilt-document"` model is retired, this model is essentially `"prebuilt-layout"` with `features=keyValuePairs` specified. _(This is only supported as an optional feature for "prebuilt-layout" and "prebuilt-invoice".)_

If you wish to still use these models, please rely on the older `azure-ai-formrecognizer` library through the older service API versions.
