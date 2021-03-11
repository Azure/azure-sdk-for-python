# Azure Form Recognizer client library for Python

Azure Cognitive Services Form Recognizer is a cloud service that uses machine learning to recognize text and table data
from form documents. It includes the following main functionalities:

* Custom models - Recognize field values and table data from forms. These models are trained with your own data, so they're tailored to your forms.
* Content API - Recognize text, table structures, and selection marks, along with their bounding box coordinates, from documents. Corresponds to the REST service's Layout API.
* Prebuilt models - Recognize data using the following prebuilt models
    * Receipt model - Recognize data from sales receipts using a prebuilt model.
    * Business card model - Recognize data from business cards using a prebuilt model.
    * Invoice model - Recognize data from invoices using a prebuilt model.

[Source code][python-fr-src] | [Package (PyPI)][python-fr-pypi] | [API reference documentation][python-fr-ref-docs]| [Product documentation][python-fr-product-docs] | [Samples][python-fr-samples]

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Cognitive Services or Form Recognizer resource][FR_or_CS_resource] to use this package.

### Install the package
Install the Azure Form Recognizer client library for Python with [pip][pip]:

```bash
pip install azure-ai-formrecognizer --pre
```

> Note: This version of the client library defaults to the v2.1-preview.2 version of the service

This table shows the relationship between SDK versions and supported API versions of the service

|SDK version|Supported API version of service
|-|-
|3.0.0 - Latest GA release (can be installed by removing the `--pre` flag)| 2.0
|3.1.0b3 - Latest release (beta)| 2.0, 2.1-preview.2


#### Create a Form Recognizer resource
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
In order to interact with the Form Recognizer service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


#### Looking up the endpoint
You can find the endpoint for your Form Recognizer resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the form recognizer resource
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
from azure.ai.formrecognizer import FormRecognizerClient

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")
form_recognizer_client = FormRecognizerClient(endpoint, credential)
```

#### Create the client with an Azure Active Directory credential

`AzureKeyCredential` authentication is used in the examples in this getting started guide, but you can also
authenticate with Azure Active Directory using the [azure-identity][azure_identity] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

To use the [DefaultAzureCredential][default_azure_credential] type shown below, or other credential types provided
with the Azure SDK, please install the `azure-identity` package:

```pip install azure-identity```

You will also need to [register a new AAD application and grant access][register_aad_app] to
Form Recognizer by assigning the `"Cognitive Services User"` role to your service principal.

Once completed, set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`.

```python
from azure.identity import DefaultAzureCredential
from azure.ai.formrecognizer import FormRecognizerClient
credential = DefaultAzureCredential()

form_recognizer_client = FormRecognizerClient(
    endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
    credential=credential
)
```

## Key concepts

### FormRecognizerClient
`FormRecognizerClient` provides operations for:

 - Recognizing form fields and content using custom models trained to recognize your custom forms. These values are returned in a collection of `RecognizedForm` objects.
 - Recognizing common fields from the following form types using prebuilt models. These fields and metadata are returned in a collection of `RecognizedForm` objects.
    - Sales receipts. See fields found on a receipt [here][service_recognize_receipt].
    - Business cards. See fields found on a business card [here][service_recognize_business_cards].
    - Invoices. See fields found on an invoice [here][service_recognize_invoice].
 - Recognizing form content, including tables, lines, words, and selection marks, without the need to train a model. Form content is returned in a collection of `FormPage` objects.

