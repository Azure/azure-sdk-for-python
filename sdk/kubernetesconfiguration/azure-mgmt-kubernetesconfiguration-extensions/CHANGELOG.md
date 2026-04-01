# Release History

## 1.0.0b2 (2026-03-18)

### Features Added

  - Client `KubernetesConfigurationExtensionsMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `KubernetesConfigurationExtensionsMgmtClient` added method `send_request`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Added model `PatchExtensionProperties`
  - Added enum `ResourceIdentityType`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `PatchExtension` moved instance variable `auto_upgrade_minor_version`, `release_train`, `version`, `configuration_settings` and `configuration_protected_settings` under property `properties`
  - Method `ExtensionsOperations.begin_delete` changed its parameter `force_delete` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ExtensionsList` which actually was not used by SDK users

## 1.0.0b1 (2025-05-19)

### Other Changes

  - Initial version
