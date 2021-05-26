# Release History

## 1.0.0 (2021-05-26)

**Features**

  - Model DedicatedCloudNode has a new parameter id_properties_sku_description_id
  - Model DedicatedCloudNode has a new parameter name_properties_sku_description_name
  - Model PrivateCloud has a new parameter type_properties_type
  - Model CustomizationPolicy has a new parameter type_properties_type
  - Added operation DedicatedCloudNodesOperations.begin_create_or_update
  - Added operation DedicatedCloudServicesOperations.begin_delete
  - Added operation VirtualMachinesOperations.begin_start
  - Added operation VirtualMachinesOperations.begin_create_or_update
  - Added operation VirtualMachinesOperations.begin_stop
  - Added operation VirtualMachinesOperations.begin_delete
  - Added operation VirtualMachinesOperations.begin_update

**Breaking changes**

  - Operation CustomizationPoliciesOperations.get has a new signature
  - Operation CustomizationPoliciesOperations.list has a new signature
  - Operation DedicatedCloudNodesOperations.delete has a new signature
  - Operation DedicatedCloudNodesOperations.get has a new signature
  - Operation DedicatedCloudNodesOperations.list_by_resource_group has a new signature
  - Operation DedicatedCloudNodesOperations.list_by_subscription has a new signature
  - Operation DedicatedCloudServicesOperations.create_or_update has a new signature
  - Operation DedicatedCloudServicesOperations.get has a new signature
  - Operation DedicatedCloudServicesOperations.list_by_resource_group has a new signature
  - Operation DedicatedCloudServicesOperations.list_by_subscription has a new signature
  - Operation Operations.get has a new signature
  - Operation PrivateCloudsOperations.get has a new signature
  - Operation PrivateCloudsOperations.list has a new signature
  - Operation ResourcePoolsOperations.get has a new signature
  - Operation ResourcePoolsOperations.list has a new signature
  - Operation SkusAvailabilityOperations.list has a new signature
  - Operation UsagesOperations.list has a new signature
  - Operation VirtualMachineTemplatesOperations.get has a new signature
  - Operation VirtualMachineTemplatesOperations.list has a new signature
  - Operation VirtualNetworksOperations.get has a new signature
  - Operation VirtualNetworksOperations.list has a new signature
  - Operation DedicatedCloudNodesOperations.update has a new signature
  - Operation Operations.list has a new signature
  - Operation DedicatedCloudServicesOperations.update has a new signature
  - Model DedicatedCloudNode no longer has parameter name1
  - Model DedicatedCloudNode no longer has parameter id1
  - Model PrivateCloud no longer has parameter private_cloud_properties_type
  - Model CustomizationPolicy no longer has parameter customization_policy_properties_type
  - Removed operation DedicatedCloudNodesOperations.create_or_update
  - Removed operation DedicatedCloudServicesOperations.delete
  - Removed operation VirtualMachinesOperations.stop
  - Removed operation VirtualMachinesOperations.create_or_update
  - Removed operation VirtualMachinesOperations.start
  - Removed operation VirtualMachinesOperations.delete
  - Removed operation VirtualMachinesOperations.update

## 0.1.0 (1970-01-01)

* Initial Release
