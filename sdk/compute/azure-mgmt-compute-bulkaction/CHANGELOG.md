# Release History

## 1.0.0b2 (2026-07-22)

### Features Added

  - Added operation group `BulkCreateCustomOperations`
  - Added operation group `LaunchBulkInstancesOperationOperations`
  - Added operation group `OccurrenceExtensionOperations`
  - Added operation group `OccurrencesOperations`
  - Added operation group `ScheduledActionExtensionOperations`
  - Added operation group `ScheduledActionOperationStatusOperations`
  - Added operation group `ScheduledActionsOperations`
  - Added support for scheduled and recurring bulk actions, including new models for scheduled actions, occurrences, recurring schedules, and operation status tracking
  - Added support for custom bulk create and launch bulk instances, including full virtual machine configuration models (compute, network, storage, OS, security, and diagnostics profiles)
  - Added request/response models `ResourcesWithContext`, `ResourceWithContext`, `ResourceAttachRequest`, `ResourceDetachRequest`, `ResourcePatchRequest`, `AcknowledgeBulkOperationErrorsRequest`, `AcknowledgeBulkOperationErrorsResponse`, `DelayRequest`, and `CancelOccurrenceRequest`

## 1.0.0b1 (2026-07-21)

### Other Changes

  - Initial version
