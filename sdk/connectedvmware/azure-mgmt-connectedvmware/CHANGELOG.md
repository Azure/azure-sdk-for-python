# Release History

## 1.0.0 (2023-10-23)

### Features Added

  - Added operation group VMInstanceGuestAgentsOperations
  - Added operation group VirtualMachineInstancesOperations
  - Added operation group VmInstanceHybridIdentityMetadataOperations
  - Model Cluster has a new parameter total_cpu_m_hz
  - Model Cluster has a new parameter total_memory_gb
  - Model Cluster has a new parameter used_cpu_m_hz
  - Model Cluster has a new parameter used_memory_gb
  - Model GuestAgent has a new parameter private_link_scope_resource_id
  - Model Host has a new parameter cpu_mhz
  - Model Host has a new parameter memory_size_gb
  - Model Host has a new parameter overall_cpu_usage_m_hz
  - Model Host has a new parameter overall_memory_usage_gb
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model ResourcePool has a new parameter cpu_capacity_m_hz
  - Model ResourcePool has a new parameter cpu_overall_usage_m_hz
  - Model ResourcePool has a new parameter mem_capacity_gb
  - Model ResourcePool has a new parameter mem_overall_usage_gb

### Breaking Changes

  - Client name is changed from `AzureArcVMwareManagementServiceAPI` to `ConnectedVMwareMgmtClient`
  - Removed operation group AzureArcVMwareManagementServiceAPIOperationsMixin
  - Removed operation group GuestAgentsOperations
  - Removed operation group HybridIdentityMetadataOperations
  - Removed operation group MachineExtensionsOperations
  - Removed operation group VirtualMachinesOperations

## 1.0.0b3 (2022-12-26)

### Features Added

  - Added operation GuestAgentsOperations.list
  - Added operation HybridIdentityMetadataOperations.list
  - Added operation VirtualMachinesOperations.begin_create_or_update
  - Added operation VirtualMachinesOperations.list_all
  - Added operation group AzureArcVMwareManagementServiceAPIOperationsMixin
  - Model Datastore has a new parameter capacity_gb
  - Model Datastore has a new parameter free_space_gb
  - Model ErrorDetail has a new parameter additional_info
  - Model GuestAgentProfile has a new parameter client_public_key
  - Model GuestAgentProfile has a new parameter mssql_discovered
  - Model Host has a new parameter datastore_ids
  - Model Host has a new parameter network_ids
  - Model InventoryItemDetails has a new parameter inventory_type
  - Model ResourcePool has a new parameter datastore_ids
  - Model ResourcePool has a new parameter network_ids
  - Model VirtualMachineInventoryItem has a new parameter cluster
  - Model VirtualMachineTemplateInventoryItem has a new parameter tools_version
  - Model VirtualMachineTemplateInventoryItem has a new parameter tools_version_status
  - Model VirtualMachineUpdate has a new parameter guest_agent_profile

### Breaking Changes

  - Operation MachineExtensionsOperations.begin_create_or_update has a new required parameter virtual_machine_name
  - Operation MachineExtensionsOperations.begin_create_or_update no longer has parameter name
  - Operation MachineExtensionsOperations.begin_delete has a new required parameter virtual_machine_name
  - Operation MachineExtensionsOperations.begin_delete no longer has parameter name
  - Operation MachineExtensionsOperations.begin_update has a new required parameter virtual_machine_name
  - Operation MachineExtensionsOperations.begin_update no longer has parameter name
  - Operation MachineExtensionsOperations.get has a new required parameter virtual_machine_name
  - Operation MachineExtensionsOperations.get no longer has parameter name
  - Operation MachineExtensionsOperations.list has a new required parameter virtual_machine_name
  - Operation MachineExtensionsOperations.list no longer has parameter name
  - Operation VirtualMachinesOperations.begin_assess_patches has a new required parameter virtual_machine_name
  - Operation VirtualMachinesOperations.begin_assess_patches no longer has parameter name
  - Operation VirtualMachinesOperations.begin_install_patches has a new required parameter virtual_machine_name
  - Operation VirtualMachinesOperations.begin_install_patches no longer has parameter name
  - Operation VirtualMachinesOperations.list has a new required parameter resource_group_name
  - Removed operation GuestAgentsOperations.list_by_vm
  - Removed operation HybridIdentityMetadataOperations.list_by_vm
  - Removed operation VirtualMachinesOperations.begin_create
  - Removed operation VirtualMachinesOperations.list_by_resource_group

## 1.0.0b2 (2022-08-15)

**Features**

  - Added operation VirtualMachinesOperations.begin_assess_patches
  - Added operation VirtualMachinesOperations.begin_install_patches
  - Model MachineExtension has a new parameter enable_automatic_upgrade
  - Model MachineExtensionUpdate has a new parameter enable_automatic_upgrade
  - Model OsProfile has a new parameter allow_extension_operations
  - Model OsProfile has a new parameter guest_id
  - Model OsProfile has a new parameter linux_configuration
  - Model OsProfile has a new parameter windows_configuration
  - Model VirtualMachine has a new parameter security_profile
  - Model VirtualMachineUpdate has a new parameter os_profile

**Breaking changes**

  - Operation VirtualMachinesOperations.begin_delete has a new parameter retain

## 1.0.0b1 (2021-11-19)

* Initial Release
