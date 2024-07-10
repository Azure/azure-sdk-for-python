# Release History

## 3.3.0 (2024-06-17)

### Features Added

  - Added operation MobileNetworksOperations.list_sim_groups
  - Added operation SimsOperations.begin_clone
  - Added operation SimsOperations.begin_move
  - Added operation group RoutingInfoOperations
  - Model InterfaceProperties has a new parameter bfd_ipv4_endpoints
  - Model InterfaceProperties has a new parameter ipv4_address_list
  - Model InterfaceProperties has a new parameter vlan_id
  - Model PacketCoreControlPlane has a new parameter user_consent
  - Model Platform has a new parameter ha_upgrades_available
  - Model SignalingConfiguration has a new parameter nas_encryption

## 3.2.0 (2024-03-18)

### Features Added

  - Added operation group ExtendedUeInformationOperations
  - Added operation group UeInformationOperations
  - Model MobileNetwork has a new parameter identity
  - Model MobileNetwork has a new parameter public_land_mobile_networks
  - Model PacketCoreControlPlane has a new parameter home_network_private_keys_provisioning

## 3.1.0 (2023-11-20)

### Features Added

  - Model PacketCapture has a new parameter output_files
  - Model PacketCoreControlPlane has a new parameter control_plane_access_virtual_ipv4_addresses
  - Model PacketCoreControlPlane has a new parameter event_hub
  - Model PacketCoreControlPlane has a new parameter signaling
  - Model PacketCoreDataPlane has a new parameter user_plane_access_virtual_ipv4_addresses

## 3.0.0 (2023-07-21)

### Features Added

  - Added operation PacketCoreControlPlaneVersionsOperations.get_by_subscription
  - Added operation PacketCoreControlPlaneVersionsOperations.list_by_subscription
  - Added operation SitesOperations.begin_delete_packet_core
  - Added operation group DiagnosticsPackagesOperations
  - Added operation group PacketCapturesOperations
  - Model Installation has a new parameter desired_state
  - Model Installation has a new parameter reasons
  - Model Installation has a new parameter reinstall_required
  - Model PacketCoreControlPlane has a new parameter diagnostics_upload
  - Model PacketCoreControlPlane has a new parameter installed_version

### Breaking Changes

  - Model ManagedServiceIdentity no longer has parameter principal_id
  - Model ManagedServiceIdentity no longer has parameter tenant_id

## 2.0.0 (2023-01-16)

### Features Added

  - Added operation PacketCoreControlPlanesOperations.begin_collect_diagnostics_package
  - Added operation PacketCoreControlPlanesOperations.begin_reinstall
  - Added operation PacketCoreControlPlanesOperations.begin_rollback
  - Added operation SimsOperations.begin_bulk_delete
  - Added operation SimsOperations.begin_bulk_upload
  - Added operation SimsOperations.begin_bulk_upload_encrypted

### Breaking Changes

  - Removed operation group PacketCoreControlPlaneOperations
  - Removed operation group SimOperations

## 1.0.0 (2022-12-15)

### Features Added

  - Added operation PacketCoreControlPlaneVersionsOperations.list
  - Added operation SimsOperations.list_by_group
  - Added operation group PacketCoreControlPlaneOperations
  - Added operation group SimOperations
  - Model DataNetworkConfiguration has a new parameter maximum_number_of_buffered_packets
  - Model PacketCoreControlPlane has a new parameter installation
  - Model PacketCoreControlPlane has a new parameter rollback_version
  - Model PacketCoreControlPlane has a new parameter ue_mtu
  - Model PacketCoreControlPlaneVersion has a new parameter platforms
  - Model PlatformConfiguration has a new parameter azure_stack_edge_devices
  - Model PlatformConfiguration has a new parameter azure_stack_hci_cluster
  - Model Sim has a new parameter site_provisioning_state
  - Model Sim has a new parameter vendor_key_fingerprint
  - Model Sim has a new parameter vendor_name
  - Model SimPolicy has a new parameter site_provisioning_state

### Breaking Changes

  - Model LocalDiagnosticsAccessConfiguration has a new required parameter authentication_type
  - Model PacketCoreControlPlane has a new required parameter sites
  - Model PacketCoreControlPlane no longer has parameter mobile_network
  - Model PacketCoreControlPlaneVersion no longer has parameter recommended_version
  - Model PacketCoreControlPlaneVersion no longer has parameter version_state
  - Parameter dns_addresses of model AttachedDataNetwork is now required
  - Parameter local_diagnostics_access of model PacketCoreControlPlane is now required
  - Parameter platform of model PacketCoreControlPlane is now required
  - Removed operation MobileNetworksOperations.begin_list_sim_ids
  - Removed operation PacketCoreControlPlaneVersionsOperations.list_by_resource_group
  - Removed operation SimsOperations.list_by_sim_group

## 1.0.0b3 (2022-08-01)

**Features**

  - Added operation SimsOperations.list_by_sim_group
  - Added operation group PacketCoreControlPlaneVersionsOperations
  - Added operation group SimGroupsOperations
  - Model AttachedDataNetwork has a new parameter dns_addresses
  - Model PacketCoreControlPlane has a new parameter identity
  - Model PacketCoreControlPlane has a new parameter interop_settings
  - Model PacketCoreControlPlane has a new parameter local_diagnostics_access
  - Model PacketCoreControlPlane has a new parameter platform

