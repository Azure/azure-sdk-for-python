# Release History

## 1.0.0b3 (Unreleased)

### Features Added
- Added the ability specify the API version by an optional `api_version` keyword parameter.
- New function `list_rooms` added in `RoomsClient` to list all created rooms.
- Added pagination support for `list_participants`.

### Breaking Changes
- Removed `participants` from `CommunicationRoom` class.
- Removed `room_join_policy`, all rooms are invite-only by default.
- `update_room` no longer accepts participant list as input.
- Replaced `add_participants` and `update_participants` with `add_or_update_participants`.
- Renamed `RoleType` to `ParticipantRole`.
- Renamed `created_on` to `created_at` in `CommunicationRoom`.
- Renamed `get_participants` to `list_participants` in `RoomsClient`.

## 1.0.0b2 (2022-08-31)

### Bugs Fixed
 - Invalid datestrings for `valid_from` and `valid_until` raises exception

### Other Changes
Python 3.6 is no longer supported. Please use Python version 3.7 or later. For more details, please read our page on [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy).

## 1.0.0b1 (2022-08-10)

- Initial version
