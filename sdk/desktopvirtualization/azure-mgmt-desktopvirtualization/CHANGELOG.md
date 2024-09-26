# Release History

## 2.0.0 (2024-09-23)

### Features Added

  - The 'DesktopVirtualizationMgmtClient' client had operation group 'app_attach_package_info' added in the current version
  - The 'DesktopVirtualizationMgmtClient' client had operation group 'app_attach_package' added in the current version
  - The model or publicly exposed class 'ExpandMsixImage' had property 'certificate_name' added in the current version
  - The model or publicly exposed class 'ExpandMsixImage' had property 'certificate_expiry' added in the current version
  - The model or publicly exposed class 'HostPool' had property 'app_attach_package_references' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnection' had property 'group_ids' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'group_ids' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'private_endpoint' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'private_link_service_connection_state' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'provisioning_state' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'id' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'name' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'type' added in the current version
  - The model or publicly exposed class 'PrivateEndpointConnectionWithSystemData' had property 'additional_properties' added in the current version
  - The model or publicly exposed class 'Resource' had property 'system_data' added in the current version
  - The model or publicly exposed class 'AppAttachPackage' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageArchitectures' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageInfoProperties' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageList' was added in the current version
  - The model or publicly exposed class 'AppAttachPackagePatch' was added in the current version
  - The model or publicly exposed class 'AppAttachPackagePatchProperties' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageProperties' was added in the current version
  - The model or publicly exposed class 'ErrorAdditionalInfo' was added in the current version
  - The model or publicly exposed class 'ErrorDetail' was added in the current version
  - The model or publicly exposed class 'ErrorResponse' was added in the current version
  - The model or publicly exposed class 'FailHealthCheckOnStagingFailure' was added in the current version
  - The model or publicly exposed class 'ImportPackageInfoRequest' was added in the current version
  - The model or publicly exposed class 'PackageTimestamped' was added in the current version
  - The model or publicly exposed class 'ProvisioningState' was added in the current version
  - The model or publicly exposed class 'RegistrationTokenList' was added in the current version
  - The model or publicly exposed class 'RegistrationTokenMinimal' was added in the current version
  - The model or publicly exposed class 'TrackedResource' was added in the current version
  - The 'HostPoolsOperations' method 'list_registration_tokens' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageInfoOperations' was added in the current version
  - The model or publicly exposed class 'AppAttachPackageOperations' was added in the current version

### Breaking Changes

  - Parameter `location` of model `ApplicationGroup` is now required
  - Parameter `location` of model `HostPool` is now required
  - Parameter `location` of model `ResourceModelWithAllowedPropertySet` is now required
  - Parameter `location` of model `ScalingPlan` is now required
  - Parameter `location` of model `Workspace` is now required

## 1.1.0 (2023-10-23)

### Features Added

  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group ScalingPlanPersonalSchedulesOperations
  - Model ApplicationGroup has a new parameter show_in_feed
  - Model ApplicationGroupPatch has a new parameter show_in_feed
  - Model HostPool has a new parameter private_endpoint_connections
  - Model HostPool has a new parameter public_network_access
  - Model HostPoolPatch has a new parameter public_network_access
  - Model Workspace has a new parameter private_endpoint_connections
  - Model Workspace has a new parameter public_network_access
  - Model WorkspacePatch has a new parameter public_network_access

## 1.0.0 (2023-03-20)

### other changes

  - First GA version

## 1.0.0b2 (2022-11-09)

### Features Added

  - Added operation group ScalingPlanPooledSchedulesOperations
  - Model HostPool has a new parameter agent_update
  - Model HostPoolPatch has a new parameter agent_update
  - Model SessionHost has a new parameter friendly_name
  - Model SessionHostPatch has a new parameter friendly_name

