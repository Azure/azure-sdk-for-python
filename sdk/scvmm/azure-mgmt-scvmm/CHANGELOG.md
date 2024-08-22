# Release History

## 1.0.0 (2024-06-20)

### Features Added

  - Added operation group GuestAgentsOperations
  - Added operation group VirtualMachineInstancesOperations
  - Added operation group VmInstanceHybridIdentityMetadatasOperations
  - Model AvailabilitySet has a new parameter properties
  - Model Cloud has a new parameter properties
  - Model InventoryItem has a new parameter properties
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model VirtualDisk has a new parameter storage_qos_policy
  - Model VirtualDiskUpdate has a new parameter storage_qos_policy
  - Model VirtualMachineInventoryItem has a new parameter bios_guid
  - Model VirtualMachineInventoryItem has a new parameter managed_machine_resource_id
  - Model VirtualMachineInventoryItem has a new parameter os_version
  - Model VirtualMachineTemplate has a new parameter properties
  - Model VirtualNetwork has a new parameter properties

### Breaking Changes

  - Client name is changed from `SCVMM` to `ScVmmMgmtClient`
  - Model AvailabilitySet no longer has parameter availability_set_name
  - Model AvailabilitySet no longer has parameter provisioning_state
  - Model AvailabilitySet no longer has parameter vmm_server_id
  - Model Cloud no longer has parameter cloud_capacity
  - Model Cloud no longer has parameter cloud_name
  - Model Cloud no longer has parameter inventory_item_id
  - Model Cloud no longer has parameter provisioning_state
  - Model Cloud no longer has parameter storage_qo_s_policies
  - Model Cloud no longer has parameter uuid
  - Model Cloud no longer has parameter vmm_server_id
  - Model InventoryItem no longer has parameter inventory_item_name
  - Model InventoryItem no longer has parameter inventory_type
  - Model InventoryItem no longer has parameter managed_resource_id
  - Model InventoryItem no longer has parameter provisioning_state
  - Model InventoryItem no longer has parameter uuid
  - Model VirtualDisk no longer has parameter storage_qo_s_policy
  - Model VirtualDiskUpdate no longer has parameter storage_qo_s_policy
  - Model VirtualMachineTemplate no longer has parameter computer_name
  - Model VirtualMachineTemplate no longer has parameter cpu_count
  - Model VirtualMachineTemplate no longer has parameter disks
  - Model VirtualMachineTemplate no longer has parameter dynamic_memory_enabled
  - Model VirtualMachineTemplate no longer has parameter dynamic_memory_max_mb
  - Model VirtualMachineTemplate no longer has parameter dynamic_memory_min_mb
  - Model VirtualMachineTemplate no longer has parameter generation
  - Model VirtualMachineTemplate no longer has parameter inventory_item_id
  - Model VirtualMachineTemplate no longer has parameter is_customizable
  - Model VirtualMachineTemplate no longer has parameter is_highly_available
  - Model VirtualMachineTemplate no longer has parameter limit_cpu_for_migration
  - Model VirtualMachineTemplate no longer has parameter memory_mb
  - Model VirtualMachineTemplate no longer has parameter network_interfaces
  - Model VirtualMachineTemplate no longer has parameter os_name
  - Model VirtualMachineTemplate no longer has parameter os_type
  - Model VirtualMachineTemplate no longer has parameter provisioning_state
  - Model VirtualMachineTemplate no longer has parameter uuid
  - Model VirtualMachineTemplate no longer has parameter vmm_server_id
  - Model VirtualNetwork no longer has parameter inventory_item_id
  - Model VirtualNetwork no longer has parameter network_name
  - Model VirtualNetwork no longer has parameter provisioning_state
  - Model VirtualNetwork no longer has parameter uuid
  - Model VirtualNetwork no longer has parameter vmm_server_id
  - Operation AvailabilitySetsOperations.begin_create_or_update has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_create_or_update has a new required parameter resource
  - Operation AvailabilitySetsOperations.begin_create_or_update no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.begin_create_or_update no longer has parameter body
  - Operation AvailabilitySetsOperations.begin_delete has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_delete no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.begin_update has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_update has a new required parameter properties
  - Operation AvailabilitySetsOperations.begin_update no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.begin_update no longer has parameter body
  - Operation AvailabilitySetsOperations.get has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.get no longer has parameter availability_set_name
  - Operation CloudsOperations.begin_create_or_update has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_create_or_update has a new required parameter resource
  - Operation CloudsOperations.begin_create_or_update no longer has parameter body
  - Operation CloudsOperations.begin_create_or_update no longer has parameter cloud_name
  - Operation CloudsOperations.begin_delete has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_delete no longer has parameter cloud_name
  - Operation CloudsOperations.begin_update has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_update has a new required parameter properties
  - Operation CloudsOperations.begin_update no longer has parameter body
  - Operation CloudsOperations.begin_update no longer has parameter cloud_name
  - Operation CloudsOperations.get has a new required parameter cloud_resource_name
  - Operation CloudsOperations.get no longer has parameter cloud_name
  - Operation InventoryItemsOperations.create has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.create has a new required parameter resource
  - Operation InventoryItemsOperations.create no longer has parameter body
  - Operation InventoryItemsOperations.create no longer has parameter inventory_item_name
  - Operation InventoryItemsOperations.delete has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.delete no longer has parameter inventory_item_name
  - Operation InventoryItemsOperations.get has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.get no longer has parameter inventory_item_name
  - Operation VirtualMachineTemplatesOperations.begin_create_or_update has a new required parameter resource
  - Operation VirtualMachineTemplatesOperations.begin_create_or_update no longer has parameter body
  - Operation VirtualMachineTemplatesOperations.begin_update has a new required parameter properties
  - Operation VirtualMachineTemplatesOperations.begin_update no longer has parameter body
  - Operation VirtualNetworksOperations.begin_create_or_update has a new required parameter resource
  - Operation VirtualNetworksOperations.begin_create_or_update no longer has parameter body
  - Operation VirtualNetworksOperations.begin_update has a new required parameter properties
  - Operation VirtualNetworksOperations.begin_update no longer has parameter body
  - Operation VmmServersOperations.begin_create_or_update has a new required parameter resource
  - Operation VmmServersOperations.begin_create_or_update no longer has parameter body
  - Operation VmmServersOperations.begin_update has a new required parameter properties
  - Operation VmmServersOperations.begin_update no longer has parameter body
  - Parameter extended_location of model AvailabilitySet is now required
  - Parameter location of model AvailabilitySet is now required
  - Parameter value of model AvailabilitySetListResult is now required
  - Parameter value of model CloudListResult is now required
  - Parameter value of model VirtualMachineTemplateListResult is now required
  - Parameter value of model VirtualNetworkListResult is now required
  - Removed operation group VirtualMachinesOperations

## 1.0.0b2 (2022-11-23)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b1 (2022-04-20)

* Initial Release
