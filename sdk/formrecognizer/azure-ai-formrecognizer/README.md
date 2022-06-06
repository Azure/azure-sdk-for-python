# Azure Form Recognizer client library for Python

Azure Cognitive Services Form Recognizer is a cloud service that uses machine learning to analyze text and structured data from your documents. It includes the following main features:

- Layout - Extract content and structure (ex. words, selection marks, tables) from documents.
- Document - Analyze key-value pairs in addition to general layout from documents.
- Read - Read page information and detected languages from documents.
- Prebuilt - Extract common field values from select document types (ex. receipts, invoices, business cards, ID documents, U.S. W-2 tax documents) using prebuilt models.
- Custom - Build custom models from your own data to extract tailored field values in addition to general layout from documents.

[Source code][python-fr-src] | [Package (PyPI)][python-fr-pypi] | [API reference documentation][python-fr-ref-docs] | [Product documentation][python-fr-product-docs] | [Samples][python-fr-samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_

## Getting started

### Prerequisites
* Python 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Cognitive Services or Form Recognizer resource][FR_or_CS_resource] to use this package.

### Install the package
Install the Azure Form Recognizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-formrecognizer --pre
```

> Note: This version of the client library defaults to the `2022-06-30-preview` version of the service.

This table shows the relationship between SDK versions and supported API versions of the service:

|SDK version|Supported API version of service
|-|-
|3.2.0b5 - Latest beta release | 2.0, 2.1, 2022-06-30-preview
|3.1.X - Latest GA release| 2.0, 2.1 (default)
|3.0.0| 2.0

> Note: Starting with version `3.2.X`, a new set of clients were introduced to leverage the newest features
> of the Form Recognizer service. Please see the [Migration Guide][migration-guide] for detailed instructions on how to update application
> code from client library version `3.1.X` or lower to the latest version. Additionally, see the [Changelog][changelog] for more detailed information.
> The below table describes the relationship of each client and its supported API version(s):

|API version|Supported clients
|-|-
|2022-06-30-preview | DocumentAnalysisClient and DocumentModelAdministrationClient
|2.1 | FormRecognizerClient and FormTrainingClient
|2.0 | FormRecognizerClient and FormTrainingClient

#### Create a Cognitive Services or Form Recognizer resource
Form Recognizer supports both [multi-service and single-service access][cognitive_resource_portal]. Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Form Recognizer access only, create a Form Recognizer resource. Please note that you will need a single-service resource if you intend to use [Azure Active Directory authentication](#create-the-client-with-an-azure-active-directory-credential).

You can create either resource using: 

* Option 1: [Azure Portal][cognitive_resource_portal].
* Option 2: [Azure CLI][cognitive_resource_cli].

Below is an example of how you can create a Form Recognizer resource using the CLI:

```PowerShell
# Create a new resource group to hold the form recognizer resource
# if using an existing resource group, skip this step
az group create --name <your-resource-name> --location <location>
```

```PowerShell
# Create form recognizer
az cognitiveservices account create \
    --name <your-resource-name> \
    --resource-group <your-resource-group-name> \
    --kind FormRecognizer \
    --sku <sku> \
    --location <location> \
    --yes
```

For more information about creating the resource or how to get the location and sku information see [here][cognitive_resource_cli].

### Authenticate the client
In order to interact with the Form Recognizer service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


#### Get the endpoint
You can find the endpoint for your Form Recognizer resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the form recognizer resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

Either a regional endpoint or a custom subdomain can be used for authentication. They are formatted as follows:

```
Regional endpoint: https://<region>.api.cognitive.microsoft.com/
Custom subdomain: https://<resource-name>.cognitiveservices.azure.com/
```

A regional endpoint is the same for every resource in a region. A complete list of supported regional endpoints can be consulted [here][regional_endpoints]. Please note that regional endpoints do not support AAD authentication.

A custom subdomain, on the other hand, is a name that is unique to the Form Recognizer resource. They can only be used by [single-service resources][cognitive_resource_portal].

#### Get the API key

The API key can be found in the [Azure Portal][azure_portal] or by running the following Azure CLI command:

```bash
az cognitiveservices account keys list --name "<resource-name>" --resource-group "<resource-group-name>"
```

#### Create the client with AzureKeyCredential

To use an [API key][cognitive_authentication_api_key] as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
document_analysis_client = DocumentAnalysisClient(endpoint, credential)
```

#### Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

You will also need to [register a new AAD application and grant access][register_aad_app] to Form Recognizer by assigning the `"Cognitive Services User"` role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

credential = DefaultAzureCredential()
document_analysis_client = DocumentAnalysisClient(
    endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
    credential=credential
)
```

## Key concepts

### DocumentAnalysisClient
`DocumentAnalysisClient` provides operations for analyzing input documents using prebuilt and custom models through the `begin_analyze_document` and `begin_analyze_document_from_url` APIs.
Use the `model` parameter to select the type of model for analysis.

|Model| Features
|-|-
|`prebuilt-layout`| Text extraction, selection marks, tables
|`prebuilt-document`| Text extraction, selection marks, tables, and key-value pairs
|`prebuilt-read`|Text extraction and detected languages
|`prebuilt-invoices`| Text extraction, selection marks, tables, and pre-trained fields and values pertaining to English invoices
|`prebuilt-businessCard`| Text extraction and pre-trained fields and values pertaining to English business cards
|`prebuilt-idDocument`| Text extraction and pre-trained fields and values pertaining to US driver licenses and international passports
|`prebuilt-receipt`| Text extraction and pre-trained fields and values pertaining to English sales receipts
|`prebuilt-tax.us.w2`| Text extraction and pre-trained fields and values pertaining to U.S. W-2 tax documents
|`{custom-model-id}`| Text extraction, selection marks, tables, labeled fields and values from your custom documents

Sample code snippets are provided to illustrate using a DocumentAnalysisClient [here](#examples "Examples").
More information about analyzing documents, including supported features, locales, and document types can be found in the [service documentation][fr-models].

### DocumentModelAdministrationClient
`DocumentModelAdministrationClient` provides operations for:

- Building custom models to analyze specific fields you specify by labeling your custom documents. A `DocumentModel` is returned indicating the document type(s) the model can analyze, as well as the estimated confidence for each field. See the [service documentation][fr-build-model] for a more detailed explanation.
- Creating a composed model from a collection of existing models.
- Managing models created in your account.
- Listing document model operations or getting a specific model operation created within the last 24 hours.
- Copying a custom model from one Form Recognizer resource to another.

Please note that models can also be built using a graphical user interface such as [Form Recognizer Studio][fr-studio].

Sample code snippets are provided to illustrate using a DocumentModelAdministrationClient [here](#examples "Examples").

### Long-running operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that analyze documents, build models, or copy/compose models are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an `LROPoller` or `AsyncLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").


## Examples

The following section provides several code snippets covering some of the most common Form Recognizer tasks, including:

* [Extract Layout](#extract-layout "Extract Layout")
* [Using the General Document Model](#using-the-general-document-model "Using the General Document Model")
* [Using Prebuilt Models](#using-prebuilt-models "Using Prebuilt Models")
* [Build a Custom Model](#build-a-custom-model "Build a custom model")
* [Analyze Documents Using a Custom Model](#analyze-documents-using-a-custom-model "Analyze Documents Using a Custom Model")
* [Manage Your Models](#manage-your-models "Manage Your Models")


### Extract Layout
Extract text, selection marks, text styles, and table structures, along with their bounding region coordinates, from documents.

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_analysis_client = DocumentAnalysisClient(endpoint, credential)

with open("<path to your document>", "rb") as fd:
    document = fd.read()

poller = document_analysis_client.begin_analyze_document("prebuilt-layout", document)
result = poller.result()

for page in result.pages:
    print("----Analyzing layout from page #{}----".format(page.page_number))
    print(
        "Page has width: {} and height: {}, measured with unit: {}".format(
            page.width, page.height, page.unit
        )
    )

    for line_idx, line in enumerate(page.lines):
        print(
            "...Line # {} has content '{}' within bounding polygon '{}'".format(
                line_idx,
                line.content,
                line.polygon,
            )
        )

    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content, word.confidence
            )
        )

    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' within bounding polygon '{}' and has a confidence of {}".format(
                selection_mark.state,
                selection_mark.polygon,
                selection_mark.confidence,
            )
        )

for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
            table_idx, table.row_count, table.column_count
        )
    )
    for region in table.bounding_regions:
        print(
            "Table # {} location on page: {} is {}".format(
                table_idx,
                region.page_number,
                region.polygon
            )
        )
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
                cell.row_index,
                cell.column_index,
                cell.content,
            )
        )
