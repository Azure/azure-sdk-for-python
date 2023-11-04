# Release History

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
