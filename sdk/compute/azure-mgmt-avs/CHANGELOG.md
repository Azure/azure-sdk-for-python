# Release History

## 7.0.0 (2021-11-11)

**Features**

  - Model PrivateCloudUpdateProperties has a new parameter encryption
  - Model PrivateCloudUpdateProperties has a new parameter availability
  - Model PrivateCloud has a new parameter secondary_circuit
  - Model PrivateCloud has a new parameter identity
  - Model PrivateCloud has a new parameter encryption
  - Model PrivateCloud has a new parameter availability
  - Model PrivateCloudProperties has a new parameter secondary_circuit
  - Model PrivateCloudProperties has a new parameter encryption
  - Model PrivateCloudProperties has a new parameter availability
  - Model PrivateCloudUpdate has a new parameter identity
  - Model PrivateCloudUpdate has a new parameter encryption
  - Model PrivateCloudUpdate has a new parameter availability
  - Model GlobalReachConnection has a new parameter express_route_id
  - Model ClusterUpdate has a new parameter hosts
  - Model ExpressRouteAuthorization has a new parameter express_route_id
  - Model Datastore has a new parameter status
  - Added operation group VirtualMachinesOperations
  - Added operation group PlacementPoliciesOperations

## 7.0.0b1 (2021-07-13)

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


## 2.0.0 (2021-07-13)

**Features**

  - Model PrivateCloud has a new parameter external_cloud_links
  - Model MetricDimension has a new parameter internal_name
  - Model MetricDimension has a new parameter to_be_exported_for_shoebox
  - Added operation PrivateCloudsOperations.rotate_vcenter_password
  - Added operation PrivateCloudsOperations.rotate_nsxt_password
  - Added operation group ScriptExecutionsOperations
  - Added operation group DatastoresOperations
  - Added operation group CloudLinksOperations
  - Added operation group ScriptPackagesOperations
  - Added operation group WorkloadNetworksOperations
  - Added operation group ScriptCmdletsOperations
  - Added operation group AddonsOperations
  - Added operation group GlobalReachConnectionsOperations

**Breaking changes**

  - Operation HcxEnterpriseSitesOperations.create_or_update has a new signature
  - Operation AuthorizationsOperations.create_or_update has a new signature

## 1.0.0 (2020-11-11)

**Features**

  - Model Operation has a new parameter properties
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model ManagementCluster has a new parameter provisioning_state

**Breaking changes**

  - Operation ClustersOperations.create_or_update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature

## 1.0.0rc1 (2020-07-03)

**Features**

  - Model Endpoints has a new parameter hcx_cloud_manager
  - Model Cluster has a new parameter hosts
  - Model Cluster has a new parameter cluster_id
  - Model Cluster has a new parameter cluster_size
  - Model Cluster has a new parameter provisioning_state
  - Added operation group HcxEnterpriseSitesOperations
  - Added operation group AuthorizationsOperations

**Breaking changes**

  - Operation ClustersOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Operation PrivateCloudsOperations.update has a new signature
  - Operation ClustersOperations.create_or_update has a new signature
  - Model Circuit no longer has parameter authorizations
  - Model Cluster no longer has parameter properties
  - Model Cluster has a new required parameter sku
  - Model PrivateCloud has a new signature
  - Model ExpressRouteAuthorization has a new signature
