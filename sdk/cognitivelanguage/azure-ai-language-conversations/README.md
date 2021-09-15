[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Cognitive Language Services Conversational Language Understanding client library for Python
Conversational Language Understanding, aka LUIS vNext and **CLU** for short, is a cloud-based conversational AI service that applies custom machine-learning intelligence to a user's conversational, natural language text to predict overall meaning, and pull out relevant, detailed information (namely intents and entities).

 Using CLU, you'll get the chance to train conversational language models with new transformer-based model with the following expectations:
-   **State-of-the-art** natural language understanding technology using advanced **neural networks**.
-   **Robust and semantically aware** classification and extraction models.
-   **Fewer** options and dials providing a **simpler** model building experience.
-   **Natively multilingual models** that enables you to train in one language and test in others.

[Source code][conversationallanguage_client_src] | [Package (PyPI)][conversationallanguage_pypi_package] | [API reference documentation][conversationallanguage_refdocs] | [Product documentation][conversationallanguage_docs] | [Samples][conversationallanguage_samples]


## Getting started

### Prerequisites

* Python 2.7, or 3.6 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* An existing CLU resource

> Note: the new unified Cognitive Language Services are not currently available for deployment.

### Install the package

Install the Azure Conversations client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-conversations
```

### Authenticate the client
In order to interact with the CLU service, you'll need to create an instance of the [ConversationAnalysisClient][conversationanalysis_client_class] class. You will need an **endpoint**, and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

#### Get an API key
You can get the **endpoint** and an **API key** from the Cognitive Services resource or CLU resource in the [Azure Portal][azure_portal].

Alternatively, use the [Azure CLI][azure_cli] command shown below to get the API key from the Question Answering resource.

```powershell
az cognitiveservices account keys list --resource-group <resource-group-name> --name <resource-name>
```


#### Create ConversationAnalysisClient
Once you've determined your **endpoint** and **API key** you can instantiate a `ConversationAnalysisClient`:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

endpoint = "https://{myaccount}.api.cognitive.microsoft.com"
credential = AzureKeyCredential("{api-key}")

client = ConversationAnalysisClient(endpoint, credential)
```


## Key concepts

### ConversationAnalysisClient
The [ConversationAnalysisClient][conversationanalysis_client_class] is the primary interface used for extracting custom intents and entities from user utterance using your own CLU's pretrained models. For asynchronous operations, an async `ConversationAnalysisClient` is in the `azure.ai.language.conversation.aio` namespace.

## Examples
The `azure-ai-language-conversation` client library provides both synchronous and asynchronous APIs.

The following examples show common scenarios using the `client` [created above](#create-conversationanalysisclient).
- [Test Deepstack](#ask-a-question)
- [Test Workflow](#ask-a-follow-up-question)
- [Test Workflow Direct](#asynchronous-operations)


## Optional Configuration
Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation][azure_core_ref_docs] describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General


### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` argument.

See full SDK logging documentation with examples [here][sdk_logging_docs].

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
[conversationallanguage_client_src]: https://github.com/Azure/azure-sdk-for-python/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_pypi_package]: https://github.com/Azure/azure-sdk-for-python/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_refdocs]: https://github.com/Azure/azure-sdk-for-python/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_docs]: https://azure.microsoft.com/en-us/services/cognitive-services/language-understanding-intelligent-service/
[conversationallanguage_samples]: https://github.com/Azure/azure-sdk-for-python/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/README.md
[conversationanalysis_client_class]: https://github.com/Azure/azure-sdk-for-python/main/sdk/cognitivelanguage/azure-ai-language-conversations/azure/ai/language/conversations/_conversation_analysis_client.py

![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fsdk%2Ftemplate%2Fazure-template%2FREADME.png)
