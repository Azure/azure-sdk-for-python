# Release History

## 1.0.0b2 (2024-09-23)

### Features Added

  - Client `MongoClusterMgmtClient` added operation group `replicas`
  - Enum `CreateMode` added member `GEO_REPLICA`
  - Enum `CreateMode` added member `REPLICA`
  - Model `MongoClusterProperties` added method `infrastructure_version`
  - Model `MongoClusterProperties` added method `preview_features`
  - Model `MongoClusterProperties` added method `replica`
  - Model `MongoClusterProperties` added method `replica_parameters`
  - Model `MongoClusterProperties` added property `replica_parameters`
  - Model `MongoClusterProperties` added property `preview_features`
  - Model `MongoClusterProperties` added property `replica`
  - Model `MongoClusterProperties` added property `infrastructure_version`
  - Model `MongoClusterRestoreParameters` added method `point_in_time_utc`
  - Model `MongoClusterRestoreParameters` added property `point_in_time_utc`
  - Model `MongoClusterUpdateProperties` added method `preview_features`
  - Model `MongoClusterUpdateProperties` added property `preview_features`
  - Model `NodeGroupSpec` added method `disk_size_gb`
  - Model `NodeGroupSpec` added property `disk_size_gb`
  - Added model `MongoClusterReplicaParameters`
  - Added enum `PreviewFeature`
  - Added enum `PromoteMode`
  - Added enum `PromoteOption`
  - Added model `PromoteReplicaRequest`
  - Added model `Replica`
  - Added model `ReplicationProperties`
  - Added enum `ReplicationRole`
  - Added enum `ReplicationState`
  - Model `MongoClustersOperations` added method `begin_promote`
  - Added model `ReplicasOperations`

### Breaking Changes

  - Model `MongoClusterRestoreParameters` deleted or renamed its instance variable `point_in_time_u_t_c`
  - Deleted or renamed method `MongoClusterRestoreParameters.point_in_time_u_t_c`
  - Model `NodeGroupSpec` deleted or renamed its instance variable `disk_size_g_b`
  - Deleted or renamed method `NodeGroupSpec.disk_size_g_b`
  - OperationDisplay.__init__ had all overloads removed

## 1.0.0b1 (2024-07-01)

### Other Changes

  - Initial version
