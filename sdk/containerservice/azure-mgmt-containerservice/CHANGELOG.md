# Release History

## 15.0.0 (2021-03-03)

**Features**

  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_node_provision_time
  - Model ManagedClusterPodIdentityProfile has a new parameter allow_network_plugin_kubenet
  - Model KubeletConfig has a new parameter container_log_max_size_mb
  - Model KubeletConfig has a new parameter pod_max_pids
  - Model KubeletConfig has a new parameter container_log_max_files
  - Model SysctlConfig has a new parameter net_core_rmem_default
  - Model SysctlConfig has a new parameter net_core_wmem_default
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter azure_portal_fqdn
  - Model Components1Q1Og48SchemasManagedclusterAllof1 has a new parameter fqdn_subdomain
  - Model ManagedCluster has a new parameter azure_portal_fqdn
  - Model ManagedCluster has a new parameter fqdn_subdomain
  - Model ManagedClusterAgentPoolProfile has a new parameter kubelet_disk_type
  - Model ManagedClusterAgentPoolProfile has a new parameter enable_encryption_at_host
  - Model ManagedClusterAgentPoolProfile has a new parameter node_public_ip_prefix_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter kubelet_disk_type
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_encryption_at_host
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_public_ip_prefix_id
  - Model AgentPool has a new parameter kubelet_disk_type
  - Model AgentPool has a new parameter enable_encryption_at_host
  - Model AgentPool has a new parameter node_public_ip_prefix_id
  - Added operation group MaintenanceConfigurationsOperations

**Breaking changes**

  - Model SysctlConfig no longer has parameter net_ipv4_tcp_rmem
  - Model SysctlConfig no longer has parameter net_ipv4_tcp_wmem

## 14.0.0 (2020-11-23)

**Features**

  - Model ManagedCluster has a new parameter pod_identity_profile
  - Model ManagedCluster has a new parameter auto_upgrade_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter linux_os_config
  - Model ManagedClusterAgentPoolProfile has a new parameter kubelet_config
  - Model ManagedClusterAgentPoolProfile has a new parameter pod_subnet_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter linux_os_config
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter kubelet_config
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter pod_subnet_id
  - Model ManagedClusterAPIServerAccessProfile has a new parameter private_dns_zone
  - Model AgentPool has a new parameter linux_os_config
  - Model AgentPool has a new parameter kubelet_config
  - Model AgentPool has a new parameter pod_subnet_id

## 14.0.0b1 (2020-10-23)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 9.4.0 (https://pypi.org/project/azure-mgmt-containerservice/9.4.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 9.4.0 (2020-09-11)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter power_state
  - Model ManagedClusterAgentPoolProfile has a new parameter os_disk_type
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_empty_bulk_delete
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter skip_nodes_with_local_storage
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter max_total_unready_percentage
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter ok_total_unready_count
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter expander
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter skip_nodes_with_system_pods
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter new_pod_scale_up_delay
  - Model AgentPool has a new parameter power_state
  - Model AgentPool has a new parameter os_disk_type
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter power_state
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter os_disk_type
  - Model ManagedCluster has a new parameter power_state
  - Added operation ManagedClustersOperations.start
  - Added operation ManagedClustersOperations.stop
  - Added operation group ResolvePrivateLinkServiceIdOperations
  - Added operation group PrivateLinkResourcesOperations

## 9.3.0 (2020-08-24)

**Features**

  - Model ManagedClusterWindowsProfile has a new parameter license_type
  - Added operation ManagedClustersOperations.upgrade_node_image_version

## 9.2.0 (2020-06-24)

**Features**
 
  - Model ManagedClusterIdentity has a new parameter user_assigned_identities
  - Model ManagedClusterAADProfile has a new parameter enable_azure_rbac
  - Model ManagedClusterAgentPoolProfile has a new parameter proximity_placement_group_id
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter proximity_placement_group_id
  - Model AgentPool has a new parameter proximity_placement_group_id
  - Added operation group PrivateEndpointConnectionsOperations

## 9.1.0 (2020-06-03)

**Features**

  - Model AgentPool has a new parameter node_image_version
  - Model AgentPool has a new parameter upgrade_settings
  - Model AgentPoolUpgradeProfile has a new parameter latest_node_image_version
  - Model ManagedClusterAgentPoolProfile has a new parameter node_image_version
  - Model ManagedClusterAgentPoolProfile has a new parameter upgrade_settings
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter node_image_version
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter upgrade_settings

