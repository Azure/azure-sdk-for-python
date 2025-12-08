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
pip install azure-ai-textanalytics
```

<!-- SNIPPET:sample_authentication.create_ta_client_with_key -->

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient

endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
key = os.environ["AZURE_TEXT_KEY"]

text_client = TextAnalysisClient(endpoint, AzureKeyCredential(key))
```

<!-- END SNIPPET -->

> Note that `5.2.X` and newer targets the Azure Cognitive Service for Language APIs. These APIs include the text analysis and natural language processing features found in the previous versions of the Text Analytics client library.
In addition, the service API has changed from semantic to date-based versioning. This version of the client library defaults to the latest supported API version, which currently is `2023-04-01`.

This table shows the relationship between SDK versions and supported API versions of the service

| SDK version  | Supported API version of service  |
| ------------ | --------------------------------- |
| 6.0.0b2 - Latest preview release | 2022-05-01, 2023-04-01, 2024-11-01, 2025-11-01, 2025-11-15-preview (default) |
| 6.0.0b1  | 2022-05-01, 2023-04-01, 2024-11-01, 2025-05-15-preview (default) |
| 5.3.X - Latest stable release | 3.0, 3.1, 2022-05-01, 2023-04-01 (default) |
| 5.2.X  | 3.0, 3.1, 2022-05-01 (default) |
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
from azure.ai.textanalytics import TextAnalysisClient

endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
key = os.environ["AZURE_TEXT_KEY"]

text_client = TextAnalysisClient(endpoint, AzureKeyCredential(key))
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
from azure.ai.textanalytics import TextAnalysisClient
from azure.identity import DefaultAzureCredential

endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
credential = DefaultAzureCredential()

text_client = TextAnalysisClient(endpoint, credential=credential)
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

- [Analyze Sentiment][analyze_sentiment_sample]
- [Recognize Entities][recognize_entities_sample]
- [Recognize Linked Entities][recognize_linked_entities_sample]
- [Recognize PII Entities][recognize_pii_entities_sample]
- [Recognize PII Entities with multiple redaction policies][recognize_pii_entities_with_redaction_policies_sample]
- [Recognize PII Entities with confidence score][recognize_pii_entities_with_confidence_score_sample]
- [Extract Key Phrases][extract_key_phrases_sample]
- [Detect Language][detect_language_sample]
- [Healthcare Entities Analysis][analyze_healthcare_entities_sample]
- [Multiple Analysis][analyze_sample]
- [Custom Entity Recognition][recognize_custom_entities_sample]
- [Custom Single Label Classification][single_label_classify_sample]
- [Custom Multi Label Classification][multi_label_classify_sample]
- [Extractive Summarization][extract_summary_sample]
- [Abstractive Summarization][abstract_summary_sample]

### Analyze Sentiment

[analyze_sentiment][analyze_sentiment] looks at its input text and determines whether its sentiment is positive, negative, neutral or mixed. It's response includes per-sentence sentiment analysis and confidence scores.

<!-- SNIPPET:sample_analyze_sentiment.analyze_sentiment -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextSentimentAnalysisInput,
    AnalyzeTextSentimentResult,
)


def sample_analyze_sentiment():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "The food and service were unacceptable, but the concierge were nice. "
        "After talking to them about the quality of the food and the process to get room service "
        "they refunded the money we spent at the restaurant and gave us a voucher for nearby restaurants."
    )

    body = TextSentimentAnalysisInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextSentimentResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            print(f"Overall sentiment: {doc.sentiment}")
            if doc.confidence_scores:
                print("Confidence scores:")
                print(f"  positive={doc.confidence_scores.positive}")
                print(f"  neutral={doc.confidence_scores.neutral}")
                print(f"  negative={doc.confidence_scores.negative}")

            if doc.sentences:
                print("\nSentence sentiments:")
                for s in doc.sentences:
                    print(f"  Text: {s.text}")
                    print(f"  Sentiment: {s.sentiment}")
                    if s.confidence_scores:
                        print(
                            "  Scores: "
                            f"pos={s.confidence_scores.positive}, "
                            f"neu={s.confidence_scores.neutral}, "
                            f"neg={s.confidence_scores.negative}"
                        )
                    print(f"  Offset: {s.offset}, Length: {s.length}\n")
            else:
                print("No sentence-level results returned.")
    else:
        print("No documents in the response or unexpected result type.")
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[AnalyzeSentimentResult][analyze_sentiment_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [sentiment analysis][sentiment_analysis]. To see how to conduct more granular analysis into the opinions related to individual aspects (such as attributes of a product or service) in a text, see [here][opinion_mining_sample].

### Recognize Entities

[recognize_entities][recognize_entities] recognizes and categories entities in its input text as people, places, organizations, date/time, quantities, percentages, currencies, and more.

<!-- SNIPPET:sample_recognize_entities.recognize_entities -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityRecognitionInput,
    EntitiesActionContent,
    AnalyzeTextEntitiesResult,
)


