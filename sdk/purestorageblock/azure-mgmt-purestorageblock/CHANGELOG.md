# Release History

## 1.1.0b1 (2026-07-29)

### Features Added

  - Client `PureStorageBlockMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `PureStorageBlockMgmtClient` added operation group `recoverable_volume_groups`
  - Client `PureStorageBlockMgmtClient` added operation group `saa_soperation_group`
  - Client `PureStorageBlockMgmtClient` added operation group `volume_group_snapshots`
  - Client `PureStorageBlockMgmtClient` added operation group `volume_groups`
  - Client `PureStorageBlockMgmtClient` added operation group `volumes`
  - Model `MarketplaceDetails` added property `saa_s_resource_id`
  - Model `StoragePoolProperties` added property `platform_console_settings`
  - Model `StoragePoolUpdateProperties` added property `platform_console_settings`
  - Added model `ActivateSaaSRequest`
  - Added model `AzureVolumeProperties`
  - Added model `ConnectionParametersResponse`
  - Added model `DestroyedStateProperties`
  - Added model `IscsiConnectionParameters`
  - Added model `IscsiEndpoint`
  - Added model `LatestLinkedSaaSResponse`
  - Added model `LinkSaaSRequest`
  - Added model `PerformanceParameters`
  - Added model `PlatformConsoleAccessSettings`
  - Added model `PlatformConsoleActivationCode`
  - Added model `PlatformConsoleAuthConfig`
  - Added model `PlatformConsoleAuthResult`
  - Added enum `PlatformConsoleAuthType`
  - Added enum `PlatformConsoleRole`
  - Added model `PlatformConsoleSettings`
  - Added model `PlatformConsoleSubnet`
  - Added model `ProtectionParameters`
  - Added model `RecoverableVolumeGroup`
  - Added model `RecoverableVolumeGroupProperties`
  - Added model `SaaSResourceDetailsResponse`
  - Added model `SshPlatformConsoleAuthConfig`
  - Added model `SshPlatformConsoleAuthResult`
  - Added model `Volume`
  - Added model `VolumeGroup`
  - Added model `VolumeGroupOverwriteRequest`
  - Added model `VolumeGroupProperties`
  - Added model `VolumeGroupSnapshot`
  - Added model `VolumeGroupSnapshotListRequest`
  - Added model `VolumeGroupSnapshotPostListResult`
  - Added model `VolumeGroupSnapshotProperties`
  - Added enum `VolumeGroupSourceType`
  - Added model `VolumeGroupStatus`
  - Added model `VolumeGroupUpdate`
  - Added model `VolumeGroupUpdateProperties`
  - Added model `VolumeOverwriteRequest`
  - Added model `VolumeSnapshotInfo`
  - Added model `VolumeSnapshotSource`
  - Added enum `VolumeSourceType`
  - Added model `VolumeUpdate`
  - Added model `VolumeUpdateProperties`
  - Operation group `ReservationsOperations` added method `begin_link_saa_s`
  - Operation group `ReservationsOperations` added method `latest_linked_saa_s`
  - Operation group `StoragePoolsOperations` added method `configure_platform_console_auth`
  - Operation group `StoragePoolsOperations` added method `list_platform_console_activation_code`
  - Added operation group `RecoverableVolumeGroupsOperations`
  - Added operation group `SaaSOperationGroupOperations`
  - Added operation group `VolumeGroupSnapshotsOperations`
  - Added operation group `VolumeGroupsOperations`
  - Added operation group `VolumesOperations`

## 1.0.0 (2025-06-30)

### Other Changes

  - First GA

## 1.0.0b1 (2025-05-27)

### Other Changes

  - Initial version
