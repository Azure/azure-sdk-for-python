# Release History

## 2.1.0b5 (2025-11-10)

### Features Added

  - Model `ServiceFabricManagedClustersManagementClient` added parameter `cloud_setting` in method `__init__`
  - Added model `ApplicationFetchHealthRequest`
  - Added enum `HealthFilter`
  - Added model `RestartDeployedCodePackageRequest`
  - Added enum `RestartKind`
  - Added model `RestartReplicaRequest`
  - Added model `RuntimeApplicationHealthPolicy`
  - Added enum `RuntimeFailureAction`
  - Added enum `RuntimeRollingUpgradeMode`
  - Added model `RuntimeRollingUpgradeUpdateMonitoringPolicy`
  - Added model `RuntimeServiceTypeHealthPolicy`
  - Added model `RuntimeUpdateApplicationUpgradeParameters`
  - Added enum `RuntimeUpgradeKind`
  - Model `ApplicationsOperations` added method `begin_fetch_health`
  - Model `ApplicationsOperations` added method `begin_restart_deployed_code_package`
  - Model `ApplicationsOperations` added method `begin_update_upgrade`
  - Model `ServicesOperations` added method `begin_restart_replica`

### Breaking Changes

  - Renamed method `ApplicationsOperations.update` to `ApplicationsOperations.begin_update`
  - Renamed method `ManagedClustersOperations.update` to `ManagedClustersOperations.begin_update`

## 2.1.0b4 (2025-08-14)

### Features Added

  - Model `ManagedClusterProperties` added property `enable_outbound_only_node_types`
  - Model `NodeTypeProperties` added property `is_outbound_only`
  - Model `ServiceEndpoint` added property `network_identifier`

## 2.1.0b3 (2025-06-26)

### Features Added

  - Enum `DiskType` added member `PREMIUM_V2_LRS`
  - Enum `DiskType` added member `PREMIUM_ZRS`
  - Enum `DiskType` added member `STANDARD_SSD_ZRS`
  - Model `ManagedClusterCodeVersionResult` added property `properties`
  - Enum `SecurityType` added member `CONFIDENTIAL_VM`
  - Added enum `CreatedByType`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added enum `FaultKind`
  - Added model `FaultSimulation`
  - Added model `FaultSimulationConstraints`
  - Added model `FaultSimulationContent`
  - Added model `FaultSimulationContentWrapper`
  - Added model `FaultSimulationDetails`
  - Added model `FaultSimulationIdContent`
  - Added enum `FaultSimulationStatus`
  - Added model `IPConfigurationPublicIPAddressConfiguration`
  - Added model `ManagedClusterVersionDetails`
  - Added model `NodeTypeFaultSimulation`
  - Added enum `SecurityEncryptionType`
  - Added enum `SfmcOperationStatus`
  - Added model `TrackedResource`
  - Added model `ZoneFaultSimulationContent`
  - Operation group `ManagedClustersOperations` added method `begin_start_fault_simulation`
  - Operation group `ManagedClustersOperations` added method `begin_stop_fault_simulation`
  - Operation group `ManagedClustersOperations` added method `get_fault_simulation`
  - Operation group `ManagedClustersOperations` added method `list_fault_simulation`
  - Operation group `NodeTypesOperations` added method `begin_deallocate`
  - Operation group `NodeTypesOperations` added method `begin_redeploy`
  - Operation group `NodeTypesOperations` added method `begin_start`
  - Operation group `NodeTypesOperations` added method `begin_start_fault_simulation`
  - Operation group `NodeTypesOperations` added method `begin_stop_fault_simulation`
  - Operation group `NodeTypesOperations` added method `get_fault_simulation`
  - Operation group `NodeTypesOperations` added method `list_fault_simulation`