```

### Using the General Document Model
Analyze key-value pairs, tables, styles, and selection marks from documents using the general document model provided by the Form Recognizer service.
Select the General Document Model by passing `model="prebuilt-document"` into the `begin_analyze_document` method:

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_analysis_client = DocumentAnalysisClient(endpoint, credential)

with open("<path to your document>", "rb") as fd:
    document = fd.read()

poller = document_analysis_client.begin_analyze_document("prebuilt-document", document)
result = poller.result()

print("----Key-value pairs found in document----")
for kv_pair in result.key_value_pairs:
    if kv_pair.key:
        print(
                "Key '{}' found within '{}' bounding regions".format(
                    kv_pair.key.content,
                    kv_pair.key.bounding_regions,
                )
            )
    if kv_pair.value:
        print(
                "Value '{}' found within '{}' bounding regions\n".format(
                    kv_pair.value.content,
                    kv_pair.value.bounding_regions,
                )
            )

print("----Tables found in document----")
for table_idx, table in enumerate(result.tables):
    print(
        "Table # {} has {} rows and {} columns".format(
            table_idx, table.row_count, table.column_count
        )
    )
    for region in table.bounding_regions:
        print(
            "Table # {} location on page: {} is {}".format(
                table_idx,
                region.page_number,
                region.polygon,
            )
        )

print("----Styles found in document----")
for style in result.styles:
    if style.is_handwritten:
        print("Document contains handwritten content: ")
        print(",".join([result.content[span.offset:span.offset + span.length] for span in style.spans]))

for page in result.pages:
    print("----Analyzing document from page #{}----".format(page.page_number))
    print(
        "Page has width: {} and height: {}, measured with unit: {}".format(
            page.width, page.height, page.unit
        )
    )

    for line_idx, line in enumerate(page.lines):
        words = line.get_words()
        print(
            "...Line # {} has {} words and text '{}' within bounding polygon '{}'".format(
                line_idx,
                len(words),
                line.content,
                line.polygon,
            )
        )

        for word in words:
            print(
                "......Word '{}' has a confidence of {}".format(
                    word.content, word.confidence
                )
            )

    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' within bounding polygon '{}' and has a confidence of {}".format(
                selection_mark.state,
                selection_mark.polygon,
                selection_mark.confidence,
            )
        )
```

- Read more about the features provided by the `prebuilt-document` model [here][service_prebuilt_document].

### Using Prebuilt Models
Extract fields from select document types such as receipts, invoices, business cards, identity documents, and U.S. W-2 tax documents using prebuilt models provided by the Form Recognizer service.

For example, to analyze fields from a sales receipt, use the prebuilt receipt model provided by passing `model="prebuilt-receipt"` into the `begin_analyze_document` method:

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_analysis_client = DocumentAnalysisClient(endpoint, credential)

with open("<path to your receipt>", "rb") as fd:
    receipt = fd.read()

poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", receipt)
result = poller.result()

