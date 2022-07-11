---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
urlFragment: conversationslanguageunderstanding-samples
---

# Samples for Azure Conversational Language Understanding client library for Python

These code samples show common scenario operations with the Azure Conversational Language Understanding client library.

You can authenticate your client with a Conversational Language Understanding API key:

- See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Conversational Language Understanding client's offerings.

| **File Name**| **Description**|
|-|-|
|[sample_analyze_conversation_app.py][sample_analyze_conversation_app] and [sample_analyze_conversation_app_async.py][sample_analyze_conversation_app_async] | Analyze intents and entities in your utterance using a conversation project. |
| [sample_analyze_orchestration_app_conv_response.py][sample_analyze_orchestration_app_conv_response] and [sample_analyze_orchestration_app_conv_response_async.py][sample_analyze_orchestration_app_conv_response_async]| Analyze user utterance using an orchestration project, which selects the best candidate from one of your different apps to analyze user query (ex: Qna, Conversation, and Luis). In this case, it uses a conversation project. |
| [sample_analyze_orchestration_app_luis_response.py][sample_analyze_orchestration_app_luis_response] and [sample_analyze_orchestration_app_luis_response_async.py][sample_analyze_orchestration_app_luis_response_async]| Analyze user utterance using an orchestration project, which selects the best candidate from one of your different apps to analyze user query (ex: Qna, Conversation, and Luis). In this case, it uses a Luis project. |
| [sample_analyze_orchestration_app_qna_response.py][sample_analyze_orchestration_app_qna_response] and [sample_analyze_orchestration_app_qna_response_async.py][sample_analyze_orchestration_app_qna_response_async]| Analyze user utterance using an orchestration project, which selects the best candidate from one of your different apps to analyze user query (ex: Qna, Conversation, and Luis). In this case, it uses a Qna project. |
| [sample_conv_summarization.py][sample_conv_summarization] and [sample_conv_summarization_async.py][sample_conv_summarization_async]| Summarize conversation in the form of issues and resolutions (ex: tech support conversation) |
| [sample_conv_pii_transcript_input.py][sample_conv_pii_transcript_input] and [sample_conv_pii_transcript_input_async.py][sample_conv_pii_transcript_input_async]| Extract and redact personally-identifiable info from/in conversations |


## Prerequisites

- Python 3.6 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and an
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



## Next Steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Conversational Language Understanding client library.

[azure_subscription]: https://azure.microsoft.com/free/
[azure_clu_account]: https://language.azure.com/clu/projects
[pip]: https://pypi.org/project/pip/

[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_authentication_async.py

[sample_analyze_conversation_app]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_conversation_app.py
[sample_analyze_conversation_app_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_conversation_app_async.py

[sample_analyze_orchestration_app_conv_response]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_orchestration_app_conv_response.py
[sample_analyze_orchestration_app_conv_response_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_orchestration_app_conv_response_async.py

[sample_analyze_orchestration_app_luis_response]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_orchestration_app_luis_response.py
[sample_analyze_orchestration_app_luis_response_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_orchestration_app_luis_response_async.py

[sample_analyze_orchestration_app_qna_response]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_analyze_orchestration_app_qna_response.py
[sample_analyze_orchestration_app_qna_response_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_analyze_orchestration_app_qna_response_async.py

[sample_conv_summarization]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conv_summarization.py
[sample_conv_summarization_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conv_summarization_async.py

[sample_conv_pii_transcript_input]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conv_pii_transcript_input.py
[sample_conv_pii_transcript_input_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conv_pii_transcript_input_async.py

[api_reference_documentation]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html
[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations#install-the-package
