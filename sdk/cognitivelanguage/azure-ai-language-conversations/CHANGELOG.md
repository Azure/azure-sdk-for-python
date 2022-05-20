# Release History

## 1.0.0b4 (2022-05-15)

### Features Added
* Async conversation issue summarization task
* Async conversation PII extraction task

### Breaking Changes
* Replace LLC with DPG
* Changed attribute names in sync api


## 1.0.0b3 (2022-04-19)

### Features Added
* Entity resolutions
* Extra features

### Breaking Changes
* The `ConversationAnalysisOptions` model used as input to the `analyze_conversation` operation is now wrapped in a `CustomConversationalTask` which combines the analysis options with the project parameters into a single model.
* The `query` within the `ConversationAnalysisOptions` is now further qualified as a `TextConversationItem` with additional properties.
* The output `AnalyzeConversationResult` is now wrapped in a `CustomConversationalTaskResult` according to the input model.

### Other Changes
* Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0b1 (2021-11-03)

### Features Added
* Initial release
