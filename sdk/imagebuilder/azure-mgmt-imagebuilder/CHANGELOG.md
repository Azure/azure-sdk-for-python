# Release History

## 2.0.0 (2026-05-20)

### Features Added

  - Client `ImageBuilderClient` added parameter `cloud_setting` in method `__init__`
  - Client `ImageBuilderClient` added method `send_request`
  - Model `ImageTemplatePropertiesOptimize` added property `workload`
  - Model `ImageTemplateSharedImageDistributor` added property `replication_mode`
  - Added model `DataDisk`
  - Added model `ImageTemplatePropertiesOptimizeWorkload`
  - Added enum `ReplicationMode`
  - Added enum `WorkloadOptimizationState`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `Trigger` moved instance variable `kind`, `status` and `provisioning_state` under property `properties`

### Other Changes

  - Deleted model `RunOutputCollection`/`TriggerCollection` which actually were not used by SDK users

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version