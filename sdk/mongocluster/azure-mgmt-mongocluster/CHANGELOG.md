# Release History

## 1.1.0b2 (2025-08-20)

### Features Added

  - Enum `UserRole` added member `DATABASE_OWNER`

### Breaking Changes

  - Model `MongoCluster` deleted or renamed its instance variable `identity`
  - Model `MongoClusterProperties` deleted or renamed its instance variable `encryption`
  - Model `MongoClusterUpdate` deleted or renamed its instance variable `identity`
  - Deleted or renamed enum value `UserRole.ROOT`
  - Deleted or renamed model `CustomerManagedKeyEncryptionProperties`
  - Deleted or renamed model `EncryptionProperties`
  - Deleted or renamed model `KeyEncryptionKeyIdentity`
  - Deleted or renamed model `KeyEncryptionKeyIdentityType`
  - Deleted or renamed model `ManagedServiceIdentity`
  - Deleted or renamed model `ManagedServiceIdentityType`
  - Deleted or renamed model `UserAssignedIdentity`

## 1.1.0b1 (2025-07-23)

### Features Added

  - Client `MongoClusterMgmtClient` added operation group `users`
  - Model `MongoCluster` added property `identity`
  - Model `MongoClusterProperties` added property `data_api`
  - Model `MongoClusterProperties` added property `auth_config`
  - Model `MongoClusterProperties` added property `encryption`
  - Model `MongoClusterUpdate` added property `identity`
  - Model `MongoClusterUpdateProperties` added property `data_api`
  - Model `MongoClusterUpdateProperties` added property `auth_config`
  - Model `StorageProperties` added property `type`
  - Model `StorageProperties` added property `iops`
  - Model `StorageProperties` added property `throughput`
  - Added model `AuthConfigProperties`
  - Added enum `AuthenticationMode`
  - Added model `CustomerManagedKeyEncryptionProperties`
  - Added enum `DataApiMode`
  - Added model `DataApiProperties`
  - Added model `DatabaseRole`
  - Added model `EncryptionProperties`
  - Added model `EntraIdentityProvider`
  - Added model `EntraIdentityProviderProperties`
  - Added enum `EntraPrincipalType`
  - Added model `IdentityProvider`
  - Added enum `IdentityProviderType`
  - Added model `KeyEncryptionKeyIdentity`
  - Added enum `KeyEncryptionKeyIdentityType`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added enum `StorageType`
  - Added model `User`
  - Added model `UserAssignedIdentity`
  - Added model `UserProperties`
  - Added enum `UserRole`
  - Added model `UsersOperations`

## 1.0.0 (2024-09-26)

### Features Added

  - Model `ConnectionString` added property `name`
  - Model `MongoClusterProperties` added property `administrator`
  - Model `MongoClusterProperties` added property `high_availability`
  - Model `MongoClusterProperties` added property `storage`
  - Model `MongoClusterProperties` added property `sharding`
  - Model `MongoClusterProperties` added property `compute`
  - Model `MongoClusterProperties` added property `backup`
  - Model `MongoClusterUpdateProperties` added property `administrator`
  - Model `MongoClusterUpdateProperties` added property `high_availability`
  - Model `MongoClusterUpdateProperties` added property `storage`
  - Model `MongoClusterUpdateProperties` added property `sharding`
  - Model `MongoClusterUpdateProperties` added property `compute`
  - Model `MongoClusterUpdateProperties` added property `backup`
  - Added model `AdministratorProperties`
  - Added model `BackupProperties`
  - Added model `ComputeProperties`
  - Added enum `HighAvailabilityMode`
  - Added model `HighAvailabilityProperties`
  - Added model `ShardingProperties`
  - Added model `StorageProperties`

### Breaking Changes

  - Model `MongoClusterProperties` deleted or renamed its instance variable `administrator_login`
  - Model `MongoClusterProperties` deleted or renamed its instance variable `administrator_login_password`
  - Model `MongoClusterProperties` deleted or renamed its instance variable `earliest_restore_time`
  - Model `MongoClusterProperties` deleted or renamed its instance variable `node_group_specs`
  - Model `MongoClusterUpdateProperties` deleted or renamed its instance variable `administrator_login`
  - Model `MongoClusterUpdateProperties` deleted or renamed its instance variable `administrator_login_password`
  - Model `MongoClusterUpdateProperties` deleted or renamed its instance variable `node_group_specs`
  - Deleted or renamed model `NodeGroupSpec`
  - Deleted or renamed model `NodeKind`

## 1.0.0b2 (2024-09-23)

### Features Added

  - Client `MongoClusterMgmtClient` added operation group `replicas`
  - Enum `CreateMode` added member `GEO_REPLICA`
  - Enum `CreateMode` added member `REPLICA`
  - Model `MongoClusterProperties` added property `replica_parameters`
  - Model `MongoClusterProperties` added property `preview_features`
  - Model `MongoClusterProperties` added property `replica`
  - Model `MongoClusterProperties` added property `infrastructure_version`
  - Model `MongoClusterUpdateProperties` added property `preview_features`
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

  - Model `MongoClusterRestoreParameters` renamed its instance variable `point_in_time_u_t_c` to `point_in_time_utc`
  - Model `NodeGroupSpec` renamed its instance variable `disk_size_g_b` to `disk_size_gb`

## 1.0.0b1 (2024-07-01)

### Other Changes

  - Initial version
