# Release History

## 3.0.0b1 (2026-10-01)

### Features Added

  - Client `ElasticSanMgmtClient` added method `begin_restore_volume`
  - Model `ElasticSanProperties` added property `total_reserved_iops`
  - Model `ElasticSanProperties` added property `total_reserved_m_bps`
  - Model `ElasticSanProperties` added property `used_capacity_gi_b`
  - Model `ElasticSanProperties` added property `version`
  - Model `ElasticSanUpdateProperties` added property `total_iops`
  - Model `ElasticSanUpdateProperties` added property `total_m_bps`
  - Model `ElasticSanUpdateProperties` added property `total_size_ti_b`
  - Enum `ProvisioningStates` added member `SOFT_DELETING`
  - Model `SkuLocationInfo` added property `zone_details`
  - Enum `SkuName` added member `ELASTIC_SAN_LRS`
  - Model `SnapshotProperties` added property `completion_percent`
  - Model `SnapshotProperties` added property `snapshot_access_state`
  - Enum `StorageTargetType` added member `DIRECT_ATTACH`
  - Model `VolumeGroupProperties` added property `delete_retention_policy`
  - Model `VolumeGroupProperties` added property `encryption_in_transit`
  - Model `VolumeGroupProperties` added property `quality_of_service`
  - Model `VolumeGroupProperties` added property `reserved_iops`
  - Model `VolumeGroupProperties` added property `reserved_m_bps`
  - Model `VolumeGroupUpdateProperties` added property `delete_retention_policy`
  - Model `VolumeGroupUpdateProperties` added property `reserved_iops`
  - Model `VolumeGroupUpdateProperties` added property `reserved_m_bps`
  - Added model `DeleteRetentionPolicy`
  - Added enum `DeleteType`
  - Added enum `ElasticSanVersion`
  - Added model `ManagedByResources`
  - Added enum `PolicyState`
  - Added enum `QualityOfService`
  - Added model `SkuZoneDetails`
  - Added enum `SnapshotAccessState`
  - Added enum `XMsAccessSoftDeletedResources`
  - Model `VolumeGroupsOperations` added parameter `x_ms_access_soft_deleted_resources` in method `list_by_elastic_san`
  - Model `VolumesOperations` added parameter `delete_type` in method `begin_delete`
  - Model `VolumesOperations` added parameter `x_ms_access_soft_deleted_resources` in method `list_by_volume_group`

### Breaking Changes

  - Deleted or renamed model `ManagedByInfo`

## 2.0.0 (2026-01-29)

### Features Added

  - Model `ElasticSanMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ElasticSanMgmtClient` added method `send_request`
  - Model `ElasticSanProperties` added property `auto_scale_properties`
  - Model `ElasticSanUpdateProperties` added property `auto_scale_properties`
  - Enum `ProvisioningStates` added member `DELETED`
  - Enum `ProvisioningStates` added member `RESTORING`
  - Added enum `AutoScalePolicyEnforcement`
  - Added model `AutoScaleProperties`
  - Added model `DiskSnapshotList`
  - Added model `PreValidationResponse`
  - Added model `ScaleUpProperties`
  - Added model `VolumeNameList`
  - Operation group `VolumesOperations` added method `begin_pre_backup`
  - Operation group `VolumesOperations` added method `begin_pre_restore`

### Breaking Changes

  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Deleted model `ElasticSanList`/`SkuInformationList`/`SnapshotList`/`VolumeGroupList`/`VolumeList` which actually were not used by SDK users
  - Method `VolumesOperations.begin_delete` changed its parameter `x_ms_delete_snapshots` from `positional_or_keyword` to `keyword_only`
  - Method `VolumesOperations.begin_delete` changed its parameter `x_ms_force_delete` from `positional_or_keyword` to `keyword_only`

## 1.2.0b2 (2025-04-21)

### Features Added

  - Client `ElasticSanMgmtClient` added method `begin_restore_volume`
  - Model `ElasticSanMgmtClient` added property `url`
  - Enum `ProvisioningStates` added member `DELETED`
  - Enum `ProvisioningStates` added member `RESTORING`
  - Enum `ProvisioningStates` added member `SOFT_DELETING`
  - Model `VolumeGroupProperties` added property `delete_retention_policy`
  - Model `VolumeGroupUpdateProperties` added property `delete_retention_policy`
  - Added model `DeleteRetentionPolicy`
  - Added enum `DeleteType`
  - Added model `DiskSnapshotList`
  - Added enum `PolicyState`
  - Added model `PreValidationResponse`
  - Added model `VolumeNameList`
  - Added enum `XMsAccessSoftDeletedResources`
  - Operation group `VolumesOperations` added method `begin_pre_backup`
  - Operation group `VolumesOperations` added method `begin_pre_restore`
  - Added operation group `ElasticSanMgmtClientOperationsMixin`

## 1.2.0b1 (2024-10-20)

### Features Added

  - Model `ElasticSanProperties` added property `auto_scale_properties`
  - Model `ElasticSanUpdateProperties` added property `auto_scale_properties`
  - Added enum `AutoScalePolicyEnforcement`
  - Added model `AutoScaleProperties`
  - Added model `ScaleUpProperties`

## 1.1.0 (2024-09-23)

### Features Added

  - Model VolumeGroupProperties has a new parameter enforce_data_integrity_check_for_iscsi
  - Model VolumeGroupUpdateProperties has a new parameter enforce_data_integrity_check_for_iscsi

