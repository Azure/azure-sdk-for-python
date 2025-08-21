[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversational Language Understanding client library for Python
Conversational Language Understanding - aka **CLU** for short - is a cloud-based conversational AI service which provides many language understanding capabilities like:
- Conversation App: It's used in extracting intents and entities in conversations
- Workflow app: Acts like an orchestrator to select the best candidate to analyze conversations to get best response from apps like Qna, Luis, and Conversation App
- Conversational Summarization: Used to analyze conversations in the form of issues/resolution, chapter title, and narrative summarizations

[Source code][conversationallanguage_client_src]
| [Package (PyPI)][conversationallanguage_pypi_package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-language-conversations/)
| [API reference documentation][api_reference_documentation]
| [Samples][conversationallanguage_samples]
| [Product documentation][conversationallanguage_docs]
| [REST API documentation][conversationallanguage_restdocs]

## Getting started

### Prerequisites

* Python 3.7 or later is required to use this package.
* An [Azure subscription][azure_subscription]
* A [Language service resource][language_resource]


### Install the package

Install the Azure Conversations client library for Python with [pip][pip_link]:

```bash
pip install azure-ai-language-conversations
```

> Note: This version of the client library defaults to the 2025-05-15-preview version of the service

### Authenticate the client
In order to interact with the CLU service, you'll need to create an instance of the [ConversationAnalysisClient][conversationanalysisclient_class] class. You will need an **endpoint**, and an **API key** to instantiate a client object. For more information regarding authenticating with Cognitive Services, see [Authenticate requests to Azure Cognitive Services][cognitive_auth].

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

#### Create a client with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]
- [Register a new AAD application][register_aad_app]
- [Grant access][grant_role_access] to the Language service by assigning the "Cognitive Services Language Reader" role to your service principal.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`

Use the returned token credential to authenticate the client:

```python
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = ConversationAnalysisClient(endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/", credential=credential)
```

## Key concepts

### ConversationAnalysisClient
The [ConversationAnalysisClient][conversationanalysisclient_class] is the primary interface for making predictions using your deployed Conversations models. For asynchronous operations, an async `ConversationAnalysisClient` is in the `azure.ai.language.conversation.aio` namespace.

## Examples
The `azure-ai-language-conversation` client library provides both synchronous and asynchronous APIs.

You can familiarize yourself with different APIs using [Samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples).

### Sync version 
* [Analyze a conversation - Conversation project](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction.py)
* [Analyze a conversation - Orchestration project](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_orchestration_prediction.py)
* [Analyze a conversation in a different language](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction_with_language.py)
* [Analyze a conversation using extra options](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction_with_options.py)
* [Analyze a conversation - Multi-turn analysis](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_multi_turn_prediction.py)
* [Analyze a conversation with Conversation Summarization](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_summarization.py)
* [Analyze a conversation with Conversation PII](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii.py)
* [Analyze a Conversation for PII Using Character Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_character_mask_policy.py)
* [Analyze a Conversation for PII Using Entity Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_entity_mask_policy.py)
* [Analyze a Conversation for PII With No Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_no_mask_policy.py)

### Async version
* [Analyze a conversation - Conversation project](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_async.py)
* [Analyze a conversation - Orchestration project](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_orchestration_prediction_async.py)
* [Analyze a conversation in a different language](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_with_language_async.py)
* [Analyze a conversation using extra options](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_with_options_async.py)
* [Analyze a conversation - Multi-turn analysis](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_multi_turn_prediction_async.py)
* [Analyze a conversation with Conversation Summarization](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_summarization_async.py)
* [Analyze a conversation with Conversation PII](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_async.py)
* [Analyze a Conversation for PII Using Character Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_character_mask_policy_async.py)
* [Analyze a Conversation for PII Using Entity Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_entity_mask_policy_async.py)
* [Analyze a Conversation for PII With No Masking](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_no_mask_policy_async.py)

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

## Contributing

See the [CONTRIBUTING.md][contributing] for details on building, testing, and contributing to this library.

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://learn.microsoft.com/cli/azure/
[azure_portal]: https://portal.azure.com/
[azure_subscription]: https://azure.microsoft.com/free/
[language_resource]: https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[cla]: https://cla.microsoft.com
[coc_contact]: mailto:opencode@microsoft.com
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[cognitive_auth]: https://learn.microsoft.com/azure/cognitive-services/authentication/
[contributing]: https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-core/latest/azure.core.html
[azure_core_readme]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[pip_link]:https://pypi.org/project/pip/
[conversationallanguage_client_src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_pypi_package]: https://pypi.org/project/azure-ai-language-conversations/
[api_reference_documentation]:https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html
[conversationallanguage_refdocs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations
[conversationallanguage_docs]: https://learn.microsoft.com/azure/cognitive-services/language-service/conversational-language-understanding/overview
[conversationallanguage_samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/README.md
[conversationallanguage_restdocs]: https://learn.microsoft.com/rest/api/language/
[conversationanalysisclient_class]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html#azure.ai.language.conversations.ConversationAnalysisClient
[azure_core_exceptions]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_language_portal]: https://language.cognitive.azure.com/home
[cognitive_authentication_aad]: https://learn.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential


