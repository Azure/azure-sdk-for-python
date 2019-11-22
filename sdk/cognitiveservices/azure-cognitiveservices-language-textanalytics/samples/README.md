---
topic: sample
languages:
  - python
products:
  - azure
  - azure-cognitiveservices-language-textanalytics
---

# Samples for Azure Text Analytics client library for Python

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations 
with Text Analytics and require Python 3.5 or later. 


* Authenticate the client with a Cognitive Services/Text Analytics subscription key or a token credential from azure.identity
    * [sample_authentication.py](TODO)

* Detect language
    * In a batch of documents: [sample_detect_language.py](TODO) ([async version](TODO))
    * In a single string of text: [sample_single_detect_language.py](TODO) ([async version](TODO))

* Recognize entities
    * In a batch of documents: [sample_recognize_entities.py](TODO) ([async version](TODO))
    * In a single string of text:[sample_single_recognize_entities.py](TODO) ([async version](TODO))

* Recognize linked entities
    * In a batch of documents: [sample_recognize_linked_entities.py](TODO) ([async version](TODO))
    * In a single string of text:[sample_single_recognize_linked_entities.py](TODO) ([async version](TODO))

* Recognize personally identifiable information
    * In a batch of documents: [sample_recognize_pii_entities.py](TODO) ([async version](TODO))
    * In a single string of text:[sample_single_recognize_pii_entities.py](TODO) ([async version](TODO))

* Extract key phrases
   * In a batch of documents: [sample_extract_key_phrases.py](TODO) ([async version](TODO))
   * In a single string of text: [sample_single_extract_key_phrases.py](TODO) ([async version](TODO))

* Analyze sentiment in a sentence
    * In a batch of documents: [sample_analyze_sentiment.py](TODO) ([async version](TODO))
    * In a single string of text: [sample_single_analyze_sentiment.py](TODO) ([async version](TODO))

## Prerequisites
* Python 2.7, or 3.5 or later is required to use this package (3.5 or later if using asyncio)
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Azure Text Analytics account](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=singleservice%2Cwindows) to run these samples.

## Setup

1. Install the Azure Text Analytics client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-cognitiveservices-language-textanalytics --pre
```

2. Clone or download this sample repository
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python sample_detect_language.py`

## Next steps

Check out the [API reference documentation](TODO) to learn more about
what you can do with the Azure Text Analytics client library.
