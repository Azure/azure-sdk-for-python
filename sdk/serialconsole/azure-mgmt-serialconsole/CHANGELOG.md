# Release History

## 1.1.0b2 (2026-05-26)

### Features Added

  - Client `MicrosoftSerialConsoleClient` added parameter `cloud_setting` in method `__init__`
  - Client `MicrosoftSerialConsoleClient` added method `send_request`
  - Model `ProxyResource` added property `system_data`
  - Model `Resource` added property `system_data`
  - Model `SerialPort` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added enum `SerialPortConnectionState`
  - Added model `SystemData`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `DisableSerialConsoleResult` moved instance variable `disabled` under property `properties` whose type is `DisableSerialConsoleResultProperties`
  - Model `EnableSerialConsoleResult` moved instance variable `disabled` under property `properties` whose type is `EnableSerialConsoleResultProperties`
  - Model `SerialConsoleStatus` moved instance variable `disabled` under property `properties` whose type is `SerialConsoleStatusProperties`
  - Deleted or renamed method `SerialPortsOperations.delete`
  - Renamed operation group `MicrosoftSerialConsoleClientOperationsMixin` to `_MicrosoftSerialConsoleClientOperationsMixin`
  - Method `MicrosoftSerialConsoleClient.disable_console` changed return type from `Union[DisableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]` to `DisableSerialConsoleResult`
  - Method `MicrosoftSerialConsoleClient.enable_console` changed return type from `Union[EnableSerialConsoleResult, GetSerialConsoleSubscriptionNotFound]` to `EnableSerialConsoleResult`
  - Method `MicrosoftSerialConsoleClient.get_console_status` changed return type from `Union[SerialConsoleStatus, GetSerialConsoleSubscriptionNotFound]` to `SerialConsoleStatus`

## 1.0.1 (2026-05-12)

### Other Changes

  - Regenerated with latest code generator tool

## 1.1.0b1 (2022-11-01)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0 (2021-05-20)

**Features**

  - Added operation group SerialPortsOperations

## 1.0.0b1 (2020-12-10)

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

## 0.1.0 (2019-04-30)

  - Initial Release
