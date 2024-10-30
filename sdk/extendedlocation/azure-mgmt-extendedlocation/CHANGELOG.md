# Release History

## 2.0.0 (2024-10-30)

### Features Added

  - Method `CustomLocationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, resource_name: str, parameters: CustomLocation, content_type: str)`
  - Method `CustomLocationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, resource_name: str, parameters: IO[bytes], content_type: str)`

### Breaking Changes

  - Model `CustomLocations` deleted or renamed its instance variable `resource_sync_rules`
  - Deleted or renamed model `CustomLocationFindTargetResourceGroupProperties`
  - Deleted or renamed model `CustomLocationFindTargetResourceGroupResult`
  - Deleted or renamed model `MatchExpressionsProperties`
  - Deleted or renamed model `PatchableResourceSyncRule`
  - Deleted or renamed model `ResourceSyncRule`
  - Deleted or renamed model `ResourceSyncRulePropertiesSelector`
  - Deleted or renamed method `CustomLocationsOperations.find_target_resource_group`
  - Deleted or renamed model `ResourceSyncRulesOperations`

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
