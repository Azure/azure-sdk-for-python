# Release History

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
