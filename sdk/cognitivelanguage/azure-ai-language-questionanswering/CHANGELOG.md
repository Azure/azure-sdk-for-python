# Release History

## 1.0.0b2 (unreleased)

* We are now targeting service version `2021-07-15-preview`

### Breaking changes
* The method `QuestionAnsweringClient.query_knowledgebase` has been renamed to `query_knowledge_base`.

### Features Added
* The method `QuestionAnsweringClient.query_text` now supports a list of records as strings, where the ID value will be automatically populated.


## 1.0.0b1 (2021-07-27)

### Features Added
* Initial release - supports querying from text records and knowledge bases.