### Breaking Changes

  - Model `ManagedClusterCodeVersionResult` deleted or renamed its instance variable `cluster_code_version`
  - Model `ManagedClusterCodeVersionResult` deleted or renamed its instance variable `support_expiry_utc`
  - Model `ManagedClusterCodeVersionResult` deleted or renamed its instance variable `os_type`
  - Model `ProxyResource` deleted or renamed its instance variable `location`
  - Model `ProxyResource` deleted or renamed its instance variable `tags`
  - Model `Resource` deleted or renamed its instance variable `location`
  - Model `Resource` deleted or renamed its instance variable `tags`
  - Model `Resource` deleted or renamed its instance variable `etag`
  - Deleted or renamed model `ApplicationResourceList`
  - Deleted or renamed model `ApplicationTypeResourceList`
  - Deleted or renamed model `ApplicationTypeVersionResourceList`
  - Deleted or renamed model `ErrorModel`
  - Deleted or renamed model `IpConfigurationPublicIPAddressConfiguration`
  - Deleted or renamed model `ManagedProxyResource`
  - Deleted or renamed model `ManagedVMSizesResult`
  - Deleted or renamed model `NodeTypeListSkuResult`
  - Deleted or renamed model `ServiceResourceList`
  - Deleted or renamed model `UpgradeMode`

## 2.1.0b2 (2024-12-16)

### Features Added

  - Model `ManagedCluster` added property `allocated_outbound_ports`
  - Operation group `NodeTypesOperations` added method `begin_update`

### Breaking Changes

  - Model `ManagedCluster` deleted or renamed its instance variable `custom_fqdn`
  - Deleted or renamed method `NodeTypesOperations.update`

## 2.1.0b1 (2024-10-21)

### Features Added

  - Model `ManagedCluster` added property `auto_generated_domain_name_label_scope`
  - Model `ManagedCluster` added property `custom_fqdn`
  - Model `NodeType` added property `vm_applications`
  - Added enum `AutoGeneratedDomainNameLabelScope`
  - Added model `VmApplication`

## 2.0.0 (2024-07-22)

