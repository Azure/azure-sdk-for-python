# Release History

## 1.0.0 (2025-10-22)

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
  - Added model `PrivateEndpointConnectionsOperations`
  - Added model `PrivateLinkResourcesOperations`

### Breaking Changes

  - Model `AdvancedThreatProtectionForUpdate` deleted or renamed its instance variable `state`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `administrator_type`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `login`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `sid`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `tenant_id`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `identity_resource_id`
  - Model `Capability` deleted or renamed its instance variable `supported_geo_backup_regions`
  - Model `Capability` deleted or renamed its instance variable `supported_flexible_server_editions`
  - Model `Capability` deleted or renamed its instance variable `supported_server_versions`
  - Model `Capability` deleted or renamed its instance variable `supported_features`
  - Model `MaintenanceUpdate` deleted or renamed its instance variable `maintenance_start_time`
  - Model `OperationProgressResult` deleted or renamed its instance variable `object_type`
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
  - Deleted or renamed model `CapabilitySetsList`
  - Deleted or renamed model `Provisioning`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `keyword` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `LocationBasedCapabilitySetOperations.get` removed default value `None` from its parameter `capability_set_name`

## 1.0.0 (2025-10-13)

### Features Added

  - Model `AzureADAdministrator` added property `properties`
  - Model `Capability` added property `properties`
  - Model `MaintenanceWindow` added property `batch_of_maintenance`
  - Model `OperationProgressResult` added property `properties`
  - Model `ServerBackupV2` added property `properties`
  - Model `ServerForUpdate` added property `properties`
  - Enum `ServerVersion` added member `ENUM_5_7`
  - Enum `ServerVersion` added member `ENUM_8_0_21`
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
  - Added model `PrivateEndpointConnectionsOperations`
  - Added model `PrivateLinkResourcesOperations`

### Breaking Changes

  - Deleted or renamed client `MySQLManagementClient`
  - Model `AdvancedThreatProtectionForUpdate` deleted or renamed its instance variable `state`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `administrator_type`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `login`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `sid`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `tenant_id`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `identity_resource_id`
  - Model `Capability` deleted or renamed its instance variable `supported_geo_backup_regions`
  - Model `Capability` deleted or renamed its instance variable `supported_flexible_server_editions`
  - Model `Capability` deleted or renamed its instance variable `supported_server_versions`
  - Model `Capability` deleted or renamed its instance variable `supported_features`
  - Model `MaintenanceUpdate` deleted or renamed its instance variable `maintenance_start_time`
  - Model `OperationProgressResult` deleted or renamed its instance variable `object_type`
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
  - Deleted or renamed enum value `ServerVersion.EIGHT0_21`
  - Deleted or renamed enum value `ServerVersion.FIVE7`
  - Model `ValidateBackupResponse` deleted or renamed its instance variable `number_of_containers`
  - Deleted or renamed model `CapabilitySetsList`
  - Deleted or renamed model `Provisioning`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `keyword` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `LocationBasedCapabilitySetOperations.get` removed default value `None` from its parameter `capability_set_name`

## 1.0.0 (2025-10-13)

### Features Added

  - Model `AzureADAdministrator` added property `properties`
  - Model `Capability` added property `properties`
  - Model `MaintenanceWindow` added property `batch_of_maintenance`
  - Model `OperationProgressResult` added property `properties`
  - Model `ServerBackupV2` added property `properties`
  - Model `ServerForUpdate` added property `properties`
  - Enum `ServerVersion` added member `ENUM_5_7`
  - Enum `ServerVersion` added member `ENUM_8_0_21`
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
  - Added model `PrivateEndpointConnectionsOperations`
  - Added model `PrivateLinkResourcesOperations`

### Breaking Changes

  - Deleted or renamed client `MySQLManagementClient`
  - Model `AdvancedThreatProtectionForUpdate` deleted or renamed its instance variable `state`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `administrator_type`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `login`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `sid`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `tenant_id`
  - Model `AzureADAdministrator` deleted or renamed its instance variable `identity_resource_id`
  - Model `Capability` deleted or renamed its instance variable `supported_geo_backup_regions`
  - Model `Capability` deleted or renamed its instance variable `supported_flexible_server_editions`
  - Model `Capability` deleted or renamed its instance variable `supported_server_versions`
  - Model `Capability` deleted or renamed its instance variable `supported_features`
  - Model `MaintenanceUpdate` deleted or renamed its instance variable `maintenance_start_time`
  - Model `OperationProgressResult` deleted or renamed its instance variable `object_type`
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
  - Deleted or renamed enum value `ServerVersion.EIGHT0_21`
  - Deleted or renamed enum value `ServerVersion.FIVE7`
  - Model `ValidateBackupResponse` deleted or renamed its instance variable `number_of_containers`
  - Deleted or renamed model `CapabilitySetsList`
  - Deleted or renamed model `Provisioning`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `keyword` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page` from `positional_or_keyword` to `keyword_only`
  - Method `ConfigurationsOperations.list_by_server` changed its parameter `page_size` from `positional_or_keyword` to `keyword_only`
  - Method `LocationBasedCapabilitySetOperations.get` removed default value `None` from its parameter `capability_set_name`

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
