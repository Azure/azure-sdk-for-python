[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversational Language Understanding client library for Python
Conversational Language Understanding, aka **CLU** for short, is a cloud-based conversational AI service which is mainly used in bots to extract useful information from user utterance (natural language processing).
The CLU **analyze api** encompasses two projects; deepstack, and workflow projects.
You can use the "deepstack" project if you want to extract intents (intention behind a user utterance] and custom entities.
You can also use the "workflow" project which orchestrates multiple language apps to get the best response (language apps like Question Answering, Luis, and Deepstack).

[Source code][conversationallanguage_client_src] | [Package (PyPI)][conversationallanguage_pypi_package] | [API reference documentation][conversationallanguage_refdocs] | [Product documentation][conversationallanguage_docs] | [Samples][conversationallanguage_samples]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 is ending 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_


## Getting started

### Prerequisites

* Python 2.7, or 3.6 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* An existing Text Analytics resource

> Note: the new unified Cognitive Language Services are not currently available for deployment.

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

### Analyze a conversation with a Deepstack App
If you would like to extract custom intents and entities from a user utterance, you can call the `client.analyze_conversations()` method with your deepstack's project name as follows:

```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import AnalyzeConversationOptions

# get secrets
conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
conv_project = os.environ["AZURE_CONVERSATIONS_PROJECT"]

# prepare data
query = "One california maki please."
input = AnalyzeConversationOptions(
    query=query
)

# analyze quey
client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
with client:
    result = client.analyze_conversations(
        input,
        project_name=conv_project,
        deployment_name='production'
    )

# view result
print("query: {}".format(result.query))
print("project kind: {}\n".format(result.prediction.project_kind))

print("view top intent:")
print("top intent: {}".format(result.prediction.top_intent))
print("\tcategory: {}".format(result.prediction.intents[0].category))
print("\tconfidence score: {}\n".format(result.prediction.intents[0].confidence_score))

print("view entities:")
for entity in result.prediction.entities:
    print("\tcategory: {}".format(entity.category))
    print("\ttext: {}".format(entity.text))
    print("\tconfidence score: {}".format(entity.confidence_score))
```

### Analyze conversation with a Workflow App

If you would like to pass the user utterance to your orchestrator (worflow) app, you can call the `client.analyze_conversations()` method with your workflow's project name. The orchestrator project simply orchestrates the submitted user utterance between your language apps (Luis, Deepstack, and Question Answering) to get the best response according to the user intent. See the next example:

```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import AnalyzeConversationOptions

# get secrets
conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
workflow_project = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT")

# prepare data
query = "How do you make sushi rice?",
input = AnalyzeConversationOptions(
    query=query
)

# analyze query
client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
with client:
    result = client.analyze_conversations(
        input,
        project_name=workflow_project,
        deployment_name='production',
    )

# view result
print("query: {}".format(result.query))
print("project kind: {}\n".format(result.prediction.project_kind))

print("view top intent:")
print("top intent: {}".format(result.prediction.top_intent))
print("\tcategory: {}".format(result.prediction.intents[0].category))
print("\tconfidence score: {}\n".format(result.prediction.intents[0].confidence_score))

print("view Question Answering result:")
print("\tresult: {}\n".format(result.prediction.intents[0].result))
```

### Analyze conversation with a Workflow (Direct) App

If you would like to use an orchestrator (workflow) app, and you want to call a specific one of your language apps directly, you can call the `client.analyze_conversations()` method with your workflow's project name and the diirect target name which corresponds to your one of you language apps as follows:

```python
# import libraries
import os
from azure.core.credentials import AzureKeyCredential

from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import AnalyzeConversationOptions

# get secrets
conv_endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
conv_key = os.environ["AZURE_CONVERSATIONS_KEY"]
workflow_project = os.environ["AZURE_CONVERSATIONS_WORKFLOW_PROJECT")

# prepare data
query = "How do you make sushi rice?",
target_intent = "SushiMaking"
input = AnalyzeConversationOptions(
    query=query,
    direct_target=target_intent,
    parameters={
        "SushiMaking": QuestionAnsweringParameters(
            calling_options={
                "question": query,
                "top": 1,
                "confidenceScoreThreshold": 0.1
            }
        )
    }
)

# analyze query
client = ConversationAnalysisClient(conv_endpoint, AzureKeyCredential(conv_key))
with client:
    result = client.analyze_conversations(
        input,
        project_name=workflow_project,
        deployment_name='production',
    )

# view result
print("query: {}".format(result.query))
print("project kind: {}\n".format(result.prediction.project_kind))

print("view top intent:")
print("top intent: {}".format(result.prediction.top_intent))
print("\tcategory: {}".format(result.prediction.intents[0].category))
print("\tconfidence score: {}\n".format(result.prediction.intents[0].confidence_score))

print("view Question Answering result:")
print("\tresult: {}\n".format(result.prediction.intents[0].result))
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
result = client.analyze_conversations(...)
```

Similarly, `logging_enable` can enable detailed logging for a single operation, even when it isn't enabled for the client:

```python
result = client.analyze_conversations(..., logging_enable=True)
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
[conversationallanguage_pypi_package]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_refdocs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_docs]: https://azure.microsoft.com/services/cognitive-services/language-understanding-intelligent-service/
[conversationallanguage_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/README.md
[conversationanalysis_client_class]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/azure/ai/language/conversations/_conversation_analysis_client.py
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
