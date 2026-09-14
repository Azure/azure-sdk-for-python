# Release History

## 1.1.0b2 (2026-07-07)

### Features Added

  - Client `CosmosdbForPostgresqlMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `CosmosdbForPostgresqlMgmtClient` added method `send_request`
  - Model `Cluster` added property `identity`
  - Model `ClusterForUpdate` added property `identity`
  - Model `NameAvailabilityRequest` added property `type`
  - Model `Operation` added property `action_type`
  - Added enum `AadEnabledEnum`
  - Added enum `ActionType`
  - Added enum `CheckNameAvailabilityResourceType`
  - Added model `DataEncryption`
  - Added enum `DataEncryptionType`
  - Added model `IdentityProperties`
  - Added enum `IdentityType`
  - Added enum `PasswordEnabledEnum`
  - Added model `RolePropertiesExternalIdentity`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `Cluster` moved instance variable `administrator_login`, `administrator_login_password`, `provisioning_state`, `state`, `postgresql_version`, `citus_version`, `maintenance_window`, `preferred_primary_zone`, `enable_shards_on_coordinator`, `enable_ha`, `coordinator_server_edition`, `coordinator_storage_quota_in_mb`, `coordinator_v_cores`, `coordinator_enable_public_ip_access`, `node_server_edition`, `node_count`, `node_storage_quota_in_mb`, `node_v_cores`, `node_enable_public_ip_access`, `server_names`, `source_resource_id`, `source_location`, `point_in_time_utc`, `read_replicas`, `earliest_restore_time`, `private_endpoint_connections`, `database_name`, `enable_geo_backup` and `auth_config` under property `properties` whose type is `ClusterProperties`
  - Model `ClusterForUpdate` moved instance variable `administrator_login_password`, `postgresql_version`, `citus_version`, `enable_shards_on_coordinator`, `enable_ha`, `preferred_primary_zone`, `coordinator_server_edition`, `coordinator_storage_quota_in_mb`, `coordinator_v_cores`, `coordinator_enable_public_ip_access`, `node_server_edition`, `node_count`, `node_storage_quota_in_mb`, `node_v_cores`, `node_enable_public_ip_access` and `maintenance_window` under property `properties` whose type is `ClusterPropertiesForUpdate`
  - Model `ClusterServer` moved instance variable `server_edition`, `storage_quota_in_mb`, `v_cores`, `enable_ha`, `enable_public_ip_access`, `is_read_only`, `administrator_login`, `fully_qualified_domain_name`, `role`, `state`, `ha_state`, `availability_zone`, `postgresql_version` and `citus_version` under property `properties` whose type is `ClusterServerProperties`
  - Model `Configuration` moved instance variable `description`, `data_type`, `allowed_values`, `requires_restart`, `server_role_group_configurations` and `provisioning_state` under property `properties` whose type is `ConfigurationProperties`
  - Model `FirewallRule` moved instance variable `start_ip_address`, `end_ip_address` and `provisioning_state` under property `properties` whose type is `FirewallRuleProperties`
  - Model `Operation` deleted or renamed its instance variable `properties`
  - Model `PrivateEndpointConnection` moved instance variable `group_ids`, `private_endpoint`, `private_link_service_connection_state` and `provisioning_state` under property `properties` whose type is `PrivateEndpointConnectionProperties`
  - Model `PrivateLinkResource` moved instance variable `group_id`, `required_members` and `required_zone_names` under property `properties` whose type is `PrivateLinkResourceProperties`
  - Model `Role` moved instance variable `role_type`, `password`, `provisioning_state`, `object_id`, `principal_type` and `tenant_id` under property `properties` whose type is `RoleProperties`
  - Model `ServerConfiguration` moved instance variable `value`, `source`, `description`, `default_value`, `data_type`, `allowed_values`, `requires_restart` and `provisioning_state` under property `properties` whose type is `ServerConfigurationProperties`
  - Model `SimplePrivateEndpointConnection` moved instance variable `private_endpoint`, `group_ids` and `private_link_service_connection_state` under property `properties` whose type is `PrivateEndpointConnectionSimpleProperties`
  - Renamed enum `OperationOrigin` to `Origin`

### Other Changes

  - Deleted model `ClusterConfigurationListResult`/`ClusterListResult`/`ClusterServerListResult`/`FirewallRuleListResult`/`OperationListResult`/`PrivateEndpointConnectionListResult`/`PrivateLinkResourceListResult`/`RoleListResult`/`ServerConfigurationListResult` which actually were not used by SDK users

## 1.1.0b1 (2024-03-18)

### Features Added

  - Model Cluster has a new parameter auth_config
  - Model Cluster has a new parameter database_name
  - Model Cluster has a new parameter enable_geo_backup
  - Model Role has a new parameter object_id
  - Model Role has a new parameter principal_type
  - Model Role has a new parameter role_type
  - Model Role has a new parameter tenant_id
  - Operation ClustersOperations.begin_promote_read_replica has a new optional parameter promote_request

## 1.0.0 (2023-09-20)

### Other Changes

  - First GA

## 1.0.0b1 (2023-06-16)

* Initial Release
