# Release History

## 1.0.0b4 (2026-01-22)

### Bugs Fixed
- Changed the continuation token format.

## 1.0.0b3 (2025-12-09)

### Features Added
- Added support for service version 2025-11-01.

### Other Changes
- Updated deployment samples (sync and async) to demonstrate usage with both 2025-11-01 (GA) and 2025-11-15-preview service versions.

## 1.0.0b2 (2025-11-14)

### Features Added
- Added support for service version 2025-11-15-preview.

### Breaking Changes
- Changed parameter type from `DeleteDeploymentDetails` to `ProjectResourceIds` when calling `begin_delete_deployment_from_resources`, with property name changed from `assigned_resource_ids` to `azure_resource_ids`.

- Changed function name from `list_deployment_Resources` to `list_project_resources`, change its return type from `AssignedDeploymentResource` to `AssignedProjectResource`.

- Changed function name from `begin_assign_deployment_resources` to `begin_assign_project_resources`, and its parameter type from `AssignDeploymentResourcesDetails` to `AssignProjectResourcesDetails`.

- Changed function name from `begin_unassign_deployment_resources` to `begin_unassign_project_resources`, changed its parameter type from `UnassignDeploymentResourcesDetails` to `ProjectResourceIds`.

- Changed function name from `get_assign_deployment_resources_status` to `get_assign_project_resources_status`, change its return type from `DeploymentResourcesState` to `ProjectResourcesState`.

- Changed function name from `get_unassign_deployment_resources_status` to `get_unassign_project_resources_status`, change its return type from `DeploymentResourcesState` to `ProjectResourcesState`.

### Other Changes
- Add samples for the following functions(sync and async):
    - list_assigned_resource_deployments
    - list_project_resources
    - delete_deployment_from_resources
    - get_assign_project_resources_status
    - get_unassign_project_resources_status
    - get_deployment_delete_from_resources_status
      
## 1.0.0b1 (2025-09-05)

### Features Added
* Initial release