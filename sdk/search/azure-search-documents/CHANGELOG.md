# Release History

## 11.1.1 (Unreleased)


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
