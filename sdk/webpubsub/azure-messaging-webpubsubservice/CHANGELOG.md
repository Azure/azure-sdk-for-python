# Release History

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
