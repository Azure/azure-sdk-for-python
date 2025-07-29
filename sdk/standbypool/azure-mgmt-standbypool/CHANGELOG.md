# Release History

## 2.0.0 (2025-04-21)

### Features Added

  - Model `ContainerGroupInstanceCountSummary` added property `zone`
  - Model `StandbyContainerGroupPoolResourceProperties` added property `zones`
  - Model `StandbyContainerGroupPoolResourceUpdateProperties` added property `zones`
  - Model `StandbyContainerGroupPoolRuntimeViewResourceProperties` added property `status`
  - Model `StandbyContainerGroupPoolRuntimeViewResourceProperties` added property `prediction`
  - Model `StandbyVirtualMachinePoolRuntimeViewResourceProperties` added property `status`
  - Model `StandbyVirtualMachinePoolRuntimeViewResourceProperties` added property `prediction`
  - Enum `VirtualMachineState` added member `HIBERNATED`
  - Added enum `HealthStateCode`
  - Added enum `PoolContainerGroupState`
  - Added model `PoolContainerGroupStateCount`
  - Added model `PoolStatus`
  - Added enum `PoolVirtualMachineState`
  - Added model `PoolVirtualMachineStateCount`
  - Added model `StandbyContainerGroupPoolForecastValues`
  - Added model `StandbyContainerGroupPoolPrediction`
  - Added model `StandbyVirtualMachinePoolForecastValues`
  - Added model `StandbyVirtualMachinePoolPrediction`

### Breaking Changes

  - Deleted or renamed model `PoolResourceStateCount`

## 1.0.0 (2024-09-25)