### Features Added

  - Added operation ApplicationsOperations.begin_read_upgrade
  - Added operation ApplicationsOperations.begin_resume_upgrade
  - Added operation ApplicationsOperations.begin_start_rollback
  - Added operation group ManagedApplyMaintenanceWindowOperations
  - Added operation group ManagedAzResiliencyStatusOperations
  - Added operation group ManagedMaintenanceWindowStatusOperations
  - Added operation group ManagedUnsupportedVMSizesOperations
  - Added operation group NodeTypeSkusOperations
  - Added operation group OperationResultsOperations
  - Added operation group OperationStatusOperations
  - Model LoadBalancingRule has a new parameter load_distribution
  - Model ManagedCluster has a new parameter auxiliary_subnets
  - Model ManagedCluster has a new parameter ddos_protection_plan_id
  - Model ManagedCluster has a new parameter enable_http_gateway_exclusive_auth_mode
  - Model ManagedCluster has a new parameter enable_ipv6
  - Model ManagedCluster has a new parameter enable_service_public_ip
  - Model ManagedCluster has a new parameter http_gateway_token_auth_connection_port
  - Model ManagedCluster has a new parameter ip_tags
  - Model ManagedCluster has a new parameter ipv6_address
  - Model ManagedCluster has a new parameter public_i_pv6_prefix_id
  - Model ManagedCluster has a new parameter public_ip_prefix_id
  - Model ManagedCluster has a new parameter service_endpoints
  - Model ManagedCluster has a new parameter subnet_id
  - Model ManagedCluster has a new parameter upgrade_description
  - Model ManagedCluster has a new parameter use_custom_vnet
  - Model ManagedCluster has a new parameter zonal_update_mode
  - Model NetworkSecurityRule has a new parameter destination_address_prefix
  - Model NetworkSecurityRule has a new parameter destination_port_range
  - Model NetworkSecurityRule has a new parameter source_address_prefix
  - Model NetworkSecurityRule has a new parameter source_port_range
  - Model NodeType has a new parameter additional_data_disks
  - Model NodeType has a new parameter additional_network_interface_configurations
  - Model NodeType has a new parameter computer_name_prefix
  - Model NodeType has a new parameter data_disk_letter
  - Model NodeType has a new parameter dscp_configuration_id
  - Model NodeType has a new parameter enable_accelerated_networking
  - Model NodeType has a new parameter enable_encryption_at_host
  - Model NodeType has a new parameter enable_node_public_i_pv6
  - Model NodeType has a new parameter enable_node_public_ip
  - Model NodeType has a new parameter enable_over_provisioning
  - Model NodeType has a new parameter eviction_policy
  - Model NodeType has a new parameter frontend_configurations
  - Model NodeType has a new parameter host_group_id
  - Model NodeType has a new parameter is_spot_vm
  - Model NodeType has a new parameter nat_configurations
  - Model NodeType has a new parameter nat_gateway_id
  - Model NodeType has a new parameter network_security_rules
  - Model NodeType has a new parameter secure_boot_enabled
  - Model NodeType has a new parameter security_type
  - Model NodeType has a new parameter service_artifact_reference_id
  - Model NodeType has a new parameter sku
  - Model NodeType has a new parameter spot_restore_timeout
  - Model NodeType has a new parameter subnet_id
  - Model NodeType has a new parameter use_default_public_load_balancer
  - Model NodeType has a new parameter use_ephemeral_os_disk
  - Model NodeType has a new parameter use_temp_data_disk
  - Model NodeType has a new parameter vm_image_plan
  - Model NodeType has a new parameter vm_image_resource_id
  - Model NodeType has a new parameter vm_setup_actions
  - Model NodeType has a new parameter vm_shared_gallery_image_id
  - Model NodeType has a new parameter zones
  - Model NodeTypeActionParameters has a new parameter update_type
  - Model NodeTypeUpdateParameters has a new parameter sku
  - Model ServiceResourceProperties has a new parameter service_dns_name
  - Model StatefulServiceProperties has a new parameter service_dns_name
  - Model StatelessServiceProperties has a new parameter service_dns_name
  - Model VMSSExtension has a new parameter enable_automatic_upgrade
  - Model VMSSExtension has a new parameter setup_order

### Breaking Changes

  - Operation ManagedClusterVersionOperations.get_by_environment has a new required parameter environment
  - Operation ManagedClusterVersionOperations.list_by_environment has a new required parameter environment
  - Parameter sku of model ManagedCluster is now required

## 2.0.0b6 (2024-02-22)

### Features Added

  - Model ManagedCluster has a new parameter enable_http_gateway_exclusive_auth_mode
  - Model ManagedCluster has a new parameter http_gateway_token_auth_connection_port

## 2.0.0b5 (2024-01-18)

### Features Added

  - Added operation ApplicationsOperations.begin_read_upgrade
  - Added operation ApplicationsOperations.begin_resume_upgrade
  - Added operation ApplicationsOperations.begin_start_rollback
  - Added operation group ManagedApplyMaintenanceWindowOperations
  - Added operation group ManagedMaintenanceWindowStatusOperations
  - Model ManagedCluster has a new parameter ddos_protection_plan_id
  - Model ManagedCluster has a new parameter public_i_pv6_prefix_id
  - Model ManagedCluster has a new parameter public_ip_prefix_id
  - Model ManagedCluster has a new parameter upgrade_description
  - Model NodeType has a new parameter additional_network_interface_configurations
  - Model NodeType has a new parameter dscp_configuration_id
  - Model NodeType has a new parameter enable_node_public_i_pv6
  - Model NodeType has a new parameter nat_gateway_id
  - Model NodeType has a new parameter service_artifact_reference_id
  - Model NodeType has a new parameter vm_image_plan
  - Model VMSSExtension has a new parameter setup_order

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
