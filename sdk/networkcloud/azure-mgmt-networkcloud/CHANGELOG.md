# Release History

## 3.0.0b1 (2026-04-02)

### Features Added

  - Client `NetworkCloudMgmtClient` added method `send_request`
  - Added enum `ExtendedLocationType`
  - Added model `ProxyResource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AgentPoolPatchParameters` moved instance variable `administrator_configuration`, `count` and `upgrade_settings` under property `properties` whose type is `AgentPoolPatchProperties`
  - Model `BareMetalMachineKeySetPatchParameters` moved instance variable `expiration`, `jump_hosts_allowed` and `user_list` under property `properties` whose type is `BareMetalMachineKeySetPatchProperties`
  - Model `BareMetalMachinePatchParameters` moved instance variable `machine_details` under property `properties` whose type is `BareMetalMachinePatchProperties`
  - Model `BmcKeySetPatchParameters` moved instance variable `expiration` and `user_list` under property `properties` whose type is `BmcKeySetPatchProperties`
  - Model `CloudServicesNetworkPatchParameters` moved instance variable `additional_egress_endpoints`, `enable_default_egress_endpoints` and `storage_options` under property `properties` whose type is `CloudServicesNetworkPatchProperties`
  - Model `ClusterMetricsConfigurationPatchParameters` moved instance variable `collection_interval` and `enabled_metrics` under property `properties` whose type is `ClusterMetricsConfigurationPatchProperties`
  - Model `ClusterPatchParameters` moved instance variable `aggregator_or_single_rack_definition`, `analytics_output_settings`, `cluster_location`, `cluster_service_principal`, `command_output_settings`, `compute_deployment_threshold`, `compute_rack_definitions`, `runtime_protection_configuration`, `secret_archive`, `secret_archive_settings`, `update_strategy` and `vulnerability_scanning_settings` under property `properties` whose type is `ClusterPatchProperties`
  - Model `ConsolePatchParameters` moved instance variable `enabled`, `expiration` and `ssh_public_key` under property `properties` whose type is `ConsolePatchProperties`
  - Model `KubernetesClusterFeaturePatchParameters` moved instance variable `options` under property `properties` whose type is `KubernetesClusterFeaturePatchProperties`
  - Model `KubernetesClusterPatchParameters` moved instance variable `administrator_configuration`, `control_plane_node_configuration` and `kubernetes_version` under property `properties` whose type is `KubernetesClusterPatchProperties`
  - Model `MachineSkuSlot` moved instance variable `bootstrap_protocol`, `cpu_cores`, `cpu_sockets`, `disks`, `generation`, `hardware_version`, `memory_capacity_gb`, `model`, `network_interfaces`, `total_threads` and `vendor` under property `properties` whose type is `MachineSkuProperties`
  - Model `RackPatchParameters` moved instance variable `rack_location` and `rack_serial_number` under property `properties` whose type is `RacksPatchProperties`
  - Model `StorageAppliancePatchParameters` moved instance variable `serial_number` under property `properties` whose type is `StorageAppliancePatchProperties`
  - Model `StorageApplianceSkuSlot` moved instance variable `capacity_gb` and `model` under property `properties` whose type is `StorageApplianceSkuProperties`
  - Model `VirtualMachinePatchParameters` moved instance variable `vm_image_repository_credentials` under property `properties` whose type is `VirtualMachinePatchProperties`
  - Deleted or renamed model `AgentPoolConfiguration`
  - Deleted or renamed model `TagsParameter`
  - Method `AgentPoolsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `AgentPoolsOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `AgentPoolsOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `AgentPoolsOperations.list_by_kubernetes_cluster` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `BareMetalMachineKeySetsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachineKeySetsOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachineKeySetsOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachineKeySetsOperations.list_by_cluster` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `BareMetalMachinesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachinesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachinesOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BareMetalMachinesOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `BareMetalMachinesOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `BmcKeySetsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BmcKeySetsOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BmcKeySetsOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `BmcKeySetsOperations.list_by_cluster` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `CloudServicesNetworksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `CloudServicesNetworksOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `CloudServicesNetworksOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `CloudServicesNetworksOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `CloudServicesNetworksOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `ClusterManagersOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClusterManagersOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClusterManagersOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `ClusterManagersOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `ClusterManagersOperations.update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClustersOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClustersOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClustersOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ClustersOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `ClustersOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `ConsolesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ConsolesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ConsolesOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `ConsolesOperations.list_by_virtual_machine` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `KubernetesClusterFeaturesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClusterFeaturesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClusterFeaturesOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClusterFeaturesOperations.list_by_kubernetes_cluster` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `KubernetesClustersOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClustersOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClustersOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `KubernetesClustersOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `KubernetesClustersOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `L2NetworksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `L2NetworksOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `L2NetworksOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `L2NetworksOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `L2NetworksOperations.update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `L3NetworksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `L3NetworksOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `L3NetworksOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `L3NetworksOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `L3NetworksOperations.update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `MetricsConfigurationsOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `MetricsConfigurationsOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `MetricsConfigurationsOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `MetricsConfigurationsOperations.list_by_cluster` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `RacksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `RacksOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `RacksOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `RacksOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `RacksOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `StorageAppliancesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `StorageAppliancesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `StorageAppliancesOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `StorageAppliancesOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `StorageAppliancesOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `TrunkedNetworksOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `TrunkedNetworksOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `TrunkedNetworksOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `TrunkedNetworksOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `TrunkedNetworksOperations.update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualMachinesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualMachinesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualMachinesOperations.begin_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VirtualMachinesOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `VirtualMachinesOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `VolumesOperations.begin_create_or_update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VolumesOperations.begin_delete` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `VolumesOperations.list_by_resource_group` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `VolumesOperations.list_by_subscription` changed its parameter `skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `VolumesOperations.update` replaced positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`

