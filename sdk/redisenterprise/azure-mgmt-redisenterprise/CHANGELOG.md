# Release History

## 2.1.0b2 (2023-04-20)

### Features Added

  - Added operation DatabasesOperations.begin_flush
  - Added operation group SkusOperations
  - Model Cluster has a new parameter encryption
  - Model Cluster has a new parameter identity
  - Model Cluster has a new parameter system_data
  - Model ClusterUpdate has a new parameter encryption
  - Model ClusterUpdate has a new parameter identity
  - Model Database has a new parameter system_data
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model PrivateLinkResource has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

## 2.1.0b1 (2022-11-22)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.0.0 (2022-04-04)

**Features**

  - Added operation DatabasesOperations.begin_force_unlink
  - Model Database has a new parameter geo_replication
  - Model DatabaseUpdate has a new parameter geo_replication

**Breaking changes**

  - Model ImportClusterParameters has a new required parameter sas_uris
  - Model ImportClusterParameters no longer has parameter sas_uri

## 1.0.0 (2021-02-22)

**Features**

  - Model Database has a new parameter persistence
  - Model DatabaseUpdate has a new parameter persistence
  - Added operation PrivateLinkResourcesOperations.list_by_cluster
  - Added operation group OperationsStatusOperations

**Breaking changes**

  - Removed operation PrivateLinkResourcesOperations.list_by_redis_enterprise_cache
  - Removed operation group GetOperations

## 1.0.0b1 (2021-02-02)

* Initial Release
