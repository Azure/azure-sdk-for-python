# Release History

## 3.0.0b1 (2026-07-07)

### Features Added

  - Client `WebPubSubManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `WebPubSubManagementClient` added method `send_request`
  - Client `WebPubSubManagementClient` added operation group `web_pub_sub_persistent_storages`
  - Model `EventHandler` added property `group_presence_events`
  - Model `WebPubSubHubProperties` added property `chat`
  - Added model `ApplicationFirewallSettings`
  - Added model `ChatSettings`
  - Added model `ClientConnectionCountRule`
  - Added enum `ClientConnectionCountRuleDiscriminator`
  - Added model `ClientTrafficControlRule`
  - Added enum `ClientTrafficControlRuleDiscriminator`
  - Added model `GroupPresenceEventFilters`
  - Added enum `GroupPresenceEventName`
  - Added model `PersistentStorage`
  - Added model `PersistentStorageProperties`
  - Added model `ThrottleByJwtCustomClaimRule`
  - Added model `ThrottleByJwtSignatureRule`
  - Added model `ThrottleByUserIdRule`
  - Added model `TrafficThrottleByJwtCustomClaimRule`
  - Added model `TrafficThrottleByJwtSignatureRule`
  - Added model `TrafficThrottleByUserIdRule`
  - Added operation group `WebPubSubPersistentStoragesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `CustomCertificate` moved instance variable `provisioning_state`, `key_vault_base_uri`, `key_vault_secret_name` and `key_vault_secret_version` under property `properties` whose type is `CustomCertificateProperties`
  - Model `CustomDomain` moved instance variable `provisioning_state`, `domain_name` and `custom_certificate` under property `properties` whose type is `CustomDomainProperties`
  - Model `PrivateEndpointConnection` moved instance variable `provisioning_state`, `private_endpoint`, `group_ids` and `private_link_service_connection_state` under property `properties` whose type is `PrivateEndpointConnectionProperties`
  - Model `PrivateLinkResource` moved instance variable `group_id`, `required_members`, `required_zone_names` and `shareable_private_link_resource_types` under property `properties` whose type is `PrivateLinkResourceProperties`
  - Model `Replica` moved instance variable `provisioning_state`, `region_endpoint_enabled` and `resource_stopped` under property `properties` whose type is `ReplicaProperties`
  - Model `SharedPrivateLinkResource` moved instance variable `group_id`, `private_link_resource_id`, `provisioning_state`, `request_message` and `status` under property `properties` whose type is `SharedPrivateLinkResourceProperties`
  - Model `WebPubSubResource` moved instance variable `provisioning_state`, `external_ip`, `host_name`, `public_port`, `server_port`, `version`, `private_endpoint_connections`, `shared_private_link_resources`, `tls`, `host_name_prefix`, `live_trace_configuration`, `resource_log_configuration`, `network_ac_ls`, `public_network_access`, `disable_local_auth`, `disable_aad_auth`, `region_endpoint_enabled`, `resource_stopped` and `socket_io` under property `properties` whose type is `WebPubSubProperties`

### Other Changes

  - Deleted model `CustomCertificateList`/`CustomDomainList`/`OperationList`/`PrivateEndpointConnectionList`/`PrivateLinkResourceList`/`ReplicaList`/`SharedPrivateLinkResourceList`/`SignalRServiceUsageList`/`WebPubSubHubList`/`WebPubSubResourceList` which actually were not used by SDK users

## 2.0.0 (2024-09-23)

