# Release History

## 1.0.0 (2021-11-09)

### Breaking changes

- rename operation `generate_client_token` to `get_client_access_token`
- moved operation `build_authentication_token` into `get_client_access_token` on the client
- rename parameter `role` to `roles` of operation `get_client_access_token`
- remove the `operations` namespace from `azure.messaging.webpubsubservice`
- rename operation `check_permission` to `has_permission`
- operations `connection_exists`, `group_exists`, `user_exists`, and `has_permission` now return boolean values instead of raising

### Bug Fixes

- add port to client's endpoint if included in connection string for `WebPubSubServiceClient.from_connection_string`
- fix proxy redirection to the endpoint specified in kwarg `reverse_proxy_endpoint` to run in correct policy placement and to not be overridden by `CustomHookPolicy`.

## 1.0.0b2 (2021-10-14)

- Change api-version to `2021-10-01`
- Add operations to client
- Support AAD
- Support Api Management Proxy

## 1.0.0b1 (2021-04-27)

- Initial version