Sample code snippets are provided to illustrate using a FormRecognizerClient [here](#recognize-forms-using-a-custom-model "Recognize Forms Using a Custom Model").

### FormTrainingClient
`FormTrainingClient` provides operations for:

- Training custom models without labels to recognize all fields and values found in your custom forms. A `CustomFormModel` is returned indicating the form types the model will recognize, and the fields it will extract for each form type. See the [service documentation][fr-train-without-labels] for a more detailed explanation.
- Training custom models with labels to recognize specific fields, selection marks, and values you specify by labeling your custom forms. A `CustomFormModel` is returned indicating the fields the model will extract, as well as the estimated accuracy for each field. See the [service documentation][fr-train-with-labels] for a more detailed explanation.
- Managing models created in your account.
- Copying a custom model from one Form Recognizer resource to another.
- Creating a composed model from a collection of existing trained models with labels.

Please note that models can also be trained using a graphical user interface such as the [Form Recognizer Labeling Tool][fr-labeling-tool].

Sample code snippets are provided to illustrate using a FormTrainingClient [here](#train-a-model "Train a model").

### Long-Running Operations
Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that train models, recognize values from forms, or copy/compose models are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an `LROPoller` or `AsyncLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").


## Examples

The following section provides several code snippets covering some of the most common Form Recognizer tasks, including:

* [Recognize Forms Using a Custom Model](#recognize-forms-using-a-custom-model "Recognize Forms Using a Custom Model")
* [Recognize Content](#recognize-content "Recognize Content")
* [Recognize Receipts](#recognize-receipts "Recognize receipts")
* [Recognize Business Cards](#recognize-business-cards "Recognize business cards")
* [Recognize Invoices](#recognize-invoices "Recognize invoices")
* [Train a Model](#train-a-model "Train a model")
* [Manage Your Models](#manage-your-models "Manage Your Models")

### Recognize Forms Using a Custom Model
Recognize name/value pairs and table data from forms. These models are trained with your own data, so they're tailored to your forms.
For best results, you should only recognize forms of the same form type that the custom model was trained on.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)
model_id = "<your custom model id>"

with open("<path to your form>", "rb") as fd:
    form = fd.read()

poller = form_recognizer_client.begin_recognize_custom_forms(model_id=model_id, form=form)
result = poller.result()

for recognized_form in result:
    print("Form type: {}".format(recognized_form.form_type))
    print("Form type confidence: {}".format(recognized_form.form_type_confidence))
    print("Form was analyzed using model with ID: {}".format(recognized_form.model_id))
    for name, field in recognized_form.fields.items():
        print("Field '{}' has label '{}' with value '{}' and a confidence score of {}".format(
            name,
            field.label_data.text if field.label_data else name,
            field.value,
            field.confidence
        ))
```

Alternatively, a form URL can also be used to recognize custom forms using the `begin_recognize_custom_forms_from_url` method.
The `_from_url` methods exist for all the recognize methods.

```
form_url = "<url_of_the_form>"
poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id=model_id, form_url=form_url)
result = poller.result()
```

### Recognize Content
Recognize text, selection marks, and table structures, along with their bounding box coordinates, from documents.

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)

with open("<path to your form>", "rb") as fd:
    form = fd.read()

poller = form_recognizer_client.begin_recognize_content(form)
form_pages = poller.result()

for content in form_pages:
    for table in content.tables:
        print("Table found on page {}:".format(table.page_number))
        print("Table location {}:".format(table.bounding_box))
        for cell in table.cells:
            print("Cell text: {}".format(cell.text))
            print("Location: {}".format(cell.bounding_box))
            print("Confidence score: {}\n".format(cell.confidence))

    if content.selection_marks:
        print("Selection marks found on page {}:".format(content.page_number))
        for selection_mark in content.selection_marks:
            print("Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                selection_mark.state,
                selection_mark.bounding_box,
                selection_mark.confidence
            ))
```

### Recognize Receipts
Recognize data from sales receipts using a prebuilt model. Receipt fields recognized by the service can be found [here][service_recognize_receipt].

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

for receipt in result:
    for name, field in receipt.fields.items():
        if name == "Items":
            print("Receipt Items:")
            for idx, items in enumerate(field.value):
                print("...Item #{}".format(idx+1))
                for item_name, item in items.value.items():
                    print("......{}: {} has confidence {}".format(item_name, item.value, item.confidence))
        else:
            print("{}: {} has confidence {}".format(name, field.value, field.confidence))
```

### Recognize Business Cards
Recognize data from business cards using a prebuilt model. Business card fields recognized by the service can be found [here][service_recognize_business_cards].

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)

with open("<path to your business card>", "rb") as fd:
    business_card = fd.read()

poller = form_recognizer_client.begin_recognize_business_cards(business_card)
result = poller.result()

