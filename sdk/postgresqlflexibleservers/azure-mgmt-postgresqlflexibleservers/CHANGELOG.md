# Release History

## 2.0.0 (2025-11-17)

### Features Added

  - Model `PostgreSQLManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `PostgreSQLManagementClient` added operation group `administrators_microsoft_entra`
  - Client `PostgreSQLManagementClient` added operation group `advanced_threat_protection_settings`
  - Client `PostgreSQLManagementClient` added operation group `backups_automatic_and_on_demand`
  - Client `PostgreSQLManagementClient` added operation group `capabilities_by_location`
  - Client `PostgreSQLManagementClient` added operation group `capabilities_by_server`
  - Client `PostgreSQLManagementClient` added operation group `captured_logs`
  - Client `PostgreSQLManagementClient` added operation group `backups_long_term_retention`
  - Client `PostgreSQLManagementClient` added operation group `name_availability`
  - Client `PostgreSQLManagementClient` added operation group `private_dns_zone_suffix`
  - Client `PostgreSQLManagementClient` added operation group `quota_usages`
  - Client `PostgreSQLManagementClient` added operation group `tuning_options`
  - Enum `ConfigurationDataType` added member `SET`
  - Enum `ConfigurationDataType` added member `STRING`
  - Model `Server` added property `cluster`
  - Model `ServerSkuCapability` added property `supported_features`
  - Model `ServerSkuCapability` added property `security_profile`
  - Enum `ServerState` added member `INACCESSIBLE`
  - Enum `ServerState` added member `PROVISIONING`
  - Enum `ServerState` added member `RESTARTING`
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
  - Added model `AdminCredentialsForPatch`
  - Added model `AdministratorMicrosoftEntra`
  - Added model `AdministratorMicrosoftEntraAdd`
  - Added model `AdministratorMicrosoftEntraList`
  - Added model `AdvancedThreatProtectionSettingsList`
  - Added model `AdvancedThreatProtectionSettingsModel`
  - Added model `AuthConfigForPatch`
  - Added enum `AzureManagedDiskPerformanceTier`
  - Added model `BackupAutomaticAndOnDemand`
  - Added model `BackupAutomaticAndOnDemandList`
  - Added model `BackupForPatch`
  - Added enum `BackupType`
  - Added model `BackupsLongTermRetentionOperation`
  - Added model `BackupsLongTermRetentionRequest`
  - Added model `BackupsLongTermRetentionResponse`
  - Added enum `Cancel`
  - Added model `Capability`
  - Added model `CapabilityList`
  - Added model `CapturedLog`
  - Added model `CapturedLogList`
  - Added model `Cluster`
  - Added model `ConfigurationList`
  - Added enum `CreateModeForPatch`
  - Added enum `DataEncryptionType`
  - Added model `DatabaseList`
  - Added model `DatabaseMigrationState`
  - Added enum `EncryptionKeyStatus`
  - Added enum `FastProvisioningSupport`
  - Added enum `FeatureStatus`
  - Added model `FirewallRuleList`
  - Added enum `GeographicallyRedundantBackup`
  - Added enum `GeographicallyRedundantBackupSupport`
  - Added model `HighAvailabilityForPatch`
  - Added enum `HighAvailabilityState`
  - Added model `ImpactRecord`
  - Added enum `LocationRestricted`
  - Added enum `LogicalReplicationOnSourceServer`
  - Added model `MaintenanceWindowForPatch`
  - Added enum `MicrosoftEntraAuth`
  - Added enum `MigrateRolesAndPermissions`
  - Added model `Migration`
  - Added enum `MigrationDatabaseState`
  - Added model `MigrationList`
  - Added model `MigrationNameAvailability`
  - Added model `MigrationSecretParametersForPatch`
  - Added enum `MigrationSubstate`
  - Added model `MigrationSubstateDetails`
  - Added model `NameAvailabilityModel`
  - Added model `NameProperty`
  - Added model `ObjectRecommendation`
  - Added model `ObjectRecommendationDetails`
  - Added model `ObjectRecommendationList`
  - Added model `ObjectRecommendationPropertiesAnalyzedWorkload`
  - Added model `ObjectRecommendationPropertiesImplementationDetails`
  - Added enum `OnlineStorageResizeSupport`
  - Added model `OperationList`
  - Added enum `OverwriteDatabasesOnTargetServer`
  - Added enum `PasswordBasedAuth`
  - Added enum `PostgresMajorVersion`
  - Added model `PrivateEndpointConnectionList`
  - Added model `PrivateLinkResourceList`
  - Added model `QuotaUsage`
  - Added model `QuotaUsageList`
  - Added enum `ReadReplicaPromoteOption`
  - Added enum `RecommendationTypeEnum`
  - Added enum `RecommendationTypeParameterEnum`
  - Added model `ServerEditionCapability`
  - Added model `ServerForPatch`
  - Added model `ServerList`
  - Added model `SkuForPatch`
  - Added enum `StartDataMigration`
  - Added enum `StorageAutoGrowthSupport`
  - Added model `SupportedFeature`
  - Added enum `TriggerCutover`
  - Added enum `TuningOptionParameterEnum`
  - Added model `TuningOptions`
  - Added model `TuningOptionsList`
  - Added model `VirtualEndpoint`
  - Added model `VirtualEndpointsList`
  - Added model `VirtualNetworkSubnetUsageModel`
  - Added enum `ZoneRedundantHighAvailabilityAndGeographicallyRedundantBackupSupport`
  - Added enum `ZoneRedundantHighAvailabilitySupport`
  - Model `MigrationsOperations` added method `cancel`
  - Model `MigrationsOperations` added method `check_name_availability`
  - Model `PrivateEndpointConnectionsOperations` added method `begin_delete`
  - Model `PrivateEndpointConnectionsOperations` added method `begin_update`
  - Model `ServersOperations` added method `begin_create_or_update`
  - Model `ServersOperations` added method `list_by_subscription`
  - Model `VirtualNetworkSubnetUsageOperations` added method `list`
  - Added model `AdministratorsMicrosoftEntraOperations`
  - Added model `AdvancedThreatProtectionSettingsOperations`
  - Added model `BackupsAutomaticAndOnDemandOperations`
  - Added model `BackupsLongTermRetentionOperations`
  - Added model `CapabilitiesByLocationOperations`
  - Added model `CapabilitiesByServerOperations`
  - Added model `CapturedLogsOperations`
  - Added model `NameAvailabilityOperations`
  - Added model `PrivateDnsZoneSuffixOperations`
  - Added model `QuotaUsagesOperations`
  - Added model `TuningOptionsOperations`

### Breaking Changes

  - Deleted or renamed client operation group `PostgreSQLManagementClient.administrators`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.backups`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.location_based_capabilities`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.server_capabilities`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.check_name_availability`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.check_name_availability_with_location`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.flexible_server`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.ltr_backup_operations`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.get_private_dns_zone_suffix`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.private_endpoint_connection`
  - Deleted or renamed client operation group `PostgreSQLManagementClient.log_files`
  - Deleted or renamed client method `PostgreSQLManagementClient.check_migration_name_availability`
  - Method `Operations.list` changed from `asynchronous` to `synchronous`
  - Method `AuthConfig.__init__` parameter `password_auth` changed default value from `str` to `none`
  - Method `Backup.__init__` parameter `geo_redundant_backup` changed default value from `str` to `none`
  - Method `HighAvailability.__init__` parameter `mode` changed default value from `str` to `none`
  - Deleted or renamed enum value `HighAvailabilityMode.DISABLED`
  - Deleted or renamed model `ActiveDirectoryAdministrator`
  - Deleted or renamed model `ActiveDirectoryAdministratorAdd`
  - Deleted or renamed model `ActiveDirectoryAuthEnum`
  - Deleted or renamed model `ArmServerKeyType`
  - Deleted or renamed model `AzureManagedDiskPerformanceTiers`
  - Deleted or renamed model `CancelEnum`
  - Deleted or renamed model `CreateModeForUpdate`
  - Deleted or renamed model `DbMigrationStatus`
  - Deleted or renamed model `FastProvisioningSupportedEnum`
  - Deleted or renamed model `FlexibleServerCapability`
  - Deleted or renamed model `FlexibleServerEditionCapability`
  - Deleted or renamed model `GeoBackupSupportedEnum`
  - Deleted or renamed model `GeoRedundantBackupEnum`
  - Deleted or renamed model `HaMode`
  - Deleted or renamed model `KeyStatusEnum`
  - Deleted or renamed model `LogFile`
  - Deleted or renamed model `LogicalReplicationOnSourceDbEnum`
  - Deleted or renamed model `LtrBackupRequest`
  - Deleted or renamed model `LtrBackupResponse`
  - Deleted or renamed model `LtrServerBackupOperation`
  - Deleted or renamed model `MigrateRolesEnum`
  - Deleted or renamed model `MigrationDbState`
  - Deleted or renamed model `MigrationNameAvailabilityResource`
  - Deleted or renamed model `MigrationResource`
  - Deleted or renamed model `MigrationSubState`
  - Deleted or renamed model `MigrationSubStateDetails`
  - Deleted or renamed model `NameAvailability`
  - Deleted or renamed model `OnlineResizeSupportedEnum`
  - Deleted or renamed model `Origin`
  - Deleted or renamed model `OverwriteDbsInTargetEnum`
  - Deleted or renamed model `PasswordAuthEnum`
  - Deleted or renamed model `ReplicationPromoteOption`
  - Deleted or renamed model `RestrictedEnum`
  - Deleted or renamed model `ServerBackup`
  - Deleted or renamed model `ServerForUpdate`
  - Deleted or renamed model `ServerHAState`
  - Deleted or renamed model `ServerThreatProtectionSettingsModel`
  - Deleted or renamed model `ServerVersion`
  - Deleted or renamed model `StartDataMigrationEnum`
  - Deleted or renamed model `StorageAutoGrowthSupportedEnum`
  - Deleted or renamed model `TriggerCutoverEnum`
  - Deleted or renamed model `VirtualEndpointResource`
  - Deleted or renamed model `VirtualNetworkSubnetUsageResult`
  - Deleted or renamed model `ZoneRedundantHaAndGeoBackupSupportedEnum`
  - Deleted or renamed model `ZoneRedundantHaSupportedEnum`
  - Method `MigrationsOperations.create` inserted a `positional_or_keyword` parameter `server_name`
  - Method `MigrationsOperations.create` deleted or renamed its parameter `subscription_id` of kind `positional_or_keyword`
  - Method `MigrationsOperations.create` deleted or renamed its parameter `target_db_server_name` of kind `positional_or_keyword`
  - Method `MigrationsOperations.get` inserted a `positional_or_keyword` parameter `server_name`
  - Method `MigrationsOperations.get` deleted or renamed its parameter `subscription_id` of kind `positional_or_keyword`
  - Method `MigrationsOperations.get` deleted or renamed its parameter `target_db_server_name` of kind `positional_or_keyword`
  - Method `MigrationsOperations.list_by_target_server` inserted a `positional_or_keyword` parameter `server_name`
  - Method `MigrationsOperations.list_by_target_server` deleted or renamed its parameter `subscription_id` of kind `positional_or_keyword`
  - Method `MigrationsOperations.list_by_target_server` deleted or renamed its parameter `target_db_server_name` of kind `positional_or_keyword`
  - Method `MigrationsOperations.update` inserted a `positional_or_keyword` parameter `server_name`
  - Method `MigrationsOperations.update` deleted or renamed its parameter `subscription_id` of kind `positional_or_keyword`
  - Method `MigrationsOperations.update` deleted or renamed its parameter `target_db_server_name` of kind `positional_or_keyword`
  - Deleted or renamed method `MigrationsOperations.delete`
  - Deleted or renamed method `ServerThreatProtectionSettingsOperations.get`
  - Deleted or renamed method `ServerThreatProtectionSettingsOperations.list_by_server`
  - Deleted or renamed method `ServersOperations.begin_create`
  - Deleted or renamed method `ServersOperations.list`
  - Deleted or renamed method `VirtualNetworkSubnetUsageOperations.execute`
  - Deleted or renamed model `AdministratorsOperations`
  - Deleted or renamed model `BackupsOperations`
  - Deleted or renamed model `CheckNameAvailabilityOperations`
  - Deleted or renamed model `CheckNameAvailabilityWithLocationOperations`
  - Deleted or renamed model `FlexibleServerOperations`
  - Deleted or renamed model `GetPrivateDnsZoneSuffixOperations`
  - Deleted or renamed model `LocationBasedCapabilitiesOperations`
  - Deleted or renamed model `LogFilesOperations`
  - Deleted or renamed model `LtrBackupOperationsOperations`
  - Deleted or renamed model `PostgreSQLManagementClientOperationsMixin`
  - Deleted or renamed model `PrivateEndpointConnectionOperations`
  - Deleted or renamed model `ServerCapabilitiesOperations`

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
