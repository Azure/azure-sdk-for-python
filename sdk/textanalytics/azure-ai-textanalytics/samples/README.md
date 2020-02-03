---
topic: sample
languages:
  - python
products:
  - azure
  - azure-ai-textanalytics
---

# Samples for Azure Text Analytics client library for Python

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations 
with Text Analytics and require Python 3.5 or later. 

Authenticate the client with a Cognitive Services/Text Analytics subscription key or a token credential from [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity):
* [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py))

In a batch of documents:
* Detect language: [sample_detect_language.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_language.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py))
* Recognize entities: [sample_recognize_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py))
* Recognize linked entities: [sample_recognize_linked_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py))
* Recognize personally identifiable information: [sample_recognize_pii_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py))
* Extract key phrases: [sample_extract_key_phrases.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py))
* Analyze sentiment: [sample_analyze_sentiment.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py))

## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Text Analytics account](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows) to run these samples.

## Setup

1. Install the Azure Text Analytics client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-ai-textanalytics --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_detect_language.py`

## Next steps

Check out the [API reference documentation](https://westus.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-0-Preview-1/operations/Languages) to learn more about
what you can do with the Azure Text Analytics client library.