def sample_recognize_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
        "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
        "amazing. Everyone in my family liked the trail although it was too challenging for the less "
        "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
        "offers services for childcare in case you want that."
    )

    body = TextEntityRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        ),
        action_content=EntitiesActionContent(model_version="latest"),
    )

    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextEntitiesResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.entities:
                print("Entities:")
                for entity in doc.entities:
                    print(f"  Text: {entity.text}")
                    print(f"  Category: {entity.category}")
                    if entity.subcategory:
                        print(f"  Subcategory: {entity.subcategory}")
                    print(f"  Offset: {entity.offset}")
                    print(f"  Length: {entity.length}")
                    print(f"  Confidence score: {entity.confidence_score}\n")
            else:
                print("No entities found for this document.")
    else:
        print("No documents in the response or unexpected result type.")
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

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextEntityLinkingInput,
    EntityLinkingActionContent,
    AnalyzeTextEntityLinkingResult,
)


def sample_recognize_linked_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "Microsoft was founded by Bill Gates with some friends he met at Harvard. One of his friends, Steve "
        "Ballmer, eventually became CEO after Bill Gates as well. Steve Ballmer eventually stepped down as "
        "CEO of Microsoft, and was succeeded by Satya Nadella. Microsoft originally moved its headquarters "
        "to Bellevue, Washington in January 1979, but is now headquartered in Redmond"
    )

    body = TextEntityLinkingInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        ),
        action_content=EntityLinkingActionContent(model_version="latest"),
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextEntityLinkingResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if not doc.entities:
                print("No linked entities found for this document.")
                continue

            print("Linked Entities:")
            for linked in doc.entities:
                print(f"  Name: {linked.name}")
                print(f"  Language: {linked.language}")
                print(f"  Data source: {linked.data_source}")
                print(f"  URL: {linked.url}")
                print(f"  ID: {linked.id}")

                if linked.matches:
                    print("  Matches:")
                    for match in linked.matches:
                        print(f"    Text: {match.text}")
                        print(f"    Confidence score: {match.confidence_score}")
                        print(f"    Offset: {match.offset}")
                        print(f"    Length: {match.length}")
                print()
    else:
        print("No documents in the response or unexpected result type.")
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

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextPiiEntitiesRecognitionInput,
    AnalyzeTextPiiResult,
)


def sample_recognize_pii_entities():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # input
    text_a = (
        "Parker Doe has repaid all of their loans as of 2020-04-25. Their SSN is 859-98-0987. "
        "To contact them, use their phone number 800-102-1100. They are originally from Brazil and "
        "have document ID number 998.214.865-68."
    )

    body = TextPiiEntitiesRecognitionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        )
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Print results
    if isinstance(result, AnalyzeTextPiiResult) and result.results and result.results.documents:
        for doc in result.results.documents:
            print(f"\nDocument ID: {doc.id}")
            if doc.entities:
                print("PII Entities:")
                for entity in doc.entities:
                    print(f"  Text: {entity.text}")
                    print(f"  Category: {entity.category}")
                    # subcategory may be optional
                    if entity.subcategory:
                        print(f"  Subcategory: {entity.subcategory}")
                    print(f"  Offset: {entity.offset}")
                    print(f"  Length: {entity.length}")
                    print(f"  Confidence score: {entity.confidence_score}\n")
            else:
                print("No PII entities found for this document.")
    else:
        print("No documents in the response or unexpected result type.")
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

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    TextKeyPhraseExtractionInput,
    KeyPhraseActionContent,
    AnalyzeTextKeyPhraseResult,
)