for receipt in result.documents:
    for name, field in receipt.fields.items():
        if name == "Items":
            print("Receipt Items:")
            for idx, item in enumerate(field.value):
                print("...Item #{}".format(idx+1))
                for item_field_name, item_field in item.value.items():
                    print("......{}: {} has confidence {}".format(
                        item_field_name, item_field.value, item_field.confidence))
        else:
            print("{}: {} has confidence {}".format(name, field.value, field.confidence))
```

You are not limited to receipts! There are a few prebuilt models to choose from, each of which has its own set of supported fields:
- Analyze receipts using the `prebuilt-receipt` model (fields recognized by the service can be found [here][service_recognize_receipt])
- Analyze business cards using the `prebuilt-businessCard` model (fields recognized by the service can be found [here][service_recognize_business_cards]).
- Analyze invoices using the `prebuilt-invoice` model (fields recognized by the service can be found [here][service_recognize_invoice]).
- Analyze identity documents using the `prebuilt-idDocuments` model (fields recognized by the service can be found [here][service_recognize_identity_documents]).
- Analyze U.S. W-2 tax documents using the `prebuilt-tax.us.w2` model (fields recognized by the service can be found [here][service_recognize_tax_documents]).

### Build a Custom Model
Build a custom model on your own document type. The resulting model can be used to analyze values from the types of documents it was trained on.
Provide a container SAS URL to your Azure Storage Blob container where you're storing the training documents.

More details on setting up a container and required file structure can be found in the [service documentation][fr-build-training-set].

```python
from azure.ai.formrecognizer import DocumentModelAdministrationClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_model_admin_client = DocumentModelAdministrationClient(endpoint, credential)

container_sas_url = "<container-sas-url>"  # training documents uploaded to blob storage
poller = document_model_admin_client.begin_build_model(
    # For more information about build_mode, see: https://aka.ms/azsdk/formrecognizer/buildmode
    source=container_sas_url, build_mode="template", model_id="my-first-model"
)
model = poller.result()

print("Model ID: {}".format(model.model_id))
print("Description: {}".format(model.description))
print("Model created on: {}\n".format(model.created_on))
print("Doc types the model can recognize:")
for name, doc_type in model.doc_types.items():
    print("\nDoc Type: '{}' which has the following fields:".format(name))
    for field_name, confidence in doc_type.field_confidence.items():
        print("Field: '{}' has confidence score {}".format(field_name, confidence))
```


### Analyze Documents Using a Custom Model
Analyze document fields, tables, selection marks, and more. These models are trained with your own data, so they're tailored to your documents.
For best results, you should only analyze documents of the same document type that the custom model was built with.

```python
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_analysis_client = DocumentAnalysisClient(endpoint, credential)
model_id = "<your custom model id>"

with open("<path to your document>", "rb") as fd:
    document = fd.read()

poller = document_analysis_client.begin_analyze_document(model=model_id, document=document)
result = poller.result()

for analyzed_document in result.documents:
    print("Document was analyzed by model with ID {}".format(result.model_id))
    print("Document has confidence {}".format(analyzed_document.confidence))
    for name, field in analyzed_document.fields.items():
        print("Field '{}' has value '{}' with confidence of {}".format(name, field.value, field.confidence))
    
# iterate over lines, words, and selection marks on each page of the document
for page in result.pages:
    print("\nLines found on page {}".format(page.page_number))
    for line in page.lines:
        print("...Line '{}'".format(line.content))
    print("\nWords found on page {}".format(page.page_number))
    for word in page.words:
        print(
            "...Word '{}' has a confidence of {}".format(
                word.content, word.confidence
            )
        )
    print("\nSelection marks found on page {}".format(page.page_number))
    for selection_mark in page.selection_marks:
        print(
            "...Selection mark is '{}' and has a confidence of {}".format(
                selection_mark.state, selection_mark.confidence
            )
        )

# iterate over tables in document
for i, table in enumerate(result.tables):
    print("\nTable {} can be found on page:".format(i + 1))
    for region in table.bounding_regions:
        print("...{}".format(region.page_number))
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
                cell.row_index, cell.column_index, cell.content
            )
        )
