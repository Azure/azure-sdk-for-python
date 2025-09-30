---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - language-service
urlFragment: conversationslanguageunderstanding-samples
---

# Samples for Azure Conversational Language Understanding client library for Python

These code samples show common scenario operations with the Azure Conversational Language Understanding client library.

You can authenticate your client with a Conversational Language Understanding API key:

- See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Conversational Language Understanding client's offerings.

| **File Name** | **Description** |
|-|-|
| [sample_conversation_prediction.py][sample_conversation_prediction] and [sample_conversation_prediction_async.py][sample_conversation_prediction_async] | Analyze intents and entities in an utterance using a conversation project. |
| [sample_orchestration_prediction.py][sample_orchestration_prediction] and [sample_orchestration_prediction_async.py][sample_orchestration_prediction_async] | Analyze an utterance with an orchestration project that routes to the best skill; this sample uses a Qna project. |
| [sample_conversation_prediction_with_language.py][sample_conversation_prediction_with_language] and [sample_conversation_prediction_with_language_async.py][sample_conversation_prediction_with_language_async] | Analyze a conversation in a specified (non-default) language/locale. |
| [sample_conversation_prediction_with_options.py][sample_conversation_prediction_with_options] and [sample_conversation_prediction_with_options_async.py][sample_conversation_prediction_with_options_async] | Analyze a conversation using extra options (e.g., verbosity, logging). |
| [sample_conversation_multi_turn_prediction.py][sample_conversation_multi_turn_prediction] and [sample_conversation_multi_turn_prediction_async.py][sample_conversation_multi_turn_prediction_async] | Perform multi-turn analysis over a back-and-forth conversation. |
| [sample_conversation_summarization.py][sample_conversation_summarization] and [sample_conversation_summarization_async.py][sample_conversation_summarization_async] | Summarize a conversation into issues and resolutions (e.g., tech support). |
| [sample_conversation_pii.py][sample_conversation_pii] and [sample_conversation_pii_async.py][sample_conversation_pii_async] | Detect and redact PII in a conversation using default masking. |
| [sample_conversation_pii_with_character_mask_policy.py][sample_conversation_pii_with_character_mask_policy] and [sample_conversation_pii_with_character_mask_policy_async.py][sample_conversation_pii_with_character_mask_policy_async] | Detect PII and apply character-masking (e.g., replace with `*`). |
| [sample_conversation_pii_with_entity_mask_policy.py][sample_conversation_pii_with_entity_mask_policy] and [sample_conversation_pii_with_entity_mask_policy_async.py][sample_conversation_pii_with_entity_mask_policy_async] | Detect PII and mask by entity type (e.g., `<PHONE_NUMBER>`). |
| [sample_conversation_pii_with_no_mask_policy.py][sample_conversation_pii_with_no_mask_policy] and [sample_conversation_pii_with_no_mask_policy_async.py][sample_conversation_pii_with_no_mask_policy_async] | Detect PII without masking; return entities and spans only. |

## Prerequisites

- Python 3.7 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and an
  [Azure CLU account][azure_clu_account] to run these samples.

## Setup

1. Install the Azure Conversational Language Understanding client library for Python with [pip][pip]:

```bash
pip install azure-ai-language-conversations
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

[sample_conversation_prediction]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction.py
[sample_conversation_prediction_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_async.py

[sample_orchestration_prediction]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_orchestration_prediction.py
[sample_orchestration_prediction_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_orchestration_prediction_async.py

[sample_conversation_prediction_with_language]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction_with_language.py
[sample_conversation_prediction_with_language_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_with_language_async.py

[sample_conversation_prediction_with_options]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_prediction_with_options.py
[sample_conversation_prediction_with_options_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_prediction_with_options_async.py

[sample_conversation_multi_turn_prediction]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_multi_turn_prediction.py
[sample_conversation_multi_turn_prediction_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_multi_turn_prediction_async.py

[sample_conversation_summarization]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_summarization.py
[sample_conversation_summarization_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_summarization_async.py

[sample_conversation_pii]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii.py
[sample_conversation_pii_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_async.py

[sample_conversation_pii_with_character_mask_policy]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_character_mask_policy.py
[sample_conversation_pii_with_character_mask_policy_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_character_mask_policy_async.py

[sample_conversation_pii_with_entity_mask_policy]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_entity_mask_policy.py
[sample_conversation_pii_with_entity_mask_policy_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_entity_mask_policy_async.py

[sample_conversation_pii_with_no_mask_policy]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/sample_conversation_pii_with_no_mask_policy.py
[sample_conversation_pii_with_no_mask_policy_async]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations/samples/async/sample_conversation_pii_with_no_mask_policy_async.py

[api_reference_documentation]: https://azuresdkdocs.z19.web.core.windows.net/python/azure-ai-language-conversations/latest/azure.ai.language.conversations.html
[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-language-conversations#install-the-package
