# Release History

## 1.0.0b2 (2023-11-20)

### Features Added

  - Added operation group HybridContainerServiceMgmtClientOperationsMixin
  - Added operation group KubernetesVersionsOperations
  - Added operation group ProvisionedClusterInstancesOperations
  - Added operation group VMSkusOperations
  - Model AgentPool has a new parameter os_sku
  - Model AgentPoolProfile has a new parameter os_sku
  - Model AgentPoolProperties has a new parameter os_sku
  - Model AgentPoolProvisioningStatusStatus has a new parameter operation_status
  - Model ControlPlaneProfile has a new parameter os_sku
  - Model NamedAgentPoolProfile has a new parameter os_sku
  - Model ProvisionedClusterUpgradeProfile has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model AgentPool no longer has parameter cloud_provider_profile
  - Model AgentPool no longer has parameter max_count
  - Model AgentPool no longer has parameter max_pods
  - Model AgentPool no longer has parameter min_count
  - Model AgentPool no longer has parameter mode
  - Model AgentPool no longer has parameter node_labels
  - Model AgentPool no longer has parameter node_taints
  - Model AgentPoolProfile no longer has parameter cloud_provider_profile
  - Model AgentPoolProfile no longer has parameter count
  - Model AgentPoolProfile no longer has parameter max_count
  - Model AgentPoolProfile no longer has parameter max_pods
  - Model AgentPoolProfile no longer has parameter min_count
  - Model AgentPoolProfile no longer has parameter mode
  - Model AgentPoolProfile no longer has parameter node_labels
  - Model AgentPoolProfile no longer has parameter node_taints
  - Model AgentPoolProfile no longer has parameter vm_size
  - Model AgentPoolProperties no longer has parameter cloud_provider_profile
  - Model AgentPoolProperties no longer has parameter max_count
  - Model AgentPoolProperties no longer has parameter max_pods
  - Model AgentPoolProperties no longer has parameter min_count
  - Model AgentPoolProperties no longer has parameter mode
  - Model AgentPoolProperties no longer has parameter node_labels
  - Model AgentPoolProperties no longer has parameter node_taints
  - Model AgentPoolProvisioningStatusStatus no longer has parameter provisioning_status
  - Model AgentPoolProvisioningStatusStatus no longer has parameter replicas
  - Model CloudProviderProfile no longer has parameter infra_storage_profile
  - Model ControlPlaneProfile no longer has parameter cloud_provider_profile
  - Model ControlPlaneProfile no longer has parameter max_count
  - Model ControlPlaneProfile no longer has parameter max_pods
  - Model ControlPlaneProfile no longer has parameter min_count
  - Model ControlPlaneProfile no longer has parameter mode
  - Model ControlPlaneProfile no longer has parameter node_labels
  - Model ControlPlaneProfile no longer has parameter node_taints
  - Model HybridIdentityMetadata no longer has parameter identity
  - Model LinuxProfileProperties no longer has parameter admin_username
  - Model NamedAgentPoolProfile no longer has parameter cloud_provider_profile
  - Model NamedAgentPoolProfile no longer has parameter max_count
  - Model NamedAgentPoolProfile no longer has parameter max_pods
  - Model NamedAgentPoolProfile no longer has parameter min_count
  - Model NamedAgentPoolProfile no longer has parameter mode
  - Model NamedAgentPoolProfile no longer has parameter node_labels
  - Model NamedAgentPoolProfile no longer has parameter node_taints
  - Model NetworkProfile no longer has parameter dns_service_ip
  - Model NetworkProfile no longer has parameter load_balancer_sku
  - Model NetworkProfile no longer has parameter pod_cidrs
  - Model NetworkProfile no longer has parameter service_cidr
  - Model NetworkProfile no longer has parameter service_cidrs
  - Model ProvisionedClusters no longer has parameter identity
  - Model ProvisionedClusters no longer has parameter location
  - Model ProvisionedClusters no longer has parameter tags
  - Operation AgentPoolOperations.begin_create_or_update has a new required parameter connected_cluster_resource_uri
  - Operation AgentPoolOperations.begin_create_or_update no longer has parameter resource_group_name
  - Operation AgentPoolOperations.begin_create_or_update no longer has parameter resource_name
  - Operation AgentPoolOperations.get has a new required parameter connected_cluster_resource_uri
  - Operation AgentPoolOperations.get no longer has parameter resource_group_name
  - Operation AgentPoolOperations.get no longer has parameter resource_name
  - Operation AgentPoolOperations.list_by_provisioned_cluster has a new required parameter connected_cluster_resource_uri
  - Operation AgentPoolOperations.list_by_provisioned_cluster no longer has parameter resource_group_name
  - Operation AgentPoolOperations.list_by_provisioned_cluster no longer has parameter resource_name
  - Operation HybridIdentityMetadataOperations.get has a new required parameter connected_cluster_resource_uri
  - Operation HybridIdentityMetadataOperations.get no longer has parameter hybrid_identity_metadata_resource_name
  - Operation HybridIdentityMetadataOperations.get no longer has parameter resource_group_name
  - Operation HybridIdentityMetadataOperations.get no longer has parameter resource_name
  - Operation HybridIdentityMetadataOperations.list_by_cluster has a new required parameter connected_cluster_resource_uri
  - Operation HybridIdentityMetadataOperations.list_by_cluster no longer has parameter resource_group_name
  - Operation HybridIdentityMetadataOperations.list_by_cluster no longer has parameter resource_name
  - Operation HybridIdentityMetadataOperations.put has a new required parameter connected_cluster_resource_uri
  - Operation HybridIdentityMetadataOperations.put no longer has parameter hybrid_identity_metadata_resource_name
  - Operation HybridIdentityMetadataOperations.put no longer has parameter resource_group_name
  - Operation HybridIdentityMetadataOperations.put no longer has parameter resource_name
  - Operation VirtualNetworksOperations.begin_create_or_update has a new required parameter virtual_network_name
  - Operation VirtualNetworksOperations.begin_create_or_update no longer has parameter virtual_networks_name
  - Operation VirtualNetworksOperations.begin_update has a new required parameter virtual_network_name
  - Operation VirtualNetworksOperations.begin_update no longer has parameter virtual_networks_name
  - Operation VirtualNetworksOperations.retrieve has a new required parameter virtual_network_name
  - Operation VirtualNetworksOperations.retrieve no longer has parameter virtual_networks_name
  - Removed operation group HybridContainerServiceOperations
  - Removed operation group ProvisionedClustersOperations
  - Removed operation group StorageSpacesOperations
  - Renamed operation AgentPoolOperations.delete to AgentPoolOperations.begin_delete
  - Renamed operation AgentPoolOperations.update to AgentPoolOperations.begin_update
  - Renamed operation HybridIdentityMetadataOperations.delete to HybridIdentityMetadataOperations.begin_delete
  - Renamed operation VirtualNetworksOperations.delete to VirtualNetworksOperations.begin_delete

## 1.0.0b1 (2023-03-20)

* Initial Release