def sample_extract_key_phrases():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike! "
        "Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was "
        "amazing. Everyone in my family liked the trail although it was too challenging for the less "
        "athletic among us. Not necessarily recommended for small children. A hotel close to the trail "
        "offers services for childcare in case you want that."
    )

    body = TextKeyPhraseExtractionInput(
        text_input=MultiLanguageTextInput(
            multi_language_inputs=[MultiLanguageInput(id="A", text=text_a, language="en")]
        ),
        action_content=KeyPhraseActionContent(model_version="latest"),
    )

    result = client.analyze_text(body=body)

    # Validate and print results
    if not isinstance(result, AnalyzeTextKeyPhraseResult):
        print("Unexpected result type.")
        return

    if result.results is None:
        print("No results returned.")
        return

    if result.results.documents is None or len(result.results.documents) == 0:
        print("No documents in the response.")
        return

    for doc in result.results.documents:
        print(f"\nDocument ID: {doc.id}")
        if doc.key_phrases:
            print("Key Phrases:")
            for phrase in doc.key_phrases:
                print(f"  - {phrase}")
        else:
            print("No key phrases found for this document.")
```

<!-- END SNIPPET -->

The returned response is a heterogeneous list of result and error objects: list[[ExtractKeyPhrasesResult][extract_key_phrases_result], [DocumentError][document_error]]

Please refer to the service documentation for a conceptual discussion of [key phrase extraction][key_phrase_extraction].

### Detect Language

[detect_language][detect_language] determines the language of its input text, including the confidence score of the predicted language.

<!-- SNIPPET:sample_detect_language.detect_language -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    TextLanguageDetectionInput,
    LanguageDetectionTextInput,
    LanguageInput,
    AnalyzeTextLanguageDetectionResult,
)


def sample_detect_language():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = "Sentences in different languages."

    body = TextLanguageDetectionInput(
        text_input=LanguageDetectionTextInput(language_inputs=[LanguageInput(id="A", text=text_a)])
    )

    # Sync (non-LRO) call
    result = client.analyze_text(body=body)

    # Validate and print results
    if not isinstance(result, AnalyzeTextLanguageDetectionResult):
        print("Unexpected result type.")
        return

    if not result.results or not result.results.documents:
        print("No documents in the response.")
        return

    for doc in result.results.documents:

        print(f"\nDocument ID: {doc.id}")
        if doc.detected_language:
            dl = doc.detected_language
            print(f"Detected language: {dl.name} ({dl.iso6391_name})")
            print(f"Confidence score: {dl.confidence_score}")
        else:
            print("No detected language returned for this document.")
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

from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    AnalyzeTextOperationAction,
    HealthcareLROTask,
    HealthcareLROResult,
)


def sample_analyze_healthcare_entities():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    # Build input
    text_a = "Prescribed 100mg ibuprofen, taken twice daily."

    text_input = MultiLanguageTextInput(
        multi_language_inputs=[
            MultiLanguageInput(id="A", text=text_a, language="en"),
        ]
    )

    actions: list[AnalyzeTextOperationAction] = [
        HealthcareLROTask(
            name="Healthcare Operation",
        ),
    ]

    # Start long-running operation (sync) – poller returns ItemPaged[TextActions]
    poller = client.begin_analyze_text_job(
        text_input=text_input,
        actions=actions,
    )

    # Operation metadata (pre-final)
    print(f"Operation ID: {poller.details.get('operation_id')}")

    # Wait for completion and get pageable of TextActions
    paged_actions = poller.result()

    # Final-state metadata
    d = poller.details
    print(f"Job ID: {d.get('job_id')}")
    print(f"Status: {d.get('status')}")
    print(f"Created: {d.get('created_date_time')}")
    print(f"Last Updated: {d.get('last_updated_date_time')}")
    if d.get("expiration_date_time"):
        print(f"Expires: {d.get('expiration_date_time')}")
    if d.get("display_name"):
        print(f"Display Name: {d.get('display_name')}")

    # Iterate results (sync pageable)
    for actions_page in paged_actions:
        print(
            f"Completed: {actions_page.completed}, "
            f"In Progress: {actions_page.in_progress}, "
            f"Failed: {actions_page.failed}, "
            f"Total: {actions_page.total}"
        )

        for op_result in actions_page.items_property or []:
            if isinstance(op_result, HealthcareLROResult):
                print(f"\nAction Name: {op_result.task_name}")
                print(f"Action Status: {op_result.status}")
                print(f"Kind: {op_result.kind}")

                hc_result = op_result.results
                for doc in hc_result.documents or []:
                    print(f"\nDocument ID: {doc.id}")

                    # Entities
                    print("Entities:")
                    for entity in doc.entities or []:
                        print(f"  Text: {entity.text}")
                        print(f"  Category: {entity.category}")
                        print(f"  Offset: {entity.offset}")
                        print(f"  Length: {entity.length}")
                        print(f"  Confidence score: {entity.confidence_score}")
                        if entity.links:
                            for link in entity.links:
                                print(f"    Link ID: {link.id}")
                                print(f"    Data source: {link.data_source}")
                        print()

                    # Relations
                    print("Relations:")
                    for relation in doc.relations or []:
                        print(f"  Relation type: {relation.relation_type}")
                        for rel_entity in relation.entities or []:
                            print(f"    Role: {rel_entity.role}")
                            print(f"    Ref: {rel_entity.ref}")
                        print()
            else:
                # Other action kinds, if present
                try:
                    print(
                        f"\n[Non-healthcare action] name={op_result.task_name}, "
                        f"status={op_result.status}, kind={op_result.kind}"
                    )
                except Exception:
                    print("\n[Non-healthcare action present]")
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
- Extractive Summarization (API version 2023-04-01 and newer)
- Abstractive Summarization (API version 2023-04-01 and newer)

<!-- SNIPPET:sample_analyze_actions.analyze -->

```python
import os

