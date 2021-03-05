# Release History

## 7.0.0 (2020-12-15)

- GA Release

## 7.0.0b1 (2020-10-20)

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

## 2.1.0 (2020-03-15)

**Features**

- Added operation group GraphQueryOperations

## 2.0.0 (2019-06-19)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes for some import. In summary, some modules
were incorrectly visible/importable and have been renamed. This fixed
several issues caused by usage of classes that were not supposed to be
used in the first place.

  - ResourceGraphClient cannot be imported from
    `azure.mgmt.resourcegraph.resource_graph_client` anymore (import
    from `azure.mgmt.resourcegraph` works like before)
  - ResourceGraphClientConfiguration import has been moved from
    `azure.mgmt.resourcegraph.resource_graph_client` to
    `azure.mgmt.resourcegraph`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.resourcegraph.models.my_class` (import
    from `azure.mgmt.resourcegraph.models` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 1.1.0 (2019-06-11)

**Note**

This version was incorrectly released with breaking changes inside. You
should use 1.0 or directly move to 2.0 if want to follow semantic
versionning closely.

**Breaking changes**

  - Result format can be table or objectArray

## 1.0.0 (2019-03-28)

  - Increment the version to show it as GA version no change in the
    contract.

## 0.1.0 (2018-09-07)

  - Initial Release