## 9.0.1 (2020-04-09)

**Bugfixes**
  
  - Switch field type to string to avoid unmarshal errors 

## 9.0.0 (2020-03-24)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter mode
  - Model ManagedCluster has a new parameter sku
  - Model OpenShiftManagedCluster has a new parameter refresh_cluster
  - Model ManagedClusterAADProfile has a new parameter admin_group_object_ids
  - Model ManagedClusterAADProfile has a new parameter managed
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter mode
  - Model OpenShiftManagedClusterMasterPoolProfile has a new parameter api_properties
  - Model ManagedClusterPropertiesAutoScalerProfile has a new parameter balance_similar_node_groups
  - Model NetworkProfile has a new parameter management_subnet_cidr
  - Model AgentPool has a new parameter mode

**Breaking changes**

  - Model OpenShiftManagedClusterMasterPoolProfile no longer has parameter name
  - Model OpenShiftManagedClusterMasterPoolProfile no longer has parameter os_type
  - Model NetworkProfile no longer has parameter peer_vnet_id

## 8.3.0 (2020-02-14)

**Features**

  - Model ManagedCluster has a new parameter auto_scaler_profile
  - Model ManagedClusterAgentPoolProfile has a new parameter spot_max_price
  - Model AgentPool has a new parameter spot_max_price
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter spot_max_price
  - Model ContainerServiceNetworkProfile has a new parameter network_mode
  - Added operation ManagedClustersOperations.list_cluster_monitoring_user_credentials

## 8.2.0 (2020-01-07)

**Features**

  - Model ManagedCluster has a new parameter disk_encryption_set_id

## 8.1.0 (2019-12-16)

**Features**

  - Model ContainerServiceNetworkProfile has a new parameter
    outbound_type
  - Model ManagedClusterAgentPoolProfile has a new parameter
    node_labels
  - Model ManagedClusterAgentPoolProfile has a new parameter tags
  - Model ManagedCluster has a new parameter identity_profile
  - Model ManagedClusterLoadBalancerProfile has a new parameter
    idle_timeout_in_minutes
  - Model ManagedClusterLoadBalancerProfile has a new parameter
    allocated_outbound_ports
  - Model AgentPool has a new parameter node_labels
  - Model AgentPool has a new parameter tags
  - Model ManagedClusterAddonProfile has a new parameter identity
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    node_labels
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    tags

## 8.0.0 (2019-10-24)

**Features**

  - Model OpenShiftManagedCluster has a new parameter monitor_profile
  - Model ManagedCluster has a new parameter private_fqdn
  - Added operation
    ManagedClustersOperations.rotate_cluster_certificates

**Breaking changes**

  - Operation AgentPoolsOperations.get_available_agent_pool_versions
    has a new signature

## 7.0.0 (2019-08-30)

**Features**

  - Model ContainerServiceNetworkProfile has a new parameter
    load_balancer_profile
  - Model ManagedCluster has a new parameter
    api_server_access_profile

**Breaking changes**

  - Model ManagedCluster no longer has parameter
    api_server_authorized_ip_ranges

