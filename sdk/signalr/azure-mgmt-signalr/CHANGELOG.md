# Release History

## 1.1.0 (2022-03-28)

**Features**

  - Added operation group SignalRCustomCertificatesOperations
  - Added operation group SignalRCustomDomainsOperations
  - Model SignalRResource has a new parameter live_trace_configuration

## 1.0.0 (2021-11-01)

**Features**

  - Model SignalRResource has a new parameter disable_aad_auth
  - Model SignalRResource has a new parameter host_name_prefix
  - Model SignalRResource has a new parameter resource_log_configuration
  - Model SignalRResource has a new parameter disable_local_auth
  - Model SignalRResource has a new parameter public_network_access
  - Model PrivateEndpointConnection has a new parameter group_ids
  - Added operation SignalROperations.list_skus

## 1.0.0b2 (2021-05-20)

**Features**

  - Model SignalRResource has a new parameter shared_private_link_resources
  - Model SignalRResource has a new parameter system_data
  - Model PrivateLinkResource has a new parameter shareable_private_link_resource_types
  - Model PrivateEndpointConnection has a new parameter system_data
  - Added operation SignalRPrivateEndpointConnectionsOperations.list
  - Added operation group SignalRSharedPrivateLinkResourcesOperations

## 1.0.0b1 (2020-12-02)

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

## 0.4.0 (2020-05-29)

**Features**

  - Model ServiceSpecification has a new parameter log_specifications
  - Model SignalRResource has a new parameter network_ac_ls
  - Model SignalRResource has a new parameter upstream
  - Model SignalRResource has a new parameter private_endpoint_connections
  - Model SignalRResource has a new parameter kind
  - Model Operation has a new parameter is_data_action
  - Model SignalRCreateOrUpdateProperties has a new parameter upstream
  - Model SignalRCreateOrUpdateProperties has a new parameter network_ac_ls
  - Added operation group SignalRPrivateEndpointConnectionsOperations
  - Added operation group SignalRPrivateLinkResourcesOperations

**General Breaking Changes**

This version uses a next-generation code generator that *might*
introduce breaking changes. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - SignalRClient cannot be imported from
    `azure.mgmt.signalr.signalr_client` anymore (import from
    `azure.mgmt.signalr` works like before)
  - SignalRClientConfiguration import has been moved from
    `azure.mgmt.signalr.signalr_client`
    to `azure.mgmt.signalr`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using `azure.mgmt.signalr.models.my_class` (import from
    `azure.mgmt.signalr.models` works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.signalr.operations.my_class_operations` (import from
    `azure.mgmt.signalr.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.3.0 (2019-08-06)

**Features**

  - Model SignalRResource has a new parameter cors
  - Model SignalRResource has a new parameter features
  - Model SignalRCreateOrUpdateProperties has a new parameter cors
  - Model SignalRCreateOrUpdateProperties has a new parameter feature

## 0.2.0 (2019-05-21)

  - Add restart operation

## 0.1.1 (2018-09-04)

**Features**

  - Model SignalRKeys has a new parameter secondary_connection_string
  - Model SignalRKeys has a new parameter primary_connection_string
  - Model MetricSpecification has a new parameter dimensions
  - Model SignalRResource has a new parameter version
  - Added operation group UsagesOperations

## 0.1.0 (2018-05-07)

  - Initial Release
