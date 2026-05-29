# Release History

## 8.1.0b1 (2026-04-13)

### Features Added

  - Client `AzureStackHCIClient` added operation group `kubernetes_versions`
  - Client `AzureStackHCIClient` added operation group `platform_updates`
  - Client `AzureStackHCIClient` added operation group `os_images`
  - Client `AzureStackHCIClient` added operation group `update_contents`
  - Client `AzureStackHCIClient` added operation group `publishers`
  - Client `AzureStackHCIClient` added operation group `update_summaries_operation_group`
  - Client `AzureStackHCIClient` added operation group `edge_machines`
  - Client `AzureStackHCIClient` added operation group `edge_machine_jobs`
  - Client `AzureStackHCIClient` added operation group `ownership_vouchers`
  - Client `AzureStackHCIClient` added operation group `cluster_jobs`
  - Client `AzureStackHCIClient` added operation group `device_pools`
  - Model `Cluster` added property `kind`
  - Model `ClusterProperties` added property `ring`
  - Model `ClusterProperties` added property `billing_properties`
  - Model `ClusterProperties` added property `confidential_vm_properties`
  - Model `ClusterProperties` added property `sdn_properties`
  - Model `ClusterProperties` added property `storage_type`
  - Model `DeploymentSettingHostNetwork` added property `san_networks`
  - Model `HciNetworkProfile` added property `sdn_properties`
  - Model `HciReportedProperties` added property `last_sync_timestamp`
  - Model `HciReportedProperties` added property `confidential_vm_profile`
  - Model `HciStorageProfile` added property `disks`
  - Model `PerNodeRemoteSupportSession` added property `transcript_location`
  - Model `RemoteSupportProperties` added property `remote_support_provisioning_state`
  - Model `ReportedProperties` added property `last_sync_timestamp`
  - Model `ReportedProperties` added property `confidential_vm_profile`
  - Enum `State` added member `HEALTH_CHECK_EXPIRED`
  - Enum `State` added member `PENDING_OEM_VALIDATION`
  - Model `Storage` added property `storage_type`
  - Model `Storage` added property `s2_d`
  - Model `Storage` added property `san`
  - Added model `ChangeRingRequest`
  - Added model `ChangeRingRequestProperties`
  - Added model `CheckUpdatesRequest`
  - Added model `ClaimDeviceRequest`
  - Added model `ClusterBillingProperties`
  - Added model `ClusterJob`
  - Added model `ClusterJobProperties`
  - Added model `ClusterSdnProperties`
  - Added enum `ConfidentialVmIntent`
  - Added model `ConfidentialVmProfile`
  - Added model `ConfidentialVmProperties`
  - Added enum `ConfidentialVmStatus`
  - Added model `ContentPayload`
  - Added model `DeviceDetail`
  - Added model `DevicePool`
  - Added model `DevicePoolPatch`
  - Added model `DevicePoolProperties`
  - Added model `DownloadOsJobProperties`
  - Added model `DownloadOsProfile`
  - Added model `DownloadRequest`
  - Added model `EdgeDeviceDisks`
  - Added model `EdgeMachine`
  - Added model `EdgeMachineCollectLogJobProperties`
  - Added model `EdgeMachineCollectLogJobReportedProperties`
  - Added enum `EdgeMachineConnectivityStatus`
  - Added model `EdgeMachineJob`
  - Added model `EdgeMachineJobProperties`
  - Added enum `EdgeMachineJobType`
  - Added enum `EdgeMachineKind`
  - Added model `EdgeMachineNetworkProfile`
  - Added model `EdgeMachineNicDetail`
  - Added model `EdgeMachinePatch`
  - Added model `EdgeMachineProperties`
  - Added model `EdgeMachineRemoteSupportJobProperties`
  - Added model `EdgeMachineRemoteSupportJobReportedProperties`
  - Added model `EdgeMachineRemoteSupportNodeSettings`
  - Added model `EdgeMachineReportedProperties`
  - Added enum `EdgeMachineState`
  - Added model `HardwareProfile`
  - Added model `HciConfigureCvmJobProperties`
  - Added model `HciConfigureSdnIntegrationJobProperties`
  - Added enum `HciJobType`
  - Added enum `IgvmStatus`
  - Added model `IgvmStatusDetail`
  - Added model `IpAddressRange`
  - Added enum `IpAssignmentType`
  - Added model `JobReportedProperties`
  - Added model `KubernetesVersion`
  - Added model `KubernetesVersionProperties`
  - Added model `NetworkAdapter`
  - Added model `NetworkConfiguration`
  - Added model `NextBillingModel`
  - Added enum `OSOperationType`
  - Added model `OnboardingConfiguration`
  - Added enum `OnboardingResourceType`
  - Added model `OperationDetail`
  - Added model `OsImage`
  - Added model `OsImageProperties`
  - Added model `OsProfile`
  - Added model `OsProvisionProfile`
  - Added enum `OverprovisioningRatio`
  - Added enum `OwnerKeyType`
  - Added model `OwnershipVoucherDetails`
  - Added model `OwnershipVoucherValidationDetails`
  - Added enum `OwnershipVoucherValidationStatus`
  - Added model `PlatformPayload`
  - Added model `PlatformUpdate`
  - Added model `PlatformUpdateDetails`
  - Added model `PlatformUpdateProperties`
  - Added model `ProvisionOsJobProperties`
  - Added model `ProvisionOsReportedProperties`
  - Added model `ProvisioningDetails`
  - Added enum `ProvisioningOsType`
  - Added model `ProvisioningRequest`
  - Added model `Publisher`
  - Added model `PublisherProperties`
  - Added model `ReleaseDeviceRequest`
  - Added enum `RemoteSupportProvisioningState`
  - Added model `SanAdapterIPConfig`
  - Added model `SanAdapterProperties`
  - Added model `SanClusterNetworkConfig`
  - Added model `SanNetworks`
  - Added enum `SdnIntegrationIntent`
  - Added model `SdnProperties`
  - Added enum `SdnStatus`
  - Added enum `SecretType`
  - Added model `SiteDetails`
  - Added model `StorageConfiguration`
  - Added model `StorageProfile`
  - Added model `StorageS2dConfig`
  - Added model `StorageSanConfig`
  - Added enum `StorageType`
  - Added model `TargetDeviceConfiguration`
  - Added model `TimeConfiguration`
  - Added model `UpdateContent`
  - Added model `UpdateContentProperties`
  - Added model `UserDetails`
  - Added model `ValidateOwnershipVouchersRequest`
  - Added model `ValidateOwnershipVouchersResponse`
  - Added enum `VolumeType`
  - Added model `WebProxyConfiguration`
  - Operation group `ClustersOperations` added method `begin_change_ring`
  - Operation group `UpdatesOperations` added method `begin_prepare`
  - Added operation group `ClusterJobsOperations`
  - Added operation group `DevicePoolsOperations`
  - Added operation group `EdgeMachineJobsOperations`
  - Added operation group `EdgeMachinesOperations`
  - Added operation group `KubernetesVersionsOperations`
  - Added operation group `OsImagesOperations`
  - Added operation group `OwnershipVouchersOperations`
  - Added operation group `PlatformUpdatesOperations`
  - Added operation group `PublishersOperations`
  - Added operation group `UpdateContentsOperations`
  - Added operation group `UpdateSummariesOperationGroupOperations`

