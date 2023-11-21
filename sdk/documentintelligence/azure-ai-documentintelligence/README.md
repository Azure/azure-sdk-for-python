
# Azure AI Document Intelligence client library for Python
Azure AI Document Intelligence ([previously known as Form Recognizer][service-rename]) is a cloud service that uses machine learning to analyze text and structured data from your documents. It includes the following main features:

- Layout - Extract content and structure (ex. words, selection marks, tables) from documents.
- Document - Analyze key-value pairs in addition to general layout from documents.
- Read - Read page information from documents.
- Prebuilt - Extract common field values from select document types (ex. receipts, invoices, business cards, ID documents, U.S. W-2 tax documents, among others) using prebuilt models.
- Custom - Build custom models from your own data to extract tailored field values in addition to general layout from documents.
- Classifiers - Build custom classification models that combine layout and language features to accurately detect and identify documents you process within your application.
- Add-on capabilities - Extract barcodes/QR codes, formulas, font/style, etc. or enable high resolution mode for large documents with optional parameters.


## Getting started

### Installating the package

```bash
python -m pip install azure-ai-documentintelligence
```

#### Prequisites

- Python 3.7 or later is required to use this package.
- You need an [Azure subscription][azure_sub] to use this package.
- An existing Azure AI Document Intelligence instance.

#### Create a Cognitive Services or Document Intelligence resource

