# Release History

## 2.1.0b1 (2025-04-21)

### Features Added

  - Model `Cluster` added property `analytics_output_settings`
  - Model `Cluster` added property `secret_archive_settings`
  - Model `Cluster` added property `vulnerability_scanning_settings`
  - Model `ClusterPatchParameters` added property `analytics_output_settings`
  - Model `ClusterPatchParameters` added property `secret_archive_settings`
  - Model `ClusterPatchParameters` added property `vulnerability_scanning_settings`
  - Enum `OsDiskCreateOption` added member `PERSISTENT`
  - Enum `StorageApplianceDetailedStatus` added member `DEGRADED`
  - Model `VirtualMachine` added property `console_extended_location`
  - Enum `VirtualMachineDeviceModelType` added member `T3`
  - Added model `AnalyticsOutputSettings`
  - Added model `SecretArchiveSettings`
  - Added model `VulnerabilityScanningSettings`
  - Added enum `VulnerabilityScanningSettingsContainerScan`
  - Added model `VulnerabilityScanningSettingsPatch`

## 2.0.0 (2025-02-24)

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
  - Operation group `ClustersOperations` added method `begin_continue_update_version`
  - Operation group `ClustersOperations` added method `begin_scan_runtime`
  - Added operation group `KubernetesClusterFeaturesOperations`

### Breaking Changes

  - Parameter `max_surge` of method `AgentPoolUpgradeSettings` is now optional

## 2.0.0b1 (2024-11-21)

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
  - Operation group `ClustersOperations` added method `begin_continue_update_version`
  - Operation group `ClustersOperations` added method `begin_scan_runtime`
  - Added operation group `KubernetesClusterFeaturesOperations`

### Breaking Changes

  - Parameter `max_surge` of model `AgentPoolUpgradeSettings` is no longer required

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