## 8.0.0 (2026-03-31)

### Features Added

  - Client `AzureStackHCIClient` added parameter `cloud_setting` in method `__init__`
  - Client `AzureStackHCIClient` added method `send_request`
  - Client `AzureStackHCIClient` added operation group `edge_device_jobs`
  - Client `AzureStackHCIClient` added operation group `validated_solution_recipes`
  - Model `Cluster` added property `identity`
  - Model `ClusterPatch` added property `identity`
  - Model `ClusterReportedProperties` added property `msi_expiration_time_stamp`
  - Model `ClusterReportedProperties` added property `hardware_class`
  - Model `DeploymentCluster` added property `hardware_class`
  - Model `DeploymentCluster` added property `cluster_pattern`
  - Model `DeploymentData` added property `identity_provider`
  - Model `DeploymentData` added property `is_management_cluster`
  - Model `DeploymentData` added property `local_availability_zones`
  - Model `DeploymentData` added property `assembly_info`
  - Model `HciNicDetail` added property `rdma_capability`
  - Model `HciReportedProperties` added property `storage_profile`
  - Model `HciReportedProperties` added property `hardware_profile`
  - Model `InfrastructureNetwork` added property `dns_server_config`
  - Model `InfrastructureNetwork` added property `dns_zones`
  - Added model `AssemblyInfo`
  - Added model `AssemblyInfoPayload`
  - Added enum `ClusterPattern`
  - Added enum `DeviceLogCollectionStatus`
  - Added enum `DnsServerConfig`
  - Added model `DnsZones`
  - Added model `EdgeDeviceJob`
  - Added enum `EdgeDeviceKind`
  - Added model `ExtensionParameters`
  - Added model `ExtensionResource`
  - Added enum `HardwareClass`
  - Added model `HciCollectLogJobProperties`
  - Added model `HciEdgeDeviceJob`
  - Added model `HciEdgeDeviceJobProperties`
  - Added enum `HciEdgeDeviceJobType`
  - Added model `HciHardwareProfile`
  - Added model `HciRemoteSupportJobProperties`
  - Added model `HciStorageProfile`
  - Added enum `IdentityProvider`
  - Added enum `JobStatus`
  - Added model `LocalAvailabilityZones`
  - Added model `LogCollectionJobSession`
  - Added model `LogCollectionReportedProperties`
  - Added model `ManagedServiceIdentity`
  - Added enum `RdmaCapability`
  - Added model `ReconcileArcSettingsRequest`
  - Added model `ReconcileArcSettingsRequestProperties`
  - Added enum `RemoteSupportAccessLevel`
  - Added model `RemoteSupportJobNodeSettings`
  - Added model `RemoteSupportJobReportedProperties`
  - Added model `RemoteSupportSession`
  - Added model `SecretsLocationDetails`
  - Added model `SecretsLocationsChangeRequest`
  - Added enum `SecretsType`
  - Added model `UpdateStateProperties`
  - Added model `ValidatedSolutionRecipe`
  - Added model `ValidatedSolutionRecipeCapabilities`
  - Added model `ValidatedSolutionRecipeCapability`
  - Added model `ValidatedSolutionRecipeComponent`
  - Added model `ValidatedSolutionRecipeComponentMetadata`
  - Added model `ValidatedSolutionRecipeComponentPayload`
  - Added model `ValidatedSolutionRecipeContent`
  - Added model `ValidatedSolutionRecipeInfo`
  - Added model `ValidatedSolutionRecipeProperties`
  - Operation group `ArcSettingsOperations` added method `begin_reconcile`
  - Operation group `ClustersOperations` added method `begin_update_secrets_locations`
  - Added operation group `EdgeDeviceJobsOperations`
  - Added operation group `ValidatedSolutionRecipesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted or renamed client operation group `AzureStackHCIClient.publishers`
  - Model `ArcIdentityResponse` moved instance variables `arc_application_client_id`, `arc_application_tenant_id`, `arc_service_principal_object_id` and `arc_application_object_id` under property `properties` whose type is `ArcIdentityResponseProperties`
  - Model `ClusterIdentityResponse` moved instance variables `aad_client_id`, `aad_tenant_id`, `aad_service_principal_object_id` and `aad_application_object_id` under property `properties` whose type is `ClusterIdentityResponseProperties`
  - Model `DeploymentSetting` moved instance variables `provisioning_state`, `arc_node_resource_ids`, `deployment_mode`, `operation_type`, `deployment_configuration` and `reported_properties` under property `properties` whose type is `DeploymentSettingsProperties`
  - Model `ExtensionPatch` moved instance variable `extension_parameters` under property `properties` whose type is `ExtensionPatchProperties`
  - Model `SecuritySetting` moved instance variables `secured_core_compliance_assignment`, `wdac_compliance_assignment`, `smb_encryption_for_intra_cluster_traffic_compliance_assignment`, `security_compliance_status` and `provisioning_state` under property `properties` whose type is `SecurityProperties`
  - Deleted or renamed enum value `Status.FAILED`
  - Deleted or renamed enum value `Status.IN_PROGRESS`
  - Deleted or renamed enum value `Status.SUCCEEDED`
  - Deleted or renamed model `Publisher`
  - Deleted or renamed operation group `PublishersOperations`
  - Method `OffersOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `OffersOperations.list_by_cluster` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `OffersOperations.list_by_publisher` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SkusOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `SkusOperations.list_by_offer` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `ArcSettingList`/`ClusterList`/`ExtensionList`/`OfferList`/`PublisherList`/`SkuList`/`UpdateList`/`UpdateRunList`/`UpdateSummariesList` which actually were not used by SDK users

