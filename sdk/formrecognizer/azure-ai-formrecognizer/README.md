# Azure Form Recognizer client library for Python

Azure Cognitive Services Form Recognizer is a cloud service that uses machine learning to recognize text and table data
from form documents. It includes the following main functionalities:

* Custom models - Recognize field values and table data from forms. These models are trained with your own data, so they're tailored to your forms. You can then take these custom models and recognize forms. You can also manage the custom models you've created and see how close you are to the limit of custom models your account can hold.
* Content API - Recognize text and table structures, along with their bounding box coordinates, from documents. Corresponds to the REST service's Layout API.
* Prebuilt receipt model - Recognize data from USA sales receipts using a prebuilt model.

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

> Note: This version of the client library supports the v2.0-preview version of the Form Recognizer service

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
The `credential` parameter may be provided as a [AzureKeyCredential][azure-key-credential] from [azure.core][azure_core].
See the full details regarding [authentication][cognitive_authentication] of cognitive services.

To use an [API key][cognitive_authentication_api_key],
pass the key as a string into an instance of `AzureKeyCredential("<api_key>")`.
The API key can be found in the Azure Portal or by running the following Azure CLI command:

```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

Use the key as the credential parameter to authenticate the client:
```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")
form_recognizer_client = FormRecognizerClient(endpoint, credential)
```

## Key concepts

### FormRecognizerClient
`FormRecognizerClient` provides operations for:

 - Recognizing form fields and content using custom models trained to recognize your custom forms. These values are returned in a collection of `RecognizedForm` objects.
 - Recognizing form content, including tables, lines and words, without the need to train a model. Form content is returned in a collection of `FormPage` objects.
 - Recognizing common fields from US receipts, using a pre-trained receipt model on the Form Recognizer service. These fields and meta-data are returned in a collection of `USReceipt` objects.

### FormTrainingClient
`FormTrainingClient` provides operations for:

- Training custom models to recognize all fields and values found in your custom forms. A `CustomFormModel` is returned indicating the form types the model will recognize, and the fields it will extract for each form type. See the [service's documents][fr-train-without-labels] for a more detailed explanation.
- Training custom models to recognize specific fields and values you specify by labeling your custom forms. A `CustomFormModel` is returned indicating the fields the model will extract, as well as the estimated accuracy for each field. See the [service's documents][fr-train-with-labels] for a more detailed explanation.
- Managing models created in your account.

Please note that models can also be trained using a graphical user interface such as the [Form Recognizer Labeling Tool][fr-labeling-tool].
### Long-Running Operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that train models or recognize values from forms are modeled as long-running operations. The client exposes
a `begin_<method-name>` method that returns an `LROPoller`. Callers should wait for the operation to complete by
calling `result()` on the operation returned from the `begin_<method-name>` method. Sample code snippets are provided
to illustrate using long-running operations [below](#examples "Examples").


## Examples

The following section provides several code snippets covering some of the most common Form Recognizer tasks, including:

* [Recognize Forms Using a Custom Model](#recognize-forms-using-a-custom-model "Recognize Forms Using a Custom Model")
* [Recognize Content](#recognize-content "Recognize Content")
* [Recognize Receipts](#recognize-receipts "Recognize receipts")
* [Train a Model](#train-a-model "Train a model")
* [Manage Your Models](#manage-your-models "Manage Your Models")

### Recognize Forms Using a Custom Model
Recognize name/value pairs and table data from forms. These models are trained with your own data, so they're tailored to your forms. You should only recognize forms of the same form type that the custom model was trained on.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)
model_id = "<your custom model id>"

# Make sure the form type is one of the types of forms your custom model can recognize
with open("<path to your form>", "rb") as fd:
    form = fd.read()

poller = form_recognizer_client.begin_recognize_custom_forms(model_id=model_id, stream=form)
result = poller.result()

for recognized_form in result:
    print("Form type ID: {}".format(recognized_form.form_type))
    for label, field in recognized_form.fields.items():
        print("Field '{}' has value '{}' with a confidence score of {}".format(
            label, field.value, field.confidence
        ))
```

### Recognize Content
Recognize text and table structures, along with their bounding box coordinates, from documents.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)

with open("<path to your form>", "rb") as fd:
    form = fd.read()

poller = form_recognizer_client.begin_recognize_content(form)
page = poller.result()

table = page[0].tables[0] # page 1, table 1
for cell in table.cells:
    print(cell.text)
    print(cell.bounding_box)
    print(cell.confidence)