## 6.0.0 (2019-06-20)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_node_public_ip
  - Model ManagedClusterAgentPoolProfile has a new parameter
    scale_set_eviction_policy
  - Model ManagedClusterAgentPoolProfile has a new parameter
    node_taints
  - Model ManagedClusterAgentPoolProfile has a new parameter
    scale_set_priority
  - Model AgentPool has a new parameter enable_node_public_ip
  - Model AgentPool has a new parameter scale_set_eviction_policy
  - Model AgentPool has a new parameter node_taints
  - Model AgentPool has a new parameter scale_set_priority
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    enable_node_public_ip
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    scale_set_eviction_policy
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    node_taints
  - Model ManagedClusterAgentPoolProfileProperties has a new parameter
    scale_set_priority
  - Added operation
    AgentPoolsOperations.get_available_agent_pool_versions
  - Added operation AgentPoolsOperations.get_upgrade_profile

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - ContainerServiceManagementClient cannot be imported from
    `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client`
    anymore (import from `azure.mgmt.containerservice.v20xx_yy_zz`
    works like before)
  - ContainerServiceManagementClientConfiguration import has been moved
    from
    `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client`
    to `azure.mgmt.containerservice.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.containerservice.v20xx_yy_zz.models.my_class`
    (import from `azure.mgmt.containerservice.v20xx_yy_zz.models`
    works like before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.containerservice.v20xx_yy_zz.operations.my_class_operations`
    (import from
    `azure.mgmt.containerservice.v20xx_yy_zz.operations` works like
    before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 5.3.0 (2019-05-03)

**Features**

  - Model OrchestratorProfile has a new parameter is_preview
  - Model OrchestratorVersionProfile has a new parameter is_preview
  - Model ContainerServiceNetworkProfile has a new parameter
    load_balancer_sku
  - Model ManagedCluster has a new parameter identity
  - Model ManagedCluster has a new parameter max_agent_pools
  - Model ManagedCluster has a new parameter windows_profile

## 5.2.0 (2019-04-30)

**Features**

  - OpenShift is now using a GA api version
  - Model OpenShiftManagedCluster has a new parameter cluster_version
  - Model NetworkProfile has a new parameter vnet_id

## 5.1.0 (2019-04-08)

**Features**

  - Model OpenShiftManagedClusterAADIdentityProvider has a new parameter
    customer_admin_group_id

## 5.0.0 (2019-03-19)

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter min_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    availability_zones
  - Model ManagedClusterAgentPoolProfile has a new parameter type
  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_auto_scaling
  - Model ManagedClusterAgentPoolProfile has a new parameter max_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    provisioning_state
  - Model ManagedClusterAgentPoolProfile has a new parameter
    orchestrator_version
  - Model ManagedCluster has a new parameter
    api_server_authorized_ip_ranges
  - Model ManagedCluster has a new parameter
    enable_pod_security_policy
  - Added operation group AgentPoolsOperations

**Breaking changes**

  - Parameter count of model ManagedClusterAgentPoolProfile is now
    required
  - Model ManagedClusterAgentPoolProfile no longer has parameter
    storage_profile

## 4.4.0 (2019-01-09)

**Features**

  - Added operation
    ManagedClustersOperations.reset_service_principal_profile
  - Added operation ManagedClustersOperations.reset_aad_profile

## 4.3.0 (2018-12-13)

**Features**

  - Support for Azure Profiles
  - OpenShift ManagedCluster (preview)

This package also adds Preview version of ManagedCluster (AKS
2018-08-01-preview), this includes the following breaking changes and
features, if you optin for this new API version:

**Features**

  - Model ManagedClusterAgentPoolProfile has a new parameter type
  - Model ManagedClusterAgentPoolProfile has a new parameter max_count
  - Model ManagedClusterAgentPoolProfile has a new parameter
    enable_auto_scaling
  - Model ManagedClusterAgentPoolProfile has a new parameter min_count

**Breaking changes**

  - Parameter count of model ManagedClusterAgentPoolProfile is now
    required
  - Model ManagedClusterAgentPoolProfile no longer has parameter
    storage_profile

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 4.2.2 (2018-08-09)

**Bugfixes**

  - Fix invalid definition of CredentialResult

## 4.2.1 (2018-08-08)

**Bugfixes**

  - Fix some invalid regexp
  - Fix invalid definition of CredentialResult

## 4.2.0 (2018-07-30)

**Features**

  - Add managed_clusters.list_cluster_admin_credentials
  - Add managed_clusters.list_cluster_user_credentials
  - Add managed_clusters.update_tags

**Bugfixes**

  - Fix incorrect JSON description of ManagedCluster class

## 4.1.0 (2018-06-13)

**Features**

  - Add node_resource_group attribute to some models

## 4.0.0 (2018-05-25)

**Features**

  - Added operation ManagedClustersOperations.get_access_profile
  - Updated VM sizes
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 3.0.1 (2018-01-25)

**Bugfixes**

  - Fix incorrect mapping in OrchestratorVersionProfileListResult

## 3.0.0 (2017-12-13)

  - Flattened ManagedCluster so there is no separate properties object
  - Added get_access_profiles operation to managed clusters

## 2.0.0 (2017-10-XX)

**Features**

  - Managed clusters

**Breaking changes**

  - VM is now require for master profile (recommended default:
    standard_d2_v2)

## 1.0.0 (2017-08-08)

  - Initial Release extracted from azure-mgmt-compute 2.1.0
