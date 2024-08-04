# Release History

## 2.2.0b2 (2024-05-20)

### Features Added

  - Added operation group ScheduledEventOperations

## 2.2.0b1 (2023-10-22)

### Features Added

  - Added operation ApplyUpdatesOperations.create_or_update_or_cancel

## 2.1.0 (2023-08-18)

### Features Added

  - Added operation ConfigurationAssignmentsOperations.get
  - Added operation ConfigurationAssignmentsOperations.get_parent
  - Added operation group ConfigurationAssignmentsForResourceGroupOperations
  - Added operation group ConfigurationAssignmentsForSubscriptionsOperations
  - Added operation group ConfigurationAssignmentsWithinSubscriptionOperations
  - Model ConfigurationAssignment has a new parameter filter
  - Model MaintenanceConfiguration has a new parameter install_patches

## 2.1.0b2 (2022-11-11)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.1.0b1 (2021-11-23)

**Features**

  - Model MaintenanceConfiguration has a new parameter install_patches
  - Added operation ConfigurationAssignmentsOperations.get
  - Added operation ConfigurationAssignmentsOperations.get_parent
  - Added operation group ConfigurationAssignmentsWithinSubscriptionOperations

## 2.0.0 (2021-05-08)

**Breaking changes**

  - Model MaintenanceConfiguration no longer has parameter install_patches
  - Removed operation ConfigurationAssignmentsOperations.get
  - Removed operation ConfigurationAssignmentsOperations.get_parent
  - Removed operation group ConfigurationAssignmentsWithinSubscriptionOperations

## 1.0.0 (2021-04-20)

**Features**

  - Model Resource has a new parameter system_data
  - Model ApplyUpdate has a new parameter system_data
  - Model ConfigurationAssignment has a new parameter system_data
  - Model Operation has a new parameter is_data_action
  - Model MaintenanceConfiguration has a new parameter system_data
  - Model MaintenanceConfiguration has a new parameter install_patches
  - Added operation ConfigurationAssignmentsOperations.get_parent
  - Added operation ConfigurationAssignmentsOperations.get
  - Added operation ApplyUpdatesOperations.list
  - Added operation group ConfigurationAssignmentsWithinSubscriptionOperations
  - Added operation group ApplyUpdateForResourceGroupOperations
  - Added operation group MaintenanceConfigurationsForResourceGroupOperations

## 1.0.0b1 (2020-12-07)

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

## 0.1.0 (2019-12-03)

  - Initial Release
