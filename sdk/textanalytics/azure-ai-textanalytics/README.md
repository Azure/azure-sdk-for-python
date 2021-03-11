# Azure Text Analytics client library for Python

Text Analytics is a cloud-based service that provides advanced natural language processing over raw text, and includes the following main functions:

- Sentiment Analysis
- Named Entity Recognition
- Linked Entity Recognition
- Personally Identifiable Information (PII) Entity Recognition
- Language Detection
- Key Phrase Extraction
- Batch Analysis
- Healthcare Entities Analysis (Gated Preview)

[Source code][source_code] | [Package (PyPI)][ta_pypi] | [API reference documentation][ta_ref_docs]| [Product documentation][ta_product_documentation] | [Samples][ta_samples]

## Getting started

### Prerequisites

- Python 2.7, or 3.5 or later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and a
  [Cognitive Services or Text Analytics resource][ta_or_cs_resource] to use this package.

#### Create a Cognitive Services or Text Analytics resource

Text Analytics supports both [multi-service and single-service access][multi_and_single_service].
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Text Analytics access only, create a Text Analytics resource.

You can create the resource using

**Option 1:** [Azure Portal][azure_portal_create_ta_resource]

**Option 2:** [Azure CLI][azure_cli_create_ta_resource].
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

Interaction with this service begins with an instance of a [client](#textanalyticsclient "TextAnalyticsClient").
To create a client object, you will need the cognitive services or text analytics `endpoint` to
your resource and a `credential` that allows you access:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
text_analytics_client = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
```

Note that if you create a [custom subdomain][cognitive_custom_subdomain]
name for your resource the endpoint may look different than in the above code snippet.
For example, `https://<my-custom-subdomain>.cognitiveservices.azure.com/`.

### Install the package

Install the Azure Text Analytics client library for Python with [pip][pip]:

```bash
pip install azure-ai-textanalytics --pre
```

> Note: This version of the client library defaults to the v3.1-preview version of the service

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version                                                               | Supported API version of service  |
| ------------------------------------------------------------------------- | --------------------------------- |
| 5.0.0 - Latest GA release (can be installed by removing the `--pre` flag) | 3.0                               |
| 5.1.0b6 - Latest release (beta)                                           | 3.0, 3.1-preview.4 |

### Authenticate the client

#### Get the endpoint

You can find the endpoint for your text analytics resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the text analytics resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API Key

You can get the [API key][cognitive_authentication_api_key] from the Cognitive Services or Text Analytics resource in the [Azure Portal][azure_portal_get_endpoint].
Alternatively, you can use [Azure CLI][azure_cli_endpoint_lookup] snippet below to get the API key of your resource.

`az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"`

#### Create a TextAnalyticsClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of [AzureKeyCredential][azure-key-credential]. Use the key as the credential parameter
to authenticate the client:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
text_analytics_client = TextAnalyticsClient(endpoint="https://<region>.api.cognitive.microsoft.com/", credential=credential)
```

#### Create a TextAnalyticsClient with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]
- [Register a new AAD application][register_aad_app]
- [Grant access][grant_role_access] to Text Analytics by assigning the `"Cognitive Services User"` role to your service principal.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
text_analytics_client = TextAnalyticsClient(endpoint="https://<my-custom-subdomain>.api.cognitive.microsoft.com/", credential=credential)
```

## Key concepts

### TextAnalyticsClient

The Text Analytics client library provides a [TextAnalyticsClient][text_analytics_client] to do analysis on [batches of documents](#examples "Examples").
It provides both synchronous and asynchronous operations to access a specific use of Text Analytics, such as language detection or key phrase extraction.

### Input

A **document** is a single unit to be analyzed by the predictive models in the Text Analytics service.
The input for each operation is passed as a **list** of documents.

Each document can be passed as a string in the list, e.g.

```python
documents = ["I hated the movie. It was so slow!", "The movie made it into my top ten favorites. What a great movie!"]
```

or, if you wish to pass in a per-item document `id` or `language`/`country_hint`, they can be passed as a list of
[DetectLanguageInput][detect_language_input] or
[TextDocumentInput][text_document_input]
or a dict-like representation of the object:

```python
documents = [
    {"id": "1", "language": "en", "text": "I hated the movie. It was so slow!"},
    {"id": "2", "language": "en", "text": "The movie made it into my top ten favorites. What a great movie!"},
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

### Long-Running Operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that support Healthcare Analysis or batch operations over multiple Text Analytics APIs are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns an `LROPoller` or `AsyncLROPoller`. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Examples

The following section provides several code snippets covering some of the most common Text Analytics tasks, including:

- [Analyze Sentiment](#analyze-sentiment "Analyze sentiment")
- [Recognize Entities](#recognize-entities "Recognize entities")
- [Recognize Linked Entities](#recognize-linked-entities "Recognize linked entities")
- [Recognize PII Entities](#recognize-pii-entities "Recognize pii entities")
- [Extract Key Phrases](#extract-key-phrases "Extract key phrases")
- [Detect Language](#detect-language "Detect language")
- [Healthcare Entities Analysis](#healthcare-entities-analysis "Healthcare Entities Analysis")
- [Batch Analysis](#batch-analysis "Batch analysis")

### Analyze sentiment

[analyze_sentiment][analyze_sentiment] looks at its input text and determines whether its sentiment is positive, negative, neutral or mixed. It's response includes per-sentence sentiment analysis and confidence scores.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    "I did not like the restaurant. The food was somehow both too spicy and underseasoned. Additionally, I thought the location was too far away from the playhouse.",
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

Please refer to the service documentation for a conceptual discussion of [sentiment analysis][sentiment_analysis]. To see how to conduct more granular analysis into the opinions related to individual aspects (such as attributes of a product or service) in a text, see [here][opinion_mining_sample].

### Recognize entities

[recognize_entities][recognize_entities] recognizes and categories entities in its input text as people, places, organizations, date/time, quantities, percentages, currencies, and more.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    """
    Microsoft was founded by Bill Gates and Paul Allen. Its headquarters are located in Redmond. Redmond is a
    city in King County, Washington, United States, located 15 miles east of Seattle.
    """,
    "Jeff bought three dozen eggs because there was a 50% discount."
]

response = text_analytics_client.recognize_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    for entity in doc.entities:
        print("Entity: {}".format(entity.text))
        print("...Category: {}".format(entity.category))
        print("...Confidence Score: {}".format(entity.confidence_score))
        print("...Offset: {}".format(entity.offset))
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizeEntitiesResult][recognize_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [named entity recognition][named_entity_recognition]
and [supported types][named_entity_categories].

### Recognize linked entities

[recognize_linked_entities][recognize_linked_entities] recognizes and disambiguates the identity of each entity found in its input text (for example,
determining whether an occurrence of the word Mars refers to the planet, or to the
Roman god of war). Recognized entities are associated with URLs to a well-known knowledge base, like Wikipedia.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    "Microsoft was founded by Bill Gates and Paul Allen. Its headquarters are located in Redmond.",
    "Easter Island, a Chilean territory, is a remote volcanic island in Polynesia."
]

response = text_analytics_client.recognize_linked_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]

for doc in result:
    for entity in doc.entities:
        print("Entity: {}".format(entity.name))
        print("...URL: {}".format(entity.url))
        print("...Data Source: {}".format(entity.data_source))
        print("...Entity matches:")
        for match in entity.matches:
            print("......Entity match text: {}".format(match.text))
            print("......Confidence Score: {}".format(match.confidence_score))
            print("......Offset: {}".format(match.offset))
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizeLinkedEntitiesResult][recognize_linked_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [entity linking][linked_entity_recognition]
and [supported types][linked_entities_categories].

### Recognize PII entities

[recognize_pii_entities][recognize_pii_entities] recognizes and categorizes Personally Identifiable Information (PII) entities in its input text, such as
Social Security Numbers, bank account information, credit card numbers, and more. This endpoint is only available for v3.1-preview and up.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    """
    We have an employee called Parker who cleans up after customers. The employee's
    SSN is 859-98-0987, and their phone number is 555-555-5555.
    """
]
response = text_analytics_client.recognize_pii_entities(documents, language="en")
result = [doc for doc in response if not doc.is_error]
for idx, doc in enumerate(result):
    print("Document text: {}".format(documents[idx]))
    print("Redacted document text: {}".format(doc.redacted_text))
    for entity in doc.entities:
        print("...Entity: {}".format(entity.text))
        print("......Category: {}".format(entity.category))
        print("......Confidence Score: {}".format(entity.confidence_score))
        print("......Offset: {}".format(entity.offset))
```

The returned response is a heterogeneous list of result and error objects: list[[RecognizePiiEntitiesResult][recognize_pii_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for [supported PII entity types][pii_entity_categories].

### Extract key phrases

[extract_key_phrases][extract_key_phrases] determines the main talking points in its input text. For example, for the input text "The food was delicious and there were wonderful staff", the API returns: "food" and "wonderful staff".

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    "Redmond is a city in King County, Washington, United States, located 15 miles east of Seattle.",
    """
    I need to take my cat to the veterinarian. He has been sick recently, and I need to take him
    before I travel to South America for the summer.
    """,
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
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = [
    """
    This whole document is written in English. In order for the whole document to be written
    in English, every sentence also has to be written in English, which it is.
    """,
    "Il documento scritto in italiano.",
    "Dies ist in deutsche Sprache verfasst."
]

response = text_analytics_client.detect_language(documents)
result = [doc for doc in response if not doc.is_error]

for doc in result:
    print("Language detected: {}".format(doc.primary_language.name))
    print("ISO6391 name: {}".format(doc.primary_language.iso6391_name))
    print("Confidence score: {}\n".format(doc.primary_language.confidence_score))
```

The returned response is a heterogeneous list of result and error objects: list[[DetectLanguageResult][detect_language_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [language detection][language_detection]
and [language and regional support][language_and_regional_support].

### Healthcare Entities Analysis

[Long-running operation](#long-running-operations) [`begin_analyze_healthcare_entities`][analyze_healthcare_entities] extracts entities recognized within the healthcare domain, and identifies relationships between entities within the input document and links to known sources of information in various well known databases, such as UMLS, CHV, MSH, etc.

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = ["Subject is taking 100mg of ibuprofen twice daily"]

poller = text_analytics_client.begin_analyze_healthcare_entities(documents)
result = poller.result()

docs = [doc for doc in result if not doc.is_error]

print("Results of Healthcare Entities Analysis:")
for idx, doc in enumerate(docs):
    for entity in doc.entities:
        print("Entity: {}".format(entity.text))
        print("...Normalized Text: {}".format(entity.normalized_text))
        print("...Category: {}".format(entity.category))
        print("...Subcategory: {}".format(entity.subcategory))
        print("...Offset: {}".format(entity.offset))
        print("...Confidence score: {}".format(entity.confidence_score))
        if entity.data_sources is not None:
            print("...Data Sources:")
            for data_source in entity.data_sources:
                print("......Entity ID: {}".format(data_source.entity_id))
                print("......Name: {}".format(data_source.name))
        if entity.assertion is not None:
            print("...Assertion:")
            print("......Conditionality: {}".format(entity.assertion.conditionality))
            print("......Certainty: {}".format(entity.assertion.certainty))
            print("......Association: {}".format(entity.assertion.association))
    for relation in doc.entity_relations:
        print("Relation of type: {} has the following roles".format(relation.relation_type))
        for role in relation.roles:
            print("...Role '{}' with entity '{}'".format(role.name, role.entity.text))
    print("------------------------------------------")
```

Note: The Healthcare Entities Analysis service is currently available only in the API v3.1 preview versions and is in gated preview. Since this is a gated preview, AAD is not supported. More information [here](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-for-health?tabs=ner#request-access-to-the-public-preview).

### Batch Analysis

[Long-running operation](#long-running-operations) [`begin_analyze_batch_actions`][analyze_batch_actions] performs multiple analyses over one set of documents in a single request. Currently batching is supported using any combination of the following Text Analytics APIs in a single request:

- Entities Recognition
- PII Entities Recognition
- Linked Entity Recognition
- Key Phrase Extraction

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    RecognizeLinkedEntitiesAction
)

credential = AzureKeyCredential("<api_key>")
endpoint="https://<region>.api.cognitive.microsoft.com/"

text_analytics_client = TextAnalyticsClient(endpoint, credential)

documents = ["Microsoft was founded by Bill Gates and Paul Allen."]

poller = text_analytics_client.begin_analyze_batch_actions(
    documents,
    display_name="Sample Text Analysis",
    actions=[
        RecognizeEntitiesAction(),
        RecognizePiiEntitiesAction(),
        ExtractKeyPhrasesAction(),
        RecognizeLinkedEntitiesAction()
    ]
)

# returns batch actions results in the same order as the inputted actions
result = poller.result()

first_action_result = next(result)
print("Results of Entities Recognition action:")
docs = [doc for doc in first_action_result.document_results if not doc.is_error]

for idx, doc in enumerate(docs):
    print("\nDocument text: {}".format(documents[idx]))
    for entity in doc.entities:
        print("Entity: {}".format(entity.text))
        print("...Category: {}".format(entity.category))
        print("...Confidence Score: {}".format(entity.confidence_score))
        print("...Offset: {}".format(entity.offset))
    print("------------------------------------------")

second_action_result = next(result)
print("Results of PII Entities Recognition action:")
docs = [doc for doc in second_action_result.document_results if not doc.is_error]

for idx, doc in enumerate(docs):
    print("Document text: {}".format(documents[idx]))
    for entity in doc.entities:
        print("Entity: {}".format(entity.text))
        print("Category: {}".format(entity.category))
        print("Confidence Score: {}\n".format(entity.confidence_score))
    print("------------------------------------------")

third_action_result = next(result)
print("Results of Key Phrase Extraction action:")
docs = [doc for doc in third_action_result.document_results if not doc.is_error]

for idx, doc in enumerate(docs):
    print("Document text: {}\n".format(documents[idx]))
    print("Key Phrases: {}\n".format(doc.key_phrases))
    print("------------------------------------------")

fourth_action_result = next(result)
print("Results of Linked Entities Recognition action:")
docs = [doc for doc in fourth_action_result.document_results if not doc.is_error]

for idx, doc in enumerate(docs):
    print("Document text: {}\n".format(documents[idx]))
    for linked_entity in doc.entities:
        print("Entity name: {}".format(linked_entity.name))
        print("...Data source: {}".format(linked_entity.data_source))
        print("...Data source language: {}".format(linked_entity.language))
        print("...Data source entity ID: {}".format(linked_entity.data_source_entity_id))
        print("...Data source URL: {}".format(linked_entity.url))
        print("...Document matches:")
        for match in linked_entity.matches:
            print("......Match text: {}".format(match.text))
            print(".........Confidence Score: {}".format(match.confidence_score))
            print(".........Offset: {}".format(match.offset))
            print(".........Length: {}".format(match.length))
    print("------------------------------------------")
```

The returned response is an object encapsulating multiple iterables, each representing results of individual analyses.

Note: Batch analysis is currently available only in the v3.1-preview API version.

## Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Known Issues

- `begin_analyze_healthcare_entities` is currently in gated preview and can not be used with AAD credentials. For more information, see [the Text Analytics for Health documentation](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-for-health?tabs=ner#request-access-to-the-public-preview).
- At time of this SDK release, the service is not respecting the value passed through `model_version` to `begin_analyze_healthcare_entities`, it only uses the latest model.

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

endpoint = "https://<region>.cognitiveservices.azure.com/"
credential = DefaultAzureCredential()

# This client will log detailed information about its HTTP sessions, at DEBUG level
text_analytics_client = TextAnalyticsClient(endpoint, credential, logging_enable=True)
result = text_analytics_client.analyze_sentiment(["I did not like the restaurant. The food was too spicy."])
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

- [sample_authentication.py][sample_authentication] ([async version][sample_authentication_async])

Common scenarios

- Analyze sentiment: [sample_analyze_sentiment.py][analyze_sentiment_sample] ([async version][analyze_sentiment_sample_async])
- Recognize entities: [sample_recognize_entities.py][recognize_entities_sample] ([async version][recognize_entities_sample_async])
- Recognize personally identifiable information: [sample_recognize_pii_entities.py][recognize_pii_entities_sample]([async version][recognize_pii_entities_sample_async])
- Recognize linked entities: [sample_recognize_linked_entities.py][recognize_linked_entities_sample] ([async version][recognize_linked_entities_sample_async])
- Extract key phrases: [sample_extract_key_phrases.py][extract_key_phrases_sample] ([async version][extract_key_phrases_sample_async])
- Detect language: [sample_detect_language.py][detect_language_sample] ([async version][detect_language_sample_async])
- Healthcare Entities Analysis: [sample_analyze_healthcare_entities.py][analyze_healthcare_entities_sample] ([async version][analyze_healthcare_entities_sample_async])
- Batch Analysis: [sample_analyze_batch_actions.py][analyze_sample] ([async version][analyze_sample_async])

Advanced scenarios

- Opinion Mining: [sample_analyze_sentiment_with_opinion_mining.py][opinion_mining_sample] ([async_version][opinion_mining_sample_async])

### Additional documentation

For more extensive documentation on Azure Cognitive Services Text Analytics, see the [Text Analytics documentation][ta_product_documentation] on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics
[ta_pypi]: https://pypi.org/project/azure-ai-textanalytics/
[ta_ref_docs]: https://aka.ms/azsdk-python-textanalytics-ref-docs
[ta_samples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples
[ta_product_documentation]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview
[azure_subscription]: https://azure.microsoft.com/free/
[ta_or_cs_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_ta_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[azure_cli_create_ta_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli?tabs=windows
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential
[service_limits]: https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview#data-limits
[azure-key-credential]: https://aka.ms/azsdk-python-core-azurekeycredential
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
[analyze_batch_actions]: https://aka.ms/azsdk/python/docs/ref/textanalytics#azure.ai.textanalytics.TextAnalyticsClient.begin_analyze_batch_actions
[analyze_healthcare_entities]: https://aka.ms/azsdk/python/docs/ref/textanalytics#azure.ai.textanalytics.TextAnalyticsClient.begin_analyze_healthcare_entities
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
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[python_logging]: https://docs.python.org/3.5/library/logging.html
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py
[detect_language_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_language.py
[detect_language_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py
[analyze_sentiment_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py
[analyze_sentiment_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py
[extract_key_phrases_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py
[extract_key_phrases_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py
[recognize_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py
[recognize_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py
[recognize_linked_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py
[recognize_linked_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py
[recognize_pii_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py
[recognize_pii_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py
[analyze_healthcare_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_healthcare_entities.py
[analyze_healthcare_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_healthcare_entities_async.py
[analyze_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_batch_actions.py
[analyze_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_batch_actions_async.py
[opinion_mining_sample]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment_with_opinion_mining.py
[opinion_mining_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_with_opinion_mining_async.py
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
