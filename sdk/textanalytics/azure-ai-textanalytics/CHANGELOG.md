# Release History

## 5.2.0b5 (Unreleased)

### Features Added

- Added `begin_recognize_custom_entities` client method to recognize custom named entities in documents.
- Added `begin_single_label_classify` client method to perform custom single label classification on documents.
- Added `begin_multi_label_classify` client method to perform custom multi label classification on documents.
- Added property `details` on returned poller objects which contain long-running operation metadata.
- Added `TextAnalysisLROPoller` and `AsyncTextAnalysisLROPoller` protocols to describe the return types from long-running operations.
- Added `cancel` method on the poller objects. Call it to cancel a long-running operation that's in progress. 

### Breaking Changes

- Removed the Extractive Text Summarization feature and related models: `ExtractSummaryAction`, `ExtractSummaryResult`, and `SummarySentence`. To access this beta feature, install the `5.2.0b4` version of the client library.
- `SingleCategoryClassifyResult` and `MultiCategoryClassifyResult` models have been merged into one model: `ClassifyDocumentResult`.
- Removed the `FHIR` feature and related keyword argument and property: `fhir_version` and `fhir_bundle`. To access this beta feature, install the `5.2.0b4` version of the client library.
- Renamed `SingleCategoryClassifyAction` to `SingleLabelClassifyAction`
- Renamed `MultiCategoryClassifyAction` to `MultiLabelClassifyAction`.

### Bugs Fixed

### Other Changes

## 5.2.0b4 (2022-05-18)

Note that this is the first version of the client library that targets the Azure Cognitive Service for Language APIs which includes the existing text analysis and natural language processing features found in the Text Analytics client library.
In addition, the service API has changed from semantic to date-based versioning. This version of the client library defaults to the latest supported API version, which currently is `2022-04-01-preview`. Support for `v3.2-preview.2` is removed, however, all functionalities are included in the latest version.

### Features Added

- Added support for Healthcare Entities Analysis through the `begin_analyze_actions` API with the `AnalyzeHealthcareEntitiesAction` type.
- Added keyword argument `fhir_version` to `begin_analyze_healthcare_entities` and `AnalyzeHealthcareEntitiesAction`. Use the keyword to indicate the version for the `fhir_bundle` contained on the `AnalyzeHealthcareEntitiesResult`.
- Added property `fhir_bundle` to `AnalyzeHealthcareEntitiesResult`.
- Added keyword argument `display_name` to `begin_analyze_healthcare_entities`.

## 5.2.0b3 (2022-03-08)

### Bugs Fixed
- `string_index_type` now correctly defaults to the Python default `UnicodeCodePoint` for `AnalyzeSentimentAction` and `RecognizeCustomEntitiesAction`.
- Fixed a bug in `begin_analyze_actions` where incorrect action types were being sent in the request if targeting the older API version `v3.1` in the beta version of the client library.
- `string_index_type` option `Utf16CodePoint` is corrected to `Utf16CodeUnit`.

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 5.2.0b2 (2021-11-02)

This version of the SDK defaults to the latest supported API version, which currently is `v3.2-preview.2`.

### Features Added
- Added support for Custom Entities Recognition through the `begin_analyze_actions` API with the `RecognizeCustomEntitiesAction` and `RecognizeCustomEntitiesResult` types.
- Added support for Custom Single Classification through the `begin_analyze_actions` API with the `SingleCategoryClassifyAction` and `SingleCategoryClassifyActionResult` types.
- Added support for Custom Multi Classification through the `begin_analyze_actions` API with the `MultiCategoryClassifyAction` and `MultiCategoryClassifyActionResult` types.
- Multiple of the same action type is now supported with `begin_analyze_actions`.

### Bugs Fixed
- Restarting a long-running operation from a saved state is now supported for the `begin_analyze_actions` and `begin_recognize_healthcare_entities` methods.
- In the event of an action level error, available partial results are now returned for any successful actions in `begin_analyze_actions`.

### Other Changes
- Package requires [azure-core](https://pypi.org/project/azure-core/) version 1.19.1 or greater

## 5.2.0b1 (2021-08-09)

This version of the SDK defaults to the latest supported API version, which currently is `v3.2-preview.1`.

### Features Added
- Added support for Extractive Summarization actions through the `ExtractSummaryAction` type.

### Bugs Fixed
- `RecognizePiiEntitiesAction` option `disable_service_logs` now correctly defaults to `True`.

### Other Changes
- Python 3.5 is no longer supported.

## 5.1.0 (2021-07-07)

This version of the SDK defaults to the latest supported API version, which currently is `v3.1`.
Includes all changes from `5.1.0b1` to `5.1.0b7`.

Note: this version will be the last to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

### Features Added

- Added `catagories_filter` to `RecognizePiiEntitiesAction`
- Added `HealthcareEntityCategory`
- Added AAD support for the `begin_analyze_healthcare_entities` methods.

### Breaking Changes

- Changed: the response structure of `being_analyze_actions`. Now, we return a list of results, where each result is a list of the action results for the document, in the order the documents and actions were passed.
- Changed: `begin_analyze_actions` now accepts a single action per type. A `ValueError` is raised if duplicate actions are passed.
- Removed: `AnalyzeActionsType`
- Removed: `AnalyzeActionsResult`
- Removed: `AnalyzeActionsError`
- Removed: `HealthcareEntityRelationRoleType`
- Changed: renamed `HealthcareEntityRelationType` to `HealthcareEntityRelation`
- Changed: renamed `PiiEntityCategoryType` to `PiiEntityCategory`
- Changed: renamed `PiiEntityDomainType` to `PiiEntityDomain`

## 5.1.0b7 (2021-05-18)

**Breaking Changes**
- Renamed `begin_analyze_batch_actions` to `begin_analyze_actions`.
- Renamed `AnalyzeBatchActionsType` to `AnalyzeActionsType`.
- Renamed `AnalyzeBatchActionsResult` to `AnalyzeActionsResult`.
- Renamed `AnalyzeBatchActionsError` to `AnalyzeActionsError`.
- Renamed `AnalyzeHealthcareEntitiesResultItem` to `AnalyzeHealthcareEntitiesResult`.
- Fixed `AnalyzeHealthcareEntitiesResult`'s `statistics` to be the correct type, `TextDocumentStatistics`
- Remove `RequestStatistics`, use `TextDocumentBatchStatistics` instead

**New Features**
- Added enums `EntityConditionality`, `EntityCertainty`, and `EntityAssociation`.
- Added `AnalyzeSentimentAction` as a supported action type for `begin_analyze_batch_actions`.
- Added kwarg `disable_service_logs`. If set to true, you opt-out of having your text input logged on the service side for troubleshooting.

## 5.1.0b6 (2021-03-09)

**Breaking Changes**
- By default, we now target the service's `v3.1-preview.4` endpoint through enum value `TextAnalyticsApiVersion.V3_1_PREVIEW`
- Removed property `related_entities` on `HealthcareEntity` and added `entity_relations` onto the document response level for healthcare
- Renamed properties `aspect` and `opinions` to `target` and `assessments` respectively in class `MinedOpinion`.
- Renamed classes `AspectSentiment` and `OpinionSentiment` to `TargetSentiment` and `AssessmentSentiment` respectively.

**New Features**
- Added `RecognizeLinkedEntitiesAction` as a supported action type for `begin_analyze_batch_actions`.
- Added parameter `categories_filter` to the `recognize_pii_entities` client method.
- Added enum `PiiEntityCategoryType`.
- Add property `normalized_text` to `HealthcareEntity`. This property is a normalized version of the `text` property that already
exists on the `HealthcareEntity`
- Add property `assertion` onto `HealthcareEntity`. This contains assertions about the entity itself, i.e. if the entity represents a diagnosis,
is this diagnosis conditional on a symptom?

**Known Issues**

- `begin_analyze_healthcare_entities` is currently in gated preview and can not be used with AAD credentials. For more information, see [the Text Analytics for Health documentation](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-for-health?tabs=ner#request-access-to-the-public-preview).
- At time of this SDK release, the service is not respecting the value passed through `model_version` to `begin_analyze_healthcare_entities`, it only uses the latest model.

## 5.1.0b5 (2021-02-10)

**Breaking Changes**

- Rename `begin_analyze` to `begin_analyze_batch_actions`.
- Now instead of separate parameters for all of the different types of actions you can pass to `begin_analyze_batch_actions`, we accept one parameter `actions`,
which is a list of actions you would like performed. The results of the actions are returned in the same order as when inputted.
- The response object from `begin_analyze_batch_actions` has also changed. Now, after the completion of your long running operation, we return a paged iterable
of action results, in the same order they've been inputted. The actual document results for each action are included under property `document_results` of
each action result.

**New Features**
- Renamed `begin_analyze_healthcare` to `begin_analyze_healthcare_entities`.
- Renamed `AnalyzeHealthcareResult` to `AnalyzeHealthcareEntitiesResult` and `AnalyzeHealthcareResultItem` to `AnalyzeHealthcareEntitiesResultItem`.
- Renamed `HealthcareEntityLink` to `HealthcareEntityDataSource` and renamed its properties `id` to `entity_id` and `data_source` to `name`.
- Removed `relations` from `AnalyzeHealthcareEntitiesResultItem` and added `related_entities` to `HealthcareEntity`.
- Moved the cancellation logic for the Analyze Healthcare Entities service from
the service client to the poller object returned from `begin_analyze_healthcare_entities`.
- Exposed Analyze Healthcare Entities operation metadata on the poller object returned from `begin_analyze_healthcare_entities`.
- No longer need to specify `api_version=TextAnalyticsApiVersion.V3_1_PREVIEW_3` when calling `begin_analyze` and `begin_analyze_healthcare_entities`. `begin_analyze_healthcare_entities` is still in gated preview though.
- Added a new parameter `string_index_type` to the service client methods `begin_analyze_healthcare_entities`, `analyze_sentiment`, `recognize_entities`, `recognize_pii_entities`, and `recognize_linked_entities` which tells the service how to interpret string offsets.
- Added property `length` to `CategorizedEntity`, `SentenceSentiment`, `LinkedEntityMatch`, `AspectSentiment`, `OpinionSentiment`, `PiiEntity` and
`HealthcareEntity`.

## 5.1.0b4 (2021-01-12)

**Bug Fixes**

- Package requires [azure-core](https://pypi.org/project/azure-core/) version 1.8.2 or greater


## 5.1.0b3 (2020-11-19)

**New Features**
- We have added method `begin_analyze`, which supports long-running batch process of Named Entity Recognition, Personally identifiable Information, and Key Phrase Extraction. To use, you must specify `api_version=TextAnalyticsApiVersion.V3_1_PREVIEW_3` when creating your client.
- We have added method `begin_analyze_healthcare`, which supports the service's Health API. Since the Health API is currently only available in a gated preview, you need to have your subscription on the service's allow list, and you must specify `api_version=TextAnalyticsApiVersion.V3_1_PREVIEW_3` when creating your client. Note that since this is a gated preview, AAD is not supported. More information [here](https://docs.microsoft.com/azure/cognitive-services/text-analytics/how-tos/text-analytics-for-health?tabs=ner#request-access-to-the-public-preview).


## 5.1.0b2 (2020-10-06)

**Breaking changes**
- Removed property `length` from `CategorizedEntity`, `SentenceSentiment`, `LinkedEntityMatch`, `AspectSentiment`, `OpinionSentiment`, and `PiiEntity`.
To get the length of the text in these models, just call `len()` on the `text` property.
- When a parameter or endpoint is not compatible with the API version you specify, we will now return a `ValueError` instead of a `NotImplementedError`.
- Client side validation of input is now disabled by default. This means there will be no `ValidationError`s thrown by the client SDK in the case of malformed input. The error will now be thrown by the service through an `HttpResponseError`.

## 5.1.0b1 (2020-09-17)

**New features**
- We are now targeting the service's v3.1-preview API as the default. If you would like to still use version v3.0 of the service,
pass in `v3.0` to the kwarg `api_version` when creating your TextAnalyticsClient
- We have added an API `recognize_pii_entities` which returns entities containing personally identifiable information for a batch of documents. Only available for API version v3.1-preview and up.
- Added `offset` and `length` properties for `CategorizedEntity`, `SentenceSentiment`, and `LinkedEntityMatch`. These properties are only available for API versions v3.1-preview and up.
  - `length` is the number of characters in the text of these models
  - `offset` is the offset of the text from the start of the document
- We now have added support for opinion mining. To use this feature, you need to make sure you are using the service's
v3.1-preview API. To get this support pass `show_opinion_mining` as True when calling the `analyze_sentiment` endpoint
- Add property `bing_entity_search_api_id` to the `LinkedEntity` class. This property is only available for v3.1-preview and up, and it is to be
used in conjunction with the Bing Entity Search API to fetch additional relevant information about the returned entity.

## 5.0.0 (2020-07-27)

- Re-release of GA version 1.0.0 with an updated version

## 1.0.0 (2020-06-09)

- First stable release of the azure-ai-textanalytics package. Targets the service's v3.0 API.

## 1.0.0b6 (2020-05-27)

**New features**
- We now have a `warnings` property on each document-level response object returned from the endpoints. It is a list of `TextAnalyticsWarning`s.
- Added `text` property to `SentenceSentiment`

**Breaking changes**
- Now targets only the service's v3.0 API, instead of the v3.0-preview.1 API
- `score` attribute of `DetectedLanguage` has been renamed to `confidence_score`
- Removed `grapheme_offset` and `grapheme_length` from `CategorizedEntity`, `SentenceSentiment`, and `LinkedEntityMatch`
- `TextDocumentStatistics` attribute `grapheme_count` has been renamed to `character_count`

## 1.0.0b5

- This was a broken release

## 1.0.0b4 (2020-04-07)

**Breaking changes**
- Removed the `recognize_pii_entities` endpoint and all related models (`RecognizePiiEntitiesResult` and `PiiEntity`)
from this library.
- Removed `TextAnalyticsApiKeyCredential` and now using `AzureKeyCredential` from azure.core.credentials as key credential
- `score` attribute has been renamed to `confidence_score` for the `CategorizedEntity`, `LinkedEntityMatch`, and
`PiiEntity` models
- All input parameters `inputs` have been renamed to `documents`

## 1.0.0b3 (2020-03-10)

**Breaking changes**
- `SentimentScorePerLabel` has been renamed to `SentimentConfidenceScores`
- `AnalyzeSentimentResult` and `SentenceSentiment` attribute `sentiment_scores` has been renamed to `confidence_scores`
- `TextDocumentStatistics` attribute `character_count` has been renamed to `grapheme_count`
- `LinkedEntity` attribute `id` has been renamed to `data_source_entity_id`
- Parameters `country_hint` and `language` are now passed as keyword arguments
- The keyword argument `response_hook` has been renamed to `raw_response_hook`
- `length` and `offset` attributes have been renamed to `grapheme_length` and `grapheme_offset` for the `SentenceSentiment`,
`CategorizedEntity`, `PiiEntity`, and `LinkedEntityMatch` models

**New features**
- Pass `country_hint="none"` to not use the default country hint of `"US"`.

**Dependency updates**
- Adopted [azure-core](https://pypi.org/project/azure-core/) version 1.3.0 or greater

## 1.0.0b2 (2020-02-11)

**Breaking changes**

- The single text, module-level operations `single_detect_language()`, `single_recognize_entities()`, `single_extract_key_phrases()`, `single_analyze_sentiment()`, `single_recognize_pii_entities()`, and `single_recognize_linked_entities()`
have been removed from the client library. Use the batching methods for optimal performance in production environments.
- To use an API key as the credential for authenticating the client, a new credential class `TextAnalyticsApiKeyCredential("<api_key>")` must be passed in for the `credential` parameter.
Passing the API key as a string is no longer supported.
- `detect_languages()` is renamed to `detect_language()`.
- The `TextAnalyticsError` model has been simplified to an object with only attributes `code`, `message`, and `target`.
- `NamedEntity` has been renamed to `CategorizedEntity` and its attributes `type` to `category` and `subtype` to `subcategory`.
- `RecognizePiiEntitiesResult` now contains on the object a list of `PiiEntity` instead of `NamedEntity`.
- `AnalyzeSentimentResult` attribute `document_scores` has been renamed to `sentiment_scores`.
- `SentenceSentiment` attribute `sentence_scores` has been renamed to `sentiment_scores`.
- `SentimentConfidenceScorePerLabel` has been renamed to `SentimentScorePerLabel`.
- `DetectLanguageResult` no longer has attribute `detected_languages`. Use `primary_language` to access the detected language in text.

**New features**

- Credential class `TextAnalyticsApiKeyCredential` provides an `update_key()` method which allows you to update the API key for long-lived clients.

**Fixes and improvements**

- `__repr__` has been added to all of the response objects.
- If you try to access a result attribute on a `DocumentError` object, an `AttributeError` is raised with a custom error message that provides the document ID and error of the invalid document.


## 1.0.0b1 (2020-01-09)

Version (1.0.0b1) is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Text Analytics. For more information about this, and preview releases of other Azure SDK libraries, please visit
https://azure.github.io/azure-sdk/releases/latest/python.html.

**Breaking changes: New API design**

- New namespace/package name:
  - The namespace/package name for Azure Text Analytics client library has changed from `azure.cognitiveservices.language.textanalytics` to `azure.ai.textanalytics`

- New operations and naming:
  - `detect_language` is renamed to `detect_languages`
  - `entities` is renamed to `recognize_entities`
  - `key_phrases` is renamed to `extract_key_phrases`
  - `sentiment` is renamed to `analyze_sentiment`
  - New operation `recognize_pii_entities` finds personally identifiable information entities in text
  - New operation `recognize_linked_entities` provides links from a well-known knowledge base for each recognized entity
  - New module-level operations `single_detect_language`, `single_recognize_entities`, `single_extract_key_phrases`, `single_analyze_sentiment`, `single_recognize_pii_entities`, and `single_recognize_linked_entities` perform
  function on a single string instead of a batch of text documents and can be imported from the `azure.ai.textanalytics` namespace.
  - New client and module-level async APIs added to subnamespace `azure.ai.textanalytics.aio`.
  - `MultiLanguageInput` has been renamed to `TextDocumentInput`
  - `LanguageInput` has been renamed to `DetectLanguageInput`
  - `DocumentLanguage` has been renamed to `DetectLanguageResult`
  - `DocumentEntities` has been renamed to `RecognizeEntitiesResult`
  - `DocumentLinkedEntities` has been renamed to `RecognizeLinkedEntitiesResult`
  - `DocumentKeyPhrases` has been renamed to `ExtractKeyPhrasesResult`
  - `DocumentSentiment` has been renamed to `AnalyzeSentimentResult`
  - `DocumentStatistics` has been renamed to `TextDocumentStatistics`
  - `RequestStatistics` has been renamed to `TextDocumentBatchStatistics`
  - `Entity` has been renamed to `NamedEntity`
  - `Match` has been renamed to `LinkedEntityMatch`
  - The batching methods' `documents` parameter has been renamed `inputs`

- New input types:
  - `detect_languages` can take as input a `list[DetectLanguageInput]` or a `list[str]`. A list of dict-like objects in the same shape as `DetectLanguageInput` is still accepted as input.
  - `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment` can take as input a `list[TextDocumentInput]` or `list[str]`.
  A list of dict-like objects in the same shape as `TextDocumentInput` is still accepted as input.

- New parameters/keyword arguments:
  - All operations now take a keyword argument `model_version` which allows the user to specify a string referencing the desired model version to be used for analysis. If no string specified, it will default to the latest, non-preview version.
  - `detect_languages` now takes a parameter `country_hint` which allows you to specify the country hint for the entire batch. Any per-item country hints will take precedence over a whole batch hint.
  - `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment` now take a parameter `language` which allows you to specify the language for the entire batch.
  Any per-item specified language will take precedence over a whole batch hint.
  - A `default_country_hint` or `default_language` keyword argument can be passed at client instantiation to set the default values for all operations.
  - A `response_hook` keyword argument can be passed with a callback to use the raw response from the service. Additionally, values returned for `TextDocumentBatchStatistics` and `model_version` used must be retrieved using a response hook.
  - `show_stats` and `model_version` parameters move to keyword only arguments.

- New return types
  - The return types for the batching methods (`detect_languages`, `recognize_entities`, `recognize_pii_entities`, `recognize_linked_entities`, `extract_key_phrases`, `analyze_sentiment`) now return a heterogeneous list of
  result objects and document errors in the order passed in with the request. To iterate over the list and filter for result or error, a boolean property on each object called `is_error` can be used to determine whether the returned response object at
  that index is a result or an error:
  - `detect_languages` now returns a List[Union[`DetectLanguageResult`, `DocumentError`]]
  - `recognize_entities` now returns a List[Union[`RecognizeEntitiesResult`, `DocumentError`]]
  - `recognize_pii_entities` now returns a List[Union[`RecognizePiiEntitiesResult`, `DocumentError`]]
  - `recognize_linked_entities` now returns a List[Union[`RecognizeLinkedEntitiesResult`, `DocumentError`]]
  - `extract_key_phrases` now returns a List[Union[`ExtractKeyPhrasesResult`, `DocumentError`]]
  - `analyze_sentiment` now returns a List[Union[`AnalyzeSentimentResult`, `DocumentError`]]
  - The module-level, single text operations will return a single result object or raise the error found on the document:
  - `single_detect_languages` returns a `DetectLanguageResult`
  - `single_recognize_entities` returns a `RecognizeEntitiesResult`
  - `single_recognize_pii_entities` returns a `RecognizePiiEntitiesResult`
  - `single_recognize_linked_entities` returns a `RecognizeLinkedEntitiesResult`
  - `single_extract_key_phrases` returns a `ExtractKeyPhrasesResult`
  - `single_analyze_sentiment` returns a `AnalyzeSentimentResult`

- New underlying REST pipeline implementation, based on the new `azure-core` library.
- Client and pipeline configuration is now available via keyword arguments at both the client level, and per-operation. See README for a full list of optional configuration arguments.
- Authentication using `azure-identity` credentials
  - see the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information
- New error hierarchy:
    - All service errors will now use the base type: `azure.core.exceptions.HttpResponseError`
    - There is one exception type derived from this base type for authentication errors:
        - `ClientAuthenticationError`: Authentication failed.

## 0.2.0 (2019-03-12)

**Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance
- New method "entities"
- Model KeyPhraseBatchResultItem has a new parameter statistics
- Model KeyPhraseBatchResult has a new parameter statistics
- Model LanguageBatchResult has a new parameter statistics
- Model LanguageBatchResultItem has a new parameter statistics
- Model SentimentBatchResult has a new parameter statistics

**Breaking changes**

- TextAnalyticsAPI main client has been renamed TextAnalyticsClient
- TextAnalyticsClient parameter is no longer a region but a complete endpoint

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be preferred.

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0


## 0.1.0 (2018-01-12)

* Initial Release
