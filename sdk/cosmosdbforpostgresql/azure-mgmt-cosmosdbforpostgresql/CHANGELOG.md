# Release History

## 1.1.0b2 (2026-07-07)

### Features Added

  - Client `CosmosdbForPostgresqlMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `CosmosdbForPostgresqlMgmtClient` added method `send_request`
  - Model `Cluster` added property `properties`
  - Model `Cluster` added property `identity`
  - Model `ClusterForUpdate` added property `properties`
  - Model `ClusterForUpdate` added property `identity`
  - Model `ClusterServer` added property `properties`
  - Model `Configuration` added property `properties`
  - Model `FirewallRule` added property `properties`
  - Model `NameAvailabilityRequest` added property `type`
  - Model `Operation` added property `action_type`
  - Model `PrivateEndpointConnection` added property `properties`
  - Model `PrivateLinkResource` added property `properties`
  - Model `Role` added property `properties`
  - Model `ServerConfiguration` added property `properties`
  - Model `SimplePrivateEndpointConnection` added property `properties`
  - Added enum `AadEnabledEnum`
  - Added enum `ActionType`
  - Added enum `CheckNameAvailabilityResourceType`
  - Added model `ClusterProperties`
  - Added model `ClusterPropertiesForUpdate`
  - Added model `ConfigurationProperties`
  - Added model `DataEncryption`
  - Added enum `DataEncryptionType`
  - Added model `FirewallRuleProperties`
  - Added model `IdentityProperties`
  - Added enum `IdentityType`
  - Added enum `Origin`
  - Added enum `PasswordEnabledEnum`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateEndpointConnectionSimpleProperties`
  - Added model `PrivateLinkResourceProperties`
  - Added model `RoleProperties`
  - Added model `RolePropertiesExternalIdentity`
  - Added model `ServerConfigurationProperties`
  - Added model `UserAssignedIdentity`