### Features Added

  - Client `StandbyPoolMgmtClient` added property `send_request`
  - Client `StandbyPoolMgmtClient` added operation group `standby_virtual_machine_pool_runtime_views`
  - Client `StandbyPoolMgmtClient` added operation group `standby_container_group_pool_runtime_views`
  - Model `ContainerGroupProfile` added property `id`
  - Model `ContainerGroupProfile` added property `revision`
  - Model `ContainerGroupProperties` added property `container_group_profile`
  - Model `ContainerGroupProperties` added property `subnet_ids`
  - Model `ErrorAdditionalInfo` added property `info`
  - Model `ErrorAdditionalInfo` added property `type`
  - Model `ErrorDetail` added property `additional_info`
  - Model `ErrorDetail` added property `code`
  - Model `ErrorDetail` added property `details`
  - Model `ErrorDetail` added property `message`
  - Model `ErrorDetail` added property `target`
  - Model `ErrorResponse` added property `error`
  - Model `Operation` added property `action_type`
  - Model `Operation` added property `display`
  - Model `Operation` added property `is_data_action`
  - Model `Operation` added property `name`
  - Model `Operation` added property `origin`
  - Model `OperationDisplay` added property `description`
  - Model `OperationDisplay` added property `operation`
  - Model `OperationDisplay` added property `provider`
  - Model `OperationDisplay` added property `resource`
  - Model `ProxyResource` added property `id`
  - Model `ProxyResource` added property `name`
  - Model `ProxyResource` added property `system_data`
  - Model `ProxyResource` added property `type`
  - Model `Resource` added property `id`
  - Model `Resource` added property `name`
  - Model `Resource` added property `system_data`
  - Model `Resource` added property `type`
  - Model `StandbyContainerGroupPoolElasticityProfile` added property `max_ready_capacity`
  - Model `StandbyContainerGroupPoolElasticityProfile` added property `refill_policy`
  - Model `StandbyContainerGroupPoolResource` added property `id`
  - Model `StandbyContainerGroupPoolResource` added property `location`
  - Model `StandbyContainerGroupPoolResource` added property `name`
  - Model `StandbyContainerGroupPoolResource` added property `properties`
  - Model `StandbyContainerGroupPoolResource` added property `system_data`
  - Model `StandbyContainerGroupPoolResource` added property `tags`
  - Model `StandbyContainerGroupPoolResource` added property `type`
  - Model `StandbyContainerGroupPoolResourceProperties` added property `container_group_properties`
  - Model `StandbyContainerGroupPoolResourceProperties` added property `elasticity_profile`
  - Model `StandbyContainerGroupPoolResourceProperties` added property `provisioning_state`
  - Model `StandbyContainerGroupPoolResourceUpdate` added property `properties`
  - Model `StandbyContainerGroupPoolResourceUpdate` added property `tags`
  - Model `StandbyContainerGroupPoolResourceUpdateProperties` added property `container_group_properties`
  - Model `StandbyContainerGroupPoolResourceUpdateProperties` added property `elasticity_profile`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added property `max_ready_capacity`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added property `min_ready_capacity`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added property `min_ready_capacity`
  - Model `StandbyVirtualMachinePoolResource` added property `id`
  - Model `StandbyVirtualMachinePoolResource` added property `location`
  - Model `StandbyVirtualMachinePoolResource` added property `name`
  - Model `StandbyVirtualMachinePoolResource` added property `properties`
  - Model `StandbyVirtualMachinePoolResource` added property `system_data`
  - Model `StandbyVirtualMachinePoolResource` added property `tags`
  - Model `StandbyVirtualMachinePoolResource` added property `type`
  - Model `StandbyVirtualMachinePoolResourceProperties` added property `attached_virtual_machine_scale_set_id`
  - Model `StandbyVirtualMachinePoolResourceProperties` added property `elasticity_profile`
  - Model `StandbyVirtualMachinePoolResourceProperties` added property `provisioning_state`
  - Model `StandbyVirtualMachinePoolResourceProperties` added property `virtual_machine_state`
  - Model `StandbyVirtualMachinePoolResourceUpdate` added property `properties`
  - Model `StandbyVirtualMachinePoolResourceUpdate` added property `tags`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added property `attached_virtual_machine_scale_set_id`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added property `elasticity_profile`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added property `virtual_machine_state`
  - Model `StandbyVirtualMachineResource` added property `id`
  - Model `StandbyVirtualMachineResource` added property `name`
  - Model `StandbyVirtualMachineResource` added property `properties`
  - Model `StandbyVirtualMachineResource` added property `system_data`
  - Model `StandbyVirtualMachineResource` added property `type`
  - Model `StandbyVirtualMachineResourceProperties` added property `provisioning_state`
  - Model `StandbyVirtualMachineResourceProperties` added property `virtual_machine_resource_id`
  - Model `Subnet` added property `id`
  - Model `SystemData` added property `created_at`
  - Model `SystemData` added property `created_by`
  - Model `SystemData` added property `created_by_type`
  - Model `SystemData` added property `last_modified_at`
  - Model `SystemData` added property `last_modified_by`
  - Model `SystemData` added property `last_modified_by_type`
  - Model `TrackedResource` added property `id`
  - Model `TrackedResource` added property `location`
  - Model `TrackedResource` added property `name`
  - Model `TrackedResource` added property `system_data`
  - Model `TrackedResource` added property `tags`
  - Model `TrackedResource` added property `type`
  - Added model `ContainerGroupInstanceCountSummary`
  - Added model `PoolResourceStateCount`
  - Added model `StandbyContainerGroupPoolRuntimeViewResource`
  - Added model `StandbyContainerGroupPoolRuntimeViewResourceProperties`
  - Added model `StandbyVirtualMachinePoolRuntimeViewResource`
  - Added model `StandbyVirtualMachinePoolRuntimeViewResourceProperties`
  - Added model `VirtualMachineInstanceCountSummary`
  - Added model `StandbyContainerGroupPoolRuntimeViewsOperations`
  - Added model `StandbyVirtualMachinePoolRuntimeViewsOperations`

### Breaking Changes

  - Model `ProxyResource` deleted or renamed its instance variable `additional_properties`
  - Deleted or renamed model `ContainerGroupProfileUpdate`
  - Deleted or renamed model `ContainerGroupPropertiesUpdate`
  - Deleted or renamed model `OperationListResult`
  - Deleted or renamed model `StandbyContainerGroupPoolElasticityProfileUpdate`
  - Deleted or renamed model `StandbyContainerGroupPoolResourceListResult`
  - Deleted or renamed model `StandbyVirtualMachinePoolElasticityProfileUpdate`
  - Deleted or renamed model `StandbyVirtualMachinePoolResourceListResult`
  - Deleted or renamed model `StandbyVirtualMachineResourceListResult`

## 1.0.0b1 (2024-04-22)

* Initial Release
