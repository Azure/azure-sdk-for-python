---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-document-intelligence
urlFragment: documentintelligence-samples
---

# Samples for Azure Document Intelligence client library for Python

These code samples show common scenario operations with the Azure Document Intelligence client library.

All of these samples need the endpoint to your Document Intelligence resource ([instructions on how to get endpoint][get-endpoint-instructions]), and your Document Intelligence API key ([instructions on how to get key][get-key-instructions]).

|**File Name**|**Description**|
|----------------|-------------|
|[sample_analyze_layout.py][sample_analyze_layout] and [sample_analyze_layout_async.py][sample_analyze_layout_async]|Extract text, selection marks, and table structures in a document|
|[sample_analyze_read.py][sample_analyze_read] and [sample_analyze_read_async.py][sample_analyze_read_async]|Read document elements, such as pages and detected languages|
|[sample_analyze_invoices.py][sample_analyze_invoices] and [sample_analyze_invoices_async.py][sample_analyze_invoices_async]|Analyze document text, selection marks, tables, and pre-trained fields and values pertaining to English invoices using a prebuilt model|
|[sample_analyze_identity_documents.py][sample_analyze_identity_documents] and [sample_analyze_identity_documents_async.py][sample_analyze_identity_documents_async]|Analyze document text and pre-trained fields and values pertaining to US driver licenses and international passports using a prebuilt model|
|[sample_analyze_receipts.py][sample_analyze_receipts] and [sample_analyze_receipts_async.py][sample_analyze_receipts_async]|Analyze document text and pre-trained fields and values pertaining to English sales receipts using a prebuilt model|
|[sample_analyze_tax_us_w2.py][sample_analyze_tax_us_w2] and [sample_analyze_tax_us_w2_async.py][sample_analyze_tax_us_w2_async]|Analyze document text and pre-trained fields and values pertaining to US tax W-2 forms using a prebuilt model|
|[sample_analyze_custom_documents.py][sample_analyze_custom_documents] and [sample_analyze_custom_documents_async.py][sample_analyze_custom_documents_async]|Analyze custom documents with your custom model to extract text, field values, selection marks, and table data from documents|
|[sample_analyze_addon_barcodes.py][sample_analyze_addon_barcodes] and [sample_analyze_addon_barcodes_async.py][sample_analyze_addon_barcodes_async]|Extract barcodes using the add-on capability.|
|[sample_analyze_addon_fonts.py][sample_analyze_addon_fonts] and [sample_analyze_addon_fonts_async.py][sample_analyze_addon_fonts_async]|Extract font information using the add-on capability.|
|[sample_analyze_addon_formulas.py][sample_analyze_addon_formulas] and [sample_analyze_addon_formulas_async.py][sample_analyze_addon_formulas_async]|Extract formulas using the add-on capability.|
|[sample_analyze_addon_highres.py][sample_analyze_addon_highres] and [sample_analyze_addon_highres_async.py][sample_analyze_addon_highres_async]|Recognize text with improved quality using the add-on capability.|
|[sample_analyze_addon_languages.py][sample_analyze_addon_languages] and [sample_analyze_addon_languages_async.py][sample_analyze_addon_languages_async]|Detect languages using the add-on capability.|

## Prerequisites
* Python 3.7 or later is required to use this package
* You must have an [Azure subscription][azure_subscription] and an
[Azure Document Intelligence account][azure_document_intelligence_account] to run these samples.

## Setup

1. Install the Azure Document Intelligence client library for Python with [pip][pip]:

```bash
pip install azure-ai-documentintelligence --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_analyze_receipts.py`

## Next steps

Check out the [API reference documentation][python-di-ref-docs] to learn more about
what you can do with the Azure Document Intelligence client library.


[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity

[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_document_intelligence_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[python-di-ref-docs]: https://aka.ms/azsdk/python/formrecognizer/docs
[get-endpoint-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md#get-the-endpoint
[get-key-instructions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/README.md#get-the-api-key
[changelog]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/documentintelligence/azure-ai-documentintelligence/CHANGELOG.md

<!-- V3.2+ links -->

[sample_analyze_layout]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_layout.py
[sample_analyze_layout_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_layout_async.py
[sample_analyze_invoices]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_invoices.py
[sample_analyze_invoices_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_invoices_async.py
[sample_analyze_identity_documents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_identity_documents.py
[sample_analyze_identity_documents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_identity_documents_async.py
[sample_analyze_receipts]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_receipts.py
[sample_analyze_receipts_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_receipts_async.py
[sample_analyze_custom_documents]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_custom_documents.py
[sample_analyze_custom_documents_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_custom_documents_async.py
[sample_analyze_read]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_read.py
[sample_analyze_read_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_read_async.py
[sample_analyze_tax_us_w2]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_tax_us_w2.py
[sample_analyze_tax_us_w2_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_tax_us_w2_async.py
[sample_analyze_addon_barcodes]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_addon_barcodes.py
[sample_analyze_addon_barcodes_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_addon_barcodes_async.py
[sample_analyze_addon_fonts]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_addon_fonts.py
[sample_analyze_addon_fonts_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_addon_fonts_async.py
[sample_analyze_addon_formulas]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_addon_formulas.py
[sample_analyze_addon_formulas_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_addon_formulas_async.py
[sample_analyze_addon_highres]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_addon_highres.py
[sample_analyze_addon_highres_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_addon_highres_async.py
[sample_analyze_addon_languages]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_analyze_addon_languages.py
[sample_analyze_addon_languages_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_analyze_addon_languages_async.py
