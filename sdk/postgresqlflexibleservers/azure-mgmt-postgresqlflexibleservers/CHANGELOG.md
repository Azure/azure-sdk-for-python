# Release History

## 1.2.0b1 (2025-05-19)

### Features Added

  - Client `PostgreSQLManagementClient` added operation group `quota_usages`
  - Client `PostgreSQLManagementClient` added operation group `tuning_options`
  - Client `PostgreSQLManagementClient` added operation group `tuning_index`
  - Client `PostgreSQLManagementClient` added operation group `tuning_configuration`
  - Model `FlexibleServerCapability` added property `supported_features`
  - Model `Server` added property `cluster`
  - Model `ServerForUpdate` added property `cluster`
  - Model `ServerSkuCapability` added property `supported_features`
  - Model `ServerSkuCapability` added property `security_profile`
  - Enum `ServerState` added member `INACCESSIBLE`
  - Enum `ServerState` added member `PROVISIONING`
  - Enum `ServerState` added member `RESTARTING`
  - Enum `ServerVersion` added member `SEVENTEEN`
  - Model `ServerVersionCapability` added property `supported_features`
  - Enum `SourceType` added member `APSARA_DB_RDS`
  - Enum `SourceType` added member `CRUNCHY_POSTGRE_SQL`
  - Enum `SourceType` added member `DIGITAL_OCEAN_DROPLETS`
  - Enum `SourceType` added member `DIGITAL_OCEAN_POSTGRE_SQL`
  - Enum `SourceType` added member `EDB_ORACLE_SERVER`
  - Enum `SourceType` added member `EDB_POSTGRE_SQL`
  - Enum `SourceType` added member `HEROKU_POSTGRE_SQL`
  - Enum `SourceType` added member `HUAWEI_COMPUTE`
  - Enum `SourceType` added member `HUAWEI_RDS`
  - Enum `SourceType` added member `POSTGRE_SQL_COSMOS_DB`
  - Enum `SourceType` added member `POSTGRE_SQL_FLEXIBLE_SERVER`
  - Enum `SourceType` added member `SUPABASE_POSTGRE_SQL`
  - Enum `StorageType` added member `ULTRA_SSD_LRS`
  - Added model `Cluster`
  - Added model `ConfigTuningRequestParameter`
  - Added model `ImpactRecord`
  - Added model `IndexRecommendationDetails`
  - Added model `IndexRecommendationListResult`
  - Added model `IndexRecommendationResource`
  - Added model `IndexRecommendationResourcePropertiesAnalyzedWorkload`
  - Added model `IndexRecommendationResourcePropertiesImplementationDetails`
  - Added model `NameProperty`
  - Added model `QuotaUsage`
  - Added model `QuotaUsagesListResult`
  - Added enum `RecommendationType`
  - Added enum `RecommendationTypeEnum`
  - Added model `SessionDetailsListResult`
  - Added model `SessionDetailsResource`
  - Added model `SessionResource`
  - Added model `SessionsListResult`
  - Added model `SupportedFeature`
  - Added enum `SupportedFeatureStatusEnum`
  - Added enum `TuningOptionEnum`
  - Added model `TuningOptionsListResult`
  - Added model `TuningOptionsResource`
  - Added operation group `QuotaUsagesOperations`
  - Added operation group `TuningConfigurationOperations`
  - Added operation group `TuningIndexOperations`
  - Added operation group `TuningOptionsOperations`

## 1.1.0 (2025-03-24)

### Features Added

  - Enum `IdentityType` added member `SYSTEM_ASSIGNED`
  - Enum `IdentityType` added member `SYSTEM_ASSIGNED_USER_ASSIGNED`
  - Model `UserAssignedIdentity` added property `principal_id`

## 1.1.0b2 (2024-12-16)

### Features Added

  - Model `ServerForUpdate` added property `cluster`

## 1.1.0b1 (2024-11-04)

### Features Added

  - Client `PostgreSQLManagementClient` added operation group `quota_usages`
  - Client `PostgreSQLManagementClient` added operation group `tuning_options`
  - Model `FlexibleServerCapability` added property `supported_features`
  - Enum `IdentityType` added member `SYSTEM_ASSIGNED`
  - Model `Server` added property `cluster`
  - Model `ServerSkuCapability` added property `supported_features`
  - Model `ServerSkuCapability` added property `security_profile`
  - Enum `ServerVersion` added member `SEVENTEEN`
  - Model `ServerVersionCapability` added property `supported_features`
  - Enum `SourceType` added member `APSARA_DB_RDS`
  - Enum `SourceType` added member `CRUNCHY_POSTGRE_SQL`
  - Enum `SourceType` added member `DIGITAL_OCEAN_DROPLETS`
  - Enum `SourceType` added member `DIGITAL_OCEAN_POSTGRE_SQL`
  - Enum `SourceType` added member `EDB_ORACLE_SERVER`
  - Enum `SourceType` added member `EDB_POSTGRE_SQL`
  - Enum `SourceType` added member `HEROKU_POSTGRE_SQL`
  - Enum `SourceType` added member `HUAWEI_COMPUTE`
  - Enum `SourceType` added member `HUAWEI_RDS`
  - Enum `SourceType` added member `POSTGRE_SQL_COSMOS_DB`
  - Enum `SourceType` added member `POSTGRE_SQL_FLEXIBLE_SERVER`
  - Enum `SourceType` added member `SUPABASE_POSTGRE_SQL`
  - Enum `StorageType` added member `ULTRA_SSD_LRS`
  - Added model `Cluster`
  - Added model `ImpactRecord`
  - Added model `IndexRecommendationDetails`
  - Added model `IndexRecommendationListResult`
  - Added model `IndexRecommendationResource`
  - Added model `IndexRecommendationResourcePropertiesAnalyzedWorkload`
  - Added model `IndexRecommendationResourcePropertiesImplementationDetails`
  - Added model `NameProperty`
  - Added model `QuotaUsage`
  - Added model `QuotaUsagesListResult`
  - Added enum `RecommendationType`
  - Added enum `RecommendationTypeEnum`
  - Added model `SupportedFeature`
  - Added enum `SupportedFeatureStatusEnum`
  - Added enum `TuningOptionEnum`
  - Added model `TuningOptionsListResult`
  - Added model `TuningOptionsResource`

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
