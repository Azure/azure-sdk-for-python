# Azure Text Analytics client library for Python
Text Analytics is a cloud-based service that provides advanced natural language processing over raw text, and includes six main functions:

* Sentiment Analysis
* Named Entity Recognition
* Personally Identifiable Information (PII) Entity Recognition
* Linked Entity Recognition
* Language Detection
* Key Phrase Extraction

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics) | [Package (PyPI)](https://pypi.org/project/azure-ai-textanalytics/) | [API reference documentation](https://aka.ms/azsdk-python-textanalytics-ref-docs) | [Product documentation](https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples)

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and a
[Cognitive Services or Text Analytics resource](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows) to use this package.

### Install the package
Install the Azure Text Analytics client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-ai-textanalytics --pre
```

### Create a Cognitive Services or Text Analytics resource
Text Analytics supports both [multi-service and single-service access](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows). 
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Text Analytics access only, create a Text Analytics resource.

You can create either resource using the
[Azure Portal](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#create-a-new-azure-cognitive-services-resource)
or [Azure CLI](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows).
Below is an example of how you can create a Text Analytics resource using the CLI:

```bash
# Create a new resource group to hold the text analytics resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2
```

```bash
# Create text analytics
az cognitiveservices account create \
    --name text-analytics-resource \
    --resource-group my-resource-group \
    --kind TextAnalytics \
    --sku F0 \
    --location westus2 \
    --yes
```

### Authenticate the client
Interaction with this service begins with an instance of a [client](#Client). 
To create a client object, you will need the cognitive services or text analytics `endpoint` to 
your resource and a `credential` that allows you access:

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics = TextAnalyticsClient(endpoint="https://westus2.api.cognitive.microsoft.com/", credential=credential)
```

Note that if you create a [custom subdomain](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains) 
name for your resource the endpoint may look different than in the above code snippet. 
For example, `https://<my-custom-subdomain>.cognitiveservices.azure.com/`.

#### Looking up the endpoint
You can find the endpoint for your text analytics resource using the 
[Azure Portal](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource)
or [Azure CLI](https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show):

```bash
# Get the endpoint for the text analytics resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "endpoint"
```

#### Types of credentials
The `credential` parameter may be provided as the subscription key to your resource or as a token from Azure Active Directory.
See the full details regarding [authentication](https://docs.microsoft.com/azure/cognitive-services/authentication) of 
cognitive services.

1. To use a [subscription key](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource), 
   provide the key as a string. This can be found in the Azure Portal under the "Quickstart" 
   section or by running the following Azure CLI command:

    ```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```
    
    Use the key as the credential parameter to authenticate the client:
    ```python
    from azure.ai.textanalytics import TextAnalyticsClient
    text = TextAnalyticsClient(endpoint="https://westus2.api.cognitive.microsoft.com/", credential="<subscription_key>")
    ```

2. To use an [Azure Active Directory (AAD) token credential](https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory),
   provide an instance of the desired credential type obtained from the
   [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials) library.
   Note that regional endpoints do not support AAD authentication. Create a [custom subdomain](https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain) 
   name for your resource in order to use this type of authentication.

   Authentication with AAD requires some initial setup:
   * [Install azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#install-the-package)
   * [Register a new AAD application](https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal)
   * [Grant access](https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal) to Text Analytics by assigning the `"Cognitive Services User"` role to your service principal.
   
   After setup, you can choose which type of [credential](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials) from azure.identity to use. 
   As an example, [DefaultAzureCredential](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential)
   can be used to authenticate the client:

   Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables: 
   AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

   Use the returned token credential to authenticate the client:
    ```python
    from azure.identity import DefaultAzureCredential
    from azure.ai.textanalytics import TextAnalyticsClient
    token_credential = DefaultAzureCredential()

    text_analytics_client = TextAnalyticsClient(
        endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
        credential=token_credential
    )
    ```

## Key concepts

#### Client
The Text Analytics client library provides a [TextAnalyticsClient](https://aka.ms/azsdk-python-textanalytics-textanalyticsclient) to do analysis on batches of documents.
It provides both synchronous and asynchronous operations to access a specific use of Text Analytics, such as language detection or key phrase extraction. 

#### Single text operations
The Text Analytics client library also provides module-level operations which can be performed on a single string
rather than a batch of documents. Each synchronous and asynchronous batching operation has a singular counterpart. 
The endpoint and credential are passed in with the desired text and other optional parameters, e.g. 
[single_analyze_sentiment()](https://aka.ms/azsdk-python-textanalytics-singleanalyzesentiment):

```python
from azure.ai.textanalytics import single_analyze_sentiment

text = "I did not like the restaurant. The food was too spicy."
result = single_analyze_sentiment(endpoint=endpoint, credential=credential, input_text=text, language="en")
```

#### Input
A **document** is a single unit to be analyzed by the predictive models in the Text Analytics service.
For the single text operations, the input document is simply passed as a string, e.g. `"hello world"`. 
For the batched operations, the input is passed as a list of documents. 

Documents can be passed as a list of strings, e.g.
```python
docs = ["I hated the movie. It was so slow!", "The movie made it into my top ten favorites.", "What a great movie!"]
```

or, if you wish to pass in a per-item document `id` or `language`/`country_hint`, they can be passed as a 
list of [DetectLanguageInput](https://aka.ms/azsdk-python-textanalytics-detectlanguageinput) or 
[TextDocumentInput](https://aka.ms/azsdk-python-textanalytics-textdocumentinput),
or a dict-like representation of the object:

```python
documents = [
    {"id": "1", "language": "en", "text": "I hated the movie. It was so slow!"}, 
    {"id": "2", "language": "en", "text": "The movie made it into my top ten favorites."}, 
    {"id": "3", "language": "en", "text": "What a great movie!"}
]
```

#### Operation Result
An operation result, such as [AnalyzeSentimentResult](https://aka.ms/azsdk-python-textanalytics-analyzesentimentresult), 
is the result of a Text Analytics operation and contains a prediction or predictions about a document input.
With a batching operation, a list is returned containing a collection of operation results and any document errors. 
These results/errors will be index-matched with the order of the provided documents.


## Examples
The following section provides several code snippets covering some of the most common Text Analytics tasks, including:

* [Analyze Sentiment](#analyze-sentient "Analyze sentiment")
* [Recognize Entities](#recognize-entities "Recognize entities")
* [Recognize PII Entities](#recognize-pii-entities "Recognize pii entities")
* [Recognize Linked Entities](#recognize-linked-entities "Recognize linked entities")
* [Extract Key Phrases](#extract-key-phrases "Extract key phrases")
* [Detect Languages](#detect-languages "Detect languages")

### Analyze sentiment
Analyze sentiment in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "I did not like the restaurant. The food was too spicy.",
    "The restaurant was decorated beautifully. The atmosphere was unlike any other restaurant I've been to.",
    "The food was yummy. :)"
]

result = text_analytics_client.analyze_sentiment(documents, language="en")

for doc in result:
    print("Overall sentiment: {}".format(doc.sentiment))
    print("Scores: positive={0:.3f}; neutral={0:.3f}; negative={0:.3f} \n".format(
        doc.document_scores.positive,
        doc.document_scores.neutral,
        doc.document_scores.negative,
    ))
```

### Recognize entities
Recognize entities in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen.",
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "Jeff bought three dozen eggs because there was a 50% discount."
]

result = text_analytics_client.recognize_entities(documents, language="en")

for doc in result:
    for entity in doc.entities:
        print("Entity: \t", entity.text, "\tType: \t", entity.type,
              "\tConfidence Score: \t", entity.score)
```

### Recognize PII entities
Recognize PII entities in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "The employee's SSN is 555-55-5555.",
    "The employee's phone number is 555-55-5555."
]

result = text_analytics_client.recognize_pii_entities(documents, language="en")

for doc in result:
    for entity in doc.entities:
        print("Entity: \t", entity.text, "\tType: \t", entity.type,
              "\tConfidence Score: \t", entity.score)
```

### Recognize linked entities
Recognize linked entities in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen.",
    "Easter Island, a Chilean territory, is a remote volcanic island in Polynesia."
]

result = text_analytics_client.recognize_linked_entities(documents, language="en")

for doc in result:
    for entity in doc.entities:
        print("Entity: {}".format(entity.name))
        print("Url: {}".format(entity.url))
        print("Data Source: {}".format(entity.data_source))
        for match in entity.matches:
            print("Score: {0:.3f}".format(match.score))
            print("Offset: {}".format(match.offset))
            print("Length: {}\n".format(match.length))
```

### Extract key phrases
Extract key phrases in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "I need to take my cat to the veterinarian.",
    "I will travel to South America in the summer."
]

result = text_analytics_client.extract_key_phrases(documents, language="en")

for doc in result:
    print(doc.key_phrases)
```

### Detect languages
Detect language in a batch of documents.

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "This is written in English.",
    "Il documento scritto in italiano.",
    "Dies ist in englischer Sprache verfasst."
]

result = text_analytics_client.detect_languages(documents)

for doc in result:
    print("Language detected: {}".format(doc.detected_languages[0].name))
    print("ISO6391 name: {}".format(doc.detected_languages[0].iso6391_name))
    print("Confidence score: {}\n".format(doc.detected_languages[0].score))
```

## Optional Configuration

Optional keyword arguments that can be passed in at the client and per-operation level. 

### Retry Policy configuration

Use the following keyword arguments when instantiating a client to configure the retry policy:

* __retry_total__ (int): Total number of retries to allow. Takes precedence over other counts.
Pass in `retry_total=0` if you do not want to retry on requests. Defaults to 10.
* __retry_connect__ (int): How many connection-related errors to retry on. Defaults to 3.
* __retry_read__ (int): How many times to retry on read errors. Defaults to 3.
* __retry_status__ (int): How many times to retry on bad status codes. Defaults to 3.

### Other client / per-operation configuration

Other optional configuration keyword arguments that can be specified on the client or per-operation.

**Client keyword arguments:**

* __connection_timeout__ (int): A single float in seconds for the connection timeout. Defaults to 300 seconds.
* __read_timeout__ (int): A single float in seconds for the read timeout. Defaults to 300 seconds.
* __transport__ (Any): User-provided transport to send the HTTP request.

**Per-operation keyword arguments:**

* __response_hook__ (callable): The given callback uses the raw response returned from the service.
Can also be passed in at the client.
* __request_id__ (str): Optional user specified identification of the request.
* __user_agent__ (str): Appends the custom value to the user-agent header to be sent with the request.
* __logging_enable__ (bool): Enables logging at the DEBUG level. Defaults to False. Can also be passed in at
the client level to enable it for all requests.
* __headers__ (dict): Pass in custom headers as key, value pairs. E.g. `headers={'CustomValue': value}`

## Troubleshooting
The Text Analytics client will raise exceptions defined in [Azure Core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md).

## Next steps

### More sample code

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations 
with Text Analytics and require Python 3.5 or later. 

Authenticate the client with a Cognitive Services/Text Analytics subscription key or a token credential from [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity):
* [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_authentication.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py))

In a batch of documents:
* Detect languages: [sample_detect_languages.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_languages.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_languages_async.py))
* Recognize entities: [sample_recognize_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py))
* Recognize linked entities: [sample_recognize_linked_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py))
* Recognize personally identifiable information: [sample_recognize_pii_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py))
* Extract key phrases: [sample_extract_key_phrases.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py))
* Analyze sentiment: [sample_analyze_sentiment.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py))

In a single string of text:
* Detect language: [sample_single_detect_language.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_detect_language.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_detect_language_async.py))
* Recognize entities: [sample_single_recognize_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_recognize_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_recognize_entities_async.py))
* Recognize linked entities: [sample_single_recognize_linked_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_recognize_linked_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_recognize_linked_entities_async.py))
* Recognize personally identifiable information: [sample_single_recognize_pii_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_recognize_pii_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_recognize_pii_entities_async.py))
* Extract key phrases: [sample_single_extract_key_phrases.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_extract_key_phrases.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_extract_key_phrases_async.py))
* Analyze sentiment: [sample_single_analyze_sentiment.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_analyze_sentiment.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_analyze_sentiment_async.py))


### Additional documentation
For more extensive documentation on Azure Cognitive Services Text Analytics, see the [Text Analytics documentation](https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview) on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
