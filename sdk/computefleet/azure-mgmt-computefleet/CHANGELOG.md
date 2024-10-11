# Release History

## 1.0.0 (2024-10-21)

### Features Added

  - Model `ComputeProfile` added method `additional_virtual_machine_capabilities`
  - Model `ComputeProfile` added property `additional_virtual_machine_capabilities`
  - Enum `DiskControllerTypes` added member `NV_ME`
  - Model `FleetProperties` added method `additional_locations_profile`
  - Model `FleetProperties` added method `vm_attributes`
  - Model `FleetProperties` added property `vm_attributes`
  - Model `FleetProperties` added property `additional_locations_profile`
  - Model `LinuxConfiguration` added method `enable_vm_agent_platform_updates`
  - Model `LinuxConfiguration` added method `provision_vm_agent`
  - Model `LinuxConfiguration` added property `provision_vm_agent`
  - Model `LinuxConfiguration` added property `enable_vm_agent_platform_updates`
  - Enum `SecurityTypes` added member `CONFIDENTIAL_VM`
  - Model `SpotPriorityProfile` added method `max_price_per_vm`
  - Model `SpotPriorityProfile` added property `max_price_per_vm`
  - Model `VMSizeProperties` added method `v_cpus_available`
  - Model `VMSizeProperties` added method `v_cpus_per_core`
  - Model `VirtualMachineScaleSetDataDisk` added method `disk_iops_read_write`
  - Model `VirtualMachineScaleSetDataDisk` added method `disk_size_gb`
  - Model `VirtualMachineScaleSetDataDisk` added property `disk_size_gb`
  - Model `VirtualMachineScaleSetDataDisk` added property `disk_iops_read_write`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` added method `private_ip_address_version`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` added method `public_ip_address_configuration`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` added property `public_ip_address_configuration`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` added property `private_ip_address_version`
  - Model `VirtualMachineScaleSetNetworkConfigurationProperties` added method `enable_ip_forwarding`
  - Model `VirtualMachineScaleSetNetworkConfigurationProperties` added property `enable_ip_forwarding`
  - Model `VirtualMachineScaleSetOSDisk` added method `disk_size_gb`
  - Model `VirtualMachineScaleSetOSDisk` added property `disk_size_gb`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` added method `public_ip_address_version`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` added method `public_ip_prefix`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` added property `public_ip_prefix`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` added property `public_ip_address_version`
  - Model `WindowsConfiguration` added method `enable_vm_agent_platform_updates`
  - Model `WindowsConfiguration` added method `provision_vm_agent`
  - Model `WindowsConfiguration` added method `win_rm`
  - Model `WindowsConfiguration` added property `provision_vm_agent`
  - Model `WindowsConfiguration` added property `win_rm`
  - Model `WindowsConfiguration` added property `enable_vm_agent_platform_updates`
  - Enum `WindowsVMGuestPatchMode` added member `AUTOMATIC_BY_OS`
  - Added enum `AcceleratorManufacturer`
  - Added enum `AcceleratorType`
  - Added model `AdditionalCapabilities`
  - Added model `AdditionalLocationsProfile`
  - Added enum `ArchitectureType`
  - Added enum `CpuManufacturer`
  - Added enum `LocalStorageDiskType`
  - Added model `LocationProfile`
  - Added model `VMAttributeMinMaxDouble`
  - Added model `VMAttributeMinMaxInteger`
  - Added enum `VMAttributeSupport`
  - Added model `VMAttributes`
  - Added enum `VMCategory`

