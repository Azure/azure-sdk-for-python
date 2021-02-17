# Azure Text Analytics client library for Python

Text Analytics is a cloud-based service that provides advanced natural language processing over raw text, and includes the following main functions:

- Sentiment Analysis
- Named Entity Recognition
- Linked Entity Recognition
- Personally Identifiable Information (PII) Entity Recognition
- Language Detection
- Key Phrase Extraction

## Getting started

### Prerequisites

- Python 2.7, or 3.5 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and a
  [Cognitive Services or Text Analytics resource][ta_or_cs_resource] to use this package.

#### Create a Cognitive Services or Text Analytics resource

Text Analytics supports both [multi-service and single-service access][multi_and_single_service].
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Text Analytics access only, create a Text Analytics resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_ta_resource]

**Option 2:** [Azure CLI][azure_cli_create_ta_resource].
Below is an example of how you can create a Text Analytics resource using the CLI:

```bash
# Create a new resource group to hold the text analytics resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2
```

```bash
# Create text analytics
az cognitiveservices account create \
    --name text-analytics-resource \
    --resource-group my-resource-group \
    --kind TextAnalytics \
    --sku F0 \
    --location westus2 \
    --yes
```

Interaction with this service begins with an instance of a [client](#textanalyticsclient "TextAnalyticsClient").
To create a client object, you will need the cognitive services or text analytics `endpoint` to
your resource and a `credential` that allows you access:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
text_analytics_client = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
```

Note that if you create a [custom subdomain][cognitive_custom_subdomain]
name for your resource the endpoint may look different than in the above code snippet.
For example, `https://<my-custom-subdomain>.cognitiveservices.azure.com/`.

### Install the package

Install the Azure Text Analytics client library for Python with [pip][pip]:

```bash
pip install azure-ai-textanalytics --pre
```

> Note: This version of the client library defaults to the v3.1-preview version of the service

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version                                                               | Supported API version of service  |
| ------------------------------------------------------------------------- | --------------------------------- |
| 5.0.0 - Latest GA release (can be installed by removing the `--pre` flag) | 3.0                               |
| 5.1.0b5 - Latest release (beta)                                           | 3.0, 3.1-preview.2, 3.1-preview.3 |

### Authenticate the client

#### Get the endpoint

You can find the endpoint for your text analytics resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the text analytics resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API Key

You can get the [API key][cognitive_authentication_api_key] from the Cognitive Services or Text Analytics resource in the [Azure Portal][azure_portal_get_endpoint].
Alternatively, you can use [Azure CLI][azure_cli_endpoint_lookup] snippet below to get the API key of your resource.

`az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"`

#### Create a TextAnalyticsClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of [AzureKeyCredential][azure-key-credential]. Use the key as the credential parameter
to authenticate the client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
text_analytics_client = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
```

#### Create a TextAnalyticsClient with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]
- [Register a new AAD application][register_aad_app]
- [Grant access][grant_role_access] to Text Analytics by assigning the `"Cognitive Services User"` role to your service principal.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
text_analytics_client = TextAnalyticsClient(endpoint="https://<my-custom-subdomain>.api.cognitive.microsoft.com/", credential=credential)
```

## Key concepts

### TextAnalyticsClient

The Text Analytics client library provides a `TextAnalyticsClient` for authentication and calls to the service to analyze on [batches of documents](#examples "Examples").
It provides both a synchronous and asynchronous caller `send_request` to send requests to the Text Analytics Service.

### Request Preparers

We offer request preparers to help you create requests for each of the documented endpoints. With the request preparers, we handle things like
the URL path and formatting query and header parameters.

### API versions

When using our main request preparers, you need to provide an API version to the request call. For example, if you want to use `v3.0` of the REST API,
calls to each request preparer would need to include `api_version="v3.0"`.

### Input

A **document** is a single unit to be analyzed by the predictive models in the Text Analytics service. Each document needs to include an `id`
and `text` entry. See the [REST API documentation][rest_api_docs] for more examples

An example input is
```python
{
  "documents": [
    {
      "countryHint": "US",
      "id": "1",
      "text": "Hello world"
    },
    {
      "id": "2",
      "text": "Bonjour tout le monde"
    },
    {
      "id": "3",
      "text": "La carretera estaba atascada. Había mucho tráfico el día de ayer."
    }
  ]
}
```

See [service limitations][service_limits] for the input, including document length limits, maximum batch size, and supported text encoding.

### Return Value

See the [REST API docs][rest_api_docs] for examples of good and bad responses.

## Examples

The following section show two ways of sending requests. Please see the [REST API docs][rest_api_docs] for more examples
of what requests and responses should look like.

- [Sending a Request](#sending-a-request "Sending a Request")
- [Sending a Request with Preparers](#sending-a-request-with-preparers "Sending a Request with Preparers")

### Sending a Request

For the lowest-level call, you can create your own request and send it through our `TextAnalyticsClient`s `send_request` caller.
Here, we make the call shown in [this][rest_api_docs] REST API doc

```python
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.ai.textanalytics import TextAnalyticsClient

client = TextAnalyticsClient(
    endpoint="<my endpoint>",
    credential=DefaultAzureCredential(),
)

request = HttpRequest("POST", "/text/analytics/v3.0/languages",
    json={
        "documents": [
            {
                "countryHint": "US",
                "id": "1",
                "text": "Hello world"
            },
            {
                "id": "2",
                "text": "Bonjour tout le monde"
            },
            {
                "id": "3",
                "text": "La carretera estaba atascada. Había mucho tráfico el día de ayer."
            }
        ]
    }
)

response: HttpResponse = client.send_request(request)
response.raise_for_status()

json_response = response.json()

error_doc_ids = [error['id'] for error in json_response['errors']]
good_docs = [doc for doc in json_response['documents'] if doc['id'] not in error_doc_ids]

doc_languages = [doc['detectedLanguage']['name'] for doc in good_docs]
```

If you want a bit more support in creating your requests, please see how to [send a request with preparers](#sending-a-request-with-preparers).

### Sending a Request with Preparers

We also offer request preparers to provide you with more support in crafting your requests. We will follow the same example flow as
[above](#sending-a-request).

```python
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.ai.textanalytics import TextAnalyticsClient
from azure.ai.textanalytics.protocol import TextAnalyticsPreparers

client = TextAnalyticsClient(
    endpoint="<my endpoint>",
    credential=DefaultAzureCredential(),
)

request: HttpRequest = TextAnalyticsPreparers.prepare_languages(
    api_version='v3.1-preview.1',
    body={
        "documents": [
            {
                "countryHint": "US",
                "id": "1",
                "text": "Hello world"
            },
            {
                "id": "2",
                "text": "Bonjour tout le monde"
            },
            {
                "id": "3",
                "text": "La carretera estaba atascada. Había mucho tráfico el día de ayer."
            }
        ]
    }
)

response: HttpResponse = client.send_request(request)
response.raise_for_status()

json_response = response.json()

error_doc_ids = [error['id'] for error in json_response['errors']]
good_docs = [doc for doc in json_response['documents'] if doc['id'] not in error_doc_ids]

doc_languages = [doc['detectedLanguage']['name'] for doc in good_docs]
```

## Troubleshooting

### General

The Text Analytics client will raise exceptions defined in [Azure Core][azure_core].

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument.

```python
from azure.identity import DefaultAzureCredential
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.ai.textanalytics import TextAnalyticsClient

client = TextAnalyticsClient(
    endpoint="<my endpoint>",
    credential=DefaultAzureCredential(),
    logging_enable=True
)
```

### Additional documentation

For more extensive documentation on Azure Cognitive Services Text Analytics' REST API endpoint, see [here][rest_api_docs]

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics
[ta_pypi]: https://pypi.org/project/azure-ai-textanalytics/
[ta_ref_docs]: https://aka.ms/azsdk-python-textanalytics-ref-docs
[ta_samples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples
[ta_product_documentation]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview
[azure_subscription]: https://azure.microsoft.com/free/
[ta_or_cs_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_ta_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[azure_cli_create_ta_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential
[service_limits]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
[azure-key-credential]: https://aka.ms/azsdk-python-core-azurekeycredential
[document_error]: https://aka.ms/azsdk-python-textanalytics-documenterror
[detect_language_result]: https://aka.ms/azsdk-python-textanalytics-detectlanguageresult
[recognize_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizeentitiesresult
[recognize_pii_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizepiientitiesresult
[recognize_linked_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizelinkedentitiesresult
[analyze_sentiment_result]: https://aka.ms/azsdk-python-textanalytics-analyzesentimentresult
[extract_key_phrases_result]: https://aka.ms/azsdk-python-textanalytics-extractkeyphrasesresult
[text_document_input]: https://aka.ms/azsdk-python-textanalytics-textdocumentinput
[detect_language_input]: https://aka.ms/azsdk-python-textanalytics-detectlanguageinput
[text_analytics_client]: https://aka.ms/azsdk-python-textanalytics-textanalyticsclient
[analyze_sentiment]: https://aka.ms/azsdk-python-textanalytics-analyzesentiment
[recognize_entities]: https://aka.ms/azsdk-python-textanalytics-recognizeentities
[recognize_pii_entities]: https://aka.ms/azsdk-python-textanalytics-recognizepiientities
[recognize_linked_entities]: https://aka.ms/azsdk-python-textanalytics-recognizelinkedentities
[extract_key_phrases]: https://aka.ms/azsdk-python-textanalytics-extractkeyphrases
[detect_language]: https://aka.ms/azsdk-python-textanalytics-detectlanguage
[language_detection]: https://docs.microsoft.com/azure/cognitive-services/Text-Analytics/how-tos/text-analytics-how-to-language-detection
[language_and_regional_support]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/language-support
[sentiment_analysis]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-sentiment-analysis
[key_phrase_extraction]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-keyword-extraction
[linked_entities_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=general
[linked_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-entity-linking
[pii_entity_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal
[named_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-entity-linking
[named_entity_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=general
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[python_logging]: https://docs.python.org/3.5/library/logging.html
[rest_api_docs]: https://westus2.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-1-preview-1/operations/Languages
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