### Features Added

  - The 'WebPubSubManagementClient' client had operation group 'web_pub_sub_replicas' added in the current version
  - The 'WebPubSubManagementClient' client had operation group 'web_pub_sub_replica_shared_private_link_resources' added in the current version
  - The 'WebPubSubManagementClient' client had operation group 'web_pub_sub_replicas' added in the current version
  - The 'WebPubSubManagementClient' client had operation group 'web_pub_sub_replica_shared_private_link_resources' added in the current version
  - The 'WebPubSubOperations' method 'list_replica_skus' was added in the current version
  - The model or publicly exposed class 'WebPubSubReplicaSharedPrivateLinkResourcesOperations' was added in the current version
  - The model or publicly exposed class 'WebPubSubReplicasOperations' was added in the current version
  - The 'WebPubSubOperations' method 'list_replica_skus' was added in the current version
  - The model or publicly exposed class 'WebPubSubReplicaSharedPrivateLinkResourcesOperations' was added in the current version
  - The model or publicly exposed class 'WebPubSubReplicasOperations' was added in the current version
  - The model or publicly exposed class 'Resource' had property 'system_data' added in the current version
  - The model or publicly exposed class 'WebPubSubHubProperties' had property 'web_socket_keep_alive_interval_in_seconds' added in the current version
  - The model or publicly exposed class 'WebPubSubNetworkACLs' had property 'ip_rules' added in the current version
  - The model or publicly exposed class 'WebPubSubResource' had property 'kind' added in the current version
  - The model or publicly exposed class 'WebPubSubResource' had property 'region_endpoint_enabled' added in the current version
  - The model or publicly exposed class 'WebPubSubResource' had property 'resource_stopped' added in the current version
  - The model or publicly exposed class 'WebPubSubResource' had property 'socket_io' added in the current version
  - The model or publicly exposed class 'IPRule' was added in the current version
  - The model or publicly exposed class 'Replica' was added in the current version
  - The model or publicly exposed class 'ReplicaList' was added in the current version
  - The model or publicly exposed class 'ServiceKind' was added in the current version
  - The model or publicly exposed class 'WebPubSubSocketIOSettings' was added in the current version

### Breaking Changes

  - Parameter `location` of model `TrackedResource` is now required
  - Parameter `location` of model `WebPubSubResource` is now required

## 2.0.0b2 (2023-10-23)

### Features Added

  - Model Replica has a new parameter region_endpoint_enabled
  - Model Replica has a new parameter resource_stopped
  - Model WebPubSubNetworkACLs has a new parameter ip_rules
  - Model WebPubSubResource has a new parameter region_endpoint_enabled
  - Model WebPubSubResource has a new parameter resource_stopped

## 2.0.0b1 (2023-07-21)

### Features Added

  - Added operation WebPubSubOperations.list_replica_skus
  - Added operation group WebPubSubReplicasOperations
  - Model PrivateLinkResource has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model WebPubSubResource has a new parameter kind

### Breaking Changes

  - Parameter location of model TrackedResource is now required
  - Parameter location of model WebPubSubResource is now required

## 1.1.0 (2023-03-20)

### Features Added

  - Added operation group WebPubSubCustomCertificatesOperations
  - Added operation group WebPubSubCustomDomainsOperations
  - Model WebPubSubHubProperties has a new parameter event_listeners

## 1.1.0b1 (2022-11-02)

### Features Added

  - Added operation group WebPubSubCustomCertificatesOperations
  - Added operation group WebPubSubCustomDomainsOperations
  - Model WebPubSubHubProperties has a new parameter event_listeners

## 1.0.0 (2021-10-11)

**Features**

  - Model PrivateEndpointConnection has a new parameter group_ids
  - Model WebPubSubResource has a new parameter host_name_prefix
  - Model WebPubSubResource has a new parameter disable_local_auth
  - Model WebPubSubResource has a new parameter resource_log_configuration
  - Model WebPubSubResource has a new parameter live_trace_configuration
  - Model WebPubSubResource has a new parameter disable_aad_auth
  - Added operation WebPubSubOperations.list_skus
  - Added operation group WebPubSubHubsOperations

**Breaking changes**

  - Model WebPubSubResource no longer has parameter features 
  - Model WebPubSubResource no longer has parameter event_handler

## 1.0.0b1 (2021-04-16)

* Initial Release