## 8.0.0b4 (2024-08-26)

### Features Added

  - The 'AzureStackHCIClient' client had operation group 'arc_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'clusters' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'deployment_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'edge_devices' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'extensions' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'offers' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'publishers' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'security_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'skus' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'update_runs' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'update_summaries' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'updates' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'arc_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'clusters' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'deployment_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'edge_devices' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'extensions' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'offers' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'publishers' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'security_settings' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'skus' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'update_runs' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'update_summaries' added in the current version
  - The 'AzureStackHCIClient' client had operation group 'updates' added in the current version
  - The model or publicly exposed class 'ArcSettingsOperations' was added in the current version
  - The model or publicly exposed class 'ClustersOperations' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingsOperations' was added in the current version
  - The model or publicly exposed class 'EdgeDevicesOperations' was added in the current version
  - The model or publicly exposed class 'ExtensionsOperations' was added in the current version
  - The model or publicly exposed class 'OffersOperations' was added in the current version
  - The model or publicly exposed class 'PublishersOperations' was added in the current version
  - The model or publicly exposed class 'SecuritySettingsOperations' was added in the current version
  - The model or publicly exposed class 'SkusOperations' was added in the current version
  - The model or publicly exposed class 'UpdateRunsOperations' was added in the current version
  - The model or publicly exposed class 'UpdateSummariesOperations' was added in the current version
  - The model or publicly exposed class 'UpdatesOperations' was added in the current version
  - The model or publicly exposed class 'Status' had property 'CONNECTED_RECENTLY' added in the current version
  - The model or publicly exposed class 'Status' had property 'DEPLOYMENT_FAILED' added in the current version
  - The model or publicly exposed class 'Status' had property 'DEPLOYMENT_IN_PROGRESS' added in the current version
  - The model or publicly exposed class 'Status' had property 'DEPLOYMENT_SUCCESS' added in the current version
  - The model or publicly exposed class 'Status' had property 'DISCONNECTED' added in the current version
  - The model or publicly exposed class 'Status' had property 'ERROR' added in the current version
  - The model or publicly exposed class 'Status' had property 'NOT_CONNECTED_RECENTLY' added in the current version
  - The model or publicly exposed class 'Status' had property 'NOT_SPECIFIED' added in the current version
  - The model or publicly exposed class 'Status' had property 'NOT_YET_REGISTERED' added in the current version
  - The model or publicly exposed class 'Status' had property 'VALIDATION_FAILED' added in the current version
  - The model or publicly exposed class 'Status' had property 'VALIDATION_IN_PROGRESS' added in the current version
  - The model or publicly exposed class 'Status' had property 'VALIDATION_SUCCESS' added in the current version
  - The model or publicly exposed class 'AccessLevel' was added in the current version
  - The model or publicly exposed class 'ArcConnectivityProperties' was added in the current version
  - The model or publicly exposed class 'ArcExtensionState' was added in the current version
  - The model or publicly exposed class 'ArcIdentityResponse' was added in the current version
  - The model or publicly exposed class 'ArcSetting' was added in the current version
  - The model or publicly exposed class 'ArcSettingAggregateState' was added in the current version
  - The model or publicly exposed class 'ArcSettingList' was added in the current version
  - The model or publicly exposed class 'ArcSettingsPatch' was added in the current version
  - The model or publicly exposed class 'AvailabilityType' was added in the current version
  - The model or publicly exposed class 'Cluster' was added in the current version
  - The model or publicly exposed class 'ClusterDesiredProperties' was added in the current version
  - The model or publicly exposed class 'ClusterIdentityResponse' was added in the current version
  - The model or publicly exposed class 'ClusterList' was added in the current version
  - The model or publicly exposed class 'ClusterNode' was added in the current version
  - The model or publicly exposed class 'ClusterNodeType' was added in the current version
  - The model or publicly exposed class 'ClusterPatch' was added in the current version
  - The model or publicly exposed class 'ClusterReportedProperties' was added in the current version
  - The model or publicly exposed class 'ComplianceAssignmentType' was added in the current version
  - The model or publicly exposed class 'ComplianceStatus' was added in the current version
  - The model or publicly exposed class 'ConnectivityStatus' was added in the current version
  - The model or publicly exposed class 'DefaultExtensionDetails' was added in the current version
  - The model or publicly exposed class 'DeploymentCluster' was added in the current version
  - The model or publicly exposed class 'DeploymentConfiguration' was added in the current version
  - The model or publicly exposed class 'DeploymentData' was added in the current version
  - The model or publicly exposed class 'DeploymentMode' was added in the current version
  - The model or publicly exposed class 'DeploymentSecuritySettings' was added in the current version
  - The model or publicly exposed class 'DeploymentSetting' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingAdapterPropertyOverrides' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingHostNetwork' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingIntents' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingListResult' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingStorageAdapterIPInfo' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingStorageNetworks' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingVirtualSwitchConfigurationOverrides' was added in the current version
  - The model or publicly exposed class 'DeploymentStep' was added in the current version
  - The model or publicly exposed class 'DeviceConfiguration' was added in the current version
  - The model or publicly exposed class 'DeviceKind' was added in the current version
  - The model or publicly exposed class 'DeviceState' was added in the current version
  - The model or publicly exposed class 'DiagnosticLevel' was added in the current version
  - The model or publicly exposed class 'EceActionStatus' was added in the current version
  - The model or publicly exposed class 'EceDeploymentSecrets' was added in the current version
  - The model or publicly exposed class 'EceReportedProperties' was added in the current version
  - The model or publicly exposed class 'EceSecrets' was added in the current version
  - The model or publicly exposed class 'EdgeDevice' was added in the current version
  - The model or publicly exposed class 'EdgeDeviceListResult' was added in the current version
  - The model or publicly exposed class 'EdgeDeviceProperties' was added in the current version
  - The model or publicly exposed class 'Extension' was added in the current version
  - The model or publicly exposed class 'ExtensionAggregateState' was added in the current version
  - The model or publicly exposed class 'ExtensionInstanceView' was added in the current version
  - The model or publicly exposed class 'ExtensionInstanceViewStatus' was added in the current version
  - The model or publicly exposed class 'ExtensionList' was added in the current version
  - The model or publicly exposed class 'ExtensionManagedBy' was added in the current version
  - The model or publicly exposed class 'ExtensionPatch' was added in the current version
  - The model or publicly exposed class 'ExtensionPatchParameters' was added in the current version
  - The model or publicly exposed class 'ExtensionProfile' was added in the current version
  - The model or publicly exposed class 'ExtensionUpgradeParameters' was added in the current version
  - The model or publicly exposed class 'HciEdgeDevice' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceAdapterPropertyOverrides' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceArcExtension' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceHostNetwork' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceIntents' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceProperties' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceStorageAdapterIPInfo' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceStorageNetworks' was added in the current version
  - The model or publicly exposed class 'HciEdgeDeviceVirtualSwitchConfigurationOverrides' was added in the current version
  - The model or publicly exposed class 'HciNetworkProfile' was added in the current version
  - The model or publicly exposed class 'HciNicDetail' was added in the current version
  - The model or publicly exposed class 'HciOsProfile' was added in the current version
  - The model or publicly exposed class 'HciReportedProperties' was added in the current version
  - The model or publicly exposed class 'HciValidationFailureDetail' was added in the current version
  - The model or publicly exposed class 'HealthState' was added in the current version
  - The model or publicly exposed class 'ImdsAttestation' was added in the current version
  - The model or publicly exposed class 'InfrastructureNetwork' was added in the current version
  - The model or publicly exposed class 'IpPools' was added in the current version
  - The model or publicly exposed class 'IsolatedVmAttestationConfiguration' was added in the current version
  - The model or publicly exposed class 'LogCollectionError' was added in the current version
  - The model or publicly exposed class 'LogCollectionJobType' was added in the current version
  - The model or publicly exposed class 'LogCollectionProperties' was added in the current version
  - The model or publicly exposed class 'LogCollectionRequest' was added in the current version
  - The model or publicly exposed class 'LogCollectionRequestProperties' was added in the current version
  - The model or publicly exposed class 'LogCollectionSession' was added in the current version
  - The model or publicly exposed class 'LogCollectionStatus' was added in the current version
  - The model or publicly exposed class 'ManagedServiceIdentityType' was added in the current version
  - The model or publicly exposed class 'NetworkController' was added in the current version
  - The model or publicly exposed class 'NicDetail' was added in the current version
  - The model or publicly exposed class 'NodeArcState' was added in the current version
  - The model or publicly exposed class 'NodeExtensionState' was added in the current version
  - The model or publicly exposed class 'Observability' was added in the current version
  - The model or publicly exposed class 'OemActivation' was added in the current version
  - The model or publicly exposed class 'Offer' was added in the current version
  - The model or publicly exposed class 'OfferList' was added in the current version
  - The model or publicly exposed class 'OperationType' was added in the current version
  - The model or publicly exposed class 'OptionalServices' was added in the current version
  - The model or publicly exposed class 'PackageVersionInfo' was added in the current version
  - The model or publicly exposed class 'PasswordCredential' was added in the current version
  - The model or publicly exposed class 'PerNodeExtensionState' was added in the current version
  - The model or publicly exposed class 'PerNodeRemoteSupportSession' was added in the current version
  - The model or publicly exposed class 'PerNodeState' was added in the current version
  - The model or publicly exposed class 'PhysicalNodes' was added in the current version
  - The model or publicly exposed class 'PrecheckResult' was added in the current version
  - The model or publicly exposed class 'PrecheckResultTags' was added in the current version
  - The model or publicly exposed class 'ProvisioningState' was added in the current version
  - The model or publicly exposed class 'Publisher' was added in the current version
  - The model or publicly exposed class 'PublisherList' was added in the current version
  - The model or publicly exposed class 'QosPolicyOverrides' was added in the current version
  - The model or publicly exposed class 'RawCertificateData' was added in the current version
  - The model or publicly exposed class 'RebootRequirement' was added in the current version
  - The model or publicly exposed class 'RemoteSupportNodeSettings' was added in the current version
  - The model or publicly exposed class 'RemoteSupportProperties' was added in the current version
  - The model or publicly exposed class 'RemoteSupportRequest' was added in the current version
  - The model or publicly exposed class 'RemoteSupportRequestProperties' was added in the current version
  - The model or publicly exposed class 'RemoteSupportType' was added in the current version
  - The model or publicly exposed class 'ReportedProperties' was added in the current version
  - The model or publicly exposed class 'SbeCredentials' was added in the current version
  - The model or publicly exposed class 'SbeDeploymentInfo' was added in the current version
  - The model or publicly exposed class 'SbeDeploymentPackageInfo' was added in the current version
  - The model or publicly exposed class 'SbePartnerInfo' was added in the current version
  - The model or publicly exposed class 'SbePartnerProperties' was added in the current version
  - The model or publicly exposed class 'ScaleUnits' was added in the current version
  - The model or publicly exposed class 'SdnIntegration' was added in the current version
  - The model or publicly exposed class 'SecurityComplianceStatus' was added in the current version
  - The model or publicly exposed class 'SecuritySetting' was added in the current version
  - The model or publicly exposed class 'SecuritySettingListResult' was added in the current version
  - The model or publicly exposed class 'ServiceConfiguration' was added in the current version
  - The model or publicly exposed class 'ServiceName' was added in the current version
  - The model or publicly exposed class 'Severity' was added in the current version
  - The model or publicly exposed class 'Sku' was added in the current version
  - The model or publicly exposed class 'SkuList' was added in the current version
  - The model or publicly exposed class 'SkuMappings' was added in the current version
  - The model or publicly exposed class 'SoftwareAssuranceChangeRequest' was added in the current version
  - The model or publicly exposed class 'SoftwareAssuranceChangeRequestProperties' was added in the current version
  - The model or publicly exposed class 'SoftwareAssuranceIntent' was added in the current version
  - The model or publicly exposed class 'SoftwareAssuranceProperties' was added in the current version
  - The model or publicly exposed class 'SoftwareAssuranceStatus' was added in the current version
  - The model or publicly exposed class 'State' was added in the current version
  - The model or publicly exposed class 'Step' was added in the current version
  - The model or publicly exposed class 'Storage' was added in the current version
  - The model or publicly exposed class 'SwitchDetail' was added in the current version
  - The model or publicly exposed class 'SwitchExtension' was added in the current version
  - The model or publicly exposed class 'Update' was added in the current version
  - The model or publicly exposed class 'UpdateList' was added in the current version
  - The model or publicly exposed class 'UpdatePrerequisite' was added in the current version
  - The model or publicly exposed class 'UpdateRun' was added in the current version
  - The model or publicly exposed class 'UpdateRunList' was added in the current version
  - The model or publicly exposed class 'UpdateRunPropertiesState' was added in the current version
  - The model or publicly exposed class 'UpdateSummaries' was added in the current version
  - The model or publicly exposed class 'UpdateSummariesList' was added in the current version
  - The model or publicly exposed class 'UpdateSummariesPropertiesState' was added in the current version
  - The model or publicly exposed class 'UploadCertificateRequest' was added in the current version
  - The model or publicly exposed class 'UserAssignedIdentity' was added in the current version
  - The model or publicly exposed class 'ValidateRequest' was added in the current version
  - The model or publicly exposed class 'ValidateResponse' was added in the current version
  - The model or publicly exposed class 'WindowsServerSubscription' was added in the current version
  - The model or publicly exposed class 'ArcSettingsOperations' was added in the current version
  - The model or publicly exposed class 'ClustersOperations' was added in the current version
  - The model or publicly exposed class 'DeploymentSettingsOperations' was added in the current version
  - The model or publicly exposed class 'EdgeDevicesOperations' was added in the current version
  - The model or publicly exposed class 'ExtensionsOperations' was added in the current version
  - The model or publicly exposed class 'OffersOperations' was added in the current version
  - The model or publicly exposed class 'PublishersOperations' was added in the current version
  - The model or publicly exposed class 'SecuritySettingsOperations' was added in the current version
  - The model or publicly exposed class 'SkusOperations' was added in the current version
  - The model or publicly exposed class 'UpdateRunsOperations' was added in the current version
  - The model or publicly exposed class 'UpdateSummariesOperations' was added in the current version
  - The model or publicly exposed class 'UpdatesOperations' was added in the current version

