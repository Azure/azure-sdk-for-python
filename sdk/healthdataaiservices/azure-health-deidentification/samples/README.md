---
page_type: sample
languages:
- python
products:
- azure
- azure-health-data-services
name: azure-health-deidentification samples for Python
description: Samples for the azure-health-deidentification client library
---

# Samples for Azure Health Data Services de-identification service client library for Python
These code samples show common scenario operations with the Azure Health Data Services de-identification service client library.

| File Name | Description |
| --- | --- |
| [deidentify_text_tag.py][deidentify_text_tag] and [deidentify_text_tag_async.py][deidentify_text_tag_async] | De-identify text using the tag operation |
| [deidentify_text_redact.py][deidentify_text_redact] and [deidentify_text_redact_async.py][deidentify_text_redact_async] | De-identify text using the redact operation |
| [deidentify_text_surrogate.py][deidentify_text_surrogate] and [deidentify_text_surrogate_async.py][deidentify_text_surrogate_async] | De-identify text using the surrogate operation |
| [deidentify_documents.py][deidentify_documents] and [deidentify_documents_async.py][deidentify_documents_async] | De-identify documents in Azure Storage with an asynchronous job |
| [list_jobs.py][list_jobs] and [list_jobs_async.py][list_jobs_async] | List de-identification jobs |
| [list_job_documents.py][list_job_documents] and [list_job_documents_async.py][list_job_documents_async] | List the documents processed by a de-identification job |

## Getting started

### Prerequisites
- Python 3.9 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- [Deploy the de-identification service][deid_quickstart].
- [Configure Azure role-based access control (RBAC)][deid_rbac] for the operations you will perform.

## Setup
1. Install the Azure Health Deidentification client library for Python with [pip](https://pypi.org/project/pip/):
   
   ```bash
   pip install azure-health-deidentification
   ```
1. Clone or download this sample repository.
1. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python deidentify_text.py`

## Next steps

Check out the [API reference documentation][api_explorer] to learn more about
what you can do with the Azure Health Data Services de-identification service client library.

<!-- LINKS -->
[api_explorer]: https://learn.microsoft.com/python/api/overview/azure/health-deidentification
[azure_sub]: https://azure.microsoft.com/free/
[deid_quickstart]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/quickstart
[deid_rbac]: https://learn.microsoft.com/azure/healthcare-apis/deidentification/manage-access-rbac

[deidentify_text_tag]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/deidentify_text_tag.py
[deidentify_text_redact]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/deidentify_text_redact.py
[deidentify_text_surrogate]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/deidentify_text_surrogate.py
[deidentify_documents]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/deidentify_documents.py
[list_jobs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/list_jobs.py
[list_job_documents]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/list_job_documents.py
[deidentify_text_tag_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/deidentify_text_tag_async.py
[deidentify_text_redact_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/deidentify_text_redact_async.py
[deidentify_text_surrogate_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/deidentify_text_surrogate_async.py
[deidentify_documents_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/deidentify_documents_async.py
[list_jobs_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/list_jobs_async.py
[list_job_documents_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/healthdataaiservices/azure-health-deidentification/samples/async_samples/list_job_documents_async.py