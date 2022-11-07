# Release History

## 1.0.0b2 (2022-11-07)

### Features Added

  - Model CustomizationPolicy has a new parameter type_properties_type
  - Model DedicatedCloudNode has a new parameter id_properties_sku_description_id
  - Model DedicatedCloudNode has a new parameter name_properties_sku_description_name
  - Model PrivateCloud has a new parameter type_properties_type

### Breaking Changes

  - Client name is changed from `VMwareCloudSimpleClient` to `VMwareCloudSimple`
  - Model CustomizationPolicy no longer has parameter customization_policy_properties_type
  - Model DedicatedCloudNode no longer has parameter id1
  - Model DedicatedCloudNode no longer has parameter name1
  - Model PrivateCloud no longer has parameter private_cloud_properties_type
  - Operation CustomizationPoliciesOperations.get has a new parameter kwargs
  - Operation CustomizationPoliciesOperations.list has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.delete has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.get has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.list_by_resource_group has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.list_by_subscription has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.update has a new parameter dedicated_cloud_node_request
  - Operation DedicatedCloudNodesOperations.update has a new parameter kwargs
  - Operation DedicatedCloudNodesOperations.update no longer has parameter tags
  - Operation DedicatedCloudServicesOperations.create_or_update has a new parameter kwargs
  - Operation DedicatedCloudServicesOperations.get has a new parameter kwargs
  - Operation DedicatedCloudServicesOperations.list_by_resource_group has a new parameter kwargs
  - Operation DedicatedCloudServicesOperations.list_by_subscription has a new parameter kwargs
  - Operation DedicatedCloudServicesOperations.update has a new parameter dedicated_cloud_service_request
  - Operation DedicatedCloudServicesOperations.update has a new parameter kwargs
  - Operation DedicatedCloudServicesOperations.update no longer has parameter tags
  - Operation Operations.get has a new parameter kwargs
  - Operation Operations.get has a new parameter referer
  - Operation Operations.list has a new parameter kwargs
  - Operation PrivateCloudsOperations.get has a new parameter kwargs
  - Operation PrivateCloudsOperations.list has a new parameter kwargs
  - Operation ResourcePoolsOperations.get has a new parameter kwargs
  - Operation ResourcePoolsOperations.list has a new parameter kwargs
  - Operation SkusAvailabilityOperations.list has a new parameter kwargs
  - Operation UsagesOperations.list has a new parameter kwargs
  - Operation VirtualMachineTemplatesOperations.get has a new parameter kwargs
  - Operation VirtualMachineTemplatesOperations.list has a new parameter kwargs
  - Operation VirtualMachinesOperations.get has a new parameter kwargs
  - Operation VirtualMachinesOperations.list_by_resource_group has a new parameter kwargs
  - Operation VirtualMachinesOperations.list_by_subscription has a new parameter kwargs
  - Operation VirtualNetworksOperations.get has a new parameter kwargs
  - Operation VirtualNetworksOperations.list has a new parameter kwargs
  - Renamed operation DedicatedCloudNodesOperations.create_or_update to DedicatedCloudNodesOperations.begin_create_or_update
  - Renamed operation DedicatedCloudServicesOperations.delete to DedicatedCloudServicesOperations.begin_delete
  - Renamed operation VirtualMachinesOperations.create_or_update to VirtualMachinesOperations.begin_create_or_update
  - Renamed operation VirtualMachinesOperations.delete to VirtualMachinesOperations.begin_delete
  - Renamed operation VirtualMachinesOperations.start to VirtualMachinesOperations.begin_start
  - Renamed operation VirtualMachinesOperations.stop to VirtualMachinesOperations.begin_stop
  - Renamed operation VirtualMachinesOperations.update to VirtualMachinesOperations.begin_update

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

## 0.2.0 (2019-10-31)

**Features**

  - Model VirtualNic has a new parameter customization
  - Model VirtualMachine has a new parameter customization
  - Added operation group CustomizationPoliciesOperations

## 0.1.0 (2019-10-08)

  - Initial Release
