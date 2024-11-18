# Release History

## 1.2.2 (Unreleased)

### Features Added
- Added support for SocketIO when generating client access token

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.2.1 (2024-08-13)

### Bugs Fixed
- Fix endpoint parsing issues

## 1.2.0 (2024-08-08)

### Features Added
- Change API version to `2024-01-01`
- Added a `webpubsub_client_access` option to specify the type of client access when generating token. This is used to generate token and client connection URL for a specific client endpoint type
- Added operations `add_connections_to_groups` and `remove_connections_from_groups`

## 1.1.0 (2024-04-24)

### Bugs Fixed
- Use the correct REST API parameter name `groups` in method `get_client_access_token`
- Upgrade dependency package `pyjwt` to `>=2.0.0` which changes the return type of `jwt.encode(...)`. See https://pyjwt.readthedocs.io/en/stable/changelog.html#id30 for detail

### Features Added
- Add overload signatures for operation `send_to_all` ,`send_to_user` ,`send_to_group` and `send_to_connection`
- Update the type of parameter `content` from `IO` to `Union[IO, str, JSON]` for operation `send_to_all` ,`send_to_user` ,`send_to_group` and `send_to_connection`

## 1.1.0b1 (2022-12-12)

### Features Added
- Operation `send_to_all` has a new optional parameter `filter`
- Operation `send_to_user` has a new optional parameter `filter`
- Operation `send_to_group` has a new optional parameter `filter`
- Operation `get_client_access_token` has a new optional parameter `group`
- Added operation `remove_connection_from_all_groups`

## 1.0.1 (2022-02-15)

### Bugs Fixed

- fix authentication who use a `reverse_proxy_endpoint` with either `WebPubSubServiceClient.from_connection_string` or pass in an `AzureKeyCredential` for authentication #22587

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.0.0 (2021-11-10)

### Breaking changes

- rename operation `generate_client_token` to `get_client_access_token`
- moved operation `build_authentication_token` into `get_client_access_token` on the client
- rename parameter `role` to `roles` of operation `get_client_access_token`
- remove the `operations` namespace from `azure.messaging.webpubsubservice`
- rename operation `check_permission` to `has_permission`
- operations `connection_exists`, `group_exists`, `user_exists`, and `has_permission` now return boolean values instead of raising
- move parameter 'hub' from operation to client

### Bug Fixes

- add port to client's endpoint if included in connection string for `WebPubSubServiceClient.from_connection_string`
- fix proxy redirection to the endpoint specified in kwarg `reverse_proxy_endpoint` to run in correct policy placement and to not be overridden by `CustomHookPolicy`.
- fix bug that prevented users from calling `WebPubSubServiceClient.from_connection_string` with python 2.7

## 1.0.0b2 (2021-10-14)

- Change api-version to `2021-10-01`
- Add operations to client
- Support AAD
- Support Api Management Proxy

## 1.0.0b1 (2021-04-27)

- Initial version