for business_card in result:
    for name, field in business_card.fields.items():
        if name == "ContactNames":
            print("ContactNames:")
            for items in field.value:
                for item_name, item in items.value.items():
                    print("...{}: {} has confidence {}".format(item_name, item.value, item.confidence))
        else:
            for item in field.value:
                print("{}: {} has confidence {}".format(item.name, item.value, item.confidence))
```

### Recognize Invoices
Recognize data from invoices using a prebuilt model. Invoice fields recognized by the service can be found [here][service_recognize_invoice].

```python
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_recognizer_client = FormRecognizerClient(endpoint, credential)

with open("<path to your invoice>", "rb") as fd:
    invoice = fd.read()

poller = form_recognizer_client.begin_recognize_invoices(invoice)
result = poller.result()

for invoice in result:
    for name, field in invoice.fields.items():
        print("{}: {} has confidence {}".format(name, field.value, field.confidence))
```


### Train a model
Train a custom model on your own form type. The resulting model can be used to recognize values from the types of forms it was trained on.
Provide a container SAS URL to your Azure Storage Blob container where you're storing the training documents.
If training files are within a subfolder in the container, use the [prefix][prefix_ref_docs] keyword argument to specify under which folder to train.

More details on setting up a container and required file structure can be found in the [service documentation][training_data].

```python
from azure.ai.formrecognizer import FormTrainingClient
from azure.core.credentials import AzureKeyCredential

endpoint = "https://<region>.api.cognitive.microsoft.com/"
credential = AzureKeyCredential("<api_key>")

form_training_client = FormTrainingClient(endpoint, credential)

container_sas_url = "<container-sas-url>"  # training documents uploaded to blob storage
poller = form_training_client.begin_training(
    container_sas_url, use_training_labels=False, model_name="my first model"
)
model = poller.result()

# Custom model information
print("Model ID: {}".format(model.model_id))
print("Model name: {}".format(model.model_name))
print("Is composed model?: {}".format(model.properties.is_composed_model))
print("Status: {}".format(model.status))
print("Training started on: {}".format(model.training_started_on))
print("Training completed on: {}".format(model.training_completed_on))

print("\nRecognized fields:")
for submodel in model.submodels:
    print(
        "The submodel with form type '{}' and model ID '{}' has recognized the following fields: {}".format(
            submodel.form_type, submodel.model_id,
            ", ".join(
                [
                    field.label if field.label else name
                    for name, field in submodel.fields.items()
                ]
            ),
        )
    )

# Training result information
for doc in model.training_documents:
    print("Document name: {}".format(doc.name))
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
custom_models = form_training_client.list_custom_models()
print("We have models with the following ids: {}".format(
    ", ".join([m.model_id for m in custom_models])
))

# Replace with the custom model ID from the "Train a model" sample
model_id = "<model_id from the Train a Model sample>"

custom_model = form_training_client.get_custom_model(model_id=model_id)
print("Model ID: {}".format(custom_model.model_id))
print("Model name: {}".format(custom_model.model_name))
print("Is composed model?: {}".format(custom_model.properties.is_composed_model))
print("Status: {}".format(custom_model.status))
print("Training started on: {}".format(custom_model.training_started_on))
print("Training completed on: {}".format(custom_model.training_completed_on))

# Finally, we will delete this model by ID
form_training_client.delete_model(model_id=custom_model.model_id)

try:
    form_training_client.get_custom_model(model_id=custom_model.model_id)
except ResourceNotFoundError:
    print("Successfully deleted model with id {}".format(custom_model.model_id))
