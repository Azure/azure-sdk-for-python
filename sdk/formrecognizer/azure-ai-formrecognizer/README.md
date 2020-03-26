# Azure Form Recognizer client library for Python

* TODO
* TODO

[Source code][TODO] | [Package (PyPI)][TODO] | [API reference documentation][TODO]| [Product documentation][TODO] | [Samples][TODO]

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

**Option 1:** [Azure Portal][TODO]

**Option 2:** [Azure CLI][TODO].
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
The `credential` parameter may be provided as a `FormRecognizerApiKeyCredential`.
See the full details regarding [authentication][cognitive_authentication] of cognitive services.

To use an [API key][cognitive_authentication_api_key],
pass the key as a string into an instance of `FormRecognizerApiKeyCredential("<api_key>")`.
The API key can be found in the Azure Portal or by running the following Azure CLI command:

```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

Use the key as the credential parameter to authenticate the client:
```python
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiKeyCredential

credential = FormRecognizerApiKeyCredential("<api_key>")
client = FormRecognizerClient(endpoint, credential)
```

## Key concepts


## Examples


## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][TODO]
describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General
Form Recognizer client library will raise exceptions defined in [Azure Core][azure_core].

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
from azure.ai.formrecognizer import FormRecognizerClient, FormRecognizerApiKeyCredential

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = FormRecognizerApiKeyCredential("<api_key>")

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = FormRecognizerClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
result = client.begin_extract_receipts(receipt, logging_enable=True)
```

## Next steps

### More sample code

### Additional documentation


## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_subscription]: https://azure.microsoft.com/free/
[FR_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/

[azure_core]: ../../core/azure-core/README.md
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