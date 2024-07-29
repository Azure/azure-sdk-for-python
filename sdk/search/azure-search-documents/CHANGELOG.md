# Release History

## 11.5.1 (2024-07-30)

### Other Changes

- Improved type checks.

## 11.5.0 (2024-07-16)

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.4.0.
> Only code written against a beta version such as 11.6.0b4 may be affected.

- Below models are renamed
  - `azure.search.documents.indexes.models.SearchIndexerIndexProjections` -> `azure.search.documents.indexes.models.SearchIndexerIndexProjection`
  - `azure.search.documents.indexes.models.LineEnding` -> `azure.search.documents.indexes.models.OrcLineEnding`
  - `azure.search.documents.indexes.models.ScalarQuantizationCompressionConfiguration` -> `azure.search.documents.indexes.models.ScalarQuantizationCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionConfiguration` -> `azure.search.documents.indexes.models.VectorSearchCompression`
  - `azure.search.documents.indexes.models.VectorSearchCompressionTargetDataType` -> `azure.search.documents.indexes.models.VectorSearchCompressionTarget`

- Below models do not exist in this release
  - `azure.search.documents.models.QueryLanguage`
  - `azure.search.documents.models.QuerySpellerType`
  - `azure.search.documents.models.QueryDebugMode`
  - `azure.search.documents.models.HybridCountAndFacetMode`
  - `azure.search.documents.models.HybridSearch`
  - `azure.search.documents.models.SearchScoreThreshold`
  - `azure.search.documents.models.VectorSimilarityThreshold`
  - `azure.search.documents.models.VectorThreshold`
  - `azure.search.documents.models.VectorThresholdKind`
  - `azure.search.documents.models.VectorizableImageBinaryQuery`
  - `azure.search.documents.models.VectorizableImageUrlQuery`
  - `azure.search.documents.indexes.models.SearchAlias`
  - `azure.search.documents.indexes.models.AIServicesVisionParameters`
  - `azure.search.documents.indexes.models.AIServicesVisionVectorizer`
  - `azure.search.documents.indexes.models.AIStudioModelCatalogName`
  - `azure.search.documents.indexes.models.AzureMachineLearningParameters`
  - `azure.search.documents.indexes.models.AzureMachineLearningSkill`
  - `azure.search.documents.indexes.models.AzureMachineLearningVectorizer`
  - `azure.search.documents.indexes.models.CustomVectorizer`
  - `azure.search.documents.indexes.models.CustomNormalizer`
  - `azure.search.documents.indexes.models.DocumentKeysOrIds`
  - `azure.search.documents.indexes.models.IndexingMode`
  - `azure.search.documents.indexes.models.LexicalNormalizer`
  - `azure.search.documents.indexes.models.LexicalNormalizerName`
  - `azure.search.documents.indexes.models.NativeBlobSoftDeleteDeletionDetectionPolicy`
  - `azure.search.documents.indexes.models.SearchIndexerCache`
  - `azure.search.documents.indexes.models.SkillNames`
  - `azure.search.documents.indexes.models.VisionVectorizeSkill`

- SearchAlias operations do not exist in this release
- `SearchIndexerClient.reset_documents` does not exist in this release
- `SearchIndexerClient.reset_skills` does not exist in this release

- Below properties do not exist
  - `azure.search.documents.indexes.models.SearchIndexerDataSourceConnection.identity`
  - `azure.search.documents.indexes.models.SearchIndex.normalizers`
  - `azure.search.documents.indexes.models.SearchField.normalizer_name`

- Below parameters do not exist
  - `SearchClient.search.debug`
  - `SearchClient.search.hybrid_search`
  - `SearchClient.search.query_language`
  - `SearchClient.search.query_speller`
  - `SearchClient.search.semantic_fields`
  - `SearchIndexerClient.create_or_update_indexer.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_data_source_connection.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_skillset.skip_indexer_reset_requirement_for_cache`
  - `SearchIndexerClient.create_or_update_indexer.disable_cache_reprocessing_change_detection`
  - `SearchIndexerClient.create_or_update_skillset.disable_cache_reprocessing_change_detection`

### Other Changes

- Updated default API version to `2024-07-01`.

## 11.6.0b4 (2024-05-07)

### Features Added

