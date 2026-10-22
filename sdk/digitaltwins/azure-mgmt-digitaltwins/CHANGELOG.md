# Release History

## 7.0.0 (2024-10-30)

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 6.4.0 (2023-03-20)

### Features Added

  - Model AzureDataExplorerConnectionProperties has a new parameter adx_relationship_lifecycle_events_table_name
  - Model AzureDataExplorerConnectionProperties has a new parameter adx_twin_lifecycle_events_table_name
  - Model AzureDataExplorerConnectionProperties has a new parameter record_property_and_item_removals
  - Operation TimeSeriesDatabaseConnectionsOperations.begin_delete has a new optional parameter cleanup_connection_artifacts

## 6.4.0b1 (2023-02-16)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 6.3.0 (2022-12-15)

### Features Added

  - Model AzureDataExplorerConnectionProperties has a new parameter identity
  - Model DigitalTwinsEndpointResourceProperties has a new parameter identity
  - Model DigitalTwinsIdentity has a new parameter user_assigned_identities
  - Model EventGrid has a new parameter identity
  - Model EventHub has a new parameter identity
  - Model ServiceBus has a new parameter identity
  - Model TimeSeriesDatabaseConnectionProperties has a new parameter identity

## 6.2.0 (2022-06-28)

**Features**

  - Model DigitalTwinsEndpointResourceProperties.provisioning_state has a new state `Updating`

## 6.1.0 (2022-03-21)

**Features**

  - Added operation group TimeSeriesDatabaseConnectionsOperations
  - Model DigitalTwinsDescription has a new parameter system_data
  - Model DigitalTwinsEndpointResource has a new parameter system_data
  - Model DigitalTwinsResource has a new parameter system_data
  - Model ExternalResource has a new parameter system_data
  - Model Operation has a new parameter properties
  - Model PrivateEndpointConnection has a new parameter system_data

## 6.0.0 (2021-05-18)

- GA release

## 6.0.0b2 (2021-02-26)
* Fix version problem.

## 6.0.0b1 (2021-01-07)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 1.0.0(https://pypi.org/project/azure-mgmt-digitaltwins/1.0.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 1.0.0 (2020-09-24)

* Release as Multi-API package.

## 0.1.0 (2020-05-31)

* Initial Release
