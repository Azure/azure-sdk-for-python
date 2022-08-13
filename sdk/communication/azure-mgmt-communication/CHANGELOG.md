# Release History

## 0.0.0 (it should be perview) (2022-08-13)



## 2.0.0b1 (2022-06-07)

**Features**

  - Added operation group CommunicationServicesOperations
  - Added operation group DomainsOperations
  - Added operation group EmailServicesOperations
  - Model CommunicationServiceResource has a new parameter linked_domains
  - Model Resource has a new parameter system_data

**Breaking changes**

  - Parameter location of model CommunicationServiceResource is now required
  - Removed operation group CommunicationServiceOperations
  - Removed operation group OperationStatusesOperations

## 1.0.0 (2021-03-29)

**Features**

  - Model CommunicationServiceResource has a new parameter system_data
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Added operation CommunicationServiceOperations.check_name_availability

**Breaking changes**

  - Model Operation no longer has parameter properties



## 1.0.0b4 (2020-11-16)
- Updated `azure-mgmt-communication` version.

## 1.0.0b3 (2020-10-06)
- Updated `azure-mgmt-communication` version.

## 1.0.0b2 (2020-09-22)

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


## 1.0.0b1 (2020-09-22)

* Initial Release
