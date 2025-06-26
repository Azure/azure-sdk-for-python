# Release History

## 1.0.0 (2025-06-26)

### Features Added

  - Client `StorageActionsMgmtClient` added method `send_request`
  - Added enum `OnFailure`
  - Added enum `OnSuccess`
  - Added model `StorageTaskUpdateProperties`
  - Model `StorageTaskAssignmentOperations` added method `storage_task_assignment_list`

### Breaking Changes

  - Deleted or renamed model `StorageTaskReportSummary`
  - Deleted or renamed method `StorageTaskAssignmentOperations.list`

## 1.0.0b2 (2025-04-20)

### Features Added

  - Enum `ProvisioningState` added member `ACCEPTED`

### Breaking Changes

  - Parameter `identity` of model `StorageTask` is now required
  - Parameter `properties` of model `StorageTask` is now required

## 1.0.0b1 (2024-03-21)

* Initial Release
