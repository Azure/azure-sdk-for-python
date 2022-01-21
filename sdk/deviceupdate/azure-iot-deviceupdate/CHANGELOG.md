# Release History

## 1.0.0b2 (2022-01-20)

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

  
## 1.0.0b1 (2021-03-03)
* This is the initial release of Azure Device Update for IoT Hub library. 
