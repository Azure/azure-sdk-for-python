# Release History

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
