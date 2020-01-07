.. :changelog:

Release History
===============

8.2.0 (2020-01-07)
++++++++++++++++++

**Features**

- Model ManagedCluster has a new parameter disk_encryption_set_id

8.1.0 (2019-12-16)
++++++++++++++++++

**Features**

- Model ContainerServiceNetworkProfile has a new parameter outbound_type
- Model ManagedClusterAgentPoolProfile has a new parameter node_labels
- Model ManagedClusterAgentPoolProfile has a new parameter tags
- Model ManagedCluster has a new parameter identity_profile
- Model ManagedClusterLoadBalancerProfile has a new parameter idle_timeout_in_minutes
- Model ManagedClusterLoadBalancerProfile has a new parameter allocated_outbound_ports
- Model AgentPool has a new parameter node_labels
- Model AgentPool has a new parameter tags
- Model ManagedClusterAddonProfile has a new parameter identity
- Model ManagedClusterAgentPoolProfileProperties has a new parameter node_labels
- Model ManagedClusterAgentPoolProfileProperties has a new parameter tags

8.0.0 (2019-10-24)
++++++++++++++++++

**Features**

- Model OpenShiftManagedCluster has a new parameter monitor_profile
- Model ManagedCluster has a new parameter private_fqdn
- Added operation ManagedClustersOperations.rotate_cluster_certificates

**Breaking changes**

- Operation AgentPoolsOperations.get_available_agent_pool_versions has a new signature

7.0.0 (2019-08-30)
++++++++++++++++++
  
**Features**

- Model ContainerServiceNetworkProfile has a new parameter load_balancer_profile
- Model ManagedCluster has a new parameter api_server_access_profile

**Breaking changes**

- Model ManagedCluster no longer has parameter api_server_authorized_ip_ranges

6.0.0 (2019-06-20)
++++++++++++++++++

**Features**

- Model ManagedClusterAgentPoolProfile has a new parameter enable_node_public_ip
- Model ManagedClusterAgentPoolProfile has a new parameter scale_set_eviction_policy
- Model ManagedClusterAgentPoolProfile has a new parameter node_taints
- Model ManagedClusterAgentPoolProfile has a new parameter scale_set_priority
- Model AgentPool has a new parameter enable_node_public_ip
- Model AgentPool has a new parameter scale_set_eviction_policy
- Model AgentPool has a new parameter node_taints
- Model AgentPool has a new parameter scale_set_priority
- Model ManagedClusterAgentPoolProfileProperties has a new parameter enable_node_public_ip
- Model ManagedClusterAgentPoolProfileProperties has a new parameter scale_set_eviction_policy
- Model ManagedClusterAgentPoolProfileProperties has a new parameter node_taints
- Model ManagedClusterAgentPoolProfileProperties has a new parameter scale_set_priority
- Added operation AgentPoolsOperations.get_available_agent_pool_versions
- Added operation AgentPoolsOperations.get_upgrade_profile

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes if you were importing from the v20xx_yy_zz API folders.
In summary, some modules were incorrectly visible/importable and have been renamed. This fixed several issues caused by usage of classes that were not supposed to be used in the first place.

- ContainerServiceManagementClient cannot be imported from `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client` anymore (import from `azure.mgmt.containerservice.v20xx_yy_zz` works like before)
- ContainerServiceManagementClientConfiguration import has been moved from `azure.mgmt.containerservice.v20xx_yy_zz.container_service_management_client` to `azure.mgmt.containerservice.v20xx_yy_zz`
- A model `MyClass` from a "models" sub-module cannot be imported anymore using `azure.mgmt.containerservice.v20xx_yy_zz.models.my_class` (import from `azure.mgmt.containerservice.v20xx_yy_zz.models` works like before)
- An operation class `MyClassOperations` from an `operations` sub-module cannot be imported anymore using `azure.mgmt.containerservice.v20xx_yy_zz.operations.my_class_operations` (import from `azure.mgmt.containerservice.v20xx_yy_zz.operations` works like before)

Last but not least, HTTP connection pooling is now enabled by default. You should always use a client as a context manager, or call close(), or use no more than one client per process.


5.3.0 (2019-05-03)
++++++++++++++++++

**Features**