## 1.0.0 (2024-01-25)

### Features Added

  - Model ElasticSanUpdate has a new parameter properties
  - Model PrivateLinkResource has a new parameter properties
  - Model VolumeGroup has a new parameter properties
  - Model VolumeGroupUpdate has a new parameter properties
  - Model VolumeUpdate has a new parameter properties

### Breaking Changes

  - Model ElasticSan has a new required parameter properties
  - Model ElasticSan no longer has parameter availability_zones
  - Model ElasticSan no longer has parameter base_size_ti_b
  - Model ElasticSan no longer has parameter extended_capacity_size_ti_b
  - Model ElasticSan no longer has parameter private_endpoint_connections
  - Model ElasticSan no longer has parameter provisioning_state
  - Model ElasticSan no longer has parameter public_network_access
  - Model ElasticSan no longer has parameter sku
  - Model ElasticSan no longer has parameter total_iops
  - Model ElasticSan no longer has parameter total_m_bps
  - Model ElasticSan no longer has parameter total_size_ti_b
  - Model ElasticSan no longer has parameter total_volume_size_gi_b
  - Model ElasticSan no longer has parameter volume_group_count
  - Model ElasticSanUpdate no longer has parameter base_size_ti_b
  - Model ElasticSanUpdate no longer has parameter extended_capacity_size_ti_b
  - Model ElasticSanUpdate no longer has parameter public_network_access
  - Model PrivateEndpointConnection has a new required parameter properties
  - Model PrivateEndpointConnection no longer has parameter group_ids
  - Model PrivateEndpointConnection no longer has parameter private_endpoint
  - Model PrivateEndpointConnection no longer has parameter private_link_service_connection_state
  - Model PrivateEndpointConnection no longer has parameter provisioning_state
  - Model PrivateLinkResource no longer has parameter group_id
  - Model PrivateLinkResource no longer has parameter required_members
  - Model PrivateLinkResource no longer has parameter required_zone_names
  - Model Snapshot has a new required parameter properties
  - Model Snapshot no longer has parameter creation_data
  - Model Snapshot no longer has parameter provisioning_state
  - Model Snapshot no longer has parameter source_volume_size_gi_b
  - Model Snapshot no longer has parameter volume_name
  - Model Volume has a new required parameter properties
  - Model Volume no longer has parameter creation_data
  - Model Volume no longer has parameter managed_by
  - Model Volume no longer has parameter provisioning_state
  - Model Volume no longer has parameter size_gi_b
  - Model Volume no longer has parameter storage_target
  - Model Volume no longer has parameter volume_id
  - Model VolumeGroup no longer has parameter encryption
  - Model VolumeGroup no longer has parameter encryption_properties
  - Model VolumeGroup no longer has parameter network_acls
  - Model VolumeGroup no longer has parameter private_endpoint_connections
  - Model VolumeGroup no longer has parameter protocol_type
  - Model VolumeGroup no longer has parameter provisioning_state
  - Model VolumeGroupUpdate no longer has parameter encryption
  - Model VolumeGroupUpdate no longer has parameter encryption_properties
  - Model VolumeGroupUpdate no longer has parameter network_acls
  - Model VolumeGroupUpdate no longer has parameter protocol_type
  - Model VolumeUpdate no longer has parameter managed_by
  - Model VolumeUpdate no longer has parameter size_gi_b

## 1.0.0b3 (2023-10-23)

### Features Added

  - Added operation group VolumeSnapshotsOperations
  - Model ElasticSan has a new parameter public_network_access
  - Model ElasticSanUpdate has a new parameter public_network_access
  - Model SourceCreationData has a new parameter source_id
  - Model Volume has a new parameter managed_by
  - Model Volume has a new parameter provisioning_state
  - Model VolumeGroup has a new parameter encryption_properties
  - Model VolumeGroup has a new parameter identity
  - Model VolumeGroupUpdate has a new parameter encryption_properties
  - Model VolumeGroupUpdate has a new parameter identity
  - Model VolumeUpdate has a new parameter managed_by
  - Operation VolumesOperations.begin_delete has a new optional parameter x_ms_delete_snapshots
  - Operation VolumesOperations.begin_delete has a new optional parameter x_ms_force_delete

### Breaking Changes

  - Model SourceCreationData no longer has parameter source_uri
  - Model VirtualNetworkRule no longer has parameter state

## 1.0.0b2 (2023-07-21)

### Features Added

  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Model ElasticSan has a new parameter private_endpoint_connections
  - Model ErrorResponse has a new parameter error
  - Model Resource has a new parameter system_data
  - Model SkuInformationList has a new parameter next_link
  - Model TrackedResource has a new parameter system_data
  - Model VolumeGroup has a new parameter private_endpoint_connections

### Breaking Changes

  - Client name is changed from `ElasticSanManagement` to `ElasticSanMgmtClient`
  - Model ErrorResponse no longer has parameter additional_info
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter message
  - Model ErrorResponse no longer has parameter target
  - Model Resource no longer has parameter tags
  - Model Volume no longer has parameter tags
  - Model VolumeGroup no longer has parameter tags
  - Model VolumeGroupUpdate no longer has parameter tags
  - Model VolumeUpdate no longer has parameter tags
  - Parameter location of model ElasticSan is now required
  - Parameter location of model TrackedResource is now required
  - Parameter size_gi_b of model Volume is now required

## 1.0.0b1 (2022-10-21)

* Initial Release
