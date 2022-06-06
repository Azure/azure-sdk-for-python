# Release History

## 1.1.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes
* Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.1.0b1 (2022-02-08)

### Features Added
* Added `QuestionAnsweringProjectsClient` for managing Qna projects. Performing project operations such as create, delete, export, and import project, as well as knowledge sources operations such as adding or listing knowledge sources, Qnas, and synonyms.

## 1.0.0 (2021-11-03)

* We are now targeting service version `2021-10-01`

### Breaking Changes

* Method `QuestionAnsweringClient.query_knowledge_base` has been renamed to `get_answers`
* Method `QuestionAnsweringClient.query_text` has been renamed to `get_answers_from_text`
* Model `QueryKnowledgeBaseOptions` has been renamed to `AnswersOptions`
* Method kwarg and model property `QueryKnowledgeBaseOptions.confidence_score_threshold` has been renamed to  `AnswersOptions.confidence_threshold`
* Method kwarg and model property `QueryKnowledgeBaseOptions.answer_span_request` has been renamed to  `AnswersOptions.short_answer_options`
* Method kwarg and model property `QueryKnowledgeBaseOptions.ranker_type` has been renamed to  `AnswersOptions.ranker_kind`
* Method kwarg and model property `QueryKnowledgeBaseOptions.context` has been renamed to  `AnswersOptions.answer_context`
* Model `QueryTextOptions` has been renamed to `AnswersFromTextOptions`
* Method kwarg and model property `QueryTextOptions.records` has been renamed to `AnswersFromTextOptions.text_documents`
* Model `AnswerSpanRequest` has been renamed to `ShortAnswerOptions`
* Model property `AnswerSpanRequest.confidence_score_threshold` has been renamed to `ShortAnswerOptions.confidence_threshold`
* Model property `AnswerSpanRequest.top_answers_with_span` has been renamed to `ShortAnswerOptions.top`
* Model `KnowledgeBaseAnswerRequestContext` has been renamed to `KnowledgeBaseAnswerContext`
* Model property `KnowledgeBaseAnswerRequestContext.previous_user_query` has been renamed to `KnowledgeBaseAnswerContext.previous_question`
* Model `TextRecord` has been renamed to `TextDocument`
* Model `KnowledgeBaseAnswers` has been renamed to `AnswersResult`
* Model `TextAnswers` has been renamed to `AnswersFromTextResult`
* Model property `KnowledgeBaseAnswer.answer_span` has been renamed to `KnowledgeBaseAnswer.short_answer`
* Model property `KnowledgeBaseAnswer.id` has been renamed to `KnowledgeBaseAnswer.qna_id`
* Model property `KnowledgeBaseAnswer.confidence_score` has been renamed to `KnowledgeBaseAnswer.confidence`
* Model property `AnswerSpan.confidence_score` has been renamed to `AnswerSpan.confidence`
* Model property `TextAnswer.confidence_score` has been renamed to `TextAnswer.confidence`
* Model property `TextAnswer.answer_span` has been renamed to `TextAnswer.short_answer`
* Enums `LogicalOperationKind` and `RankerType` have been removed
* The `operations` and `aio.operations` namespaces are no longer public

### Bugs Fixed

* Fixed formating of `MetadataFilter.metadata`

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
