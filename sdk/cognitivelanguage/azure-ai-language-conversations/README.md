[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversational Language Understanding client library for Python
Conversational Language Understanding - aka **CLU** for short - is a cloud-based conversational AI service which provides many language understanding capabilities like:
- Conversation App: It's used in extracting intents and entities in conversations
- Workflow app: Acts like an orchestrator to select the best candidate to analyze conversations to get best response from apps like Qna, Luis, and Conversation App


[Source code][conversationallanguage_client_src] | [Package (PyPI)][conversationallanguage_pypi_package] | [API reference documentation][api_reference_documentation] | [Product documentation][conversationallanguage_docs] | [Samples][conversationallanguage_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_


## Getting started

### Prerequisites

* Python 3.6 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* An existing Azure Language Service Resource


### Install the package

Install the Azure Conversations client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-conversations
```

### Authenticate the client
In order to interact with the CLU service, you'll need to create an instance of the [ConversationAnalysisClient][conversationanalysis_client_class] class, or [ConversationAuthoringClient][conversationauthoring_client_class] class. You will need an **endpoint**, and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### Get an API key
You can get the **endpoint** and an **API key** from the Cognitive Services resource in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] command shown below to get the API key from the Cognitive Service resource.

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```


#### Create ConversationAnalysisClient
Once you've determined your **endpoint** and **API key** you can instantiate a `ConversationAnalysisClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api-key>")
client = ConversationAnalysisClient(endpoint, credential)
```

#### Create ConversationAuthoringClient
Once you've determined your **endpoint** and **API key** you can instantiate a `ConversationAuthoringClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<api-key>")
client = ConversationAuthoringClient(endpoint, credential)
```

#### Create a client with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]
- [Register a new AAD application][register_aad_app]
- [Grant access][grant_role_access] to the Language service by assigning the "Cognitive Services User" role to your service principal.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
from azure.ai.textanalytics import ConversationAnalysisClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = ConversationAnalysisClient(endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/", credential=credential)
```

## Key concepts

### ConversationAnalysisClient
The [ConversationAnalysisClient][conversationanalysis_client_class] is the primary interface for making predictions using your deployed Conversations models. For asynchronous operations, an async `ConversationAnalysisClient` is in the `azure.ai.language.conversation.aio` namespace.

### ConversationAnalysisClient
You can use the [ConversationAuthoringClient][conversationauthoring_client_class] to interface with the [Azure Language Portal][azure_language_portal] to carry out authoring operations on your language resource/project. For example, you can use it to create a project, populate with training data, train, test, and deploy. For asynchronous operations, an async `ConversationAnalysisClient` is in the `azure.ai.language.conversation.authoring.aio` namespace.

## Examples
The `azure-ai-language-conversation` client library provides both synchronous and asynchronous APIs.

The following examples show common scenarios using the `client` [created above](#create-conversationanalysisclient).

### Analyze Text with a Conversation App
If you would like to extract custom intents and entities from a user utterance, you can call the `client.analyze_conversation()` method with your conversation's project name as follows:


```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

# get secrets
clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

# analyze quey
client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
with client:
    query = "Send an email to Carol about the tomorrow's demo"
    result = client.analyze_conversation(
        task={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "participantId": "1",
                    "id": "1",
                    "modality": "text",
                    "language": "en",
                    "text": query
                },
                "isLoggingEnabled": False
            },
            "parameters": {
                "projectName": project_name,
                "deploymentName": deployment_name,
                "verbose": True
            }
        }
    )

# view result
print("query: {}".format(result["result"]["query"]))
print("project kind: {}\n".format(result["result"]["prediction"]["projectKind"]))

print("top intent: {}".format(result["result"]["prediction"]["topIntent"]))
print("category: {}".format(result["result"]["prediction"]["intents"][0]["category"]))
print("confidence score: {}\n".format(result["result"]["prediction"]["intents"][0]["confidenceScore"]))

print("entities:")
for entity in result["result"]["prediction"]["entities"]:
    print("\ncategory: {}".format(entity["category"]))
    print("text: {}".format(entity["text"]))
    print("confidence score: {}".format(entity["confidenceScore"]))
    if "resolutions" in entity:
        print("resolutions")
        for resolution in entity["resolutions"]:
            print("kind: {}".format(resolution["resolutionKind"]))
            print("value: {}".format(resolution["value"]))
    if "extraInformation" in entity:
        print("extra info")
        for data in entity["extraInformation"]:
            print("kind: {}".format(data["extraInformationKind"]))
            if data["extraInformationKind"] == "ListKey":
                print("key: {}".format(data["key"]))
            if data["extraInformationKind"] == "EntitySubtype":
                print("value: {}".format(data["value"]))
```

### Analyze Text with an Orchestration App

If you would like to pass the user utterance to your orchestrator (worflow) app, you can call the `client.analyze_conversation()` method with your orchestration's project name. The orchestrator project simply orchestrates the submitted user utterance between your language apps (Luis, Conversation, and Question Answering) to get the best response according to the user intent. See the next example:


```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

# get secrets
clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]
project_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"]
deployment_name = os.environ["AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME"]

# analyze query
client = ConversationAnalysisClient(clu_endpoint, AzureKeyCredential(clu_key))
with client:
    query = "Reserve a table for 2 at the Italian restaurant"
    result = client.analyze_conversation(
        task={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "participantId": "1",
                    "id": "1",
                    "modality": "text",
                    "language": "en",
                    "text": query
                },
                "isLoggingEnabled": False
            },
            "parameters": {
                "projectName": project_name,
                "deploymentName": deployment_name,
                "verbose": True
            }
        }
    )

# view result
print("query: {}".format(result["result"]["query"]))
print("project kind: {}\n".format(result["result"]["prediction"]["projectKind"]))

# top intent
top_intent = result["result"]["prediction"]["topIntent"]
print("top intent: {}".format(top_intent))
top_intent_object = result["result"]["prediction"]["intents"][top_intent]
print("confidence score: {}".format(top_intent_object["confidenceScore"]))
print("project kind: {}".format(top_intent_object["targetProjectKind"]))

if top_intent_object["targetProjectKind"] == "Luis":
    print("\nluis response:")
    luis_response = top_intent_object["result"]["prediction"]
    print("top intent: {}".format(luis_response["topIntent"]))
    print("\nentities:")
    for entity in luis_response["entities"]:
        print("\n{}".format(entity))
```

### Import a Conversation Project
This sample shows a common scenario for the authoring part of the SDK

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient

clu_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
clu_key = os.environ["AZURE_CONVERSATIONS_KEY"]

project_name = "test_project"

exported_project_assets = {
    "projectKind": "Conversation",
    "intents": [{"category": "Read"}, {"category": "Delete"}],
    "entities": [{"category": "Sender"}],
    "utterances": [
        {
            "text": "Open Blake's email",
            "dataset": "Train",
            "intent": "Read",
            "entities": [{"category": "Sender", "offset": 5, "length": 5}],
        },
        {
            "text": "Delete last email",
            "language": "en-gb",
            "dataset": "Test",
            "intent": "Delete",
            "entities": [],
        },
    ],
}

client = ConversationAuthoringClient(
    clu_endpoint, AzureKeyCredential(clu_key)
)
poller = client.begin_import_project(
    project_name=project_name,
    project={
        "assets": exported_project_assets,
        "metadata": {
            "projectKind": "Conversation",
            "settings": {"confidenceThreshold": 0.7},
            "projectName": "EmailApp",
            "multilingual": True,
            "description": "Trying out CLU",
            "language": "en-us",
        },
        "projectFileVersion": "2022-05-01",
    },
)
response = poller.result()
print(response)

```


## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General

The Conversations client will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging

This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

```python
import sys
import logging
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = AzureKeyCredential("<my-api-key>")

# This client will log detailed information about its HTTP sessions, at DEBUG level
client = ConversationAnalysisClient(endpoint, credential, logging_enable=True)
result = client.analyze_conversation(...)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:

```python
result = client.analyze_conversation(..., logging_enable=True)
```

## Next steps

### More sample code

See the [Sample README][conversationallanguage_samples] for several code snippets illustrating common patterns used in the CLU Python API.

## Contributing

See the [CONTRIBUTING.md][contributing] for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure/
[azure_portal]: https://portal.azure.com/
[azure_subscription]: https://azure.microsoft.com/free/

[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[cognitive_auth]: https://docs.microsoft.com/azure/cognitive-services/authentication/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://docs.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]:https://pypi.org/project/pip/
[conversationallanguage_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_pypi_package]: https://pypi.org/project/azure-ai-language-conversations/
[api_reference_documentation]:https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html
[conversationallanguage_refdocs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_docs]: https://docs.microsoft.com/azure/cognitive-services/language-service/conversational-language-understanding/overview
[conversationallanguage_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/README.md
[conversationanalysis_client_class]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html#azure.ai.language.conversations.ConversationAnalysisClient
[conversationauthoring_client_class]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html#azure.ai.language.conversations.ConversationAuthoringClient
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_language_portal]: https://language.cognitive.azure.com/home
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
