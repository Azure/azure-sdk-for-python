# Release History

## 1.0.0 (2021-04-07)

 - GA release

## 1.0.0b1 (2020-12-03)

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

## 0.2.0 (2020-01-09)

**Features**

  - Model ServerEndpoint has a new parameter recall_status
  - Model ServerEndpoint has a new parameter cloud_tiering_status
  - Model CloudEndpointCreateParameters has a new parameter
    friendly_name
  - Added operation CloudEndpointsOperations.trigger_change_detection
  - Added operation group OperationStatusOperations

**General Breaking Changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. StorageSyncManagementClient cannot be imported from
azure.mgmt.storagesync.storage_sync_management_client anymore (import
from azure.mgmt.storagesync works like before)
StorageSyncManagementClientConfiguration import has been moved from
azure.mgmt.storagesync.storage_sync_management_client to
azure.mgmt.storagesync A model MyClass from a "models" sub-module cannot
be imported anymore using azure.mgmt.storagesync.models.my_class
(import from azure.mgmt.storagesync.models works like before) An
operation class MyClassOperations from an operations sub-module cannot
be imported anymore using
azure.mgmt.storagesync.operations.my_class_operations (import from
azure.mgmt.storagesync.operations works like before) Last but not least,
HTTP connection pooling is now enabled by default. You should always use
a client as a context manager, or call close(), or use no more than one
client per process.

## 0.1.0 (2019-04-05)

  - Initial Release
