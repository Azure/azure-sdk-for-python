# Release History

## 1.0.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0 (2024-06-13)

This release targets Azure Dev Center 2023-04-01 General Available API, which is the same version as the previous 1.0.0-beta.3 release. The main improvement was the addition of models as Convenience API was enabled for the SDK. 

### Features Added

- Added classes for each Dev Center concept.
    - `models`:
        - Catalog
        - DevBox
        - DevBoxAction
        - DevBoxActionDelayResult
        - DevBoxNextAction
        - Environment
        - EnvironmentDefinition
        - EnvironmentDefinitionParameter
        - EnvironmentType
        - Error
        - HardwareProfile
        - ImageReference
        - InnerError
        - OperationDetails
        - OSDisk
        - Pool
        - Project
        - RemoteConnection
        - Schedule
        - StopOnDisconnectConfiguration
        - StorageProfile
        
    - `enums`:
        - DevBoxActionDelayStatus
        - DevBoxActionType
        - DevBoxProvisioningState
        - EnvironmentProvisioningState
        - EnvironmentTypeStatus
        - HibernateSupport
        - LocalAdministratorStatus
        - OperationStatus
        - OSType
        - ParameterType
        - PoolHealthStatus
        - PowerState
        - ScheduledFrequency
        - ScheduledType
        - SkuName
        - StopOnDisconnectEnableStatus


- Updated each previous client method to return the correspondent model. E.g. The response type for `get_dev_box` was updated from `JSON` to `DevBox` model.   

### Breaking Changes

- Removed `filter`  and `top` as optional request parameters from all list operations
    - list_pools
    - list_schedules
    - list_dev_boxes
    - list_all_dev_boxes
    - list_all_dev_boxes_by_user
    - list_projects
    - list_environments
    - list_all_environments
    - list_environment_definitions
    - list_environment_definitions_by_catalog
    - list_environment_types
    - list_catalogs
    
### Other Changes

 - Added more samples

## 1.0.0b3 (2023-11-02)

This release updates the Azure DevCenter library to use the 2023-04-01 GA API.

### Breaking Changes

 - `DevCenterClient.dev_center`, `DevCenterClient.dev_box` and `DevCenterClient.environment` operation groups were removed. Operations are accessed directly through the `DevCenterClient`.
 -  Environments now works with with "environment definitions" instead of "catalog items". E.g. `DevCenterClient.get_environment` operation returns `environmentDefinitionName` property instead of `catalogItemName`.     
 -  The environment used in `DevCenterClient.begin_create_or_update_environment` requires passing `environmentDefinitionName` and `catalogName` parameters instead of `catalogItemName`.
 - `user_id` is no longer a parameter with default value.
 - All `actions` operations have `dev_box` added to their names. E.g. `get_action` operation is updated to `get_dev_box_action`

### Other Changes

 - Updated samples
 - Improved integration test coverage with session records  

## 1.0.0b2 (2023-02-07)

This release updates the Azure DevCenter library to use the 2022-11-11-preview API.

### Breaking Changes

- `DevCenterClient` now accepts an endpoint URI on construction rather than tenant ID + dev center name.

### Features Added

- Added upcoming actions APIs to dev boxes.
    - `delay_upcoming_action`
    - `get_upcoming_action`
    - `list_upcoming_actions`
    - `skip_upcoming_action`

### Bugs Fixed

- Invalid response types removed from `begin_delete_dev_box`, `begin_start_dev_box`, and `begin_stop_dev_box` APIs.
- Invalid `begin_delete_environment_action` API removed from `DevCenterClient`.
- Unimplemented artifacts APIs removed from `DevCenterClient`.

## 1.0.0b1 (2022-11-11)

- Initial version for the DevCenter service


