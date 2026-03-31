# Release History

## 6.1.0b2 (2026-03-10)

### Features Added

  - Model `UsageManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `UsageManagementClient` added method `send_request`
  - Model `UsageAggregation` added property `properties`
  - Added model `ErrorObjectResponse`
  - Added model `UsageSample`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted or renamed model `InfoField`
  - Renamed enum `OfferTermInfoEnum` to `OfferTermInfoName`
  - Model `UsageAggregation` moved instance variable `subscription_id`, `meter_id`, `usage_start_time`, `usage_end_time`, `quantity`, `unit`, `meter_name`, `meter_category`, `meter_sub_category`, `meter_region`, `info_fields` and `instance_data` under property `properties`
  - Method `UsageAggregatesOperations.list` changed its parameter `reported_start_time`/`reported_end_time`/`show_details`/`aggregation_granularity`/`continuation_token_parameter` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `RateCardQueryParameters` which actually were not used by SDK users

## 6.1.0b1 (2023-02-10)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 6.0.0 (2020-12-22)

- GA release

## 6.0.0b1 (2020-10-22)

This is beta preview version.

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

## 1.0.1 (2018-02-21)

  - usage_aggregation.quantity is now correctly declared as float
  - All operation groups have now a "models" attribute

## 1.0.0 (2017-06-23)

  - Initial stable release

This wheel package is now built with the azure wheel extension

If moved from 0.30.0rc6, expect some tiny renaming like (not
exhaustive):

  - reportedstart_time renamed to reported_start_time
  - self.Name renamed to self.name in some classes
