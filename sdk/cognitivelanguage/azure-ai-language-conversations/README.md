[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversational Language Understanding client library for Python
Conversational Language Understanding - aka **CLU** for short - is a cloud-based conversational AI service which provides many language understanding capabilities like:
- Conversation App: It's used in extracting intents and entities in conversations
- Workflow app: Acts like an orchestrator to select the best candidate to analyze conversations to get best response from apps like Qna, Luis, and Conversation App
- Conversational Issue Summarization: Used to summarize conversations in the form of issues, and final resolutions
- Conversational PII: Used to extract and redact personally-identifiable info (PII) 

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
In order to interact with the CLU service, you'll need to create an instance of the [ConversationAnalysisClient][conversationanalysis_client_class] class. You will need an **endpoint**, and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

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


## Key concepts

### ConversationAnalysisClient
The [ConversationAnalysisClient][conversationanalysis_client_class] is the primary interface for making predictions using your deployed Conversations models. For asynchronous operations, an async `ConversationAnalysisClient` is in the `azure.ai.language.conversation.aio` namespace.

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

### Conversational Issue Summarization

You can use this sample if you need to summarize a conversation in the form of an issue, and final resolution. For example, a dialog from tech support:

```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations import ConversationAnalysisClient

# get secrets
endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
key = os.environ["AZURE_CONVERSATIONS_KEY"]

# analyze quey
client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
with client:
    poller = client.begin_conversation_analysis(
        task={
            "displayName": "Analyze conversations from xxx",
            "analysisInput": {
                "conversations": [
                    {
                        "conversationItems": [
                            {
                                "text": "Hello, how can I help you?",
                                "modality": "text",
                                "id": "1",
                                "participantId": "Agent"
                            },
                            {
                                "text": "How to upgrade Office? I am getting error messages the whole day.",
                                "modality": "text",
                                "id": "2",
                                "participantId": "Customer"
                            },
                            {
                                "text": "Press the upgrade button please. Then sign in and follow the instructions.",
                                "modality": "text",
                                "id": "3",
                                "participantId": "Agent"
                            }
                        ],
                        "modality": "text",
                        "id": "conversation1",
                        "language": "en"
                    },
                ]
            },
            "tasks": [
                {
                    "taskName": "analyze 1",
                    "kind": "ConversationalSummarizationTask",
                    "parameters": {
                        "summaryAspects": ["Issue, Resolution"]
                    }
                }
            ]
        }
    )

    # view result
    result = poller.result()
    task_result = result["tasks"]["items"][0]
    print("... view task status ...")
    print("status: {}".format(task_result["status"]))
    issue_resolution_result = task_result["results"]
    if issue_resolution_result["errors"]:
        print("... errors occured ...")
        for error in issue_resolution_result["errors"]:
            print(error)
    else:
        conversation_result = issue_resolution_result["conversations"][0]
        if conversation_result["warnings"]:
            print("... view warnings ...")
            for warning in conversation_result["warnings"]:
                print(warning)
        else:
            summaries = conversation_result["summaries"]
            print("... view task result ...")
            print("issue: {}".format(summaries[0]["text"]))
            print("resolution: {}".format(summaries[1]["text"]))

```

### Conversational PII

You can use this sample if you need to extract and redact pii info from/in conversations

```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations import ConversationAnalysisClient

# get secrets
endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
key = os.environ["AZURE_CONVERSATIONS_KEY"]

# analyze quey
client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
with client:

    poller = client.begin_conversation_analysis(
        task={
            "displayName": "Analyze PII in conversation",
            "analysisInput": {
                "conversations": [
                    {
                        "conversationItems": [
                            {
                                "id": "1",
                                "participantId": "0",
                                "modality": "transcript",
                                "text": "It is john doe.",
                                "lexical": "It is john doe",
                                "itn": "It is john doe",
                                "maskedItn": "It is john doe"
                            },
                            {
                                "id": "2",
                                "participantId": "1",
                                "modality": "transcript",
                                "text": "Yes, 633-27-8199 is my phone",
                                "lexical": "yes six three three two seven eight one nine nine is my phone",
                                "itn": "yes 633278199 is my phone",
                                "maskedItn": "yes 633278199 is my phone",
                            },
                            {
                                "id": "3",
                                "participantId": "1",
                                "modality": "transcript",
                                "text": "j.doe@yahoo.com is my email",
                                "lexical": "j dot doe at yahoo dot com is my email",
                                "maskedItn": "j.doe@yahoo.com is my email",
                                "itn": "j.doe@yahoo.com is my email",
                            }
                        ],
                        "modality": "transcript",
                        "id": "1",
                        "language": "en"
                    }
                ]
            },
            "tasks": [
                {
                    "kind": "ConversationalPIITask",
                    "parameters": {
                        "redactionSource": "lexical",
                        "piiCategories": [
                            "all"
                        ]
                    }
                }
            ]
        }
    )

    # view result
    result = poller.result()
    task_result = result["tasks"]["items"][0]
    print("... view task status ...")
    print("status: {}".format(task_result["status"]))
    conv_pii_result = task_result["results"]
    if conv_pii_result["errors"]:
        print("... errors occured ...")
        for error in conv_pii_result["errors"]:
            print(error)
    else:
        conversation_result = conv_pii_result["conversations"][0]
        if conversation_result["warnings"]:
            print("... view warnings ...")
            for warning in conversation_result["warnings"]:
                print(warning)
        else:
            print("... view task result ...")
            for conversation in conversation_result["conversationItems"]:
                print("conversation id: {}".format(conversation["id"]))
                print("... entities ...")
                for entity in conversation["entities"]:
                    print("text: {}".format(entity["text"]))
                    print("category: {}".format(entity["category"]))
                    print("confidence: {}".format(entity["confidenceScore"]))
                    print("offset: {}".format(entity["offset"]))
                    print("length: {}".format(entity["length"]))

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
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
