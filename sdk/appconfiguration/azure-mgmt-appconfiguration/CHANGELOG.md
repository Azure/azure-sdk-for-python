# Release History

## 1.0.0 (2020-09-15)

**Features**

  - Model ConfigurationStoreUpdateParameters has a new parameter properties
  - Added operation ConfigurationStoresOperations.create
  - Added operation ConfigurationStoresOperations.update
  - Added operation ConfigurationStoresOperations.delete

**Breaking changes**

  - Operation Operations.list has a new signature
  - Operation ConfigurationStoresOperations.list_keys has a new signature
  - Operation ConfigurationStoresOperations.list_by_resource_group has a new signature
  - Operation ConfigurationStoresOperations.list has a new signature
  - Operation ConfigurationStoresOperations.get has a new signature
  - Model ConfigurationStore no longer has parameter private_endpoint_connections
  - Model ConfigurationStore no longer has parameter public_network_access
  - Model ConfigurationStore no longer has parameter encryption
  - Model ConfigurationStoreUpdateParameters no longer has parameter encryption
  - Operation ConfigurationStoresOperations.list_key_value has a new signature
  - Operation ConfigurationStoresOperations.regenerate_key has a new signature
  - Operation Operations.check_name_availability has a new signature
  - Removed operation ConfigurationStoresOperations.begin_update
  - Removed operation ConfigurationStoresOperations.begin_delete
  - Removed operation ConfigurationStoresOperations.begin_create
  - Removed operation group PrivateLinkResourcesOperations
  - Removed operation group PrivateEndpointConnectionsOperations

## 1.0.0b1 (2020-06-17)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

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