### Breaking Changes

  - The 'AzureStackHCIClient' client had operation group 'gallery_images' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'logical_networks' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'marketplace_gallery_images' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'network_interfaces' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'storage_containers' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'virtual_hard_disks' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'virtual_machine_instances' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'hybrid_identity_metadata' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'guest_agent' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'guest_agents' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'gallery_images' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'logical_networks' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'marketplace_gallery_images' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'network_interfaces' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'storage_containers' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'virtual_hard_disks' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'virtual_machine_instances' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'hybrid_identity_metadata' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'guest_agent' deleted or renamed in the current version
  - The 'AzureStackHCIClient' client had operation group 'guest_agents' deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImagesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentsOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'HybridIdentityMetadataOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworksOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImagesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfacesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainersOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDisksOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'CloudInitDataSource' was deleted or renamed in the current version
  - The model or publicly exposed class 'DiskFileFormat' was deleted or renamed in the current version
  - The model or publicly exposed class 'ExtendedLocation' was deleted or renamed in the current version
  - The model or publicly exposed class 'ExtendedLocationTypes' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryDiskImage' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageIdentifier' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageStatusDownloadStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageVersion' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImageVersionStorageProfile' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImages' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImagesListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImagesUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryOSDiskImage' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgent' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentInstallStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentList' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestCredential' was deleted or renamed in the current version
  - The model or publicly exposed class 'HardwareProfileUpdate' was deleted or renamed in the current version
  - The model or publicly exposed class 'HttpProxyConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'HybridIdentityMetadata' was deleted or renamed in the current version
  - The model or publicly exposed class 'HybridIdentityMetadataList' was deleted or renamed in the current version
  - The model or publicly exposed class 'HyperVGeneration' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPConfigurationProperties' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPConfigurationPropertiesSubnet' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPPool' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPPoolInfo' was deleted or renamed in the current version
  - The model or publicly exposed class 'IPPoolTypeEnum' was deleted or renamed in the current version
  - The model or publicly exposed class 'Identity' was deleted or renamed in the current version
  - The model or publicly exposed class 'InstanceViewStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'InterfaceDNSSettings' was deleted or renamed in the current version
  - The model or publicly exposed class 'IpAllocationMethodEnum' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworkPropertiesDhcpOptions' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworkStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworkStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworks' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworksListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworksUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImageStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImageStatusDownloadStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImageStatusProvisioningStatus' was deleted or renamed in the current version        
  - The model or publicly exposed class 'MarketplaceGalleryImages' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImagesListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImagesUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfaceStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfaceStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfaces' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfacesListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfacesUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkProfileUpdate' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkProfileUpdateNetworkInterfacesItem' was deleted or renamed in the current version
  - The model or publicly exposed class 'OperatingSystemTypes' was deleted or renamed in the current version
  - The model or publicly exposed class 'OsProfileUpdate' was deleted or renamed in the current version
  - The model or publicly exposed class 'OsProfileUpdateLinuxConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'OsProfileUpdateWindowsConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'PowerStateEnum' was deleted or renamed in the current version
  - The model or publicly exposed class 'ProvisioningAction' was deleted or renamed in the current version
  - The model or publicly exposed class 'ProvisioningStateEnum' was deleted or renamed in the current version
  - The model or publicly exposed class 'Route' was deleted or renamed in the current version
  - The model or publicly exposed class 'RouteTable' was deleted or renamed in the current version
  - The model or publicly exposed class 'SecurityTypes' was deleted or renamed in the current version
  - The model or publicly exposed class 'SshConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'SshPublicKey' was deleted or renamed in the current version
  - The model or publicly exposed class 'StatusTypes' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainerStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainerStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainers' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainersListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainersUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageProfileUpdate' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageProfileUpdateDataDisksItem' was deleted or renamed in the current version
  - The model or publicly exposed class 'Subnet' was deleted or renamed in the current version
  - The model or publicly exposed class 'SubnetPropertiesFormatIpConfigurationReferencesItem' was deleted or renamed in the current version    
  - The model or publicly exposed class 'VirtualHardDiskStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDiskStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDisks' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDisksListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDisksUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineConfigAgentInstanceView' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstance' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstanceListResult' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesHardwareProfile' was deleted or renamed in the current version        
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesNetworkProfile' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesNetworkProfileNetworkInterfacesItem' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesOsProfile' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesOsProfileLinuxConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesOsProfileWindowsConfiguration' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesSecurityProfile' was deleted or renamed in the current version        
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesSecurityProfileUefiSettings' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesStorageProfile' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesStorageProfileDataDisksItem' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesStorageProfileImageReference' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancePropertiesStorageProfileOsDisk' was deleted or renamed in the current version   
  - The model or publicly exposed class 'VirtualMachineInstanceStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstanceStatusProvisioningStatus' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstanceUpdateProperties' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstanceUpdateRequest' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstanceView' was deleted or renamed in the current version
  - The model or publicly exposed class 'VmSizeEnum' was deleted or renamed in the current version
  - The model or publicly exposed class 'GalleryImagesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'GuestAgentsOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'HybridIdentityMetadataOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'LogicalNetworksOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'MarketplaceGalleryImagesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'NetworkInterfacesOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'StorageContainersOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualHardDisksOperations' was deleted or renamed in the current version
  - The model or publicly exposed class 'VirtualMachineInstancesOperations' was deleted or renamed in the current version