```

### Recognize Receipts
Recognize data from USA sales receipts using a prebuilt model.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)

with open("<path to your receipt>", "rb") as fd:
    receipt = fd.read()

poller = form_recognizer_client.begin_recognize_receipts(receipt)
result = poller.result()

r = result[0]
print("Receipt contained the following values with confidences: ")
print("Receipt Type: {} has confidence: {}".format(r.receipt_type.type, r.receipt_type.confidence))
print("Merchant Name: {} has confidence: {}".format(r.merchant_name.value, r.merchant_name.confidence))
print("Transaction Date: {} has confidence: {}".format(r.transaction_date.value, r.transaction_date.confidence))
print("Receipt items:")
for item in r.receipt_items:
    print("...Item Name: {} has confidence: {}".format(item.name.value, item.name.confidence))
    print("...Item Quantity: {} has confidence: {}".format(item.quantity.value, item.quantity.confidence))
    print("...Individual Item Price: {} has confidence: {}".format(item.price.value, item.price.confidence))
    print("...Total Item Price: {} has confidence: {}".format(item.total_price.value, item.total_price.confidence))
print("Subtotal: {} has confidence: {}".format(r.subtotal.value, r.subtotal.confidence))
print("Tax: {} has confidence: {}".format(r.tax.value, r.tax.confidence))
print("Tip: {} has confidence: {}".format(r.tip.value, r.tip.confidence))
print("Total: {} has confidence: {}".format(r.total.value, r.total.confidence))
```

### Train a model
Train a machine-learned model on your own form type. The resulting model will be able to recognize values from the types of forms it was trained on.
Provide a container SAS url to your Azure Storage Blob container where you're storing the training documents. See details on setting this up
in the [service quickstart documentation][quickstart_training].

```python
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_training_client = FormTrainingClient(endpoint, credential)

container_sas_url = "xxx"  # training documents uploaded to blob storage
poller = form_training_client.begin_train_model(container_sas_url)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Status: {}".format(model.status))
print("Created on: {}".format(model.created_on))
print("Last modified: {}".format(model.last_modified))

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

### Manage Your Models
Manage the custom models attached to your account.

```python
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_training_client = FormTrainingClient(endpoint, credential)

account_properties = form_training_client.get_account_properties()
print("Our account has {} custom models, and we can have at most {} custom models".format(
    account_properties.custom_model_count, account_properties.custom_model_limit
))

# Here we get a paged list of all of our custom models
custom_models = form_training_client.list_model_infos()
print("We have models with the following ids: {}".format(
    ", ".join([m.model_id for m in custom_models])
))

# Now we get the custom model from the "Train a model" sample
model_id = "<model id from the Train a Model sample>"

custom_model = form_training_client.get_custom_model(model_id=model_id)
print("Model ID: {}".format(custom_model.model_id))
print("Status: {}".format(custom_model.status))
print("Created on: {}".format(custom_model.created_on))
print("Last modified: {}".format(custom_model.last_modified))

# Finally, we will delete this model by ID
form_training_client.delete_model(model_id=custom_model.model_id)

try:
    form_training_client.get_custom_model(model_id=custom_model.model_id)
except ResourceNotFoundError:
    print("Successfully deleted model with id {}".format(custom_model.model_id))
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
form_recognizer_client = FormRecognizerClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
poller = form_recognizer_client.begin_recognize_receipts(receipt, logging_enable=True)
```

## Next steps

The following section provides several code snippets illustrating common patterns used in the Form Recognizer Python API.

### More sample code

These code samples show common scenario operations with the Azure Form Recognizer client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations
with Form Recognizer and require Python 3.5 or later.

* Recognize receipts: [sample_recognize_receipts.py][sample_recognize_receipts] ([async version][sample_recognize_receipts_async])
* Recognize receipts from a URL: [sample_recognize_receipts_from_url.py][sample_recognize_receipts_from_url] ([async version][sample_recognize_receipts_from_url_async])
* Recognize content: [sample_recognize_content.py][sample_recognize_content] ([async version][sample_recognize_content_async])
* Recognize custom forms: [sample_recognize_custom_forms.py][sample_recognize_custom_forms] ([async version][sample_recognize_custom_forms_async])
* Train a model without labels: [sample_train_model_without_labels.py][sample_train_model_without_labels] ([async version][sample_train_model_without_labels_async])
* Train a model with labels: [sample_train_model_with_labels.py][sample_train_model_with_labels] ([async version][sample_train_model_with_labels_async])
* Manage custom models: [sample_manage_custom_models.py][sample_manage_custom_models] ([async_version][sample_manage_custom_models_async])

### Additional documentation

For more extensive documentation on Azure Cognitive Services Form Recognizer, see the [Form Recognizer documentation][python-fr-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

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
[fr-labeling-tool]: https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/quickstarts/label-tool
[fr-train-without-labels]: https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/overview#train-without-labels
[fr-train-with-labels]: https://docs.microsoft.com/en-us/azure/cognitive-services/form-recognizer/overview#train-with-labels

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

[sample_manage_custom_models]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_manage_custom_models.py
[sample_manage_custom_models_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_manage_custom_models_async.py
[sample_recognize_content]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_content.py
[sample_recognize_content_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_content_async.py
[sample_recognize_custom_forms]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_custom_forms.py
[sample_recognize_custom_forms_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_custom_forms_async.py
[sample_recognize_receipts_from_url]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts_from_url.py
[sample_recognize_receipts_from_url_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_receipts_from_url_async.py
[sample_recognize_receipts]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_receipts.py
[sample_recognize_receipts_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_receipts_async.py
[sample_train_model_with_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_with_labels.py
[sample_train_model_with_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_with_labels_async.py
[sample_train_model_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_without_labels.py
[sample_train_model_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_without_labels_async.py
