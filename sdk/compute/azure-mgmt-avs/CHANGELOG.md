# Release History

## 9.0.0 (2024-09-22)

### Features Added

  - Client `AVSClient` added operation group `iscsi_paths`
  - Model `CloudLink` added property `provisioning_state`
  - Model `Cluster` added property `vsan_datastore_name`
  - Model `ClusterUpdate` added property `sku`
  - Model `Datastore` added property `elastic_san_volume`
  - Model `Endpoints` added property `nsxt_manager_ip`
  - Model `Endpoints` added property `vcenter_ip`
  - Model `Endpoints` added property `hcx_cloud_manager_ip`
  - Model `HcxEnterpriseSite` added property `provisioning_state`
  - Model `ManagementCluster` added parameter `vsan_datastore_name` in method `__init__`
  - Model `Operation` added property `action_type`
  - Model `PrivateCloud` added property `virtual_network_id`
  - Model `PrivateCloud` added property `dns_zone_type`
  - Model `PrivateCloudUpdate` added property `sku`
  - Model `PrivateCloudUpdate` added property `dns_zone_type`
  - Model `Resource` added property `system_data`
  - Model `ScriptCmdlet` added property `provisioning_state`
  - Model `ScriptCmdlet` added property `audience`
  - Model `ScriptPackage` added property `provisioning_state`
  - Model `Sku` added property `tier`
  - Model `Sku` added property `size`
  - Model `Sku` added property `family`
  - Model `Sku` added property `capacity`
  - Model `VirtualMachine` added property `provisioning_state`
  - Model `WorkloadNetworkGateway` added property `provisioning_state`
  - Model `WorkloadNetworkVirtualMachine` added property `provisioning_state`
  - Added enum `ActionType`
  - Added enum `CloudLinkProvisioningState`
  - Added enum `CreatedByType`
  - Added enum `DnsZoneType`
  - Added model `ElasticSanVolume`
  - Added enum `HcxEnterpriseSiteProvisioningState`
  - Added model `IscsiPath`
  - Added model `IscsiPathListResult`
  - Added enum `IscsiPathProvisioningState`
  - Added model `OperationListResult`
  - Added enum `Origin`
  - Added enum `ScriptCmdletAudience`
  - Added enum `ScriptCmdletProvisioningState`
  - Added enum `ScriptPackageProvisioningState`
  - Added enum `SkuTier`
  - Added model `SystemData`
  - Added enum `VirtualMachineProvisioningState`
  - Added enum `WorkloadNetworkProvisioningState`
  - Added model `IscsiPathsOperations`

### Breaking Changes

  - Model `Operation` deleted or renamed its instance variable `properties`
  - Parameter `location` of model `PrivateCloud` is now required
  - Parameter `type` of model `PrivateCloudIdentity` is now required
  - Parameter `location` of model `TrackedResource` is now required
  - Deleted or renamed model `ClusterProperties`
  - Deleted or renamed model `CommonClusterProperties`
  - Deleted or renamed model `LogSpecification`
  - Deleted or renamed model `MetricDimension`
  - Deleted or renamed model `MetricSpecification`
  - Deleted or renamed model `OperationList`
  - Deleted or renamed model `OperationProperties`
  - Deleted or renamed model `PrivateCloudProperties`
  - Deleted or renamed model `PrivateCloudUpdateProperties`
  - Deleted or renamed model `ServiceSpecification`
  - Deleted or renamed model `WorkloadNetworkName`
  - Method `WorkloadNetworksOperations.get` deleted or renamed its parameter `workload_network_name` of kind `positional_or_keyword`
  - Model WorkloadNetworksOperations renamed its instance variable `list_public_i_ps` to `list_public_ips`

## 9.0.0b1 (2024-06-28)

