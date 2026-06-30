# Release History

## 1.0.0 (2026-06-29)

### Features Added

  - Model `ResourceOperationDetails` added property `fallback_operation_info`
  - Model `RetryPolicy` added property `on_failure_action`
  - Added model `FallbackOperationInfo`
  - Added operation group `VirtualMachineBulkOperationsOperations`

### Breaking Changes

  - Deleted or renamed client `ComputeBulkActionsMgmtClient`
  - Renamed model `CancelOperationsRequest` to `CancelOperationsContent`
  - Renamed model `ExecuteDeallocateRequest` to `ExecuteDeallocateContent`
  - Renamed model `ExecuteDeleteRequest` to `ExecuteDeleteContent`
  - Renamed model `ExecuteHibernateRequest` to `ExecuteHibernateContent`
  - Renamed model `ExecuteStartRequest` to `ExecuteStartContent`
  - Renamed model `GetOperationStatusRequest` to `GetOperationStatusContent`
  - Deleted or renamed operation group `BulkActionsOperations`
  - Model `ExecutionParameters` deleted or renamed its instance variable `optimization_preference`

### Other Changes

  - Deleted model `AcceleratorManufacturer`/`AcceleratorType`/`AdditionalCapabilities`/`AdditionalUnattendContent`/`AllInstancesDown`/`AllocationStrategy`/`ApiEntityReference`/`ApiError`/`ApiErrorBase`/`ApplicationProfile`/`ArchitectureType`/`BootDiagnostics`/`CachingTypes`/`CapacityReservationProfile`/`CapacityType`/`ComputeProfile`/`CpuManufacturer`/`CreateResourceOperationResponse`/`CreatedByType`/`DataDisk`/`DeleteOptions`/`DiagnosticsProfile`/`DiffDiskOptions`/`DiffDiskPlacement`/`DiffDiskSettings`/`DiskControllerTypes`/`DiskCreateOptionTypes`/`DiskDeleteOptionTypes`/`DiskDetachOptionTypes`/`DiskEncryptionSetParameters`/`DiskEncryptionSettings`/`DomainNameLabelScopeTypes`/`EncryptionIdentity`/`EventGridAndResourceGraph`/`EvictionPolicy`/`ExecuteCreateRequest`/`HostEndpointSettings`/`HyperVGeneration`/`IPVersions`/`ImageReference`/`InnerError`/`KeyVaultKeyReference`/`KeyVaultSecretReference`/`LaunchBulkInstancesOperationProperties`/`LinuxConfiguration`/`LinuxPatchAssessmentMode`/`LinuxPatchSettings`/`LinuxVMGuestPatchAutomaticByPlatformRebootSetting`/`LinuxVMGuestPatchAutomaticByPlatformSettings`/`LinuxVMGuestPatchMode`/`LocalStorageDiskType`/`LocationBasedLaunchBulkInstancesOperation`/`ManagedDiskParameters`/`ManagedServiceIdentity`/`ManagedServiceIdentityType`/`Mode`/`Modes`/`NetworkApiVersion`/`NetworkInterfaceAuxiliaryMode`/`NetworkInterfaceAuxiliarySku`/`NetworkInterfaceReference`/`NetworkInterfaceReferenceProperties`/`NetworkProfile`/`OSDisk`/`OSImageNotificationProfile`/`OSProfile`/`OperatingSystemTypes`/`OperationStatusResult`/`OptimizationPreference`/`PatchSettings`/`Plan`/`PriorityProfile`/`ProtocolTypes`/`ProvisioningState`/`ProxyAgentSettings`/`ProxyResource`/`PublicIPAddressSku`/`PublicIPAddressSkuName`/`PublicIPAddressSkuTier`/`PublicIPAllocationMethod`/`Resource`/`ResourceProvisionPayload`/`ScheduledEventsAdditionalPublishingTargets`/`ScheduledEventsPolicy`/`ScheduledEventsProfile`/`SecurityEncryptionTypes`/`SecurityProfile`/`SecurityTypes`/`SettingNames`/`SshConfiguration`/`SshPublicKey`/`StorageAccountTypes`/`StorageProfile`/`SubResource`/`SystemData`/`TerminateNotificationProfile`/`UefiSettings`/`UserAssignedIdentity`/`UserInitiatedReboot`/`UserInitiatedRedeploy`/`VMAttributeMinMaxDouble`/`VMAttributeMinMaxInteger`/`VMAttributeSupport`/`VMAttributes`/`VMCategory`/`VMDiskSecurityProfile`/`VMGalleryApplication`/`VMOperationStatus`/`VaultCertificate`/`VaultSecretGroup`/`VirtualHardDisk`/`VirtualMachine`/`VirtualMachineExtension`/`VirtualMachineExtensionProperties`/`VirtualMachineIpTag`/`VirtualMachineNetworkInterfaceConfiguration`/`VirtualMachineNetworkInterfaceConfigurationProperties`/`VirtualMachineNetworkInterfaceDnsSettingsConfiguration`/`VirtualMachineNetworkInterfaceIPConfiguration`/`VirtualMachineNetworkInterfaceIPConfigurationProperties`/`VirtualMachineProfile`/`VirtualMachinePublicIPAddressConfiguration`/`VirtualMachinePublicIPAddressConfigurationProperties`/`VirtualMachinePublicIPAddressDnsSettingsConfiguration`/`VirtualMachineType`/`VmSizeProfile`/`WinRMConfiguration`/`WinRMListener`/`WindowsConfiguration`/`WindowsPatchAssessmentMode`/`WindowsVMGuestPatchAutomaticByPlatformRebootSetting`/`WindowsVMGuestPatchAutomaticByPlatformSettings`/`WindowsVMGuestPatchMode`/`ZoneAllocationPolicy`/`ZoneDistributionStrategy`/`ZonePreference` which actually were not used by SDK users

## 1.0.0b1 (1970-01-01)

### Other Changes

  - Initial version
