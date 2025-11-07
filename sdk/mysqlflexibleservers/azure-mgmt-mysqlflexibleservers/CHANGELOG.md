# Release History

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
  - Added model `PrivateEndpointConnectionsOperations`
  - Added model `PrivateLinkResourcesOperations`

### Breaking Changes

  - Model `OperationProgressResult` deleted or renamed its instance variable `object_type`
  - Method `Storage.__init__` parameter `storage_redundancy` changed default value from `None` to `str`
  - Deleted or renamed model `Provisioning`

## 1.0.0 (2025-11-07)

### Features Added

  - Model `MySQLManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `MySQLManagementClient` added method `send_request`
  - Client `MySQLManagementClient` added operation group `private_endpoint_connections`
  - Client `MySQLManagementClient` added operation group `private_link_resources`
  - Model `AzureADAdministrator` added property `properties`
  - Model `Capability` added property `properties`
  - Model `MaintenanceWindow` added property `batch_of_maintenance`
  - Model `OperationProgressResult` added property `properties`
  - Model `ServerBackupV2` added property `properties`
  - Model `ServerForUpdate` added property `properties`
  - Added model `AdministratorProperties`
  - Added model `AdvancedThreatProtectionUpdateProperties`
  - Added enum `BatchOfMaintenance`
  - Added model `CapabilityPropertiesV2`
  - Added model `MaintenancePropertiesForUpdate`
  - Added enum `Origin`
  - Added model `PrivateEndpointConnectionListResult`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceProperties`
  - Added model `ServerBackupPropertiesV2`
  - Added model `ServerPropertiesForUpdate`
  - Added model `ValidateBackupResponseProperties`
  - Added operation group `PrivateEndpointConnectionsOperations`
  - Added operation group `PrivateLinkResourcesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `AdvancedThreatProtectionForUpdate` instance variable `state` have been moved under property `properties`
  - Model `AzureADAdministrator` instance variables `administrator_type`, `login`, `sid`, `tenant_id`, and `identity_resource_id` have been moved under property `properties`
  - Model `Capability` instance variables `supported_geo_backup_regions`, `supported_flexible_server_editions`, `supported_server_versions`, and `supported_features` have been moved under property `properties`
  - Model `MaintenanceUpdate` instance variable `maintenance_start_time` have been moved under property `properties`
  - Model `OperationProgressResult` instance variable `object_type` has been moved under property `properties`
  - Model `ServerBackupV2` instance variables `backup_name_v2`, `backup_type`, `completed_time`, `source`, and `provisioning_state` have been moved under property `properties`
  - Model `ServerForUpdate` instance variables `administrator_login_password`, `version`, `storage`, `backup`, `high_availability`, `maintenance_policy`, `maintenance_window`, `replication_role`, `data_encryption`, and `network` have been moved under property `properties`
  - Model `ValidateBackupResponse` instance variable `number_of_containers` have been moved under property `properties`
  - Deleted or renamed model `CapabilitySetsList`
  - Deleted or renamed model `Provisioning`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `keyword` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Parameter `capability_set_name` of `LocationBasedCapabilitySetOperations.get` is now required

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
