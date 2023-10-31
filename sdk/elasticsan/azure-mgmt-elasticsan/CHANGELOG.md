# Release History

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
