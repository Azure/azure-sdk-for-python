# Release History

## 1.0.0 (2023-08-18)

### Breaking Changes

  - Removed operation BareMetalMachinesOperations.begin_validate_hardware
  - Removed operation StorageAppliancesOperations.begin_run_read_commands
  - Removed operation VirtualMachinesOperations.begin_attach_volume
  - Removed operation VirtualMachinesOperations.begin_detach_volume

## 1.0.0b2 (2023-07-19)

### Features Added

  - Added operation BareMetalMachineKeySetsOperations.list_by_cluster
  - Added operation BmcKeySetsOperations.list_by_cluster
  - Added operation ConsolesOperations.list_by_virtual_machine
  - Added operation MetricsConfigurationsOperations.list_by_cluster
  - Added operation group AgentPoolsOperations
  - Added operation group KubernetesClustersOperations
  - Model BareMetalMachine has a new parameter associated_resource_ids
  - Model CloudServicesNetwork has a new parameter associated_resource_ids
  - Model L2Network has a new parameter associated_resource_ids
  - Model L3Network has a new parameter associated_resource_ids
  - Model TrunkedNetwork has a new parameter associated_resource_ids
  - Model VirtualMachine has a new parameter availability_zone

### Breaking Changes

  - Removed operation BareMetalMachineKeySetsOperations.list_by_resource_group
  - Removed operation BmcKeySetsOperations.list_by_resource_group
  - Removed operation ConsolesOperations.list_by_resource_group
  - Removed operation MetricsConfigurationsOperations.list_by_resource_group
  - Removed operation StorageAppliancesOperations.begin_validate_hardware
  - Removed operation group DefaultCniNetworksOperations
  - Removed operation group HybridAksClustersOperations

## 1.0.0b1 (2023-05-19)

* Initial Release
