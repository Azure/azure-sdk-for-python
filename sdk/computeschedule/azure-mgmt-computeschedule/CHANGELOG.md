# Release History

## 1.2.0b1 (2025-07-24)

### Features Added

  - Client `ComputeScheduleMgmtClient` added operation group `scheduled_action_extension`
  - Client `ComputeScheduleMgmtClient` added operation group `occurrences`
  - Client `ComputeScheduleMgmtClient` added operation group `occurrence_extension`
  - Added model `CancelOccurrenceRequest`
  - Added enum `CreatedByType`
  - Added model `DelayRequest`
  - Added model `ExtensionResource`
  - Added enum `Language`
  - Added enum `Month`
  - Added model `NotificationProperties`
  - Added enum `NotificationType`
  - Added model `Occurrence`
  - Added model `OccurrenceExtensionProperties`
  - Added model `OccurrenceExtensionResource`
  - Added model `OccurrenceProperties`
  - Added model `OccurrenceResource`
  - Added model `OccurrenceResultSummary`
  - Added enum `OccurrenceState`
  - Added enum `ProvisioningState`
  - Added model `ProxyResource`
  - Added model `RecurringActionsResourceOperationResult`
  - Added model `Resource`
  - Added model `ResourceAttachRequest`
  - Added model `ResourceDetachRequest`
  - Added enum `ResourceOperationStatus`
  - Added model `ResourcePatchRequest`
  - Added enum `ResourceProvisioningState`
  - Added model `ResourceResultSummary`
  - Added model `ResourceStatus`
  - Added enum `ResourceType`
  - Added model `ScheduledAction`
  - Added model `ScheduledActionProperties`
  - Added model `ScheduledActionResource`
  - Added model `ScheduledActionResources`
  - Added enum `ScheduledActionType`
  - Added model `ScheduledActionUpdate`
  - Added model `ScheduledActionUpdateProperties`
  - Added model `ScheduledActionsSchedule`
  - Added model `SystemData`
  - Added model `TrackedResource`
  - Added enum `WeekDay`
  - Model `ScheduledActionsOperations` added method `attach_resources`
  - Model `ScheduledActionsOperations` added method `begin_create_or_update`
  - Model `ScheduledActionsOperations` added method `begin_delete`
  - Model `ScheduledActionsOperations` added method `cancel_next_occurrence`
  - Model `ScheduledActionsOperations` added method `detach_resources`
  - Model `ScheduledActionsOperations` added method `disable`
  - Model `ScheduledActionsOperations` added method `enable`
  - Model `ScheduledActionsOperations` added method `list_by_resource_group`
  - Model `ScheduledActionsOperations` added method `list_by_subscription`
  - Model `ScheduledActionsOperations` added method `list_resources`
  - Model `ScheduledActionsOperations` added method `patch_resources`
  - Model `ScheduledActionsOperations` added method `trigger_manual_occurrence`
  - Added operation group `OccurrenceExtensionOperations`
  - Added operation group `OccurrencesOperations`
  - Added operation group `ScheduledActionExtensionOperations`

## 1.1.0 (2025-06-05)

### Features Added

  - Added model `CreateResourceOperationResponse`
  - Added model `DeleteResourceOperationResponse`
  - Added model `ExecuteCreateRequest`
  - Added model `ExecuteDeleteRequest`
  - Added model `ResourceProvisionPayload`
  - Model `ScheduledActionsOperations` added method `virtual_machines_execute_create`
  - Model `ScheduledActionsOperations` added method `virtual_machines_execute_delete`

## 1.0.0 (2025-01-20)

### Features Added

  - Model `OperationErrorDetails` added property `timestamp`
  - Model `OperationErrorDetails` added property `azure_operation_name`
  - Model `ResourceOperationDetails` added property `timezone`
  - Model `Schedule` added property `deadline`
  - Model `Schedule` added property `timezone`

## 1.0.0b1 (2024-09-26)

### Other Changes

  - Initial version
