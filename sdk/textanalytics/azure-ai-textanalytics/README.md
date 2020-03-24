# Azure Text Analytics client library for Python
Text Analytics is a cloud-based service that provides advanced natural language processing over raw text, and includes six main functions:

* Sentiment Analysis
* Named Entity Recognition
* Personally Identifiable Information (PII) Entity Recognition
* Linked Entity Recognition
* Language Detection
* Key Phrase Extraction

[Source code][source_code] | [Package (PyPI)][TA_pypi] | [API reference documentation][TA_ref_docs]| [Product documentation][TA_product_documentation] | [Samples][TA_samples]

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and a
[Cognitive Services or Text Analytics resource][TA_or_CS_resource] to use this package.

### Install the package
Install the Azure Text Analytics client library for Python with [pip][pip]:

```bash
pip install azure-ai-textanalytics --pre
```

### Create a Cognitive Services or Text Analytics resource
Text Analytics supports both [multi-service and single-service access][multi_and_single_service].
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Text Analytics access only, create a Text Analytics resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_TA_resource]

**Option 2:** [Azure CLI][azure_cli_create_TA_resource].
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
Interaction with this service begins with an instance of a [client](#client "ta-client").
To create a client object, you will need the cognitive services or text analytics `endpoint` to
your resource and a `credential` that allows you access:

```python
from azure.ai.textanalytics import TextAnalyticsClient

text_analytics_client  = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
```

Note that if you create a [custom subdomain][cognitive_custom_subdomain]
name for your resource the endpoint may look different than in the above code snippet.
For example, `https://<my-custom-subdomain>.cognitiveservices.azure.com/`.

#### Looking up the endpoint
You can find the endpoint for your text analytics resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the text analytics resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "endpoint"
```

#### Types of credentials
The `credential` parameter may be provided as a `TextAnalyticsApiKeyCredential` or as a token from Azure Active Directory.
See the full details regarding [authentication][cognitive_authentication] of
cognitive services.

1. To use an [API key][cognitive_authentication_api_key],
   pass the key as a string into an instance of `TextAnalyticsApiKeyCredential("<api_key>")`.
   The API key can be found in the Azure Portal or by running the following Azure CLI command:

    ```az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"```

    Use the key as the credential parameter to authenticate the client:
    ```python
    from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

    credential = TextAnalyticsApiKeyCredential("<api_key>")
    text = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
    ```

2. To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
   provide an instance of the desired credential type obtained from the
   [azure-identity][azure_identity_credentials] library.
   Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
   name for your resource in order to use this type of authentication.

   Authentication with AAD requires some initial setup:
   * [Install azure-identity][install_azure_identity]
   * [Register a new AAD application][register_aad_app]
   * [Grant access][grant_role_access] to Text Analytics by assigning the `"Cognitive Services User"` role to your service principal.

   After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
   As an example, [DefaultAzureCredential][default_azure_credential]
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

### Client
The Text Analytics client library provides a [TextAnalyticsClient][text_analytics_client] to do analysis on [batches of documents](#Examples "examples").
It provides both synchronous and asynchronous operations to access a specific use of Text Analytics, such as language detection or key phrase extraction.

### Input
A **document** is a single unit to be analyzed by the predictive models in the Text Analytics service.
The input for each operation is passed as a **list** of documents.

Each document can be passed as a string in the list, e.g.
```python
documents = ["I hated the movie. It was so slow!", "The movie made it into my top ten favorites.", "What a great movie!"]
```

or, if you wish to pass in a per-item document `id` or `language`/`country_hint`, they can be passed as a list of
[DetectLanguageInput][detect_language_input] or
[TextDocumentInput][text_document_input]
or a dict-like representation of the object:

```python
documents = [
    {"id": "1", "language": "en", "text": "I hated the movie. It was so slow!"},
    {"id": "2", "language": "en", "text": "The movie made it into my top ten favorites."},
    {"id": "3", "language": "en", "text": "What a great movie!"}
]
```

See [service limitations][service_limits] for the input, including document length limits, maximum batch size, and supported text encoding.

### Return Value
The return value for a single document can be a result or error object.
A heterogeneous list containing a collection of result and error objects is returned from each operation.
These results/errors are index-matched with the order of the provided documents.

A **result**, such as [AnalyzeSentimentResult][analyze_sentiment_result],
is the result of a Text Analytics operation and contains a prediction or predictions about a document input.

The **error** object, [DocumentError][document_error], indicates that the service had trouble processing the document and contains
the reason it was unsuccessful.

### Document Error Handling
You can filter for a result or error object in the list by using the `is_error` attribute. For a result object this is always `False` and for a
[DocumentError][document_error] this is `True`.

For example, to filter out all DocumentErrors you might use list comprehension:
```python
response = text_analytics_client.analyze_sentiment(documents)
successful_responses = [doc for doc in response if not doc.is_error]
```


## Examples
The following section provides several code snippets covering some of the most common Text Analytics tasks, including:

* [Analyze Sentiment](#analyze-sentiment "Analyze sentiment")
* [Recognize Entities](#recognize-entities "Recognize entities")
* [Recognize PII Entities](#recognize-pii-entities "Recognize pii entities")
* [Recognize Linked Entities](#recognize-linked-entities "Recognize linked entities")
* [Extract Key Phrases](#extract-key-phrases "Extract key phrases")
* [Detect Language](#detect-language "Detect language")

### Analyze sentiment
[analyze_sentiment][analyze_sentiment] looks at its input text and determines whether its sentiment is positive, negative, neutral or mixed. It's response includes per-sentence sentiment analysis and confidence scores.

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "I did not like the restaurant. The food was too spicy.",
    "The restaurant was decorated beautifully. The atmosphere was unlike any other restaurant I've been to.",
    "The food was yummy. :)"
]

response = text_analytics_client.analyze_sentiment(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    print("Overall sentiment: {}".format(doc.sentiment))
    print("Scores: positive={}; neutral={}; negative={} \n".format(
        doc.confidence_scores.positive,
        doc.confidence_scores.neutral,
        doc.confidence_scores.negative,
    ))
```

The returned response is a heterogeneous list of result and error objects: list[[AnalyzeSentimentResult][analyze_sentiment_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [sentiment analysis][sentiment_analysis].

### Recognize entities
[recognize_entities][recognize_entities] recognizes and categories entities in its input text as people, places, organizations, date/time, quantities, percentages, currencies, and more.

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen.",
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "Jeff bought three dozen eggs because there was a 50% discount."
]

response = text_analytics_client.recognize_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    for entity in doc.entities:
        print("Entity: \t", entity.text, "\tCategory: \t", entity.category,
              "\tConfidence Score: \t", entity.confidence_score)
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizeEntitiesResult][recognize_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [named entity recognition][named_entity_recognition]
and [supported types][named_entity_categories].

### Recognize PII entities
[recognize_pii_entities][recognize_pii_entities] recognizes and categorizes Personally Identifiable Information (PII) entities in its input text, such as
Social Security Numbers, bank account information, credit card numbers, and more.

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "The employee's SSN is 555-55-5555.",
    "The employee's phone number is 555-55-5555."
]

response = text_analytics_client.recognize_pii_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    for entity in doc.entities:
        print("Entity: \t", entity.text, "\tCategory: \t", entity.category,
              "\tConfidence Score: \t", entity.confidence_score)
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizePiiEntitiesResult][recognize_pii_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for [supported PII entity types][pii_entity_categories].

### Recognize linked entities
[recognize_linked_entities][recognize_linked_entities] recognizes and disambiguates the identity of each entity found in its input text (for example,
determining whether an occurrence of the word Mars refers to the planet, or to the
Roman god of war). Recognized entities are associated with URLs to a well-known knowledge base, like Wikipedia.

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen.",
    "Easter Island, a Chilean territory, is a remote volcanic island in Polynesia."
]

response = text_analytics_client.recognize_linked_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    for entity in doc.entities:
        print("Entity: {}".format(entity.name))
        print("URL: {}".format(entity.url))
        print("Data Source: {}".format(entity.data_source))
        for match in entity.matches:
            print("Confidence Score: {}".format(match.confidence_score))
            print("Entity as appears in request: {}".format(match.text))
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizeLinkedEntitiesResult][recognize_linked_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [entity linking][linked_entity_recognition]
and [supported types][linked_entities_categories].

### Extract key phrases
[extract_key_phrases][extract_key_phrases] determines the main talking points in its input text. For example, for the input text "The food was delicious and there were wonderful staff", the API returns: "food" and "wonderful staff".

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    "I need to take my cat to the veterinarian.",
    "I will travel to South America in the summer."
]

response = text_analytics_client.extract_key_phrases(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    print(doc.key_phrases)
```

The returned response is a heterogeneous list of result and error objects: list[[ExtractKeyPhrasesResult][extract_key_phrases_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [key phrase extraction][key_phrase_extraction].

### Detect language
[detect_language][detect_language] determines the language of its input text, including the confidence score of the predicted language.

```python
from azure.ai.textanalytics import TextAnalyticsClient, TextAnalyticsApiKeyCredential

text_analytics_client = TextAnalyticsClient(endpoint, TextAnalyticsApiKeyCredential(key))

documents = [
    "This is written in English.",
    "Il documento scritto in italiano.",
    "Dies ist in deutsche Sprache verfasst."
]

response = text_analytics_client.detect_language(documents)
result = [doc for doc in response if not doc.is_error]

for doc in result:
    print("Language detected: {}".format(doc.primary_language.name))
    print("ISO6391 name: {}".format(doc.primary_language.iso6391_name))
    print("Confidence score: {}\n".format(doc.primary_language.score))
```

The returned response is a heterogeneous list of result and error objects: list[[DetectLanguageResult][detect_language_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [language detection][language_detection]
and [language and regional support][language_and_regional_support].

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting

### General
The Text Analytics client will raise exceptions defined in [Azure Core][azure_core].

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

Detailed DEBUG level logging, including request/response bodies and unredacted
headers, can be enabled on a client with the `logging_enable` keyword argument:
```python
import sys
import logging
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalyticsClient

# Create a logger for the 'azure' SDK
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)

# Configure a console output
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

endpoint = "https://<my-custom-subdomain>.cognitiveservices.azure.com/"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
text_analytics_client = TextAnalyticsClient(endpoint, credential, logging_enable=True)
```

Similarly, `logging_enable` can enable detailed logging for a single operation,
even when it isn't enabled for the client:
```python
result = text_analytics_client.analyze_sentiment(documents, logging_enable=True)
```

## Next steps

### More sample code

These code samples show common scenario operations with the Azure Text Analytics client library.
The async versions of the samples (the python sample files appended with `_async`) show asynchronous operations
with Text Analytics and require Python 3.5 or later.

Authenticate the client with a Cognitive Services/Text Analytics API key or a token credential from [azure-identity][azure_identity]:
* [sample_authentication.py][sample_authentication] ([async version][sample_authentication_async])

In a batch of documents:
* Detect language: [sample_detect_language.py][detect_language_sample] ([async version][detect_language_sample_async])
* Recognize entities: [sample_recognize_entities.py][recognize_entities_sample] ([async version][recognize_entities_sample_async])
* Recognize linked entities: [sample_recognize_linked_entities.py][recognize_linked_entities_sample] ([async version][recognize_linked_entities_sample_async])
* Recognize personally identifiable information: [sample_recognize_pii_entities.py][recognize_pii_entities_sample] ([async version][recognize_pii_entities_sample_async])
* Extract key phrases: [sample_extract_key_phrases.py][extract_key_phrases_sample] ([async version][extract_key_phrases_sample_async])
* Analyze sentiment: [sample_analyze_sentiment.py][analyze_sentiment_sample] ([async version][analyze_sentiment_sample_async])

### Additional documentation
For more extensive documentation on Azure Cognitive Services Text Analytics, see the [Text Analytics documentation][TA_product_documentation] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: azure/ai/textanalytics
[TA_pypi]: https://pypi.org/project/azure-ai-textanalytics/
[TA_ref_docs]: https://aka.ms/azsdk-python-textanalytics-ref-docs
[TA_samples]: samples
[TA_product_documentation]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview
[azure_subscription]: https://azure.microsoft.com/free/
[TA_or_CS_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/

[azure_portal_create_TA_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[azure_cli_create_TA_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: ../../identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: ../../identity/azure-identity#credentials
[default_azure_credential]: ../../identity/azure-identity#defaultazurecredential
[service_limits]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits

[document_error]: https://aka.ms/azsdk-python-textanalytics-documenterror
[detect_language_result]: https://aka.ms/azsdk-python-textanalytics-detectlanguageresult
[recognize_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizeentitiesresult
[recognize_pii_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizepiientitiesresult
[recognize_linked_entities_result]: https://aka.ms/azsdk-python-textanalytics-recognizelinkedentitiesresult
[analyze_sentiment_result]: https://aka.ms/azsdk-python-textanalytics-analyzesentimentresult
[extract_key_phrases_result]: https://aka.ms/azsdk-python-textanalytics-extractkeyphrasesresult
[text_document_input]: https://aka.ms/azsdk-python-textanalytics-textdocumentinput
[detect_language_input]: https://aka.ms/azsdk-python-textanalytics-detectlanguageinput
[text_analytics_client]: https://aka.ms/azsdk-python-textanalytics-textanalyticsclient

[analyze_sentiment]: https://aka.ms/azsdk-python-textanalytics-analyzesentiment
[recognize_entities]: https://aka.ms/azsdk-python-textanalytics-recognizeentities
[recognize_pii_entities]: https://aka.ms/azsdk-python-textanalytics-recognizepiientities
[recognize_linked_entities]: https://aka.ms/azsdk-python-textanalytics-recognizelinkedentities
[extract_key_phrases]: https://aka.ms/azsdk-python-textanalytics-extractkeyphrases
[detect_language]: https://aka.ms/azsdk-python-textanalytics-detectlanguage

[language_detection]: https://docs.microsoft.com/azure/cognitive-services/Text-Analytics/how-tos/text-analytics-how-to-language-detection
[language_and_regional_support]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/language-support
[sentiment_analysis]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-sentiment-analysis
[key_phrase_extraction]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-keyword-extraction
[linked_entities_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=general
[linked_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-entity-linking
[pii_entity_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal
[named_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-how-to-entity-linking
[named_entity_categories]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/named-entity-types?tabs=general

[azure_core_ref_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/1.2.1/azure.core.pipeline.policies.html
[azure_core]: ../../core/azure-core/README.md
[azure_identity]: ../../identity/azure-identity
[python_logging]: https://docs.python.org/3.5/library/logging.html
[sample_authentication]: samples/sample_authentication.py
[sample_authentication_async]: samples/async_samples/sample_authentication_async.py
[detect_language_sample]: samples/sample_detect_language.py
[detect_language_sample_async]: samples/async_samples/sample_detect_language_async.py
[analyze_sentiment_sample]: samples/sample_analyze_sentiment.py
[analyze_sentiment_sample_async]: samples/async_samples/sample_analyze_sentiment_async.py
[extract_key_phrases_sample]: samples/sample_extract_key_phrases.py
[extract_key_phrases_sample_async]: samples/async_samples/sample_extract_key_phrases_async.py
[recognize_entities_sample]: samples/sample_recognize_entities.py
[recognize_entities_sample_async]: samples/async_samples/sample_recognize_entities_async.py
[recognize_pii_entities_sample]: samples/sample_recognize_pii_entities.py
[recognize_pii_entities_sample_async]: samples/async_samples/sample_recognize_pii_entities_async.py
[recognize_linked_entities_sample]: samples/sample_recognize_linked_entities.py
[recognize_linked_entities_sample_async]: samples/async_samples/sample_recognize_linked_entities_async.py

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
