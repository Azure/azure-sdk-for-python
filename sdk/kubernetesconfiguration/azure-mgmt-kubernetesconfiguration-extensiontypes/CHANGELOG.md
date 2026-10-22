# Release History

## 1.0.0b2 (2026-03-18)

### Features Added

  - Client `KubernetesConfigurationExtensionTypesMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `KubernetesConfigurationExtensionTypesMgmtClient` added method `send_request`
  - Model `ClusterScopeSettings` added property `system_data`
  - Model `ExtensionType` added property `system_data`
  - Model `ExtensionTypeVersionForReleaseTrain` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Added enum `CreatedByType`
  - Added model `SystemData`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Method `ExtensionTypesOperations.cluster_list_versions` changed its parameter `release_train`/`major_version`/`show_latest` from `positional_or_keyword` to `keyword_only`
  - Method `ExtensionTypesOperations.list` changed its parameter `publisher_id`/`offer_id`/`plan_id`/`release_train` from `positional_or_keyword` to `keyword_only`
  - Method `ExtensionTypesOperations.list_versions` changed its parameter `release_train`/`cluster_type`/`major_version`/`show_latest` from `positional_or_keyword` to `keyword_only`
  - Method `ExtensionTypesOperations.location_list` changed its parameter `publisher_id`/`offer_id`/`plan_id`/`release_train`/`cluster_type` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ExtensionTypeVersionsList`/`ExtensionTypesList` which actually were not used by SDK users

## 1.0.0b1 (2025-05-19)

### Other Changes

  - Initial version
