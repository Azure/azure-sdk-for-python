# Release History

## 1.0.0b3 (2023-08-22)

### Other Changes

  - Regular release

## 1.0.0b2 (2022-11-02)

### Features Added

  - Model Controller has a new parameter target_container_host_api_server_fqdn

### Breaking Changes

  - Operation ContainerHostMappingsOperations.get_container_host_mapping has a new parameter container_host_mapping
  - Operation ContainerHostMappingsOperations.get_container_host_mapping has a new parameter kwargs
  - Operation ContainerHostMappingsOperations.get_container_host_mapping no longer has parameter container_host_resource_id
  - Operation ControllersOperations.get has a new parameter kwargs
  - Operation ControllersOperations.list has a new parameter kwargs
  - Operation ControllersOperations.list_by_resource_group has a new parameter kwargs
  - Operation ControllersOperations.list_connection_details has a new parameter kwargs
  - Operation ControllersOperations.list_connection_details has a new parameter list_connection_details_parameters
  - Operation ControllersOperations.list_connection_details no longer has parameter target_container_host_resource_id
  - Operation ControllersOperations.update has a new parameter controller_update_parameters
  - Operation ControllersOperations.update has a new parameter kwargs
  - Operation ControllersOperations.update no longer has parameter tags
  - Operation ControllersOperations.update no longer has parameter target_container_host_credentials_base64
  - Operation Operations.list has a new parameter kwargs
  - Renamed operation ControllersOperations.create to ControllersOperations.begin_create
  - Renamed operation ControllersOperations.delete to ControllersOperations.begin_delete

## 1.0.0b1 (2021-05-26)

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

## 0.2.0 (2019-05-23)

**Features**

  - Model ControllerUpdateParameters has a new parameter
    target_container_host_credentials_base64
  - Added operation group ContainerHostMappingsOperations

**Breaking changes**

  - Operation ControllersOperations.list_connection_details has a new
    signature
  - Operation ControllersOperations.update has a new signature
  - Model ControllerConnectionDetails has a new signature

## 0.1.0 (2018-07-12)

  - Initial Release