## 8.0.0b3 (2023-10-23)

### Features Added

  - Added operation GuestAgentsOperations.list
  - Added operation HybridIdentityMetadataOperations.list
  - Added operation group GalleryImagesOperations
  - Added operation group LogicalNetworksOperations
  - Added operation group MarketplaceGalleryImagesOperations
  - Added operation group NetworkInterfacesOperations
  - Added operation group StorageContainersOperations
  - Added operation group VirtualHardDisksOperations
  - Added operation group VirtualMachineInstancesOperations
  - Model HardwareProfileUpdate has a new parameter memory_mb
  - Model HttpProxyConfiguration has a new parameter http_proxy
  - Model HttpProxyConfiguration has a new parameter no_proxy
  - Model HttpProxyConfiguration has a new parameter trusted_ca
  - Model IPPool has a new parameter name
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model StorageProfileUpdateDataDisksItem has a new parameter id
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model GuestAgent no longer has parameter http_proxy_config
  - Model HardwareProfileUpdate no longer has parameter memory_gb
  - Model StorageProfileUpdateDataDisksItem no longer has parameter name
  - Operation GuestAgentOperations.begin_create has a new required parameter resource_uri
  - Operation GuestAgentOperations.begin_create no longer has parameter name
  - Operation GuestAgentOperations.begin_create no longer has parameter resource_group_name
  - Operation GuestAgentOperations.begin_create no longer has parameter virtual_machine_name
  - Operation GuestAgentOperations.begin_delete has a new required parameter resource_uri
  - Operation GuestAgentOperations.begin_delete no longer has parameter name
  - Operation GuestAgentOperations.begin_delete no longer has parameter resource_group_name
  - Operation GuestAgentOperations.begin_delete no longer has parameter virtual_machine_name
  - Operation GuestAgentOperations.get has a new required parameter resource_uri
  - Operation GuestAgentOperations.get no longer has parameter name
  - Operation GuestAgentOperations.get no longer has parameter resource_group_name
  - Operation GuestAgentOperations.get no longer has parameter virtual_machine_name
  - Operation HybridIdentityMetadataOperations.get has a new required parameter resource_uri
  - Operation HybridIdentityMetadataOperations.get no longer has parameter metadata_name
  - Operation HybridIdentityMetadataOperations.get no longer has parameter resource_group_name
  - Operation HybridIdentityMetadataOperations.get no longer has parameter virtual_machine_name
  - Removed operation GuestAgentsOperations.list_by_virtual_machines
  - Removed operation HybridIdentityMetadataOperations.create
  - Removed operation HybridIdentityMetadataOperations.delete
  - Removed operation HybridIdentityMetadataOperations.list_by_virtual_machines
  - Removed operation group ArcSettingsOperations
  - Removed operation group ClustersOperations
  - Removed operation group ExtensionsOperations
  - Removed operation group GalleryimagesOperations
  - Removed operation group MachineExtensionsOperations
  - Removed operation group MarketplacegalleryimagesOperations
  - Removed operation group NetworkinterfacesOperations
  - Removed operation group StoragecontainersOperations
  - Removed operation group VirtualharddisksOperations
  - Removed operation group VirtualmachinesOperations
  - Removed operation group VirtualnetworksOperations

