[![Build Status](https://dev.azure.com/azure-sdk/public/_apis/build/status/azure-sdk-for-python.client?branchName=main)](https://dev.azure.com/azure-sdk/public/_build/latest?definitionId=46?branchName=main)

# Azure Conversational Language Understanding client library for Python
Conversational Language Understanding - aka **CLU** for short - is a cloud-based conversational AI service which provides many language understanding capabilities like:
- Conversation App: It's used in extracting intents and entities in conversations
- Workflow app: Acts like an orchestrator to select the best candidate to analyze conversations to get best response from apps like Qna and Conversation App
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

> Note: This version of the client library defaults to the 2025-11-15-preview version of the service

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

The following examples show common scenarios using the `client` [created above](#create-conversationanalysisclient).

### Analyze Text with a Conversation App
If you would like to extract custom intents and entities from a user utterance, you can call the `client.analyze_conversation()` method with your conversation's project name as follows:
<!-- SNIPPET:sample_conversation_prediction.conversation_prediction -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationLanguageUnderstandingInput,
    ConversationAnalysisInput,
    TextConversationItem,
    ConversationActionContent,
    StringIndexType,
    ConversationActionResult,
    ConversationPrediction,
    DateTimeResolution,
)


def sample_conversation_prediction():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    credential = DefaultAzureCredential()
    client = ConversationAnalysisClient(endpoint, credential=credential)

    # build request
    data = ConversationLanguageUnderstandingInput(
        conversation_input=ConversationAnalysisInput(
            conversation_item=TextConversationItem(
                id="1",
                participant_id="participant1",
                text="Send an email to Carol about tomorrow's demo",
            )
        ),
        action_content=ConversationActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
        ),
    )

    # call sync API
    response = client.analyze_conversation(data)

    if isinstance(response, ConversationActionResult):
        pred = response.result.prediction
        if isinstance(pred, ConversationPrediction):
            # top intent
            print(f"Top intent: {pred.top_intent}\n")

            # intents
            print("Intents:")
            for intent in pred.intents or []:
                print(f"  Category: {intent.category}")
                print(f"  Confidence: {intent.confidence}")
                print()

            # entities
            print("Entities:")
            for entity in pred.entities or []:
                print(f"  Category: {entity.category}")
                print(f"  Text: {entity.text}")
                print(f"  Offset: {entity.offset}")
                print(f"  Length: {entity.length}")
                print(f"  Confidence: {entity.confidence}")

                for res in entity.resolutions or []:
                    if isinstance(res, DateTimeResolution):
                        print("  DateTime Resolution:")
                        print(f"    Sub Kind: {res.date_time_sub_kind}")
                        print(f"    Timex: {res.timex}")
                        print(f"    Value: {res.value}")
                print()
    else:
        print("Unexpected result type from analyze_conversation.")
```

<!-- END SNIPPET -->


### Analyze Text with an Orchestration App

If you would like to pass the user utterance to your orchestrator (worflow) app, you can call the `client.analyze_conversation()` method with your orchestration's project name. The orchestrator project simply orchestrates the submitted user utterance between your language apps (Luis, Conversation, and Question Answering) to get the best response according to the user intent. See the next example:

<!-- SNIPPET:sample_orchestration_prediction.orchestration_prediction -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    ConversationActionContent,
    ConversationAnalysisInput,
    TextConversationItem,
    StringIndexType,
    ConversationLanguageUnderstandingInput,
    OrchestrationPrediction,
    QuestionAnsweringTargetIntentResult,
    ConversationActionResult,
)


def sample_orchestration_prediction():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    project_name = os.environ["AZURE_CONVERSATIONS_PROJECT_NAME"]
    deployment_name = os.environ["AZURE_CONVERSATIONS_DEPLOYMENT_NAME"]

    credential = DefaultAzureCredential()
    client = ConversationAnalysisClient(endpoint, credential=credential)

    # Build request using strongly-typed models
    data = ConversationLanguageUnderstandingInput(
        conversation_input=ConversationAnalysisInput(
            conversation_item=TextConversationItem(
                id="1",
                participant_id="participant1",
                text="How are you?",
            )
        ),
        action_content=ConversationActionContent(
            project_name=project_name,
            deployment_name=deployment_name,
            string_index_type=StringIndexType.UTF16_CODE_UNIT,
        ),
    )

    # Call sync API
    response = client.analyze_conversation(data)

    # Narrow to expected result types
    if isinstance(response, ConversationActionResult):
        pred = response.result.prediction
        if isinstance(pred, OrchestrationPrediction):
            # Top intent name is the routed project name
            top_intent = pred.top_intent
            if not top_intent:
                print("No top intent was returned by orchestration.")
                return

            print(f"Top intent (responding project): {top_intent}")

            # Look up the routed target result
            target_intent_result = pred.intents.get(top_intent)
            if not isinstance(target_intent_result, QuestionAnsweringTargetIntentResult):
                print("Top intent did not route to a Question Answering result.")
                return

            qa = target_intent_result.result
            if qa is not None and qa.answers is not None:
                for ans in qa.answers:
                    print(ans.answer or "")
        else:
            print("Prediction was not an OrchestrationPrediction.")
    else:
        print("Unexpected result type from analyze_conversation.")
```

<!-- END SNIPPET -->

### Conversational Summarization

You can use this sample if you need to summarize a conversation in the form of an issue, and final resolution. For example, a dialog from tech support:

<!-- SNIPPET:sample_conversation_summarization.conversation_summarization -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations import ConversationAnalysisClient
from azure.ai.language.conversations.models import (
    TextConversationItem,
    TextConversation,
    ParticipantRole,
    MultiLanguageConversationInput,
    SummarizationOperationAction,
    ConversationSummarizationActionContent,
    SummaryAspect,
    AnalyzeConversationOperationInput,
    SummarizationOperationResult,
    ConversationError,
)


def sample_conversation_summarization():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    credential = DefaultAzureCredential()

    # Build conversation input
    conversation_items = [
        TextConversationItem(
            id="1", participant_id="Agent_1", text="Hello, how can I help you?", role=ParticipantRole.AGENT
        ),
        TextConversationItem(
            id="2",
            participant_id="Customer_1",
            text="How to upgrade Office? I am getting error messages the whole day.",
            role=ParticipantRole.CUSTOMER,
        ),
        TextConversationItem(
            id="3",
            participant_id="Agent_1",
            text="Press the upgrade button please. Then sign in and follow the instructions.",
            role=ParticipantRole.AGENT,
        ),
    ]

    conversation_input = MultiLanguageConversationInput(
        conversations=[TextConversation(id="1", language="en", conversation_items=conversation_items)]
    )

    # Build the operation input and inline actions
    operation_input = AnalyzeConversationOperationInput(
        conversation_input=conversation_input,
        actions=[
            SummarizationOperationAction(
                name="Issue task",
                action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.ISSUE]),
            ),
            SummarizationOperationAction(
                name="Resolution task",
                action_content=ConversationSummarizationActionContent(summary_aspects=[SummaryAspect.RESOLUTION]),
            ),
        ],
    )

    client = ConversationAnalysisClient(endpoint, credential=credential)

    poller = client.begin_analyze_conversation_job(body=operation_input)

    # Operation ID
    op_id = poller.details.get("operation_id")
    if op_id:
        print(f"Operation ID: {op_id}")

    # Wait for result
    paged_actions = poller.result()

    # Final-state metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    print(f"Created: {d.get('created_date_time')}")
    print(f"Last Updated: {d.get('last_updated_date_time')}")
    if d.get("expiration_date_time"):
        print(f"Expires: {d.get('expiration_date_time')}")
    if d.get("display_name"):
        print(f"Display Name: {d.get('display_name')}")

    # Iterate results
    for actions_page in paged_actions: # pylint: disable=too-many-nested-blocks
        print(
            f"Completed: {actions_page.completed}, "
            f"In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, "
            f"Total: {actions_page.total}"
        )

        for action_result in actions_page.task_results or []:
            if isinstance(action_result, SummarizationOperationResult):
                for conversation in action_result.results.conversations or []:
                    print(f"  Conversation ID: {conversation.id}")
                    print("  Summaries:")
                    for summary in conversation.summaries or []:
                        print(f"    Aspect: {summary.aspect}")
                        print(f"    Text: {summary.text}")
                    if conversation.warnings:
                        print("  Warnings:")
                        for warning in conversation.warnings:
                            print(f"    Code: {warning.code}, Message: {warning.message}")
            else:
                print("  [No supported results to display for this action type]")

    # Errors
    if d.get("errors"):
        print("\nErrors:")
        for error in d["errors"]:
            if isinstance(error, ConversationError):
                print(f"  Code: {error.code} - {error.message}")
```

<!-- END SNIPPET -->

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


