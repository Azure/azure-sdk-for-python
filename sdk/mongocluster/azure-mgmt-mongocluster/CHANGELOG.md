# Release History

## 1.0.0b2 (2024-09-23)

### Features Added

  - The 'MongoClusterMgmtClient' client had operation group 'replicas' added in the current version
  - The 'MongoClusterMgmtClient' client had operation group 'replicas' added in the current version
  - The 'MongoClustersOperations' method 'begin_promote' was added in the current version
  - The model or publicly exposed class 'ReplicasOperations' was added in the current version
  - The 'MongoClustersOperations' method 'begin_promote' was added in the current version
  - The model or publicly exposed class 'ReplicasOperations' was added in the current version
  - The 'ConnectionString' method 'name' was added in the current version
  - The model or publicly exposed class 'ConnectionString' had property 'name' added in the current version
  - The model or publicly exposed class 'CreateMode' had property 'GEO_REPLICA' added in the current version
  - The model or publicly exposed class 'CreateMode' had property 'REPLICA' added in the current version
  - The 'MongoClusterProperties' method 'administrator' was added in the current version
  - The 'MongoClusterProperties' method 'backup' was added in the current version
  - The 'MongoClusterProperties' method 'compute' was added in the current version
  - The 'MongoClusterProperties' method 'high_availability' was added in the current version
  - The 'MongoClusterProperties' method 'infrastructure_version' was added in the current version
  - The 'MongoClusterProperties' method 'preview_features' was added in the current version
  - The 'MongoClusterProperties' method 'replica' was added in the current version
  - The 'MongoClusterProperties' method 'replica_parameters' was added in the current version
  - The 'MongoClusterProperties' method 'sharding' was added in the current version
  - The 'MongoClusterProperties' method 'storage' was added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'replica_parameters' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'administrator' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'high_availability' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'storage' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'sharding' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'compute' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'backup' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'preview_features' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'replica' added in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had property 'infrastructure_version' added in the current version
  - The 'MongoClusterUpdateProperties' method 'administrator' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'backup' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'compute' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'high_availability' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'preview_features' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'sharding' was added in the current version
  - The 'MongoClusterUpdateProperties' method 'storage' was added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'administrator' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'high_availability' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'storage' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'sharding' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'compute' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'backup' added in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had property 'preview_features' added in the current version
  - The model or publicly exposed class 'AdministratorProperties' was added in the current version
  - The model or publicly exposed class 'BackupProperties' was added in the current version
  - The model or publicly exposed class 'ComputeProperties' was added in the current version
  - The model or publicly exposed class 'HighAvailabilityMode' was added in the current version
  - The model or publicly exposed class 'HighAvailabilityProperties' was added in the current version
  - The model or publicly exposed class 'MongoClusterReplicaParameters' was added in the current version
  - The model or publicly exposed class 'PreviewFeature' was added in the current version
  - The model or publicly exposed class 'PromoteMode' was added in the current version
  - The model or publicly exposed class 'PromoteOption' was added in the current version
  - The model or publicly exposed class 'PromoteReplicaRequest' was added in the current version
  - The model or publicly exposed class 'Replica' was added in the current version
  - The model or publicly exposed class 'ReplicationProperties' was added in the current version
  - The model or publicly exposed class 'ReplicationRole' was added in the current version
  - The model or publicly exposed class 'ReplicationState' was added in the current version
  - The model or publicly exposed class 'ShardingProperties' was added in the current version
  - The model or publicly exposed class 'StorageProperties' was added in the current version

### Breaking Changes

  - The model or publicly exposed class 'MongoClusterProperties' had its instance variable 'administrator_login' deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had its instance variable 'administrator_login_password' deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had its instance variable 'earliest_restore_time' deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterProperties' had its instance variable 'node_group_specs' deleted or renamed in the current version
  - The 'MongoClusterProperties' method 'administrator_login' was deleted or renamed in the current version
  - The 'MongoClusterProperties' method 'administrator_login_password' was deleted or renamed in the current version
  - The 'MongoClusterProperties' method 'earliest_restore_time' was deleted or renamed in the current version
  - The 'MongoClusterProperties' method 'node_group_specs' was deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had its instance variable 'administrator_login' deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had its instance variable 'administrator_login_password' deleted or renamed in the current version
  - The model or publicly exposed class 'MongoClusterUpdateProperties' had its instance variable 'node_group_specs' deleted or renamed in the current version
  - The 'MongoClusterUpdateProperties' method 'administrator_login' was deleted or renamed in the current version
  - The 'MongoClusterUpdateProperties' method 'administrator_login_password' was deleted or renamed in the current version
  - The 'MongoClusterUpdateProperties' method 'node_group_specs' was deleted or renamed in the current version
  - The model or publicly exposed class 'NodeGroupSpec' was deleted or renamed in the current version
  - The model or publicly exposed class 'NodeKind' was deleted or renamed in the current version

## 1.0.0b1 (2024-07-01)

### Other Changes

  - Initial version
