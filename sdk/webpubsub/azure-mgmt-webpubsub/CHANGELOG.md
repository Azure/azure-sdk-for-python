# Release History

## 3.0.0b1 (2026-07-07)

### Features Added

  - Client `WebPubSubManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `WebPubSubManagementClient` added method `send_request`
  - Client `WebPubSubManagementClient` added operation group `web_pub_sub_persistent_storages`
  - Model `CustomCertificate` added property `properties`
  - Model `CustomDomain` added property `properties`
  - Model `EventHandler` added property `group_presence_events`
  - Model `PrivateEndpointConnection` added property `properties`
  - Model `PrivateLinkResource` added property `properties`
  - Model `Replica` added property `properties`
  - Model `SharedPrivateLinkResource` added property `properties`
  - Model `WebPubSubHubProperties` added property `chat`
  - Model `WebPubSubResource` added property `properties`
  - Added model `ApplicationFirewallSettings`
  - Added model `ChatSettings`
  - Added model `ClientConnectionCountRule`
  - Added enum `ClientConnectionCountRuleDiscriminator`
  - Added model `ClientTrafficControlRule`
  - Added enum `ClientTrafficControlRuleDiscriminator`
  - Added model `CustomCertificateProperties`
  - Added model `CustomDomainProperties`
  - Added model `GroupPresenceEventFilters`
  - Added enum `GroupPresenceEventName`
  - Added model `PersistentStorage`
  - Added model `PersistentStorageProperties`
  - Added model `PrivateEndpointConnectionProperties`
  - Added model `PrivateLinkResourceProperties`
  - Added model `ReplicaProperties`
  - Added model `SharedPrivateLinkResourceProperties`
  - Added model `ThrottleByJwtCustomClaimRule`
  - Added model `ThrottleByJwtSignatureRule`
  - Added model `ThrottleByUserIdRule`
  - Added model `TrafficThrottleByJwtCustomClaimRule`
  - Added model `TrafficThrottleByJwtSignatureRule`
  - Added model `TrafficThrottleByUserIdRule`
  - Added model `WebPubSubProperties`
  - Added model `WebPubSubPersistentStoragesOperations`

### Breaking Changes

  - Model `CustomCertificate` deleted or renamed its instance variable `provisioning_state`
  - Model `CustomCertificate` deleted or renamed its instance variable `key_vault_base_uri`
  - Model `CustomCertificate` deleted or renamed its instance variable `key_vault_secret_name`
  - Model `CustomCertificate` deleted or renamed its instance variable `key_vault_secret_version`
  - Model `CustomDomain` deleted or renamed its instance variable `provisioning_state`
  - Model `CustomDomain` deleted or renamed its instance variable `domain_name`
  - Model `CustomDomain` deleted or renamed its instance variable `custom_certificate`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `provisioning_state`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_endpoint`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `group_ids`
  - Model `PrivateEndpointConnection` deleted or renamed its instance variable `private_link_service_connection_state`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `group_id`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_members`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `required_zone_names`
  - Model `PrivateLinkResource` deleted or renamed its instance variable `shareable_private_link_resource_types`
  - Model `Replica` deleted or renamed its instance variable `provisioning_state`
  - Model `Replica` deleted or renamed its instance variable `region_endpoint_enabled`
  - Model `Replica` deleted or renamed its instance variable `resource_stopped`
  - Model `SharedPrivateLinkResource` deleted or renamed its instance variable `group_id`
  - Model `SharedPrivateLinkResource` deleted or renamed its instance variable `private_link_resource_id`
  - Model `SharedPrivateLinkResource` deleted or renamed its instance variable `provisioning_state`
  - Model `SharedPrivateLinkResource` deleted or renamed its instance variable `request_message`
  - Model `SharedPrivateLinkResource` deleted or renamed its instance variable `status`
  - Model `WebPubSubResource` deleted or renamed its instance variable `provisioning_state`
  - Model `WebPubSubResource` deleted or renamed its instance variable `external_ip`
  - Model `WebPubSubResource` deleted or renamed its instance variable `host_name`
  - Model `WebPubSubResource` deleted or renamed its instance variable `public_port`
  - Model `WebPubSubResource` deleted or renamed its instance variable `server_port`
  - Model `WebPubSubResource` deleted or renamed its instance variable `version`
  - Model `WebPubSubResource` deleted or renamed its instance variable `private_endpoint_connections`
  - Model `WebPubSubResource` deleted or renamed its instance variable `shared_private_link_resources`
  - Model `WebPubSubResource` deleted or renamed its instance variable `tls`
  - Model `WebPubSubResource` deleted or renamed its instance variable `host_name_prefix`
  - Model `WebPubSubResource` deleted or renamed its instance variable `live_trace_configuration`
  - Model `WebPubSubResource` deleted or renamed its instance variable `resource_log_configuration`
  - Model `WebPubSubResource` deleted or renamed its instance variable `network_ac_ls`
  - Model `WebPubSubResource` deleted or renamed its instance variable `public_network_access`
  - Model `WebPubSubResource` deleted or renamed its instance variable `disable_local_auth`
  - Model `WebPubSubResource` deleted or renamed its instance variable `disable_aad_auth`
  - Model `WebPubSubResource` deleted or renamed its instance variable `region_endpoint_enabled`
  - Model `WebPubSubResource` deleted or renamed its instance variable `resource_stopped`
  - Model `WebPubSubResource` deleted or renamed its instance variable `socket_io`
  - Deleted or renamed model `CustomCertificateList`
  - Deleted or renamed model `CustomDomainList`
  - Deleted or renamed model `OperationList`
  - Deleted or renamed model `PrivateEndpointConnectionList`
  - Deleted or renamed model `PrivateLinkResourceList`
  - Deleted or renamed model `ReplicaList`
  - Deleted or renamed model `SharedPrivateLinkResourceList`
  - Deleted or renamed model `SignalRServiceUsageList`
  - Deleted or renamed model `WebPubSubHubList`
  - Deleted or renamed model `WebPubSubResourceList`

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
