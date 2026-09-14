# Release History

## 1.1.0b3 (2026-07-08)

### Features Added

  - Client `MySQLManagementClient` added method `send_request`
  - Client `MySQLManagementClient` added operation group `fabric_mirroring_settings`
  - Enum `CreateMode` added member `RENAME`
  - Added enum `FabricMirroringProvisioningState`
  - Added model `FabricMirroringSetting`
  - Added model `FabricMirroringSettingListResult`
  - Added enum `FabricMirroringSettingsName`
  - Added model `FabricMirroringSettingsProperties`
  - Added enum `FabricMirroringState`
  - Added operation group `FabricMirroringSettingsOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AdvancedThreatProtection` moved instance variable `creation_time`, `state` and `provisioning_state` under property `properties` whose type is `AdvancedThreatProtectionProperties`
  - Model `AdvancedThreatProtectionForUpdate` moved instance variable `state` under property `properties` whose type is `AdvancedThreatProtectionUpdateProperties`
  - Model `AzureADAdministrator` moved instance variable `administrator_type`, `login`, `sid`, `tenant_id` and `identity_resource_id` under property `properties` whose type is `AdministratorProperties`
  - Model `BackupAndExportResponse` moved instance variable `datasource_size_in_bytes`, `data_transferred_in_bytes` and `backup_metadata` under property `properties` whose type is `BackupAndExportResponseProperties`
  - Model `Capability` moved instance variable `supported_geo_backup_regions`, `supported_flexible_server_editions`, `supported_server_versions` and `supported_features` under property `properties` whose type is `CapabilityPropertiesV2`
  - Model `Configuration` moved instance variable `value`, `current_value`, `description`, `documentation_link`, `default_value`, `data_type`, `allowed_values`, `source`, `is_read_only`, `is_config_pending_restart` and `is_dynamic_config` under property `properties` whose type is `ConfigurationProperties`
  - Model `ConfigurationForBatchUpdate` moved instance variable `value` and `source` under property `properties` whose type is `ConfigurationForBatchUpdateProperties`
  - Model `Database` moved instance variable `charset` and `collation` under property `properties` whose type is `DatabaseProperties`
  - Model `FirewallRule` moved instance variable `start_ip_address` and `end_ip_address` under property `properties` whose type is `FirewallRuleProperties`
  - Model `LogFile` moved instance variable `size_in_kb`, `created_time`, `type_properties_type`, `last_modified_time` and `url` under property `properties` whose type is `LogFileProperties`
  - Model `Maintenance` moved instance variable `maintenance_type`, `maintenance_state`, `maintenance_start_time`, `maintenance_end_time`, `maintenance_execution_start_time`, `maintenance_execution_end_time`, `maintenance_available_schedule_min_time`, `maintenance_available_schedule_max_time`, `maintenance_title`, `maintenance_description` and `provisioning_state` under property `properties` whose type is `MaintenanceProperties`
  - Model `MaintenanceUpdate` moved instance variable `maintenance_start_time` under property `properties` whose type is `MaintenancePropertiesForUpdate`
  - Model `PrivateEndpointConnection` moved instance variable `group_ids`, `private_endpoint`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `PrivateEndpointConnectionProperties`
  - Model `PrivateLinkResource` moved instance variable `group_id`, `required_members` and `required_zone_names` under property `properties` whose type is `PrivateLinkResourceProperties`
  - Model `Server` moved instance variable `administrator_login`, `administrator_login_password`, `version`, `full_version`, `availability_zone`, `create_mode`, `source_server_resource_id`, `restore_point_in_time`, `replication_role`, `replica_capacity`, `data_encryption`, `state`, `fully_qualified_domain_name`, `database_port`, `storage`, `backup`, `high_availability`, `network`, `private_endpoint_connections`, `maintenance_policy`, `maintenance_window`, `import_source_properties` and `lower_case_table_names` under property `properties` whose type is `ServerProperties`
  - Model `ServerBackup` moved instance variable `backup_type`, `completed_time` and `source` under property `properties` whose type is `ServerBackupProperties`
  - Model `ServerBackupV2` moved instance variable `backup_name_v2`, `backup_type`, `completed_time`, `source` and `provisioning_state` under property `properties` whose type is `ServerBackupPropertiesV2`
  - Model `ServerForUpdate` moved instance variable `administrator_login_password`, `version`, `storage`, `backup`, `high_availability`, `maintenance_policy`, `maintenance_window`, `replication_role`, `data_encryption` and `network` under property `properties` whose type is `ServerPropertiesForUpdate`
  - Model `ValidateBackupResponse` moved instance variable `number_of_containers` under property `properties` whose type is `ValidateBackupResponseProperties`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags`/`keyword`/`page`/`page_size` from `positional_or_keyword` to `keyword_only`
  - Parameter `capability_set_name` of method `LocationBasedCapabilitySetOperations.get` is now required
  - Method `PrivateLinkResourcesOperations.list_by_server` changed return type from `PrivateLinkResourceListResult` to `ItemPaged[_models.PrivateLinkResource]`

### Other Changes

  - Deleted model `AdministratorListResult`/`AdvancedThreatProtectionListResult`/`CapabilitiesListResult`/`CapabilitySetsList`/`DatabaseListResult`/`FirewallRuleListResult`/`LogFileListResult`/`MaintenanceListResult`/`OperationListResult`/`PrivateLinkResourceListResult`/`ServerBackupListResult`/`ServerBackupV2ListResult`/`ServerListResult` which actually were not used by SDK users

## 1.1.0b2 (2025-12-12)

### Bugs Fixed

  - Set default value of `lro_options` same as old version to keep compatibility for some LRO APIs

## 1.1.0b1 (2025-11-19)

### Features Added

  - Model `HighAvailability` added property `replication_mode`
  - Model `Server` added property `lower_case_table_names`
  - Enum `ServerVersion` added member `EIGHT4`
  - Added enum `ReplicationMode`
  - Operation group  `LongRunningBackupOperations` added method `begin_delete`

## 1.0.0 (2025-11-07)

### Features Added

  - Model `MySQLManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `MySQLManagementClient` added operation group `private_endpoint_connections`
  - Client `MySQLManagementClient` added operation group `private_link_resources`
  - Model `MaintenanceWindow` added property `batch_of_maintenance`
  - Model `OperationProgressResult` added property `properties`
  - Added enum `BatchOfMaintenance`
  - Added enum `Origin`
  - Added model `PrivateEndpointConnectionListResult`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceListResult`
  - Added operation group `PrivateEndpointConnectionsOperations`
  - Added operation group `PrivateLinkResourcesOperations`

### Breaking Changes

  - Model `OperationProgressResult` instance variable `object_type` has been moved under property `properties`
  - Deleted unused model `Provisioning`

## 1.0.0b3 (2024-11-18)

### Features Added

  - Model `Capability` added property `supported_features`
  - Model `Server` added property `full_version`
  - Added model `FeatureProperty`

## 1.0.0b2 (2024-09-26)

### Features Added

  - Model `Server` added property `database_port`
  - Model `Server` added property `maintenance_policy`
  - Model `ServerForUpdate` added property `maintenance_policy`
  - Added model `MaintenancePolicy`
  - Added enum `PatchStrategy`

## 1.0.0b1 (2024-08-27)

### Other Changes

  - Initial version