from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalysisClient
from azure.ai.textanalytics.models import (
    MultiLanguageTextInput,
    MultiLanguageInput,
    EntitiesLROTask,
    KeyPhraseLROTask,
    EntityRecognitionOperationResult,
    KeyPhraseExtractionOperationResult,
    EntityTag,
)


def sample_analyze():
    # get settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    credential = DefaultAzureCredential()

    client = TextAnalysisClient(endpoint, credential=credential)

    text_a = (
        "We love this trail and make the trip every year. The views are breathtaking and well worth the hike!"
        " Yesterday was foggy though, so we missed the spectacular views. We tried again today and it was"
        " amazing. Everyone in my family liked the trail although it was too challenging for the less"
        " athletic among us. Not necessarily recommended for small children. A hotel close to the trail"
        " offers services for childcare in case you want that."
    )

    text_b = "Sentences in different languages."

    text_c = (
        "That was the best day of my life! We went on a 4 day trip where we stayed at Hotel Foo. They had"
        " great amenities that included an indoor pool, a spa, and a bar. The spa offered couples massages"
        " which were really good. The spa was clean and felt very peaceful. Overall the whole experience was"
        " great. We will definitely come back."
    )

    text_d = ""

    # Prepare documents (you can batch multiple docs)
    text_input = MultiLanguageTextInput(
        multi_language_inputs=[
            MultiLanguageInput(id="A", text=text_a, language="en"),
            MultiLanguageInput(id="B", text=text_b, language="es"),
            MultiLanguageInput(id="C", text=text_c, language="en"),
            MultiLanguageInput(id="D", text=text_d),
        ]
    )

    actions = [
        EntitiesLROTask(name="EntitiesOperationActionSample"),
        KeyPhraseLROTask(name="KeyPhraseOperationActionSample"),
    ]

    # Submit a multi-action analysis job (LRO)
    poller = client.begin_analyze_text_job(text_input=text_input, actions=actions)
    paged_actions = poller.result()

    # Iterate through each action's results
    for action_result in paged_actions:
        print()  # spacing between action blocks

        # --- Entities ---
        if isinstance(action_result, EntityRecognitionOperationResult):
            print("=== Entity Recognition Results ===")
            for ent_doc in action_result.results.documents:
                print(f'Result for document with Id = "{ent_doc.id}":')
                print(f"  Recognized {len(ent_doc.entities)} entities:")
                for entity in ent_doc.entities:
                    print(f"    Text: {entity.text}")
                    print(f"    Offset: {entity.offset}")
                    print(f"    Length: {entity.length}")
                    print(f"    Category: {entity.category}")
                    if hasattr(entity, "type") and entity.type is not None:
                        print(f"    Type: {entity.type}")
                    if hasattr(entity, "subcategory") and entity.subcategory:
                        print(f"    Subcategory: {entity.subcategory}")
                    if hasattr(entity, "tags") and entity.tags:
                        print("    Tags:")
                        for tag in entity.tags:
                            if isinstance(tag, EntityTag):
                                print(f"        TagName: {tag.name}")
                                print(f"        TagConfidenceScore: {tag.confidence_score}")
                    print(f"    Confidence score: {entity.confidence_score}")
                    print()
            for err in action_result.results.errors:
                print(f"  Error in document: {err.id}!")
                print(f"  Document error: {err.error}")

        # --- Key Phrases ---
        elif isinstance(action_result, KeyPhraseExtractionOperationResult):
            print("=== Key Phrase Extraction Results ===")
            for kp_doc in action_result.results.documents:
                print(f'Result for document with Id = "{kp_doc.id}":')
                for kp in kp_doc.key_phrases:
                    print(f"    {kp}")
                print()
            for err in action_result.results.errors:
                print(f"  Error in document: {err.id}!")
                print(f"  Document error: {err.error}")
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
- Recognize personally identifiable information(Multiple redaction policies): [sample_recognize_pii_entities_with_redaction_policies.py][recognize_pii_entities_with_redaction_policies_sample] ([async version][recognize_pii_entities_with_redaction_policies_sample_async])
- Recognize personally identifiable information(Confidence score): [sample_recognize_pii_entities_with_confidence_score.py][recognize_pii_entities_with_confidence_score_sample] ([async version][recognize_pii_entities_with_confidence_score_sample_async])
- Recognize linked entities: [sample_recognize_linked_entities.py][recognize_linked_entities_sample] ([async version][recognize_linked_entities_sample_async])
- Extract key phrases: [sample_extract_key_phrases.py][extract_key_phrases_sample] ([async version][extract_key_phrases_sample_async])
- Detect language: [sample_detect_language.py][detect_language_sample] ([async version][detect_language_sample_async])
- Healthcare Entities Analysis: [sample_analyze_healthcare_entities.py][analyze_healthcare_entities_sample] ([async version][analyze_healthcare_entities_sample_async])
- Multiple Analysis: [sample_analyze_actions.py][analyze_sample] ([async version][analyze_sample_async])
- Custom Entity Recognition: [sample_recognize_custom_entities.py][recognize_custom_entities_sample] ([async_version][recognize_custom_entities_sample_async])
- Custom Single Label Classification: [sample_single_label_classify.py][single_label_classify_sample] ([async_version][single_label_classify_sample_async])
- Custom Multi Label Classification: [sample_multi_label_classify.py][multi_label_classify_sample] ([async_version][multi_label_classify_sample_async])
- Extractive text summarization: [sample_extract_summary.py][extract_summary_sample] ([async version][extract_summary_sample_async])
- Abstractive text summarization: [sample_abstract_summary.py][abstract_summary_sample] ([async version][abstract_summary_sample_async])

