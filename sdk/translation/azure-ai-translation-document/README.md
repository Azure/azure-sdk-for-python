# Azure Document Translation client library for Python

Azure Cognitive Services Document Translation is a cloud service that can be used to translate multiple and complex documents across languages and dialects while preserving original document structure and data format.
Use the client library for Document Translation to:

* Translate numerous, large files from an Azure Blob Storage container to a target container in your language of choice.
* Check the translation status and progress of each document in the translation operation.
* Apply a custom translation model or glossaries to tailor translation to your specific case.

[Source code][python-dt-src] | [Package (PyPI)][python-dt-pypi] | [API reference documentation][python-dt-ref-docs] | [Product documentation][python-dt-product-docs] | [Samples][python-dt-samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites
* Python 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Translator resource][DT_resource] to use this package.

### Install the package
Install the Azure Document Translation client library for Python with [pip][pip]:

```bash
pip install azure-ai-translation-document
```

> Note: This version of the client library defaults to the v1.0 version of the service

#### Create a Translator resource
The Document Translation feature supports [single-service access][single_service] only.
To access the service, create a Translator resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_DT_resource]

**Option 2:** [Azure CLI][azure_cli_create_DT_resource].
Below is an example of how you can create a Translator resource using the CLI:

```bash
# Create a new resource group to hold the Translator resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2
```

```bash
# Create document translation
az cognitiveservices account create \
    --name document-translation-resource \
    --custom-domain document-translation-resource \
    --resource-group my-resource-group \
    --kind TextTranslation \
    --sku S1 \
    --location westus2 \
    --yes
```

### Authenticate the client
In order to interact with the Document Translation feature service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


#### Looking up the endpoint
You can find the endpoint for your Translator resource using the
[Azure Portal][azure_portal_get_endpoint].

> Note that the service requires a custom domain endpoint. Follow the instructions in the above link to format your endpoint:
> https://{NAME-OF-YOUR-RESOURCE}.cognitiveservices.azure.com/

#### Get the API key

The API key can be found in the Azure Portal or by running the following Azure CLI command:

```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

#### Create the client with AzureKeyCredential

To use an [API key][cognitive_authentication_api_key] as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
document_translation_client = DocumentTranslationClient(endpoint, credential)
```

#### Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

You will also need to [register a new AAD application and grant access][register_aad_app] to your
Translator resource by assigning the `"Cognitive Services User"` role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.translation.document import DocumentTranslationClient
credential = DefaultAzureCredential()

document_translation_client = DocumentTranslationClient(
    endpoint="https://<resource-name>.cognitiveservices.azure.com/",
    credential=credential
)
```

## Key concepts

The Document Translation service requires that you upload your files to an Azure Blob Storage source container and provide
a target container where the translated documents can be written. Additional information about setting this up can be found in
the service documentation:

- [Set up Azure Blob Storage containers][source_containers] with your documents
- Optionally apply [glossaries][glossary] or a [custom model for translation][custom_model]
- Allow access to your storage account with either of the following options:
    - Generate [SAS tokens][sas_token] to your containers (or files) with the appropriate [permissions][sas_token_permissions]
    - Create and use a [managed identity][managed_identity] to grant access to your storage account

### DocumentTranslationClient

Interaction with the Document Translation client library begins with an instance of the `DocumentTranslationClient`.
The client provides operations for:

 - Creating a translation operation to translate documents in your source container(s) and write results to you target container(s).
 - Checking the status of individual documents in the translation operation and monitoring each document's progress.
 - Enumerating all past and current translation operations.
 - Identifying supported glossary and document formats.

### Translation Input

Input to the `begin_translation` client method can be provided in two different ways:

1) A single source container with documents can be translated to a different language:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

document_translation_client = DocumentTranslationClient("<endpoint>", AzureKeyCredential("<api_key>"))
poller = document_translation_client.begin_translation("<sas_url_to_source>", "<sas_url_to_target>", "<target_language>")
```

2) Or multiple different sources can be provided each with their own targets.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget

my_input = [
    DocumentTranslationInput(
        source_url="<sas_url_to_source_A>",
        targets=[
            TranslationTarget(target_url="<sas_url_to_target_fr>", language="fr"),
            TranslationTarget(target_url="<sas_url_to_target_de>", language="de")
        ]
    ),
    DocumentTranslationInput(
        source_url="<sas_url_to_source_B>",
        targets=[
            TranslationTarget(target_url="<sas_url_to_target_fr>", language="fr"),
            TranslationTarget(target_url="<sas_url_to_target_de>", language="de")
        ]
    ),
    DocumentTranslationInput(
        source_url="<sas_url_to_source_C>",
        targets=[
            TranslationTarget(target_url="<sas_url_to_target_fr>", language="fr"),
            TranslationTarget(target_url="<sas_url_to_target_de>", language="de")
        ]
    )
]

document_translation_client = DocumentTranslationClient("<endpoint>", AzureKeyCredential("<api_key>"))
poller = document_translation_client.begin_translation(my_input)
```

> Note: the target_url for each target language must be unique.

To translate documents under a folder, or only translate certain documents, see [sample_begin_translation_with_filters.py][sample_begin_translation_with_filters].
See the service documentation for all [supported languages][supported_languages].

### Long-Running Operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that translate documents are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns a `DocumentTranslationLROPoller` or `AsyncDocumentTranslationLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Examples

The following section provides several code snippets covering some of the most common Document Translation tasks, including:

