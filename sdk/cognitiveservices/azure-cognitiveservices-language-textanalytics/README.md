# Azure Text Analytics client library for Python
Text Analytics is a cloud-based service that provides advanced natural language processing over raw text, and includes four main functions:

* Sentiment Analysis
* Named Entity Recognition
* Language Detection
* Key Phrase Extraction

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics) | [Package (PyPI)](https://pypi.org/project/azure-cognitiveservices-language-textanalytics/) | [API reference documentation](https://westus.dev.cognitive.microsoft.com/docs/services/TextAnalytics-v3-0-Preview-1/operations/Languages) | [Product documentation](https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview) | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples)

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription](https://azure.microsoft.com/free/) and an
[Cognitive Services or Text Analytics account](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows) to use this package.

### Install the package
Install the Azure Text Analytics client library for Python with [pip](https://pypi.org/project/pip/):

```bash
pip install azure-cognitiveservices-language-textanalytics --pre
```

### Create a Cognitive Services or Text Analytics resource
Text Analytics supports both [multi-service and single-service access](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows). Create a Cognitive Services resource if you plan
to access multiple cognitive services under a single endpoint/key. For Text Analytics access only, create a Text Analytics resource.

You can create either resource using the
[Azure Portal](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#create-a-new-azure-cognitive-services-resource)
or [Azure CLI](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows).
Below is an example of how you can create a Text Analytics resource using the CLI:

```
# Create a new resource group to hold the text analytics resource -
# if using an existing resource group, skip this step
az group create --name my-resource-group --location westus2

# Create text analytics
az cognitiveservices account create \
    --name text-analytics-resource \
    --resource-group my-resource-group \
    --kind TextAnalytics \
    --sku F0 \
    --location westus2 \
    --yes
```

### Create the client
The Azure Text Analytics client library for Python allows you to engage with the Text Analytics service to 
analyze sentiment, recognize entities, detect language, and extract key phrases from text.
Interaction with this service begins with an instance of a [client](#Client). 
To create a client object, you will need the cognitive services or text analytics endpoint to 
your resource and a credential that allows you access:

```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics = TextAnalyticsClient(endpoint="https://westus2.api.cognitive.microsoft.com/", credential=credential)
```

Note that if you create a [custom subdomain](https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains) 
for your resource the endpoint may look different than in the above code snippet. 
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
    from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
    service = TextAnalyticsClient(endpoint="https://westus2.api.cognitive.microsoft.com/", credential="<subscription_key>")
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
    from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
    token_credential = DefaultAzureCredential()

    text_analytics_client = TextAnalyticsClient(
        endpoint="https://<my-custom-subdomain>.cognitiveservices.azure.com/",
        credential=token_credential
    )
    ```

## Key concepts

The following are types of text analysis that the service offers:

1. [Sentiment Analysis](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-sentiment-analysis)
    
    Use sentiment analysis to find out what customers think of your brand or topic by analyzing raw text for clues about positive or negative sentiment.
    Scores closer to `1` indicate positive sentiment, while scores closer to `0` indicate negative sentiment.
    Sentiment analysis returns scores and labels at a document and sentence level.

2. [Named Entity Recognition](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-entity-linking)
    
    Use named entity recognition (NER) to identify different entities in text and categorize them into pre-defined classes, or types.
    Entity recognition in the client library provides three different methods depending on what you are interested in.
    * `recognize_entities()` can be used to identify and categorize entities in your text as people, places, organizations, date/time, quantities, percentages, currencies, and more.
    * `recognize_pii_entities()` can be used to recognize personally identifiable information such as SSNs and bank account numbers.
    * `recognize_linked_entities()` can be used to identify and disambiguate the identity of an entity found in text (For example, determining whether
    "Mars" is being used as the planet or as the Roman god of war). This process uses Wikipedia as the knowledge base to which recognized entities are linked.
    
    See a full list of [Named Entity Recognition Types](https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal).

3. [Language Detection](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-language-detection)
    
    Detect the language of the input text and report a single language code for every document submitted on the request. 
    The language code is paired with a score indicating the strength of the score.
    A wide range of languages, variants, dialects, and some regional/cultural languages are supported -
    see [supported languages](https://docs.microsoft.com/azure/cognitive-services/text-analytics/language-support#language-detection) for full details.

4. [Key Phrase Extraction](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-keyword-extraction)
    
    Extract key phrases to quickly identify the main points in text. 
    For example, for the input text "The food was delicious and there were wonderful staff", the main talking points returned: "food" and "wonderful staff".

See [Language and regional support](https://docs.microsoft.com/azure/cognitive-services/text-analytics/language-support) for what is currently available for each operation.


### Client
The Text Analytics client library provides a [TextAnalyticsClient](TODO) to do analysis on batches of documents.


A batch contains the text documents you wish to process, and may contain a per-item ID and language/country hint
if you choose. For example, a batch can simply be passed as a list of strings:
```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)
documents = ["I hated the movie. It was so slow!", "The movie made it into my top ten favorites.", "What a great movie!"]

result = text_analytics_client.analyze_sentiment(documents)
```
or as a list of [LanguageInput](TODO) or [MultiLanguageInput](TODO):
```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)
documents = [
    {"id": "1", "language": "en", "text": "I hated the movie. It was so slow!"}, 
    {"id": "2", "language": "en", "text": "The movie made it into my top ten favorites."}, 
    {"id": "3", "language": "en", "text": "What a great movie!"}
]
result = text_analytics_client.analyze_sentiment(documents)
```

The returned response will be index-matched with the order of the provided documents.


### Single text operations
The Text Analytics client library also provides module-level operations which can be performed on a single string
of text. 

These operations are an introduction to the client library and have simpler inputs and outputs than
that of the batched client operations. The endpoint and credential are passed in with the desired text and 
other optional parameters. 

```python
from azure.cognitiveservices.language.textanalytics import single_analyze_sentiment

text = "I did not like the restaurant. The food was too spicy."
result = single_analyze_sentiment(endpoint=endpoint, credential=credential, text=text, language="en")

print(result.sentiment)
```


## Examples
The following section provides several code snippets covering some of the most common Text Analytics tasks, including:

* [Analyze Sentiment](#analyze-sentient "Analyze sentiment")
* [Recognize Entities](#recognize-entities "Recognize entities")
* [Extract Key Phrases](#extract-key-phrases "Extract key phrases")
* [Detect Language](#detect-language "Detect language")

### Analyze sentiment
Analyze sentiment in a batch of documents.

```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "I did not like the restaurant. The food was too spicy.",
    "The restaurant was decorated beautifully. The atmosphere was unlike any other restaurant I've been to.",
    "The food was yummy. :)"
]

result = text_analytics_client.analyze_sentiment(documents, language="en")

for text in result:
    print(text.sentiment)
```

### Recognize entities
Recognize entities in a batch of documents.

```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen.",
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "Jeff bought three dozen eggs because there was a 50% discount."
]