### Other Changes

  - Deleted model `AgentPoolList`/`BareMetalMachineKeySetList`/`BareMetalMachineList`/`BmcKeySetList`/`CloudServicesNetworkList`/`ClusterList`/`ClusterManagerList`/`ClusterMetricsConfigurationList`/`ConsoleList`/`KubernetesClusterFeatureList`/`KubernetesClusterList`/`L2NetworkList`/`L3NetworkList`/`RackList`/`RackSkuList`/`StorageApplianceList`/`TrunkedNetworkList`/`VirtualMachineList`/`VolumeList` which actually were not used by SDK users

## 2.2.0 (2025-12-22)

### Features Added

  - Model `NetworkCloudMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `BareMetalMachine` added property `action_states`
  - Model `BareMetalMachine` added property `ca_certificate`
  - Model `BareMetalMachineKeySet` added property `privilege_level_name`
  - Enum `BareMetalMachineKeySetPrivilegeLevel` added member `OTHER`
  - Model `BareMetalMachineReplaceParameters` added property `safeguard_mode`
  - Model `BareMetalMachineReplaceParameters` added property `storage_policy`
  - Model `CloudServicesNetwork` added property `storage_options`
  - Model `CloudServicesNetwork` added property `storage_status`
  - Model `CloudServicesNetworkPatchParameters` added property `storage_options`
  - Model `Cluster` added property `action_states`
  - Model `CommandOutputSettings` added property `overrides`
  - Model `SecretArchiveReference` added property `key_vault_uri`
  - Model `StorageAppliance` added property `ca_certificate`
  - Model `VirtualMachine` added property `identity`
  - Model `VirtualMachine` added property `network_data_content`
  - Model `VirtualMachine` added property `user_data_content`
  - Model `VirtualMachinePatchParameters` added property `identity`
  - Model `Volume` added property `allocated_size_mi_b`
  - Model `Volume` added property `storage_appliance_id`
  - Added model `ActionState`
  - Added enum `ActionStateStatus`
  - Added enum `BareMetalMachineReplaceSafeguardMode`
  - Added enum `BareMetalMachineReplaceStoragePolicy`
  - Added model `CertificateInfo`
  - Added enum `CloudServicesNetworkStorageMode`
  - Added model `CloudServicesNetworkStorageOptions`
  - Added model `CloudServicesNetworkStorageOptionsPatch`
  - Added model `CloudServicesNetworkStorageStatus`
  - Added enum `CloudServicesNetworkStorageStatusStatus`
  - Added model `CommandOutputOverride`
  - Added enum `CommandOutputType`
  - Added enum `RelayType`
  - Added model `StepState`
  - Added enum `StepStateStatus`
  - Added model `StorageApplianceCommandSpecification`
  - Added model `StorageApplianceRunReadCommandsParameters`
  - Added model `VirtualMachineAssignRelayParameters`
  - Operation group `BareMetalMachinesOperations` added method `begin_run_data_extracts_restricted`
  - Operation group `StorageAppliancesOperations` added method `begin_run_read_commands`
  - Operation group `VirtualMachinesOperations` added method `begin_assign_relay`

## 2.2.0b1 (2025-11-17)

### Features Added

  - Model `NetworkCloudMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Model `BareMetalMachine` added property `action_states`
  - Model `BareMetalMachine` added property `ca_certificate`
  - Model `BareMetalMachineKeySet` added property `privilege_level_name`
  - Enum `BareMetalMachineKeySetPrivilegeLevel` added member `OTHER`
  - Model `BareMetalMachineReplaceParameters` added property `safeguard_mode`
  - Model `BareMetalMachineReplaceParameters` added property `storage_policy`
  - Model `CloudServicesNetwork` added property `storage_options`
  - Model `CloudServicesNetwork` added property `storage_status`
  - Model `CloudServicesNetworkPatchParameters` added property `storage_options`
  - Model `Cluster` added property `action_states`
  - Model `CommandOutputSettings` added property `overrides`
  - Model `SecretArchiveReference` added property `key_vault_uri`
  - Model `StorageAppliance` added property `ca_certificate`
  - Model `VirtualMachine` added property `identity`
  - Model `VirtualMachine` added property `network_data_content`
  - Model `VirtualMachine` added property `user_data_content`
  - Model `VirtualMachinePatchParameters` added property `identity`
  - Model `Volume` added property `allocated_size_mi_b`
  - Model `Volume` added property `storage_appliance_id`
  - Added model `ActionState`
  - Added enum `ActionStateStatus`
  - Added enum `BareMetalMachineReplaceSafeguardMode`
  - Added enum `BareMetalMachineReplaceStoragePolicy`
  - Added model `CertificateInfo`
  - Added enum `CloudServicesNetworkStorageMode`
  - Added model `CloudServicesNetworkStorageOptions`
  - Added model `CloudServicesNetworkStorageOptionsPatch`
  - Added model `CloudServicesNetworkStorageStatus`
  - Added enum `CloudServicesNetworkStorageStatusStatus`
  - Added model `CommandOutputOverride`
  - Added enum `CommandOutputType`
  - Added enum `RelayType`
  - Added model `StepState`
  - Added enum `StepStateStatus`
  - Added model `StorageApplianceCommandSpecification`
  - Added model `StorageApplianceRunReadCommandsParameters`
  - Added model `VirtualMachineAssignRelayParameters`
  - Operation group `BareMetalMachinesOperations` added method `begin_run_data_extracts_restricted`
  - Operation group `StorageAppliancesOperations` added method `begin_run_read_commands`
  - Operation group `VirtualMachinesOperations` added method `begin_assign_relay`