- Model OrchestratorProfile has a new parameter is_preview
- Model OrchestratorVersionProfile has a new parameter is_preview
- Model ContainerServiceNetworkProfile has a new parameter load_balancer_sku
- Model ManagedCluster has a new parameter identity
- Model ManagedCluster has a new parameter max_agent_pools
- Model ManagedCluster has a new parameter windows_profile


5.2.0 (2019-04-30)
++++++++++++++++++

**Features**

- OpenShift is now using a GA api version
- Model OpenShiftManagedCluster has a new parameter cluster_version
- Model NetworkProfile has a new parameter vnet_id

5.1.0 (2019-04-08)
++++++++++++++++++

**Features**

- Model OpenShiftManagedClusterAADIdentityProvider has a new parameter customer_admin_group_id

5.0.0 (2019-03-19)
++++++++++++++++++

**Features**

- Model ManagedClusterAgentPoolProfile has a new parameter min_count
- Model ManagedClusterAgentPoolProfile has a new parameter availability_zones
- Model ManagedClusterAgentPoolProfile has a new parameter type
- Model ManagedClusterAgentPoolProfile has a new parameter enable_auto_scaling
- Model ManagedClusterAgentPoolProfile has a new parameter max_count
- Model ManagedClusterAgentPoolProfile has a new parameter provisioning_state
- Model ManagedClusterAgentPoolProfile has a new parameter orchestrator_version
- Model ManagedCluster has a new parameter api_server_authorized_ip_ranges
- Model ManagedCluster has a new parameter enable_pod_security_policy
- Added operation group AgentPoolsOperations

**Breaking changes**

- Parameter count of model ManagedClusterAgentPoolProfile is now required
- Model ManagedClusterAgentPoolProfile no longer has parameter storage_profile

4.4.0 (2019-01-09)
++++++++++++++++++

**Features**

- Added operation ManagedClustersOperations.reset_service_principal_profile
- Added operation ManagedClustersOperations.reset_aad_profile

4.3.0 (2018-12-13)
++++++++++++++++++

**Features**

- Support for Azure Profiles
- OpenShift ManagedCluster (preview)

This package also adds
Preview version of ManagedCluster (AKS 2018-08-01-preview), this includes the following breaking changes and features, if you optin for this new API version:

**Features**

- Model ManagedClusterAgentPoolProfile has a new parameter type
- Model ManagedClusterAgentPoolProfile has a new parameter max_count
- Model ManagedClusterAgentPoolProfile has a new parameter enable_auto_scaling
- Model ManagedClusterAgentPoolProfile has a new parameter min_count

**Breaking changes**

- Parameter count of model ManagedClusterAgentPoolProfile is now required
- Model ManagedClusterAgentPoolProfile no longer has parameter storage_profile

**Note**

- azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

4.2.2 (2018-08-09)
++++++++++++++++++

**Bugfixes**

- Fix invalid definition of CredentialResult

4.2.1 (2018-08-08)
++++++++++++++++++

**Bugfixes**

- Fix some invalid regexp
- Fix invalid definition of CredentialResult

4.2.0 (2018-07-30)
++++++++++++++++++

**Features**

- Add managed_clusters.list_cluster_admin_credentials
- Add managed_clusters.list_cluster_user_credentials
- Add managed_clusters.update_tags

**Bugfixes**

- Fix incorrect JSON description of ManagedCluster class

4.1.0 (2018-06-13)
++++++++++++++++++

**Features**

- Add node_resource_group attribute to some models

4.0.0 (2018-05-25)
++++++++++++++++++

**Features**

- Added operation ManagedClustersOperations.get_access_profile
- Updated VM sizes
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

3.0.1 (2018-01-25)
++++++++++++++++++

**Bugfixes**

* Fix incorrect mapping in OrchestratorVersionProfileListResult

3.0.0 (2017-12-13)
++++++++++++++++++

* Flattened ManagedCluster so there is no separate properties object
* Added get_access_profiles operation to managed clusters

2.0.0 (2017-10-XX)
++++++++++++++++++

**Features**

* Managed clusters

**Breaking changes**

* VM is now require for master profile (recommended default: standard_d2_v2)

1.0.0 (2017-08-08)
++++++++++++++++++

* Initial Release extracted from azure-mgmt-compute 2.1.0
