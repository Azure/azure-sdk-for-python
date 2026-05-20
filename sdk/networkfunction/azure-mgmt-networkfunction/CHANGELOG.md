# Release History

## 1.0.0b2 (2026-03-16)

### Features Added

  - Model `TrafficCollectorMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `TrafficCollectorMgmtClient` added method `send_request`
  - Model `AzureTrafficCollector` added property `properties`
  - Model `CollectorPolicy` added property `properties`
  - Model `ProxyResource` added property `system_data`
  - Model `SystemData` added property `last_modified_at`
  - Added model `AzureTrafficCollectorPropertiesFormat`
  - Added model `CloudError`
  - Added model `CollectorPolicyPropertiesFormat`
  - Added model `Resource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AzureTrafficCollector` moved instance variable `collector_policies`, `virtual_hub` and `provisioning_state` under property `properties`
  - Model `CollectorPolicy` moved instance variable `ingestion_policy`, `emission_policies` and `provisioning_state` under property `properties`
  - Method `AzureTrafficCollectorsOperations.begin_create_or_update` moved its parameters `location`/`tags`/`virtual_hub` under property `parameters`
  - Method `CollectorPoliciesOperations.begin_create_or_update` moved its parameters `location`/`tags`/`ingestion_policy`/`emission_policies` under property `parameters`

### Other Changes

  - Deleted model `ApiVersionParameter`/`TrackedResource`/`TrackedResourceSystemData` which actually were not used by SDK users

## 1.0.0b1 (2022-11-18)

* Initial Release