**Breaking changes**

  - Model PacketCoreControlPlane has a new required parameter sku
  - Model PacketCoreControlPlane no longer has parameter custom_location
  - Model Sim no longer has parameter location
  - Model Sim no longer has parameter mobile_network
  - Model Sim no longer has parameter tags
  - Operation SimsOperations.begin_create_or_update has a new parameter sim_group_name
  - Operation SimsOperations.begin_delete has a new parameter sim_group_name
  - Operation SimsOperations.get has a new parameter sim_group_name
  - Removed operation SimsOperations.list_by_resource_group
  - Removed operation SimsOperations.list_by_subscription
  - Removed operation SimsOperations.update_tags

## 1.0.0b2 (2022-04-02)

**Features**

  - Model AttachedDataNetwork has a new parameter system_data
  - Model DataNetwork has a new parameter system_data
  - Model InterfaceProperties has a new parameter ipv4_address
  - Model InterfaceProperties has a new parameter ipv4_gateway
  - Model InterfaceProperties has a new parameter ipv4_subnet
  - Model MobileNetwork has a new parameter system_data
  - Model PacketCoreControlPlane has a new parameter system_data
  - Model PacketCoreDataPlane has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model Service has a new parameter system_data
  - Model Sim has a new parameter sim_state
  - Model Sim has a new parameter system_data
  - Model SimPolicy has a new parameter system_data
  - Model Site has a new parameter system_data
  - Model Slice has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

**Breaking changes**

  - Model AttachedDataNetwork no longer has parameter created_at
  - Model AttachedDataNetwork no longer has parameter created_by
  - Model AttachedDataNetwork no longer has parameter created_by_type
  - Model AttachedDataNetwork no longer has parameter last_modified_at
  - Model AttachedDataNetwork no longer has parameter last_modified_by
  - Model AttachedDataNetwork no longer has parameter last_modified_by_type
  - Model DataNetwork no longer has parameter created_at
  - Model DataNetwork no longer has parameter created_by
  - Model DataNetwork no longer has parameter created_by_type
  - Model DataNetwork no longer has parameter last_modified_at
  - Model DataNetwork no longer has parameter last_modified_by
  - Model DataNetwork no longer has parameter last_modified_by_type
  - Model MobileNetwork no longer has parameter created_at
  - Model MobileNetwork no longer has parameter created_by
  - Model MobileNetwork no longer has parameter created_by_type
  - Model MobileNetwork no longer has parameter last_modified_at
  - Model MobileNetwork no longer has parameter last_modified_by
  - Model MobileNetwork no longer has parameter last_modified_by_type
  - Model PacketCoreControlPlane no longer has parameter created_at
  - Model PacketCoreControlPlane no longer has parameter created_by
  - Model PacketCoreControlPlane no longer has parameter created_by_type
  - Model PacketCoreControlPlane no longer has parameter last_modified_at
  - Model PacketCoreControlPlane no longer has parameter last_modified_by
  - Model PacketCoreControlPlane no longer has parameter last_modified_by_type
  - Model PacketCoreDataPlane no longer has parameter created_at
  - Model PacketCoreDataPlane no longer has parameter created_by
  - Model PacketCoreDataPlane no longer has parameter created_by_type
  - Model PacketCoreDataPlane no longer has parameter last_modified_at
  - Model PacketCoreDataPlane no longer has parameter last_modified_by
  - Model PacketCoreDataPlane no longer has parameter last_modified_by_type
  - Model Service no longer has parameter created_at
  - Model Service no longer has parameter created_by
  - Model Service no longer has parameter created_by_type
  - Model Service no longer has parameter last_modified_at
  - Model Service no longer has parameter last_modified_by
  - Model Service no longer has parameter last_modified_by_type
  - Model Sim no longer has parameter configuration_state
  - Model Sim no longer has parameter created_at
  - Model Sim no longer has parameter created_by
  - Model Sim no longer has parameter created_by_type
  - Model Sim no longer has parameter last_modified_at
  - Model Sim no longer has parameter last_modified_by
  - Model Sim no longer has parameter last_modified_by_type
  - Model SimPolicy no longer has parameter created_at
  - Model SimPolicy no longer has parameter created_by
  - Model SimPolicy no longer has parameter created_by_type
  - Model SimPolicy no longer has parameter last_modified_at
  - Model SimPolicy no longer has parameter last_modified_by
  - Model SimPolicy no longer has parameter last_modified_by_type
  - Model Site no longer has parameter created_at
  - Model Site no longer has parameter created_by
  - Model Site no longer has parameter created_by_type
  - Model Site no longer has parameter last_modified_at
  - Model Site no longer has parameter last_modified_by
  - Model Site no longer has parameter last_modified_by_type
  - Model Slice no longer has parameter created_at
  - Model Slice no longer has parameter created_by
  - Model Slice no longer has parameter created_by_type
  - Model Slice no longer has parameter last_modified_at
  - Model Slice no longer has parameter last_modified_by
  - Model Slice no longer has parameter last_modified_by_type

## 1.0.0b1 (2022-02-28)

* Initial Release
