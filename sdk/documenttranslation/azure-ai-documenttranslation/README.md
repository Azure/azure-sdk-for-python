# Azure Document Translation client library for Python

Azure Cognitive Services Document Translation is a cloud service that translates documents to and from 90 languages 
and dialects while preserving document structure and data format. Use the client library for Document Translation to:

* Translate numerous, large files from an Azure Blob Storage container to a target container in your language of choice
* Check the translation status and progress of each document in the translation job
* Apply a custom translation model or glossaries to tailor translation to your specific case

[Source code][python-dt-src] | [Package (PyPI)][python-dt-pypi] | [API reference documentation][python-dt-ref-docs]| [Product documentation][python-dt-product-docs] | [Samples][python-dt-samples]

## Getting started

### Prerequisites
* Python 2.7, or 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Document Translation resource][DT_resource] to use this package.

### Install the package
Install the Azure Document Translation client library for Python with [pip][pip]:

```bash
pip install azure-ai-documenttranslation --pre
```

> Note: This version of the client library defaults to the v1.0-preview.1 version of the service

#### Create a Document Translation resource
Document Translation supports [single-service access][single_service] only.
To access the service, create a Translator resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_DT_resource]

**Option 2:** [Azure CLI][azure_cli_create_DT_resource].
Below is an example of how you can create a Document Translation resource using the CLI:

```bash
# Create a new resource group to hold the document translation resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2
```

```bash
# Create document translation
az cognitiveservices account create \
    --name document-translation-resource \
    --resource-group my-resource-group \
    --kind TextTranslation \
    --sku F0 \
    --location westus2 \
    --yes
```

### Authenticate the client
In order to interact with the Document Translation service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


#### Looking up the endpoint
You can find the endpoint for your Document Translation resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the document translation resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API key

The API key can be found in the Azure Portal or by running the following Azure CLI command:

```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

#### Create the client with AzureKeyCredential

To use an [API key][cognitive_authentication_api_key] as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documenttranslation import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
document_translation_client = DocumentTranslationClient(endpoint, credential)
```

## Key concepts

Interaction with the Document Translation client library begins with an instance of the `DocumentTranslationClient`.

### DocumentTranslationClient
`DocumentTranslationClient` provides operations for:

 - Creating a translation job to translate documents in your source container(s) and write results to you target container(s)
 - Checking the status of individual documents in the translation job and monitoring each document's progress
 - Enumerating all past and current translation jobs with the option to wait until the job(s) finish
 - Identifying supported glossary and document formats

See the service documentation for [supported languages][supported_languages].

## Examples

The following section provides several code snippets covering some of the most common Document Translation tasks, including:

* [Translate your documents](#translate-your-documents "Translate Your Documents")
* [Check status on individual documents](#check-status-on-individual-documents "Check Status On Individual Documents")
* [List translation jobs](#list-translation-jobs "List Translation Jobs")

### Translate your documents
TODO

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documenttranslation import DocumentTranslationClient, BatchDocumentInput, StorageTarget

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
source_container_sas_url_en = "<container-sas-url-en>"
target_container_sas_url_es = "<container-sas-url-es>"
target_container_sas_url_fr = "<container-sas-url-fr>"

document_translation_client = DocumentTranslationClient(endpoint, credential)

job = document_translation_client.create_translation_job(
    [
        BatchDocumentInput(
            source_url=source_container_sas_url_en,
            targets=[
                StorageTarget(target_url=target_container_sas_url_es, language="es"),
                StorageTarget(target_url=target_container_sas_url_fr, language="fr"),
            ],
        )
    ]
)  # type: JobStatusDetail

job_detail = document_translation_client.wait_until_done(job.id)  # type: JobStatusDetail

print("Job created on: {}".format(job_detail.created_on))
print("Job last updated on: {}".format(job_detail.last_updated_on))
print("Total number of translations on documents: {}".format(job_detail.documents_total_count))

print("Of total documents...")
print("{} failed".format(job_detail.documents_failed_count))
print("{} succeeded".format(job_detail.documents_succeeded_count))
print("{} in progress".format(job_detail.documents_in_progress_count))
print("{} not yet started".format(job_detail.documents_not_yet_started_count))
print("{} cancelled".format(job_detail.documents_cancelled_count))

if job_detail.status == "Succeeded":
    print("Our translation job succeeded")

if job_detail.status == "Failed":
    print("All documents failed in the translation job")

# check document statuses... see next sample
```

### Check status on individual documents
TODO

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documenttranslation import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
job_id = "<job-id>"

document_translation_client = DocumentTranslationClient(endpoint, credential)

docs_to_retry = []
for doc in document_translation_client.list_documents_statuses(job_id):
    if doc.status == "Succeeded":
        print("Document at {} was translated to {} language".format(
            doc.url, doc.translate_to
        ))
    if doc.status == "Failed":
        print("Document ID: {}, Error Code: {}, Message: {}".format(
            doc.id, doc.error.code, doc.error.message
        ))
        if doc.url not in docs_to_retry:
            docs_to_retry.append(doc.source_url)

```

### List translation jobs
TODO

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documenttranslation import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_translation_client = DocumentTranslationClient(endpoint, credential)

jobs = document_translation_client.list_submitted_jobs()  # type: ItemPaged[JobStatusDetail]

for job in jobs:
    if job.status in ["NotStarted", "Running"]:
        job = document_translation_client.wait_until_done(job.id)

    print("Job ID: {}".format(job.id))
    print("Job status: {}".format(job.status))
    print("Job created on: {}".format(job.created_on))
    print("Job last updated on: {}".format(job.last_updated_on))
    print("Total number of translations on documents: {}".format(job.documents_total_count))
    print("Total number of characters charged: {}".format(job.total_characters_charged))

    print("Of total documents...")
    print("{} failed".format(job.documents_failed_count))
    print("{} succeeded".format(job.documents_succeeded_count))
    print("{} in progress".format(job.documents_in_progress_count))
    print("{} not yet started".format(job.documents_not_yet_started_count))
    print("{} cancelled".format(job.documents_cancelled_count))
```


To see how to use the Document Translation client library with Azure Storage Blob to upload documents, create SAS tokens
for your containers, and download the finished translated documents, see this [sample](). Note that you will need to install
the azure-storage-blob library to run this sample:

```bash
pip install azure-storage-blob
```


## Troubleshooting

### General
Document Translation client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging
This library uses the standard
[logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Next steps

The following section provides several code snippets illustrating common patterns used in the Document Translation Python API.

### More sample code

These code samples show common scenario operations with the Azure Document Translation client library.

* Client authentication: TODO


### Async APIs
This library also includes a complete async API supported on Python 3.6+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). Async clients
are found under the `azure.ai.documenttranslation.aio` namespace.

* Client authentication: TODO


### Additional documentation

For more extensive documentation on Azure Cognitive Services Document Translation, see the [Document Translation documentation][python-dt-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-dt-src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/documenttranslation/azure-ai-documenttranslation/azure/ai/documenttranslation
[python-dt-pypi]: https://pypi.org/project/azure-ai-documenttranslation/
[python-dt-product-docs]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview
[python-dt-ref-docs]: https://aka.ms/azsdk/python/documenttranslation/docs
[python-dt-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/documenttranslation/azure-ai-documenttranslation/samples

[azure_subscription]: https://azure.microsoft.com/free/
[DT_resource]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=python
[single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_DT_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextTranslation
[azure_cli_create_DT_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[supported_languages]: https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate

[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource

[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
