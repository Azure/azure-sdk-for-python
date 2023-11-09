# Release History

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
