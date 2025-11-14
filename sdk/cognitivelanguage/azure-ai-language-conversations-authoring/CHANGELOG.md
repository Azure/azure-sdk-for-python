# Release History

## 1.0.0b2 (2025-11-14)

### Features Added
- Added support for service version 2024-05-01, 2024-11-01, 2024-11-15-preview,2025-05-15-preview.


### Breaking Changes
- Changed parameter type from `DeleteDeploymentOptions` to `ProjectResourceIds` when calling `DeleteDeploymentFromResources`, with property name changed from `assignedResourceIds` to `azureResourceIds`.
- Changed function name from `list_deployment_Resources` to `list_project_resources`, change its return type from `AssignedDeploymentResource` to `ProjectResourceInfo`.
- changed function name from `assign_deployment_resources` to `assign_project_resources`
- changed function name from `unassign_deployment_resources` to `unassign_project_resources`, changed its parameter type from `UnassignDeploymentOptions` to `ProjectAzureResourceIds`
- changed function name from `get_assign_deployment_resources_status` to `get_assign_project_resources_status`, change its return type from `DeploymentResourcesJobState` to `ProjectResourcesJobState`.
- changed function name from `get_unassign_deployment_resources_status` to `get_unassign_project_resources_status`, change its return type from `DeploymentResourcesJobState` to `ProjectResourcesJobState`.

### Other Changes
* This version and all future versions will require Python 3.7+. Python 3.6 is no longer supported.

## 1.0.0b1 (2025-09-05)

### Features Added
* Initial release