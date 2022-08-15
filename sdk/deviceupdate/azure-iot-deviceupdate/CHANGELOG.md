# Release History

## 1.0.0b4 (Unreleased)

### Features Added
- Added filter to DeviceManagementOperations.list_device_classes method
- Updated description for some methods to be more descriptive and less ambiguous

### Breaking Changes
- Removed filter from DeviceManagementOperations.list_best_updates_for_group method

## 1.0.0b3 (2022-07-07)

### Features Added

- Added `relatedFiles` and `downloadHandler` to `Update`
- Updated various model that reference update to include not only `updateId` but also update `description` and `friendlyName`
- Removed device tag concept
- Allow to filter by deployment status in the `list_devices` method
- Added ability to update device class friendly name
- Added ability to delete device class
- Added device class subgroups to groups
- Added new method to retrieve devices health information

## 1.0.0b2 (2022-01-25)

### Features Added
    
  - Added DeviceManagementOperations
  - Added DeviceUpdateOperations
  - Added operation `send_request` to send customized http request conveniently
  - Added `client.device_management`

### Breaking Changes

  - Removed all models
  - Removed DeploymentsOperations
  - Removed UpdateOperations
  - Dropped support for Python2.7(https://github.com/Azure/azure-sdk-for-python#disclaimer)
  - Parameter `account_endpoint` of DeviceUpdateClient is renamed to `endpoint`
  - Renamed `client.updates` to `client.device_update`
  - Removed `client.devices`
  - Removed `client.deployments`
  - Renamed UpdatesOperations.get_update to DeviceUpdateOperations.get_update
  - Renamed UpdatesOperations.delete_update to DeviceUpdateOperations.begin_delete_update
  - Renamed UpdatesOperations.get_providers to DeviceUpdateOperations.list_providers
  - Renamed UpdatesOperations.get_names to DeviceUpdateOperations.list_names
  - Renamed UpdatesOperations.get_versions to DeviceUpdateOperations.list_versions
  - Renamed UpdatesOperations.get_file to DeviceUpdateOperations.get_file
  - Renamed UpdatesOperations.get_files to DeviceUpdateOperations.list_files
  - Renamed UpdatesOperations.get_operation to DeviceUpdateOperations.get_operation
  - Renamed UpdatesOperations.get_operations to DeviceUpdateOperations.list_operations
  - Renamed DevicesOperations.get_all_device_classes to DeviceManagementOperations.list_device_classes
  - Renamed DevicesOperations.get_device_class to DeviceManagementOperations.get_device_class
  - Renamed DevicesOperations.get_device_class_device_ids to DeviceManagementOperations.
  - Renamed DevicesOperations.list_devices to DeviceManagementOperations.list_devices
  - Renamed DevicesOperations.list_devices to DeviceManagementOperations.
  - Renamed DevicesOperations.get_all_device_tags to DeviceManagementOperations.list_device_tags
  - Renamed DevicesOperations.get_all_groups to DeviceManagementOperations.list_groups
  - Renamed DevicesOperations.get_group to DeviceManagementOperations.get_group
  - Renamed DevicesOperations.create_or_update_group to DeviceManagementOperations.create_or_update_group
  - Renamed DevicesOperations.delete_group to DeviceManagementOperations.delete_group
  - Renamed DevicesOperations.get_group_update_compliance to DeviceManagementOperations.get_group_update_compliance
  - Renamed DevicesOperations.get_group_best_updates to DeviceManagementOperations.list_best_updates_for_group
  - Renamed DeploymentsOperations.get_deployment_status to DeviceManagementOperations.get_deployment_status
  - Renamed DeploymentsOperations.create_or_update_deployment to DeviceManagementOperations.create_or_update_deployment
  - Renamed DeploymentsOperations.delete_deployment to DeviceManagementOperations.delete_deployment
  - Renamed DeploymentsOperations.get_deployment_devices to DeviceManagementOperations.list_deployment_devices

  
## 1.0.0b1 (2021-03-03)
* This is the initial release of Azure Device Update for IoT Hub library. 
