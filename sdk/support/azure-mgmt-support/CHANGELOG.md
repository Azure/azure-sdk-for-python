# Release History

## 8.0.0 (2026-07-06)

### Features Added

  - Model `CommunicationDetails` added property `system_data`
  - Model `Operation` added property `is_data_action`
  - Model `Operation` added property `origin`
  - Model `Operation` added property `action_type`
  - Model `ProblemClassification` added property `system_data`
  - Model `Service` added property `system_data`
  - Model `SupportTicketDetails` added property `system_data`
  - Model `UpdateSupportTicket` added property `direct_connect_escalation`
  - Added enum `ActionType`
  - Added enum `ChatConversationStatus`
  - Added model `ClassificationService`
  - Added model `DirectConnectEscalation`
  - Added enum `EscalationStatus`
  - Added model `LookUpResourceIdRequest`
  - Added model `LookUpResourceIdResponse`
  - Added enum `Origin`
  - Added model `ProblemClassificationsClassificationInput`
  - Added model `ProblemClassificationsClassificationOutput`
  - Added model `ProblemClassificationsClassificationResult`
  - Added model `ServiceClassificationAnswer`
  - Added model `ServiceClassificationOutput`
  - Added model `ServiceClassificationRequest`
  - Added enum `SupportChannel`
  - Operation group `SupportTicketsOperations` added method `look_up_resource_id`
  - Added operation group `ClassifyProblemsNoSubscriptionOperations`
  - Added operation group `ClassifyProblemsOperations`
  - Added operation group `ClassifyServicesNoSubscriptionOperations`
  - Added operation group `ClassifyServicesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Renamed client `MicrosoftSupport` to `SupportMgmtClient`
  - Model `ChatTranscriptDetails` moved instance variable `messages` and `start_time` under property `properties` whose type is `ChatTranscriptDetailsProperties`
  - Model `CommunicationDetails` moved instance variable `communication_type`, `communication_direction`, `sender`, `subject`, `body` and `created_date` under property `properties` whose type is `CommunicationDetailsProperties`
  - Model `FileDetails` moved instance variable `created_on`, `chunk_size`, `file_size` and `number_of_chunks` under property `properties` whose type is `FileDetailsProperties`
  - Model `FileWorkspaceDetails` moved instance variable `created_on` and `expiration_time` under property `properties` whose type is `FileWorkspaceDetailsProperties`
  - Model `ProblemClassification` moved instance variable `display_name` and `secondary_consent_enabled` under property `properties` whose type is `ProblemClassificationProperties`
  - Model `Service` moved instance variable `display_name` and `resource_types` under property `properties` whose type is `ServiceProperties`
  - Model `SupportTicketDetails` moved instance variable `support_ticket_id`, `description`, `problem_classification_id`, `problem_classification_display_name`, `severity`, `enrollment_id`, `require24_x7_response`, `advanced_diagnostic_consent`, `problem_scoping_questions`, `support_plan_id`, `contact_details`, `service_level_agreement`, `support_engineer`, `support_plan_type`, `support_plan_display_name`, `title`, `problem_start_time`, `service_id`, `service_display_name`, `status`, `created_date`, `modified_date`, `file_workspace_name`, `is_temporary_ticket`, `technical_ticket_details`, `quota_ticket_details` and `secondary_consent` under property `properties` whose type is `SupportTicketDetailsProperties`

### Other Changes

  - Deleted model `ChatTranscriptsListResult`/`CommunicationsListResult`/`FilesListResult`/`OperationsListResult`/`ProblemClassificationsListResult`/`ServicesListResult`/`SupportTicketsListResult`/`TranscriptContentType` which actually were not used by SDK users

## 7.0.0 (2024-04-22)

### Features Added

  - Added operation group ChatTranscriptsNoSubscriptionOperations
  - Added operation group ChatTranscriptsOperations
  - Added operation group CommunicationsNoSubscriptionOperations
  - Added operation group FileWorkspacesNoSubscriptionOperations
  - Added operation group FileWorkspacesOperations
  - Added operation group FilesNoSubscriptionOperations
  - Added operation group FilesOperations
  - Added operation group SupportTicketsNoSubscriptionOperations
  - Model ProblemClassification has a new parameter secondary_consent_enabled
  - Model SupportTicketDetails has a new parameter file_workspace_name
  - Model SupportTicketDetails has a new parameter is_temporary_ticket
  - Model SupportTicketDetails has a new parameter problem_scoping_questions
  - Model SupportTicketDetails has a new parameter secondary_consent
  - Model SupportTicketDetails has a new parameter support_plan_display_name
  - Model SupportTicketDetails has a new parameter support_plan_id
  - Model UpdateSupportTicket has a new parameter advanced_diagnostic_consent
  - Model UpdateSupportTicket has a new parameter secondary_consent

### Breaking Changes

  - Model SupportTicketDetails has a new required parameter advanced_diagnostic_consent
  - Parameter body of model CommunicationDetails is now required
  - Parameter contact_details of model SupportTicketDetails is now required
  - Parameter description of model SupportTicketDetails is now required
  - Parameter problem_classification_id of model SupportTicketDetails is now required
  - Parameter service_id of model SupportTicketDetails is now required
  - Parameter severity of model SupportTicketDetails is now required
  - Parameter subject of model CommunicationDetails is now required
  - Parameter title of model SupportTicketDetails is now required

## 6.1.0b3 (2024-03-18)

### Features Added

  - Added operation ChatTranscriptsNoSubscriptionOperations.list
  - Added operation CommunicationsNoSubscriptionOperations.list
  - Added operation ProblemClassificationsOperations.classify_problems
  - Added operation group LookUpResourceIdOperations
  - Added operation group ProblemClassificationsNoSubscriptionOperations
  - Added operation group ServiceClassificationsNoSubscriptionOperations
  - Added operation group ServiceClassificationsOperations
  - Model ProblemClassification has a new parameter metadata
  - Model ProblemClassification has a new parameter parent_problem_classification
  - Model Service has a new parameter metadata
  - Model SupportTicketDetails has a new parameter is_temporary_ticket

### Breaking Changes

  - Removed operation group SupportTicketChatTranscriptsNoSubscriptionOperations
  - Removed operation group SupportTicketCommunicationsNoSubscriptionOperations

## 6.1.0b2 (2023-10-23)

### Features Added

  - Added operation group ChatTranscriptsNoSubscriptionOperations
  - Added operation group ChatTranscriptsOperations
  - Added operation group CommunicationsNoSubscriptionOperations
  - Added operation group FileWorkspacesNoSubscriptionOperations
  - Added operation group FileWorkspacesOperations
  - Added operation group FilesNoSubscriptionOperations
  - Added operation group FilesOperations
  - Added operation group SupportTicketChatTranscriptsNoSubscriptionOperations
  - Added operation group SupportTicketCommunicationsNoSubscriptionOperations
  - Added operation group SupportTicketsNoSubscriptionOperations
  - Model ProblemClassification has a new parameter secondary_consent_enabled
  - Model SupportTicketDetails has a new parameter advanced_diagnostic_consent
  - Model SupportTicketDetails has a new parameter file_workspace_name
  - Model SupportTicketDetails has a new parameter problem_scoping_questions
  - Model SupportTicketDetails has a new parameter secondary_consent
  - Model SupportTicketDetails has a new parameter support_plan_display_name
  - Model SupportTicketDetails has a new parameter support_plan_id
  - Model UpdateSupportTicket has a new parameter advanced_diagnostic_consent
  - Model UpdateSupportTicket has a new parameter secondary_consent

## 6.1.0b1 (2022-10-28)
### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 6.0.0 (2021-03-29)

 - GA release

## 6.0.0b1 (2020-12-02)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 1.0.0 (2020-03-14)

**Features**

- Model UpdateSupportTicket has a new parameter status
- Model Service has a new parameter resource_types

**Breaking changes**

- Model SupportTicketDetails no longer has parameter production_outage
- Operation SupportTicketsOperations.update has a new signature

## 0.1.0 (2020-01-31)

* Initial Release