### Features Added

  - Added operation WorkloadNetworksOperations.list_public_ips
  - Added operation group IscsiPathsOperations
  - Model Addon has a new parameter system_data
  - Model CloudLink has a new parameter provisioning_state
  - Model CloudLink has a new parameter system_data
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter vsan_datastore_name
  - Model ClusterUpdate has a new parameter sku
  - Model Datastore has a new parameter elastic_san_volume
  - Model Datastore has a new parameter system_data
  - Model Endpoints has a new parameter hcx_cloud_manager_ip
  - Model Endpoints has a new parameter nsxt_manager_ip
  - Model Endpoints has a new parameter vcenter_ip
  - Model ExpressRouteAuthorization has a new parameter system_data
  - Model GlobalReachConnection has a new parameter system_data
  - Model HcxEnterpriseSite has a new parameter provisioning_state
  - Model HcxEnterpriseSite has a new parameter system_data
  - Model ManagementCluster has a new parameter vsan_datastore_name
  - Model Operation has a new parameter action_type
  - Model PlacementPolicy has a new parameter system_data
  - Model PrivateCloud has a new parameter dns_zone_type
  - Model PrivateCloud has a new parameter system_data
  - Model PrivateCloud has a new parameter virtual_network_id
  - Model PrivateCloudUpdate has a new parameter dns_zone_type
  - Model PrivateCloudUpdate has a new parameter sku
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ScriptCmdlet has a new parameter audience
  - Model ScriptCmdlet has a new parameter provisioning_state
  - Model ScriptCmdlet has a new parameter system_data
  - Model ScriptExecution has a new parameter system_data
  - Model ScriptPackage has a new parameter provisioning_state
  - Model ScriptPackage has a new parameter system_data
  - Model Sku has a new parameter capacity
  - Model Sku has a new parameter family
  - Model Sku has a new parameter size
  - Model Sku has a new parameter tier
  - Model TrackedResource has a new parameter system_data
  - Model VirtualMachine has a new parameter provisioning_state
  - Model VirtualMachine has a new parameter system_data
  - Model WorkloadNetwork has a new parameter provisioning_state
  - Model WorkloadNetwork has a new parameter system_data
  - Model WorkloadNetworkDhcp has a new parameter system_data
  - Model WorkloadNetworkDnsService has a new parameter system_data
  - Model WorkloadNetworkDnsZone has a new parameter system_data
  - Model WorkloadNetworkGateway has a new parameter provisioning_state
  - Model WorkloadNetworkGateway has a new parameter system_data
  - Model WorkloadNetworkPortMirroring has a new parameter system_data
  - Model WorkloadNetworkPublicIP has a new parameter system_data
  - Model WorkloadNetworkSegment has a new parameter system_data
  - Model WorkloadNetworkVMGroup has a new parameter system_data
  - Model WorkloadNetworkVirtualMachine has a new parameter provisioning_state
  - Model WorkloadNetworkVirtualMachine has a new parameter system_data

### Breaking Changes

  - Model Operation no longer has parameter properties
  - Operation WorkloadNetworksOperations.get no longer has parameter workload_network_name
  - Parameter location of model PrivateCloud is now required
  - Parameter location of model TrackedResource is now required
  - Parameter type of model PrivateCloudIdentity is now required
  - Parameter value of model AddonList is now required
  - Parameter value of model CloudLinkList is now required
  - Parameter value of model ClusterList is now required
  - Parameter value of model DatastoreList is now required
  - Parameter value of model ExpressRouteAuthorizationList is now required
  - Parameter value of model GlobalReachConnectionList is now required
  - Parameter value of model HcxEnterpriseSiteList is now required
  - Parameter value of model PlacementPoliciesList is now required
  - Parameter value of model PrivateCloudList is now required
  - Parameter value of model ScriptCmdletsList is now required
  - Parameter value of model ScriptExecutionsList is now required
  - Parameter value of model ScriptPackagesList is now required
  - Parameter value of model VirtualMachinesList is now required
  - Parameter value of model WorkloadNetworkDhcpList is now required
  - Parameter value of model WorkloadNetworkDnsServicesList is now required
  - Parameter value of model WorkloadNetworkDnsZonesList is now required
  - Parameter value of model WorkloadNetworkGatewayList is now required
  - Parameter value of model WorkloadNetworkList is now required
  - Parameter value of model WorkloadNetworkPortMirroringList is now required
  - Parameter value of model WorkloadNetworkPublicIPsList is now required
  - Parameter value of model WorkloadNetworkSegmentsList is now required
  - Parameter value of model WorkloadNetworkVMGroupsList is now required
  - Parameter value of model WorkloadNetworkVirtualMachinesList is now required
  - Removed operation WorkloadNetworksOperations.list_public_i_ps

## 8.0.0 (2023-08-25)

### Features Added

  - Model ErrorResponse has a new parameter error
  - Model PrivateCloud has a new parameter extended_network_blocks
  - Model PrivateCloudProperties has a new parameter extended_network_blocks
  - Model PrivateCloudUpdate has a new parameter extended_network_blocks
  - Model PrivateCloudUpdateProperties has a new parameter extended_network_blocks

### Breaking Changes

  - Model ErrorResponse no longer has parameter additional_info
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter message
  - Model ErrorResponse no longer has parameter target

## 7.2.0b1 (2022-12-29)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

# 7.1.0 (2022-10-18)

### Features Added

  - Added operation ClustersOperations.list_zones
  - Added operation WorkloadNetworksOperations.get
  - Added operation WorkloadNetworksOperations.list
  - Model EncryptionKeyVaultProperties has a new parameter auto_detected_key_version
  - Model PlacementPolicyUpdate has a new parameter affinity_strength
  - Model PlacementPolicyUpdate has a new parameter azure_hybrid_benefit_type
  - Model PrivateCloud has a new parameter nsx_public_ip_quota_raised
  - Model PrivateCloudProperties has a new parameter nsx_public_ip_quota_raised
  - Model ScriptPackage has a new parameter company
  - Model ScriptPackage has a new parameter uri
  - Model VmHostPlacementPolicyProperties has a new parameter affinity_strength
  - Model VmHostPlacementPolicyProperties has a new parameter azure_hybrid_benefit_type
  - Operation LocationsOperations.check_trial_availability has a new parameter sku

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
