# Release History

## 1.0.0b2 (2024-09-23)

### Features Added

  - Client `StandbyPoolMgmtClient` added method `send_request`
  - Client `StandbyPoolMgmtClient` added operation group `standby_virtual_machine_pool_runtime_views`
  - Client `StandbyPoolMgmtClient` added operation group `standby_container_group_pool_runtime_views`
  - Model `ContainerGroupProfile` added method `id`
  - Model `ContainerGroupProfile` added method `revision`
  - Model `ContainerGroupProperties` added method `container_group_profile`
  - Model `ContainerGroupProperties` added method `subnet_ids`
  - Model `ErrorAdditionalInfo` added method `info`
  - Model `ErrorAdditionalInfo` added method `type`
  - Model `ErrorDetail` added method `additional_info`
  - Model `ErrorDetail` added method `code`
  - Model `ErrorDetail` added method `details`
  - Model `ErrorDetail` added method `message`
  - Model `ErrorDetail` added method `target`
  - Model `ErrorResponse` added method `error`
  - Model `Operation` added method `action_type`
  - Model `Operation` added method `display`
  - Model `Operation` added method `is_data_action`
  - Model `Operation` added method `name`
  - Model `Operation` added method `origin`
  - Model `OperationDisplay` added method `description`
  - Model `OperationDisplay` added method `operation`
  - Model `OperationDisplay` added method `provider`
  - Model `OperationDisplay` added method `resource`
  - Model `ProxyResource` added method `id`
  - Model `ProxyResource` added method `name`
  - Model `ProxyResource` added method `system_data`
  - Model `ProxyResource` added method `type`
  - Model `Resource` added method `id`
  - Model `Resource` added method `name`
  - Model `Resource` added method `system_data`
  - Model `Resource` added method `type`
  - Model `StandbyContainerGroupPoolElasticityProfile` added method `max_ready_capacity`
  - Model `StandbyContainerGroupPoolElasticityProfile` added method `refill_policy`
  - Model `StandbyContainerGroupPoolResource` added method `id`
  - Model `StandbyContainerGroupPoolResource` added method `location`
  - Model `StandbyContainerGroupPoolResource` added method `name`
  - Model `StandbyContainerGroupPoolResource` added method `properties`
  - Model `StandbyContainerGroupPoolResource` added method `system_data`
  - Model `StandbyContainerGroupPoolResource` added method `tags`
  - Model `StandbyContainerGroupPoolResource` added method `type`
  - Model `StandbyContainerGroupPoolResourceProperties` added method `container_group_properties`
  - Model `StandbyContainerGroupPoolResourceProperties` added method `elasticity_profile`
  - Model `StandbyContainerGroupPoolResourceProperties` added method `provisioning_state`
  - Model `StandbyContainerGroupPoolResourceUpdate` added method `properties`
  - Model `StandbyContainerGroupPoolResourceUpdate` added method `tags`
  - Model `StandbyContainerGroupPoolResourceUpdateProperties` added method `container_group_properties`
  - Model `StandbyContainerGroupPoolResourceUpdateProperties` added method `elasticity_profile`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added method `max_ready_capacity`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added method `min_ready_capacity`
  - Model `StandbyVirtualMachinePoolElasticityProfile` added property `min_ready_capacity`
  - Model `StandbyVirtualMachinePoolResource` added method `id`
  - Model `StandbyVirtualMachinePoolResource` added method `location`
  - Model `StandbyVirtualMachinePoolResource` added method `name`
  - Model `StandbyVirtualMachinePoolResource` added method `properties`
  - Model `StandbyVirtualMachinePoolResource` added method `system_data`
  - Model `StandbyVirtualMachinePoolResource` added method `tags`
  - Model `StandbyVirtualMachinePoolResource` added method `type`
  - Model `StandbyVirtualMachinePoolResourceProperties` added method `attached_virtual_machine_scale_set_id`
  - Model `StandbyVirtualMachinePoolResourceProperties` added method `elasticity_profile`
  - Model `StandbyVirtualMachinePoolResourceProperties` added method `provisioning_state`
  - Model `StandbyVirtualMachinePoolResourceProperties` added method `virtual_machine_state`
  - Model `StandbyVirtualMachinePoolResourceUpdate` added method `properties`
  - Model `StandbyVirtualMachinePoolResourceUpdate` added method `tags`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added method `attached_virtual_machine_scale_set_id`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added method `elasticity_profile`
  - Model `StandbyVirtualMachinePoolResourceUpdateProperties` added method `virtual_machine_state`
  - Model `StandbyVirtualMachineResource` added method `id`
  - Model `StandbyVirtualMachineResource` added method `name`
  - Model `StandbyVirtualMachineResource` added method `properties`
  - Model `StandbyVirtualMachineResource` added method `system_data`
  - Model `StandbyVirtualMachineResource` added method `type`
  - Model `StandbyVirtualMachineResourceProperties` added method `provisioning_state`
  - Model `StandbyVirtualMachineResourceProperties` added method `virtual_machine_resource_id`
  - Model `Subnet` added method `id`
  - Model `SystemData` added method `created_at`
  - Model `SystemData` added method `created_by`
  - Model `SystemData` added method `created_by_type`
  - Model `SystemData` added method `last_modified_at`
  - Model `SystemData` added method `last_modified_by`
  - Model `SystemData` added method `last_modified_by_type`
  - Model `TrackedResource` added method `id`
  - Model `TrackedResource` added method `location`
  - Model `TrackedResource` added method `name`
  - Model `TrackedResource` added method `system_data`
  - Model `TrackedResource` added method `tags`
  - Model `TrackedResource` added method `type`
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