### Breaking Changes

  - Client name is changed from `DesktopVirtualizationAPIClient` to `DesktopVirtualizationMgmtClient`
  - Model ApplicationGroup no longer has parameter migration_request
  - Model HostPool no longer has parameter migration_request
  - Model HostPool no longer has parameter public_network_access
  - Model HostPoolPatch no longer has parameter public_network_access
  - Model Workspace no longer has parameter public_network_access
  - Model WorkspacePatch no longer has parameter public_network_access
  - Operation ApplicationGroupsOperations.list_by_resource_group has a new parameter initial_skip
  - Operation ApplicationGroupsOperations.list_by_resource_group has a new parameter is_descending
  - Operation ApplicationGroupsOperations.list_by_resource_group has a new parameter page_size
  - Operation ApplicationsOperations.list has a new parameter initial_skip
  - Operation ApplicationsOperations.list has a new parameter is_descending
  - Operation ApplicationsOperations.list has a new parameter page_size
  - Operation DesktopsOperations.list has a new parameter initial_skip
  - Operation DesktopsOperations.list has a new parameter is_descending
  - Operation DesktopsOperations.list has a new parameter page_size
  - Operation HostPoolsOperations.list has a new parameter initial_skip
  - Operation HostPoolsOperations.list has a new parameter is_descending
  - Operation HostPoolsOperations.list has a new parameter page_size
  - Operation HostPoolsOperations.list_by_resource_group has a new parameter initial_skip
  - Operation HostPoolsOperations.list_by_resource_group has a new parameter is_descending
  - Operation HostPoolsOperations.list_by_resource_group has a new parameter page_size
  - Operation MSIXPackagesOperations.list has a new parameter initial_skip
  - Operation MSIXPackagesOperations.list has a new parameter is_descending
  - Operation MSIXPackagesOperations.list has a new parameter page_size
  - Operation ScalingPlansOperations.list_by_host_pool has a new parameter initial_skip
  - Operation ScalingPlansOperations.list_by_host_pool has a new parameter is_descending
  - Operation ScalingPlansOperations.list_by_host_pool has a new parameter page_size
  - Operation ScalingPlansOperations.list_by_resource_group has a new parameter initial_skip
  - Operation ScalingPlansOperations.list_by_resource_group has a new parameter is_descending
  - Operation ScalingPlansOperations.list_by_resource_group has a new parameter page_size
  - Operation ScalingPlansOperations.list_by_subscription has a new parameter initial_skip
  - Operation ScalingPlansOperations.list_by_subscription has a new parameter is_descending
  - Operation ScalingPlansOperations.list_by_subscription has a new parameter page_size
  - Operation SessionHostsOperations.list has a new parameter initial_skip
  - Operation SessionHostsOperations.list has a new parameter is_descending
  - Operation SessionHostsOperations.list has a new parameter page_size
  - Operation StartMenuItemsOperations.list has a new parameter initial_skip
  - Operation StartMenuItemsOperations.list has a new parameter is_descending
  - Operation StartMenuItemsOperations.list has a new parameter page_size
  - Operation UserSessionsOperations.list has a new parameter initial_skip
  - Operation UserSessionsOperations.list has a new parameter is_descending
  - Operation UserSessionsOperations.list has a new parameter page_size
  - Operation UserSessionsOperations.list_by_host_pool has a new parameter initial_skip
  - Operation UserSessionsOperations.list_by_host_pool has a new parameter is_descending
  - Operation UserSessionsOperations.list_by_host_pool has a new parameter page_size
  - Operation WorkspacesOperations.list_by_resource_group has a new parameter initial_skip
  - Operation WorkspacesOperations.list_by_resource_group has a new parameter is_descending
  - Operation WorkspacesOperations.list_by_resource_group has a new parameter page_size
  - Parameter time_zone of model ScalingPlan is now required
  - Removed operation group PrivateEndpointConnectionsOperations
  - Removed operation group PrivateLinkResourcesOperations

## 1.0.0b1 (2021-11-11)

* Initial Release
