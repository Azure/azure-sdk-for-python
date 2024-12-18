# Release History

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