```

## Troubleshooting

### General
Form Recognizer client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

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

The following section provides several code snippets illustrating common patterns used in the Form Recognizer Python API.

### More sample code

These code samples show common scenario operations with the Azure Form Recognizer client library.

* Client authentication: [sample_authentication.py][sample_authentication]
* Recognize receipts: [sample_recognize_receipts.py][sample_recognize_receipts]
* Recognize receipts from a URL: [sample_recognize_receipts_from_url.py][sample_recognize_receipts_from_url]
* Recognize business cards: [sample_recognize_business_cards.py][sample_recognize_business_cards]
* Recognize invoices: [sample_recognize_invoices.py][sample_recognize_invoices]
* Recognize content: [sample_recognize_content.py][sample_recognize_content]
* Recognize custom forms: [sample_recognize_custom_forms.py][sample_recognize_custom_forms]
* Train a model without labels: [sample_train_model_without_labels.py][sample_train_model_without_labels]
* Train a model with labels: [sample_train_model_with_labels.py][sample_train_model_with_labels]
* Manage custom models: [sample_manage_custom_models.py][sample_manage_custom_models]
* Copy a model between Form Recognizer resources: [sample_copy_model.py][sample_copy_model]
* Create a composed model from a collection of models trained with labels: [sample_create_composed_model.py][sample_create_composed_model]

### Async APIs
This library also includes a complete async API supported on Python 3.5+. To use it, you must
first install an async transport, such as [aiohttp](https://pypi.org/project/aiohttp/). Async clients
are found under the `azure.ai.formrecognizer.aio` namespace.

* Client authentication: [sample_authentication_async.py][sample_authentication_async]
* Recognize receipts: [sample_recognize_receipts_async.py][sample_recognize_receipts_async]
* Recognize receipts from a URL: [sample_recognize_receipts_from_url_async.py][sample_recognize_receipts_from_url_async]
* Recognize business cards: [sample_recognize_business_cards_async.py][sample_recognize_business_cards_async]
* Recognize invoices: [sample_recognize_invoices_async.py][sample_recognize_invoices_async]
* Recognize content: [sample_recognize_content_async.py][sample_recognize_content_async]
* Recognize custom forms: [sample_recognize_custom_forms_async.py][sample_recognize_custom_forms_async]
* Train a model without labels: [sample_train_model_without_labels_async.py][sample_train_model_without_labels_async]
* Train a model with labels: [sample_train_model_with_labels_async.py][sample_train_model_with_labels_async]
* Manage custom models: [sample_manage_custom_models_async.py][sample_manage_custom_models_async]
* Copy a model between Form Recognizer resources: [sample_copy_model_async.py][sample_copy_model_async]
* Create a composed model from a collection of models trained with labels: [sample_create_composed_model_async.py][sample_create_composed_model_async]

### Additional documentation

For more extensive documentation on Azure Cognitive Services Form Recognizer, see the [Form Recognizer documentation][python-fr-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-fr-src]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/azure/ai/formrecognizer
[python-fr-pypi]: https://pypi.org/project/azure-ai-formrecognizer/
[python-fr-product-docs]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/overview
[python-fr-ref-docs]: https://aka.ms/azsdk/python/formrecognizer/docs
[python-fr-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples
[train-a-model-using-labeled-data]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/quickstarts/python-labeled-data#train-a-model-using-labeled-data


[training_data]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/build-training-data-set
[azure_subscription]: https://azure.microsoft.com/free/
[FR_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_FR_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer
[azure_cli_create_FR_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[fr-labeling-tool]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/quickstarts/label-tool
[fr-train-without-labels]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/overview#train-without-labels
[fr-train-with-labels]: https://docs.microsoft.com/azure/cognitive-services/form-recognizer/overview#train-with-labels
[prefix_ref_docs]: https://aka.ms/azsdk/python/formrecognizer/docs#azure.ai.formrecognizer.FormTrainingClient.begin_training

[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential
[service_recognize_receipt]: https://aka.ms/formrecognizer/receiptfields
[service_recognize_business_cards]: https://aka.ms/formrecognizer/businesscardfields
[service_recognize_invoice]: https://aka.ms/formrecognizer/invoicefields
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_authentication_async.py
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
[sample_recognize_business_cards]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_business_cards.py
[sample_recognize_business_cards_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_business_cards_async.py
[sample_recognize_invoices]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_recognize_invoices.py
[sample_recognize_invoices_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_recognize_invoices_async.py
[sample_train_model_with_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_with_labels.py
[sample_train_model_with_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_with_labels_async.py
[sample_train_model_without_labels]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_train_model_without_labels.py
[sample_train_model_without_labels_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_train_model_without_labels_async.py
[sample_copy_model]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_copy_model.py
[sample_copy_model_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_copy_model_async.py
[sample_create_composed_model]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/sample_create_composed_model.py
[sample_create_composed_model_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/formrecognizer/azure-ai-formrecognizer/samples/async_samples/sample_create_composed_model_async.py
