# Azure Form Recognizer client library for Python

Azure Cognitive Services Form Recognizer is a cloud service that uses machine learning to extract text and table data
from form documents. Form Recognizer is made up of the following services:

* Custom models - Extract name/value pairs and table data from forms. These models are trained with your own data, so they're tailored to your forms.
* Prebuilt receipt model - Extract data from USA sales receipts using a prebuilt model.
* Layout API - Extract text and table structures, along with their bounding box coordinates, from documents.

[Source code][python-fr-src] | [Package (PyPI)][python-fr-pypi] | [API reference documentation][python-fr-ref-docs]| [Product documentation][python-fr-product-docs] | [Samples][python-fr-samples]

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Cognitive Services or Form Recognizer resource][FR_or_CS_resource] to use this package.

### Install the package
Install the Azure Form Recognizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-formrecognizer
```

### Create a Form Recognizer resource
Form Recognizer supports both [multi-service and single-service access][multi_and_single_service].
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Form Recognizer access only, create a Form Recognizer resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_FR_resource]

**Option 2:** [Azure CLI][azure_cli_create_FR_resource].
Below is an example of how you can create a Form Recognizer resource using the CLI:

```bash
# Create a new resource group to hold the form recognizer resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2
```

```bash
# Create form recognizer
az cognitiveservices account create \
    --name form-recognizer-resource \
    --resource-group my-resource-group \
    --kind FormRecognizer \
    --sku F0 \
    --location westus2 \
    --yes
```

### Authenticate the client

#### Looking up the endpoint
You can find the endpoint for your form recognizer resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the form recognizer resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "endpoint"
```

#### Types of credentials
The `credential` parameter may be provided as a [`AzureKeyCredential`][azure-key-credential] from [azure.core][azure_core].
See the full details regarding [authentication][cognitive_authentication] of cognitive services.

To use an [API key][cognitive_authentication_api_key],
pass the key as a string into an instance of [`AzureKeyCredential("<api_key>")`][azure-key-credential].
The API key can be found in the Azure Portal or by running the following Azure CLI command:

```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

Use the key as the credential parameter to authenticate the client:
```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

credential = AzureKeyCredential("<api_key>")
client = FormRecognizerClient(endpoint, credential)
```

## Key concepts

### FormRecognizerClient
A `FormRecognizerClient` is the Form Recognizer interface to use for analyzing receipts and extracting layout items from
forms. It provides different methods based on inputs from a URL and inputs from a stream. You can extract receipt field
values from receipts from the US, table data and geometry from a URl or stream, and use a custom trained model to extract
form data.

### FormTrainingClient
A `FormTrainingClient` is the Form Recognizer interface to use for creating, using, and managing custom machine-learned models.
It provides operations for training models on forms you provide, and extracting field values and locations from your
custom forms.  It also provides operations for viewing and deleting models, as well as understanding how close you
are to reaching subscription limits for the number of models you can train.

### Long-Running Operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that train models or extract values from forms are modeled as long-running operations.  The client exposes
a `begin_<method-name>` method that returns an `LROPoller`.  Callers should wait for the operation to complete by
calling `result()` on the operation returned from the `begin_<method-name>` method.  Sample code snippets are provided
to illustrate using long-running operations [below](#Examples).

### Training models
Using the `FormTrainingClient`, you can train a machine-learned model on your own form type.  The resulting model will
be able to extract values from the types of forms it was trained on.

#### Training without labels
A model trained without labels uses unsupervised learning to understand the layout and relationships between field
names and values in your forms. The learning algorithm clusters the training forms by type and learns what fields and
tables are present in each form type.

This approach doesn't require manual data labeling or intensive coding and maintenance, and we recommend you try this
method first when training custom models.

#### Training with labels
A model trained with labels uses supervised learning to extract values you specify by adding labels to your training forms.
The learning algorithm uses a label file you provide to learn what fields are found at various locations in the form,
and learns to extract just those values.

This approach can result in better-performing models, and those models can work with more complex form structures.

### Extracting values from forms
Using the `FormRecognizerClient`, you can use your own trained models to extract field values and locations, as well as
table data, from forms of the type you trained your models on.  The output of models trained with and without labels
differs as described below.

#### Using models trained without labels
Models trained without labels consider each form page to be a different form type.  For example, if you train your
model on 3-page forms, it will learn that these are three different types of forms.  When you send a form to it for
analysis, it will return a collection of three pages, where each page contains the field names, values, and locations,
as well as table data, found on that page.

#### Using models trained with labels
Models trained with labels consider a form as a single unit.  For example, if you train your model on 3-page forms
with labels, it will learn to extract field values from the locations you've labeled across all pages in the form.
If you sent a document containing two forms to it for analysis, it would return a collection of two forms,
where each form contains the field names, values, and locations, as well as table data, found in that form.
Fields and tables have page numbers to identify the pages where they were found.

### Managing Custom Models
Using the `FormTrainingClient`, you can get, list, and delete the custom models you've trained.
You can also view the count of models you've trained and the maximum number of models your subscription will
allow you to store.

## Examples

The following section provides several code snippets covering some of the most common Form Recognizer tasks, including:

* [Recognize Receipts](#recognize-receipts "Recognize receipts")
* [Extract Form Layouts](#extract-form-layouts "Extract form layouts")
* [Train a Model](#train-a-model "Train a model")
* [Extract Forms Using a Model](#extract-forms-using-a-model "Extract forms using a model")


### Recognize Receipts
Recognize data from USA sales receipts using a prebuilt model.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
client = FormRecognizerClient(endpoint, AzureKeyCredential(key))

with open("<path to your receipt>", "rb") as fd:
    receipt = fd.read()

poller = client.begin_recognize_receipts(receipt)
result = poller.result()

r = result[0]
print("Receipt contained the following values with confidences: ")
print("ReceiptType: {}\nconfidence: {}\n".format(r.receipt_type.type, r.receipt_type.confidence))
print("MerchantName: {}\nconfidence: {}\n".format(r.merchant_name.value, r.merchant_name.confidence))
print("TransactionDate: {}\nconfidence: {}\n".format(r.transaction_date.value, r.transaction_date.confidence))
print("Receipt items:")
for item in r.receipt_items:
    print("Item Name: {}\nconfidence: {}".format(item.name.value, item.name.confidence))
    print("Item Quantity: {}\nconfidence: {}".format(item.quantity.value, item.quantity.confidence))
    print("Total Price: {}\nconfidence: {}\n".format(item.total_price.value, item.total_price.confidence))
print("Subtotal: {}\nconfidence: {}\n".format(r.subtotal.value, r.subtotal.confidence))
print("Tax: {}\nconfidence: {}\n".format(r.tax.value, r.tax.confidence))
print("Tip: {}\nconfidence: {}\n".format(r.tip.value, r.tip.confidence))
print("Total: {}\nconfidence: {}\n".format(r.total.value, r.total.confidence))
```

