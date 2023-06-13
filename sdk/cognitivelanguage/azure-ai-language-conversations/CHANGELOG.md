# Release History

## 1.1.0 (2023-06-13)

### Features Added
- Added support for service version 2023-04-01.

### Breaking Changes

> Note: The following changes are only breaking from the previous beta. They are not breaking since version 1.0.0 when those types and members did not exist.

- Removed support for service version 2022-05-15-preview.
- Removed support for service version 2022-10-01-preview.
- Removed support for "ConversationalPIITask" analysis with `ConversationAnalysisClient`.
- Removed support for "ConversationalSentimentTask" with `ConversationAnalysisClient`.
- Removed the following methods from `ConversationAuthoringClient`:
  - `begin_assign_deployment_resources`
  - `get_assign_deployment_resources_status`
  - `begin_unassign_deployment_resources`
  - `get_unassign_deployment_resources_status`
  - `begin_delete_deployment_from_resources`
  - `get_deployment_delete_from_resources_status`
  - `list_assigned_resource_deployments`
  - `list_deployment_resources`

## 1.1.0b3 (2022-11-10)

### Features Added
- Added support for the "ConversationalSentimentTask" kind with `begin_conversation_analysis`.
- Added support for "chapterTitle" and "narrative" `summaryAspects` options for ConversationalSummarizationTasks.
- Added methods to the `ConversationAuthoringClient` to manage deployment resources:
  - `begin_assign_deployment_resources`
  - `get_assign_deployment_resources_status`
  - `begin_unassign_deployment_resources`
  - `get_unassign_deployment_resources_status`
  - `begin_delete_deployment_from_resources`
  - `get_deployment_delete_from_resources_status`
  - `begin_load_snapshot`
  - `get_load_snapshot_status`
  - `list_assigned_resource_deployments`
  - `list_deployment_resources`
- Added optional `trained_model_label` keyword argument to `begin_export_project`.

### Other Changes
* This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

## 1.1.0b2 (2022-07-01)

### Features Added
* Added Azure Active Directory (AAD) authentication support
* Added support for authoring operations with `ConversationAuthoringClient` under the `azure.ai.language.conversations.authoring` namespace.

## 1.0.0 (2022-06-27)

### Features Added
* Added Azure Active Directory (AAD) authentication support
* Added more resolution types for entities
* Added support for authoring operations with `ConversationAuthoringClient` under the `azure.ai.language.conversations.authoring` namespace.

### Breaking Changes
* Client now uses python dictionaries for method parameters and results instead of classes.

## 1.1.0b1 (2022-05-26)

### Features Added
* Conversation summarization task (Long-running operation)
* Conversation PII extraction task (Long-running operation)

### Breaking Changes
* Client now uses python dictionaries for method parameters and results instead of classes.
* Many input and result parameter name changes in `analyze_conversation()` method

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
