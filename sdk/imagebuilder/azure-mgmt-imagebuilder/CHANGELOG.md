# Release History

## 2.0.0 (2026-05-20)

### Features Added

  - Client `ImageBuilderClient` added parameter `cloud_setting` in method `__init__`
  - Client `ImageBuilderClient` added method `send_request`
  - Model `ImageTemplatePropertiesOptimize` added property `workload`
  - Model `ImageTemplateSharedImageDistributor` added property `replication_mode`
  - Model `Trigger` added property `properties`
  - Added model `DataDisk`
  - Added model `ImageTemplatePropertiesOptimizeWorkload`
  - Added enum `ReplicationMode`
  - Added enum `WorkloadOptimizationState`

### Breaking Changes

  - Model `Trigger` deleted or renamed its instance variable `kind`
  - Model `Trigger` deleted or renamed its instance variable `status`
  - Model `Trigger` deleted or renamed its instance variable `provisioning_state`
  - Deleted or renamed model `RunOutputCollection`
  - Deleted or renamed model `TriggerCollection`

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version