Document Intelligence supports both [multi-service and single-service access][cognitive_resource_portal]. Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Document Intelligence access only, create a Document Intelligence resource. Please note that you will need a single-service resource if you intend to use [Azure Active Directory authentication](#create-the-client-with-an-azure-active-directory-credential).

You can create either resource using: 

* Option 1: [Azure Portal][cognitive_resource_portal].
* Option 2: [Azure CLI][cognitive_resource_cli].

Below is an example of how you can create a Document Intelligence resource using the CLI:

```PowerShell
# Create a new resource group to hold the Document Intelligence resource
# if using an existing resource group, skip this step
az group create --name <your-resource-name> --location <location>
```

```PowerShell
# Create the Document Intelligence resource
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

In order to interact with the Document Intelligence service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.

#### Get the endpoint

You can find the endpoint for your Document Intelligence resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the Document Intelligence resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

Either a regional endpoint or a custom subdomain can be used for authentication. They are formatted as follows:

```
Regional endpoint: https://<region>.api.cognitive.microsoft.com/
Custom subdomain: https://<resource-name>.cognitiveservices.azure.com/
```

A regional endpoint is the same for every resource in a region. A complete list of supported regional endpoints can be consulted [here][regional_endpoints]. Please note that regional endpoints do not support AAD authentication.

A custom subdomain, on the other hand, is a name that is unique to the Document Intelligence resource. They can only be used by [single-service resources][cognitive_resource_portal].

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
from azure.ai.documentintelligence import DocumentIntelligenceClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")
document_analysis_client = DocumentIntelligenceClient(endpoint, credential)
```

#### Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

You will also need to [register a new AAD application and grant access][register_aad_app] to Document Intelligence by assigning the `"Cognitive Services User"` role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
"""DefaultAzureCredential will use the values from these environment
variables: AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
"""
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
credential = DefaultAzureCredential()

document_analysis_client = DocumentIntelligenceClient(endpoint, credential)
```

## Key concepts

### DocumentIntelligenceClient

`DocumentIntelligenceClient` provides operations for analyzing input documents using prebuilt and custom models through the `begin_analyze_document` API.
Use the `model_id` parameter to select the type of model for analysis. See a full list of supported models [here][di-models]. 
The `DocumentIntelligenceClient` also provides operations for classifying documents through the `begin_classify_document` API. 
Custom classification models can classify each page in an input file to identify the document(s) within and can also identify multiple documents or multiple instances of a single document within an input file.

Sample code snippets are provided to illustrate using a DocumentIntelligenceClient [here](#examples "Examples").
More information about analyzing documents, including supported features, locales, and document types can be found in the [service documentation][di-models].

### DocumentIntelligenceAdministrationClient

`DocumentIntelligenceAdministrationClient` provides operations for:

- Building custom models to analyze specific fields you specify by labeling your custom documents. A `DocumentModelDetails` is returned indicating the document type(s) the model can analyze, as well as the estimated confidence for each field. See the [service documentation][di-build-model] for a more detailed explanation.
- Creating a composed model from a collection of existing models.
- Managing models created in your account.
- Listing operations or getting a specific model operation created within the last 24 hours.
- Copying a custom model from one Document Intelligence resource to another.
- Build and manage a custom classification model to classify the documents you process within your application.

Please note that models can also be built using a graphical user interface such as [Document Intelligence Studio][di-studio].

Sample code snippets are provided to illustrate using a DocumentIntelligenceAdministrationClient [here](#examples "Examples").

### Long-running operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that analyze documents, build models, or copy/compose models are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an `LROPoller` or `AsyncLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Examples

The following section provides several code snippets covering some of the most common Document Intelligence tasks, including:

* [Extract Layout](#extract-layout "Extract Layout")
* [Using the General Document Model](#using-the-general-document-model "Using the General Document Model")
* [Using Prebuilt Models](#using-prebuilt-models "Using Prebuilt Models")
* [Build a Custom Model](#build-a-custom-model "Build a custom model")
* [Analyze Documents Using a Custom Model](#analyze-documents-using-a-custom-model "Analyze Documents Using a Custom Model")
* [Manage Your Models](#manage-your-models "Manage Your Models")
* [Add-on capabilities](#add-on-capabilities "Add-on Capabilities")

### Extract Layout

Extract text, selection marks, text styles, and table structures, along with their bounding region coordinates, from documents.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

document_intelligence_client = DocumentIntelligenceClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
with open(path_to_sample_documents, "rb") as f:
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout", analyze_request=f, content_type="application/octet-stream"
    )
result = poller.result()

for idx, style in enumerate(result.styles):
    print(
        "Document contains {} content".format(
            "handwritten" if style.is_handwritten else "no handwritten"
        )
    )

for page in result.pages:
    print("----Analyzing layout from page #{}----".format(page.page_number))
    print(
        "Page has width: {} and height: {}, measured with unit: {}".format(
            page.width, page.height, page.unit
        )
    )

    for line_idx, line in enumerate(page.lines):
        words = line.get_words()
        print(
            "...Line # {} has word count {} and text '{}' within bounding polygon '{}'".format(
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
    for cell in table.cells:
        print(
            "...Cell[{}][{}] has content '{}'".format(
                cell.row_index,
                cell.column_index,
                cell.content,
            )
        )
        for region in cell.bounding_regions:
            print(
                "...content on page {} is within bounding polygon '{}'".format(
                    region.page_number,
                    region.polygon,
                )
            )

print("----------------------------------------")
```

### Using Prebuilt Models

Extract fields from select document types such as receipts, invoices, business cards, identity documents, and U.S. W-2 tax documents using prebuilt models provided by the Document Intelligence service.

For example, to analyze fields from a sales receipt, use the prebuilt receipt model provided by passing `model_id="prebuilt-receipt"` into the `begin_analyze_document` method:

<!-- SNIPPET:sample_analyze_receipts.analyze_receipts -->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

document_analysis_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-receipt", analyze_request=f, locale="en-US", content_type="application/octet-stream"
    )
receipts = poller.result()

for idx, receipt in enumerate(receipts.documents):
    print(f"--------Analysis of receipt #{idx + 1}--------")
    print(f"Receipt type: {receipt.doc_type if receipt.doc_type else 'N/A'}")
    merchant_name = receipt.fields.get("MerchantName")
    if merchant_name:
        print(f"Merchant Name: {merchant_name.get('valueString')} has confidence: " f"{merchant_name.confidence}")
    transaction_date = receipt.fields.get("TransactionDate")
    if transaction_date:
        print(
            f"Transaction Date: {transaction_date.get('valueDate')} has confidence: "
            f"{transaction_date.confidence}"
        )
    if receipt.fields.get("Items"):
        print("Receipt items:")
        for idx, item in enumerate(receipt.fields.get("Items").get("valueArray")):
            print(f"...Item #{idx + 1}")
            item_description = item.get("valueObject").get("Description")
            if item_description:
                print(
                    f"......Item Description: {item_description.get('valueString')} has confidence: "
                    f"{item_description.confidence}"
                )
            item_quantity = item.get("valueObject").get("Quantity")
            if item_quantity:
                print(
                    f"......Item Quantity: {item_quantity.get('valueString')} has confidence: "
                    f"{item_quantity.confidence}"
                )
            item_total_price = item.get("valueObject").get("TotalPrice")
            if item_total_price:
                print(
                    f"......Total Item Price: {format_price(item_total_price.get('valueCurrency'))} has confidence: "
                    f"{item_total_price.confidence}"
                )
    subtotal = receipt.fields.get("Subtotal")
    if subtotal:
        print(f"Subtotal: {format_price(subtotal.get('valueCurrency'))} has confidence: {subtotal.confidence}")
    tax = receipt.fields.get("TotalTax")
    if tax:
        print(f"Total tax: {format_price(tax.get('valueCurrency'))} has confidence: {tax.confidence}")
    tip = receipt.fields.get("Tip")
    if tip:
        print(f"Tip: {format_price(tip.get('valueCurrency'))} has confidence: {tip.confidence}")
    total = receipt.fields.get("Total")
    if total:
        print(f"Total: {format_price(total.get('valueCurrency'))} has confidence: {total.confidence}")
    print("--------------------------------------")
```

<!-- END SNIPPET -->

You are not limited to receipts! There are a few prebuilt models to choose from, each of which has its own set of supported fields. See other supported prebuilt models [here][di-models].

### Build a Custom Model

Build a custom model on your own document type. The resulting model can be used to analyze values from the types of documents it was trained on.
Provide a container SAS URL to your Azure Storage Blob container where you're storing the training documents.

More details on setting up a container and required file structure can be found in the [service documentation][di-build-training-set].


```python
from azure.ai.formrecognizer import (
    DocumentIntelligenceAdministrationClient,
    ModelBuildMode,
)
from azure.core.credentials import AzureKeyCredential

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
container_sas_url = os.environ["CONTAINER_SAS_URL"]

document_model_admin_client = DocumentIntelligenceAdministrationClient(
    endpoint, AzureKeyCredential(key)
)
poller = document_model_admin_client.begin_build_document_model(
    ModelBuildMode.TEMPLATE,
    blob_container_url=container_sas_url,
    description="my model description",
)
model = poller.result()

print(f"Model ID: {model.model_id}")
print(f"Description: {model.description}")
print(f"Model created on: {model.created_on}")
print(f"Model expires on: {model.expires_on}")
print("Doc types the model can recognize:")
for name, doc_type in model.doc_types.items():
    print(
        f"Doc Type: '{name}' built with '{doc_type.build_mode}' mode which has the following fields:"
    )
    for field_name, field in doc_type.field_schema.items():
        print(
            f"Field: '{field_name}' has type '{field['type']}' and confidence score "
            f"{doc_type.field_confidence[field_name]}"
        )
```

### Analyze Documents Using a Custom Model

Analyze document fields, tables, selection marks, and more. These models are trained with your own data, so they're tailored to your documents.
For best results, you should only analyze documents of the same document type that the custom model was built with.

<!-- SNIPPET:sample_analyze_custom_documents.analyze_custom_documents -->

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
model_id = os.getenv("CUSTOM_BUILT_MODEL_ID", custom_model_id)

document_analysis_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Make sure your document's type is included in the list of document types the custom model can analyze
with open(path_to_sample_documents, "rb") as f:
    poller = document_analysis_client.begin_analyze_document(
        model_id=model_id, analyze_request=f, content_type="application/octet-stream"
    )
result = poller.result()

for idx, document in enumerate(result.documents):
    print(f"--------Analyzing document #{idx + 1}--------")
    print(f"Document has type {document.doc_type}")
    print(f"Document has document type confidence {document.confidence}")
    print(f"Document was analyzed with model with ID {result.model_id}")
    for name, field in document.fields.items():
        field_value = field.get("valueString") if field.get("valueString") else field.content
        print(
            f"......found field of type '{field.type}' with value '{field_value}' and with confidence {field.confidence}"
        )

# iterate over tables, lines, and selection marks on each page
for page in result.pages:
    print(f"\nLines found on page {page.page_number}")
    for line in page.lines:
        print(f"...Line '{line.content}'")
    for word in page.words:
        print(f"...Word '{word.content}' has a confidence of {word.confidence}")
    if page.selection_marks:
        print(f"\nSelection marks found on page {page.page_number}")
        for selection_mark in page.selection_marks:
            print(
                f"...Selection mark is '{selection_mark.state}' and has a confidence of {selection_mark.confidence}"
            )

for i, table in enumerate(result.tables):
    print(f"\nTable {i + 1} can be found on page:")
    for region in table.bounding_regions:
        print(f"...{region.page_number}")
    for cell in table.cells:
        print(f"...Cell[{cell.row_index}][{cell.column_index}] has text '{cell.content}'")
print("-----------------------------------")
```

<!-- END SNIPPET -->

Additionally, a document URL can also be used to analyze documents using the `begin_analyze_document` method.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]

document_analysis_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/documentintelligence/azure-ai-documentintelligence/tests/sample_forms/receipt/contoso-receipt.png"
poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", AnalyzeDocumentRequest(url_source=url))
receipts = poller.result()
```

### Manage Your Models

Manage the custom models attached to your account.

```python
from azure.ai.documentintelligence import DocumentIntelligenceAdministrationClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

document_model_admin_client = DocumentIntelligenceAdministrationClient(endpoint, credential)

account_details = document_model_admin_client.get_resource_info()
print("Our account has {} custom models, and we can have at most {} custom models".format(
    account_details.custom_document_models.count, account_details.custom_document_models.limit
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

### Add-on Capabilities
Document Intelligence supports more sophisticated analysis capabilities. These optional features can be enabled and disabled depending on the scenario of the document extraction.

The following add-on capabilities are available for 2023-07-31 (GA) and later releases:
- [barcode/QR code][addon_barcodes_sample]
- [formula][addon_formulas_sample]
- [font/style][addon_fonts_sample]
- [high resolution mode][addon_highres_sample]
- [language][addon_languages_sample]

Note that some add-on capabilities will incur additional charges. See pricing: https://azure.microsoft.com/pricing/details/ai-document-intelligence/.

## Troubleshooting

### General

Document Intelligence client library will raise exceptions defined in [Azure Core][azure_core_exceptions].
Error codes and messages raised by the Document Intelligence service can be found in the [service documentation][di-errors].

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

See the [Sample README][sample_readme] for several code snippets illustrating common patterns used in the Document Intelligence Python API.

### Additional documentation

For more extensive documentation on Azure AI Document Intelligence, see the [Document Intelligence documentation][python-di-product-docs] on docs.microsoft.com.


## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[pip]: https://pypi.org/project/pip/
[azure_sub]: https://azure.microsoft.com/free/

[python-di-src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/azure/ai/documentintelligence
[python-di-pypi]: https://pypi.org/project/azure-ai-formrecognizer/
[python-di-product-docs]: https://learn.microsoft.com/azure/applied-ai-services/form-recognizer/overview?view=form-recog-3.0.0
[python-di-ref-docs]: https://aka.ms/azsdk/python/formrecognizer/docs
[python-di-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples

[azure_portal]: https://ms.portal.azure.com/
[regional_endpoints]: https://azure.microsoft.com/global-infrastructure/services/?products=form-recognizer
[FR_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[cognitive_resource_portal]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer
[cognitive_resource_cli]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[labeling-tool]: https://aka.ms/azsdk/formrecognizer/labelingtool
[di-studio]: https://aka.ms/azsdk/formrecognizer/formrecognizerstudio
[di-build-model]: https://aka.ms/azsdk/formrecognizer/buildmodel
[di-build-training-set]: https://aka.ms/azsdk/formrecognizer/buildtrainingset
[di-models]: https://aka.ms/azsdk/formrecognizer/models
[di-errors]: https://aka.ms/azsdk/formrecognizer/errors

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
[service_recognize_receipt]: https://aka.ms/azsdk/formrecognizer/receiptfieldschema
[service_recognize_business_cards]: https://aka.ms/azsdk/formrecognizer/businesscardfieldschema
[service_recognize_invoice]: https://aka.ms/azsdk/formrecognizer/invoicefieldschema
[service_recognize_identity_documents]: https://aka.ms/azsdk/formrecognizer/iddocumentfieldschema
[service_recognize_tax_documents]: https://aka.ms/azsdk/formrecognizer/taxusw2fieldschema
[service_prebuilt_document]: https://docs.microsoft.com/azure/applied-ai-services/form-recognizer/concept-general-document#general-document-features
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/sdk/azure-sdk-logging
[sample_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples
[changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/CHANGELOG.md
[addon_barcodes_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_analyze_addon_barcodes.py
[addon_fonts_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_analyze_addon_fonts.py
[addon_formulas_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_analyze_addon_formulas.py
[addon_highres_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_analyze_addon_highres.py
[addon_languages_sample]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/documentintelligence/azure-ai-documentintelligence/samples/sample_analyze_addon_languages.py
[service-rename]: https://techcommunity.microsoft.com/t5/azure-ai-services-blog/azure-form-recognizer-is-now-azure-ai-document-intelligence-with/ba-p/3875765

[cla]: https://cla.microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
