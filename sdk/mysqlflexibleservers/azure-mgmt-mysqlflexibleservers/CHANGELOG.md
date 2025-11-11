# Release History

## 1.0.0 (2025-11-07)

### Features Added

  - Model `MySQLManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `MySQLManagementClient` added operation group `private_endpoint_connections`
  - Client `MySQLManagementClient` added operation group `private_link_resources`
  - Model `MaintenanceWindow` added property `batch_of_maintenance`
  - Model `OperationProgressResult` added property `properties`
  - Added enum `BatchOfMaintenance`
  - Added enum `Origin`
  - Added model `PrivateEndpointConnectionListResult`
  - Added model `PrivateLinkResource`
  - Added model `PrivateLinkResourceListResult`
  - Added operation group `PrivateEndpointConnectionsOperations`
  - Added operation group `PrivateLinkResourcesOperations`

### Breaking Changes

  - Model `OperationProgressResult` instance variable `object_type` has been moved under property `properties`
  - Deleted unused model `Provisioning`

## 1.0.0b3 (2024-11-18)

### Features Added

  - Model `Capability` added property `supported_features`
  - Model `Server` added property `full_version`
  - Added model `FeatureProperty`

## 1.0.0b2 (2024-09-26)

### Features Added

  - Model `Server` added property `database_port`
  - Model `Server` added property `maintenance_policy`
  - Model `ServerForUpdate` added property `maintenance_policy`
  - Added model `MaintenancePolicy`
  - Added enum `PatchStrategy`

## 1.0.0b1 (2024-08-27)

### Other Changes

  - Initial version