## 2.1.0 (2025-06-16)

### Features Added

  - All resources implement concurrency control via Etag/If-Match/If-None-Match parameters. As a result, customers who use create/patch/delete methods with positional arguments may need to adjust part of calls. It is recommended to switch to keyword based calls to avoid any future issues.
  - Model `AgentPool` added property `etag`
  - Model `BareMetalMachine` added property `etag`
  - Model `BareMetalMachineKeySet` added property `etag`
  - Model `BmcKeySet` added property `etag`
  - Model `CloudServicesNetwork` added property `etag`
  - Model `Cluster` added property `etag`
  - Model `Cluster` added property `analytics_output_settings`
  - Model `Cluster` added property `secret_archive_settings`
  - Model `Cluster` added property `vulnerability_scanning_settings`
  - Model `ClusterManager` added property `etag`
  - Model `ClusterMetricsConfiguration` added property `etag`
  - Model `ClusterPatchParameters` added property `analytics_output_settings`
  - Model `ClusterPatchParameters` added property `secret_archive_settings`
  - Model `ClusterPatchParameters` added property `vulnerability_scanning_settings`
  - Model `Console` added property `etag`
  - Model `KubernetesCluster` added property `etag`
  - Model `KubernetesClusterFeature` added property `etag`
  - Model `L2Network` added property `etag`
  - Model `L3Network` added property `etag`
  - Enum `OsDiskCreateOption` added member `PERSISTENT`
  - Model `Rack` added property `etag`
  - Model `StorageAppliance` added property `etag`
  - Enum `StorageApplianceDetailedStatus` added member `DEGRADED`
  - Model `TrunkedNetwork` added property `etag`
  - Model `VirtualMachine` added property `etag`
  - Model `VirtualMachine` added property `console_extended_location`
  - Enum `VirtualMachineDeviceModelType` added member `T3`
  - Model `Volume` added property `etag`
  - Added model `AnalyticsOutputSettings`
  - Added model `SecretArchiveSettings`
  - Added model `VulnerabilityScanningSettings`
  - Added enum `VulnerabilityScanningSettingsContainerScan`
  - Added model `VulnerabilityScanningSettingsPatch`

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
