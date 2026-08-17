# Release History

## 1.0.0b2 (2026-08-14)

### Features Added

  - Client `HorizonDBMgmtClient` added operation group `horizon_db_administrators`
  - Model `HorizonDbCluster` added property `identity`
  - Model `HorizonDbClusterForPatchUpdate` added property `identity`
  - Model `HorizonDbClusterProperties` added property `auth_config`
  - Model `HorizonDbClusterProperties` added property `compute_model`
  - Model `HorizonDbClusterProperties` added property `mirroring`
  - Model `HorizonDbClusterPropertiesForPatchUpdate` added property `auth_config`
  - Model `HorizonDbClusterPropertiesForPatchUpdate` added property `compute_model`
  - Model `HorizonDbClusterPropertiesForPatchUpdate` added property `mirroring`
  - Enum `State` added member `SUCCEEDED`
  - Enum `State` added member `UPGRADING`
  - Added enum `AuthenticationState`
  - Added model `HorizonDbAdministrator`
  - Added model `HorizonDbAdministratorAdd`
  - Added model `HorizonDbAdministratorProperties`
  - Added model `HorizonDbAdministratorPropertiesForAdd`
  - Added model `HorizonDbClusterAuthConfig`
  - Added model `HorizonDbClusterMirroring`
  - Added model `HorizonDbComputeModel`
  - Added enum `HorizonDbComputeModelType`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added enum `PrincipalTypes`
  - Added model `UserAssignedIdentity`
  - Operation group `HorizonDbClustersOperations` added method `begin_restart`
  - Operation group `HorizonDbClustersOperations` added method `begin_start`
  - Operation group `HorizonDbClustersOperations` added method `begin_stop`
  - Operation group `HorizonDbPrivateEndpointConnectionsOperations` added method `update_status`
  - Added operation group `HorizonDbAdministratorsOperations`

### Breaking Changes

  - Deleted or renamed model `OptionalPropertiesUpdateableProperties`
  - Deleted or renamed model `PrivateEndpointConnection`
  - Deleted or renamed model `PrivateEndpointConnectionUpdate`
  - Method `HorizonDbPrivateEndpointConnectionsOperations.begin_delete` inserted a `positional_or_keyword` parameter `cluster_name`
  - Deleted or renamed method `HorizonDbPrivateEndpointConnectionsOperations.begin_update`

## 1.0.0b1 (2026-04-22)

### Other Changes

  - Initial version