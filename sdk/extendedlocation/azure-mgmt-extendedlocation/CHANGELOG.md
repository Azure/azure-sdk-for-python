# Release History

## 2.1.0b1 (2026-04-15)

### Features Added

  - Model `CustomLocationOperation` added property `display`
  - Model `MatchExpressionsProperties` added property `values_property`
  - Model `PatchableCustomLocations` added property `properties`
  - Model `PatchableResourceSyncRule` added property `properties`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `TrackedResource` added property `system_data`
  - Added model `CustomLocationOperationValueDisplay`
  - Model `CustomLocationsOperations` added parameter `properties` in method `update`

### Breaking Changes

  - Deleted or renamed model `CustomLocations`
  - Model `CustomLocationOperation` deleted or renamed its instance variable `description`
  - Model `CustomLocationOperation` deleted or renamed its instance variable `operation`
  - Model `CustomLocationOperation` deleted or renamed its instance variable `provider`
  - Model `CustomLocationOperation` deleted or renamed its instance variable `resource`
  - Model `MatchExpressionsProperties` deleted or renamed its instance variable `values`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `authentication`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `cluster_extension_ids`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `display_name`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `host_resource_id`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `host_type`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `namespace`
  - Model `PatchableCustomLocations` deleted or renamed its instance variable `provisioning_state`
  - Model `PatchableResourceSyncRule` deleted or renamed its instance variable `priority`
  - Model `PatchableResourceSyncRule` deleted or renamed its instance variable `provisioning_state`
  - Model `PatchableResourceSyncRule` deleted or renamed its instance variable `selector`
  - Model `PatchableResourceSyncRule` deleted or renamed its instance variable `target_resource_group`
  - Deleted or renamed model `CustomLocationOperationsList`
  - Method `CustomLocationsOperations.update` changed its parameter `identity` from `positional_or_keyword` to `keyword_only`
  - Method `CustomLocationsOperations.update` changed its parameter `tags` from `positional_or_keyword` to `keyword_only`
  - Method `CustomLocationsOperations.update` inserted a `positional_or_keyword` parameter `parameters`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `authentication` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `cluster_extension_ids` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `display_name` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `host_resource_id` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `host_type` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `namespace` of kind `positional_or_keyword`
  - Method `CustomLocationsOperations.update` deleted or renamed its parameter `provisioning_state` of kind `positional_or_keyword`
  - Method `ResourceSyncRulesOperations.begin_update` inserted a `positional_or_keyword` parameter `parameters`
  - Method `ResourceSyncRulesOperations.begin_update` deleted or renamed its parameter `tags` of kind `positional_or_keyword`
  - Method `ResourceSyncRulesOperations.begin_update` deleted or renamed its parameter `priority` of kind `positional_or_keyword`
  - Method `ResourceSyncRulesOperations.begin_update` deleted or renamed its parameter `selector` of kind `positional_or_keyword`
  - Method `ResourceSyncRulesOperations.begin_update` deleted or renamed its parameter `target_resource_group` of kind `positional_or_keyword`

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
