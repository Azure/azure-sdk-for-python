# Release History

## 1.2.0b2 (2026-05-06)

### Features Added

  - Model `ComputeScheduleMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Enum `ActionType` added member `INTERNAL`
  - Model `ResourceOperationDetails` added property `fallback_operation_info`
  - Enum `ResourceOperationType` added member `CREATE`
  - Enum `ResourceOperationType` added member `DELETE`
  - Model `ResourceProvisionPayload` added property `virtual_machine_base_profile`
  - Model `ResourceProvisionPayload` added property `virtual_machine_overrides`
  - Model `RetryPolicy` added property `on_failure_action`
  - Added model `AdditionalCapabilities`
  - Added model `AdditionalUnattendContent`
  - Added model `AllInstancesDown`
  - Added enum `AllocationStrategy`
  - Added model `ApiEntityReference`
  - Added model `ApplicationProfile`
  - Added model `BootDiagnostics`
  - Added model `BulkActionVMExtension`
  - Added model `BulkActionVMProperties`
  - Added model `BulkActionVmExtensionProperties`
  - Added model `BulkVMConfiguration`
  - Added enum `CachingTypes`
  - Added model `CancelOperationsContent`
  - Added model `CapacityReservationProfile`
  - Added model `CreateFlexResourceOperationResponse`
  - Added model `DataDisk`
  - Added enum `DeleteOptions`
  - Added model `DiagnosticsProfile`
  - Added enum `DiffDiskOptions`
  - Added enum `DiffDiskPlacement`
  - Added model `DiffDiskSettings`
  - Added enum `DiskControllerTypes`
  - Added enum `DiskCreateOptionTypes`
  - Added enum `DiskDeleteOptionTypes`
  - Added enum `DiskDetachOptionTypes`
  - Added model `DiskEncryptionSetParameters`
  - Added model `DiskEncryptionSettings`
  - Added enum `DistributionStrategy`
  - Added enum `DomainNameLabelScopeTypes`
  - Added model `EncryptionIdentity`
  - Added model `EventGridAndResourceGraph`
  - Added model `ExecuteCreateContent`
  - Added model `ExecuteCreateFlexContent`
  - Added model `ExecuteDeallocateContent`
  - Added model `ExecuteDeleteContent`
  - Added model `ExecuteHibernateContent`
  - Added model `ExecuteStartContent`
  - Added model `ExtendedLocation`
  - Added enum `ExtendedLocationType`
  - Added model `FallbackOperationInfo`
  - Added model `FlexProperties`
  - Added model `GetOperationErrorsContent`
  - Added model `GetOperationStatusContent`
  - Added model `HardwareProfile`
  - Added model `HostEndpointSettings`
  - Added enum `IPVersions`
  - Added model `ImageReference`
  - Added model `KeyVaultKeyReference`
  - Added model `KeyVaultSecretReference`
  - Added model `LinuxConfiguration`
  - Added enum `LinuxPatchAssessmentMode`
  - Added model `LinuxPatchSettings`
  - Added enum `LinuxVMGuestPatchAutomaticByPlatformRebootSetting`
  - Added model `LinuxVMGuestPatchAutomaticByPlatformSettings`
  - Added enum `LinuxVMGuestPatchMode`
  - Added model `ManagedDiskParameters`
  - Added enum `Mode`
  - Added enum `Modes`
  - Added enum `NetworkApiVersion`
  - Added enum `NetworkInterfaceAuxiliaryMode`
  - Added enum `NetworkInterfaceAuxiliarySku`
  - Added model `NetworkInterfaceReference`
  - Added model `NetworkInterfaceReferenceProperties`
  - Added model `NetworkProfile`
  - Added model `OSDisk`
  - Added model `OSImageNotificationProfile`
  - Added model `OSProfile`
  - Added enum `OperatingSystemTypes`
  - Added enum `OsType`
  - Added model `PatchSettings`
  - Added model `Placement`
  - Added model `Plan`
  - Added model `PriorityProfile`
  - Added enum `PriorityType`
  - Added enum `ProtocolTypes`
  - Added model `ProxyAgentSettings`
  - Added model `PublicIPAddressSku`
  - Added enum `PublicIPAddressSkuName`
  - Added enum `PublicIPAddressSkuTier`
  - Added enum `PublicIPAllocationMethod`
  - Added model `RecurringActionsResourceOperationResult`
  - Added enum `ResourceIdentityType`
  - Added model `ResourceProvisionFlexPayload`
  - Added enum `ScheduledActionType`
  - Added model `ScheduledActionUpdate`
  - Added model `ScheduledActionUpdateProperties`
  - Added model `ScheduledActionsExtensionProperties`
  - Added model `ScheduledEventsAdditionalPublishingTargets`
  - Added model `ScheduledEventsPolicy`
  - Added model `ScheduledEventsProfile`
  - Added enum `SecurityEncryptionTypes`
  - Added model `SecurityProfile`
  - Added enum `SecurityTypes`
  - Added enum `SettingNames`
  - Added model `SshConfiguration`
  - Added model `SshPublicKey`
  - Added enum `StorageAccountTypes`
  - Added model `StorageProfile`
  - Added model `SubResource`
  - Added model `SubmitDeallocateContent`
  - Added model `SubmitHibernateContent`
  - Added model `SubmitStartContent`
  - Added model `TerminateNotificationProfile`
  - Added model `UefiSettings`
  - Added model `UserAssignedIdentitiesValue`
  - Added model `UserInitiatedReboot`
  - Added model `UserInitiatedRedeploy`
  - Added model `VMDiskSecurityProfile`
  - Added model `VMGalleryApplication`
  - Added model `VaultCertificate`
  - Added model `VaultSecretGroup`
  - Added model `VirtualHardDisk`
  - Added model `VirtualMachineIdentity`
  - Added model `VirtualMachineIpTag`
  - Added model `VirtualMachineNetworkInterfaceConfiguration`
  - Added model `VirtualMachineNetworkInterfaceConfigurationProperties`
  - Added model `VirtualMachineNetworkInterfaceDnsSettingsConfiguration`
  - Added model `VirtualMachineNetworkInterfaceIPConfiguration`
  - Added model `VirtualMachineNetworkInterfaceIPConfigurationProperties`
  - Added model `VirtualMachinePublicIPAddressConfiguration`
  - Added model `VirtualMachinePublicIPAddressConfigurationProperties`
  - Added model `VirtualMachinePublicIPAddressDnsSettingsConfiguration`
  - Added model `VmSizeProfile`
  - Added model `VmSizeProperties`
  - Added model `WinRMConfiguration`
  - Added model `WinRMListener`
  - Added model `WindowsConfiguration`
  - Added enum `WindowsPatchAssessmentMode`
  - Added enum `WindowsVMGuestPatchAutomaticByPlatformRebootSetting`
  - Added model `WindowsVMGuestPatchAutomaticByPlatformSettings`
  - Added enum `WindowsVMGuestPatchMode`
  - Added model `ZoneAllocationPolicy`
  - Added enum `ZonePlacementPolicyType`
  - Added model `ZonePreference`
  - Model `ScheduledActionsOperations` added method `virtual_machines_execute_create_flex`

### Breaking Changes

  - Deleted or renamed enum value `ActionType.DEALLOCATE`
  - Deleted or renamed enum value `ActionType.HIBERNATE`
  - Deleted or renamed enum value `ActionType.START`
  - Model `ResourceProvisionPayload` deleted or renamed its instance variable `base_profile`
  - Model `ResourceProvisionPayload` deleted or renamed its instance variable `resource_overrides`
  - Deleted or renamed model `CancelOperationsRequest`
  - Deleted or renamed model `ExecuteCreateRequest`
  - Deleted or renamed model `ExecuteDeallocateRequest`
  - Deleted or renamed model `ExecuteDeleteRequest`
  - Deleted or renamed model `ExecuteHibernateRequest`
  - Deleted or renamed model `ExecuteStartRequest`
  - Deleted or renamed model `GetOperationErrorsRequest`
  - Deleted or renamed model `GetOperationStatusRequest`
  - Deleted or renamed model `ResourceOperationResponse`
  - Deleted or renamed model `SubmitDeallocateRequest`
  - Deleted or renamed model `SubmitHibernateRequest`
  - Deleted or renamed model `SubmitStartRequest`

## 1.2.0b1 (2025-07-24)

### Features Added

  - Client `ComputeScheduleMgmtClient` added operation group `scheduled_action_extension`
  - Client `ComputeScheduleMgmtClient` added operation group `occurrences`
  - Client `ComputeScheduleMgmtClient` added operation group `occurrence_extension`
  - Added model `CancelOccurrenceRequest`
  - Added enum `CreatedByType`
  - Added model `DelayRequest`
  - Added model `ExtensionResource`
  - Added enum `Language`
  - Added enum `Month`
  - Added model `NotificationProperties`
  - Added enum `NotificationType`
  - Added model `Occurrence`
  - Added model `OccurrenceExtensionProperties`
  - Added model `OccurrenceExtensionResource`
  - Added model `OccurrenceProperties`
  - Added model `OccurrenceResource`
  - Added model `OccurrenceResultSummary`
  - Added enum `OccurrenceState`
  - Added enum `ProvisioningState`
  - Added model `ProxyResource`
  - Added model `RecurringActionsResourceOperationResult`
  - Added model `Resource`
  - Added model `ResourceAttachRequest`
  - Added model `ResourceDetachRequest`
  - Added enum `ResourceOperationStatus`
  - Added model `ResourcePatchRequest`
  - Added enum `ResourceProvisioningState`
  - Added model `ResourceResultSummary`
  - Added model `ResourceStatus`
  - Added enum `ResourceType`
  - Added model `ScheduledAction`
  - Added model `ScheduledActionProperties`
  - Added model `ScheduledActionResource`
  - Added model `ScheduledActionResources`
  - Added enum `ScheduledActionType`
  - Added model `ScheduledActionUpdate`
  - Added model `ScheduledActionUpdateProperties`
  - Added model `ScheduledActionsSchedule`
  - Added model `SystemData`
  - Added model `TrackedResource`
  - Added enum `WeekDay`
  - Model `ScheduledActionsOperations` added method `attach_resources`
  - Model `ScheduledActionsOperations` added method `begin_create_or_update`
  - Model `ScheduledActionsOperations` added method `begin_delete`
  - Model `ScheduledActionsOperations` added method `cancel_next_occurrence`
  - Model `ScheduledActionsOperations` added method `detach_resources`
  - Model `ScheduledActionsOperations` added method `disable`
  - Model `ScheduledActionsOperations` added method `enable`
  - Model `ScheduledActionsOperations` added method `list_by_resource_group`
  - Model `ScheduledActionsOperations` added method `list_by_subscription`
  - Model `ScheduledActionsOperations` added method `list_resources`
  - Model `ScheduledActionsOperations` added method `patch_resources`
  - Model `ScheduledActionsOperations` added method `trigger_manual_occurrence`
  - Added operation group `OccurrenceExtensionOperations`
  - Added operation group `OccurrencesOperations`
  - Added operation group `ScheduledActionExtensionOperations`

## 1.1.0 (2025-06-05)

### Features Added

  - Added model `CreateResourceOperationResponse`
  - Added model `DeleteResourceOperationResponse`
  - Added model `ExecuteCreateRequest`
  - Added model `ExecuteDeleteRequest`
  - Added model `ResourceProvisionPayload`
  - Model `ScheduledActionsOperations` added method `virtual_machines_execute_create`
  - Model `ScheduledActionsOperations` added method `virtual_machines_execute_delete`

## 1.0.0 (2025-01-20)

### Features Added

  - Model `OperationErrorDetails` added property `timestamp`
  - Model `OperationErrorDetails` added property `azure_operation_name`
  - Model `ResourceOperationDetails` added property `timezone`
  - Model `Schedule` added property `deadline`
  - Model `Schedule` added property `timezone`

## 1.0.0b1 (2024-09-26)

### Other Changes

  - Initial version