## 8.0.0b2 (2022-12-15)

### Features Added

  - Added operation ClustersOperations.delete
  - Added operation group GalleryimagesOperations
  - Added operation group GuestAgentOperations
  - Added operation group GuestAgentsOperations
  - Added operation group HybridIdentityMetadataOperations
  - Added operation group MachineExtensionsOperations
  - Added operation group MarketplacegalleryimagesOperations
  - Added operation group NetworkinterfacesOperations
  - Added operation group StoragecontainersOperations
  - Added operation group VirtualharddisksOperations
  - Added operation group VirtualmachinesOperations
  - Added operation group VirtualnetworksOperations
  - Model ArcSetting has a new parameter created_at
  - Model ArcSetting has a new parameter created_by
  - Model ArcSetting has a new parameter created_by_type
  - Model ArcSetting has a new parameter last_modified_at
  - Model ArcSetting has a new parameter last_modified_by
  - Model ArcSetting has a new parameter last_modified_by_type
  - Model Cluster has a new parameter created_at
  - Model Cluster has a new parameter created_by
  - Model Cluster has a new parameter created_by_type
  - Model Cluster has a new parameter last_modified_at
  - Model Cluster has a new parameter last_modified_by
  - Model Cluster has a new parameter last_modified_by_type
  - Model Extension has a new parameter created_at
  - Model Extension has a new parameter created_by
  - Model Extension has a new parameter created_by_type
  - Model Extension has a new parameter last_modified_at
  - Model Extension has a new parameter last_modified_by
  - Model Extension has a new parameter last_modified_by_type