### Breaking Changes

  - Model `Cluster` deleted or renamed its instance variable `administrator_login`
  - Model `Cluster` deleted or renamed its instance variable `administrator_login_password`
  - Model `Cluster` deleted or renamed its instance variable `provisioning_state`
  - Model `Cluster` deleted or renamed its instance variable `state`
  - Model `Cluster` deleted or renamed its instance variable `postgresql_version`
  - Model `Cluster` deleted or renamed its instance variable `citus_version`
  - Model `Cluster` deleted or renamed its instance variable `maintenance_window`
  - Model `Cluster` deleted or renamed its instance variable `preferred_primary_zone`
  - Model `Cluster` deleted or renamed its instance variable `enable_shards_on_coordinator`
  - Model `Cluster` deleted or renamed its instance variable `enable_ha`
  - Model `Cluster` deleted or renamed its instance variable `coordinator_server_edition`
  - Model `Cluster` deleted or renamed its instance variable `coordinator_storage_quota_in_mb`
  - Model `Cluster` deleted or renamed its instance variable `coordinator_v_cores`
  - Model `Cluster` deleted or renamed its instance variable `coordinator_enable_public_ip_access`
  - Model `Cluster` deleted or renamed its instance variable `node_server_edition`
  - Model `Cluster` deleted or renamed its instance variable `node_count`
  - Model `Cluster` deleted or renamed its instance variable `node_storage_quota_in_mb`
  - Model `Cluster` deleted or renamed its instance variable `node_v_cores`
  - Model `Cluster` deleted or renamed its instance variable `node_enable_public_ip_access`
  - Model `Cluster` deleted or renamed its instance variable `server_names`
  - Model `Cluster` deleted or renamed its instance variable `source_resource_id`
  - Model `Cluster` deleted or renamed its instance variable `source_location`
  - Model `Cluster` deleted or renamed its instance variable `point_in_time_utc`
  - Model `Cluster` deleted or renamed its instance variable `read_replicas`
  - Model `Cluster` deleted or renamed its instance variable `earliest_restore_time`
  - Model `Cluster` deleted or renamed its instance variable `private_endpoint_connections`
  - Model `Cluster` deleted or renamed its instance variable `database_name`
  - Model `Cluster` deleted or renamed its instance variable `enable_geo_backup`
  - Model `Cluster` deleted or renamed its instance variable `auth_config`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `administrator_login_password`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `postgresql_version`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `citus_version`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `enable_shards_on_coordinator`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `enable_ha`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `preferred_primary_zone`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `coordinator_server_edition`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `coordinator_storage_quota_in_mb`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `coordinator_v_cores`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `coordinator_enable_public_ip_access`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `node_server_edition`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `node_count`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `node_storage_quota_in_mb`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `node_v_cores`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `node_enable_public_ip_access`
  - Model `ClusterForUpdate` deleted or renamed its instance variable `maintenance_window`
  - Model `ClusterServer` deleted or renamed its instance variable `server_edition`
  - Model `ClusterServer` deleted or renamed its instance variable `storage_quota_in_mb`
  - Model `ClusterServer` deleted or renamed its instance variable `v_cores`
  - Model `ClusterServer` deleted or renamed its instance variable `enable_ha`
  - Model `ClusterServer` deleted or renamed its instance variable `enable_public_ip_access`
  - Model `ClusterServer` deleted or renamed its instance variable `is_read_only`
  - Model `ClusterServer` deleted or renamed its instance variable `administrator_login`
  - Model `ClusterServer` deleted or renamed its instance variable `fully_qualified_domain_name`
  - Model `ClusterServer` deleted or renamed its instance variable `role`
  - Model `ClusterServer` deleted or renamed its instance variable `state`
  - Model `ClusterServer` deleted or renamed its instance variable `ha_state`
  - Model `ClusterServer` deleted or renamed its instance variable `availability_zone`
  - Model `ClusterServer` deleted or renamed its instance variable `postgresql_version`
  - Model `ClusterServer` deleted or renamed its instance variable `citus_version`
  - Model `Configuration` deleted or renamed its instance variable `description`
  - Model `Configuration` deleted or renamed its instance variable `data_type`
  - Model `Configuration` deleted or renamed its instance variable `allowed_values`
  - Model `Configuration` deleted or renamed its instance variable `requires_restart`
  - Model `Configuration` deleted or renamed its instance variable `server_role_group_configurations`
  - Model `Configuration` deleted or renamed its instance variable `provisioning_state`
  - Model `FirewallRule` deleted or renamed its instance variable `start_ip_address`
  - Model `FirewallRule` deleted or renamed its instance variable `end_ip_address`
  - Model `FirewallRule` deleted or renamed its instance variable `provisioning_state`
  - Model `Operation` deleted or renamed its instance variable `properties`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `group_ids`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_endpoint`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_link_service_connection_state`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `group_id`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_members`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_zone_names`
  - Model `Role` deleted or renamed its instance variable `role_type`
  - Model `Role` deleted or renamed its instance variable `password`
  - Model `Role` deleted or renamed its instance variable `provisioning_state`
  - Model `Role` deleted or renamed its instance variable `object_id`
  - Model `Role` deleted or renamed its instance variable `principal_type`
  - Model `Role` deleted or renamed its instance variable `tenant_id`
  - Model `ServerConfiguration` deleted or renamed its instance variable `value`
  - Model `ServerConfiguration` deleted or renamed its instance variable `source`
  - Model `ServerConfiguration` deleted or renamed its instance variable `description`
  - Model `ServerConfiguration` deleted or renamed its instance variable `default_value`
  - Model `ServerConfiguration` deleted or renamed its instance variable `data_type`
  - Model `ServerConfiguration` deleted or renamed its instance variable `allowed_values`
  - Model `ServerConfiguration` deleted or renamed its instance variable `requires_restart`
  - Model `ServerConfiguration` deleted or renamed its instance variable `provisioning_state`
  - Model `SimplePrivateEndpointConnection` deleted or renamed its instance variable `private_endpoint`
  - Model `SimplePrivateEndpointConnection` deleted or renamed its instance variable `group_ids`
  - Model `SimplePrivateEndpointConnection` deleted or renamed its instance variable `private_link_service_connection_state`
  - Deleted or renamed model `ClusterConfigurationListResult`
  - Deleted or renamed model `ClusterListResult`
  - Deleted or renamed model `ClusterServerListResult`
  - Deleted or renamed model `FirewallRuleListResult`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `OperationOrigin`
  - Deleted or renamed model `PrivateEndpointConnectionListResult`
  - Deleted or renamed model `PrivateLinkResourceListResult`
  - Deleted or renamed model `RoleListResult`
  - Deleted or renamed model `ServerConfigurationListResult`

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
