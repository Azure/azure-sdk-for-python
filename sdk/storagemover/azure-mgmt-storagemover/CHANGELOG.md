# Release History

## 3.0.0 (2025-07-21)

### Features Added

  - Enum `Minute` added member `ENUM_0`
  - Enum `Minute` added member `ENUM_30`
  - Model `StorageMoverUpdateParameters` added property `properties`
  - Added model `AgentUpdateProperties`
  - Added model `JobDefinitionUpdateProperties`
  - Added model `ProjectUpdateProperties`
  - Added model `StorageMoverUpdateProperties`

### Breaking Changes

  - Deleted or renamed client `StorageMoverMgmtClient`
  - Model `AgentUpdateParameters` deleted or renamed its instance variable `description`
  - Model `AgentUpdateParameters` deleted or renamed its instance variable `upload_limit_schedule`
  - Model `JobDefinitionUpdateParameters` deleted or renamed its instance variable `description`
  - Model `JobDefinitionUpdateParameters` deleted or renamed its instance variable `copy_mode`
  - Model `JobDefinitionUpdateParameters` deleted or renamed its instance variable `agent_name`
  - Deleted or renamed enum value `Minute.THIRTY`
  - Deleted or renamed enum value `Minute.ZERO`
  - Model `ProjectUpdateParameters` deleted or renamed its instance variable `description`
  - Model `StorageMoverUpdateParameters` deleted or renamed its instance variable `description`
  - Deleted or renamed model `AgentList`
  - Deleted or renamed model `EndpointList`
  - Deleted or renamed model `JobDefinitionList`
  - Deleted or renamed model `JobRunList`
  - Deleted or renamed model `ProjectList`
  - Deleted or renamed model `StorageMoverList`
  - Deleted or renamed model `UploadLimit`

## 2.1.0 (2024-06-17)

### Features Added

  - Model Agent has a new parameter time_zone
  - Model Agent has a new parameter upload_limit_schedule
  - Model AgentUpdateParameters has a new parameter upload_limit_schedule

## 2.0.0 (2023-10-23)

### Features Added

  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model AzureStorageBlobContainerEndpointUpdateProperties has a new required parameter endpoint_type
  - Model EndpointBaseUpdateProperties has a new required parameter endpoint_type
  - Model NfsMountEndpointUpdateProperties has a new required parameter endpoint_type

## 2.0.0b1 (2023-07-21)

### Features Added

  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model AzureStorageBlobContainerEndpointUpdateProperties has a new required parameter endpoint_type
  - Model EndpointBaseUpdateProperties has a new required parameter endpoint_type
  - Model NfsMountEndpointUpdateProperties has a new required parameter endpoint_type

## 1.0.0 (2023-03-07)

### Other changes

  - First GA version

## 1.0.0b1 (2023-02-20)

* Initial Release
