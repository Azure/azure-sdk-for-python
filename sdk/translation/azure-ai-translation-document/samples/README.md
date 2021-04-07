---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-document-translation
urlFragment: documenttranslation-samples
---

# Samples for Azure Document Translation client library for Python

These code samples show common scenario operations with the Azure Document Translation client library.
The async versions of the samples require Python 3.6 or later.

You can authenticate your client with a Document Translation API key:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Document Translation client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_create_translation_job.py][create_translation_job] and [sample_create_translation_job_async.py][create_translation_job_async]|Create a document translation job|
|[sample_translation_with_glossaries.py][create_translation_job_with_glossaries] and [sample_translation_with_glossaries_async.py][create_translation_job_with_glossaries_async]|Create a document translation job using custom glossaries|
|[sample_check_document_statuses.py][check_document_statuses] and [sample_check_document_statuses_async.py][check_document_statuses_async]|Check status of submitted documents|
|[sample_list_all_submitted_jobs.py][list_all_submitted_jobs] and [sample_list_all_submitted_jobs_async.py][list_all_submitted_jobs_async]|Check status of all submitted translation jobs|


## Prerequisites
* Python 2.7, or 3.6 or later is required to use this package (3.6 or later if using asyncio)
* You must have an [Azure subscription][azure_subscription] and an
[Azure Translation account][azure_document_translation_account] to run these samples.

## Setup

1. Install the Azure Document Translation client library for Python with [pip][pip]:

```bash
pip install azure-ai-translation-document --pre
```
For more information about how the versioning story of the SDK corresponds to the versioning story of the service's API, see [here][versioning_story_readme].

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_create_translation_job.py`

## Next steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Document Translation client library.

|**Advanced Sample File Name**|**Description**|
|----------------|-------------|
|[sample_translation_with_azure_blob.py][create_translation_job_with_azure_blob] and [sample_translation_with_azure_blob_async.py][create_translation_job_with_azure_blob_async]|Create a document translation job with document upload/download help|


[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/translation/azure-ai-translation-document#install-the-package
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_authentication_async.py
[create_translation_job]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_create_translation_job.py
[create_translation_job_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_create_translation_job_async.py
[create_translation_job_with_azure_blob]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_azure_blob.py
[create_translation_job_with_azure_blob_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_azure_blob_async.py
[create_translation_job_with_glossaries]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_glossaries.py
[create_translation_job_with_glossaries_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_glossaries_async.py
[check_document_statuses]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_check_document_statuses.py
[check_document_statuses_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_check_document_statuses_async.py
[list_all_submitted_jobs]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/sample_list_all_submitted_jobs.py
[list_all_submitted_jobs_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_list_all_submitted_jobs_async.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_document_translation_account]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=python
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[api_reference_documentation]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview
