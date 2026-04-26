# Release History

## 3.1.0 (2026-03-25)

### Features Added

  - Client `StorageMoverMgmtClient` added operation group `connections`
  - Model `AzureMultiCloudConnectorEndpointProperties` added property `endpoint_kind`
  - Model `AzureStorageBlobContainerEndpointProperties` added property `endpoint_kind`
  - Model `AzureStorageNfsFileShareEndpointProperties` added property `endpoint_kind`
  - Model `AzureStorageSmbFileShareEndpointProperties` added property `endpoint_kind`
  - Enum `CredentialType` added member `AZURE_KEY_VAULT_S3_WITH_HMAC`
  - Model `EndpointBaseProperties` added property `endpoint_kind`
  - Enum `EndpointType` added member `S3_WITH_HMAC`
  - Model `JobDefinitionProperties` added property `connections`
  - Model `JobDefinitionProperties` added property `schedule`
  - Model `JobDefinitionProperties` added property `data_integrity_validation`
  - Model `JobDefinitionProperties` added property `preserve_permissions`
  - Model `JobDefinitionUpdateProperties` added property `connections`
  - Model `JobDefinitionUpdateProperties` added property `data_integrity_validation`
  - Model `JobRunProperties` added property `trigger_type`
  - Model `JobRunProperties` added property `scheduled_execution_time`
  - Model `JobRunProperties` added property `warnings`
  - Model `NfsMountEndpointProperties` added property `endpoint_kind`
  - Model `SmbMountEndpointProperties` added property `endpoint_kind`
  - Added model `AzureKeyVaultS3WithHmacCredentials`
  - Added model `Connection`
  - Added model `ConnectionProperties`
  - Added enum `ConnectionStatus`
  - Added enum `DataIntegrityValidation`
  - Added enum `EndpointKind`
  - Added enum `Frequency`
  - Added model `JobRunWarning`
  - Added model `S3WithHmacEndpointProperties`
  - Added model `S3WithHmacEndpointUpdateProperties`
  - Added enum `S3WithHmacSourceType`
  - Added model `ScheduleInfo`
  - Added enum `TriggerType`
  - Added operation group `ConnectionsOperations`

## 3.0.0 (2025-09-04)

### Features Added

  - Model `StorageMoverMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `StorageMoverMgmtClient` added method `send_request`
  - Model `Endpoint` added property `identity`
  - Model `EndpointBaseUpdateParameters` added property `identity`
  - Enum `EndpointType` added member `AZURE_MULTI_CLOUD_CONNECTOR`
  - Enum `EndpointType` added member `AZURE_STORAGE_NFS_FILE_SHARE`
  - Model `StorageMoverUpdateParameters` added property `properties`
  - Added model `AgentUpdateProperties`
  - Added model `AzureMultiCloudConnectorEndpointProperties`
  - Added model `AzureMultiCloudConnectorEndpointUpdateProperties`
  - Added model `AzureStorageNfsFileShareEndpointProperties`
  - Added model `AzureStorageNfsFileShareEndpointUpdateProperties`
  - Added model `JobDefinitionPropertiesSourceTargetMap`
  - Added model `JobDefinitionUpdateProperties`
  - Added enum `JobType`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `ProjectUpdateProperties`
  - Added model `SourceEndpoint`
  - Added model `SourceEndpointProperties`
  - Added model `SourceTargetMap`
  - Added model `StorageMoverUpdateProperties`
  - Added model `TargetEndpoint`
  - Added model `TargetEndpointProperties`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AgentUpdateParameters` moved instance variable `description` and `upload_limit_schedule` under property `properties`
  - Model `JobDefinitionUpdateParameters` moved instance variable `description`, `copy_mode` and `agent_name` under property `properties`
  - Model `ProjectUpdateParameters` deleted or renamed its instance variable `description`
  - Model `StorageMoverUpdateParameters` deleted or renamed its instance variable `description`
  - Deleted or renamed model `UploadLimit`

### Other Changes

  - Deleted model `AgentList`/`EndpointList`/`JobDefinitionList`/`JobRunList`/`ProjectList`/`StorageMoverList` which actually were not used by SDK users

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
