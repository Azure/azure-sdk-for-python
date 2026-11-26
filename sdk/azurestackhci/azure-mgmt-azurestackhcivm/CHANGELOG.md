# Release History

## 1.0.0b2 (2026-10-19)

### Features Added

  - Client `AzureStackHCIVmClient` added parameter `cloud_setting` in method `__init__`
  - Client `AzureStackHCIVmClient` added operation group `inbound_rules`
  - Client `AzureStackHCIVmClient` added operation group `load_balancers`
  - Client `AzureStackHCIVmClient` added operation group `nat_gateways`
  - Client `AzureStackHCIVmClient` added operation group `operations`
  - Client `AzureStackHCIVmClient` added operation group `public_ip_addresses`
  - Client `AzureStackHCIVmClient` added operation group `snapshots`
  - Client `AzureStackHCIVmClient` added operation group `virtual_network_subnets`
  - Client `AzureStackHCIVmClient` added operation group `virtual_networks`
  - Model `HardwareProfileUpdate` added property `dynamic_memory_config`
  - Enum `HyperVGeneration` added member `NA`
  - Model `LogicalNetworkProperties` added property `fabric_network_configuration`
  - Model `LogicalNetworkStatus` added property `fabric_integration`
  - Model `NetworkInterfaceProperties` added property `bypass_sdn_policies`
  - Model `NetworkInterfacesUpdateProperties` added property `bypass_sdn_policies`
  - Model `SubnetProperties` added property `provisioning_state`
  - Model `VirtualHardDiskProperties` added property `creation_data`
  - Model `VirtualHardDiskProperties` added property `local_vhd_path`
  - Model `VirtualMachineInstanceProperties` added property `local_vm_name`
  - Model `VirtualMachineInstancePropertiesHardwareProfileDynamicMemoryConfig` added property `enabled`
  - Model `VirtualMachineInstanceStatus` added property `operation_details`
  - Added enum `ActionType`
  - Added model `BackendAddressPool`
  - Added model `BackendAddressPoolProperties`
  - Added model `CreationData`
  - Added enum `DiskCreateOption`
  - Added enum `FabricConnectionHealthEnum`
  - Added enum `FabricIntegrationStateEnum`
  - Added model `FabricIntegrationStatus`
  - Added model `FabricIssue`
  - Added enum `FabricResourceTypeEnum`
  - Added model `FrontendIPConfiguration`
  - Added model `FrontendIPConfigurationProperties`
  - Added model `IPConfigurationArmReference`
  - Added enum `InboundNATRuleProtocol`
  - Added model `InboundRule`
  - Added model `InboundRuleProperties`
  - Added model `InboundRuleStatus`
  - Added model `InboundRuleStatusProvisioningStatus`
  - Added model `LoadBalancer`
  - Added model `LoadBalancerBackendAddress`
  - Added enum `LoadBalancerBackendAddressAdminState`
  - Added model `LoadBalancerBackendAddressPoolReference`
  - Added model `LoadBalancerBackendAddressProperties`
  - Added model `LoadBalancerFrontendIPConfigurationReference`
  - Added enum `LoadBalancerProbeProtocol`
  - Added model `LoadBalancerProbeReference`
  - Added model `LoadBalancerProperties`
  - Added model `LoadBalancerRule`
  - Added model `LoadBalancerRuleProperties`
  - Added enum `LoadBalancerRuleSessionPersistenceType`
  - Added enum `LoadBalancerRuleTransportProtocol`
  - Added model `LoadBalancerStatus`
  - Added model `LoadBalancerStatusProvisioningStatus`
  - Added model `LoadBalancerTagsUpdate`
  - Added model `ManagedNetworkFabricArmReference`
  - Added model `NatGateway`
  - Added model `NatGatewayArmReference`
  - Added model `NatGatewayProperties`
  - Added model `NatGatewayStatus`
  - Added model `NatGatewayStatusProvisioningStatus`
  - Added model `NatGatewayTagsUpdate`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added model `OperationStatusResult`
  - Added model `OperationStepResult`
  - Added enum `Origin`
  - Added model `PowerOffVirtualMachineOptions`
  - Added model `Probe`
  - Added model `ProbeProperties`
  - Added model `PublicIPAddress`
  - Added model `PublicIPAddressArmReference`
  - Added model `PublicIPAddressProperties`
  - Added model `PublicIPAddressTagsUpdate`
  - Added enum `PublicIPAddressType`
  - Added model `Snapshot`
  - Added model `SnapshotProperties`
  - Added model `SnapshotStatus`
  - Added model `SnapshotStatusProvisioningStatus`
  - Added model `SnapshotTagsUpdate`
  - Added model `VirtualNetwork`
  - Added model `VirtualNetworkAddressSpace`
  - Added model `VirtualNetworkArmReference`
  - Added model `VirtualNetworkDhcpOptions`
  - Added model `VirtualNetworkProperties`
  - Added model `VirtualNetworkStatus`
  - Added model `VirtualNetworkStatusProvisioningStatus`
  - Added model `VirtualNetworkSubnet`
  - Added model `VirtualNetworkSubnetArmReference`
  - Added model `VirtualNetworkSubnetIpConfigurationReference`
  - Added model `VirtualNetworkSubnetProperties`
  - Added model `VirtualNetworkSubnetStatus`
  - Added model `VirtualNetworkSubnetStatusProvisioningStatus`
  - Added model `VirtualNetworkSubnetUpdateProperties`
  - Added model `VirtualNetworkSubnetUpdateRequest`
  - Added model `VirtualNetworkTagsUpdate`
  - Operation group `VirtualMachineInstancesOperations` added method `begin_power_off`
  - Added operation group `InboundRulesOperations`
  - Added operation group `LoadBalancersOperations`
  - Added operation group `NatGatewaysOperations`
  - Added operation group `Operations`
  - Added operation group `PublicIPAddressesOperations`
  - Added operation group `SnapshotsOperations`
  - Added operation group `VirtualNetworkSubnetsOperations`
  - Added operation group `VirtualNetworksOperations`

### Breaking Changes

  - Model `GalleryImageProperties` deleted or renamed its instance variable `vm_image_repository_credentials`
  - Deleted or renamed model `VmImageRepositoryCredentials`

## 1.0.0b1 (2025-08-07)

### Other Changes

  - Initial version
