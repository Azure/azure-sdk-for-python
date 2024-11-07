# Release History

## 2.0.0b1 (2024-11-18)

### Features Added

  - Client `NetworkCloudMgmtClient` added operation group `kubernetes_cluster_features`
  - Model `AgentPoolPatchParameters` added property `administrator_configuration`
  - Model `AgentPoolUpgradeSettings` added property `drain_timeout`
  - Model `AgentPoolUpgradeSettings` added property `max_unavailable`
  - Model `BareMetalMachine` added property `machine_cluster_version`
  - Model `BareMetalMachine` added property `machine_roles`
  - Model `BareMetalMachine` added property `runtime_protection_status`
  - Model `BareMetalMachine` added property `secret_rotation_status`
  - Model `Cluster` added property `identity`
  - Model `Cluster` added property `command_output_settings`
  - Model `Cluster` added property `runtime_protection_configuration`
  - Model `Cluster` added property `secret_archive`
  - Model `Cluster` added property `update_strategy`
  - Enum `ClusterConnectionStatus` added member `DISCONNECTED`
  - Enum `ClusterDetailedStatus` added member `UPDATE_PAUSED`
  - Model `ClusterManager` added property `identity`
  - Model `ClusterManagerPatchParameters` added property `identity`
  - Model `ClusterPatchParameters` added property `identity`
  - Model `ClusterPatchParameters` added property `command_output_settings`
  - Model `ClusterPatchParameters` added property `runtime_protection_configuration`
  - Model `ClusterPatchParameters` added property `secret_archive`
  - Model `ClusterPatchParameters` added property `update_strategy`
  - Model `ControlPlaneNodePatchConfiguration` added property `administrator_configuration`
  - Model `KeySetUser` added property `user_principal_name`
  - Model `KubernetesClusterPatchParameters` added property `administrator_configuration`
  - Model `NetworkConfiguration` added property `l2_service_load_balancer_configuration`
  - Model `OperationStatusResult` added property `exit_code`
  - Model `OperationStatusResult` added property `output_head`
  - Model `OperationStatusResult` added property `result_ref`
  - Model `OperationStatusResult` added property `result_url`
  - Enum `RackSkuProvisioningState` added member `CANCELED`
  - Enum `RackSkuProvisioningState` added member `FAILED`
  - Model `StorageAppliance` added property `manufacturer`
  - Model `StorageAppliance` added property `model`
  - Model `StorageAppliance` added property `secret_rotation_status`
  - Model `StorageAppliance` added property `version`
  - Added model `AdministratorConfigurationPatch`
  - Added enum `ClusterContinueUpdateVersionMachineGroupTargetingMode`
  - Added model `ClusterContinueUpdateVersionParameters`
  - Added model `ClusterScanRuntimeParameters`
  - Added enum `ClusterScanRuntimeParametersScanActivity`
  - Added model `ClusterSecretArchive`
  - Added enum `ClusterSecretArchiveEnabled`
  - Added model `ClusterUpdateStrategy`
  - Added enum `ClusterUpdateStrategyType`
  - Added model `CommandOutputSettings`
  - Added model `IdentitySelector`
  - Added model `KubernetesClusterFeature`
  - Added enum `KubernetesClusterFeatureAvailabilityLifecycle`
  - Added enum `KubernetesClusterFeatureDetailedStatus`
  - Added model `KubernetesClusterFeatureList`
  - Added model `KubernetesClusterFeaturePatchParameters`
  - Added enum `KubernetesClusterFeatureProvisioningState`
  - Added enum `KubernetesClusterFeatureRequired`
  - Added model `L2ServiceLoadBalancerConfiguration`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentitySelectorType`
  - Added enum `ManagedServiceIdentityType`
  - Added model `NodePoolAdministratorConfigurationPatch`
  - Added model `RuntimeProtectionConfiguration`
  - Added enum `RuntimeProtectionEnforcementLevel`
  - Added model `RuntimeProtectionStatus`
  - Added model `SecretArchiveReference`
  - Added model `SecretRotationStatus`
  - Added model `StringKeyValuePair`
  - Added model `UserAssignedIdentity`
  - Model `ClustersOperations` added method `begin_continue_update_version`
  - Model `ClustersOperations` added method `begin_scan_runtime`
  - Added model `KubernetesClusterFeaturesOperations`
  - Method `AgentPoolsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, agent_pool_name: str, agent_pool_parameters: IO[bytes], content_type: str)`
  - Method `AgentPoolsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, agent_pool_name: str, agent_pool_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BareMetalMachineKeySetsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cluster_name: str, bare_metal_machine_key_set_name: str, bare_metal_machine_key_set_parameters: IO[bytes], content_type: str)`
  - Method `BareMetalMachineKeySetsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, cluster_name: str, bare_metal_machine_key_set_name: str, bare_metal_machine_key_set_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_cordon` has a new overload `def begin_cordon(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_cordon_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_parameters: IO[bytes], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_power_off` has a new overload `def begin_power_off(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_power_off_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_replace` has a new overload `def begin_replace(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_replace_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_run_command` has a new overload `def begin_run_command(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_run_command_parameters: IO[bytes], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_run_data_extracts` has a new overload `def begin_run_data_extracts(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_run_data_extracts_parameters: IO[bytes], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_run_read_commands` has a new overload `def begin_run_read_commands(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_run_read_commands_parameters: IO[bytes], content_type: str)`
  - Method `BareMetalMachinesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, bare_metal_machine_name: str, bare_metal_machine_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `BmcKeySetsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cluster_name: str, bmc_key_set_name: str, bmc_key_set_parameters: IO[bytes], content_type: str)`
  - Method `BmcKeySetsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, cluster_name: str, bmc_key_set_name: str, bmc_key_set_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `CloudServicesNetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cloud_services_network_name: str, cloud_services_network_parameters: IO[bytes], content_type: str)`
  - Method `CloudServicesNetworksOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, cloud_services_network_name: str, cloud_services_network_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `ClusterManagersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cluster_manager_name: str, cluster_manager_parameters: IO[bytes], content_type: str)`
  - Method `ClusterManagersOperations.update` has a new overload `def update(self: None, resource_group_name: str, cluster_manager_name: str, cluster_manager_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `ClustersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cluster_name: str, cluster_parameters: IO[bytes], content_type: str)`
  - Method `ClustersOperations.begin_deploy` has a new overload `def begin_deploy(self: None, resource_group_name: str, cluster_name: str, cluster_deploy_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `ClustersOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, cluster_name: str, cluster_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `ClustersOperations.begin_update_version` has a new overload `def begin_update_version(self: None, resource_group_name: str, cluster_name: str, cluster_update_version_parameters: IO[bytes], content_type: str)`
  - Method `ClustersOperations.begin_continue_update_version` has a new overload `def begin_continue_update_version(self: None, resource_group_name: str, cluster_name: str, cluster_continue_update_version_parameters: ClusterContinueUpdateVersionParameters, content_type: str)`
  - Method `ClustersOperations.begin_continue_update_version` has a new overload `def begin_continue_update_version(self: None, resource_group_name: str, cluster_name: str, cluster_continue_update_version_parameters: IO[bytes], content_type: str)`
  - Method `ClustersOperations.begin_scan_runtime` has a new overload `def begin_scan_runtime(self: None, resource_group_name: str, cluster_name: str, cluster_scan_runtime_parameters: Optional[ClusterScanRuntimeParameters], content_type: str)`
  - Method `ClustersOperations.begin_scan_runtime` has a new overload `def begin_scan_runtime(self: None, resource_group_name: str, cluster_name: str, cluster_scan_runtime_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `ConsolesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_machine_name: str, console_name: str, console_parameters: IO[bytes], content_type: str)`
  - Method `ConsolesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, virtual_machine_name: str, console_name: str, console_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `KubernetesClustersOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, kubernetes_cluster_parameters: IO[bytes], content_type: str)`
  - Method `KubernetesClustersOperations.begin_restart_node` has a new overload `def begin_restart_node(self: None, resource_group_name: str, kubernetes_cluster_name: str, kubernetes_cluster_restart_node_parameters: IO[bytes], content_type: str)`
  - Method `KubernetesClustersOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, kubernetes_cluster_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `L2NetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, l2_network_name: str, l2_network_parameters: IO[bytes], content_type: str)`
  - Method `L2NetworksOperations.update` has a new overload `def update(self: None, resource_group_name: str, l2_network_name: str, l2_network_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `L3NetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, l3_network_name: str, l3_network_parameters: IO[bytes], content_type: str)`
  - Method `L3NetworksOperations.update` has a new overload `def update(self: None, resource_group_name: str, l3_network_name: str, l3_network_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `MetricsConfigurationsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, cluster_name: str, metrics_configuration_name: str, metrics_configuration_parameters: IO[bytes], content_type: str)`
  - Method `MetricsConfigurationsOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, cluster_name: str, metrics_configuration_name: str, metrics_configuration_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `RacksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, rack_name: str, rack_parameters: IO[bytes], content_type: str)`
  - Method `RacksOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, rack_name: str, rack_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `StorageAppliancesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, storage_appliance_name: str, storage_appliance_parameters: IO[bytes], content_type: str)`
  - Method `StorageAppliancesOperations.begin_enable_remote_vendor_management` has a new overload `def begin_enable_remote_vendor_management(self: None, resource_group_name: str, storage_appliance_name: str, storage_appliance_enable_remote_vendor_management_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `StorageAppliancesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, storage_appliance_name: str, storage_appliance_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `TrunkedNetworksOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, trunked_network_name: str, trunked_network_parameters: IO[bytes], content_type: str)`
  - Method `TrunkedNetworksOperations.update` has a new overload `def update(self: None, resource_group_name: str, trunked_network_name: str, trunked_network_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VirtualMachinesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, virtual_machine_name: str, virtual_machine_parameters: IO[bytes], content_type: str)`
  - Method `VirtualMachinesOperations.begin_power_off` has a new overload `def begin_power_off(self: None, resource_group_name: str, virtual_machine_name: str, virtual_machine_power_off_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VirtualMachinesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, virtual_machine_name: str, virtual_machine_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `VolumesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, volume_name: str, volume_parameters: IO[bytes], content_type: str)`
  - Method `VolumesOperations.update` has a new overload `def update(self: None, resource_group_name: str, volume_name: str, volume_update_parameters: Optional[IO[bytes]], content_type: str)`
  - Method `KubernetesClusterFeaturesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, feature_name: str, kubernetes_cluster_feature_parameters: KubernetesClusterFeature, content_type: str)`
  - Method `KubernetesClusterFeaturesOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, feature_name: str, kubernetes_cluster_feature_parameters: IO[bytes], content_type: str)`
  - Method `KubernetesClusterFeaturesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, feature_name: str, kubernetes_cluster_feature_update_parameters: Optional[KubernetesClusterFeaturePatchParameters], content_type: str)`
  - Method `KubernetesClusterFeaturesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, kubernetes_cluster_name: str, feature_name: str, kubernetes_cluster_feature_update_parameters: Optional[IO[bytes]], content_type: str)`

### Breaking Changes

  - Method `AgentPoolUpgradeSettings.__init__` parameter `max_surge` changed default value from `str` to `none`

## 1.0.0 (2023-08-18)

### Breaking Changes

  - Removed operation BareMetalMachinesOperations.begin_validate_hardware
  - Removed operation StorageAppliancesOperations.begin_run_read_commands
  - Removed operation VirtualMachinesOperations.begin_attach_volume
  - Removed operation VirtualMachinesOperations.begin_detach_volume

## 1.0.0b2 (2023-07-19)

### Features Added

  - Added operation BareMetalMachineKeySetsOperations.list_by_cluster
  - Added operation BmcKeySetsOperations.list_by_cluster
  - Added operation ConsolesOperations.list_by_virtual_machine
  - Added operation MetricsConfigurationsOperations.list_by_cluster
  - Added operation group AgentPoolsOperations
  - Added operation group KubernetesClustersOperations
  - Model BareMetalMachine has a new parameter associated_resource_ids
  - Model CloudServicesNetwork has a new parameter associated_resource_ids
  - Model L2Network has a new parameter associated_resource_ids
  - Model L3Network has a new parameter associated_resource_ids
  - Model TrunkedNetwork has a new parameter associated_resource_ids
  - Model VirtualMachine has a new parameter availability_zone

### Breaking Changes

  - Removed operation BareMetalMachineKeySetsOperations.list_by_resource_group
  - Removed operation BmcKeySetsOperations.list_by_resource_group
  - Removed operation ConsolesOperations.list_by_resource_group
  - Removed operation MetricsConfigurationsOperations.list_by_resource_group
  - Removed operation StorageAppliancesOperations.begin_validate_hardware
  - Removed operation group DefaultCniNetworksOperations
  - Removed operation group HybridAksClustersOperations

## 1.0.0b1 (2023-05-19)

* Initial Release
