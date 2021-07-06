# Release History

## 1.0.0 (2021-04-27)

**Features**

  - Model Operation has a new parameter properties
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter is_data_action
  - Model SpatialAnchorsAccount has a new parameter plan
  - Model SpatialAnchorsAccount has a new parameter system_data
  - Model SpatialAnchorsAccount has a new parameter sku
  - Model SpatialAnchorsAccount has a new parameter identity
  - Model SpatialAnchorsAccount has a new parameter storage_account_name
  - Model SpatialAnchorsAccount has a new parameter kind
  - Model RemoteRenderingAccount has a new parameter plan
  - Model RemoteRenderingAccount has a new parameter system_data
  - Model RemoteRenderingAccount has a new parameter sku
  - Model RemoteRenderingAccount has a new parameter storage_account_name
  - Model RemoteRenderingAccount has a new parameter kind
  - Added operation group ObjectAnchorsAccountsOperations

## 1.0.0b1 (2020-12-14)

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

## 0.2.0 (2020-05-25)

**Features**

  - Added operation SpatialAnchorsAccountsOperations.list_keys
  - Added operation SpatialAnchorsAccountsOperations.get
  - Added operation SpatialAnchorsAccountsOperations.regenerate_keys
  - Added operation SpatialAnchorsAccountsOperations.delete
  - Added operation group MixedRealityClientOperationsMixin
  - Added operation group RemoteRenderingAccountsOperations

**Breaking changes**

  - Operation SpatialAnchorsAccountsOperations.create has a new signature
  - Operation SpatialAnchorsAccountsOperations.update has a new signature
  - Removed operation SpatialAnchorsAccountsOperations.get_keys

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - MixedRealityClient cannot be imported from
    `azure.mgmt.mixedreality.mixed_reality_client` anymore (import from
    `azure.mgmt.mixedreality` works like before)
  - MixedRealityClientConfiguration import has been moved from
    `azure.mgmt.mixedreality.mixedreality_client`
    to `azure.mgmt.mixedreality`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.mixedreality.models.my_class` (import from
    `azure.mgmt.mixedreality.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.mixedreality.operations.my_class_operations` (import from
    `azure.mgmt.mixedreality.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.1.0 (2019-02-05)

  - Initial Release
