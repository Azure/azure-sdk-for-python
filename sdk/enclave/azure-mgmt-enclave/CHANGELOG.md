# Release History

## 2.0.0b1 (2026-11-20)

### Features Added

  - Model `CheckAddressSpaceAvailabilityRequest` added property `address_space`
  - Model `CheckAddressSpaceAvailabilityRequest` added property `prefix_length`
  - Model `CommunityEndpointDestinationRule` added property `direction`
  - Model `CommunityEndpointPatchProperties` added property `sync_to`
  - Model `CommunityEndpointProperties` added property `sync_destination_statuses`
  - Model `CommunityEndpointProperties` added property `sync_from`
  - Model `CommunityEndpointProperties` added property `sync_performed_by`
  - Model `CommunityEndpointProperties` added property `sync_status`
  - Model `CommunityEndpointProperties` added property `sync_to`
  - Model `CommunityPatchProperties` added property `subnet_join_policy_mode`
  - Model `CommunityProperties` added property `subnet_join_policy_mode`
  - Enum `DiagnosticDestination` added member `UNSPECIFIED`
  - Enum `EnclaveConnectionState` added member `DEGRADED`
  - Enum `EnclaveConnectionState` added member `RECONCILING`
  - Enum `ServiceIdentifier` added member `AZURE_LOCAL`
  - Model `SubnetConfiguration` added property `subnet_purpose`
  - Model `VirtualEnclavePatchProperties` added property `address_spaces`
  - Model `VirtualEnclavePatchProperties` added property `subnet_configurations`
  - Model `VirtualEnclaveProperties` added property `address_spaces`
  - Model `VirtualEnclaveProperties` added property `allow_subnet_communication`
  - Model `VirtualEnclaveProperties` added property `computed_address_spaces`
  - Model `VirtualEnclaveProperties` added property `network_name`
  - Model `VirtualEnclaveProperties` added property `subnet_configurations`
  - Added model `AddressSpaceEntry`
  - Added enum `AddressSpaceOwnership`
  - Added enum `ApprovalActionRequestApprovalStatus`
  - Added enum `ApprovalCallbackRequestApprovalStatus`
  - Added enum `ApprovalCallbackRequestResourceRequestAction`
  - Added enum `ApprovalDeletionCallbackRequestResourceRequestAction`
  - Added enum `CommunityPropertiesPolicyOverride`
  - Added model `ComputedAddressSpaceEntry`
  - Added enum `GovernedServiceItemEnforcement`
  - Added enum `GovernedServiceItemOption`
  - Added enum `GovernedServiceItemPolicyAction`
  - Added enum `MaintenanceModeConfigurationModelJustification`
  - Added enum `MaintenanceModeConfigurationModelMode`
  - Added enum `PrincipalType`
  - Added enum `RuleDirection`
  - Added enum `SubnetJoinPolicyMode`
  - Added enum `SubnetPurpose`
  - Added model `SyncDestinationStatus`
  - Added model `SyncPerformedBy`
  - Added enum `SyncStatus`
  - Operation group `CommunityEndpointsOperations` added method `begin_sync`

### Breaking Changes

  - Model `CheckAddressSpaceAvailabilityRequest` deleted or renamed its instance variable `enclave_virtual_network`
  - Model `VirtualEnclavePatchProperties` deleted or renamed its instance variable `enclave_virtual_network`
  - Model `VirtualEnclaveProperties` deleted or renamed its instance variable `enclave_address_spaces`
  - Model `VirtualEnclaveProperties` deleted or renamed its instance variable `enclave_virtual_network`
  - Deleted or renamed model `EnclaveVirtualNetworkModel`

### Other Changes

  - Deleted model `EnclaveAddressSpacesModel` which actually were not used by SDK users

## 1.0.0 (2026-08-27)

### Other Changes

  - First GA

## 1.0.0b1 (2026-07-17)

### Other Changes

  - Initial version