result = text_analytics_client.recognize_entities(documents, language="en")

for text in result:
    print(text.entities)
```

### Extract key phrases
Extract key phrases in a batch of documents.

```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "I need to take my cat to the veterinarian.",
    "I will travel to South America in the summer."
]

result = text_analytics_client.extract_key_phrases(documents, language="en")

for text in result:
    print(text.key_phrases)
```

### Detect language
Detect language in a batch of documents.

```python
from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient

text_analytics_client = TextAnalyticsClient(endpoint, key)

documents = [
    "This is written in English.",
    "Este es un document escrito en Español.",
    "这是一个用中文写的文件"
]

result = text_analytics_client.detect_language(documents)

for text in result:
    print(text.detected_language.name)
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
* [sample_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_authentication.py)

In a batch of documents:
* Detect language: [sample_detect_language.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_detect_language.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_detect_language_async.py))
* Recognize entities: [sample_recognize_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_recognize_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_recognize_entities_async.py))
* Recognize linked entities: [sample_recognize_linked_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_recognize_linked_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py))
* Recognize personally identifiable information: [sample_recognize_pii_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_recognize_pii_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py))
* Extract key phrases: [sample_extract_key_phrases.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_extract_key_phrases.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py))
* Analyze sentiment: [sample_analyze_sentiment.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_analyze_sentiment.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py))

In a single string of text:
* Detect language: [sample_single_detect_language.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_detect_language.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_detect_language_async.py))
* Recognize entities: [sample_single_recognize_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_recognize_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_recognize_entities_async.py))
* Recognize linked entities: [sample_single_recognize_linked_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_recognize_linked_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_recognize_linked_entities_async.py))
* Recognize personally identifiable information: [sample_single_recognize_pii_entities.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_recognize_pii_entities.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_recognize_pii_entities_async.py))
* Extract key phrases: [sample_single_extract_key_phrases.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_extract_key_phrases.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_extract_key_phrases_async.py))
* Analyze sentiment: [sample_single_analyze_sentiment.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/sample_single_analyze_sentiment.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/cognitiveservices/azure-cognitiveservices-language-textanalytics/samples/async_samples/sample_single_analyze_sentiment_async.py))


### Additional documentation
For more extensive documentation on Azure Cognitive Services, see the [Azure Cognitive Services documentation](https://docs.microsoft.com/azure/cognitive-services/) on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