### Breaking Changes

  - Deleted or renamed enum value `DiskControllerTypes.N_V_ME`
  - Model `LinuxConfiguration` deleted or renamed its instance variable `provision_v_m_agent`
  - Model `LinuxConfiguration` deleted or renamed its instance variable `enable_v_m_agent_platform_updates`
  - Deleted or renamed method `LinuxConfiguration.enable_v_m_agent_platform_updates`
  - Deleted or renamed method `LinuxConfiguration.provision_v_m_agent`
  - Deleted or renamed enum value `NetworkApiVersion.ENUM_2020_11_01`
  - Deleted or renamed enum value `SecurityEncryptionTypes.DISK_WITH_V_M_GUEST_STATE`
  - Deleted or renamed enum value `SecurityEncryptionTypes.NON_PERSISTED_T_P_M`
  - Deleted or renamed enum value `SecurityEncryptionTypes.V_M_GUEST_STATE_ONLY`
  - Deleted or renamed enum value `SecurityTypes.CONFIDENTIAL_V_M`
  - Model `SpotPriorityProfile` deleted or renamed its instance variable `max_price_per_v_m`
  - Deleted or renamed method `SpotPriorityProfile.max_price_per_v_m`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_V2_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.PREMIUM_Z_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_S_S_D_L_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.STANDARD_S_S_D_Z_R_S`
  - Deleted or renamed enum value `StorageAccountTypes.ULTRA_S_S_D_L_R_S`
  - Model `VMSizeProperties` deleted or renamed its instance variable `v_c_p_us_available`
  - Model `VMSizeProperties` deleted or renamed its instance variable `v_c_p_us_per_core`
  - Deleted or renamed method `VMSizeProperties.v_c_p_us_available`
  - Deleted or renamed method `VMSizeProperties.v_c_p_us_per_core`
  - Model `VirtualMachineScaleSetDataDisk` deleted or renamed its instance variable `disk_size_g_b`
  - Model `VirtualMachineScaleSetDataDisk` deleted or renamed its instance variable `disk_i_o_p_s_read_write`
  - Deleted or renamed method `VirtualMachineScaleSetDataDisk.disk_i_o_p_s_read_write`
  - Deleted or renamed method `VirtualMachineScaleSetDataDisk.disk_size_g_b`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` deleted or renamed its instance variable `public_i_p_address_configuration`
  - Model `VirtualMachineScaleSetIPConfigurationProperties` deleted or renamed its instance variable `private_i_p_address_version`
  - Deleted or renamed method `VirtualMachineScaleSetIPConfigurationProperties.private_i_p_address_version`
  - Deleted or renamed method `VirtualMachineScaleSetIPConfigurationProperties.public_i_p_address_configuration`
  - Model `VirtualMachineScaleSetNetworkConfigurationProperties` deleted or renamed its instance variable `enable_i_p_forwarding`
  - Deleted or renamed method `VirtualMachineScaleSetNetworkConfigurationProperties.enable_i_p_forwarding`
  - Model `VirtualMachineScaleSetOSDisk` deleted or renamed its instance variable `disk_size_g_b`
  - Deleted or renamed method `VirtualMachineScaleSetOSDisk.disk_size_g_b`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` deleted or renamed its instance variable `public_i_p_prefix`
  - Model `VirtualMachineScaleSetPublicIPAddressConfigurationProperties` deleted or renamed its instance variable `public_i_p_address_version`
  - Deleted or renamed method `VirtualMachineScaleSetPublicIPAddressConfigurationProperties.public_i_p_address_version`
  - Deleted or renamed method `VirtualMachineScaleSetPublicIPAddressConfigurationProperties.public_i_p_prefix`
  - Model `WindowsConfiguration` deleted or renamed its instance variable `provision_v_m_agent`
  - Model `WindowsConfiguration` deleted or renamed its instance variable `win_r_m`
  - Model `WindowsConfiguration` deleted or renamed its instance variable `enable_v_m_agent_platform_updates`
  - Deleted or renamed method `WindowsConfiguration.enable_v_m_agent_platform_updates`
  - Deleted or renamed method `WindowsConfiguration.provision_v_m_agent`
  - Deleted or renamed method `WindowsConfiguration.win_r_m`
  - Deleted or renamed enum value `WindowsVMGuestPatchMode.AUTOMATIC_BY_O_S`

## 1.0.0b1 (2024-07-22)

### Other Changes

  - Initial version
