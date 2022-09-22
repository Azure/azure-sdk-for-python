---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-translator
urlFragment: documenttranslation-samples
---

# Samples for Azure Document Translation client library for Python

These code samples show common scenario operations with the Azure Document Translation client library.

You can authenticate your client with a Document Translation API key or through Azure Active Directory with a token credential from [azure-identity][azure_identity]:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Document Translation client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_begin_translation.py][begin_translation] and [sample_begin_translation_async.py][begin_translation_async]|Translate your documents|
|[sample_translate_multiple_inputs.py][sample_translate_multiple_inputs] and [sample_translate_multiple_inputs_async.py][sample_translate_multiple_inputs_async]|Translate multiple source containers with documents to multiple target containers in different languages|
|[sample_translation_with_glossaries.py][begin_translation_with_glossaries] and [sample_translation_with_glossaries_async.py][begin_translation_with_glossaries_async]|Translate your documents using custom glossaries|
|[sample_check_document_statuses.py][check_document_statuses] and [sample_check_document_statuses_async.py][check_document_statuses_async]|Check status of submitted documents|
|[sample_list_translations.py][list_translations] and [sample_list_translations_async.py][list_translations_async]|Check status of all submitted translation operations|


## Prerequisites
* Python 3.6 or later is required to use this package
* You must have an [Azure subscription][azure_subscription] and an
[Azure Translator account][azure_document_translation_account] to run these samples.

## Setup

1. Install the Azure Document Translation client library for Python with [pip][pip]:

```bash
pip install azure-ai-translation-document
```
For more information about how the versioning of the SDK corresponds to the versioning of the service's API, see [here][versioning_story_readme].

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_begin_translation.py`

## Next steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Document Translation client library.

|**Advanced Sample File Name**|**Description**|
|----------------|-------------|
|[sample_translation_with_azure_blob.py][begin_translation_with_azure_blob] and [sample_translation_with_azure_blob_async.py][begin_translation_with_azure_blob_async]|Translate documents with upload/download help using Azure Blob Storage|
|[sample_translation_with_custom_model.py][sample_translation_with_custom_model] and [sample_translation_with_custom_model_async.py][sample_translation_with_custom_model_async]|Translate documents using a custom model|
|[sample_begin_translation_with_filters.py][sample_begin_translation_with_filters] and [sample_begin_translation_with_filters_async.py][sample_begin_translation_with_filters_async]|Translate documents under a folder or translate only a specific document|
|[sample_list_document_statuses_with_filters.py][sample_list_document_statuses_with_filters] and [sample_list_document_statuses_with_filters_async.py][sample_list_document_statuses_with_filters_async]|List document statuses using filters|
|[sample_list_translations_with_filters.py][sample_list_translations_with_filters] and [sample_list_translations_with_filters_async.py][sample_list_translations_with_filters_async]|List translation operations using filters|


[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document#install-the-package
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_authentication_async.py
[begin_translation]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation.py
[begin_translation_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_begin_translation_async.py
[sample_translate_multiple_inputs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_translate_multiple_inputs.py
[sample_translate_multiple_inputs_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translate_multiple_inputs_async.py
[begin_translation_with_azure_blob]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_azure_blob.py
[begin_translation_with_azure_blob_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_azure_blob_async.py
[begin_translation_with_glossaries]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_glossaries.py
[begin_translation_with_glossaries_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_glossaries_async.py
[check_document_statuses]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_check_document_statuses.py
[check_document_statuses_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_check_document_statuses_async.py
[list_translations]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_list_translations.py
[list_translations_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_list_translations_async.py
[sample_translation_with_custom_model]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_custom_model.py
[sample_translation_with_custom_model_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_custom_model_async.py
[sample_begin_translation_with_filters]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation_with_filters.py
[sample_begin_translation_with_filters_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_begin_translation_with_filters_async.py
[sample_list_document_statuses_with_filters]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_list_document_statuses_with_filters.py
[sample_list_document_statuses_with_filters_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_list_document_statuses_with_filters_async.py
[sample_list_translations_with_filters]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/sample_list_translations_with_filters.py
[sample_list_translations_with_filters_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_list_translations_with_filters_async.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_document_translation_account]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=python
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[api_reference_documentation]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview
