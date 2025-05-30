# Release History

## 1.1.0b1 (2025-05-30)

### Features Added

  - Client `MongoClusterMgmtClient` added operation group `users`
  - Model `MongoClusterProperties` added property `data_api`
  - Model `MongoClusterProperties` added property `auth_config`
  - Model `MongoClusterUpdateProperties` added property `data_api`
  - Model `MongoClusterUpdateProperties` added property `auth_config`
  - Model `StorageProperties` added property `type`
  - Model `StorageProperties` added property `iops`
  - Model `StorageProperties` added property `throughput`
  - Added model `AuthConfigProperties`
  - Added enum `AuthenticationMode`
  - Added enum `DataApiMode`
  - Added model `DataApiProperties`
  - Added model `DatabaseRole`
  - Added model `EntraIdentityProvider`
  - Added model `EntraIdentityProviderProperties`
  - Added enum `EntraPrincipalType`
  - Added model `IdentityProvider`
  - Added enum `IdentityProviderType`
  - Added enum `StorageType`
  - Added model `User`
  - Added model `UserProperties`
  - Added enum `UserRole`
  - Added model `UsersOperations`
  - Method `MongoClusterProperties.__init__` has a new overload `def __init__(self: None, create_mode: Optional[Union[str, _models.CreateMode]], restore_parameters: Optional[_models.MongoClusterRestoreParameters], replica_parameters: Optional[_models.MongoClusterReplicaParameters], administrator: Optional[_models.AdministratorProperties], server_version: Optional[str], public_network_access: Optional[Union[str, _models.PublicNetworkAccess]], high_availability: Optional[_models.HighAvailabilityProperties], storage: Optional[_models.StorageProperties], sharding: Optional[_models.ShardingProperties], compute: Optional[_models.ComputeProperties], backup: Optional[_models.BackupProperties], data_api: Optional[_models.DataApiProperties], preview_features: Optional[List[Union[str, _models.PreviewFeature]]], auth_config: Optional[_models.AuthConfigProperties])`
  - Method `MongoClusterUpdateProperties.__init__` has a new overload `def __init__(self: None, administrator: Optional[_models.AdministratorProperties], server_version: Optional[str], public_network_access: Optional[Union[str, _models.PublicNetworkAccess]], high_availability: Optional[_models.HighAvailabilityProperties], storage: Optional[_models.StorageProperties], sharding: Optional[_models.ShardingProperties], compute: Optional[_models.ComputeProperties], backup: Optional[_models.BackupProperties], data_api: Optional[_models.DataApiProperties], preview_features: Optional[List[Union[str, _models.PreviewFeature]]], auth_config: Optional[_models.AuthConfigProperties])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, display: Optional[_models.OperationDisplay])`
  - Method `StorageProperties.__init__` has a new overload `def __init__(self: None, size_gb: Optional[int], type: Optional[Union[str, _models.StorageType]], iops: Optional[int], throughput: Optional[int])`
  - Method `AuthConfigProperties.__init__` has a new overload `def __init__(self: None, allowed_modes: Optional[List[Union[str, _models.AuthenticationMode]]])`
  - Method `AuthConfigProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `DataApiProperties.__init__` has a new overload `def __init__(self: None, mode: Optional[Union[str, _models.DataApiMode]])`
  - Method `DataApiProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `DatabaseRole.__init__` has a new overload `def __init__(self: None, db: str, role: Union[str, _models.UserRole])`
  - Method `DatabaseRole.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `EntraIdentityProvider.__init__` has a new overload `def __init__(self: None, properties: _models.EntraIdentityProviderProperties)`
  - Method `EntraIdentityProvider.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `EntraIdentityProvider.__init__` has a new overload `def __init__(self: None, type: str)`
  - Method `EntraIdentityProvider.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `EntraIdentityProviderProperties.__init__` has a new overload `def __init__(self: None, principal_type: Union[str, _models.EntraPrincipalType])`
  - Method `EntraIdentityProviderProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `IdentityProvider.__init__` has a new overload `def __init__(self: None, type: str)`
  - Method `IdentityProvider.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `User.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.UserProperties])`
  - Method `User.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `UserProperties.__init__` has a new overload `def __init__(self: None, identity_provider: Optional[_models.IdentityProvider], roles: Optional[List[_models.DatabaseRole]])`
  - Method `UserProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `UsersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, mongo_cluster_name: str, user_name: str, resource: User, content_type: str)`
  - Method `UsersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, mongo_cluster_name: str, user_name: str, resource: JSON, content_type: str)`
  - Method `UsersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, mongo_cluster_name: str, user_name: str, resource: IO[bytes], content_type: str)`

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