### Breaking Changes

  - Model ArcSetting no longer has parameter arc_application_client_id
  - Model ArcSetting no longer has parameter arc_application_object_id
  - Model ArcSetting no longer has parameter arc_application_tenant_id
  - Model ArcSetting no longer has parameter arc_service_principal_object_id
  - Model ArcSetting no longer has parameter connectivity_properties
  - Model ArcSetting no longer has parameter system_data
  - Model Cluster no longer has parameter aad_application_object_id
  - Model Cluster no longer has parameter aad_service_principal_object_id
  - Model Cluster no longer has parameter principal_id
  - Model Cluster no longer has parameter service_endpoint
  - Model Cluster no longer has parameter software_assurance_properties
  - Model Cluster no longer has parameter system_data
  - Model Cluster no longer has parameter tenant_id
  - Model Cluster no longer has parameter type_identity_type
  - Model Cluster no longer has parameter user_assigned_identities
  - Model ClusterNode no longer has parameter node_type
  - Model ClusterNode no longer has parameter os_display_version
  - Model ClusterPatch no longer has parameter principal_id
  - Model ClusterPatch no longer has parameter tenant_id
  - Model ClusterPatch no longer has parameter type
  - Model ClusterPatch no longer has parameter user_assigned_identities
  - Model Extension no longer has parameter system_data
  - Model ProxyResource no longer has parameter system_data
  - Model Resource no longer has parameter system_data
  - Model TrackedResource no longer has parameter system_data
  - Removed operation ArcSettingsOperations.begin_create_identity
  - Removed operation ArcSettingsOperations.generate_password
  - Removed operation ArcSettingsOperations.update
  - Removed operation ClustersOperations.begin_create_identity
  - Removed operation ClustersOperations.begin_delete
  - Removed operation ClustersOperations.begin_extend_software_assurance_benefit
  - Removed operation ClustersOperations.begin_upload_certificate
  - Removed operation group OffersOperations
  - Removed operation group PublishersOperations
  - Removed operation group SkusOperations
  - Removed operation group UpdateRunsOperations
  - Removed operation group UpdateSummariesOperations
  - Removed operation group UpdatesOperations

