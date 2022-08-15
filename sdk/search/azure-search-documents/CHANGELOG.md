# Release History

## 11.3.0b9 (Unreleased)

### Features Added
- Added support for other national clouds.

### Breaking Changes

### Bugs Fixed
- Fixed issue where async `search` call would fail with a 403 error when retrieving large number of documents.

### Other Changes

## 11.3.0b8 (2022-03-08)

### Features Added
- Added support to create, update and delete aliases via the `SearchIndexClient`.

## 11.3.0b7 (2022-02-08)

### Features Added

- Support for [`AzureMachineLearningSkill`](https://docs.microsoft.com/azure/search/cognitive-search-aml-skill). The AML skill allows you to extend AI enrichment with a custom [Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning/overview-what-is-azure-machine-learning) (AML) model. Once an AML model is [trained and deployed](https://docs.microsoft.com/azure/machine-learning/concept-azure-machine-learning-architecture#workspace), an AML skill integrates it into AI enrichment.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 11.3.0b6 (2021-11-19)

### Features Added

- Added properties to `SearchClient.search`: `semantic_configuration_name`
- Added properties to `SearchIndex`: `semantic_settings`
- Added models: `PrioritizedFields`, `SemanticConfiguration`, `SemanticField`, `SemanticSettings`
- Added new values to model `QueryLanguage`

## 11.3.0b5 (2021-11-09)

### Features Added

- Added properties to `SearchClient.search`: `session_id`, `scoring_statistics`.
- Added properties to `SearchIndexerDataSourceConnection`: `identity`, `encryption_key`.
- Added `select` property to the following `SearchIndexClient` operations: `get_synonym_maps`, `list_indexes`.
- Added `select` property to the following `SearchIndexersClient` operations: `get_data_source_connections`, `get_indexers`, `get_skillsets`.
- Added operations to `SearchIndexerClient`: `reset_skills`, `reset_documents`.
- Added model: `DocumentKeysOrIds`

## 11.3.0b4 (2021-10-05)

### Features Added

- Added properties to `SearchClient`: `query_answer`, `query_answer_count`,
  `query_caption`, `query_caption_highlight` and `semantic_fields`.

### Breaking Changes

- Renamed `SearchClient.speller` to `SearchClient.query_speller`.
- Renamed model `Speller` to `QuerySpellerType`.
- Renamed model `Answers` to `QueryAnswerType`. 
- Removed keyword arguments from `SearchClient`: `answers` and `captions`.
- `SentimentSkill`, `EntityRecognitionSkill`: added client-side validation to prevent sending unsupported parameters.
- Renamed property `ignore_reset_requirements` to `skip_indexer_reset_requirement_for_cache`.

## 11.3.0b3 (2021-09-08)

### Features Added

- Added new models: 
  - `azure.search.documents.models.QueryCaptionType`
  - `azure.search.documents.models.CaptionResult`
  - `azure.search.documents.indexes.models.CustomEntityLookupSkillLanguage`
  - `azure.search.documents.indexes.models.EntityRecognitionSkillVersion`
  - `azure.search.documents.indexes.models.LexicalNormalizerName`
  - `azure.search.documents.indexes.models.PIIDetectionSkill`
  - `azure.search.documents.indexes.models.PIIDetectionSkillMaskingMode`
  - `azure.search.documents.indexes.models.SearchIndexerCache`
  - `azure.search.documents.indexes.models.SearchIndexerDataIdentity`
  - `azure.search.documents.indexes.models.SearchIndexerDataNoneIdentity`
  - `azure.search.documents.indexes.models.SearchIndexerDataUserAssignedIdentity`
  - `azure.search.documents.indexes.models.SentimentSkillVersion`
- Added `normalizer_name` property to `AnalyzeTextOptions` model.

### Breaking Changes

- Removed:
  - `azure.search.documents.indexes.models.SentimentSkillV3`
  - `azure.search.documents.indexes.models.EntityRecognitionSkillV3`
- Renamed:
  - `SearchField.normalizer` renamed to `SearchField.normalizer_name`.

### Other Changes
- `SentimentSkill` and `EntityRecognitionSkill` can now be created by specifying
  the `skill_version` keyword argument with a `SentimentSkillVersion` or
  `EntityRecognitionSkillVersion`, respectively. The default behavior if `skill_version`
  is not specified is to create a version 1 skill.

## 11.3.0b2 (2021-08-10)

### Features Added

- Added new skills: `SentimentSkillV3`, `EntityLinkingSkill`, `EntityRecognitionSkillV3`

## 11.3.0b1 (2021-07-07)

### Features Added

- Added AAD support
- Added support for semantic search
- Added normalizer support

## 11.2.0 (2021-06-08)

This version will be the last version to officially support Python 3.5, future versions will require Python 2.7 or Python 3.6+.

**New features**

- Added support for knowledge store    #18461
- Added new data source type ADLS gen2  #16852

## 11.1.0 (2021-02-10)

**Breaking Changes**

- `IndexDocumentsBatch` does not support `enqueue_action` any longer. `enqueue_actions` takes a single action too.
- `max_retries` of `SearchIndexingBufferedSender` is renamed to `max_retries_per_action`
- `SearchClient` does not support `get_search_indexing_buffered_sender`

## 11.1.0b4 (2020-11-10)

**Features**

- Added `get_search_indexing_buffered_sender` support for `SearchClient`
- Added `initial_batch_action_count` support for `SearchIndexingBufferedSender`
- Added `max_retries` support for `SearchIndexingBufferedSender`

## 11.1.0b3 (2020-10-06)

**Breaking Changes**

- Renamed `SearchIndexDocumentBatchingClient` to `SearchIndexingBufferedSender`
- Renamed `SearchIndexDocumentBatchingClient.add_upload_actions` to `SearchIndexingBufferedSender.upload_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_delete_actions` to `SearchIndexingBufferedSender.delete_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_merge_actions` to `SearchIndexingBufferedSender.merge_documents`
- Renamed `SearchIndexDocumentBatchingClient.add_merge_or_upload_actions` to `SearchIndexingBufferedSender.merge_or_upload_documents`
- Stopped supporting `window` kwargs for `SearchIndexingBufferedSender`
- Splitted kwarg `hook` into `on_new`, `on_progress`, `on_error`, `on_remove` for `SearchIndexingBufferedSender`

**Features**

- Added `auto_flush_interval` support for `SearchIndexingBufferedSender`

## 11.1.0b2 (2020-09-08)

**Features**

- Added `azure.search.documents.RequestEntityTooLargeError`
- `Flush` method in `BatchClient` now will not return until all actions are done

**Breaking Changes**

- Removed `succeeded_actions` & `failed_actions` from `BatchClient`
- Removed `get_index_document_batching_client` from `SearchClient`

## 11.1.0b1 (2020-08-11)

**Features**

- new `SearchIndexDocumentBatchingClient`

`SearchIndexDocumentBatchingClient` supports handling document indexing actions in an automatic way. It can trigger the flush method automatically based on pending tasks and idle time.

### Fixes

- Doc & Sample fixes

## 11.0.0 (2020-07-07)

**Features**

- Exposed more models:

  * BM25SimilarityAlgorithm
  * ClassicSimilarityAlgorithm
  * EdgeNGramTokenFilterSide
  * EntityCategory
  * EntityRecognitionSkillLanguage
  * FieldMapping
  * FieldMappingFunction
  * ImageAnalysisSkillLanguage
  * ImageDetail
  * IndexerExecutionStatus
  * IndexerStatus
  * KeyPhraseExtractionSkillLanguage
  * MicrosoftStemmingTokenizerLanguage
  * MicrosoftTokenizerLanguage
  * OcrSkillLanguage
  * PhoneticEncoder
  * ScoringFunctionAggregation
  * ScoringFunctionInterpolation

## 1.0.0b4 (2020-06-09)

**Breaking Changes**

- Reorganized `SearchServiceClient` into `SearchIndexClient` & `SearchIndexerClient`    #11507
- Split searchindex.json and searchservice.json models and operations into separate namespaces #11508
- Renamed `edm` to `SearchFieldDataType`    #11511
- Now Search Synonym Map creation/update returns a model    #11514
- Renaming  #11565

  * SearchIndexerDataSource -> SearchIndexerDataSourceConnection
  * SearchField.SynonymMaps -> SearchField.SynonymMapNames
  * SearchField.Analyzer -> SearchField.AnalyzerName
  * SearchField.IndexAnalyzer -> SearchField.IndexAnalyzerName
  * SearchField.SearchAnalyzer -> SearchField.SearchAnalyzerName
  * SearchableField.SynonymMaps -> SearchableField.SynonymMapNames
  * SearchableField.Analyzer -> SearchableField.AnalyzerName
  * SearchableField.IndexAnalyzer -> SearchableField.IndexAnalyzerName
  * SearchableField.SearchAnalyzer -> SearchableField.SearchAnalyzerName
  * Similarity -> SimilarityAlgorithm
  * Suggester -> SearchSuggester
  * PathHierarchyTokenizerV2 -> PathHierarchyTokenizer
- Renamed DataSource methods to DataSourceConnection    #11693
- Autocomplete & suggest methods now takes arguments search_text & suggester_name rather than query objects   #11747
- Create_or_updates methods does not support partial updates    #11800
- Renamed AnalyzeRequest to AnalyzeTextOptions  #11800
- Renamed Batch methods #11800
  

## 1.0.0b3 (2020-05-04)

**Features**

- Add support for synonym maps operations #10830
- Add support for skillset operations #10832
- Add support of indexers operation #10836
- Add helpers for defining searchindex fields #10833

**Breaking Changes**

- `SearchIndexClient` renamed to `SearchClient`

## 1.0.0b2 (2020-04-07)

**Features**

- Added index service client    #10324
- Accepted an array of RegexFlags for PatternAnalyzer and PatternTokenizer  #10409

**Breaking Changes**

- Removed `SearchApiKeyCredential` and now using `AzureKeyCredential` from azure.core.credentials as key credential

## 1.0.0b1 (2020-03-10)

First release of Azure Search SDK for Python
