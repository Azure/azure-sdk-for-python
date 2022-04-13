# Release History

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