```

Alternatively, a document URL can also be used to analyze documents using the `begin_analyze_document_from_url` method.

```python
document_url = "<url_of_the_document>"
poller = document_analysis_client.begin_analyze_document_from_url(model=model_id, document_url=document_url)
result = poller.result()
```

### Manage Your Models
Manage the custom models attached to your account.

```python
from azure.ai.formrecognizer import DocumentModelAdministrationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_model_admin_client = DocumentModelAdministrationClient(endpoint, credential)

account_info = document_model_admin_client.get_account_info()
print("Our account has {} custom models, and we can have at most {} custom models".format(
    account_info.document_model_count, account_info.document_model_limit
))

# Here we get a paged list of all of our models
models = document_model_admin_client.list_models()
print("We have models with the following ids: {}".format(
    ", ".join([m.model_id for m in models])
))

# Replace with the custom model ID from the "Build a model" sample
model_id = "<model_id from the Build a Model sample>"

custom_model = document_model_admin_client.get_model(model_id=model_id)
print("Model ID: {}".format(custom_model.model_id))
print("Description: {}".format(custom_model.description))
print("Model created on: {}\n".format(custom_model.created_on))

# Finally, we will delete this model by ID
document_model_admin_client.delete_model(model_id=custom_model.model_id)

try:
    document_model_admin_client.get_model(model_id=custom_model.model_id)
except ResourceNotFoundError:
    print("Successfully deleted model with id {}".format(custom_model.model_id))
```

## Troubleshooting

### General
Form Recognizer client library will raise exceptions defined in [Azure Core][azure_core_exceptions].
Error codes and messages raised by the Form Recognizer service can be found in the [service documentation][fr-errors].

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

### More sample code

See the [Sample README][sample_readme] for several code snippets illustrating common patterns used in the Form Recognizer Python API.

### Additional documentation

For more extensive documentation on Azure Cognitive Services Form Recognizer, see the [Form Recognizer documentation][python-fr-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-fr-src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer
[python-fr-pypi]: https://pypi.org/project/azure-ai-formrecognizer/
[python-fr-product-docs]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/overview
[python-fr-ref-docs]: https://aka.ms/azsdk/python/formrecognizer/docs
[python-fr-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples

[azure_subscription]: https://azure.microsoft.com/free/
[azure_portal]: https://ms.portal.azure.com/
[regional_endpoints]: https://azure.microsoft.com/global-infrastructure/services/?products=azure-applied-ai-services
[FR_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[cognitive_resource_portal]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer
[cognitive_resource_cli]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[labeling-tool]: https://aka.ms/azsdk/formrecognizer/labelingtool
[fr-studio]: https://aka.ms/azsdk/formrecognizer/formrecognizerstudio
[fr-build-model]: https://aka.ms/azsdk/formrecognizer/buildmodel
[fr-build-training-set]: https://aka.ms/azsdk/formrecognizer/buildtrainingset
[fr-models]: https://aka.ms/azsdk/formrecognizer/models
[fr-errors]: https://aka.ms/azsdk/formrecognizer/errors

[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[service_recognize_receipt]: https://aka.ms/azsdk/formrecognizer/receiptfieldschema
[service_recognize_business_cards]: https://aka.ms/azsdk/formrecognizer/businesscardfieldschema
[service_recognize_invoice]: https://aka.ms/azsdk/formrecognizer/invoicefieldschema
[service_recognize_identity_documents]: https://aka.ms/azsdk/formrecognizer/iddocumentfieldschema
[service_recognize_tax_documents]: https://aka.ms/azsdk/formrecognizer/taxusw2fieldschema
[service_prebuilt_document]: https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/concept-general-document#general-document-features
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[sample_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/samples
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/CHANGELOG.md
[migration-guide]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/formrecognizer/azure-ai-formrecognizer/MIGRATION_GUIDE.md

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
