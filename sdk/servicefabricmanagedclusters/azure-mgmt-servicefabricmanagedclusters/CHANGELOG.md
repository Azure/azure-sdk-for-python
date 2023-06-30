# Release History

## 2.0.0b4 (2023-05-20)

### Features Added

  - Model ManagedCluster has a new parameter use_custom_vnet
  - Model ManagedCluster has a new parameter zonal_update_mode
  - Model NodeType has a new parameter enable_node_public_ip
  - Model NodeType has a new parameter secure_boot_enabled
  - Model NodeType has a new parameter security_type
  - Model NodeType has a new parameter subnet_id
  - Model NodeType has a new parameter vm_setup_actions
  - Model NodeType has a new parameter vm_shared_gallery_image_id
  - Model NodeTypeActionParameters has a new parameter update_type
  - Model ServiceResourceProperties has a new parameter service_dns_name
  - Model StatefulServiceProperties has a new parameter service_dns_name
  - Model StatelessServiceProperties has a new parameter service_dns_name

### Breaking Changes

  - Parameter sku of model ManagedCluster is now required

## 2.0.0b3 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 2.0.0b2 (2022-09-14)

### Features Added

  - Model FrontendConfiguration has a new parameter application_gateway_backend_address_pool_id
  - Model NodeType has a new parameter eviction_policy
  - Model NodeType has a new parameter host_group_id
  - Model NodeType has a new parameter spot_restore_timeout
  - Model NodeType has a new parameter use_ephemeral_os_disk
  - Model NodeType has a new parameter vm_image_resource_id

## 2.0.0b1 (2022-06-02)

**Features**

  - Added operation group ManagedAzResiliencyStatusOperations
  - Added operation group ManagedUnsupportedVMSizesOperations
  - Added operation group NodeTypeSkusOperations
  - Added operation group OperationResultsOperations
  - Added operation group OperationStatusOperations
  - Model LoadBalancingRule has a new parameter load_distribution
  - Model ManagedCluster has a new parameter auxiliary_subnets
  - Model ManagedCluster has a new parameter enable_ipv6
  - Model ManagedCluster has a new parameter enable_service_public_ip
  - Model ManagedCluster has a new parameter ip_tags
  - Model ManagedCluster has a new parameter ipv6_address
  - Model ManagedCluster has a new parameter service_endpoints
  - Model ManagedCluster has a new parameter subnet_id
  - Model NetworkSecurityRule has a new parameter destination_address_prefix
  - Model NetworkSecurityRule has a new parameter destination_port_range
  - Model NetworkSecurityRule has a new parameter source_address_prefix
  - Model NetworkSecurityRule has a new parameter source_port_range
  - Model NodeType has a new parameter additional_data_disks
  - Model NodeType has a new parameter data_disk_letter
  - Model NodeType has a new parameter enable_accelerated_networking
  - Model NodeType has a new parameter enable_encryption_at_host
  - Model NodeType has a new parameter enable_over_provisioning
  - Model NodeType has a new parameter frontend_configurations
  - Model NodeType has a new parameter is_spot_vm
  - Model NodeType has a new parameter network_security_rules
  - Model NodeType has a new parameter sku
  - Model NodeType has a new parameter use_default_public_load_balancer
  - Model NodeType has a new parameter use_temp_data_disk
  - Model NodeType has a new parameter zones
  - Model NodeTypeUpdateParameters has a new parameter sku
  - Model VMSSExtension has a new parameter enable_automatic_upgrade

**Breaking changes**

  - Operation ManagedClusterVersionOperations.get_by_environment has a new parameter environment
  - Operation ManagedClusterVersionOperations.list_by_environment has a new parameter environment

## 1.0.0 (2021-04-27)

**Features**

  - Model ManagedCluster has a new parameter zonal_resiliency
  - Model ManagedCluster has a new parameter cluster_upgrade_mode
  - Model NodeType has a new parameter data_disk_type
  - Model NodeType has a new parameter multiple_placement_groups
  - Model NodeType has a new parameter is_stateless
  - Model LoadBalancingRule has a new parameter probe_port
  - Added operation group ManagedClusterVersionOperations

**Breaking changes**

  - Model StatelessServiceProperties no longer has parameter service_dns_name
  - Model StatelessServiceProperties no longer has parameter instance_close_delay_duration
  - Model ServiceResourceProperties no longer has parameter service_dns_name
  - Model AverageServiceLoadScalingTrigger has a new required parameter use_only_primary_load
  - Model StatefulServiceProperties no longer has parameter service_dns_name
  - Model StatefulServiceProperties no longer has parameter drop_source_replica_on_move

## 1.0.0b1 (2021-02-26)

* Initial Release
