# Release History

## 1.0.0 (2024-10-22)

### Features Added

  - Model `ComputeProfile` added property `additional_virtual_machine_capabilities`
  - Model `FleetProperties` added property `vm_attributes`
  - Model `FleetProperties` added property `additional_locations_profile`
  - Enum `DiskControllerTypes` added member `NV_ME`
  - Enum `SecurityTypes` added member `CONFIDENTIAL_VM`
  - Enum `WindowsVMGuestPatchMode` added member `AUTOMATIC_BY_OS`
  - Added model `AdditionalCapabilities`
  - Added model `AdditionalLocationsProfile`
  - Added model `LocationProfile`
  - Added model `VMAttributeMinMaxDouble`
  - Added model `VMAttributeMinMaxInteger`
  - Added model `VMAttributes`
  - Added enum `AcceleratorManufacturer`
  - Added enum `AcceleratorType`
  - Added enum `ArchitectureType`
  - Added enum `CpuManufacturer`
  - Added enum `LocalStorageDiskType`
  - Added enum `VMAttributeSupport`
  - Added enum `VMCategory`

### Breaking Changes

  - Model `LinuxConfiguration` renamed its instance variable `provision_v_m_agent` into `provision_vm_agent`
  - Model `LinuxConfiguration` renamed its instance variable `enable_v_m_agent_platform_updates` into `enable_vm_agent_platform_updates`
  - Model `SpotPriorityProfile` renamed its instance variable `max_price_per_v_m` into `max_price_per_vm`
  - Model `VMSizeProperties` renamed its instance variable `v_c_p_us_available` into `v_cpus_available`
  - Model `VMSizeProperties` renamed its instance variable `v_c_p_us_per_core` into `v_cpus_per_core`
  - Model `VirtualMachineScaleSetDataDisk` renamed its instance variable `disk_size_g_b` into `disk_size_gb`
  - Model `VirtualMachineScaleSetDataDisk` renamed its instance variable `disk_i_o_p_s_read_write` into `disk_iops_read_write`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` renamed its instance variable `public_i_p_address_configuration` into `public_ip_address_configuration`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` renamed its instance variable `private_i_p_address_version` into `private_ip_address_version`
  - Model `VirtualMachineScaleSetNetworkConfigurationProperties` renamed its instance variable `enable_i_p_forwarding` into `enable_ip_forwarding`
  - Model `VirtualMachineScaleSetOSDisk` renamed its instance variable `disk_size_g_b` into `disk_size_gb`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` renamed its instance variable `public_i_p_prefix` into `public_ip_prefix`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` renamed its instance variable `public_i_p_address_version` into `public_ip_address_version`
  - Model `WindowsConfiguration` renamed its instance variable `provision_v_m_agent` into `provision_vm_agent`
  - Model `WindowsConfiguration` renamed its instance variable `win_r_m` into `win_rm`
  - Model `WindowsConfiguration` renamed its instance variable `enable_v_m_agent_platform_updates` into `enable_vm_agent_platform_updates`
  - Deleted or renamed enum value `DiskControllerTypes.N_V_ME`
  - Deleted or renamed enum value `NetworkApiVersion.ENUM_2020_11_01`
  - Deleted or renamed enum value `SecurityEncryptionTypes.DISK_WITH_V_M_GUEST_STATE`
  - Deleted or renamed enum value `SecurityEncryptionTypes.NON_PERSISTED_T_P_M`
  - Deleted or renamed enum value `SecurityEncryptionTypes.V_M_GUEST_STATE_ONLY`
  - Deleted or renamed enum value `SecurityTypes.CONFIDENTIAL_V_M`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_V2_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_Z_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_S_S_D_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_S_S_D_Z_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.ULTRA_S_S_D_L_R_S`
  - Deleted or renamed enum value `WindowsVMGuestPatchMode.AUTOMATIC_BY_O_S`

## 1.0.0b1 (2024-07-22)

### Other Changes

  - Initial version
