# Release History

## 1.0.0b2 (2021-10-06)

* We are now targeting service version `2021-07-15-preview`

### Breaking changes

* The method `QuestionAnsweringClient.query_knowledgebase` has been renamed to `query_knowledge_base`.
* Options bag model `KnowledgeBaseQueryOptions` for `query_knowledge_base` is renamed to `QueryKnowledgeBaseOptions`
* Options bag model `TextQueryOptions` for `query_text` is renamed to `QueryTextOptions`
* The filters model `StrictFilters` is renamed to `QueryFilters`
* Enum `CompoundOperationKind` is renamed to `LogicalOperationKind`
* We have removed the `string_index_type` input to all models and operations. We have also removed the `StringIndexType` enum.
* The type of input `metadata` to `MetadataFilter` has changed from a dictionary of strings to a list of key-value tuples. For example, the input has changed from `{"key": "value"}` to `[("key", "value")]`.
* The input to the `query_knowledge_base` and `query_text` overloads that take in a positional model for the body should be considered positional only.

### Features Added

* The method `QuestionAnsweringClient.query_text` now supports a list of records as strings, where the ID value will be automatically populated.
* Added keyword argument `default_language` onto `QuestionAnsweringClient`, which has default value `'en'`. The default language for any operation call will be this default language value.


## 1.0.0b1 (2021-07-27)

### Features Added
* Initial release - supports querying from text records and knowledge bases.