### Additional documentation

For more extensive documentation on Azure Cognitive Service for Language, see the [Language Service documentation][language_product_documentation] on learn.microsoft.com.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[source_code]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/cognitivelanguage/azure-ai-textanalytics/azure/ai/textanalytics
[ta_pypi]: https://pypi.org/project/azure-ai-textanalytics/
[ta_ref_docs]: https://aka.ms/azsdk-python-textanalytics-ref-docs
[ta_samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples
[language_product_documentation]: https://learn.microsoft.com/azure/cognitive-services/language-service
[azure_subscription]: https://azure.microsoft.com/free/
[ta_or_cs_resource]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[pip]: https://pypi.org/project/pip/
[azure_portal_create_ta_resource]: https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics
[azure_cli]: https://learn.microsoft.com/cli/azure
[azure_cli_create_ta_resource]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account-cli
[multi_and_single_service]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows
[azure_cli_endpoint_lookup]: https://learn.microsoft.com/cli/azure/cognitiveservices/account?view=azure-cli-latest#az-cognitiveservices-account-show
[azure_portal_get_endpoint]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[cognitive_authentication]: https://learn.microsoft.com/azure/cognitive-services/authentication
[cognitive_authentication_api_key]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-apis-create-account?tabs=multiservice%2Cwindows#get-the-keys-for-your-resource
[install_azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity#install-the-package
[register_aad_app]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[grant_role_access]: https://learn.microsoft.com/azure/cognitive-services/authentication#assign-a-role-to-a-service-principal
[cognitive_custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/cognitive-services-custom-subdomains
[custom_subdomain]: https://learn.microsoft.com/azure/cognitive-services/authentication#create-a-resource-with-a-custom-subdomain
[cognitive_authentication_aad]: https://learn.microsoft.com/azure/cognitive-services/authentication#authenticate-with-azure-active-directory
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
[language_detection]: https://learn.microsoft.com/azure/cognitive-services/language-service/language-detection/overview
[language_and_regional_support]: https://learn.microsoft.com/azure/cognitive-services/language-service/language-detection/language-support
[sentiment_analysis]: https://learn.microsoft.com/azure/cognitive-services/language-service/sentiment-opinion-mining/overview
[key_phrase_extraction]: https://learn.microsoft.com/azure/cognitive-services/language-service/key-phrase-extraction/overview
[linked_entities_categories]: https://aka.ms/taner
[linked_entity_recognition]: https://learn.microsoft.com/azure/cognitive-services/language-service/entity-linking/overview
[pii_entity_categories]: https://aka.ms/azsdk/language/pii
[named_entity_recognition]: https://learn.microsoft.com/azure/cognitive-services/language-service/named-entity-recognition/overview
[named_entity_categories]: https://aka.ms/taner
[azure_core_ref_docs]: https://aka.ms/azsdk-python-core-policies
[azure_core]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[python_logging]: https://docs.python.org/3/library/logging.html
[sample_authentication]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_authentication.py
[sample_authentication_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_authentication_async.py
[detect_language_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_detect_language.py
[detect_language_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_detect_language_async.py
[analyze_sentiment_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_analyze_sentiment.py
[analyze_sentiment_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_analyze_sentiment_async.py
[extract_key_phrases_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_extract_key_phrases.py
[extract_key_phrases_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_extract_key_phrases_async.py
[recognize_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_entities.py
[recognize_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_entities_async.py
[recognize_linked_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_linked_entities.py
[recognize_linked_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_linked_entities_async.py
[recognize_pii_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_pii_entities.py
[recognize_pii_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_async.py
[recognize_pii_entities_with_redaction_policies_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_pii_entities_with_redaction_policies.py
[recognize_pii_entities_with_redaction_policies_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_with_redaction_policies_async.py
[recognize_pii_entities_with_confidence_score_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_pii_entities_with_confidence_score.py
[recognize_pii_entities_with_confidence_score_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_pii_entities_with_confidence_score_async.py
[analyze_healthcare_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_analyze_healthcare_entities.py
[analyze_healthcare_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_analyze_healthcare_entities_async.py
[analyze_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_analyze_actions.py
[analyze_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_analyze_actions_async.py
[recognize_custom_entities_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_recognize_custom_entities.py
[recognize_custom_entities_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_recognize_custom_entities_async.py
[single_label_classify_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_single_label_classify.py
[single_label_classify_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_single_label_classify_async.py
[multi_label_classify_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_multi_label_classify.py
[multi_label_classify_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_multi_label_classify_async.py
[healthcare_action_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_analyze_healthcare_action.py
[extract_summary_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_extract_summary.py
[extract_summary_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_extract_summary_async.py
[abstract_summary_sample]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/sample_abstract_summary.py
[abstract_summary_sample_async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/cognitivelanguage/azure-ai-textanalytics/samples/async_samples/sample_abstract_summary_async.py
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com