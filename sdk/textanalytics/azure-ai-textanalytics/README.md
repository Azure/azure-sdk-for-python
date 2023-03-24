# Azure Text Analytics client library for Python

The Azure Cognitive Service for Language is a cloud-based service that provides Natural Language Processing (NLP) features for understanding and analyzing text, and includes the following main features:

- Sentiment Analysis
- Named Entity Recognition
- Language Detection
- Key Phrase Extraction
- Entity Linking
- Multiple Analysis
- Personally Identifiable Information (PII) Detection
- Text Analytics for Health
- Custom Named Entity Recognition
- Custom Text Classification
- Extractive Text Summarization
- Abstractive Text Summarization

[Source code][source_code]
| [Package (PyPI)][ta_pypi]
| [Package (Conda)](https://anaconda.org/microsoft/azure-ai-textanalytics/)
| [API reference documentation][ta_ref_docs]
| [Product documentation][language_product_documentation]
| [Samples][ta_samples]

## Getting started

### Prerequisites

- Python 3.7 later is required to use this package.
- You must have an [Azure subscription][azure_subscription] and a
  [Cognitive Services or Language service resource][ta_or_cs_resource] to use this package.

#### Create a Cognitive Services or Language service resource

The Language service supports both [multi-service and single-service access][multi_and_single_service].
Create a Cognitive Services resource if you plan to access multiple cognitive services under a single endpoint/key. For Language service access only, create a Language service resource.
You can create the resource using the [Azure Portal][azure_portal_create_ta_resource] or [Azure CLI][azure_cli] following the steps in [this document][azure_cli_create_ta_resource].

Interaction with the service using the client library begins with a [client](#textanalyticsclient "TextAnalyticsClient").
To create a client object, you will need the Cognitive Services or Language service `endpoint` to
your resource and a `credential` that allows you access:

```python
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

credential = AzureKeyCredential("<api_key>")
text_analytics_client = TextAnalyticsClient(endpoint="https://<resource-name>.cognitiveservices.azure.com/", credential=credential)
```

Note that for some Cognitive Services resources the endpoint might look different from the above code snippet.
For example, `https://<region>.api.cognitive.microsoft.com/`.

### Install the package

Install the Azure Text Analytics client library for Python with [pip][pip]:

```bash
pip install azure-ai-textanalytics --pre
```

<!-- SNIPPET:sample_authentication.create_ta_client_with_key -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
```

<!-- END SNIPPET -->

> Note that `5.2.X` and newer targets the Azure Cognitive Service for Language APIs. These APIs include the text analysis and natural language processing features found in the previous versions of the Text Analytics client library.
In addition, the service API has changed from semantic to date-based versioning. This version of the client library defaults to the latest supported API version, which currently is `2022-10-01-preview`.

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version  | Supported API version of service  |
| ------------ | --------------------------------- |
| 5.3.0b2 - Latest beta release | 3.0, 3.1, 2022-05-01, 2022-10-01-preview (default) |
| 5.2.X - Latest stable release | 3.0, 3.1, 2022-05-01 (default) |
| 5.1.0  | 3.0, 3.1 (default) |
| 5.0.0  | 3.0 |

API version can be selected by passing the [api_version][text_analytics_client] keyword argument into the client.
For the latest Language service features, consider selecting the most recent beta API version. For production scenarios, the latest stable version is recommended. Setting to an older version may result in reduced feature compatibility.

### Authenticate the client

#### Get the endpoint

You can find the endpoint for your Language service resource using the
[Azure Portal][azure_portal_get_endpoint]
or [Azure CLI][azure_cli_endpoint_lookup]:

```bash
# Get the endpoint for the Language service resource
az cognitiveservices account show --name "resource-name" --resource-group "resource-group-name" --query "properties.endpoint"
```

#### Get the API Key

You can get the [API key][cognitive_authentication_api_key] from the Cognitive Services or Language service resource in the [Azure Portal][azure_portal_get_endpoint].
Alternatively, you can use [Azure CLI][azure_cli_endpoint_lookup] snippet below to get the API key of your resource.

`az cognitiveservices account keys list --name "resource-name" --resource-group "resource-group-name"`

#### Create a TextAnalyticsClient with an API Key Credential

Once you have the value for the API key, you can pass it as a string into an instance of [AzureKeyCredential][azure-key-credential]. Use the key as the credential parameter
to authenticate the client:

<!-- SNIPPET:sample_authentication.create_ta_client_with_key -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
```

<!-- END SNIPPET -->

#### Create a TextAnalyticsClient with an Azure Active Directory Credential

To use an [Azure Active Directory (AAD) token credential][cognitive_authentication_aad],
provide an instance of the desired credential type obtained from the
[azure-identity][azure_identity_credentials] library.
Note that regional endpoints do not support AAD authentication. Create a [custom subdomain][custom_subdomain]
name for your resource in order to use this type of authentication.

Authentication with AAD requires some initial setup:

- [Install azure-identity][install_azure_identity]
- [Register a new AAD application][register_aad_app]
- [Grant access][grant_role_access] to the Language service by assigning the `"Cognitive Services Language Reader"` role to your service principal.

After setup, you can choose which type of [credential][azure_identity_credentials] from azure.identity to use.
As an example, [DefaultAzureCredential][default_azure_credential]
can be used to authenticate the client:

Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

Use the returned token credential to authenticate the client:

<!-- SNIPPET:sample_authentication.create_ta_client_with_aad -->

```python
import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
credential = DefaultAzureCredential()

text_analytics_client = TextAnalyticsClient(endpoint, credential=credential)
```

<!-- END SNIPPET -->

## Key concepts

### TextAnalyticsClient

The Text Analytics client library provides a [TextAnalyticsClient][text_analytics_client] to do analysis on [batches of documents](#examples "Examples").
It provides both synchronous and asynchronous operations to access a specific use of text analysis, such as language detection or key phrase extraction.

### Input

A **document** is a single unit to be analyzed by the predictive models in the Language service.
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
is the result of a text analysis operation and contains a prediction or predictions about a document input.

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

You can also use the `kind` attribute to filter between result types:

```python
poller = text_analytics_client.begin_analyze_actions(documents, actions)
response = poller.result()
for result in response:
    if result.kind == "SentimentAnalysis":
        print(f"Sentiment is {result.sentiment}")
    elif result.kind == "KeyPhraseExtraction":
        print(f"Key phrases: {result.key_phrases}")
    elif result.is_error is True:
        print(f"Document error: {result.code}, {result.message}")
```

### Long-Running Operations

Long-running operations are operations which consist of an initial request sent to the service to start an operation,
followed by polling the service at intervals to determine whether the operation has completed or failed, and if it has
succeeded, to get the result.

Methods that support healthcare analysis, custom text analysis, or multiple analyses are modeled as long-running operations.
The client exposes a `begin_<method-name>` method that returns a poller object. Callers should wait
for the operation to complete by calling `result()` on the poller object returned from the `begin_<method-name>` method.
Sample code snippets are provided to illustrate using long-running operations [below](#examples "Examples").

## Examples

The following section provides several code snippets covering some of the most common Language service tasks, including:

- [Analyze Sentiment](#analyze-sentiment "Analyze sentiment")
- [Recognize Entities](#recognize-entities "Recognize entities")
- [Recognize Linked Entities](#recognize-linked-entities "Recognize linked entities")
- [Recognize PII Entities](#recognize-pii-entities "Recognize pii entities")
- [Extract Key Phrases](#extract-key-phrases "Extract key phrases")
- [Detect Language](#detect-language "Detect language")
- [Healthcare Entities Analysis](#healthcare-entities-analysis "Healthcare Entities Analysis")
- [Multiple Analysis](#multiple-analysis "Multiple analysis")
- [Custom Entity Recognition][recognize_custom_entities_sample]
- [Custom Single Label Classification][single_label_classify_sample]
- [Custom Multi Label Classification][multi_label_classify_sample]
- [Extractive Summarization][extract_summary_sample]
- [Abstractive Summarization][abstractive_summary_sample]

### Analyze Sentiment

[analyze_sentiment][analyze_sentiment] looks at its input text and determines whether its sentiment is positive, negative, neutral or mixed. It's response includes per-sentence sentiment analysis and confidence scores.

<!-- SNIPPET:sample_analyze_sentiment.analyze_sentiment -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

documents = [
    """I had the best day of my life. I decided to go sky-diving and it made me appreciate my whole life so much more.
    I developed a deep-connection with my instructor as well, and I feel as if I've made a life-long friend in her.""",
    """This was a waste of my time. All of the views on this drop are extremely boring, all I saw was grass. 0/10 would
    not recommend to any divers, even first timers.""",
    """This was pretty good! The sights were ok, and I had fun with my instructors! Can't complain too much about my experience""",
    """I only have one word for my experience: WOW!!! I can't believe I have had such a wonderful skydiving company right
    in my backyard this whole time! I will definitely be a repeat customer, and I want to take my grandmother skydiving too,
    I know she'll love it!"""
]


result = text_analytics_client.analyze_sentiment(documents, show_opinion_mining=True)
docs = [doc for doc in result if not doc.is_error]

print("Let's visualize the sentiment of each of these documents")
for idx, doc in enumerate(docs):
    print(f"Document text: {documents[idx]}")
    print(f"Overall sentiment: {doc.sentiment}")
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[AnalyzeSentimentResult][analyze_sentiment_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [sentiment analysis][sentiment_analysis]. To see how to conduct more granular analysis into the opinions related to individual aspects (such as attributes of a product or service) in a text, see [here][opinion_mining_sample].

### Recognize Entities

[recognize_entities][recognize_entities] recognizes and categories entities in its input text as people, places, organizations, date/time, quantities, percentages, currencies, and more.

<!-- SNIPPET:sample_recognize_entities.recognize_entities -->

```python
import os
import typing
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
reviews = [
    """I work for Foo Company, and we hired Contoso for our annual founding ceremony. The food
    was amazing and we all can't say enough good words about the quality and the level of service.""",
    """We at the Foo Company re-hired Contoso after all of our past successes with the company.
    Though the food was still great, I feel there has been a quality drop since their last time
    catering for us. Is anyone else running into the same problem?""",
    """Bar Company is over the moon about the service we received from Contoso, the best sliders ever!!!!"""
]

result = text_analytics_client.recognize_entities(reviews)
result = [review for review in result if not review.is_error]
organization_to_reviews: typing.Dict[str, typing.List[str]] = {}

for idx, review in enumerate(result):
    for entity in review.entities:
        print(f"Entity '{entity.text}' has category '{entity.category}'")
        if entity.category == 'Organization':
            organization_to_reviews.setdefault(entity.text, [])
            organization_to_reviews[entity.text].append(reviews[idx])

for organization, reviews in organization_to_reviews.items():
    print(
        "\n\nOrganization '{}' has left us the following review(s): {}".format(
            organization, "\n\n".join(reviews)
        )
    )
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[RecognizeEntitiesResult][recognize_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [named entity recognition][named_entity_recognition]
and [supported types][named_entity_categories].

### Recognize Linked Entities

[recognize_linked_entities][recognize_linked_entities] recognizes and disambiguates the identity of each entity found in its input text (for example,
determining whether an occurrence of the word Mars refers to the planet, or to the
Roman god of war). Recognized entities are associated with URLs to a well-known knowledge base, like Wikipedia.

<!-- SNIPPET:sample_recognize_linked_entities.recognize_linked_entities -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
documents = [
    """
    Microsoft was founded by Bill Gates with some friends he met at Harvard. One of his friends,
    Steve Ballmer, eventually became CEO after Bill Gates as well. Steve Ballmer eventually stepped
    down as CEO of Microsoft, and was succeeded by Satya Nadella.
    Microsoft originally moved its headquarters to Bellevue, Washington in January 1979, but is now
    headquartered in Redmond.
    """
]

result = text_analytics_client.recognize_linked_entities(documents)
docs = [doc for doc in result if not doc.is_error]

print(
    "Let's map each entity to it's Wikipedia article. I also want to see how many times each "
    "entity is mentioned in a document\n\n"
)
entity_to_url = {}
for doc in docs:
    for entity in doc.entities:
        print("Entity '{}' has been mentioned '{}' time(s)".format(
            entity.name, len(entity.matches)
        ))
        if entity.data_source == "Wikipedia":
            entity_to_url[entity.name] = entity.url
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[RecognizeLinkedEntitiesResult][recognize_linked_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [entity linking][linked_entity_recognition]
and [supported types][linked_entities_categories].

### Recognize PII Entities

[recognize_pii_entities][recognize_pii_entities] recognizes and categorizes Personally Identifiable Information (PII) entities in its input text, such as
Social Security Numbers, bank account information, credit card numbers, and more.

<!-- SNIPPET:sample_recognize_pii_entities.recognize_pii_entities -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)
documents = [
    """Parker Doe has repaid all of their loans as of 2020-04-25.
    Their SSN is 859-98-0987. To contact them, use their phone number
    555-555-5555. They are originally from Brazil and have Brazilian CPF number 998.214.865-68"""
]

result = text_analytics_client.recognize_pii_entities(documents)
docs = [doc for doc in result if not doc.is_error]

print(
    "Let's compare the original document with the documents after redaction. "
    "I also want to comb through all of the entities that got redacted"
)
for idx, doc in enumerate(docs):
    print(f"Document text: {documents[idx]}")
    print(f"Redacted document text: {doc.redacted_text}")
    for entity in doc.entities:
        print("...Entity '{}' with category '{}' got redacted".format(
            entity.text, entity.category
        ))
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[RecognizePiiEntitiesResult][recognize_pii_entities_result], [DocumentError][document_error]]

Please refer to the service documentation for [supported PII entity types][pii_entity_categories].

Note: The Recognize PII Entities service is available in API version v3.1 and newer.

### Extract Key Phrases

[extract_key_phrases][extract_key_phrases] determines the main talking points in its input text. For example, for the input text "The food was delicious and there were wonderful staff", the API returns: "food" and "wonderful staff".

<!-- SNIPPET:sample_extract_key_phrases.extract_key_phrases -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
articles = [
    """
    Washington, D.C. Autumn in DC is a uniquely beautiful season. The leaves fall from the trees
    in a city chock-full of forests, leaving yellow leaves on the ground and a clearer view of the
    blue sky above...
    """,
    """
    Redmond, WA. In the past few days, Microsoft has decided to further postpone the start date of
    its United States workers, due to the pandemic that rages with no end in sight...
    """,
    """
    Redmond, WA. Employees at Microsoft can be excited about the new coffee shop that will open on campus
    once workers no longer have to work remotely...
    """
]

result = text_analytics_client.extract_key_phrases(articles)
for idx, doc in enumerate(result):
    if not doc.is_error:
        print("Key phrases in article #{}: {}".format(
            idx + 1,
            ", ".join(doc.key_phrases)
        ))
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[ExtractKeyPhrasesResult][extract_key_phrases_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [key phrase extraction][key_phrase_extraction].

### Detect Language

[detect_language][detect_language] determines the language of its input text, including the confidence score of the predicted language.

<!-- SNIPPET:sample_detect_language.detect_language -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
documents = [
    """
    The concierge Paulette was extremely helpful. Sadly when we arrived the elevator was broken, but with Paulette's help we barely noticed this inconvenience.
    She arranged for our baggage to be brought up to our room with no extra charge and gave us a free meal to refurbish all of the calories we lost from
    walking up the stairs :). Can't say enough good things about my experience!
    """,
    """
    最近由于工作压力太大，我们决定去富酒店度假。那儿的温泉实在太舒服了，我跟我丈夫都完全恢复了工作前的青春精神！加油！
    """
]

result = text_analytics_client.detect_language(documents)
reviewed_docs = [doc for doc in result if not doc.is_error]

print("Let's see what language each review is in!")

for idx, doc in enumerate(reviewed_docs):
    print("Review #{} is in '{}', which has ISO639-1 name '{}'\n".format(
        idx, doc.primary_language.name, doc.primary_language.iso6391_name
    ))
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[DetectLanguageResult][detect_language_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [language detection][language_detection]
and [language and regional support][language_and_regional_support].

### Healthcare Entities Analysis

[Long-running operation](#long-running-operations) [begin_analyze_healthcare_entities][analyze_healthcare_entities] extracts entities recognized within the healthcare domain, and identifies relationships between entities within the input document and links to known sources of information in various well known databases, such as UMLS, CHV, MSH, etc.

<!-- SNIPPET:sample_analyze_healthcare_entities.analyze_healthcare_entities -->

```python
import os
import typing
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient, HealthcareEntityRelation

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)

documents = [
    """
    Patient needs to take 100 mg of ibuprofen, and 3 mg of potassium. Also needs to take
    10 mg of Zocor.
    """,
    """
    Patient needs to take 50 mg of ibuprofen, and 2 mg of Coumadin.
    """
]

poller = text_analytics_client.begin_analyze_healthcare_entities(documents)
result = poller.result()

docs = [doc for doc in result if not doc.is_error]

print("Let's first visualize the outputted healthcare result:")
for doc in docs:
    for entity in doc.entities:
        print(f"Entity: {entity.text}")
        print(f"...Normalized Text: {entity.normalized_text}")
        print(f"...Category: {entity.category}")
        print(f"...Subcategory: {entity.subcategory}")
        print(f"...Offset: {entity.offset}")
        print(f"...Confidence score: {entity.confidence_score}")
        if entity.data_sources is not None:
            print("...Data Sources:")
            for data_source in entity.data_sources:
                print(f"......Entity ID: {data_source.entity_id}")
                print(f"......Name: {data_source.name}")
        if entity.assertion is not None:
            print("...Assertion:")
            print(f"......Conditionality: {entity.assertion.conditionality}")
            print(f"......Certainty: {entity.assertion.certainty}")
            print(f"......Association: {entity.assertion.association}")
    for relation in doc.entity_relations:
        print(f"Relation of type: {relation.relation_type} has the following roles")
        for role in relation.roles:
            print(f"...Role '{role.name}' with entity '{role.entity.text}'")
    print("------------------------------------------")

print("Now, let's get all of medication dosage relations from the documents")
dosage_of_medication_relations = [
    entity_relation
    for doc in docs
    for entity_relation in doc.entity_relations if entity_relation.relation_type == HealthcareEntityRelation.DOSAGE_OF_MEDICATION
]
```

<!-- END SNIPPET -->

Note: Healthcare Entities Analysis is only available with API version v3.1 and newer.

### Multiple Analysis

[Long-running operation](#long-running-operations) [begin_analyze_actions][analyze_actions] performs multiple analyses over one set of documents in a single request. Currently it is supported using any combination of the following Language APIs in a single request:

- Entities Recognition
- PII Entities Recognition
- Linked Entity Recognition
- Key Phrase Extraction
- Sentiment Analysis
- Custom Entity Recognition (API version 2022-05-01 and newer)
- Custom Single Label Classification (API version 2022-05-01 and newer)
- Custom Multi Label Classification (API version 2022-05-01 and newer)
- Healthcare Entities Analysis (API version 2022-05-01 and newer)
- Extractive Summarization (API version 2022-10-01-preview and newer)
- Abstractive Summarization (API version 2022-10-01-preview and newer)

<!-- SNIPPET:sample_analyze_actions.analyze -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    RecognizeEntitiesAction,
    RecognizeLinkedEntitiesAction,
    RecognizePiiEntitiesAction,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction,
)

endpoint = os.environ["AZURE_LANGUAGE_ENDPOINT"]
key = os.environ["AZURE_LANGUAGE_KEY"]

text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
)

documents = [
    'We went to Contoso Steakhouse located at midtown NYC last week for a dinner party, and we adore the spot! '
    'They provide marvelous food and they have a great menu. The chief cook happens to be the owner (I think his name is John Doe) '
    'and he is super nice, coming out of the kitchen and greeted us all.'
    ,

    'We enjoyed very much dining in the place! '
    'The Sirloin steak I ordered was tender and juicy, and the place was impeccably clean. You can even pre-order from their '
    'online menu at www.contososteakhouse.com, call 312-555-0176 or send email to order@contososteakhouse.com! '
    'The only complaint I have is the food didn\'t come fast enough. Overall I highly recommend it!'
]

poller = text_analytics_client.begin_analyze_actions(
    documents,
    display_name="Sample Text Analysis",
    actions=[
        RecognizeEntitiesAction(),
        RecognizePiiEntitiesAction(),
        ExtractKeyPhrasesAction(),
        RecognizeLinkedEntitiesAction(),
        AnalyzeSentimentAction(),
    ],
)

document_results = poller.result()
for doc, action_results in zip(documents, document_results):
    print(f"\nDocument text: {doc}")
    for result in action_results:
        if result.kind == "EntityRecognition":
            print("...Results of Recognize Entities Action:")
            for entity in result.entities:
                print(f"......Entity: {entity.text}")
                print(f".........Category: {entity.category}")
                print(f".........Confidence Score: {entity.confidence_score}")
                print(f".........Offset: {entity.offset}")

        elif result.kind == "PiiEntityRecognition":
            print("...Results of Recognize PII Entities action:")
            for pii_entity in result.entities:
                print(f"......Entity: {pii_entity.text}")
                print(f".........Category: {pii_entity.category}")
                print(f".........Confidence Score: {pii_entity.confidence_score}")

        elif result.kind == "KeyPhraseExtraction":
            print("...Results of Extract Key Phrases action:")
            print(f"......Key Phrases: {result.key_phrases}")

        elif result.kind == "EntityLinking":
            print("...Results of Recognize Linked Entities action:")
            for linked_entity in result.entities:
                print(f"......Entity name: {linked_entity.name}")
                print(f".........Data source: {linked_entity.data_source}")
                print(f".........Data source language: {linked_entity.language}")
                print(
                    f".........Data source entity ID: {linked_entity.data_source_entity_id}"
                )
                print(f".........Data source URL: {linked_entity.url}")
                print(".........Document matches:")
                for match in linked_entity.matches:
                    print(f"............Match text: {match.text}")
                    print(f"............Confidence Score: {match.confidence_score}")
                    print(f"............Offset: {match.offset}")
                    print(f"............Length: {match.length}")

        elif result.kind == "SentimentAnalysis":
            print("...Results of Analyze Sentiment action:")
            print(f"......Overall sentiment: {result.sentiment}")
            print(
                f"......Scores: positive={result.confidence_scores.positive}; \
                neutral={result.confidence_scores.neutral}; \
                negative={result.confidence_scores.negative} \n"
            )

        elif result.is_error is True:
            print(
                f"...Is an error with code '{result.error.code}' and message '{result.error.message}'"
            )

    print("------------------------------------------")
```

<!-- END SNIPPET -->

The returned response is an object encapsulating multiple iterables, each representing results of individual analyses.

Note: Multiple analysis is available in API version v3.1 and newer.

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

endpoint = "https://<resource-name>.cognitiveservices.azure.com/"
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

Authenticate the client with a Cognitive Services/Language service API key or a token credential from [azure-identity][azure_identity]:

- [sample_authentication.py][sample_authentication] ([async version][sample_authentication_async])

Common scenarios

- Analyze sentiment: [sample_analyze_sentiment.py][analyze_sentiment_sample] ([async version][analyze_sentiment_sample_async])
- Recognize entities: [sample_recognize_entities.py][recognize_entities_sample] ([async version][recognize_entities_sample_async])
- Recognize personally identifiable information: [sample_recognize_pii_entities.py][recognize_pii_entities_sample] ([async version][recognize_pii_entities_sample_async])
- Recognize linked entities: [sample_recognize_linked_entities.py][recognize_linked_entities_sample] ([async version][recognize_linked_entities_sample_async])
- Extract key phrases: [sample_extract_key_phrases.py][extract_key_phrases_sample] ([async version][extract_key_phrases_sample_async])
- Detect language: [sample_detect_language.py][detect_language_sample] ([async version][detect_language_sample_async])
- Healthcare Entities Analysis: [sample_analyze_healthcare_entities.py][analyze_healthcare_entities_sample] ([async version][analyze_healthcare_entities_sample_async])
- Multiple Analysis: [sample_analyze_actions.py][analyze_sample] ([async version][analyze_sample_async])
- Custom Entity Recognition: [sample_recognize_custom_entities.py][recognize_custom_entities_sample] ([async_version][recognize_custom_entities_sample_async])
- Custom Single Label Classification: [sample_single_label_classify.py][single_label_classify_sample] ([async_version][single_label_classify_sample_async])
- Custom Multi Label Classification: [sample_multi_label_classify.py][multi_label_classify_sample] ([async_version][multi_label_classify_sample_async])
- Extractive text summarization: [sample_extract_summary.py][extract_summary_sample] ([async version][extract_summary_sample_async])
- Abstractive text summarization: [sample_abstractive_summary.py][abstractive_summary_sample] ([async version][abstractive_summary_sample_async])

Advanced scenarios

- Opinion Mining: [sample_analyze_sentiment_with_opinion_mining.py][opinion_mining_sample] ([async_version][opinion_mining_sample_async])
- NER resolutions: [sample_recognize_entity_resolutions.py][recognize_entity_resolutions_sample] ([async_version][recognize_entity_resolutions_sample_async])

### Additional documentation

For more extensive documentation on Azure Cognitive Service for Language, see the [Language Service documentation][language_product_documentation] on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/textanalytics/azure-ai-textanalytics/azure/ai/textanalytics
[ta_pypi]: https://pypi.org/project/azure-ai-textanalytics/
[ta_ref_docs]: https://aka.ms/azsdk-python-textanalytics-ref-docs
[ta_samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples
[language_product_documentation]: https://docs.microsoft.com/azure/cognitive-services/language-service
[azure_subscription]: https://azure.microsoft.com/free/
[ta_or_cs_resource]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_ta_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_cli_create_ta_resource]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli
[multi_and_single_service]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://docs.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://docs.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://docs.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://docs.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://docs.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
[azure_identity_credentials]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#credentials
[default_azure_credential]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#defaultazurecredential
[service_limits]: https://aka.ms/azsdk/textanalytics/data-limits
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
[analyze_actions]: https://aka.ms/azsdk/python/docs/ref/textanalytics#azure.ai.textanalytics.TextAnalyticsClient.begin_analyze_actions
[analyze_healthcare_entities]: https://aka.ms/azsdk/python/docs/ref/textanalytics#azure.ai.textanalytics.TextAnalyticsClient.begin_analyze_healthcare_entities
[recognize_entities]: https://aka.ms/azsdk-python-textanalytics-recognizeentities
[recognize_pii_entities]: https://aka.ms/azsdk-python-textanalytics-recognizepiientities
[recognize_linked_entities]: https://aka.ms/azsdk-python-textanalytics-recognizelinkedentities
[extract_key_phrases]: https://aka.ms/azsdk-python-textanalytics-extractkeyphrases
[detect_language]: https://aka.ms/azsdk-python-textanalytics-detectlanguage
[language_detection]: https://docs.microsoft.com/azure/cognitive-services/language-service/language-detection/overview
[language_and_regional_support]: https://docs.microsoft.com/azure/cognitive-services/language-service/language-detection/language-support
[sentiment_analysis]: https://docs.microsoft.com/azure/cognitive-services/language-service/sentiment-opinion-mining/overview
[key_phrase_extraction]: https://docs.microsoft.com/azure/cognitive-services/language-service/key-phrase-extraction/overview
[linked_entities_categories]: https://aka.ms/taner
[linked_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/language-service/entity-linking/overview
[pii_entity_categories]: https://aka.ms/azsdk/language/pii
[named_entity_recognition]: https://docs.microsoft.com/azure/cognitive-services/language-service/named-entity-recognition/overview
[named_entity_categories]: https://aka.ms/taner
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[python_logging]: https://docs.python.org/3/library/logging.html
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py
[detect_language_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_detect_language.py
[detect_language_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py
[analyze_sentiment_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment.py
[analyze_sentiment_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py
[extract_key_phrases_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_key_phrases.py
[extract_key_phrases_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py
[recognize_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entities.py
[recognize_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py
[recognize_linked_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py
[recognize_linked_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py
[recognize_pii_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py
[recognize_pii_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py
[analyze_healthcare_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_healthcare_entities.py
[analyze_healthcare_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_healthcare_entities_async.py
[analyze_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_actions.py
[analyze_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_actions_async.py
[opinion_mining_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_sentiment_with_opinion_mining.py
[opinion_mining_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_with_opinion_mining_async.py
[recognize_custom_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_custom_entities.py
[recognize_custom_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_custom_entities_async.py
[single_label_classify_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_single_label_classify.py
[single_label_classify_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_single_label_classify_async.py
[multi_label_classify_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_multi_label_classify.py
[multi_label_classify_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_multi_label_classify_async.py
[healthcare_action_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_analyze_healthcare_action.py
[extract_summary_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_extract_summary.py
[extract_summary_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_extract_summary_async.py
[abstractive_summary_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_abstractive_summary.py
[abstractive_summary_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_abstractive_summary_async.py
[recognize_entity_resolutions_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/sample_recognize_entity_resolutions.py
[recognize_entity_resolutions_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/samples/async_samples/sample_recognize_entity_resolutions_async.py
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
