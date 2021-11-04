# Release History

## 1.0.0b3 (2021-11-04)

**Features**

  - Model AccountUpdate has a new parameter identity
  - Model Instance has a new parameter diagnostic_storage_properties
  - Model Instance has a new parameter enable_diagnostics
  - Model Instance has a new parameter system_data
  - Model Account has a new parameter identity
  - Model Account has a new parameter system_data
  - Model Account has a new parameter public_network_access
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data
  - Model ErrorResponse has a new parameter error
  - Added operation InstancesOperations.head
  - Added operation AccountsOperations.head
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group DeviceUpdateOperationsMixin
  - Added operation group PrivateEndpointConnectionsOperations

**Breaking changes**

  - Model ErrorResponse no longer has parameter additional_info
  - Model ErrorResponse no longer has parameter message
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter target

## 1.0.0b2 (2021-03-24)

**Breaking changes**

  - Removed operation InstancesOperations.list_by_subscription
  - Model ErrorResponse has a new signature
  - Model ErrorDefinition has a new signature

## 1.0.0b1 (2021-03-02)

* Initial Release