- Added new models:
  - `azure.search.documents.models.HybridCountAndFacetMode`
  - `azure.search.documents.models.HybridSearch`
  - `azure.search.documents.models.SearchScoreThreshold`
  - `azure.search.documents.models.VectorSimilarityThreshold`
  - `azure.search.documents.models.VectorThreshold`
  - `azure.search.documents.models.VectorThresholdKind`
  - `azure.search.documents.models.VectorizableImageBinaryQuery`
  - `azure.search.documents.models.VectorizableImageUrlQuery`
  - `azure.search.documents.indexes.models.AIServicesVisionParameters`
  - `azure.search.documents.indexes.models.AIServicesVisionVectorizer`
  - `azure.search.documents.indexes.models.AIStudioModelCatalogName`
  - `azure.search.documents.indexes.models.AzureMachineLearningParameters`
  - `azure.search.documents.indexes.models.AzureMachineLearningVectorizer`
  - `azure.search.documents.indexes.models.AzureOpenAIModelName`
  - `azure.search.documents.indexes.models.VectorEncodingFormat`
  - `azure.search.documents.indexes.models.VisionVectorizeSkill`
- Added `hybrid_search` support for `SearchClient.search` method.
- Updated default API version to `2024-05-01-preview`.

### Bugs Fixed

- Fixed the bug that SearchClient failed when both answer count and answer threshold applied.

## 11.6.0b3 (2024-04-09)

### Features Added

- Added `IndexerExecutionEnvironment`, `IndexingMode`, `LineEnding`, `NativeBlobSoftDeleteDeletionDetectionPolicy`, `ScalarQuantizationCompressionConfiguration`, `ScalarQuantizationParameters`, `SearchServiceCounters`, `SearchServiceLimits`, `SearchServiceStatistics`, `VectorSearchCompressionConfiguration` & `VectorSearchCompressionTargetDataType`.
- Added `stored` in `SearchField`.

## 11.6.0b2 (2024-03-05)

### Breaking Changes

- `SearchIndexerSkillset`, `SearchField`, `SearchIndex`, `AnalyzeTextOptions`, `SearchResourceEncryptionKey`, `SynonymMap`, `SearchIndexerDataSourceConnection` are no longer subclasses of `_serialization.Model`.

### Bugs Fixed

- Fixed the issue that `SearchIndexerSkillset`, `SearchField`, `SearchIndex`, `AnalyzeTextOptions`, `SearchResourceEncryptionKey`, `SynonymMap`, `SearchIndexerDataSourceConnection` could not be serialized and `as_dict` did not work.
- Fixed the issue that `context` was missing for `EntityRecognitionSkill` and `SentimentSkill`. #34623

### Other Changes

- Default to API version `V2024_03_01_PREVIEW`

## 11.6.0b1 (2024-01-31)

### Features Added

- Added back `semantic_query` for `Search` method.
- Added back alias operations to `SearchIndexClient`.
- Added back `AzureOpenAIEmbeddingSkill`, `AzureOpenAIParameters` and `AzureOpenAIVectorizer`.
- Added back `query_language`, `query_speller`, `semantic_fields` and `debug` for `Search` method.
- Added `send_request` method for `SearchClient` & `SearchIndexClient` to run a network request using the client's existing pipeline.

### Bugs Fixed

- Fixed the issue that we added unexpected `retrievable` property for `SearchField`.

### Other Changes

- Python 3.7 is no longer supported. Please use Python version 3.8 or later.

## 11.4.0 (2023-10-13)

### Features Added

- Added new models:
  - `VectorSearchAlgorithmMetric`
  - `IndexProjectionMode`
  - `SearchIndexerIndexProjections`
  - `SearchIndexerIndexProjectionSelector`
  - `SearchIndexerIndexProjectionsParameters`
  - `BlobIndexerDataToExtract`
  - `BlobIndexerImageAction`
  - `BlobIndexerParsingMode`
  - `CharFilterName`
  - `CustomEntity`
  - `CustomEntityAlias`
  - `DataChangeDetectionPolicy`
  - `DataDeletionDetectionPolicy`
  - `DefaultCognitiveServicesAccount`
  - `HighWaterMarkChangeDetectionPolicy`
  - `HnswAlgorithmConfiguration`
  - `IndexerExecutionResult`
  - `IndexingParameters`
  - `IndexingParametersConfiguration`
  - `IndexingSchedule`
  - `LexicalAnalyzerName`
  - `LexicalTokenizerName`
  - `PIIDetectionSkill`
  - `PIIDetectionSkillMaskingMode`
  - `ScoringProfile`
  - `SemanticSearch`
- Added `index_projections` support for `SearchIndexerSkillset`

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b11 may be affected.

