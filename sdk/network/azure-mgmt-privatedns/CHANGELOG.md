# Release History

## 2.0.0b1 (2026-07-06)

### Features Added

  - Client `PrivateDnsManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `PrivateDnsManagementClient` added method `send_request`
  - Model `PrivateZone` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `RecordSet` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `VirtualNetworkLink` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `SystemData`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `PrivateZone` moved instance variable `max_number_of_record_sets`, `number_of_record_sets`, `max_number_of_virtual_network_links`, `number_of_virtual_network_links`, `max_number_of_virtual_network_links_with_registration`, `number_of_virtual_network_links_with_registration`, `provisioning_state` and `internal_id` under property `properties` whose type is `PrivateZoneProperties`
  - Model `RecordSet` moved instance variable `metadata`, `ttl`, `fqdn`, `is_auto_registered`, `a_records`, `aaaa_records`, `cname_record`, `mx_records`, `ptr_records`, `soa_record`, `srv_records` and `txt_records` under property `properties` whose type is `RecordSetProperties`
  - Model `VirtualNetworkLink` moved instance variable `virtual_network`, `registration_enabled`, `resolution_policy`, `virtual_network_link_state` and `provisioning_state` under property `properties` whose type is `VirtualNetworkLinkProperties`
  - Method `PrivateZonesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` with keyword_only parameters `etag`/`match_condition`
  - Method `PrivateZonesOperations.begin_delete` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `PrivateZonesOperations.begin_update` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` with keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.delete` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.update` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` with keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_delete` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `VirtualNetworkLinksOperations.begin_update` replaced positional_or_keyword parameter `if_match` with keyword_only parameters `etag`/`match_condition`
  - Method `RecordSetsOperations.list` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_type` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `PrivateZoneListResult`/`RecordSetListResult`/`VirtualNetworkLinkListResult` which actually were not used by SDK users
  - Deleted model `TrackedResource` which actually were not used by SDK users

## 1.2.0 (2024-09-23)

### Features Added

  - Model `VirtualNetworkLink` added property `resolution_policy`
  - Added enum `ResolutionPolicy`

## 1.1.0 (2023-05-20)

### Features Added

  - Model PrivateZone has a new parameter internal_id

## 1.1.0b1 (2022-10-28)

### Features Added

  - Model PrivateZone has a new parameter internal_id

## 1.0.0 (2021-03-25)

- GA release

## 1.0.0b1 (2021-02-09)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 10.2.0 (https://pypi.org/project/azure-mgmt-network/10.2.0/)

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 0.1.0 (2019-02-26)

  - Initial Release