## 8.0.0b1 (2022-11-25)

### Features Added

  - Added operation ClustersOperations.begin_extend_software_assurance_benefit
  - Added operation group OffersOperations
  - Added operation group PublishersOperations
  - Added operation group SkusOperations
  - Added operation group UpdateRunsOperations
  - Added operation group UpdateSummariesOperations
  - Added operation group UpdatesOperations
  - Model ArcSetting has a new parameter system_data
  - Model Cluster has a new parameter principal_id
  - Model Cluster has a new parameter software_assurance_properties
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter tenant_id
  - Model Cluster has a new parameter type_identity_type
  - Model Cluster has a new parameter user_assigned_identities
  - Model ClusterNode has a new parameter node_type
  - Model ClusterNode has a new parameter os_display_version
  - Model ClusterPatch has a new parameter principal_id
  - Model ClusterPatch has a new parameter tenant_id
  - Model ClusterPatch has a new parameter type
  - Model ClusterPatch has a new parameter user_assigned_identities
  - Model Extension has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model ArcSetting no longer has parameter created_at
  - Model ArcSetting no longer has parameter created_by
  - Model ArcSetting no longer has parameter created_by_type
  - Model ArcSetting no longer has parameter last_modified_at
  - Model ArcSetting no longer has parameter last_modified_by
  - Model ArcSetting no longer has parameter last_modified_by_type
  - Model Cluster no longer has parameter created_at
  - Model Cluster no longer has parameter created_by
  - Model Cluster no longer has parameter created_by_type
  - Model Cluster no longer has parameter last_modified_at
  - Model Cluster no longer has parameter last_modified_by
  - Model Cluster no longer has parameter last_modified_by_type
  - Model Extension no longer has parameter created_at
  - Model Extension no longer has parameter created_by
  - Model Extension no longer has parameter created_by_type
  - Model Extension no longer has parameter last_modified_at
  - Model Extension no longer has parameter last_modified_by
  - Model Extension no longer has parameter last_modified_by_type

## 7.0.0 (2022-05-26)

**Features**

  - Added operation ArcSettingsOperations.begin_create_identity
  - Added operation ArcSettingsOperations.generate_password
  - Added operation ArcSettingsOperations.update
  - Added operation ClustersOperations.begin_create_identity
  - Added operation ClustersOperations.begin_delete
  - Added operation ClustersOperations.begin_upload_certificate
  - Model ArcSetting has a new parameter arc_application_client_id
  - Model ArcSetting has a new parameter arc_application_object_id
  - Model ArcSetting has a new parameter arc_application_tenant_id
  - Model ArcSetting has a new parameter arc_service_principal_object_id
  - Model ArcSetting has a new parameter connectivity_properties
  - Model Cluster has a new parameter aad_application_object_id
  - Model Cluster has a new parameter aad_service_principal_object_id
  - Model Cluster has a new parameter service_endpoint

**Breaking changes**

  - Removed operation ClustersOperations.delete

## 6.1.0 (2022-04-08)

**Features**

  - Model Cluster has a new parameter desired_properties
  - Model ClusterNode has a new parameter windows_server_subscription
  - Model ClusterPatch has a new parameter aad_client_id
  - Model ClusterPatch has a new parameter aad_tenant_id
  - Model ClusterPatch has a new parameter desired_properties
  - Model ClusterReportedProperties has a new parameter diagnostic_level
  - Model ClusterReportedProperties has a new parameter imds_attestation

## 6.1.0b1 (2021-06-29)

**Features**

  - Model Cluster has a new parameter cloud_management_endpoint
  - Added operation group ArcSettingsOperations
  - Added operation group ExtensionsOperations

## 6.0.0 (2021-05-20)

- GA release

## 6.0.0b1 (2020-12-08)

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

## 1.0.0 (2020-10-14)

**Features**

  - Model Cluster has a new parameter last_billing_timestamp
  - Model Cluster has a new parameter registration_timestamp
  - Model Cluster has a new parameter last_sync_timestamp
  - Added operation ClustersOperations.list_by_subscription

**Breaking changes**

  - Removed operation ClustersOperations.list

## 1.0.0rc (2020-07-22)

* Initial Release
