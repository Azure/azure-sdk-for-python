# Release History

## 2.0.0 (2026-07-29)

### Features Added

  - Client `PrivateDnsManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `PrivateDnsManagementClient` added method `send_request`
  - Model `PrivateZone` added property `properties`
  - Model `PrivateZone` added property `system_data`
  - Model `ProxyResource` added property `system_data`
  - Model `RecordSet` added property `properties`
  - Model `RecordSet` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `VirtualNetworkLink` added property `properties`
  - Model `VirtualNetworkLink` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `PrivateZoneProperties`
  - Added model `RecordSetProperties`
  - Added model `SystemData`
  - Added model `VirtualNetworkLinkProperties`
  - Model `PrivateZonesOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `PrivateZonesOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `PrivateZonesOperations` added parameter `etag` in method `begin_delete`
  - Model `PrivateZonesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `PrivateZonesOperations` added parameter `etag` in method `begin_update`
  - Model `PrivateZonesOperations` added parameter `match_condition` in method `begin_update`
  - Model `RecordSetsOperations` added parameter `etag` in method `create_or_update`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `create_or_update`
  - Model `RecordSetsOperations` added parameter `etag` in method `delete`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `delete`
  - Model `RecordSetsOperations` added parameter `etag` in method `update`
  - Model `RecordSetsOperations` added parameter `match_condition` in method `update`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_delete`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_delete`
  - Model `VirtualNetworkLinksOperations` added parameter `etag` in method `begin_update`
  - Model `VirtualNetworkLinksOperations` added parameter `match_condition` in method `begin_update`

### Breaking Changes

  - Model `PrivateZone` deleted or renamed its instance variable `internal_id`
  - Model `PrivateZone` deleted or renamed its instance variable `max_number_of_record_sets`
  - Model `PrivateZone` deleted or renamed its instance variable `max_number_of_virtual_network_links`
  - Model `PrivateZone` deleted or renamed its instance variable `max_number_of_virtual_network_links_with_registration`
  - Model `PrivateZone` deleted or renamed its instance variable `number_of_record_sets`
  - Model `PrivateZone` deleted or renamed its instance variable `number_of_virtual_network_links`
  - Model `PrivateZone` deleted or renamed its instance variable `number_of_virtual_network_links_with_registration`
  - Model `PrivateZone` deleted or renamed its instance variable `provisioning_state`
  - Model `RecordSet` deleted or renamed its instance variable `a_records`
  - Model `RecordSet` deleted or renamed its instance variable `aaaa_records`
  - Model `RecordSet` deleted or renamed its instance variable `cname_record`
  - Model `RecordSet` deleted or renamed its instance variable `fqdn`
  - Model `RecordSet` deleted or renamed its instance variable `is_auto_registered`
  - Model `RecordSet` deleted or renamed its instance variable `metadata`
  - Model `RecordSet` deleted or renamed its instance variable `mx_records`
  - Model `RecordSet` deleted or renamed its instance variable `ptr_records`
  - Model `RecordSet` deleted or renamed its instance variable `soa_record`
  - Model `RecordSet` deleted or renamed its instance variable `srv_records`
  - Model `RecordSet` deleted or renamed its instance variable `ttl`
  - Model `RecordSet` deleted or renamed its instance variable `txt_records`
  - Model `VirtualNetworkLink` deleted or renamed its instance variable `provisioning_state`
  - Model `VirtualNetworkLink` deleted or renamed its instance variable `registration_enabled`
  - Model `VirtualNetworkLink` deleted or renamed its instance variable `resolution_policy`
  - Model `VirtualNetworkLink` deleted or renamed its instance variable `virtual_network`
  - Model `VirtualNetworkLink` deleted or renamed its instance variable `virtual_network_link_state`
  - Deleted or renamed model `PrivateZoneListResult`
  - Deleted or renamed model `RecordSetListResult`
  - Deleted or renamed model `TrackedResource`
  - Deleted or renamed model `VirtualNetworkLinkListResult`
  - Method `PrivateZonesOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `PrivateZonesOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `PrivateZonesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `PrivateZonesOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `RecordSetsOperations.list` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.list_by_type` changed its parameter `recordsetnamesuffix` from `positional_or_keyword` to `keyword_only`
  - Method `RecordSetsOperations.update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `VirtualNetworkLinksOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `PrivateZonesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'content_type', 'if_match', 'if_none_match', 'parameters', 'private_zone_name', 'resource_group_name', 'kwargs']` to `['self', 'content_type', 'etag', 'match_condition', 'parameters', 'private_zone_name', 'resource_group_name', 'kwargs']`
  - Method `VirtualNetworkLinksOperations.begin_create_or_update` re-ordered its parameters from `['self', 'content_type', 'if_match', 'if_none_match', 'parameters', 'private_zone_name', 'resource_group_name', 'virtual_network_link_name', 'kwargs']` to `['self', 'content_type', 'etag', 'match_condition', 'parameters', 'private_zone_name', 'resource_group_name', 'virtual_network_link_name', 'kwargs']`
  - Method `RecordSetsOperations.create_or_update` re-ordered its parameters from `['self', 'content_type', 'if_match', 'if_none_match', 'parameters', 'private_zone_name', 'record_type', 'relative_record_set_name', 'resource_group_name', 'kwargs']` to `['self', 'content_type', 'etag', 'match_condition', 'parameters', 'private_zone_name', 'record_type', 'relative_record_set_name', 'resource_group_name', 'kwargs']`

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
