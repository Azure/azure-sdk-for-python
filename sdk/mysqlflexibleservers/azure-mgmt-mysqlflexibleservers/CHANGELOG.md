# Release History

## 1.1.0b3 (2026-07-07)

### Features Added

  - Client `MySQLManagementClient` added method `send_request`
  - Client `MySQLManagementClient` added operation group `fabric_mirroring_settings`
  - Model `AdvancedThreatProtection` added property `properties`
  - Model `AzureADAdministrator` added property `properties`
  - Model `BackupAndExportResponse` added property `properties`
  - Model `Capability` added property `properties`
  - Model `Configuration` added property `properties`
  - Model `ConfigurationForBatchUpdate` added property `properties`
  - Enum `CreateMode` added member `RENAME`
  - Model `Database` added property `properties`
  - Model `FirewallRule` added property `properties`
  - Model `LogFile` added property `properties`
  - Model `Maintenance` added property `properties`
  - Model `PrivateEndpointConnection` added property `properties`
  - Model `PrivateLinkResource` added property `properties`
  - Model `Server` added property `properties`
  - Model `ServerBackup` added property `properties`
  - Model `ServerBackupV2` added property `properties`
  - Model `ServerForUpdate` added property `properties`
  - Added model `AdministratorProperties`
  - Added model `AdvancedThreatProtectionProperties`
  - Added model `AdvancedThreatProtectionUpdateProperties`
  - Added model `BackupAndExportResponseProperties`
  - Added model `CapabilityPropertiesV2`
  - Added model `ConfigurationForBatchUpdateProperties`
  - Added model `ConfigurationProperties`
  - Added model `DatabaseProperties`
  - Added enum `FabricMirroringProvisioningState`
  - Added model `FabricMirroringSetting`
  - Added model `FabricMirroringSettingListResult`
  - Added enum `FabricMirroringSettingsName`
  - Added model `FabricMirroringSettingsProperties`
  - Added enum `FabricMirroringState`
  - Added model `FirewallRuleProperties`
  - Added model `LogFileProperties`
  - Added model `MaintenanceProperties`
  - Added model `MaintenancePropertiesForUpdate`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateLinkResourceProperties`
  - Added model `ServerBackupProperties`
  - Added model `ServerBackupPropertiesV2`
  - Added model `ServerProperties`
  - Added model `ServerPropertiesForUpdate`
  - Added model `ValidateBackupResponseProperties`
  - Added model `FabricMirroringSettingsOperations`

### Breaking Changes

  - Method `PrivateLinkResourcesOperations.list_by_server` changed from `asynchronous` to `synchronous`
  - Model `AdvancedThreatProtection` deleted or renamed its instance variable `creation_time`
  - Model `AdvancedThreatProtection` deleted or renamed its instance variable `state`
  - Model `AdvancedThreatProtection` deleted or renamed its instance variable `provisioning_state`
  - Model `AdvancedThreatProtectionForUpdate` deleted or renamed its instance variable `state`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `administrator_type`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `login`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `sid`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `tenant_id`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `identity_resource_id`
  - Model `BackupAndExportResponse` deleted or renamed its instance variable `datasource_size_in_bytes`
  - Model `BackupAndExportResponse` deleted or renamed its instance variable `data_transferred_in_bytes`
  - Model `BackupAndExportResponse` deleted or renamed its instance variable `backup_metadata`
  - Model `Capability` deleted or renamed its instance variable `supported_geo_backup_regions`
  - Model `Capability` deleted or renamed its instance variable `supported_flexible_server_editions`
  - Model `Capability` deleted or renamed its instance variable `supported_server_versions`
  - Model `Capability` deleted or renamed its instance variable `supported_features`
  - Model `Configuration` deleted or renamed its instance variable `value`
  - Model `Configuration` deleted or renamed its instance variable `current_value`
  - Model `Configuration` deleted or renamed its instance variable `description`
  - Model `Configuration` deleted or renamed its instance variable `documentation_link`
  - Model `Configuration` deleted or renamed its instance variable `default_value`
  - Model `Configuration` deleted or renamed its instance variable `data_type`
  - Model `Configuration` deleted or renamed its instance variable `allowed_values`
  - Model `Configuration` deleted or renamed its instance variable `source`
  - Model `Configuration` deleted or renamed its instance variable `is_read_only`
  - Model `Configuration` deleted or renamed its instance variable `is_config_pending_restart`
  - Model `Configuration` deleted or renamed its instance variable `is_dynamic_config`
  - Model `ConfigurationForBatchUpdate` deleted or renamed its instance variable `value`
  - Model `ConfigurationForBatchUpdate` deleted or renamed its instance variable `source`
  - Model `Database` deleted or renamed its instance variable `charset`
  - Model `Database` deleted or renamed its instance variable `collation`
  - Model `FirewallRule` deleted or renamed its instance variable `start_ip_address`
  - Model `FirewallRule` deleted or renamed its instance variable `end_ip_address`
  - Model `LogFile` deleted or renamed its instance variable `size_in_kb`
  - Model `LogFile` deleted or renamed its instance variable `created_time`
  - Model `LogFile` deleted or renamed its instance variable `type_properties_type`
  - Model `LogFile` deleted or renamed its instance variable `last_modified_time`
  - Model `LogFile` deleted or renamed its instance variable `url`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_type`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_state`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_start_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_end_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_execution_start_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_execution_end_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_available_schedule_min_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_available_schedule_max_time`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_title`
  - Model `Maintenance` deleted or renamed its instance variable `maintenance_description`
  - Model `Maintenance` deleted or renamed its instance variable `provisioning_state`
  - Model `MaintenanceUpdate` deleted or renamed its instance variable `maintenance_start_time`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `group_ids`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_endpoint`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_link_service_connection_state`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `group_id`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_members`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_zone_names`
  - Model `Server` deleted or renamed its instance variable `administrator_login`
  - Model `Server` deleted or renamed its instance variable `administrator_login_password`
  - Model `Server` deleted or renamed its instance variable `version`
  - Model `Server` deleted or renamed its instance variable `full_version`
  - Model `Server` deleted or renamed its instance variable `availability_zone`
  - Model `Server` deleted or renamed its instance variable `create_mode`
  - Model `Server` deleted or renamed its instance variable `source_server_resource_id`
  - Model `Server` deleted or renamed its instance variable `restore_point_in_time`
  - Model `Server` deleted or renamed its instance variable `replication_role`
  - Model `Server` deleted or renamed its instance variable `replica_capacity`
  - Model `Server` deleted or renamed its instance variable `data_encryption`
  - Model `Server` deleted or renamed its instance variable `state`
  - Model `Server` deleted or renamed its instance variable `fully_qualified_domain_name`
  - Model `Server` deleted or renamed its instance variable `database_port`
  - Model `Server` deleted or renamed its instance variable `storage`
  - Model `Server` deleted or renamed its instance variable `backup`
  - Model `Server` deleted or renamed its instance variable `high_availability`
  - Model `Server` deleted or renamed its instance variable `network`
  - Model `Server` deleted or renamed its instance variable `private_endpoint_connections`
  - Model `Server` deleted or renamed its instance variable `maintenance_policy`
  - Model `Server` deleted or renamed its instance variable `maintenance_window`
  - Model `Server` deleted or renamed its instance variable `import_source_properties`
  - Model `Server` deleted or renamed its instance variable `lower_case_table_names`
  - Model `ServerBackup` deleted or renamed its instance variable `backup_type`
  - Model `ServerBackup` deleted or renamed its instance variable `completed_time`
  - Model `ServerBackup` deleted or renamed its instance variable `source`
  - Model `ServerBackupV2` deleted or renamed its instance variable `backup_name_v2`
  - Model `ServerBackupV2` deleted or renamed its instance variable `backup_type`
  - Model `ServerBackupV2` deleted or renamed its instance variable `completed_time`
  - Model `ServerBackupV2` deleted or renamed its instance variable `source`
  - Model `ServerBackupV2` deleted or renamed its instance variable `provisioning_state`
  - Model `ServerForUpdate` deleted or renamed its instance variable `administrator_login_password`
  - Model `ServerForUpdate` deleted or renamed its instance variable `version`
  - Model `ServerForUpdate` deleted or renamed its instance variable `storage`
  - Model `ServerForUpdate` deleted or renamed its instance variable `backup`
  - Model `ServerForUpdate` deleted or renamed its instance variable `high_availability`
  - Model `ServerForUpdate` deleted or renamed its instance variable `maintenance_policy`
  - Model `ServerForUpdate` deleted or renamed its instance variable `maintenance_window`
  - Model `ServerForUpdate` deleted or renamed its instance variable `replication_role`
  - Model `ServerForUpdate` deleted or renamed its instance variable `data_encryption`
  - Model `ServerForUpdate` deleted or renamed its instance variable `network`
  - Model `ValidateBackupResponse` deleted or renamed its instance variable `number_of_containers`
  - Deleted or renamed model `AdministratorListResult`
  - Deleted or renamed model `AdvancedThreatProtectionListResult`
  - Deleted or renamed model `CapabilitiesListResult`
  - Deleted or renamed model `CapabilitySetsList`
  - Deleted or renamed model `DatabaseListResult`
  - Deleted or renamed model `FirewallRuleListResult`
  - Deleted or renamed model `LogFileListResult`
  - Deleted or renamed model `MaintenanceListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `PrivateLinkResourceListResult`
  - Deleted or renamed model `ServerBackupListResult`
  - Deleted or renamed model `ServerBackupV2ListResult`
  - Deleted or renamed model `ServerListResult`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `keyword` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `LocationBasedCapabilitySetOperations.get` removed default value `None` from its parameter `capability_set_name`
  - Method `PrivateLinkResourcesOperations.list_by_server` changed return type from `PrivateLinkResourceListResult` to `AsyncItemPaged[_models.PrivateLinkResource]`
  - Method `PrivateLinkResourcesOperations.list_by_server` changed return type from `PrivateLinkResourceListResult` to `ItemPaged[_models.PrivateLinkResource]`

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
