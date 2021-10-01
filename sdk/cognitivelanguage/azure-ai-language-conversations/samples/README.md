---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-ai-language-conversations
urlFragment: conversationslanhguageunderstanding-samples
---

# Samples for Azure Conversational Language Understanding client library for Python

These code samples show common scenario operations with the Azure Conversational Language Understanding client library.
The async versions of the samples require Python 3.6 or later.

You can authenticate your client with a Conversational Language Understanding API key or through Azure Active Directory with a token credential from [azure-identity][azure_identity]:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Conversational Language Understanding client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_analyze_conversation_app.py][sample_analyze_conversation_app] and [sample_analyze_conversation_app_async.py][sample_analyze_conversation_app_async]|Analyze intents and entities in your utterance using a deepstack (conversation) project|
|[sample_analyze_workflow_app.py][sample_analyze_workflow_app] and [sample_analyze_workflow_app_async.py][sample_analyze_workflow_app_async]|Analyze user utterance using an orchestrator (workflow) project, which uses the best candidate from one of your different apps to analyze user query (ex: Qna, DeepStack, and Luis)|
|


## Prerequisites
* Python 2.7, or 3.6 or later is required to use this package (3.6 or later if using asyncio)
* You must have an [Azure subscription][azure_subscription] and an
[Azure CLU account][azure_clu_account] to run these samples.

## Setup

1. Install the Azure Conversational Language Understanding client library for Python with [pip][pip]:

```bash
pip install azure-ai-language-conversations --pre
```
For more information about how the versioning of the SDK corresponds to the versioning of the service's API, see [here][versioning_story_readme].

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_analyze_conversation_app.py`

## Next steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Conversational Language Understanding client library.

|**Advanced Sample File Name**|**Description**|
|----------------|-------------|
|[sample_analyze_workflow_app_with_parms.py][sample_analyze_workflow_app_with_parms] and [sample_analyze_workflow_app_with_parms_async.py][sample_analyze_workflow_app_with_parms_async]|Same as workflow sample, but with ability to customize call with parameters|
|[sample_analyze_workflow_app_direct.py][sample_analyze_workflow_app_direct] and [sample_analyze_workflow_app_direct_async.py][sample_analyze_workflow_app_direct_async]|Same as workflow app, but with ability to target a specific app within your orchestrator project|
|




[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[azure_subscription]: https://azure.microsoft.com/free/
[azure_clu_account]: https://language.azure.com/clu/projects
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[pip]: https://pypi.org/project/pip/


[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_authentication_async.py

[sample_analyze_conversation_app]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_conversation_app.py
[sample_analyze_conversation_app_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_conversation_app_async.py

[sample_analyze_workflow_app]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_workflow_app.py
[sample_analyze_workflow_app_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_workflow_app_async.py

[sample_analyze_workflow_app_with_parms]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_workflow_app_with_parms.py
[sample_analyze_workflow_app_with_parms_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_workflow_app_with_parms_async.py

[sample_analyze_workflow_app_direct]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_sample_analyze_workflow_app_direct.py
[sample_analyze_workflow_app_direct_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_sample_analyze_workflow_app_direct_async.py


[api_reference_documentation]: https://language.azure.com/clu/projects

[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations#install-the-package