- Renamed `AnswerResult` to `QueryAnswerResult` and `CaptionResult` to `QueryCaptionResult`.
- Renamed `SemanticErrorHandling` to `SemanticErrorMode`.
- Renamed `RawVectorQuery` to `VectorizedQuery`.
- Renamed `ExhaustiveKnnVectorSearchAlgorithmConfiguration` to `ExhaustiveKnnAlgorithmConfiguration`.
- Renamed `PrioritizedFields` to `SemanticPrioritizedFields`.
- Renamed `query_caption_highlight` to `query_caption_highlight_enabled`.
- `query_language` and `query_speller` are not available for `Search` method in this stable release.
- `alias` operations are not available in this stable release.
- `AzureOpenAIEmbeddingSkill`, `AzureOpenAIParameters` and `AzureOpenAIVectorizer` are not available in 11.4.0.
- Renamed `vector_search_profile` to `vector_search_profile_name` in `SearchField`.
- Renamed `SemanticSettings` to `SemanticSearch`.

### Other Changes

- Used API version "2023-11-01".

## 11.4.0b11 (2023-10-11)

### Features Added

- Added `vector_filter_mode` support for `Search` method.
- Exposed `VectorizableTextQuery` in `azure.search.document.models`.

## 11.4.0b10 (2023-10-10)

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Renamed `vector_search_configuration` to `vector_search_profile` in `SearchField`.
- Renamed `vectors` to `vector_queries` in `Search` method.
- Renamed `azure.search.documents.models.Vector` to `azure.search.documents.models.VectorQuery`.
- Stopped supporting api version `V2023_07_01_PREVIEW` anymore.

### Other Changes

- Default to use API version `V2023_10_01_PREVIEW`

## 11.4.0b9 (2023-09-12)

### Bugs Fixed

- Fixed the bug that list type of `order_by` was not correctly handled. #31837

## 11.4.0b8 (2023-08-08)

### Features Added

- Exposed `HnswVectorSearchAlgorithmConfiguration`

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Instead of using `VectorSearchAlgorithmConfiguration`, now you need to use concrete types like `HnswVectorSearchAlgorithmConfiguration`.

## 11.4.0b7 (2023-08-08)

### Features Added

- Added multi-vector search support. Now instead of passing in `vector`, `top_k` and `vector_fields`, search method accepts `vectors` which is a list of `Vector` object.

### Breaking Changes

> These changes do not impact the API of stable versions such as 11.3.0.
> Only code written against a beta version such as 11.4.0b6 may be affected.
- Stopped supporting `vector`, `top_k` and `vector_fields` in `SearchClient.search` method.

## 11.4.0b6 (2023-07-11)

### Features Added

- Added `top_k` support for `VectorSearch`.

## 11.4.0b5 (2023-07-11)

### Features Added

- Exposed `azure.search.documents.models.Vector`.

## 11.4.0b4 (2023-07-11)

### Features Added

- Added `VectorSearch` support.

### Breaking Changes

- Deprecated `SentimentSkillV1` and `EntityRecognitionSkillV1`.

## 11.4.0b3 (2023-02-07)

### Features Added

- Added the semantic reranker score and captions on `SearchResult`.(thanks to @LucasVascovici for the contribution)

## 11.4.0b2 (2022-11-08)

### Features Added

- Enabled `OcrSkill` and `ImageAnalysisSkill`

### Other Changes

- Added Python 3.11 support.

## 11.4.0b1 (2022-09-08)

### Features Added

- Added support to create, update and delete aliases via the `SearchIndexClient`.

## 11.3.0 (2022-09-06)

### Note

- Some of the features that were available in the `11.3.0b8` version are not available in this GA. They would be available in the upcoming beta release.

### Features Added

- Added support for other national clouds.
- Added support for TokenCredential

### Bugs Fixed

- Fixed issue where async `search` call would fail with a 403 error when retrieving large number of documents.

### Other Changes

- Python 3.6 is no longer supported. Please use Python version 3.7 or later.

## 11.2.2 (2022-04-14)

### Bugs Fixed

- Fixes a bug allowing users to set keys for cognitive service skills using the API. Exposes `DefaultCognitiveServicesAccount` and `CognitiveServicesAccountKey`

## 11.3.0b8 (2022-03-08)

### Features Added

- Added support to create, update and delete aliases via the `SearchIndexClient`.

## 11.3.0b7 (2022-02-08)

### Features Added

- Support for [`AzureMachineLearningSkill`](https://docs.microsoft.com/azure/search/cognitive-search-aml-skill). The AML skill allows you to extend AI enrichment with a custom [Azure Machine Learning](https://docs.microsoft.com/azure/machine-learning/overview-what-is-azure-machine-learning) (AML) model. Once an AML model is [trained and deployed](https://docs.microsoft.com/azure/machine-learning/concept-azure-machine-learning-architecture#workspace), an AML skill integrates it into AI enrichment.

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 11.2.1 (2022-01-10)

Minor updates.

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