* [Translate your documents](#translate-your-documents "Translate Your Documents")
* [Translate multiple inputs](#translate-multiple-inputs "Translate Multiple Inputs")
* [List translation operations](#list-translation-operations "List Translation Operations")

### Translate your documents
Translate all the documents in your source container to the target container. To translate documents under a folder, or only translate certain documents, see [sample_begin_translation_with_filters.py][sample_begin_translation_with_filters].

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
source_container_sas_url_en = "<sas-url-en>"
target_container_sas_url_es = "<sas-url-es>"

document_translation_client = DocumentTranslationClient(endpoint, credential)

poller = document_translation_client.begin_translation(source_container_sas_url_en, target_container_sas_url_es, "es")

result = poller.result()

print(f"Status: {poller.status()}")
print(f"Created on: {poller.details.created_on}")
print(f"Last updated on: {poller.details.last_updated_on}")
print(f"Total number of translations on documents: {poller.details.documents_total_count}")

print("\nOf total documents...")
print(f"{poller.details.documents_failed_count} failed")
print(f"{poller.details.documents_succeeded_count} succeeded")

for document in result:
    print(f"Document ID: {document.id}")
    print(f"Document status: {document.status}")
    if document.status == "Succeeded":
        print(f"Source document location: {document.source_document_url}")
        print(f"Translated document location: {document.translated_document_url}")
        print(f"Translated to language: {document.translated_to}\n")
    else:
        print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")
```

### Translate multiple inputs
Begin translating with documents in multiple source containers to multiple target containers in different languages.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
source_container_sas_url_de = "<sas-url-de>"
source_container_sas_url_en = "<sas-url-en>"
target_container_sas_url_es = "<sas-url-es>"
target_container_sas_url_fr = "<sas-url-fr>"
target_container_sas_url_ar = "<sas-url-ar>"

document_translation_client = DocumentTranslationClient(endpoint, credential)

poller = document_translation_client.begin_translation(
    [
        DocumentTranslationInput(
            source_url=source_container_sas_url_en,
            targets=[
                TranslationTarget(target_url=target_container_sas_url_es, language="es"),
                TranslationTarget(target_url=target_container_sas_url_fr, language="fr"),
            ],
        ),
        DocumentTranslationInput(
            source_url=source_container_sas_url_de,
            targets=[
                TranslationTarget(target_url=target_container_sas_url_ar, language="ar"),
            ],
        )
    ]
)

result = poller.result()

for document in result:
    print(f"Document ID: {document.id}")
    print(f"Document status: {document.status}")
    if document.status == "Succeeded":
        print(f"Source document location: {document.source_document_url}")
        print(f"Translated document location: {document.translated_document_url}")
        print(f"Translated to language: {document.translated_to}\n")
    else:
        print(f"Error Code: {document.error.code}, Message: {document.error.message}\n")
```

### List translation operations
Enumerate over the translation operations submitted for the resource.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import DocumentTranslationClient

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_translation_client = DocumentTranslationClient(endpoint, credential)

operations = document_translation_client.list_translation_statuses()  # type: ItemPaged[TranslationStatus]

for operation in operations:
    print(f"\nID: {operation.id}")
    print(f"Status: {operation.status}")
    print(f"Created on: {operation.created_on}")
    print(f"Last updated on: {operation.last_updated_on}")
    print(f"Total number of translations on documents: {operation.documents_total_count}")
    print(f"Total number of characters charged: {operation.total_characters_charged}")

    print("Of total documents...")
    print(f"{operation.documents_failed_count} failed")
    print(f"{operation.documents_succeeded_count} succeeded")
    print(f"{operation.documents_canceled_count} canceled")
```

To see how to use the Document Translation client library with Azure Storage Blob to upload documents, create SAS tokens
for your containers, and download the finished translated documents, see this [sample][sample_translation_with_azure_blob].
Note that you will need to install the [azure-storage-blob][azure_storage_blob] library to run this sample.

## Advanced Topics

The following section provides some insights for some advanced translation features such as glossaries and custom translation models.

### **Glossaries**
Glossaries are domain-specific dictionaries. For example, if you want to translate some medical-related documents, you may need support for the many words, terminology, and idioms in the medical field which you can't find in the standard translation dictionary, or you simply need specific translation. This is why Document Translation provides support for glossaries. 

#### **How To Create Glossary File**

Document Translation supports glossaries in the following formats:

|**File Type**|**Extension**|**Description**|**Samples**|
|---------------|---------------|---------------|---------------|
|Tab-Separated Values/TAB|.tsv, .tab|Read more on [wikipedia][tsv_files_wikipedia]|[glossary_sample.tsv][sample_tsv_file]|
|Comma-Separated Values|.csv|Read more on [wikipedia][csv_files_wikipedia]|[glossary_sample.csv][sample_csv_file]|
|Localization Interchange File Format|.xlf, .xliff|Read more on [wikipedia][xlf_files_wikipedia]|[glossary_sample.xlf][sample_xlf_file]|

View all supported formats [here][supported_glossary_formats].

#### **How Use Glossaries in Document Translation**
In order to use glossaries with Document Translation, you first need to upload your glossary file to a blob container, and then provide the SAS URL to the file as in the code samples [sample_translation_with_glossaries.py][sample_translation_with_glossaries].

### **Custom Translation Models**
Instead of using Document Translation's engine for translation, you can use your own custom Azure machine/deep learning model.
 
#### **How To Create a Custom Translation Model**
For more info on how to create, provision, and deploy your own custom Azure translation model, please follow the instructions here: [Build, deploy, and use a custom model for translation][custom_translation_article]

#### **How To Use a Custom Translation Model With Document Translation**
In order to use a custom translation model with Document Translation, you first 
need to create and deploy your model, then follow the code sample [sample_translation_with_custom_model.py][sample_translation_with_custom_model] to use with Document Translation.


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

The following section provides several code snippets illustrating common patterns used in the Document Translation Python client library.
More samples can be found under the [samples][samples] directory.

### More sample code

These code samples show common scenario operations with the Azure Document Translation client library.

* Client authentication: [sample_authentication.py][sample_authentication]
* Begin translating documents: [sample_begin_translation.py][sample_begin_translation]
* Translate with multiple inputs: [sample_translate_multiple_inputs.py][sample_translate_multiple_inputs]
* Check the status of documents: [sample_check_document_statuses.py][sample_check_document_statuses]
* List all submitted translation operations: [sample_list_translations.py][sample_list_translations]
* Apply a custom glossary to translation: [sample_translation_with_glossaries.py][sample_translation_with_glossaries]
* Use Azure Blob Storage to set up translation resources: [sample_translation_with_azure_blob.py][sample_translation_with_azure_blob]


### Async samples
This library also includes a complete set of async APIs. To use them, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). Async clients
are found under the `azure.ai.translation.document.aio` namespace.

* Client authentication: [sample_authentication_async.py][sample_authentication_async]
* Begin translating documents: [sample_begin_translation_async.py][sample_begin_translation_async]
* Translate with multiple inputs: [sample_translate_multiple_inputs_async.py][sample_translate_multiple_inputs_async]
* Check the status of documents: [sample_check_document_statuses_async.py][sample_check_document_statuses_async]
* List all submitted translation operations: [sample_list_translations_async.py][sample_list_translations_async]
* Apply a custom glossary to translation: [sample_translation_with_glossaries_async.py][sample_translation_with_glossaries_async]
* Use Azure Blob Storage to set up translation resources: [sample_translation_with_azure_blob_async.py][sample_translation_with_azure_blob_async]

### Additional documentation

For more extensive documentation on Azure Cognitive Services Document Translation, see the [Document Translation documentation][python-dt-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-dt-src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/azure/ai/translation/document
[python-dt-pypi]: https://aka.ms/azsdk/python/texttranslation/pypi
[python-dt-product-docs]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview
[python-dt-ref-docs]: https://aka.ms/azsdk/python/documenttranslation/docs
[python-dt-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples

[azure_subscription]: https://azure.microsoft.com/free/
[DT_resource]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=python
[single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_DT_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextTranslation
[azure_cli_create_DT_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[supported_languages]: https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
[source_containers]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=csharp#create-azure-blob-storage-containers
[custom_model]: https://docs.microsoft.com/azure/cognitive-services/translator/custom-translator/quickstart-build-deploy-custom-model
[glossary]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview#supported-glossary-formats
[sas_token]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/create-sas-tokens?tabs=Containers#create-your-sas-tokens-with-azure-storage-explorer
[sas_token_permissions]: https://aka.ms/azsdk/documenttranslation/sas-permissions
[azure_storage_blob]: https://pypi.org/project/azure-storage-blob/

[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=csharp#get-your-custom-domain-name-and-subscription-key
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/get-started-with-document-translation?tabs=csharp#get-your-subscription-key
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication?tabs=powershell#authenticate-with-azure-active-directory
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[managed_identity]: https://aka.ms/azsdk/documenttranslation/managed-identity
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/sdk/azure-sdk-logging

[samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_authentication_async.py
[sample_begin_translation]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation.py
[sample_begin_translation_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_begin_translation_async.py
[sample_translate_multiple_inputs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_translate_multiple_inputs.py
[sample_translate_multiple_inputs_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translate_multiple_inputs_async.py
[sample_check_document_statuses]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_check_document_statuses.py
[sample_check_document_statuses_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_check_document_statuses_async.py
[sample_list_translations]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_list_translations.py
[sample_list_translations_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_list_translations_async.py
[sample_translation_with_glossaries]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_glossaries.py
[sample_translation_with_glossaries_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_glossaries_async.py
[sample_translation_with_azure_blob]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_azure_blob.py
[sample_translation_with_azure_blob_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_azure_blob_async.py
[sample_translation_with_custom_model]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_translation_with_custom_model.py
[sample_translation_with_custom_model_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/async_samples/sample_translation_with_custom_model_async.py
[sample_begin_translation_with_filters]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/sample_begin_translation_with_filters.py

[supported_glossary_formats]: https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview#supported-glossary-formats
[custom_translation_article]: https://docs.microsoft.com/azure/cognitive-services/translator/custom-translator/quickstart-build-deploy-custom-model
[tsv_files_wikipedia]: https://wikipedia.org/wiki/Tab-separated_values
[xlf_files_wikipedia]: https://wikipedia.org/wiki/XLIFF
[csv_files_wikipedia]: https://wikipedia.org/wiki/Comma-separated_values
[sample_tsv_file]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/assets/glossary_sample.tsv
[sample_csv_file]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/assets/glossary_sample.csv
[sample_xlf_file]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/translation/azure-ai-translation-document/samples/assets/glossary_sample.xlf

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
