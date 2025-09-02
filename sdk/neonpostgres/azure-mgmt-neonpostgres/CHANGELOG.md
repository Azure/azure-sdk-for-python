# Release History

## 2.0.0b1 (2025-09-02)

### Features Added

  - Model `NeonPostgresMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `BranchProperties` added property `branch_id`
  - Model `BranchProperties` added property `branch`
  - Model `BranchProperties` added property `data_size`
  - Model `BranchProperties` added property `last_active`
  - Model `BranchProperties` added property `compute_hours`
  - Model `BranchProperties` added property `protected`
  - Model `BranchProperties` added property `is_default`
  - Model `EndpointProperties` added property `endpoint_id`
  - Model `EndpointProperties` added property `compute_name`
  - Model `EndpointProperties` added property `status`
  - Model `EndpointProperties` added property `last_active`
  - Model `EndpointProperties` added property `size`
  - Model `NeonDatabaseProperties` added property `database_name`
  - Model `NeonDatabaseProperties` added property `last_updated`
  - Model `NeonRoleProperties` added property `role_name`
  - Model `NeonRoleProperties` added property `last_updated`
  - Model `NeonRoleProperties` added property `owns`
  - Added model `AutoscalingSize`
  - Added enum `EndpointStatus`
  - Added enum `EntityType`
  - Added model `PreflightCheckParameters`
  - Added model `PreflightCheckResult`
  - Model `BranchesOperations` added method `preflight`

### Breaking Changes

  - Deleted or renamed client operation group `NeonPostgresMgmtClient.models`
  - Deleted or renamed method `BranchesOperations.begin_update`
  - Deleted or renamed method `ComputesOperations.begin_create_or_update`
  - Deleted or renamed method `ComputesOperations.begin_update`
  - Deleted or renamed method `ComputesOperations.delete`
  - Deleted or renamed method `ComputesOperations.get`
  - Deleted or renamed method `EndpointsOperations.begin_update`
  - Deleted or renamed method `EndpointsOperations.get`
  - Deleted or renamed method `NeonDatabasesOperations.begin_update`
  - Deleted or renamed method `NeonDatabasesOperations.get`
  - Deleted or renamed method `NeonRolesOperations.begin_update`
  - Deleted or renamed method `NeonRolesOperations.get`
  - Deleted or renamed method `ProjectsOperations.begin_update`
  - Deleted or renamed model `ModelsOperations`

## 1.0.0 (2025-04-21)

### Features Added

  - Client `NeonPostgresMgmtClient` added operation group `models`
  - Client `NeonPostgresMgmtClient` added operation group `projects`
  - Client `NeonPostgresMgmtClient` added operation group `branches`
  - Client `NeonPostgresMgmtClient` added operation group `computes`
  - Client `NeonPostgresMgmtClient` added operation group `neon_databases`
  - Client `NeonPostgresMgmtClient` added operation group `neon_roles`
  - Client `NeonPostgresMgmtClient` added operation group `endpoints`
  - Model `OrganizationProperties` added property `project_properties`
  - Added model `Attributes`
  - Added model `Branch`
  - Added model `BranchProperties`
  - Added model `Compute`
  - Added model `ComputeProperties`
  - Added model `ConnectionUriProperties`
  - Added model `DefaultEndpointSettings`
  - Added model `Endpoint`
  - Added model `EndpointProperties`
  - Added enum `EndpointType`
  - Added model `NeonDatabase`
  - Added model `NeonDatabaseProperties`
  - Added model `NeonRole`
  - Added model `NeonRoleProperties`
  - Added model `PgVersion`
  - Added model `PgVersionsResult`
  - Added model `Project`
  - Added model `ProjectProperties`
  - Added model `ProxyResource`
  - Operation group `OrganizationsOperations` added method `get_postgres_versions`
  - Added operation group `BranchesOperations`
  - Added operation group `ComputesOperations`
  - Added operation group `EndpointsOperations`
  - Added operation group `ModelsOperations`
  - Added operation group `NeonDatabasesOperations`
  - Added operation group `NeonRolesOperations`
  - Added operation group `ProjectsOperations`

## 1.0.0b1 (2024-12-03)

### Other Changes

  - Initial version
