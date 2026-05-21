# Release History

## 3.0.0b1 (2026-05-20)

### Features Added

  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Added model `CustomLocationFindTargetResourceGroupProperties`
  - Added model `CustomLocationFindTargetResourceGroupResult`
  - Added model `MatchExpressionsProperties`
  - Added model `PatchableResourceSyncRule`
  - Added model `ResourceSyncRule`
  - Added model `ResourceSyncRuleProperties`
  - Added model `ResourceSyncRulePropertiesSelector`
  - Operation group `CustomLocationsOperations` added method `find_target_resource_group`
  - Added operation group `ResourceSyncRulesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Deleted or renamed model `CustomLocations`
  - Model `CustomLocationOperation` moved instance variable `description`, `operation`, `provider` and `resource` under property `display` whose type is `CustomLocationOperationValueDisplay`
  - Model `PatchableCustomLocations` moved instance variable `authentication`, `cluster_extension_ids`, `display_name`, `host_resource_id`, `host_type`, `namespace` and `provisioning_state` under property `properties` whose type is `CustomLocationProperties`
  - Method `CustomLocationsOperations.update` inserted a `positional_or_keyword` parameter `parameters`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `identity` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `authentication` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `cluster_extension_ids` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `display_name` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `host_resource_id` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `host_type` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `namespace` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `provisioning_state` of kind `positional_or_keyword`

### Other Changes

  - Deleted model `CustomLocationOperationsList` which actually was not used by SDK users

## 2.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 1.2.0b1 (2023-02-14)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.1.0 (2022-07-12)

**Features**

  - Added operation CustomLocationsOperations.find_target_resource_group
  - Added operation group ResourceSyncRulesOperations

## 1.0.0 (2021-09-22)

**Features**
  - Adding a new API Version 2021-08-15
  - Adding support for Managed Identity [SystemAssigned]
  - Model PatchableCustomLocations has a new parameter identity
  - Model CustomLocation has a new parameter identity

**Breaking changes**

  - Operation CustomLocationsOperations.update has a new signature

## 1.0.0b2 (2021-05-06)

* Remove v2020_07_15_privatepreview

## 1.0.0b1 (2021-03-25)

* Initial Release
