# Release History

## 1.0.0 (2023-11-20)

### Features Added

  - Added operation group VMInstanceGuestAgentsOperations
  - Added operation group VirtualMachineInstanceHybridIdentityMetadataOperations
  - Added operation group VirtualMachineInstancesOperations
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model VirtualMachineInventoryItem has a new parameter bios_guid
  - Model VirtualMachineInventoryItem has a new parameter managed_machine_resource_id
  - Model VirtualMachineInventoryItem has a new parameter os_version

### Breaking Changes

  - Operation AvailabilitySetsOperations.begin_create_or_update has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_create_or_update no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.begin_delete has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_delete no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.begin_update has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.begin_update no longer has parameter availability_set_name
  - Operation AvailabilitySetsOperations.get has a new required parameter availability_set_resource_name
  - Operation AvailabilitySetsOperations.get no longer has parameter availability_set_name
  - Operation CloudsOperations.begin_create_or_update has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_create_or_update no longer has parameter cloud_name
  - Operation CloudsOperations.begin_delete has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_delete no longer has parameter cloud_name
  - Operation CloudsOperations.begin_update has a new required parameter cloud_resource_name
  - Operation CloudsOperations.begin_update no longer has parameter cloud_name
  - Operation CloudsOperations.get has a new required parameter cloud_resource_name
  - Operation CloudsOperations.get no longer has parameter cloud_name
  - Operation InventoryItemsOperations.create has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.create no longer has parameter inventory_item_name
  - Operation InventoryItemsOperations.delete has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.delete no longer has parameter inventory_item_name
  - Operation InventoryItemsOperations.get has a new required parameter inventory_item_resource_name
  - Operation InventoryItemsOperations.get no longer has parameter inventory_item_name
  - Parameter extended_location of model AvailabilitySet is now required
  - Parameter location of model AvailabilitySet is now required
  - Removed operation group VirtualMachinesOperations

## 1.0.0b2 (2022-11-23)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b1 (2022-04-20)

* Initial Release
