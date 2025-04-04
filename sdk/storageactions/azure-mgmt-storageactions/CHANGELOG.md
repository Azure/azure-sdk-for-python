# Release History

## 1.0.0 (2025-04-20)

### Features Added

  - Enum `ProvisioningState` added member `ACCEPTED`
  - Method `StorageTasksOperations.begin_create` has a new overload `def begin_create(self: None, resource_group_name: str, storage_task_name: str, parameters: IO[bytes], content_type: str)`
  - Method `StorageTasksOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, storage_task_name: str, parameters: IO[bytes], content_type: str)`
  - Method `StorageTasksOperations.preview_actions` has a new overload `def preview_actions(self: None, location: str, parameters: IO[bytes], content_type: str)`

### Breaking Changes

  - Method `StorageTask.__init__` removed default value `None` from its parameter `identity`
  - Method `StorageTask.__init__` removed default value `None` from its parameter `properties`

## 1.0.0b1 (2024-03-21)

* Initial Release
