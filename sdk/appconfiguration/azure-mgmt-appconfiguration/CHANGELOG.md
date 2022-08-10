# Release History

## 2.2.0 (2022-08-10)

### Features Added

  - Added operation group ReplicasOperations

### Other Changes

  - Changed to multiapi package(please refer to https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/multiapi.md for more info)

## 2.1.0 (2022-06-08)

**Features**

  - Added operation ConfigurationStoresOperations.begin_purge_deleted
  - Added operation ConfigurationStoresOperations.get_deleted
  - Added operation ConfigurationStoresOperations.list_deleted
  - Added operation Operations.regional_check_name_availability
  - Model ConfigurationStore has a new parameter create_mode
  - Model ConfigurationStore has a new parameter enable_purge_protection
  - Model ConfigurationStore has a new parameter soft_delete_retention_in_days
  - Model ConfigurationStoreUpdateParameters has a new parameter enable_purge_protection

## 2.1.0b2 (2022-02-28)

**Features**

  - Model ConfigurationStoreUpdateParameters has a new parameter enable_purge_protection

## 2.1.0b1 (2022-02-16)

**Features**

  - Added operation ConfigurationStoresOperations.begin_purge_deleted
  - Added operation ConfigurationStoresOperations.get_deleted
  - Added operation ConfigurationStoresOperations.list_deleted
  - Added operation Operations.regional_check_name_availability
  - Model ConfigurationStore has a new parameter create_mode
  - Model ConfigurationStore has a new parameter enable_purge_protection
  - Model ConfigurationStore has a new parameter soft_delete_retention_in_days

## 2.0.0 (2021-06-21)

**Features**

  - Model OperationDefinition has a new parameter properties
  - Model OperationDefinition has a new parameter is_data_action
  - Model OperationDefinition has a new parameter origin
  - Model KeyValue has a new parameter id
  - Model KeyValue has a new parameter type
  - Model KeyValue has a new parameter name
  - Model ConfigurationStore has a new parameter system_data
  - Model ConfigurationStore has a new parameter disable_local_auth
  - Model ConfigurationStoreUpdateParameters has a new parameter disable_local_auth
  - Added operation group KeyValuesOperations

**Breaking changes**

  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter tags
  - Removed operation ConfigurationStoresOperations.list_key_value

## 1.0.1 (2020-09-18)

**Bug fix**

  - Require azure-mgmt-core>=1.2.0 in setup.py

## 1.0.0 (2020-09-15)

**Features**

  - Model ConfigurationStoreUpdateParameters has a new parameter public_network_access

## 1.0.0b1 (2020-06-17)

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

## 0.4.0 (2020-02-07)

**Features**

- Model ConfigurationStoreUpdateParameters has a new parameter encryption
- Model ConfigurationStore has a new parameter encryption
- Added operation group PrivateEndpointConnectionsOperations
- Added operation group PrivateLinkResourcesOperations

**Breaking changes**

- Model ConfigurationStoreUpdateParameters no longer has parameter properties

## 0.3.0 (2019-11-08)

**Features**

  - Model ConfigurationStore has a new parameter identity
  - Model ConfigurationStoreUpdateParameters has a new parameter
    identity
  - Model ConfigurationStoreUpdateParameters has a new parameter sku

**Breaking changes**

  - Operation ConfigurationStoresOperations.create has a new signature
  - Operation ConfigurationStoresOperations.update has a new signature
  - Model ConfigurationStore has a new required parameter sku

## 0.2.0 (2019-11-04)

**Features**

  - Added operation ConfigurationStoresOperations.list_key_value

## 0.1.0 (2019-06-17)

  - Initial Release
