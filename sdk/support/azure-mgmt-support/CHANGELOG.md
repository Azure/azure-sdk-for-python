# Release History

## 8.0.0 (2026-07-07)

### Features Added

  - Model `ChatTranscriptDetails` added property `properties`
  - Model `CommunicationDetails` added property `properties`
  - Model `CommunicationDetails` added property `system_data`
  - Model `FileDetails` added property `properties`
  - Model `FileWorkspaceDetails` added property `properties`
  - Model `Operation` added property `is_data_action`
  - Model `Operation` added property `origin`
  - Model `Operation` added property `action_type`
  - Model `ProblemClassification` added property `properties`
  - Model `ProblemClassification` added property `system_data`
  - Model `Service` added property `properties`
  - Model `Service` added property `system_data`
  - Model `SupportTicketDetails` added property `properties`
  - Model `SupportTicketDetails` added property `system_data`
  - Model `UpdateSupportTicket` added property `direct_connect_escalation`
  - Added enum `ActionType`
  - Added enum `ChatConversationStatus`
  - Added model `ChatTranscriptDetailsProperties`
  - Added model `ClassificationService`
  - Added model `CommunicationDetailsProperties`
  - Added model `DirectConnectEscalation`
  - Added enum `EscalationStatus`
  - Added model `FileDetailsProperties`
  - Added model `FileWorkspaceDetailsProperties`
  - Added model `LookUpResourceIdRequest`
  - Added model `LookUpResourceIdResponse`
  - Added enum `Origin`
  - Added model `ProblemClassificationProperties`
  - Added model `ProblemClassificationsClassificationInput`
  - Added model `ProblemClassificationsClassificationOutput`
  - Added model `ProblemClassificationsClassificationResult`
  - Added model `ServiceClassificationAnswer`
  - Added model `ServiceClassificationOutput`
  - Added model `ServiceClassificationRequest`
  - Added model `ServiceProperties`
  - Added enum `SupportChannel`
  - Added model `SupportTicketDetailsProperties`
  - Model `SupportTicketsOperations` added method `look_up_resource_id`
  - Added model `ClassifyProblemsNoSubscriptionOperations`
  - Added model `ClassifyProblemsOperations`
  - Added model `ClassifyServicesNoSubscriptionOperations`
  - Added model `ClassifyServicesOperations`

### Breaking Changes

  - Deleted or renamed model `MicrosoftSupport`
  - Model `ChatTranscriptDetails` deleted or renamed its instance variable `messages`
  - Model `ChatTranscriptDetails` deleted or renamed its instance variable `start_time`
  - Model `CommunicationDetails` deleted or renamed its instance variable `communication_type`
  - Model `CommunicationDetails` deleted or renamed its instance variable `communication_direction`
  - Model `CommunicationDetails` deleted or renamed its instance variable `sender`
  - Model `CommunicationDetails` deleted or renamed its instance variable `subject`
  - Model `CommunicationDetails` deleted or renamed its instance variable `body`
  - Model `CommunicationDetails` deleted or renamed its instance variable `created_date`
  - Model `FileDetails` deleted or renamed its instance variable `created_on`
  - Model `FileDetails` deleted or renamed its instance variable `chunk_size`
  - Model `FileDetails` deleted or renamed its instance variable `file_size`
  - Model `FileDetails` deleted or renamed its instance variable `number_of_chunks`
  - Model `FileWorkspaceDetails` deleted or renamed its instance variable `created_on`
  - Model `FileWorkspaceDetails` deleted or renamed its instance variable `expiration_time`
  - Model `ProblemClassification` deleted or renamed its instance variable `display_name`
  - Model `ProblemClassification` deleted or renamed its instance variable `secondary_consent_enabled`
  - Model `Service` deleted or renamed its instance variable `display_name`
  - Model `Service` deleted or renamed its instance variable `resource_types`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `support_ticket_id`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `description`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `problem_classification_id`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `problem_classification_display_name`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `severity`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `enrollment_id`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `require24_x7_response`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `advanced_diagnostic_consent`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `problem_scoping_questions`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `support_plan_id`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `contact_details`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `service_level_agreement`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `support_engineer`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `support_plan_type`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `support_plan_display_name`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `title`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `problem_start_time`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `service_id`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `service_display_name`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `status`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `created_date`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `modified_date`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `file_workspace_name`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `is_temporary_ticket`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `technical_ticket_details`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `quota_ticket_details`
  - Model `SupportTicketDetails` deleted or renamed its instance variable `secondary_consent`
  - Deleted or renamed model `ChatTranscriptsListResult`
  - Deleted or renamed model `CommunicationsListResult`
  - Deleted or renamed model `FilesListResult`
  - Deleted or renamed model `OperationsListResult`
  - Deleted or renamed model `ProblemClassificationsListResult`
  - Deleted or renamed model `ServicesListResult`
  - Deleted or renamed model `SupportTicketsListResult`
  - Deleted or renamed model `TranscriptContentType`

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
