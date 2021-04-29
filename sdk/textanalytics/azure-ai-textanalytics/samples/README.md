---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-cognitive-services
  - azure-text-analytics
urlFragment: textanalytics-samples
---

# Samples for Azure Text Analytics client library for Python

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples require Python 3.5 or later.

You can authenticate your client with a Cognitive Services/Text Analytics API key or through Azure Active Directory with a token credential from [azure-identity][azure_identity]:
* See [sample_authentication.py][sample_authentication] and [sample_authentication_async.py][sample_authentication_async] for how to authenticate in the above cases.

These sample programs show common scenarios for the Text Analytics client's offerings.

|**File Name**|**Description**|
|----------------|-------------|
|[sample_detect_language.py][detect_language] and [sample_detect_language_async.py][detect_language_async]|Detect language in documents|
|[sample_recognize_entities.py][recognize_entities] and [sample_recognize_entities_async.py][recognize_entities_async]|Recognize named entities in documents|
|[sample_recognize_linked_entities.py][recognize_linked_entities] and [sample_recognize_linked_entities_async.py][recognize_linked_entities_async]|Recognize linked entities in documents|
|[sample_recognize_pii_entities.py][recognize_pii_entities] and [sample_recognize_pii_entities_async.py][recognize_pii_entities_async]|Recognize personally identifiable information in documents|
|[sample_extract_key_phrases.py][extract_key_phrases] and [sample_extract_key_phrases_async.py][extract_key_phrases_async]|Extract key phrases from documents|
|[sample_analyze_sentiment.py][analyze_sentiment] and [sample_analyze_sentiment_async.py][analyze_sentiment_async]|Analyze the sentiment of documents|
|[sample_alternative_document_input.py][sample_alternative_document_input] and [sample_alternative_document_input_async.py][sample_alternative_document_input_async]|Pass documents to an endpoint using dicts|
|[sample_analyze_healthcare_entities.py][analyze_healthcare_entities_sample] and [sample_analyze_healthcare_entities_async.py][analyze_healthcare_entities_sample_async]|Analyze healthcare entities|
|[sample_analyze_batch_actions.py][analyze_sample] and [sample_analyze_batch_actions_async.py][analyze_sample_async]|Batch multiple analyses together in a single request|

## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription][azure_subscription] and an
[Azure Text Analytics account][azure_text_analytics_account] to run these samples.

## Setup

1. Install the Azure Text Analytics client library for Python with [pip][pip]:

```bash
pip install azure-ai-textanalytics --pre
```
For more information about how the versioning story of the SDK corresponds to the versioning story of the service's API, see [here][versioning_story_readme].

* If authenticating with Azure Active Directory, make sure you have [azure-identity][azure_identity_pip] installed:
  ```bash
  pip install azure-identity
  ```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_detect_language.py`

## Next steps

Check out the [API reference documentation][api_reference_documentation] to learn more about
what you can do with the Azure Text Analytics client library.

|**Advanced Sample File Name**|**Description**|
|----------------|-------------|
|[sample_analyze_sentiment_with_opinion_mining.py][sample_analyze_sentiment_with_opinion_mining] and [sample_analyze_sentiment_with_opinion_mining_async.py][sample_analyze_sentiment_with_opinion_mining_async]|Analyze sentiment in documents with granular analysis into individual opinions present in a sentence. Only available with API version v3.1-preview and up.|
|[sample_get_detailed_diagnostics_information.py][get_detailed_diagnostics_information] and [sample_get_detailed_diagnostics_information_async.py][get_detailed_diagnostics_information_async]|Get the request batch statistics, model version, and raw response in JSON format through a callback|

[versioning_story_readme]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics#install-the-package
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py
[detect_language]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_language.py
[detect_language_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py
[recognize_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py
[recognize_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py
[recognize_linked_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py
[recognize_linked_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py
[recognize_pii_entities]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py
[recognize_pii_entities_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py
[extract_key_phrases]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py
[extract_key_phrases_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py
[analyze_sentiment]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py
[analyze_sentiment_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py
[get_detailed_diagnostics_information]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_get_detailed_diagnostics_information.py
[get_detailed_diagnostics_information_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_get_detailed_diagnostics_information_async.py
[sample_alternative_document_input]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_alternative_document_input.py
[sample_alternative_document_input_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_alternative_document_input_async.py
[sample_analyze_sentiment_with_opinion_mining]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment_with_opinion_mining.py
[sample_analyze_sentiment_with_opinion_mining_async]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_with_opinion_mining_async.py
[analyze_healthcare_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_healthcare_entities.py
[analyze_healthcare_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_healthcare_entities_async.py
[analyze_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_batch_actions.py
[analyze_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_batch_actions_async.py
[pip]: https://pypi.org/project/pip/
[azure_subscription]: https://azure.microsoft.com/free/
[azure_text_analytics_account]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows
[azure_identity_pip]: https://pypi.org/project/azure-identity/
[api_reference_documentation]: https://aka.ms/azsdk-python-textanalytics-ref-docs