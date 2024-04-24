# Guide for migrating to azure-ai-textanalytics v5.x.x from azure-cognitiveservices-language-textanalytics v0.2.1

This guide is intended to assist in the migration to azure-ai-textanalytics v5.x.x from azure-cognitiveservices-language-textanalytics v0.2.1.

It will focus on side-by-side comparisons for similar operations between the two packages.

Familiarity with the `azure-cognitiveservices-language-textanalytics` v0.2.1 package is assumed.
For those new to the Azure Text Analytics library for Python, please refer to the [README for `azure-ai-textanalytics`](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/README.md) rather than this guide.

## Table of contents

* [Migration benefits](#migration-benefits)
  * [New Features](#new-features)
* [Important changes](#important-changes)
  * [Detect Language](#detect-language)
  * [Recognize Entities](#recognize-entities)
  * [Extract Key Phrases](#extract-key-phrases)
  * [Analyze Sentiment](#analyze-sentiment)
* [Samples](#samples)

## Migration benefits

A natural question to ask when considering whether or not to adopt a new version or library is what
the benefits of doing so would be. As Azure has matured and been embraced by a more diverse group of developers,
we have been focused on learning the patterns and practices to best support developer productivity and
to understand the gaps that the Python client libraries have.

There were several areas of consistent feedback expressed across the Azure client library ecosystem.
One of the most important is that the client libraries for different Azure services have not had a
consistent approach to organization, naming, and API structure. Additionally, many developers have felt
that the learning curve was difficult, and the APIs did not offer a good, approachable,
and consistent onboarding story for those learning Azure or exploring a specific Azure service.

To try and improve the development experience across Azure services,
a set of uniform [design guidelines](https://azure.github.io/azure-sdk/general_introduction.html) was created
for all languages to drive a consistent experience with established API patterns for all services.
A set of [Python-specific guidelines](https://azure.github.io/azure-sdk/python/guidelines/index.html) was also introduced to ensure
that Python clients have a natural and idiomatic feel with respect to the Python ecosystem.
Further details are available in the guidelines for those interested.

### New Features

We have a variety of new features in the version v5.x.x of the AI Language Text Analytics library, in addition to existing features. The client provides functionality for:
  - Sentiment Analysis
  - Entity Recognition
  - Personally Identifiable Information Recognition
  - Linked Entity Recognition
  - Key Phrase Extraction
  - Language Detection
  - Healthcare Entities Analysis
  - Multiple Analysis
  - Custom Entity Recognition
  - Custom Single Label Classification
  - Custom Multi Label Classification
  - Extractive Text Summarization
  - Abstractive Text Summarization

Refer to the [CHANGELOG.md](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/textanalytics/azure-ai-textanalytics/CHANGELOG.md) for more new features, changes, and bug fixes.

## Important changes

For all previously existing methods on the TextAnalyticsClient, the following changes have been made:
 - The `custom_headers` optional parameter has been replaced by `headers`.
 - Optional parameter `raw` has been removed.
 - `operation_config` is now `kwargs`.
 - For information on additional optional arguments to each method, please refer to the [API reference documentation](https://aka.ms/azsdk-python-textanalytics-ref-docs).

More specific changes are listed below.

### Detect Language

The following changes have been made to the `detect_language` method:
 - The `documents` parameter now takes arguments of type `List[str]`, `List[Dict[str, str]]`, or `List[DetectLanguageInput]`, where the `DetectLanguageResult` model has been renamed from `LanguageInput`.
 - The returned value will be a list of `DetectLanguageResult` or `DocumentError` models, instead of `LanguageBatchResult`.

### Recognize Entities

The `entities` method has been renamed to `recognize_entities`. Other changes:
 - The `documents` parameter now takes arguments of type `List[str]`, `List[Dict[str, str]]`, or `List[TextDocumentInput]`, where the `TextDocumentInput` model has been renamed from `MultiLanguageInput`.
 - The returned value will be a list of `RecognizeEntitiesResult` or `DocumentError` models, instead of `EntitiesBatchResult`.

Separate methods have been added on the TextAnalyticsClient to recognize entities containing personal information in a batch of documents, `recognize_pii_entities`, and to recognize linked entities from a well-known knowledge base for a batch of documents, `recognize_linked_entities`.

### Extract Key Phrases

The `key_phrases` method has been renamed to `extract_key_phrases`. Other changes:
 - The `documents` parameter now takes arguments of type `List[str]`, `List[Dict[str, str]]`, or `List[TextDocumentInput]`, where the `TextDocumentInput` model has been renamed from `MultiLanguageInput`.
 - The returned value will be a list of `ExtractKeyPhrasesResult` or `DocumentError` models, instead of `KeyPhraseBatchResult`.

### Analyze Sentiment

The `sentiment` method has been renamed to `analyze_sentiment`. Other changes:
 - The `documents` parameter now takes arguments of type `List[str]`, `List[Dict[str, str]]`, or `List[TextDocumentInput]`, where the `TextDocumentInput` model has been renamed from `MultiLanguageInput`.
 - The returned value will be a list of `AnalyzeSentimentResult` or `DocumentError` models, instead of `SentimentBatchResult`.

## Samples

Usage examples can be found at [Samples for azure-ai-textanalytics](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/textanalytics/azure-ai-textanalytics/samples).