### Recognize Form Content
Recognize text and table structures, along with their bounding box coordinates, from documents.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

client = FormRecognizerClient(endpoint, AzureKeyCredential(key))

with open("<path to your form>", "rb") as fd:
    form = fd.read()

poller = client.begin_recognize_content(form)
page = poller.result()

table = page[0].tables[0] # page 1, table 1
for cell in table.cells:
    print(cell.text)
    print(cell.bounding_box)
```

### Train a model
Train a machine-learned model on your own form type. The resulting model will be able to extract values from the types of forms it was trained on.
Provide a container SAS url to your Azure Storage Blob container where you're storing the training documents. See details on setting this up
in the [service quickstart documentation][quickstart_training].

```python
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

client = FormTrainingClient(endpoint, AzureKeyCredential(key))

blob_sas_url = "xxx"  # training documents uploaded to blob storage
poller = client.begin_training(blob_sas_url)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Status: {}".format(model.status))
print("Created on: {}".format(model.created_on))
print("Last updated on: {}".format(model.last_updated_on))

print("Recognized fields:")
# looping through the submodels, which contains the fields they were trained on
for submodel in model.models:
    print("We have recognized the following fields: {}".format(
        ", ".join([label for label in submodel.fields])
    ))

# Training result information
for doc in model.training_documents:
    print("Document name: {}".format(doc.document_name))
    print("Document status: {}".format(doc.status))
    print("Document page count: {}".format(doc.page_count))
    print("Document errors: {}".format(doc.errors))
```

### Recognize Forms Using a Model
Recognize name/value pairs and table data from forms. These models are trained with your own data, so they're tailored to your forms.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
model_id = "<model id from the above sample>"

with open("sample_forms/forms/Form_1.jpg", "rb") as fd:
    form = fd.read()

poller = client.begin_recognize_custom_forms(model_id=model_id, stream=form)
result = poller.result()

for recognized_form in result:
    print("Form type ID: {}".format(recognized_form.form_type))
    for label, field in recognized_form.fields.items():
        print("Field '{}' has value '{}' with a confidence score of {}".format(
            label, field.value, field.confidence
        ))
```

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General
Form Recognizer client library will raise exceptions defined in [Azure Core][azure_core_ref_docs].

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:
```python
import sys
import logging
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api_key>")

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = FormRecognizerClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
result = client.begin_recognize_receipts(receipt, logging_enable=True)
```

## Next steps

The following section provides several code snippets illustrating common patterns used in the Form Recognizer Python API.

### More sample code

These code samples show common scenario operations with the Azure Form Recognizer client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations
with Form Recognizer and require Python 3.5 or later.

Authenticate the client with a Form Recognizer API key:
* [sample_authentication.py][sample_authentication] ([async version][sample_authentication_async])

* Extract receipts: TODO
* Extract form layouts: TODO
* Train a model: TODO
* Train a model with labels: TODO
* Analyze a form using a custom model: TODO
* Analyze a form using a custom labeled model: TODO
* Get, list, delete models: TODO

### Additional documentation

For more extensive documentation on Azure Cognitive Services Form Recognizer, see the [Form Recognizer documentation][python-fr-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-fr-src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer
[python-fr-pypi]: https://pypi.org/project/azure-ai-formrecognizer/
[python-fr-product-docs]: https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/overview
[python-fr-ref-docs]: https://aka.ms/azsdk-python-formrecognizer-ref-docs
[python-fr-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples


[quickstart_training]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/quickstarts/curl-train-extract#train-a-form-recognizer-model
[azure_subscription]: https://azure.microsoft.com/free/
[FR_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_FR_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer
[azure_cli_create_FR_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk-python-core-azurekeycredential

[azure_core]: ../../core/azure-core/README.md
[azure_core_ref_docs]: https://aka.ms/azsdk-python-azure-core
[python_logging]: https://docs.python.org/3/library/logging.html
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: ../../identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: ../../identity/azure-identity#credentials
[default_azure_credential]: ../../identity/azure-identity#defaultazurecredential

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com