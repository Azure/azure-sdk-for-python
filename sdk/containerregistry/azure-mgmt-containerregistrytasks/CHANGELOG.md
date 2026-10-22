# Release History

## 1.0.0b1 (2026-02-09)

### Features Added

  - Client `ContainerRegistryTasksMgmtClient` added method `send_request`
  - Model `AgentPoolUpdateParameters` added property `properties`
  - Model `TaskRunUpdateParameters` added property `properties`
  - Model `TaskUpdateParameters` added property `properties`
  - Added model `AgentPoolPropertiesUpdateParameters`
  - Added model `TaskPropertiesUpdateParameters`
  - Added model `TaskRunPropertiesUpdateParameters`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `EncodedTaskRunRequest` renamed its instance variable `values` to `values_property`
  - Model `EncodedTaskStep` renamed its instance variable `values` to `values_property`
  - Model `EncodedTaskStepUpdateParameters` renamed its instance variable `values` to `values_property`
  - Model `FileTaskRunRequest` renamed its instance variable `values` to `values_property`
  - Model `FileTaskStep` renamed its instance variable `values` to `values_property`
  - Model `FileTaskStepUpdateParameters` renamed its instance variable `values` to `values_property`
  - Model `OverrideTaskStepProperties` renamed its instance variable `values` to `values_property`
  - Model `AgentPoolUpdateParameters` moved instance variable `count` under property `properties`
  - Model `TaskRunUpdateParameters` moved instance variables `run_request` and `force_update_tag` under property `properties`
  - Model `TaskUpdateParameters` moved instance variables `status`, `platform`, `agent_configuration`, `agent_pool_name`, `timeout`, `step`, `trigger`, `credentials` and `log_template` under property `properties`

### Other Changes

  - This package has been separated from [azure-mgmt-containerregistry](https://pypi.org/project/azure-mgmt-containerregistry)
