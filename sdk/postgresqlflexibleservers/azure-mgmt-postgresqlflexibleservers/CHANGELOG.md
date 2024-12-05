# Release History

## 1.0.0 (2024-10-11)

### Features Added

  - Enum `Origin` added member `CUSTOMER_ON_DEMAND`
  - Model `ServerForUpdate` added property `administrator_login`
  - Model `BackupsOperations` added method `begin_create`
  - Model `BackupsOperations` added method `begin_delete`
  - Added operation group `LongRunningBackupOperations`
  - Added operation group `LongRunningBackupsOperations`
  - Added operation group `MaintenancesOperations`
  - Added operation group `LogFilesOperations`
  - Added operation group `MigrationsOperations`
  - Added operation group `PrivateEndpointConnectionOperations`
  - Added operation group `VirtualEndpointsOperations`
  - Added operation group `ServerThreatProtectionSettingsOperations`
  - Added operation group `AdvancedThreatProtectionSettingsOperations`
  - Added operation group `LocationBasedCapabilitySetOperations`
  - Added operation group `OperationProgressOperations`
  - Added operation group `OperationResultsOperations`
  - Model `DataEncryption` has a new parameter `geo_backup_encryption_key_status`
  - Model `DataEncryption` has a new parameter `geo_backup_key_uri`
  - Model `DataEncryption` has a new parameter `geo_backup_user_assigned_identity_id`
  - Model `DataEncryption` has a new parameter `primary_encryption_key_status`
  - Model `Storage` has a new parameter `auto_grow`
  - Model `Storage` has a new parameter `iops`
  - Model `Storage` has a new parameter `iops_tier`
  - Model `Storage` has a new parameter `throughput`
  - Model `Storage` has a new parameter `type`
  - Model `Server` has a new parameter `private_endpoint_connections`
  - Model `Server` has a new parameter `replica`
  - Model `ServerForUpdate` has a new parameter `replica`

### Breaking Changes

  - Deleted or renamed client operation group `PostgreSQLManagementClient.quota_usages`
  - Deleted or renamed model `NameProperty`
  - Deleted or renamed model `QuotaUsage`
  - Deleted or renamed model `QuotaUsagesOperations`

## 1.0.0b1 (2024-08-27)

### Other Changes

  - Initial version
